import asyncio
import random
from student import StudentAgent
from tutor import TutorAgent
from peer import PeerAgent
from resource_manager import ResourceManagerAgent

async def main():
    # Criar agentes
    number_students = 5
    number_tutors = 3
    number_peers = 2

    agents = {
<<<<<<< HEAD
        "student1": StudentAgent("student1@localhost", "1234"),
        "student2": StudentAgent("student2@localhost", "1234"),
        "tutor1": TutorAgent("tutor1@localhost", "1234", capacity = 1),
        "tutor2": TutorAgent("tutor2@localhost", "1234", capacity = 1),
        "peer1": PeerAgent("peer1@localhost", "1234"),
        "peer2": PeerAgent("peer2@localhost", "1234"),
=======
>>>>>>> c0226c2 (Autocreation of agents. Added subscriptions)
        "resource": ResourceManagerAgent("resource@localhost", "1234"),
    }

    for i in range(1,number_students + 1):
        agents.update({f"student{i}": StudentAgent(f"student{i}@localhost", "1234")})

    for i in range(1,number_students + 1):
        agents.update({f"tutor{i}": TutorAgent(f"tutor{i}@localhost", "1234", capacity=random.uniform(1,3))})
    
    for i in range(1,number_students + 1):
        agents.update({f"peer{i}": PeerAgent(f"peer{i}@localhost", "1234")})
    
    print(agents)

    # Start agents
    for name, agent in agents.items():
        agent.to_subscribe = []
        if name.startswith("student"):
            for n, a in agents.items():
                if n.startswith("student"): continue
                agent.to_subscribe.append(a.jid)
        
        else:
            agent.to_subscribe.append(agents["resource"].jid)
                    

        print(f"{name} trying to subscribe to {agent.to_subscribe}")
        await agent.start(auto_register=True)

    await asyncio.timeout(5)

    print("\n⏳ Simulação terminada. A encerrar agentes...\n")

    # Stop agents
    for name, agent in agents.items():
        print(f"🔻 A parar {name}...")
        await agent.stop()

    print("\n✅ Todos agentes terminados. Sistema encerrado.\n")

if __name__ == "__main__":
    asyncio.run(main())

