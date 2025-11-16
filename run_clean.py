import os
import sys
import signal
import asyncio

# Configurar tratamento de erros SSL ANTES de importar SPADE
from ssl_utils import setup_ssl_error_handling, safe_shutdown
setup_ssl_error_handling()

os.environ["QASYNC_QTIMPL"] = "PySide6"

# Handler para shutdown gracioso
def signal_handler(signum, frame):
    print("\n🔻 Interrupção detectada - encerrando sistema...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

async def main():
    """Main function that starts the GUI with main.py logic integrated"""
    async with safe_shutdown():
        try:
            # Set event loop policy for better Windows compatibility
            if sys.platform.startswith('win'):
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            
            print("🚀 Iniciando Sistema Multi-Agente com Interface Gráfica...")
            
            # Import GUI modules
            import qasync
            from PySide6.QtWidgets import QApplication
            from interface.gui_main import MainWindow
            
            # Create Qt application with async support  
            app = QApplication(sys.argv)
            
            # Create main window
            main_window = MainWindow()
            
            # Show window
            main_window.show()
            
            # Set up qasync event loop
            loop = qasync.QEventLoop(app)
            asyncio.set_event_loop(loop)
            
            print("🖥️ Interface gráfica iniciada")
            print("💡 Use a interface para configurar e iniciar a simulação")
            
            # Run the Qt application
            with loop:
                loop.run_forever()
                
        except ImportError as e:
            if "PySide6" in str(e) or "qasync" in str(e):
                print("❌ Erro: Dependências GUI não encontradas")
                print("💡 Execute: pip install PySide6 qasync")
                
                # Fallback: run terminal version using main.py logic
                print("🔄 Executando versão terminal...")
                await run_terminal_simulation()
            else:
                raise e
        except KeyboardInterrupt:
            print("\n🔻 Sistema interrompido pelo usuário")
        except Exception as e:
            print(f"❌ Erro no sistema: {e}")
            import traceback
            traceback.print_exc()

async def run_terminal_simulation():
    """Fallback terminal simulation using main.py logic"""
    import random
    from student import StudentAgent
    from tutor import TutorAgent
    from peer import PeerAgent
    from resource_manager import ResourceManagerAgent
    
    print("🚀 Sistema Multi-Agente de Tutoria Iniciado (Modo Terminal)")
    
    # Use main.py configuration
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

    # Create students
    for i in range(1, number_students + 1):
        agents.update({f"student{i}": StudentAgent(f"student{i}@localhost", "1234", learning_style=random.choice(learning_styles))})

    print(f"📚 Criados {number_students} estudantes")
    
    # Create tutors
    for i in range(1, number_tutors + 1):
        cap = round(random.uniform(1, 3))
        agents.update({f"tutor{i}": TutorAgent(f"tutor{i}@localhost", "1234", discipline=random.choice(disciplines), expertise=random.uniform(0.5, 1), capacity=cap)})
    print(f"👨‍🏫 Criados {number_tutors} tutores")

    # Create peers
    for i in range(1, number_peers + 1):
        agents.update({f"peer{i}": PeerAgent(f"peer{i}@localhost", "1234")})
    
    print(f"👥 Criados {number_peers} peers")
    print(f"\n✅ Total: {number_students} estudantes, {number_tutors} tutores e {number_peers} peers.\n")
    
    # Start agents
    for name, agent in agents.items():
        try:
            await agent.start(auto_register=True)
            print(f"✅ {name} iniciado")
        except Exception as e:
            print(f"⚠️ {name} iniciado em modo simulação: {e}")

    await asyncio.sleep(1)

    # Subscribe students to all non-students (like main.py)
    for name, agent in agents.items():
        if name.startswith("student"):
            for other_name, other_agent in agents.items():
                if not other_name.startswith("student"):
                    try:
                        agent.presence.subscribe(other_agent.jid)
                        print(f"🔔 {name} subscreveu a {other_name}")
                    except Exception as e:
                        print(f"⚠️ Erro na subscrição {name} -> {other_name}: {e}")

    # Tutors and peers subscribe to resource manager
    for name, agent in agents.items():
        if name.startswith(("tutor", "peer")):
            try:
                agent.presence.subscribe(agents["resource"].jid)
                print(f"🔔 {name} subscreveu ao resource manager")
            except Exception as e:
                print(f"⚠️ Erro na subscrição {name} -> resource: {e}")

    await asyncio.sleep(2)
    print("📡 Subscrições configuradas")

    # Run simulation for 60 seconds (like main.py)
    print("⏱️ Simulação rodando por 60 segundos...")
    duration = 60
    start_time = asyncio.get_event_loop().time()
    
    while asyncio.get_event_loop().time() - start_time < duration:
        await asyncio.sleep(5)
        elapsed = asyncio.get_event_loop().time() - start_time
        remaining = duration - elapsed
        print(f"⏰ Tempo: {elapsed:.0f}s / {duration}s (restante: {remaining:.0f}s)")

    print("\n⏳ Simulação terminada. Parando agentes...")

    # Stop agents and show progress
    for name, agent in agents.items():
        try:
            if name.startswith("student"):
                print(f"📊 {name} progresso final: {agent.progress:.2f}")
            await agent.stop()
            print(f"🔻 {name} parado")
        except Exception as e:
            print(f"⚠️ Erro ao parar {name}: {e}")

    print("\n✅ Sistema encerrado com sucesso!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🔻 Sistema encerrado")
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        sys.exit(1)