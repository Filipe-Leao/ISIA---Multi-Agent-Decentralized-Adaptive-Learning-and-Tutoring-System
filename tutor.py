from spade.agent import Agent
from spade.message import Message
from spade.behaviour import *
from spade.presence import *
from spade import behaviour
import asyncio
from colorama import Fore, Style


class TutorAgent(Agent):
    def __init__(self, jid, password, discipline, expertise=0.5, capacity=1):
        super().__init__(jid, password)
        self.discipline = discipline
        self.capacity = capacity
        self.available_slots = capacity
        self.expertise = expertise    # <-- NEW
        self.queue = []  # (student, priority)

    async def setup(self):
        print(Fore.CYAN + f"[Tutor-{self.name}] Iniciado | Capacidade: {self.capacity} | Available: {self.available_slots} | Expertise: {self.expertise}" + Style.RESET_ALL)
        self.add_behaviour(self.HelpResponder())
        self.add_behaviour(self.Subscription())


    class Subscription(OneShotBehaviour):
        def on_available(self, peer_jid, presence_info, last_presence):
            print(f"[{self.agent.name}] Agent {peer_jid.split('@')[0]} is {presence_info.show.value}")

        def on_subscribed(self, peer_jid):
            print(f"[{self.agent.name}] Agent {peer_jid.split('@')[0]} has accepted the subscription")
            contacts = self.agent.presence.get_contacts()
            print(f"[{self.agent.name}] Contacts List: {contacts}")

        def on_subscribe(self, peer_jid):
            print(f"[{self.agent.name}] Agent {peer_jid.split('@')[0]} asked for subscription. Let's approve it")
            self.presence.approve_subscription(peer_jid)
            self.presence.subscribe(peer_jid)

        async def run(self):
            self.presence.set_presence(
                presence_type=PresenceType.AVAILABLE,
                show=PresenceShow.CHAT,
                status="Ready to chat"
            )
            self.presence.on_subscribe = self.on_subscribe
            self.presence.on_subscribed = self.on_subscribed
            self.presence.on_available = self.on_available



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

                priority = 0

                # priority = expertise * (1 - student_progress)
                if str(parts["topic"]) == str(self.agent.discipline): 
                    priority = 1
                    print(Fore.RED + f"[{self.agent.name}] Priority to student {msg.sender} increased for matching discipline." + Style.RESET_ALL)
                priority += self.agent.expertise * (1 - student_progress)

                self.agent.queue.append((str(msg.sender), priority))
                self.agent.queue.sort(key=lambda x: x[1], reverse=True)

                chosen_student = self.agent.queue[0][0]

                # if tutor available and this student is highest priority
                if self.agent.available_slots > 0 and str(msg.sender) == chosen_student:
                    proposal = Message(to=str(msg.sender))
                    proposal.set_metadata("performative", "propose")
                    proposal.body = f"available_in:1;discipline:{self.agent.discipline};expertise:{self.agent.expertise};slots:{self.agent.available_slots}"
                    await self.send(proposal)

                else:
                    refusal = Message(to=str(msg.sender))
                    refusal.set_metadata("performative", "refuse")
                    refusal.body = "reject-proposal"
                    await self.send(refusal)

            # ---------- Acceptance ----------
            elif perf == "accept-proposal":
                self.agent.available_slots -= 1
                print(Fore.GREEN + f"[Tutor-{self.agent.name}] ✅ Aceitou {msg.sender}" + Style.RESET_ALL)

                await asyncio.sleep(2)  # simulate teaching time

                rsp = Message(to=str(msg.sender))
                rsp.set_metadata("performative", "inform")
                rsp.body = "explicacao:Feito!"
                await self.send(rsp)

                self.agent.available_slots += 1

            # ---------- Rejection ----------
            elif perf == "reject-proposal":
                print(Fore.RED + f"[Tutor-{self.agent.name}] ❌ Rejeitado por {msg.sender}" + Style.RESET_ALL)
