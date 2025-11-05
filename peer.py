from spade.agent import Agent
from spade.message import Message
from spade import behaviour
import asyncio
from colorama import Fore

class PeerAgent(Agent):
    async def setup(self):
        print(Fore.MAGENTA + f"[Peer-{self.name}] Pronto para ajudar colegas 👥")
        self.add_behaviour(self.HelpPeers())

    class HelpPeers(behaviour.CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=5)
            if msg and msg.get_metadata("performative") == "peer-help":
                print(Fore.MAGENTA + f"[Peer-{self.agent.name}] ✅ Ajudando {msg.sender}")

                await asyncio.sleep(1)

                reply = Message(to=str(msg.sender))
                reply.set_metadata("performative", "inform")
                reply.body = "explicacao:Ajuda do peer enviada ✅"
                await self.send(reply)
