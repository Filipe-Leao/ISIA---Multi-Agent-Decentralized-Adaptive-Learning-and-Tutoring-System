# app/gui_config_panel.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QPushButton, 
                               QSpinBox, QLabel, QGroupBox, QLineEdit)
import asyncio


class ConfigPanel(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        layout = QVBoxLayout()

        # Configurações
        config_group = QGroupBox("⚙️ Configurações")
        form = QFormLayout()

        # Servidor XMPP
        self.s_server = QLineEdit()
        self.s_server.setText("localhost")
        self.s_server.setPlaceholderText("Ex: localhost ou jabber.hot-chilli.net")
        form.addRow("Servidor XMPP:", self.s_server)
        
        # Senha
        self.s_password = QLineEdit()
        self.s_password.setText("1234")
        self.s_password.setEchoMode(QLineEdit.Password)
        form.addRow("Senha:", self.s_password)

        self.s_students = QSpinBox()
        self.s_students.setRange(1, 10)
        self.s_students.setValue(3)
        form.addRow("Estudantes:", self.s_students)

        self.s_tutors = QSpinBox()
        self.s_tutors.setRange(1, 10)
        self.s_tutors.setValue(3)
        form.addRow("Tutores:", self.s_tutors)

        self.s_peers = QSpinBox()
        self.s_peers.setRange(0, 5)
        self.s_peers.setValue(1)
        form.addRow("Auxiliares:", self.s_peers)
        
        # Duração da simulação
        self.s_duration = QSpinBox()
        self.s_duration.setRange(0, 3600)
        self.s_duration.setValue(0)
        self.s_duration.setSuffix(" s")
        self.s_duration.setSpecialValueText("Manual")
        form.addRow("Duração:", self.s_duration)
        
        config_group.setLayout(form)
        layout.addWidget(config_group)

        # Controles
        controls_group = QGroupBox("Simulação")
        controls_layout = QVBoxLayout()
        
        self.btn_start = QPushButton("Start ▶️")
        self.btn_stop = QPushButton("Stop ⏹️")
        self.btn_stop.setEnabled(False)

        controls_layout.addWidget(self.btn_start)
        controls_layout.addWidget(self.btn_stop)
        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)

        self.btn_start.clicked.connect(self.start_sim)
        self.btn_stop.clicked.connect(self.stop_sim)

        self.setLayout(layout)

    def start_sim(self):
        """Inicia a simulação"""
        # Desabilitar botão start
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        
        # Criar task assíncrona e adicionar callback
        task = asyncio.create_task(
            self.controller.run_simulation(
                num_students=self.s_students.value(),
                num_tutors=self.s_tutors.value(),
                num_peers=self.s_peers.value(),
                server=self.s_server.text(),
                password=self.s_password.text(),
                duration=self.s_duration.value()
            )
        )
        
        # Quando terminar, re-habilitar botão
        task.add_done_callback(lambda _: self.on_simulation_finished())

    def stop_sim(self):
        """Para a simulação"""
        # Parar simulação
        asyncio.create_task(self.controller.stop_simulation())
        
    def on_simulation_finished(self):
        """Callback quando simulação termina"""
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
