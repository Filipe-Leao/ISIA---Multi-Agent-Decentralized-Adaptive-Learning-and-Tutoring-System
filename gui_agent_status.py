# app/gui_agent_status.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox, QHBoxLayout, QProgressBar


class AgentStatusPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Estudantes
        self.students_group = QGroupBox("Estudantes")
        self.students_layout = QVBoxLayout()
        self.students_group.setLayout(self.students_layout)
        layout.addWidget(self.students_group)
        
        # Tutores
        self.tutors_group = QGroupBox("Tutores")
        self.tutors_layout = QVBoxLayout()
        self.tutors_group.setLayout(self.tutors_layout)
        layout.addWidget(self.tutors_group)
        
        # Peers
        self.peers_group = QGroupBox("Peers")
        self.peers_layout = QVBoxLayout()
        self.peers_group.setLayout(self.peers_layout)
        layout.addWidget(self.peers_group)
        
        self.setLayout(layout)
    
    def update_status(self, agents):
        # Limpar layouts anteriores
        self.clear_layout(self.students_layout)
        self.clear_layout(self.tutors_layout)
        self.clear_layout(self.peers_layout)
        
        # Atualizar estudantes
        for name, agent in agents.items():
            if name.startswith("student"):
                widget = QWidget()
                layout = QHBoxLayout()
                
                label = QLabel(f"{agent.name} ({agent.learning_style})")
                progress_bar = QProgressBar()
                progress_bar.setRange(0, 100)
                progress_bar.setValue(int(agent.progress * 100))
                progress_bar.setFormat(f"{agent.progress:.2f}")
                
                layout.addWidget(label)
                layout.addWidget(progress_bar)
                widget.setLayout(layout)
                self.students_layout.addWidget(widget)
            
            elif name.startswith("tutor"):
                widget = QWidget()
                layout = QHBoxLayout()
                
                label = QLabel(f"{agent.name}")
                disc_label = QLabel(f"Disciplina: {agent.discipline}")
                exp_label = QLabel(f"Expertise: {agent.expertise:.2f}")
                slots_label = QLabel(f"Slots: {agent.available_slots}/{agent.capacity}")
                
                layout.addWidget(label)
                layout.addWidget(disc_label)
                layout.addWidget(exp_label)
                layout.addWidget(slots_label)
                widget.setLayout(layout)
                self.tutors_layout.addWidget(widget)
                
            elif name.startswith("peer"):
                label = QLabel(f"{agent.name} - Ativo")
                self.peers_layout.addWidget(label)
    
    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
