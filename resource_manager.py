from spade import behaviour
from spade.agent import Agent
from spade.message import Message
import spade
import asyncio
from colorama import Fore, Style, init


# ========================
# AGENTE RESOURCE MANAGER
# ========================
class ResourceManagerAgent(Agent):
    class ResourceBehaviour(behaviour.CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                print(Fore.RED + f"[ResourceManager: {self.agent.name}] Pedido recebido de {msg.sender}: {msg.body}")
                response = Message(to=str(msg.sender))
                response.body = "recurso_enviado: vídeo sobre regressão linear"
                await self.send(response)
                print(Fore.RED + f"[ResourceManager: {self.agent.name}] Recurso enviado.")

    async def setup(self):
        print("Resource Manager ativo.")
        self.add_behaviour(self.ResourceBehaviour())