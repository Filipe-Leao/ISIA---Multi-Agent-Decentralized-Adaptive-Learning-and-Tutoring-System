import sys
import os

# IMPORTANTE: Configurar qasync para usar PySide6 ANTES de importar qualquer coisa
os.environ['QASYNC_QTIMPL'] = 'PySide6'

# Adicionar o diretório raiz ao path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import qasync

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                               QVBoxLayout, QTabWidget, QLabel, QSplitter)
from PySide6.QtCore import Qt

from gui_config_panel import ConfigPanel
from gui_agent_status import AgentStatusPanel
from gui_tabs import LogsTab, MetricsTab
from controller.simulation import SimulationController


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎓 ISIA - Sistema Multi-Agente de Tutoria Adaptativa")
        self.setGeometry(100, 100, 1400, 900)
        
        # Controller (Core SPADE logic)
        self.controller = SimulationController()
        
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
        
        # Config Panel
        self.config_panel = ConfigPanel(self.controller)
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
        
        tabs.addTab(self.logs_tab, "📋 Logs")
        tabs.addTab(self.metrics_tab, "📊 Métricas")
        
        right_layout.addWidget(tabs)
        splitter.addWidget(right_panel)
        
        # Splitter proportions
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        main_layout.addWidget(splitter, 1)
        
        # Connect signals
        self.connect_signals()
        
        # Initial log message
        self.logs_tab.log("🌟 Sistema iniciado. Configure os parâmetros e clique em 'Iniciar Simulação'")
        self.logs_tab.log("📌 Certifique-se de que um servidor XMPP está rodando antes de iniciar")
    
    def connect_signals(self):
        """Conecta os signals do controller aos componentes da GUI"""
        # Conectar logs
        self.controller.log_signal.connect(self.logs_tab.log)
        
        # Conectar status updates
        self.controller.status_update.connect(self.agent_status.update_status)
        
        # Conectar metrics updates
        self.controller.metrics_update.connect(self.metrics_tab.update_metrics)


def start_gui_app():
    app = QApplication(sys.argv)
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    win = MainWindow()
    win.show()

    with loop:
        loop.run_forever()


