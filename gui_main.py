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
    """Main simulation logic adapted exactly from main.py"""

    def __init__(self, gui_window=None):
        self.gui = gui_window
        self.agents = {}
        self._running = False
        
    @property
    def running(self):
        return self._running
        
    def set_gui(self, gui_window):
        """Connect to GUI window for logging"""
        self.gui = gui_window
        
    def log(self, text):
        """Log message to GUI and console"""
        # Print to console (will be intercepted and sent to GUI automatically)
        print(text)

    async def simulate(self, agents, duration=None):
        """Simulate the multi-agent tutoring system for a specified duration or until the end."""
        if duration is None:
            print("Simulação a decorrer até ao fim dos agentes...\n")
            start_time = asyncio.get_event_loop().time()
            while any(agent.is_alive() for name, agent in agents.items() if name.startswith("student")):
                # Update GUI panels if available
                if self.gui and hasattr(self.gui, 'agent_status'):
                    self.gui.agent_status.update_status(agents)
                    
                # Update metrics
                if self.gui and hasattr(self.gui, 'metrics_tab'):
                    self.gui.metrics_tab.update_metrics(agents)

                # Show periodic progress (every 5 seconds)
                elapsed = asyncio.get_event_loop().time() - start_time
                if int(elapsed) % 5 == 0 and elapsed > 0:
                    remaining = duration - elapsed
                    print(f"⏰ Simulação: {elapsed:.0f}s / {duration}s (restante: {remaining:.0f}s)")

                for name, agent in agents.items():
                    if name.startswith("student") and not agent.is_alive():
                        print(f"❌ Estudante {name} terminou a sua atividade.")
                #print("⏳ Agentes ainda ativos, a aguardar...")
                await asyncio.sleep(1)
        else:
            print(f"Simulação a decorrer por {duration} segundos...\n")
            while asyncio.get_event_loop().time() - start_time < duration:
                await asyncio.sleep(1)
                # Update GUI panels if available
                if self.gui and hasattr(self.gui, 'agent_status'):
                    self.gui.agent_status.update_status(agents)
                    
                # Update metrics
                if self.gui and hasattr(self.gui, 'metrics_tab'):
                    self.gui.metrics_tab.update_metrics(agents)

                # Show periodic progress (every 5 seconds)
                elapsed = asyncio.get_event_loop().time() - start_time
                if int(elapsed) % 5 == 0 and elapsed > 0:
                    remaining = duration - elapsed
                    print(f"⏰ Simulação: {elapsed:.0f}s / {duration}s (restante: {remaining:.0f}s)")

                for name, agent in agents.items():
                    if name.startswith("student") and not agent.is_alive():
                        print(f"❌ Estudante {name} terminou a sua atividade.")
                await asyncio.sleep(1)
        return
        
    async def run_simulation(self, num_students=10, num_tutors=3, num_peers=1, duration=30, server="localhost", password="1234"):
        """Run simulation using EXACT main.py logic"""
        try:
            self._running = True
            
            # Use main.py configuration exactly - same variable names and flow
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
            agents = {
                "resource": ResourceManagerAgent(f"resource@{server}", password),
            }

            # Create students exactly like main.py
            for i in range(1, number_students + 1):
                agents.update({f"student{i}": StudentAgent(f"student{i}@{server}", password, learning_style=random.choice(learning_styles), disciplines=disciplines)})

            print(f"\nCriados estudantes")
            
            # Create tutors exactly like main.py  
            for i in range(1, number_tutors + 1):
                random.seed()
                cap = round(random.uniform(1, 3))
                agents.update({f"tutor{i}": TutorAgent(f"tutor{i}@{server}", password, discipline=random.choice(disciplines), expertise=random.uniform(0.5, 1), capacity=cap)})
            print(f"\nCriados tutores")

            # Create peers exactly like main.py
            for i in range(1, number_peers + 1):
                agents.update({f"peer{i}": PeerAgent(f"peer{i}@{server}", password)})
            
            print(f"\nCriados {number_students} estudantes, {number_tutors} tutores e {number_peers} peers.\n")
            
            # Store agents for stopping later
            self.agents = agents
            
            # Start agents exactly like main.py
            for name, agent in agents.items():
                await agent.start(auto_register=True)

            await asyncio.sleep(1)

            # Fazer subscrições centralmente: estudantes subscrevem a todos os não-estudantes (EXACTLY like main.py)
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

            # Run simulation with periodic updates for GUI
            await self.simulate(agents, duration=duration)

            print("\n⏳ Simulação terminada. A encerrar agentes...\n")

            # Stop agents exactly like main.py
            for name, agent in agents.items():
                print(f"🔻 A parar {name}...")
                if name.startswith("student"):
                    print(f"Progresso Final: {agent.initial_progress} -> {agent.progress}")
                await agent.stop()

            print("\n✅ Todos agentes terminados. Sistema encerrado.\n")
            
        except Exception as e:
            print(f"❌ Erro na simulação: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self._running = False
    
    async def stop_simulation(self):
        """Stop the running simulation"""
        if not self._running:
            print("⚠️ Simulação não está rodando")
            return
            
        print("🛑 Parando simulação...")
        self._running = False
        
        if hasattr(self, 'agents') and self.agents:
            for name, agent in self.agents.items():
                try:
                    print(f"🔻 Parando {name}...")
                    await agent.stop()
                except Exception as e:
                    print(f"⚠️ Erro ao parar {name}: {e}")
            
            self.agents.clear()
        
        print("✅ Simulação parada com sucesso")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎓 ISIA - Sistema Multi-Agente de Tutoria Adaptativa")
        self.setGeometry(100, 100, 1400, 900)
        
        # Setup background first
        self.setup_background()
        
        # Main simulation logic (replaces SimulationController)
        self.simulation = MainSimulation(self)
        
        # Central Widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Title Label
        title = QLabel("🎓 ISIA - Sistema Inteligente de Tutoria Adaptativa")
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #ffffff;
                background-color: rgba(34, 34, 34, 200);
                padding: 15px;
                border-radius: 8px;
                border: 2px solid #4CAF50;
            }
        """)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Main content splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Configuration + Status
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(15)
        
        # Config Panel (now with new simulation logic)
        self.config_panel = ConfigPanel(self.simulation)
        left_layout.addWidget(self.config_panel)
        
        # Agent Status Panel
        self.agent_status = AgentStatusPanel()
        left_layout.addWidget(self.agent_status, 1)
        
        splitter.addWidget(left_panel)
        
        # Right panel - Tabs
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Tab widget
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                background-color: rgba(255, 255, 255, 230);
                border: 2px solid #4CAF50;
                border-radius: 8px;
            }
            QTabBar::tab {
                background-color: rgba(100, 100, 100, 200);
                color: white;
                padding: 10px 20px;
                margin: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #4CAF50;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: rgba(76, 175, 80, 150);
            }
        """)
        
        # Add tabs
        self.logs_tab = LogsTab()
        self.metrics_tab = MetricsTab()
        
        tabs.addTab(self.logs_tab, "📋 Logs do Sistema")
        tabs.addTab(self.metrics_tab, "📊 Métricas")
        
        right_layout.addWidget(tabs)
        splitter.addWidget(right_panel)
        
        # Splitter proportions
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        main_layout.addWidget(splitter, 1)
        
        # Initial log message
        self.logs_tab.log("🌟 Sistema ISIA iniciado - Interface do main.py")
        self.logs_tab.log("💡 Configure parâmetros e clique 'Iniciar Simulação'")
        self.logs_tab.log("📋 Todos os logs dos agentes aparecerão aqui em tempo real")
        self.logs_tab.log("🔧 Para conectividade XMPP completa, execute 'spade run' antes de iniciar")
    
    def setup_background(self):
        """Setup background with modern dark theme"""
        # Use a beautiful gradient background instead of image
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a2e, stop:0.3 #16213e, stop:0.7 #0f3460, stop:1 #1a1a2e);
            }
        """)


def start_gui_app():
    app = QApplication(sys.argv)
    app.setStyleSheet(CHALKBOARD_STYLE)
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    win = MainWindow()
    win.show()

    with loop:
        loop.run_forever()
