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
            print(f"Starting study routine...")
            self.study_progress = 0
            self.resources = []
            await asyncio.sleep(3)  # Wait to ensure other agents are active

        async def run(self):
            if self.study_progress < 100:
                print(Fore.BLUE + f"[student: {self.agent.name}] Current progress: {self.study_progress}%")

                await self.request_resource("video_about_ML")

                if self.study_progress < 50:
                    await self.ask_for_help(f"I need help with linear regression")

                self.study_progress += 20
                await asyncio.sleep(5)
            else:
                print(Fore.BLUE + f"[student: {self.agent.name}] Study completed!")
                self.kill()
            

        async def request_resource(self, resource_name):
            msg = Message(
                to="resource_manager@localhost",
                body=f"resource_request:{resource_name}"
            )
            print(Fore.BLUE + f"[student: {self.agent.name}] Requesting resource: {resource_name}")
            await self.send(msg)

        async def ask_for_help(self, question):
            msg = Message(
                to="tutor1@localhost",
                body=f"help_request:{question}"
            )
            print(Fore.BLUE + f"[student: {self.agent.name}] Asking tutor for help: {question}")
            await self.send(msg)

    async def setup(self):
        print(f"{self.name} started.")
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
                print(Fore.RED + f"[ResourceManager: {self.agent.name}] Request received from {msg.sender}: {msg.body}")
                response = Message(to=str(msg.sender))
                response.body = "resource_sent: video about linear regression"
                await self.send(response)
                print(Fore.RED + f"[ResourceManager: {self.agent.name}] Resource sent.")

    async def setup(self):
        print("Resource Manager active.")
        self.add_behaviour(self.ResourceBehaviour())


# ========================
# AGENTE TUTOR
# ========================
class TutorAgent(Agent):
    class HelpBehaviour(behaviour.CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                print(Fore.GREEN + f"[Tutor: {self.agent.name}] Help request from {msg.sender}: {msg.body}")
                response = Message(to=str(msg.sender))
                response.body = "help: explanation about linear regression sent!"
                await self.send(response)
                print(Fore.GREEN + f"[tutor: {self.agent.name}] Help sent.")

    async def setup(self):
        print(f"tutor {self.name} active.")
        self.add_behaviour(self.HelpBehaviour())


# ========================
# EXECUÇÃO
# ========================
async def main():
    init(autoreset=True)

    student = StudentAgent("Joao@localhost", "1234")
    tutor = TutorAgent("tutor1@localhost", "1234")
    manager = ResourceManagerAgent("resource_manager@localhost", "1234")

    await tutor.start(auto_register=True)
    await manager.start(auto_register=True)
    await asyncio.sleep(1)  # Ensures they are ready
    await student.start(auto_register=True)

    # Keeps the loop active
    while student.is_alive():
        if student.study.is_killed():
            await student.stop()
        await asyncio.sleep(1)

    await tutor.stop()
    await manager.stop()
    print("Shutting down agents...")


if __name__ == "__main__":
    spade.run(main())

