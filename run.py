import os
import sys
import signal
import asyncio
import traceback
import logging

# Configurar logging para suprimir erros XML verbosos
logging.getLogger('slixmpp').setLevel(logging.CRITICAL)
logging.getLogger('pyjabber').setLevel(logging.CRITICAL)
logging.getLogger('xml').setLevel(logging.CRITICAL)

# Configurar tratamento de erros SSL ANTES de importar SPADE
from ssl_utils import setup_ssl_error_handling, safe_shutdown
setup_ssl_error_handling()

os.environ["QASYNC_QTIMPL"] = "PySide6"

# Interceptar todos os prints para enviar para a GUI
class PrintInterceptor:
    def __init__(self, gui_callback=None):
        self.gui_callback = gui_callback
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
    
    def write(self, text):
        # Escrever no console original
        self.original_stdout.write(text)
        self.original_stdout.flush()
        
        # Enviar para GUI se disponível
        if self.gui_callback and text.strip():
            try:
                self.gui_callback(text.strip())
            except Exception:
                pass  # Ignorar erros de GUI
    
    def flush(self):
        self.original_stdout.flush()
    
    def restore(self):
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr

# Global print interceptor
print_interceptor = None

# Handler para shutdown gracioso
def signal_handler(signum, frame):
    print("\n🔻 Interrupção detectada - encerrando sistema...")
    if print_interceptor:
        print_interceptor.restore()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

async def main():
    """Main function that starts the GUI properly with SPADE compatibility"""
    global print_interceptor
    
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
            
            # Configure print interceptor to send all output to GUI logs
            def gui_log_callback(text):
                if hasattr(main_window, 'logs_tab') and main_window.logs_tab:
                    main_window.logs_tab.log(text)
            
            print_interceptor = PrintInterceptor(gui_log_callback)
            sys.stdout = print_interceptor
            
            # Show window
            main_window.show()
            
            # Set up qasync event loop
            loop = qasync.QEventLoop(app)
            asyncio.set_event_loop(loop)
            
            print("🖥️ Interface gráfica iniciada")
            print("💡 Use a interface para configurar e iniciar a simulação")
            print("🔧 Para conectividade XMPP completa, execute 'spade run' em outro terminal")
            print("⚠️ Nota: Todos os logs dos agentes aparecerão na aba 'Logs'")
            
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
            traceback.print_exc()
        finally:
            if print_interceptor:
                print_interceptor.restore()

async def run_terminal_simulation():
    """Fallback terminal simulation using main.py logic with robust error handling"""
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

    print(f"\nCriados estudantes")
    
    # Create tutors
    for i in range(1, number_tutors + 1):
        random.seed()
        cap = round(random.uniform(1, 3))
        agents.update({f"tutor{i}": TutorAgent(f"tutor{i}@localhost", "1234", discipline=random.choice(disciplines), expertise=random.uniform(0.5, 1), capacity=cap)})
    print(f"\nCriados tutores")

    # Create peers
    for i in range(1, number_peers + 1):
        agents.update({f"peer{i}": PeerAgent(f"peer{i}@localhost", "1234")})
    
    print(f"\nCriados {number_students} estudantes, {number_tutors} tutores e {number_peers} peers.\n")
    
    # Start agents with robust error handling for XML and connection errors
    for name, agent in agents.items():
        try:
            await agent.start(auto_register=True)
        except Exception as e:
            # Em modo terminal, mostrar erros mas continuar
            print(f"⚠️ {name} teve problemas de conectividade: {e}")

    await asyncio.sleep(1)

    # Subscribe exactly like main.py
    for name, agent in agents.items():
        if name.startswith("student"):
            for n, a in agents.items():
                if n.startswith("student"):
                    continue
                try:
                    agent.presence.subscribe(a.jid)
                    print(f"[{agent.name}] 🔔 Subscribed to {a.jid}")
                except Exception as e:
                    print(f"⚠️ Erro na subscrição {name} -> {n}: {e}")
        else:
            if name.startswith("resource"):
                continue
            if "resource" in agents and agent.jid != agents["resource"].jid:
                try:
                    agent.presence.subscribe(agents["resource"].jid)
                    print(f"[{agent.name}] 🔔 Subscribed to {agents['resource'].jid}")
                except Exception as e:
                    print(f"⚠️ Erro na subscrição {name} -> resource: {e}")

    print("\n✅ Todos agentes iniciados. Simulação a correr...\n")

    # Run simulation for 30 seconds (exactly like main.py)
    await asyncio.sleep(30)

    print("\n⏳ Simulação terminada. A encerrar agentes...\n")

    # Stop agents exactly like main.py
    for name, agent in agents.items():
        print(f"🔻 A parar {name}...")
        if name.startswith("student"):
            print(f"Progresso Final: {agent.initial_progress} -> {agent.progress}")
        try:
            await agent.stop()
        except Exception as e:
            print(f"⚠️ Erro ao parar {name}: {e}")

    print("\n✅ Todos agentes terminados. Sistema encerrado.\n")

def run_system():
    """Wrapper function for different execution modes"""
    try:
        # Verificar se devemos usar spade.run() ou asyncio.run()
        use_spade = False
        
        # Tentar detectar se spade está disponível e se devemos usá-lo
        try:
            import spade
            # Verificar se há argumentos específicos ou variáveis de ambiente
            if '--use-spade' in sys.argv or os.environ.get('USE_SPADE_RUN'):
                use_spade = True
                print("📡 Modo SPADE explicitamente solicitado")
        except ImportError:
            pass
        
        if use_spade:
            print("📡 Executando com spade.run() para compatibilidade XMPP...")
            try:
                spade.run(main())
            except Exception as e:
                print(f"⚠️ spade.run() falhou: {e}")
                print("🔄 Tentando com asyncio.run()...")
                asyncio.run(main())
        else:
            print("🔧 Executando com asyncio.run() (padrão)...")
            asyncio.run(main())
            
    except KeyboardInterrupt:
        print("\n🔻 Sistema encerrado pelo usuário")
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        if '--debug' in sys.argv:
            traceback.print_exc()
        input("\nPressione ENTER para sair...")

if __name__ == "__main__":
    print("🎯 Sistema Multi-Agente ISIA")
    print("💡 Para usar spade.run() adicione: --use-spade")
    print("🐛 Para debug detalhado adicione: --debug")
    print("📋 Todos os logs dos agentes aparecerão na interface")
    print("─" * 50)
    
    run_system()
