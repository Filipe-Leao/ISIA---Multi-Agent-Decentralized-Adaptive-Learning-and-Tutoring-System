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
    
    async def simulate(self, agents, duration=None):
        """Simulate the multi-agent tutoring system for a specified duration or until the end."""
        start_time = asyncio.get_event_loop().time()
        if duration is None:
            print("Simulação a decorrer até ao fim dos agentes...\n")
            while any(agent.is_alive() for name, agent in agents.items() if name.startswith("student")):
                elapsed = asyncio.get_event_loop().time() - start_time
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
                elapsed = asyncio.get_event_loop().time() - start_time
                remaining = duration - elapsed
                print(f"⏰ Simulação: {elapsed:.0f}s / {duration}s (restante: {remaining:.0f}s)")

                for name, agent in agents.items():
                    if name.startswith("student") and not agent.is_alive():
                        print(f"❌ Estudante {name} terminou a sua atividade.")
                await asyncio.sleep(1)

            print("⏳ Duração da simulação atingida.")
        return

    async def run_simulation(self, num_students, num_tutors, num_peers, duration=30,
                            server="localhost", password="1234"):
        """
        Inicia a simulação com agentes SPADE reais
        
        Args:
            num_students: Número de estudantes
            num_tutors: Número de tutores
            num_peers: Número de peers
            server: Servidor XMPP
            password: Senha para os agentes
        """

        print(f"------------------------------\n")
        print(f"Iniciando simulação com parâmetros:")
        print(f"Estudantes: {num_students}\nTutores: {num_tutors}\nPeers: {num_peers}\nDuração: {duration} segundos\nServidor: {server}")
        print("------------------------------")
        try:
            self.is_running = True
            
            # 🔴 REDIRECIONAR STDOUT PARA GUI
            self.original_stdout = sys.stdout
            self.stdout_redirector = StdoutRedirector(self.log_signal)
            sys.stdout = self.stdout_redirector
            
            self.log("🚀 Iniciando simulação SPADE...")
            
            disciplines = [
                "estatística bayesiana", "aprendizagem automática", "programação",
                "estatística", "português", "álgebra"
            ]
            learning_styles = ["visual", "auditory", "cinestésico", "kinesthetic"]
            
            # Criar Resource Manager
            self.log("🔧 Criando Resource Manager...")
            resource_jid = f"resource@{server}"
            self.agents['resource'] = ResourceManagerAgent(resource_jid, password)
            
            # Criar Estudantes
            self.log(f"🎓 Criando {num_students} estudantes...")
            for i in range(1, num_students + 1):
                style = random.choice(learning_styles)
                jid = f"student{i}@{server}"
                student = StudentAgent(jid, password, learning_style=style)
                self.agents[f'student{i}'] = student
                self.log(f"   ➤ Estudante {i}: {jid} (estilo: {style})")
            
            # Criar Tutores
            self.log(f"👨‍🏫 Criando {num_tutors} tutores...")
            for i in range(1, num_tutors + 1):
                discipline = random.choice(disciplines)
                expertise = round(random.uniform(0.5, 1.0), 2)
                capacity = random.randint(1, 3)
                jid = f"tutor{i}@{server}"
                tutor = TutorAgent(jid, password, discipline=discipline, 
                                 expertise=expertise, capacity=capacity)
                self.agents[f'tutor{i}'] = tutor
                self.log(f"   ➤ Tutor {i}: {jid} (disc: {discipline}, exp: {expertise})")
            
            # Criar Peers
            self.log(f"👥 Criando {num_peers} peers...")
            for i in range(1, num_peers + 1):
                jid = f"peer{i}@{server}"
                peer = PeerAgent(jid, password)
                self.agents[f'peer{i}'] = peer
                self.log(f"   ➤ Peer {i}: {jid}")
            
            # Iniciar todos os agentes (sem auto_register para melhor controle)
            self.log("⚡ Iniciando agentes SPADE...")
            for name, agent in self.agents.items():
                try:
                    await agent.start()
                    self.log(f"   ✅ {name} iniciado com sucesso")
                    
                    # Capturar logs do agente
                    self.setup_agent_logging(name, agent)
                    
                except Exception as e:
                    self.log(f"   ❌ Erro ao iniciar {name}: {e}")
            
            # Aguardar TODOS os agentes estarem registrados e conectados
            self.log("⏳ Aguardando todos os agentes estarem registrados...")
            await asyncio.sleep(8)  # Tempo maior para garantir conexão XMPP completa
            
            # Fazer subscrições entre agentes (como no main.py)
            self.log("📡 Configurando subscrições entre agentes...")
            for name, agent in self.agents.items():
                if name.startswith("student"):
                    # Estudantes se subscrevem a todos exceto outros estudantes
                    for other_name, other_agent in self.agents.items():
                        if not other_name.startswith("student"):
                            try:
                                agent.presence.subscribe(other_agent.jid)
                                self.log(f"   [{name}] 🔔 Subscrito a {other_agent.jid}")
                            except Exception as e:
                                self.log(f"   ⚠️ Erro na subscrição {name} -> {other_name}: {e}")
                else:
                    # Tutores e peers se subscrevem ao resource manager
                    if name != "resource" and "resource" in self.agents:
                        try:
                            agent.presence.subscribe(self.agents["resource"].jid)
                            self.log(f"   [{name}] 🔔 Subscrito a {self.agents['resource'].jid}")
                        except Exception as e:
                            self.log(f"   ⚠️ Erro na subscrição {name} -> resource: {e}")
            
            # Aguardar subscrições serem processadas
            await asyncio.sleep(3)
            
            self.log("✅ Todos os agentes iniciados e conectados!")
            
            # 🔴 ATIVAR FLAGS PARA INICIAR BEHAVIOURS
            self.log("🚦 Ativando behaviours dos agentes...")
            for name, agent in self.agents.items():
                if name.startswith("student"):
                    agent.can_start_studying = True
                    self.log(f"   ✅ {name} pode começar a estudar")
                elif name.startswith("tutor"):
                    agent.can_start_helping = True
                    self.log(f"   ✅ {name} pode começar a ajudar")
                elif name.startswith("peer"):
                    agent.can_start_helping = True
                    self.log(f"   ✅ {name} pode começar a ajudar")
            
            self.log("📡 Os agentes agora podem começar a comunicar...")
            
            # Atualizar status inicial
            self.update_status()
            
            start_time = asyncio.get_event_loop().time()
            # Loop de monitoramento (atualizar a cada 3 segundos)
            await self.simulate(self.agents, duration=duration)
                
        except Exception as e:
            self.log(f"❌ Erro na simulação: {e}")
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
        """Para a simulação"""
        if not self.is_running:
            return
            
        self.log("🔻 Parando simulação...")
        self.is_running = False
        
        # 🔴 PRIMEIRO: Sinalizar todos os agentes para parar
        for name, agent in self.agents.items():
            agent.is_stopping = True
        
        # 🔴 SEGUNDO: Aguardar behaviours processarem a flag
        await asyncio.sleep(1.5)
        
        # 🔴 TERCEIRO: Mostrar progresso final após aguardar
        self.log("📊 Progresso final dos estudantes:")
        for name, agent in self.agents.items():
            if name.startswith("student"):
                try:
                    # Mostrar progresso final
                    final_progress = sum(agent.knowledge.values()) / len(agent.knowledge)
                    self.log(f"   🔻 {agent.name}: {agent.initial_progress:.4f} → {final_progress:.4f}")
                except Exception as e:
                    self.log(f"   ⚠️ Erro ao mostrar progresso de {name}: {e}")
        
        # 🔴 QUARTO: Parar todos os agentes
        self.log("🛑 Parando todos os agentes...")
        for name, agent in list(self.agents.items()):
            try:
                # Forçar parada de todos os behaviours primeiro
                if hasattr(agent, 'behaviours'):
                    for behaviour in agent.behaviours:
                        try:
                            behaviour.kill()
                        except:
                            pass
                
                # Parar o agente
                await agent.stop()
                self.log(f"   ✅ {name} parado")
                
            except Exception as e:
                self.log(f"   ⚠️ Erro ao parar {name}: {e}")
        
        # Aguardar para garantir que todos os behaviours e mensagens terminaram
        await asyncio.sleep(1)
        
        self.agents.clear()
        self.log("✅ Simulação encerrada")
        
        # 🔴 RESTAURAR STDOUT ORIGINAL
        if self.original_stdout:
            sys.stdout = self.original_stdout
            self.stdout_redirector = None
        
        # Limpar status na interface
        self.status_update.emit({})
        self.metrics_update.emit({})