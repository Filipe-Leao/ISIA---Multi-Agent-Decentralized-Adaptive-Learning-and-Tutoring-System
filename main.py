import asyncio
import random
from student import StudentAgent
from tutor import TutorAgent
from peer import PeerAgent
from resource_manager import ResourceManagerAgent

async def simulate(agents, duration_seconds=None):
    """Simulate the multi-agent tutoring system for a specified duration or until the end."""
    if duration_seconds is None:
        print("Simulação a decorrer até ao fim dos agentes...\n")
        while any(agent.is_alive() for name, agent in agents.items() if name.startswith("student")):
            for name, agent in agents.items():
                if name.startswith("student") and not agent.is_alive():
                    print(f"❌ Estudante {name} terminou a sua atividade.")
            #print("⏳ Agentes ainda ativos, a aguardar...")
            await asyncio.sleep(1)
    else:
        print(f"Simulação a decorrer por {duration_seconds} segundos...\n")
        await asyncio.sleep(duration_seconds)
    return
async def main():
    # Criar agentes
    number_students = 10
    number_tutors = 3
    number_peers = 1

    disciplines = [
                    "estatística bayesiana", 
                    "aprendizagem automática", 
                    "programação", 
                    "estatística", 
                    "português", 
                    "álgebra"
                ]
    learning_styles = ["visual", "auditory", "cinestésico", "kinesthetic"]
    
    agents = {
        "resource": ResourceManagerAgent("resource@localhost", "1234"),
    }

    for i in range(1, number_students + 1):
        agents.update({f"student{i}": StudentAgent(f"student{i}@localhost", "1234", learning_style=random.choice(learning_styles), disciplines=disciplines)})

    print(f"\nCriados estudantes")
    for i in range(1, number_tutors + 1):
        random.seed()
        cap = round(random.uniform(1, 3))
        agents.update({f"tutor{i}": TutorAgent(f"tutor{i}@localhost", "1234", discipline=random.choice(disciplines), expertise=random.uniform(0.5, 1), capacity=cap)})
    print(f"\nCriados tutores")

    for i in range(1, number_peers + 1):
        agents.update({f"peer{i}": PeerAgent(f"peer{i}@localhost", "1234")})
    
    print(f"\nCriados {number_students} estudantes, {number_tutors} tutores e {number_peers} peers.\n")
    
    # Start agents
    for name, agent in agents.items():
        await agent.start(auto_register=True)

    await asyncio.sleep(1)

    # Fazer subscrições centralmente: estudantes subscrevem a todos os não-estudantes
    for name, agent in agents.items():
        if name.startswith("student"):
            for n, a in agents.items():
                if n.startswith("student"):
                    continue
                agent.presence.subscribe(a.jid)
                print(f"[{agent.name}] 🔔 Subscribed to {a.jid}")
        else:
            if name.startswith("resource"):
                continue
            if "resource" in agents and agent.jid != agents["resource"].jid:
                agent.presence.subscribe(agents["resource"].jid)
                print(f"[{agent.name}] 🔔 Subscribed to {agents['resource'].jid}")

    print("\n✅ Todos agentes iniciados. Simulação a correr...\n")

    # Tempo da simulação
    await simulate(agents, duration_seconds=None)

    print("\n⏳ Simulação terminada. A encerrar agentes...\n")

    # Stop agents
    for name, agent in agents.items():
        print(f"🔻 A parar {name}...")
        if name.startswith("student"):
            print(f"Progresso Final: {agent.initial_progress} -> {agent.progress}")
            for discipline, knowledge in agent.knowledge.items():
                print(f" - {discipline}:  {agent.initial_knowledge[discipline]:.2f} -> {knowledge:.2f}")
        await agent.stop()

    print("\n✅ Todos agentes terminados. Sistema encerrado.\n")

if __name__ == "__main__":
    asyncio.run(main())
    
