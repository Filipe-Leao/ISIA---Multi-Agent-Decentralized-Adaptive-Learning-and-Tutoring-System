from spade.agent import Agent
from spade.message import Message
from spade import behaviour
from colorama import Fore

class ResourceManagerAgent(Agent):
    class ResourceBehaviour(behaviour.CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if not msg:
                return

            parts = dict(p.split(":") for p in msg.body.split(";"))
            topic = parts.get("topic", "desconhecido")
            progress = float(parts.get("progress", 0))
            
            # PT ↔ EN mapping for learning styles
            style_map = {
                "visual": "visual",
                "auditory": "auditory",
                "cinestésico": "kinesthetic",
                "kinesthetic": "kinesthetic"
            }
            style = style_map.get(parts.get("style", ""), "visual")

            if progress < 0.5:
                resource = f"Vídeo {style} introdutório sobre {topic}"
            else:
                resource = f"Exercício {style} avançado sobre {topic}"

            resp = Message(to=str(msg.sender))
            resp.body = f"resource:{resource}"
            await self.send(resp)

            print(Fore.YELLOW + f"[Resource] recurso enviado → {msg.sender}: {resource}")

    async def setup(self):
        print("Resource Manager ativo.")
        self.add_behaviour(self.ResourceBehaviour())
