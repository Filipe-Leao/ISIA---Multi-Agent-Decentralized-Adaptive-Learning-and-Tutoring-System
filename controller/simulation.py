import asyncio
import random
import sys
import io
from datetime import datetime
from PySide6.QtCore import QObject, Signal

# Importar agentes SPADE reais
from student import StudentAgent
from tutor import TutorAgent
from peer import PeerAgent
from resource_manager import ResourceManagerAgent


class StdoutRedirector(io.TextIOBase):
    """Redireciona stdout para o signal da GUI"""
    def __init__(self, log_signal):
        self.log_signal = log_signal
        self.original_stdout = sys.stdout
        
    def write(self, text):
        # Enviar para GUI (remover ANSI codes e filtrar mensagens repetitivas)
        if text and text.strip():
            # Remover códigos de cor ANSI
            import re
            clean_text = re.sub(r'\x1b\[[0-9;]*m', '', text)
            
            # Filtrar mensagens repetitivas de "Proposal chosen"
            if "Proposal chosen (different discipline):" in clean_text:
                # Não enviar para GUI
                self.original_stdout.write(text)
                return len(text)
            
            self.log_signal.emit(clean_text.strip())
        # Também manter no stdout original
        self.original_stdout.write(text)
        return len(text)
        
    def flush(self):
        self.original_stdout.flush()


class SimulationController(QObject):
    """Controlador central da simulação SPADE"""
    
    # Signals para comunicação com GUI
    log_signal = Signal(str)
    status_update = Signal(dict)
    metrics_update = Signal(dict)
    
    def __init__(self):
        super().__init__()
        self.agents = {}
        self.is_running = False
        self.simulation_task = None
        self.stdout_redirector = None
        self.original_stdout = None
        
    def log(self, message):
        """Envia log para a interface"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] {message}"
        self.log_signal.emit(formatted_msg)
        # Print no stdout original para não criar loop infinito
        if self.original_stdout and self.original_stdout != sys.stdout:
            self.original_stdout.write(formatted_msg + "\n")
        elif not self.stdout_redirector:
            print(formatted_msg)
    
    async def run_simulation(self, num_students, num_tutors, num_peers, 
                            server="localhost", password="1234", duration=0):
        """
        Inicia a simulação com agentes SPADE reais
        
        Args:
            num_students: Número de estudantes
            num_tutors: Número de tutores
            num_peers: Número de peers
            server: Servidor XMPP
            password: Senha para os agentes
            duration: Duração da simulação em segundos (0 = manual)
        """
        try:
            self.is_running = True
            self._simulation_duration = duration  # 🔴 Armazenar duração
            
            # 🔴 REDIRECIONAR STDOUT PARA GUI
            self.original_stdout = sys.stdout
            self.stdout_redirector = StdoutRedirector(self.log_signal)
            sys.stdout = self.stdout_redirector
            
            if duration > 0:
                self.log(f"Starting SPADE simulation... (duration: {duration}s)")
            else:
                self.log("Starting SPADE simulation... (manual mode)")
            
            disciplines = [
                "estatística bayesiana", "aprendizagem automática", "programação",
                "estatística", "português", "álgebra"
            ]
            learning_styles = ["visual", "auditory", "cinestésico", "kinesthetic"]
            
            # Criar Resource Manager
            self.log("Creating Resource Manager...")
            resource_jid = f"resource@{server}"
            self.agents['resource'] = ResourceManagerAgent(resource_jid, password)
            
            # Criar Estudantes
            self.log(f"Creating {num_students} students...")
            for i in range(1, num_students + 1):
                style = random.choice(learning_styles)
                jid = f"student{i}@{server}"
                student = StudentAgent(jid, password, learning_style=style, disciplines=disciplines)
                self.agents[f'student{i}'] = student
                self.log(f"   Student {i}: {jid} (style: {style})")
            
            # Criar Tutores
            self.log(f"Creating {num_tutors} tutors...")
            for i in range(1, num_tutors + 1):
                discipline = random.choice(disciplines)
                expertise = round(random.uniform(0.5, 1.0), 2)
                capacity = random.randint(1, 3)
                jid = f"tutor{i}@{server}"
                tutor = TutorAgent(jid, password, discipline=discipline, 
                                 expertise=expertise, capacity=capacity)
                self.agents[f'tutor{i}'] = tutor
                self.log(f"   Tutor {i}: {jid} (disc: {discipline}, exp: {expertise})")
            
            # Criar Peers
            self.log(f"Creating {num_peers} peers...")
            for i in range(1, num_peers + 1):
                jid = f"peer{i}@{server}"
                peer = PeerAgent(jid, password)
                self.agents[f'peer{i}'] = peer
                self.log(f"   Peer {i}: {jid}")
            
            # Iniciar todos os agentes (sem auto_register para melhor controle)
            self.log("Starting SPADE agents...")
            for name, agent in self.agents.items():
                try:
                    await agent.start()
                    self.log(f"   {name} started successfully")
                    
                    # Capturar logs do agente
                    self.setup_agent_logging(name, agent)
                    
                except Exception as e:
                    self.log(f"   Error starting {name}: {e}")
            
            # Aguardar TODOS os agentes estarem registrados e conectados
            self.log("Waiting for all agents to register...")
            await asyncio.sleep(8)  # Tempo maior para garantir conexão XMPP completa
            
            # Fazer subscrições entre agentes (como no main.py)
            self.log("Configuring agent subscriptions...")
            for name, agent in self.agents.items():
                if name.startswith("student"):
                    # Estudantes se subscrevem a todos exceto outros estudantes
                    for other_name, other_agent in self.agents.items():
                        if not other_name.startswith("student"):
                            try:
                                agent.presence.subscribe(other_agent.jid)
                                self.log(f"   [{name}] Subscribed to {other_agent.jid}")
                            except Exception as e:
                                self.log(f"   Subscription error {name} -> {other_name}: {e}")
                else:
                    # Tutores e peers se subscrevem ao resource manager
                    if name != "resource" and "resource" in self.agents:
                        try:
                            agent.presence.subscribe(self.agents["resource"].jid)
                            self.log(f"   [{name}] Subscribed to {self.agents['resource'].jid}")
                        except Exception as e:
                            self.log(f"   Subscription error {name} -> resource: {e}")
            
            # Aguardar subscrições serem processadas
            await asyncio.sleep(3)
            
            self.log("All agents started and connected!")
            
            # 🔴 ATIVAR FLAGS PARA INICIAR BEHAVIOURS
            self.log("Activating agent behaviours...")
            for name, agent in self.agents.items():
                if name.startswith("student"):
                    agent.can_start_studying = True
                    self.log(f"   {name} can start studying")
                elif name.startswith("tutor"):
                    agent.can_start_helping = True
                    self.log(f"   {name} can start helping")
                elif name.startswith("peer"):
                    agent.can_start_helping = True
                    self.log(f"   {name} can start helping")
            
            self.log("Agents can now begin communicating...")
            
            # Atualizar status inicial
            self.update_status()
            
            # Loop de monitoramento (atualizar a cada 3 segundos)
            start_time = asyncio.get_event_loop().time()
            while self.is_running:
                await asyncio.sleep(3)
                self.update_status()
                
                # ⏱️ Verificar se deve parar por tempo (se duration > 0)
                if hasattr(self, '_simulation_duration') and self._simulation_duration > 0:
                    elapsed = asyncio.get_event_loop().time() - start_time
                    if elapsed >= self._simulation_duration:
                        self.log(f"Simulation time ({self._simulation_duration}s) reached - stopping automatically...")
                        await self.stop_simulation()
                        break
                
                # ✅ Verificar se todos os estudantes chegaram a 100%
                all_students_complete = True
                for name, agent in self.agents.items():
                    if name.startswith("student"):
                        if hasattr(agent, 'progress') and agent.progress < 1.0:
                            all_students_complete = False
                            break
                
                if all_students_complete:
                    self.log("All students reached 100% progress - stopping automatically...")
                    await self.stop_simulation()
                    break
                
        except Exception as e:
            self.log(f"Simulation error: {e}")
            import traceback
            self.log(traceback.format_exc())
            self.is_running = False
        finally:
            # 🔴 RESTAURAR STDOUT ORIGINAL
            if self.original_stdout:
                sys.stdout = self.original_stdout
    
    def setup_agent_logging(self, name, agent):
        """Configura captura de logs dos agentes"""
        # Os agentes já estão printando diretamente no stdout
        # Esses prints JÁ aparecem no terminal
        # Não precisamos capturar nada adicional aqui
        pass
    
    def update_status(self):
        """Atualiza status dos agentes na interface"""
        status = {}
        for name, agent in self.agents.items():
            if hasattr(agent, 'is_alive') and agent.is_alive():
                status[name] = {
                    'name': name,
                    'jid': str(agent.jid),
                    'running': True
                }
                
                # Adicionar informações específicas
                if name.startswith('student'):
                    status[name]['learning_style'] = getattr(agent, 'learning_style', 'N/A')
                    status[name]['progress'] = getattr(agent, 'progress', 0.0)
                    status[name]['initial_progress'] = getattr(agent, 'initial_progress', 0.0)
                    status[name]['topic'] = getattr(agent, 'topic', 'N/A')
                elif name.startswith('tutor'):
                    status[name]['discipline'] = getattr(agent, 'discipline', 'N/A')
                    status[name]['expertise'] = getattr(agent, 'expertise', 0.0)
                    status[name]['capacity'] = getattr(agent, 'capacity', 0)
                    status[name]['available_slots'] = getattr(agent, 'available_slots', 0)
        
        self.status_update.emit(status)
        self.metrics_update.emit(status)
    
    async def stop_simulation(self):
        """Para a simulação de forma otimizada para evitar bloqueio do CPU"""
        if not self.is_running:
            return
            
        self.log("Stopping simulation...")
        self.is_running = False
        
        # 🔴 PRIMEIRO: Mostrar progresso final ANTES de sinalizar parada
        self.log("Final student progress:")
        for name, agent in self.agents.items():
            if name.startswith("student"):
                try:
                    final_progress = sum(agent.knowledge.values()) / len(agent.knowledge)
                    self.log(f"   {agent.name}: {agent.initial_progress:.4f} -> {final_progress:.4f}")
                except Exception as e:
                    self.log(f"   Error displaying progress for {name}: {e}")
        
        # 🔴 SEGUNDO: Sinalizar todos os agentes para parar
        for name, agent in self.agents.items():
            agent.is_stopping = True
        
        # 🔴 TERCEIRO: Aguardar behaviours processarem a flag (reduzido para não saturar CPU)
        await asyncio.sleep(0.5)
        
        # 🔴 QUARTO: Parar agentes EM PARALELO com timeout para evitar bloqueio
        self.log("Stopping all agents...")
        
        async def stop_agent_safe(name, agent):
            """Para um agente com timeout para evitar bloqueio"""
            try:
                # Não forçar kill de behaviours - deixar SPADE gerir isso
                # Parar o agente com timeout de 3 segundos
                await asyncio.wait_for(agent.stop(), timeout=3.0)
                self.log(f"   {name} stopped")
                return True
            except asyncio.TimeoutError:
                self.log(f"   {name} timeout - forcing stop")
                return False
            except Exception as e:
                self.log(f"   Error stopping {name}: {e}")
                return False
        
        # Parar todos os agentes em paralelo (mais eficiente que sequencial)
        stop_tasks = [
            stop_agent_safe(name, agent) 
            for name, agent in list(self.agents.items())
        ]
        
        # Executar em paralelo com gather
        await asyncio.gather(*stop_tasks, return_exceptions=True)
        
        # Pequena pausa para limpeza final
        await asyncio.sleep(0.3)
        
        self.agents.clear()
        self.log("Simulation ended")
        
        # 🔴 RESTAURAR STDOUT ORIGINAL
        if self.original_stdout:
            sys.stdout = self.original_stdout
            self.stdout_redirector = None
        
        # Limpar status na interface
        self.status_update.emit({})
        self.metrics_update.emit({})