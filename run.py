#!/usr/bin/env python3
"""
run.py - Iniciar a interface GUI do sistema ISIA
Este script inicia a interface gráfica que controla a simulação multi-agente.
Certifique-se de que o servidor SPADE está rodando em paralelo.
"""
import sys
import os

# Configurar qasync para usar PySide6 ANTES de importar qualquer coisa
os.environ['QASYNC_QTIMPL'] = 'PySide6'

# Adicionar o diretório raiz ao path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import asyncio
import qasync
from PySide6.QtWidgets import QApplication

from interface.gui_main import MainWindow

# Estilo global da aplicação
STYLE = """
    QWidget {
        background-color: #2d3748;
        color: #e2e8f0;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    QMainWindow {
        background-color: #1a202c;
    }

    QGroupBox {
        background-color: rgba(74, 85, 104, 180);
        border: 2px solid #32CD32;
        border-radius: 8px;
        font-weight: bold;
        color: #ffffff;
        padding: 15px;
        margin-top: 10px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 15px;
        padding: 5px 10px;
        background-color: #32CD32;
        border-radius: 4px;
        color: white;
    }
    QPushButton {
        background-color: #32CD32;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 14px;
    }
    QPushButton:hover {
        background-color: #28a428;
    }
    QPushButton:pressed {
        background-color: #208020;
    }
    QPushButton:disabled {
        background-color: #718096;
        color: #a0aec0;
    }
    QLabel {
        color: #e2e8f0;
        font-size: 13px;
    }
    QLineEdit, QSpinBox {
        background-color: #1a202c;
        color: #e2e8f0;
        border: 2px solid #4a5568;
        border-radius: 4px;
        padding: 6px;
        font-size: 13px;
    }
    QLineEdit:focus, QSpinBox:focus {
        border-color: #32CD32;
    }
    QTextEdit {
        background-color: #1a202c;
        color: #e2e8f0;
        border: 2px solid #4a5568;
        border-radius: 6px;
        padding: 8px;
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 12px;
    }
    QProgressBar {
        border: 2px solid #4a5568;
        border-radius: 6px;
        background-color: #1a202c;
        text-align: center;
        color: white;
        font-weight: bold;
    }
    QProgressBar::chunk {
        background-color: #32CD32;
        border-radius: 4px;
    }
    QTabWidget::pane {
        background-color: rgba(45, 55, 72, 200);
        border: 2px solid #32CD32;
        border-radius: 8px;
    }
    QTabBar::tab {
        background-color: #4a5568;
        color: #e2e8f0;
        padding: 10px 20px;
        margin: 2px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        font-weight: bold;
    }
    QTabBar::tab:selected {
        background-color: #32CD32;
        color: white;
    }
    QTabBar::tab:hover {
        background-color: #718096;
    }
    QScrollBar:vertical {
        background-color: #2d3748;
        width: 12px;
        border-radius: 6px;
    }
    QScrollBar::handle:vertical {
        background-color: #4a5568;
        border-radius: 6px;
    }
    QScrollBar::handle:vertical:hover {
        background-color: #32CD32;
    }
"""

def main():
    """Função principal para iniciar a aplicação GUI"""
    print("=" * 60)
    print("ISIA - Sistema Multi-Agente de Tutoria Adaptativa")
    print("=" * 60)
    print("✅ Iniciando interface gráfica...")
    print("⚠️  Certifique-se de que o servidor SPADE está rodando!")
    print("=" * 60)
    
    # Criar aplicação Qt
    app = QApplication(sys.argv)
    
    # Aplicar estilo global
    app.setStyleSheet(STYLE)
    
    # Configurar event loop assíncrono
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    # Criar e mostrar janela principal
    window = MainWindow()
    window.show()
    
    print("Interface iniciada com sucesso!")
    print("📋 Configure os parâmetros e clique em 'Start'")
    print("=" * 60)
    
    # Executar event loop
    with loop:
        sys.exit(loop.run_forever())


if __name__ == "__main__":
    main()
