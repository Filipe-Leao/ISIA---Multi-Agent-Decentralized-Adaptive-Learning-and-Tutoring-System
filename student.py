from spade import behaviour
from spade.agent import Agent
from spade.message import Message
import spade
import asyncio
from colorama import Fore, Style, init

# ========================
# AGENTE DO ESTUDANTE
# ========================
class StudentAgent(Agent):
    class StudyBehaviour(behaviour.CyclicBehaviour):
        async def on_start(self):
            print(f"Iniciando rotina de estudo...")
            self.study_progress = 0
            self.resources = []
            await asyncio.sleep(3)  # Espera para garantir que os outros agentes estão ativos

        async def run(self):
            if self.study_progress < 100:
                print(Fore.BLUE + f"[student: {self.agent.name}] Progresso atual: {self.study_progress}%")

                await self.request_resource("video_sobre_ML")

                if self.study_progress < 50:
                    await self.ask_for_help(f"Preciso de ajuda com regressão linear")

                self.study_progress += 20
                await asyncio.sleep(5)
            else:
                print(Fore.BLUE + f"[student: {self.agent.name}] Estudo completo!")
                self.kill()
            

        async def request_resource(self, resource_name):
            msg = Message(
                to="resource_manager@localhost",
                body=f"pedido_recurso:{resource_name}"
            )
            print(Fore.BLUE + f"[student: {self.agent.name}] A pedir recurso: {resource_name}")
            await self.send(msg)

        async def ask_for_help(self, question):
            msg = Message(
                to="tutor1@localhost",
                body=f"pedido_ajuda:{question}"
            )
            print(Fore.BLUE + f"[student: {self.agent.name}] A pedir ajuda ao tutor: {question}")
            await self.send(msg)

    async def setup(self):
        print(f"{self.name} iniciado.")
        self.study = self.StudyBehaviour()
        self.add_behaviour(self.study)
