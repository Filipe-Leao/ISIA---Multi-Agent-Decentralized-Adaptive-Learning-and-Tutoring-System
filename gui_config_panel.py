# app/gui_config_panel.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QPushButton, 
                               QSpinBox, QLabel, QGroupBox, QLineEdit)
import asyncio


class ConfigPanel(QWidget):
    def __init__(self, simulation):
        super().__init__()
        self.simulation = simulation

        layout = QVBoxLayout()

        # Configurações
        config_group = QGroupBox("Configurações da Simulação")
        form = QFormLayout()

        # XMPP Server
        self.s_server = QLineEdit()
        self.s_server.setText("localhost")
        self.s_server.setPlaceholderText("Ex: localhost ou jabber.hot-chilli.net")
        
        # Password
        self.s_password = QLineEdit()
        self.s_password.setText("1234")
        self.s_password.setEchoMode(QLineEdit.Password)

        self.s_students = QSpinBox()
        self.s_students.setRange(1, 20)
        self.s_students.setValue(10)  # Default from main.py

        self.s_tutors = QSpinBox()
        self.s_tutors.setRange(1, 10)
        self.s_tutors.setValue(3)  # Default from main.py

        self.s_peers = QSpinBox()
        self.s_peers.setRange(0, 5)
        self.s_peers.setValue(1)  # Default from main.py

        self.s_duration = QSpinBox()
        self.s_duration.setRange(10, 600)
        self.s_duration.setValue(30)  # Default from main.py (30 seconds)
        self.s_duration.setSuffix(" segundos")

        form.addRow("🌐 Servidor XMPP:", self.s_server)
        form.addRow("🔑 Senha:", self.s_password)
        form.addRow("🎓 Estudantes:", self.s_students)
        form.addRow("👨‍🏫 Tutores:", self.s_tutors)
        form.addRow("👥 Peers:", self.s_peers)
        form.addRow("⏱️ Duração:", self.s_duration)
        
        config_group.setLayout(form)
        layout.addWidget(config_group)

        # Controles
        controls_group = QGroupBox("Controles")
        controls_layout = QVBoxLayout()
        
        self.btn_start = QPushButton("🚀 Iniciar Simulação")
        self.btn_stop = QPushButton("⏹️ Parar Simulação")
        self.btn_stop.setEnabled(False)

        controls_layout.addWidget(self.btn_start)
        controls_layout.addWidget(self.btn_stop)
        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)

        self.btn_start.clicked.connect(self.start_sim)
        self.btn_stop.clicked.connect(self.stop_sim)

        self.setLayout(layout)

    def start_sim(self):
        # Start simulation and update button states
        async def run_and_update():
            self.btn_start.setEnabled(False)
            self.btn_stop.setEnabled(True)
            
            try:
                await self.simulation.run_simulation(
                    self.s_students.value(),
                    self.s_tutors.value(),
                    self.s_peers.value(),
                    self.s_duration.value(),
                    server=self.s_server.text(),
                    password=self.s_password.text()
                )
            finally:
                # Re-enable start button when simulation ends
                self.btn_start.setEnabled(True)
                self.btn_stop.setEnabled(False)
        
        asyncio.create_task(run_and_update())

    def stop_sim(self):
        async def stop_and_update():
            await self.simulation.stop_simulation()
            self.btn_start.setEnabled(True)
            self.btn_stop.setEnabled(False)
            
        asyncio.create_task(stop_and_update())
