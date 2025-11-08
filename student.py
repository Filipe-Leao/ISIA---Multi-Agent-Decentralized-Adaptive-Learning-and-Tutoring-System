from spade.agent import Agent
from spade.message import Message
from spade.presence import *
from spade.behaviour import *
from colorama import Fore, Style
import asyncio, random, time
from metrics import MetricsLogger


class StudentAgent(Agent):
    """
    Student agent that studies a specific topic and requests help from tutors or peers when needed.

    Attributes:
        jid (str): The Jabber ID of the agent.
        password (str): The password for the agent.
        learning_style (str): Prefered learning style (visual, auditory, cinestésico, kinesthetic).
    """
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
        print(Fore.CYAN + f"[{self.name}] estilo={self.learning_style} progresso médio={round(self.progress, 2)}" + Style.RESET_ALL)

    async def setup(self):
        print(Fore.CYAN + f"[Student-{self.name}] Iniciado" + Style.RESET_ALL)
        self.study = self.StudyBehaviour()
        self.add_behaviour(self.Subscription())
        self.add_behaviour(self.study)
        self.add_behaviour(self.ReceiveBehaviour())
        self.proposals = []

    class Subscription(OneShotBehaviour):
        """ Manages presence subscriptions with other agents. """
        async def run(self):
            # ⚙️ Configurar callbacks corretamente
            self.agent.presence.on_subscribe = self.on_subscribe
            self.agent.presence.on_subscribed = self.on_subscribed
            self.agent.presence.on_available = self.on_available

            # ⚙️ Definir presença inicial
            self.agent.presence.set_presence(
                presence_type=PresenceType.AVAILABLE,
                show=PresenceShow.CHAT,
                status="Ready to chat"
            )

            # ⚙️ Esperar servidor estabilizar
            await asyncio.sleep(2)

            contacts = self.agent.presence.get_contacts()

        def on_available(self, peer_jid, presence_info, last_presence):
            print(f"[{self.agent.name}] Agent {peer_jid.split('@')[0]} is {presence_info.show.value}")

        def on_subscribed(self, peer_jid):
            print(f"[{self.agent.name}] Agent {peer_jid.split('@')[0]} accepted the subscription")

        def on_subscribe(self, peer_jid):
            print(f"[{self.agent.name}] Agent {peer_jid.split('@')[0]} asked for subscription. Approving...")
            self.agent.presence.approve_subscription(peer_jid)
            self.agent.presence.subscribe(peer_jid)


    class StudyBehaviour(CyclicBehaviour):
        async def on_start(self):
            self.agent.proposals = []
            self.peer_used = False
            self.chosen_tutor = None
            self.start_time = time.time()
            await asyncio.sleep(5)
            print(f"[{self.agent.name}] {self.agent.presence.get_presence()}")
            while self.agent.progress < 1.0:
                print(Fore.BLUE + f"[{self.agent.name}] 🎯 A estudar {self.agent.topic} (progresso: {self.agent.progress:.2f})" + Style.RESET_ALL)
                await self.ask_for_help()
                await asyncio.sleep(2)


        async def ask_for_help(self):
            tutors = []
            peers = []
            contacts = self.agent.presence.get_contacts()

            for contact, info in contacts.items():
                contact = str(contact)
                if contact.startswith("tutor"):
                    tutors.append(contact)
                elif contact.startswith("peer"):
                    peers.append(contact)

            print(f"[{self.agent.name}] Tutors List: {tutors}")
            print(f"[{self.agent.name}] Peers List: {peers}")
            for tutor in tutors:
                msg = Message(to=tutor)
                msg.set_metadata("performative", "cfp")
                msg.body = f"topic:{self.agent.topic};progress:{self.agent.progress};style:{self.agent.learning_style}"
                print(Fore.BLUE + f"[{self.agent.name}] CFP → {tutor}: {self.agent.topic}" + Style.RESET_ALL)
                await self.send(msg)

            await asyncio.sleep(3)

            if not self.agent.proposals:
                print(Fore.RED + f"[{self.agent.name}] ❌ Nenhum tutor respondeu — pedir peer" + Style.RESET_ALL)
                self.peer_used = True
                for peer in peers:
                    peer = Message(to=peer)
                    peer.set_metadata("performative", "peer-help")
                    await self.send(peer)
                return

            # ✅ Ordenar propostas (expertise, slots) + ruído mínimo para desempatar
            self.agent.proposals.sort(
                key=lambda p: (p["expertise"], p["slots"], random.random() * 0.01),
                reverse=True
            )

            if self.peer_used:
                print(Fore.BLUE + f"[{self.agent.name}] {self.agent.proposals}" + Style.RESET_ALL)

            # ✅ Escolher primeiro tutor com vaga (>0)
            for p in self.agent.proposals:
                if p["slots"] > 0:
                    self.chosen_tutor = p["tutor"]
                    break

            if not self.chosen_tutor:
                print(Fore.YELLOW + f"[{self.agent.name}] Nenhum tutor com vagas — tentar novamente em 3s" + Style.RESET_ALL)
                await asyncio.sleep(3)
                await self.ask_for_help()
                return

            print(Fore.BLUE + f"[{self.agent.name}] ✉️ Aceitou proposta de {self.chosen_tutor}" + Style.RESET_ALL)

            msg = Message(to=self.chosen_tutor)
            msg.set_metadata("performative", "accept-proposal")
            await self.send(msg)

            # Rejeita os restantes
            for p in self.agent.proposals:
                if p["tutor"] != self.chosen_tutor:
                    rej = Message(to=p["tutor"])
                    rej.set_metadata("performative", "reject-proposal")
                    await self.send(rej)

            print(Fore.BLUE + f"[{self.agent.name}] ⏳ A aguardar explicação..." + Style.RESET_ALL)

            self.agent.presence.set_presence(
                             presence_type=PresenceType.AVAILABLE,  # set availability
                             show=PresenceShow.DND,  # show status
                             status="Waiting for tutor",  # status message
                             priority=2  # connection priority
                            )
            print(f"[{self.agent.name}] {self.agent.presence.get_presence()}")

        async def run(self):
            await asyncio.sleep(1)

    class ReceiveBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=5)
            if not msg:
                return

            perf = msg.get_metadata("performative")

            if perf == "propose":
                parts = dict(p.split(":") for p in msg.body.split(";"))
                expertise = float(parts.get("expertise", 0))
                slots = int(parts.get("slots", 0))

                self.agent.proposals.append({
                    "tutor": str(msg.sender),
                    "expertise": expertise,
                    "slots": slots
                })
                print(Fore.YELLOW + f"[{self.agent.name}] 📩 Proposta de {msg.sender} (exp={expertise}, slots={slots})" + Style.RESET_ALL)

            elif perf == "reject-proposal":
                # Tutor recusou por estar ocupado → tentar outro
                print(Fore.RED + f"[{self.agent.name}] ❌ {msg.sender} ocupado — tentar outro" + Style.RESET_ALL)
                await self.agent.study.ask_for_help()

            elif perf in ["inform", "peer-inform"]:
                study = self.agent.study
                chosen = "peer" if study.peer_used else study.chosen_tutor

                self.agent.presence.set_presence(
                             presence_type=PresenceType.AVAILABLE,  # set availability
                             show=PresenceShow.DND,  # show status
                             status=f"Studing with {chosen}",  # status message
                             priority=2  # connection priority
                            )
                
                print(f"[{self.agent.name}] {self.agent.presence.get_presence()}")

                # ✅ usar defaults seguros
                
                end = time.time()   
                rt = round(end - study.start_time, 2)

                print(Fore.GREEN + f"[{self.agent.name}] ✅ Explicação recebida -> {chosen}" + Style.RESET_ALL)
                old = self.agent.progress
                self.agent.progress = min(1.0, old + random.uniform(0.08, 0.25))
                print(Fore.GREEN + f"[{self.agent.name}] 🎓 Tempo de execução {rt}" + Style.RESET_ALL)

                print(Fore.GREEN + f"[{self.agent.name}] 🎓 progresso {old:.2f} → {self.agent.progress:.2f}" + Style.RESET_ALL)

                self.agent.logger.log(
                    student=self.agent.name,
                    tutor=chosen,
                    topic=self.agent.topic,
                    response_time=rt,
                    proposals_received=len(self.agent.proposals),
                    chosen_tutor=chosen,
                    rejected_count=(len(self.agent.proposals) - 1) if chosen != "peer" else 0,
                    peer_used=(chosen == "peer")
                )
