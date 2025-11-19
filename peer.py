from spade.agent import Agent
from spade.message import Message
from spade.behaviour import *
from spade.presence import *
import asyncio
from colorama import Fore, Style

class PeerAgent(Agent):
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.can_start_helping = False  # Flag to control start
        self.is_stopping = False  # Flag to stop behaviours
    
    async def setup(self):
        print(Fore.MAGENTA + f"[Peer-{self.name}] Started - Ready to help students" + Style.RESET_ALL)
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
            # 🔴 CHECK IF STOPPING
            if self.agent.is_stopping:
                return
            
            # 🔴 WAIT UNTIL ALL AGENTS ARE READY
            if not self.agent.can_start_helping:
                await asyncio.sleep(1)
                return
            
            msg = await self.receive(timeout=5)
            if msg and msg.get_metadata("performative") == "peer-help":
                print(Fore.MAGENTA + f"[Peer-{self.agent.name}] ✅ Helping {msg.sender}" + Style.RESET_ALL)

                await asyncio.sleep(1)

                reply = Message(to=str(msg.sender))
                reply.set_metadata("performative", "inform")
                reply.body = "explanation:Peer help sent ✅"
                await self.send(reply)
