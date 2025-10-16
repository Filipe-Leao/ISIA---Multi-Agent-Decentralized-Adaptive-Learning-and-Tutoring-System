from spade import behaviour
from spade.agent import Agent
from spade.message import Message
import spade
import asyncio
from colorama import Fore, Style, init

# ========================
# AGENTE TUTOR
# ========================
class TutorAgent(Agent):
    class HelpBehaviour(behaviour.CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                print(Fore.GREEN + f"[Tutor: {self.agent.name}] Pedido de ajuda de {msg.sender}: {msg.body}")
                response = Message(to=str(msg.sender))
                response.body = "ajuda: explicação sobre regressão linear enviada!"
                await self.send(response)
                print(Fore.GREEN + f"[tutor: {self.agent.name}] Ajuda enviada.")

    async def setup(self):
        print(f"tutor {self.name} ativo.")
        self.add_behaviour(self.HelpBehaviour())