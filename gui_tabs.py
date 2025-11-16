# app/gui_tabs.py
from PySide6.QtWidgets import QWidget, QTextEdit, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class LogsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.log_widget = QTextEdit()
        self.log_widget.setReadOnly(True)
        self.log_widget.setFont(QFont("Consolas", 9))
        layout.addWidget(self.log_widget)
        self.setLayout(layout)

    def log(self, text):
        self.log_widget.append(text)


class MetricsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.figure = Figure(figsize=(12, 8))
        self.canvas = FigureCanvasQTAgg(self.figure)
        
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
    def update_metrics(self, agents):
        self.figure.clear()
        
        # Criar subplots
        ax1 = self.figure.add_subplot(2, 2, 1)
        ax2 = self.figure.add_subplot(2, 2, 2)
        ax3 = self.figure.add_subplot(2, 2, 3)
        ax4 = self.figure.add_subplot(2, 2, 4)
        
        # Gráfico 1: Progresso por disciplina
        students = [a for name, a in agents.items() if name.startswith("student")]
        if students:
            disciplines = list(students[0].knowledge.keys())
            progress_data = {disc: [] for disc in disciplines}
            
            for student in students:
                for disc in disciplines:
                    progress_data[disc].append(student.knowledge[disc])
            
            for i, (disc, values) in enumerate(progress_data.items()):
                ax1.bar(disc.replace(' ', '\n'), sum(values)/len(values), alpha=0.7)
            ax1.set_title('Progresso Médio por Disciplina')
            ax1.set_ylabel('Progresso (0-1)')
            plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')
        
        # Gráfico 2: Disponibilidade dos tutores
        tutors = [a for name, a in agents.items() if name.startswith("tutor")]
        if tutors:
            tutor_names = []
            available_slots = []
            capacities = []
            
            for tutor in tutors:
                tutor_names.append(f"{tutor.name}\n({tutor.discipline})")
                available_slots.append(tutor.available_slots)
                capacities.append(tutor.capacity)
            
            x = range(len(tutor_names))
            ax2.bar(x, capacities, alpha=0.3, label='Capacidade Total')
            ax2.bar(x, available_slots, alpha=0.8, label='Slots Disponíveis')
            ax2.set_title('Status dos Tutores')
            ax2.set_xticks(x)
            ax2.set_xticklabels(tutor_names)
            ax2.legend()
            plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
        
        # Gráfico 3: Progresso individual dos estudantes
        if students:
            student_names = [s.name for s in students]
            current_progress = [s.progress for s in students]
            initial_progress = [s.initial_progress for s in students]
            
            x = range(len(student_names))
            ax3.bar([i-0.2 for i in x], initial_progress, width=0.4, 
                   alpha=0.5, label='Progresso Inicial')
            ax3.bar([i+0.2 for i in x], current_progress, width=0.4, 
                   alpha=0.8, label='Progresso Atual')
            ax3.set_title('Progresso dos Estudantes')
            ax3.set_xticks(x)
            ax3.set_xticklabels(student_names)
            ax3.legend()
            ax3.set_ylabel('Progresso Médio')
        
        # Gráfico 4: Distribuição de estilos de aprendizagem
        if students:
            styles = {}
            for student in students:
                style = student.learning_style
                styles[style] = styles.get(style, 0) + 1
            
            ax4.pie(styles.values(), labels=styles.keys(), autopct='%1.1f%%')
            ax4.set_title('Estilos de Aprendizagem')
        
        self.figure.tight_layout()
        self.canvas.draw()
