from spade.agent import Agent
from spade.message import Message
from spade import behaviour
from colorama import Fore
import asyncio, time, random
from metrics import MetricsLogger

class StudentAgent(Agent):
    def __init__(self, jid, password, learning_style="visual"):
        super().__init__(jid, password)
        self.learning_style = learning_style
        self.knowledge = {
            "estatística bayesiana": random.uniform(0, 0.4),
            "aprendizagem automática": random.uniform(0, 0.4)
        }
        self.topic = random.choice(list(self.knowledge.keys()))
        self.progress = self.knowledge[self.topic]
        self.logger = MetricsLogger()
        print(Fore.CYAN + f"[{self.name}] estilo={self.learning_style} progresso médio={round(self.progress,2)}")

    async def setup(self):
        print(Fore.CYAN + f"[Student-{self.name}] Iniciado")

        # ✅ guardar comportamento
        self.study = self.StudyBehaviour()
        self.add_behaviour(self.study)

        self.add_behaviour(self.ReceiveBehaviour())
        self.proposals = []

    class StudyBehaviour(behaviour.CyclicBehaviour):
        async def on_start(self):
            self.agent.proposals = []
            self.peer_used = False
            self.chosen_tutor = None
            self.start_time = time.time()
            await asyncio.sleep(2)
            await self.ask_for_help()

        async def ask_for_help(self):
            tutors = ["tutor1@localhost", "tutor2@localhost"]

            for tutor in tutors:
                msg = Message(to=tutor)
                msg.set_metadata("performative", "cfp")
                msg.body = f"topic:{self.agent.topic};progress:{self.agent.progress};style:{self.agent.learning_style}"
                print(Fore.BLUE + f"[{self.agent.name}] CFP → {tutor}: {self.agent.topic}")
                await self.send(msg)

            await asyncio.sleep(3)

            if not self.agent.proposals:
                print(Fore.RED + f"[{self.agent.name}] ❌ Nenhum tutor -> pedir peer")
                self.peer_used = True
                peer = Message(to="peer1@localhost")
                peer.set_metadata("performative", "peer-help")
                await self.send(peer)
                return

            best = self.agent.proposals[0]
            self.chosen_tutor = best["tutor"]

            msg = Message(to=self.chosen_tutor)
            msg.set_metadata("performative", "accept-proposal")
            await self.send(msg)

            for p in self.agent.proposals:
                if p["tutor"] != self.chosen_tutor:
                    rej = Message(to=p["tutor"])
                    rej.set_metadata("performative", "reject-proposal")
                    await self.send(rej)

            print(Fore.BLUE + f"[{self.agent.name}] ⏳ A aguardar explicação...")

        async def run(self):
            await asyncio.sleep(1)

    class ReceiveBehaviour(behaviour.CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1)
            if not msg:
                return

            perf = msg.get_metadata("performative")

            if perf == "propose":
                self.agent.proposals.append({"tutor": str(msg.sender)})
                print(Fore.YELLOW + f"[{self.agent.name}] 📩 Proposta de {msg.sender}")

            elif perf in ["inform", "peer-inform"]:
                # ✅ usar defaults seguros
                study = self.agent.study
                chosen = "peer" if study.peer_used else study.chosen_tutor

                end = time.time()
                rt = round(end - study.start_time, 2)

                print(Fore.GREEN + f"[{self.agent.name}] ✅ Explicação recebida")
                old = self.agent.progress
                self.agent.progress = min(1.0, old + random.uniform(0.08, 0.25))
                print(Fore.GREEN + f"[{self.agent.name}] 🎓 progresso {old:.2f} → {self.agent.progress:.2f}")

                self.agent.logger.log(
                    student=self.agent.name,
                    tutor=chosen,
                    topic=self.agent.topic,
                    response_time=rt,
                    proposals_received=len(self.agent.proposals),
                    chosen_tutor=chosen,
                    rejected_count=(len(self.agent.proposals)-1) if chosen != "peer" else 0,
                    peer_used=(chosen == "peer")
                )
