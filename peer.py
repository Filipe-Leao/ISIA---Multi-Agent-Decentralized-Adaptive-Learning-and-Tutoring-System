from spade.agent import Agent
from spade.message import Message
from spade.behaviour import *
from spade.presence import *
import asyncio
from colorama import Fore

class PeerAgent(Agent):
    async def setup(self):
        print(Fore.MAGENTA + f"[Peer-{self.name}] Pronto para ajudar colegas 👥")
        self.add_behaviour(self.HelpPeers())
        self.add_behaviour(self.Subcreption())

    class Subcreption(OneShotBehaviour):
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
            
    class HelpPeers(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=3)
            if msg and msg.get_metadata("performative") == "peer-help":
                print(Fore.MAGENTA + f"[Peer-{self.agent.name}] ✅ Ajudando {msg.sender}")

                await asyncio.sleep(1)

                reply = Message(to=str(msg.sender))
                reply.set_metadata("performative", "inform")
                reply.body = "explicacao:Ajuda do peer enviada ✅"
                await self.send(reply)
