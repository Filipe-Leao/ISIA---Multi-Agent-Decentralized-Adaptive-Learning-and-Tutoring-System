# app/gui_tabs.py
from PySide6.QtWidgets import QWidget, QTextEdit, QVBoxLayout, QLabel, QScrollArea
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class LogsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create scroll area for logs
        self.log_widget = QTextEdit()
        self.log_widget.setReadOnly(True)
        self.log_widget.setFont(QFont("Consolas", 10))
        
        # Estilo escuro simples para logs
        self.log_widget.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 2px solid #32CD32;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        
        layout.addWidget(self.log_widget)
        self.setLayout(layout)

    def log(self, text):
        self.log_widget.append(text)
        # Auto-scroll to bottom
        scrollbar = self.log_widget.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


class MetricsTab(QWidget):
    def __init__(self):
        super().__init__()
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create scroll area for metrics
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Create content widget for scroll area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create matplotlib figure and canvas
        self.figure = Figure(figsize=(12, 10))
        self.canvas = FigureCanvasQTAgg(self.figure)
        
        # Set minimum size for better visibility
        self.canvas.setMinimumSize(800, 600)
        
        content_layout.addWidget(self.canvas)
        content_layout.addStretch()  # Add stretch to prevent compression
        
        # Set the content widget to scroll area
        scroll_area.setWidget(content_widget)
        
        # Add scroll area to main layout
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)
        
    def update_metrics(self, agents):
        if not agents:
            return
            
        try:
            self.figure.clear()
            
            # Criar subplots
            ax1 = self.figure.add_subplot(2, 2, 1)
            ax2 = self.figure.add_subplot(2, 2, 2)
            ax3 = self.figure.add_subplot(2, 2, 3)
            ax4 = self.figure.add_subplot(2, 2, 4)
            
            # Filter agents safely (agents agora são dicts)
            students = {name: a for name, a in agents.items() if name.startswith("student")}
            tutors = {name: a for name, a in agents.items() if name.startswith("tutor")}
            peers = {name: a for name, a in agents.items() if name.startswith("peer")}
            
            # Gráfico 1: Progresso individual dos estudantes
            if students:
                student_names = list(students.keys())
                current_progress = [students[name].get('progress', 0) for name in student_names]
                # Obter progresso inicial real dos estudantes
                initial_progress = [students[name].get('initial_progress', 0) for name in student_names]
                
                x = range(len(student_names))
                bars1 = ax1.bar([i-0.2 for i in x], initial_progress, width=0.4, 
                               alpha=0.5, label='Progresso Inicial', color='lightblue')
                bars2 = ax1.bar([i+0.2 for i in x], current_progress, width=0.4, 
                               alpha=0.8, label='Progresso Atual', color='darkblue')
                ax1.set_title('Progresso dos Estudantes')
                ax1.set_xticks(x)
                ax1.set_xticklabels([name.replace('student', 'S') for name in student_names], rotation=45)
                ax1.legend()
                ax1.set_ylabel('Progresso')
                ax1.set_ylim(0, 1)
            else:
                ax1.text(0.5, 0.5, 'Aguardando dados\ndos estudantes', 
                        ha='center', va='center', transform=ax1.transAxes)
                ax1.set_title('Progresso dos Estudantes')
            
            # Gráfico 2: Status dos tutores
            if tutors:
                tutor_names = []
                available_slots = []
                capacities = []
                
                for name, tutor in tutors.items():
                    discipline = tutor.get('discipline', 'N/A')[:10]  # Truncar
                    tutor_names.append(f"{name}\n({discipline})")
                    available_slots.append(tutor.get('available_slots', 0))
                    capacities.append(tutor.get('capacity', 1))
                
                x = range(len(tutor_names))
                ax2.bar(x, capacities, alpha=0.3, label='Capacidade Total', color='lightgreen')
                ax2.bar(x, available_slots, alpha=0.8, label='Slots Disponíveis', color='green')
                ax2.set_title('Status dos Tutores')
                ax2.set_xticks(x)
                ax2.set_xticklabels([name.split('\n')[0].replace('tutor', 'T') for name in tutor_names])
                ax2.legend()
                ax2.set_ylabel('Slots')
            else:
                ax2.text(0.5, 0.5, 'Aguardando dados\ndos tutores', 
                        ha='center', va='center', transform=ax2.transAxes)
                ax2.set_title('Status dos Tutores')
            
            # Gráfico 3: Distribuição de estilos de aprendizagem
            if students:
                styles = {}
                for name, student in students.items():
                    style = student.get('learning_style', 'unknown')
                    styles[style] = styles.get(style, 0) + 1
                
                if styles:
                    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
                    ax3.pie(styles.values(), labels=styles.keys(), autopct='%1.1f%%', 
                           colors=colors[:len(styles)])
                    ax3.set_title('Estilos de Aprendizagem')
            else:
                ax3.text(0.5, 0.5, 'Aguardando dados\ndos estilos', 
                        ha='center', va='center', transform=ax3.transAxes)
                ax3.set_title('Estilos de Aprendizagem')
            
            # Gráfico 4: Progresso médio vs tempo (simulado)
            if students:
                progress_values = [student.get('progress', 0) for student in students.values()]
                avg_progress = sum(progress_values) / len(progress_values)
                
                # Create a simple progress indicator
                categories = ['Inicial', 'Atual', 'Meta']
                values = [0.0, avg_progress, 1.0]
                colors = ['red', 'orange' if avg_progress < 0.5 else 'green', 'lightgreen']
                
                bars = ax4.bar(categories, values, color=colors, alpha=0.7)
                ax4.set_title('Progresso Médio Geral')
                ax4.set_ylabel('Progresso')
                ax4.set_ylim(0, 1)
                
                # Add value labels on bars
                for bar, value in zip(bars, values):
                    height = bar.get_height()
                    ax4.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                            f'{value:.3f}', ha='center', va='bottom')
            else:
                ax4.text(0.5, 0.5, 'Aguardando dados\nde progresso', 
                        ha='center', va='center', transform=ax4.transAxes)
                ax4.set_title('Progresso Médio Geral')
            
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            # If there's any error, show a message
            self.figure.clear()
            ax = self.figure.add_subplot(1, 1, 1)
            ax.text(0.5, 0.5, f'Erro ao atualizar métricas:\n{str(e)}', 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Erro nas Métricas')
            self.canvas.draw()
