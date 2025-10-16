from spade import behaviour
from spade.agent import Agent
from spade.message import Message
import spade
import asyncio

# ========================
# AGENTE DO ESTUDANTE
# ========================
class StudentAgent(Agent):
    class StudyBehaviour(behaviour.CyclicBehaviour):
        async def on_start(self):
            print(f"[{self}] Iniciando rotina de estudo...")
            self.study_progress = 0
            self.resources = []
            await asyncio.sleep(3)  # Espera para garantir que os outros agentes estão ativos

        async def run(self):
            if self.study_progress < 100:
                print(f"[{self}] Progresso atual: {self.study_progress}%")

                await self.request_resource("video_sobre_ML")

                if self.study_progress < 50:
                    await self.ask_for_help("Preciso de ajuda com regressão linear")

                self.study_progress += 20
                await asyncio.sleep(5)
            else:
                print(f"[{self}] Estudo completo! 🚀")
                self.kill()
            

        async def request_resource(self, resource_name):
            msg = Message(
                to="resource_manager@localhost",
                body=f"pedido_recurso:{resource_name}"
            )
            print(f"[{self}] A pedir recurso: {resource_name}")
            await self.send(msg)

        async def ask_for_help(self, question):
            msg = Message(
                to="tutor1@localhost",
                body=f"pedido_ajuda:{question}"
            )
            print(f"[{self}] A pedir ajuda ao tutor: {question}")
            await self.send(msg)

    async def setup(self):
        print(f"👩‍🎓 {self.name} iniciado.")
        self.study = self.StudyBehaviour()
        self.add_behaviour(self.study)


# ========================
# AGENTE RESOURCE MANAGER
# ========================
class ResourceManagerAgent(Agent):
    class ResourceBehaviour(behaviour.CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                print(f"[ResourceManager] Pedido recebido de {msg.sender}: {msg.body}")
                response = Message(to=str(msg.sender))
                response.body = "recurso_enviado: vídeo sobre regressão linear"
                await self.send(response)
                print("[ResourceManager] Recurso enviado.")

    async def setup(self):
        print("📦 Resource Manager ativo.")
        self.add_behaviour(self.ResourceBehaviour())


# ========================
# AGENTE TUTOR
# ========================
class TutorAgent(Agent):
    class HelpBehaviour(behaviour.CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                print(f"[Tutor] Pedido de ajuda de {msg.sender}: {msg.body}")
                response = Message(to=str(msg.sender))
                response.body = "ajuda: explicação sobre regressão linear enviada!"
                await self.send(response)
                print("[Tutor] Ajuda enviada.")

    async def setup(self):
        print("👨‍🏫 Tutor ativo.")
        self.add_behaviour(self.HelpBehaviour())


# ========================
# EXECUÇÃO
# ========================
async def main():
    student = StudentAgent("student@localhost", "1234")
    tutor = TutorAgent("tutor1@localhost", "1234")
    manager = ResourceManagerAgent("resource_manager@localhost", "1234")

    await tutor.start(auto_register=True)
    await manager.start(auto_register=True)
    await asyncio.sleep(1)  # Garante que estão prontos
    await student.start(auto_register=True)

    # Mantém o loop ativo
    while student.is_alive():
        if student.study.is_killed():
            await student.stop()
        await asyncio.sleep(1)

    await tutor.stop()
    await manager.stop()
    print("Encerrando agentes...")


if __name__ == "__main__":
    spade.run(main())

