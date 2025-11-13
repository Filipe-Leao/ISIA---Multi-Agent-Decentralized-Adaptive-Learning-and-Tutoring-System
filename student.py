from spade.agent import Agent
from spade.message import Message
from spade import behaviour
from spade.presence import PresenceType, PresenceShow
from colorama import Fore, Style
import asyncio, random, time
from metrics import MetricsLogger


class StudentAgent(Agent):
    def __init__(self, jid, password, learning_style="visual"):
        super().__init__(jid, password)
        self.learning_style = learning_style
        self.knowledge = {
            "estatística bayesiana": random.uniform(0, 0.4),
            "aprendizagem automática": random.uniform(0, 0.4),
            "programação": random.uniform(0, 0.4),
            "estatística": random.uniform(0, 0.4),
            "português": random.uniform(0, 0.4),
            "álgebra": random.uniform(0, 0.4),
        }
        self.tutor_message = NotImplementedError
        self.progress = sum(self.knowledge.values()) / len(self.knowledge)
        self.initial_progress = self.progress
        self.logger = MetricsLogger()
        print(Fore.CYAN + f"[{self.name}] estilo={self.learning_style} progresso médio={round(self.progress, 2)}" + Style.RESET_ALL)

    async def setup(self):
        print(Fore.CYAN + f"[Student-{self.name}] Iniciado")
        self.study = self.StudyBehaviour()
        self.add_behaviour(self.Subscription())
        self.add_behaviour(self.study)
        self.add_behaviour(self.ReceiveBehaviour())
        self.proposals = []

    class Subscription(behaviour.OneShotBehaviour):
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

    class StudyBehaviour(behaviour.CyclicBehaviour):
        async def on_start(self):
            self.agent.proposals = []
            self.peer_used = False
            self.chosen_tutor = None
            self.chosen_tutor_expertise = None
            self.start_time = time.time()
            print(f"[{self.agent.name}] {self.agent.presence.get_presence()}")
            await asyncio.sleep(5)
            self.agent.topic = random.choice(list(self.agent.knowledge.keys()))
            self.agent.progress = self.agent.knowledge[self.agent.topic]
            while self.agent.progress < 1.0:
                print(Fore.BLUE + f"[{self.agent.name}] 🎯 A estudar {self.agent.topic} (progresso: {self.agent.progress:.2f})" + Style.RESET_ALL)
                await self.ask_for_help()
                await self.update_progress()
                await asyncio.sleep(2) 

        async def update_progress(self):
            old = self.agent.progress
            self.agent.progress = sum(self.agent.knowledge.values()) / len(self.agent.knowledge)
            print(Fore.MAGENTA + f"[{self.agent.name}] 📊 Progresso geral atualizado: {old:.2f} -> {self.agent.progress:.2f}" + Style.RESET_ALL)
            await asyncio.sleep(1)

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

            for tutor in tutors:
                msg = Message(to=tutor)
                msg.set_metadata("performative", "cfp")
                msg.body = f"topic:{self.agent.topic};progress:{self.agent.progress};style:{self.agent.learning_style}"
                print(Fore.BLUE + f"[{self.agent.name}] CFP → {tutor}: {self.agent.topic}" + Style.RESET_ALL)
                await self.send(msg)

            await asyncio.sleep(2)

            if not self.agent.proposals:
                print(Fore.RED + f"[{self.agent.name}] ❌ Nenhum tutor respondeu — pedir peer" + Style.RESET_ALL)
                self.peer_used = True
                self.chosen_tutor = "peer" 

                for peer in peers:
                    peer = Message(to=peer)
                    peer.set_metadata("performative", "peer-help")
                    await self.send(peer)
                return

            # ✅ Ordenar propostas (expertise, slots)
            self.agent.proposals.sort(
                key=lambda p: (p["expertise"], p["slots"], random.random() * 0.01),
                reverse=True
            )

            if self.peer_used:
                print(Fore.BLUE + f"[{self.agent.name}] {self.agent.proposals}" + Style.RESET_ALL) 

            # ✅ Escolher o tutor com vagas
            for p in self.agent.proposals:
                if p["slots"] > 0 and p["discipline"] == self.agent.topic:
                    self.chosen_tutor = p["tutor"]
                    print(Fore.RED + f"[{self.agent.name}] Proposal chosen: {p}" + Style.RESET_ALL)
                    self.agent.tutor_message = p
                    print(self.agent.tutor_message)
                    break
                elif p["slots"] > 0 and p["expertise"] >= (self.chosen_tutor_expertise if self.chosen_tutor_expertise else 0):
                    self.chosen_tutor = p["tutor"]
                    print(Fore.RED + f"[{self.agent.name}] Proposal chosen (different discipline): {p}" + Style.RESET_ALL)
                    self.agent.tutor_message = p
                    print(self.agent.tutor_message)
                    self.chosen_tutor = p["tutor"]
                    self.chosen_tutor_expertise = p["expertise"]
            
            

            if not self.chosen_tutor:
                print(Fore.YELLOW + f"[{self.agent.name}] Nenhum tutor com vagas — tentar novamente em 3s" + Style.RESET_ALL)
                await asyncio.sleep(3)
                await self.ask_for_help()
                return

            print(Fore.BLUE + f"[{self.agent.name}] ✉️ Aceitou proposta de {self.chosen_tutor}" + Style.RESET_ALL)

            msg = Message(to=self.chosen_tutor)
            msg.set_metadata("performative", "accept-proposal")
            await self.send(msg)

            # Rejeitar os outros
            for p in self.agent.proposals:
                if p["tutor"] != self.chosen_tutor:
                    rej = Message(to=p["tutor"])
                    rej.set_metadata("performative", "reject-proposal")
                    await self.send(rej)

            self.agent.presence.set_presence(
                presence_type=PresenceType.AVAILABLE,  # set availability
                show=PresenceShow.DND,  # show status
                status="Waiting for tutor",  # status message
                priority=2  # connection priority
            )

            print(Fore.BLUE + f"[{self.agent.name}] ⏳ A aguardar explicação..." + Style.RESET_ALL)

        async def run(self):
            await asyncio.sleep(1)

    class ReceiveBehaviour(behaviour.CyclicBehaviour):
        async def run(self):
            self.agent.progress = sum(self.agent.knowledge.values()) / len(self.agent.knowledge)
            msg = await self.receive(timeout=1)
            if not msg:
                return

            perf = msg.get_metadata("performative")

            # --- proposta de tutor ---
            if perf == "propose":
                parts = dict(p.split(":") for p in msg.body.split(";"))
                discipline = parts.get("discipline", "")
                expertise = float(parts.get("expertise", 0))
                slots = int(parts.get("slots", 0))

                self.agent.proposals.append({
                    "tutor": str(msg.sender),
                    "discipline": discipline,
                    "expertise": expertise,
                    "slots": slots
                })
                print(Fore.YELLOW + f"[{self.agent.name}] 📩 Proposta de {msg.sender}: (discipline= {discipline}, exp={expertise}, slots={slots})" + Style.RESET_ALL)

            # --- tutor rejeitou ---
            elif perf == "refuse":
                print(Fore.RED + f"[{self.agent.name}] ❌ {msg.sender} ocupado — tentar outro" + Style.RESET_ALL)
                return

            # --- explicação recebida ---
            elif perf in ["inform", "peer-inform"]:
                study = self.agent.study
                chosen = "peer" if study.peer_used else study.chosen_tutor
                end = time.time()
                rt = round(end - study.start_time, 2)

                self.agent.presence.set_presence(
                    presence_type=PresenceType.AVAILABLE,  # set availability
                    show=PresenceShow.DND,  # show status
                    status=f"Waiting for {chosen}",  # status message
                    priority=2  # connection priority
                ) 

                print(Fore.GREEN + f"[{self.agent.name}] ✅ Explicação recebida" + Style.RESET_ALL)
                old = self.agent.knowledge[self.agent.topic]

                if chosen == "peer":
                    self.agent.knowledge[self.agent.topic] = min(1.0, old + random.uniform(0.03, 0.10))
                elif self.agent.tutor_message and self.agent.tutor_message["discipline"] == self.agent.topic:
                    self.agent.knowledge[self.agent.topic] = min(1.0, old + (random.uniform(0.08, 0.25) * self.agent.tutor_message["expertise"]))
                else:
                    self.agent.knowledge[self.agent.topic] = min(1.0, old + (random.uniform(0.05, 0.15) * self.agent.tutor_message["expertise"]))
                print(Fore.GREEN + f"[{self.agent.name}] 🎓 progresso {old:.2f} → {self.agent.knowledge[self.agent.topic]:.2f}" + Style.RESET_ALL)

                # Registar no logger
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

                # --- 💡 Pedir recurso complementar ---
                resource_msg = Message(to="resource@localhost")
                resource_msg.set_metadata("performative", "resource-request")
                resource_msg.body = f"topic:{self.agent.topic};progress:{self.agent.progress};style:{self.agent.learning_style}"
                await self.send(resource_msg)
                print(Fore.YELLOW + f"[{self.agent.name}] 🔎 A pedir recurso complementar ao Resource Manager...")

            # --- recurso recebido ---
            elif perf == "resource-recommendation":
                resource = msg.body.split("resource:")[1]
                print(Fore.LIGHTYELLOW_EX + f"[{self.agent.name}] 📘 Recurso complementar recebido: {resource}" + Style.RESET_ALL)

                # 🔼 Aumentar ligeiramente o progresso
                old = self.agent.knowledge[self.agent.topic]
                self.agent.knowledge[self.agent.topic] = min(1.0, old + random.uniform(0.01, 0.05))
                await asyncio.sleep(2)
                print(Fore.LIGHTGREEN_EX + f"[{self.agent.name}] 📈 progresso após recurso {old:.2f} → {self.agent.knowledge[self.agent.topic]:.2f}" + Style.RESET_ALL)
                self.agent.topic = random.choice(list(self.agent.knowledge.keys()))
                self.agent.progress = self.agent.knowledge[self.agent.topic]