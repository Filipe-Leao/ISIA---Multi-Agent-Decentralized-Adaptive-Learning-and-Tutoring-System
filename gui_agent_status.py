# app/gui_agent_status.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox, QHBoxLayout, QProgressBar, QScrollArea
from PySide6.QtCore import Qt


class AgentStatusPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout()
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Create scroll content widget
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # Estudantes
        self.students_group = QGroupBox("📚 Estudantes")
        self.students_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                color: #2E86AB;
                border: 2px solid #2E86AB;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        self.students_layout = QVBoxLayout()
        self.students_group.setLayout(self.students_layout)
        scroll_layout.addWidget(self.students_group)
        
        # Tutores
        self.tutors_group = QGroupBox("👨‍🏫 Tutores")
        self.tutors_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                color: #F18F01;
                border: 2px solid #F18F01;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        self.tutors_layout = QVBoxLayout()
        self.tutors_group.setLayout(self.tutors_layout)
        scroll_layout.addWidget(self.tutors_group)
        
        # Peers
        self.peers_group = QGroupBox("👥 Peers")
        self.peers_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                color: #8E44AD;
                border: 2px solid #8E44AD;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        self.peers_layout = QVBoxLayout()
        self.peers_group.setLayout(self.peers_layout)
        scroll_layout.addWidget(self.peers_group)
        
        # Add stretch to push content to top
        scroll_layout.addStretch()
        
        # Set scroll content
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        
        self.setLayout(main_layout)
    
    def update_status(self, agents):
        # Limpar layouts anteriores
        self.clear_layout(self.students_layout)
        self.clear_layout(self.tutors_layout)
        self.clear_layout(self.peers_layout)
        
        # Atualizar estudantes
        for name, agent in agents.items():
            if name.startswith("student"):
                widget = QWidget()
                layout = QHBoxLayout()  # Changed back to horizontal for compactness
                layout.setContentsMargins(5, 2, 5, 2)  # Reduce margins
                
                # Basic info (more compact)
                basic_info = QLabel(f"📚 {name}")
                basic_info.setStyleSheet("font-weight: bold; color: #2E86AB; font-size: 10px;")
                basic_info.setMinimumWidth(80)
                layout.addWidget(basic_info)
                
                # Learning style
                style_label = QLabel(f"({agent.get('learning_style')})")
                style_label.setStyleSheet("color: #666; font-size: 9px;")
                style_label.setMinimumWidth(70)
                layout.addWidget(style_label)
                
                # Progress bar (compact)
                progress_bar = QProgressBar()
                progress_bar.setRange(0, 100)
                progress_bar.setValue(int(agent.get('progress', 0) * 100))
                progress_bar.setFormat(f"{agent.get('progress', 0):.3f}")
                progress_bar.setMaximumHeight(15)
                progress_bar.setMinimumWidth(100)
                layout.addWidget(progress_bar)
                
                # Current topic if available (compact)
                if agent.get('topic'):
                    topic_label = QLabel(f"📖 {agent.get('topic')[:15]}...")  # Truncate topic
                    topic_label.setStyleSheet("color: #A23B72; font-style: italic; font-size: 9px;")
                    topic_label.setMinimumWidth(120)
                    layout.addWidget(topic_label)
                else:
                    layout.addStretch()
                
                widget.setLayout(layout)
                widget.setMaximumHeight(25)  # Limit height
                widget.setStyleSheet("""
                    QWidget { 
                        border: 1px solid #ddd; 
                        border-radius: 3px; 
                        padding: 2px; 
                        margin: 1px;
                        background-color: rgba(255, 255, 255, 0.8);
                    }
                """)
                self.students_layout.addWidget(widget)
            
            elif name.startswith("tutor"):
                widget = QWidget()
                layout = QHBoxLayout()
                layout.setContentsMargins(5, 2, 5, 2)
                
                # Tutor name
                header = QLabel(f"👨‍🏫 {name}")
                header.setStyleSheet("font-weight: bold; color: #F18F01; font-size: 10px;")
                header.setMinimumWidth(80)
                layout.addWidget(header)
                
                # Discipline (truncated)
                disc_short = agent.get('discipline')[:12] + "..." if len(agent.get('discipline')) > 12 else agent.get('discipline')
                info1 = QLabel(f"📚 {disc_short}")
                info1.setStyleSheet("color: #333; font-size: 9px;")
                info1.setMinimumWidth(100)
                layout.addWidget(info1)
                
                # Expertise
                info2 = QLabel(f"🎯 {agent.get('expertise', 0):.2f}")
                info2.setStyleSheet("color: #333; font-size: 9px;")
                info2.setMinimumWidth(50)
                layout.addWidget(info2)
                
                # Slots
                info3 = QLabel(f"👥 {agent.get('available_slots', 0)}/{agent.get('capacity', 0)}")
                info3.setStyleSheet("color: #333; font-size: 9px;")
                info3.setMinimumWidth(40)
                layout.addWidget(info3)
                
                # Queue status (compact)
                if agent.get('queue') and len(agent.get('queue')) > 0:
                    queue_info = QLabel(f"📋 {len(agent.get('queue'))}")
                    queue_info.setStyleSheet("color: #C73E1D; font-weight: bold; font-size: 9px;")
                else:
                    queue_info = QLabel("📋 0")
                    queue_info.setStyleSheet("color: #4CAF50; font-size: 9px;")
                queue_info.setMinimumWidth(30)
                layout.addWidget(queue_info)
                
                widget.setLayout(layout)
                widget.setMaximumHeight(25)
                widget.setStyleSheet("""
                    QWidget { 
                        border: 1px solid #ddd; 
                        border-radius: 3px; 
                        padding: 2px; 
                        margin: 1px;
                        background-color: rgba(255, 255, 255, 0.8);
                    }
                """)
                self.tutors_layout.addWidget(widget)
                
            elif name.startswith("peer"):
                widget = QWidget()
                layout = QHBoxLayout()
                layout.setContentsMargins(5, 2, 5, 2)
                
                header = QLabel(f"👥 {name}")
                header.setStyleSheet("font-weight: bold; color: #8E44AD; font-size: 10px;")
                layout.addWidget(header)
                
                status = QLabel("🟢 Ativo")
                status.setStyleSheet("color: #4CAF50; font-size: 9px;")
                layout.addWidget(status)
                
                layout.addStretch()
                
                widget.setLayout(layout)
                widget.setMaximumHeight(25)
                widget.setStyleSheet("""
                    QWidget { 
                        border: 1px solid #ddd; 
                        border-radius: 3px; 
                        padding: 2px; 
                        margin: 1px;
                        background-color: rgba(255, 255, 255, 0.8);
                    }
                """)
                self.peers_layout.addWidget(widget)
    
    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
