import sys
import os

# IMPORTANTE: Configurar SSL error handling e qasync ANTES de importar qualquer coisa
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ssl_utils import setup_ssl_error_handling
setup_ssl_error_handling()

os.environ['QASYNC_QTIMPL'] = 'PySide6'

import asyncio
import qasync
import random
from datetime import datetime

from utils.style import CHALKBOARD_STYLE
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                               QVBoxLayout, QTabWidget, QLabel, QSplitter)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPalette, QBrush

from gui_config_panel import ConfigPanel
from gui_agent_status import AgentStatusPanel
from gui_tabs import LogsTab, MetricsTab
# Import the actual agent classes like main.py does
from student import StudentAgent
from tutor import TutorAgent
from peer import PeerAgent
from resource_manager import ResourceManagerAgent


class MainSimulation:
    """Main simulation logic adapted from main.py with robust error handling"""

    def __init__(self, gui_window=None):
        self.gui = gui_window
        self.agents = {}
        self.running = False
        self.sim_task = None
        
    def set_gui(self, gui_window):
        """Connect to GUI window for logging"""
        self.gui = gui_window
        
    def log(self, text):
        """Log message to GUI"""
        if self.gui and hasattr(self.gui, 'logs_tab'):
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.gui.logs_tab.log(f"[{timestamp}] {text}")
            
    async def run_simulation(self, num_students=10, num_tutors=3, num_peers=1, duration=30, server="localhost", password="1234"):
        """Run simulation exactly like main.py with robust error handling"""
        try:
            self.running = True
            self.log("🚀 Sistema Multi-Agente de Tutoria Iniciado")
            
            # Use main.py configuration exactly
            number_students = num_students
            number_tutors = num_tutors
            number_peers = num_peers

            disciplines = [
                "estatística bayesiana", 
                "aprendizagem automática", 
                "programação", 
                "estatística", 
                "português", 
                "álgebra"
            ]
            learning_styles = ["visual", "auditory", "cinestésico", "kinesthetic"]
            
            # Create agents exactly like main.py
            self.agents = {
                "resource": ResourceManagerAgent(f"resource@{server}", password),
            }
            
            # Create students exactly like main.py
            for i in range(1, number_students + 1):
                self.agents.update({f"student{i}": StudentAgent(f"student{i}@{server}", password, learning_style=random.choice(learning_styles))})

            self.log(f"📚 Criados {number_students} estudantes")
            
            # Create tutors exactly like main.py
            for i in range(1, number_tutors + 1):
                random.seed()
                cap = round(random.uniform(1, 3))
                self.agents.update({f"tutor{i}": TutorAgent(f"tutor{i}@{server}", password, discipline=random.choice(disciplines), expertise=random.uniform(0.5, 1), capacity=cap)})
            self.log(f"👨‍🏫 Criados {number_tutors} tutores")

            # Create peers exactly like main.py
            for i in range(1, number_peers + 1):
                self.agents.update({f"peer{i}": PeerAgent(f"peer{i}@{server}", password)})
            
            self.log(f"👥 Criados {number_peers} peers")
            self.log(f"✅ Total: {number_students} estudantes, {number_tutors} tutores e {number_peers} peers")
            
            # Start agents exactly like main.py with robust error handling
            self.log("🔄 Iniciando agentes...")
            simulation_mode = False
            
            for name, agent in self.agents.items():
                try:
                    result = await agent.start(auto_register=True)
                    if result:
                        if hasattr(agent, 'simulation_mode') and agent.simulation_mode:
                            self.log(f"🤖 {name} iniciado em modo simulação")
                            simulation_mode = True
                        else:
                            self.log(f"✅ {name} conectado ao XMPP")
                    else:
                        self.log(f"🤖 {name} iniciado em modo simulação")
                        simulation_mode = True
                except Exception as e:
                    self.log(f"🤖 {name} em modo simulação: {e}")
                    simulation_mode = True

            if simulation_mode:
                self.log("⚙️ Sistema funcionando em modo simulação offline")
                self.log("💡 Para conectividade XMPP real, execute 'spade run' em outro terminal")
            
            await asyncio.sleep(1)

            # Subscribe students to all non-students (exactly like main.py)
            # Só fazer subscrições se não estivermos em modo simulação
            if not simulation_mode:
                self.log("🔗 Configurando subscrições XMPP...")
                for name, agent in self.agents.items():
                    if name.startswith("student"):
                        for other_name, other_agent in self.agents.items():
                            if not other_name.startswith("student"):
                                try:
                                    agent.presence.subscribe(other_agent.jid)
                                    self.log(f"🔔 {name} subscreveu a {other_name}")
                                except Exception as e:
                                    self.log(f"⚠️ Erro na subscrição {name} -> {other_name}: {e}")

                # Tutors and peers subscribe to resource manager (like main.py)
                for name, agent in self.agents.items():
                    if name.startswith(("tutor", "peer")):
                        try:
                            agent.presence.subscribe(self.agents["resource"].jid)
                            self.log(f"🔔 {name} subscreveu ao resource manager")
                        except Exception as e:
                            self.log(f"⚠️ Erro na subscrição {name} -> resource: {e}")

                await asyncio.sleep(2)
                self.log("📡 Subscrições XMPP configuradas")
            else:
                self.log("📡 Subscrições ignoradas (modo simulação)")

            self.log(f"⏱️ Simulação rodando por {duration} segundos...")

            # Monitor loop exactly like main.py
            start_time = asyncio.get_event_loop().time()
            
            while asyncio.get_event_loop().time() - start_time < duration and self.running:
                await asyncio.sleep(5)
                elapsed = asyncio.get_event_loop().time() - start_time
                remaining = duration - elapsed
                self.log(f"⏰ Tempo: {elapsed:.0f}s / {duration}s (restante: {remaining:.0f}s)")
                
                # Show student progress
                for name, agent in self.agents.items():
                    if name.startswith("student") and hasattr(agent, 'progress'):
                        self.log(f"📚 {name}: progresso {agent.progress:.2f}")

            self.log("⏳ Simulação terminada. Parando agentes...")

            # Stop agents and show progress exactly like main.py
            for name, agent in self.agents.items():
                try:
                    if name.startswith("student"):
                        self.log(f"📊 {name} progresso final: {agent.progress:.2f}")
                    await agent.stop()
                    self.log(f"🔻 {name} parado")
                except Exception as e:
                    self.log(f"⚠️ Erro ao parar {name}: {e}")

            if simulation_mode:
                self.log("✅ Simulação offline concluída!")
            else:
                self.log("✅ Simulação XMPP concluída!")
            
        except Exception as e:
            self.log(f"❌ Erro na simulação: {e}")
            import traceback
            self.log(f"🔍 Detalhes: {traceback.format_exc()}")
        finally:
            self.running = False
    
    async def stop_simulation(self):
        """Stop the running simulation"""
        if not self.running:
            self.log("⚠️ Simulação não está rodando")
            return
            
        self.log("🛑 Parando simulação...")
        self.running = False
        
        if hasattr(self, 'agents') and self.agents:
            for name, agent in self.agents.items():
                try:
                    self.log(f"🔻 Parando {name}...")
                    await agent.stop()
                except Exception as e:
                    self.log(f"⚠️ Erro ao parar {name}: {e}")
            
            self.agents.clear()
        
        self.log("✅ Simulação parada com sucesso")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ISIA - Sistema Multi-Agente de Tutoria")
        self.setGeometry(100, 100, 1400, 900)
        
        # Aplicar estilo
        self.setStyleSheet(CHALKBOARD_STYLE)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QHBoxLayout(central_widget)
        
        # Criar splitter principal
        main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(main_splitter)
        
        # Painel esquerdo - configuração e status
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Título
        title = QLabel("🎓 ISIA Multi-Agent System")
        title.setObjectName("title")
        left_layout.addWidget(title)
        
        # Criar instância de simulação primeiro
        self.simulation = MainSimulation(self)
        
        # Painel de configuração (precisa da instância de simulação)
        self.config_panel = ConfigPanel(self.simulation)
        left_layout.addWidget(self.config_panel)
        
        # Status dos agentes
        self.agent_status = AgentStatusPanel()
        left_layout.addWidget(self.agent_status)
        
        main_splitter.addWidget(left_panel)
        
        # Painel direito - logs e métricas
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Tabs para logs e métricas
        self.tabs = QTabWidget()
        self.logs_tab = LogsTab()
        self.metrics_tab = MetricsTab()
        
        self.tabs.addTab(self.logs_tab, "📜 Logs")
        self.tabs.addTab(self.metrics_tab, "📊 Métricas")
        
        right_layout.addWidget(self.tabs)
        main_splitter.addWidget(right_panel)
        
        # Configurar proporções do splitter
        main_splitter.setSizes([400, 1000])
        
        # A simulação já foi criada acima
        # self.simulation já existe e está conectada ao config_panel

def start_gui_app():
    """Função para iniciar a aplicação GUI"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Configurar loop assíncrono
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    # Criar e mostrar janela principal
    window = MainWindow()
    window.show()
    
    print("🖥️ Interface gráfica ISIA iniciada")
    print("💡 Use o painel de configuração para iniciar a simulação")
    
    # Executar aplicação
    with loop:
        loop.run_forever()

if __name__ == "__main__":
    start_gui_app()


