from spade.agent import Agent
from spade.message import Message
from spade import behaviour
import asyncio
from colorama import Fore


class TutorAgent(Agent):
    def __init__(self, jid, password, expertise=0.5, capacity=1):
        super().__init__(jid, password)
        self.capacity = capacity
        self.available_slots = capacity
        self.expertise = expertise    # <-- NEW
        self.queue = []  # (student, priority)

    async def setup(self):
        print(Fore.CYAN + f"[Tutor-{self.name}] Iniciado | Capacidade: {self.capacity} | Expertise: {self.expertise}")
        self.add_behaviour(self.HelpResponder())


    class HelpResponder(behaviour.CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=5)
            if not msg:
                return

            perf = msg.get_metadata("performative")

            # ---------- CFP received ----------
            if perf == "cfp":
                parts = dict(p.split(":") for p in msg.body.split(";"))
                student_progress = float(parts.get("progress", 0))

                # priority = expertise * (1 - student_progress)
                priority = self.agent.expertise * (1 - student_progress)

                self.agent.queue.append((str(msg.sender), priority))
                self.agent.queue.sort(key=lambda x: x[1], reverse=True)

                chosen_student = self.agent.queue[0][0]

                # if tutor available and this student is highest priority
                if self.agent.available_slots > 0 and str(msg.sender) == chosen_student:
                    proposal = Message(to=str(msg.sender))
                    proposal.set_metadata("performative", "propose")
                    proposal.body = f"available_in:1;expertise:{self.agent.expertise}"
                    await self.send(proposal)

            # ---------- Acceptance ----------
            elif perf == "accept-proposal":
                self.agent.available_slots -= 1
                print(Fore.GREEN + f"[Tutor-{self.agent.name}] ✅ Aceitou {msg.sender}")

                await asyncio.sleep(2)  # simulate teaching time

                rsp = Message(to=str(msg.sender))
                rsp.set_metadata("performative", "inform")
                rsp.body = "explicacao:Feito!"
                await self.send(rsp)

                self.agent.available_slots += 1

            # ---------- Rejection ----------
            elif perf == "reject-proposal":
                print(Fore.RED + f"[Tutor-{self.agent.name}] ❌ Rejeitado")
