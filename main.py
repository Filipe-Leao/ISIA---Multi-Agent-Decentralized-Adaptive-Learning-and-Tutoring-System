import asyncio
from student import StudentAgent
from tutor import TutorAgent
from peer import PeerAgent
from resource_manager import ResourceManagerAgent

async def main():
    # Criar agentes
    agents = {
        "student1": StudentAgent("student1@localhost", "1234"),
        "student2": StudentAgent("student2@localhost", "1234"),
        "tutor1": TutorAgent("tutor1@localhost", "1234", capacity = 1),
        "tutor2": TutorAgent("tutor2@localhost", "1234", capacity = 1),
        "peer1": PeerAgent("peer1@localhost", "1234"),
        "peer2": PeerAgent("peer2@localhost", "1234"),
        "resource": ResourceManagerAgent("resource@localhost", "1234"),
    }

    # Start agents
    for name, agent in agents.items():
        await agent.start(auto_register=True)

    print("\n✅ Todos agentes iniciados. Simulação a correr...\n")

    # Tempo da simulação
    await asyncio.sleep(20)

    print("\n⏳ Simulação terminada. A encerrar agentes...\n")

    # Stop agents
    for name, agent in agents.items():
        print(f"🔻 A parar {name}...")
        await agent.stop()

    print("\n✅ Todos agentes terminados. Sistema encerrado.\n")

if __name__ == "__main__":
    asyncio.run(main())

