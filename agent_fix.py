import asyncio
import logging
from spade.agent import Agent

# Configuração para resolver problemas de conectividade XMPP
logging.getLogger('slixmpp').setLevel(logging.WARNING)
logging.getLogger('asyncio').setLevel(logging.WARNING)

class BaseAgentWithFix(Agent):
    """Classe base para agentes com configurações de conectividade corrigidas"""
    
    def __init__(self, jid, password):
        super().__init__(jid, password)
        
        # As configurações de plugin serão feitas no setup
        self._connection_configured = False
        self._is_stopping = False
        
    def _configure_connection(self):
        """Configura plugins XMPP se ainda não foi feito"""
        if not self._connection_configured and hasattr(self, 'client') and self.client:
            try:
                # Configurações específicas para resolver problemas de conectividade
                self.client.register_plugin('xep_0030')  # Service Discovery
                self.client.register_plugin('xep_0004')  # Data Forms
                self.client.register_plugin('xep_0060')  # PubSub
                self.client.register_plugin('xep_0199')  # XMPP Ping
                
                # Configurar connection timeout e retry
                self.client.reconnect = False  # Evitar reconexões automáticas que causam problemas
                self.client.reconnect_max_delay = 5
                
                self._connection_configured = True
            except Exception as e:
                print(f"⚠️ Aviso ao configurar plugins XMPP para {self.jid}: {e}")
        
    async def start(self, auto_register=True):
        """Override start method to handle connection errors gracefully"""
        # Configurar conexão antes de tentar conectar
        self._configure_connection()
        
        try:
            # Primeira tentativa: start normal
            result = await super().start(auto_register=auto_register)
            if result:
                print(f"✅ {self.jid} conectado ao servidor XMPP")
                return result
        except TypeError as e:
            if "unexpected keyword argument 'host'" in str(e):
                # Erro específico de versão - esse é um problema conhecido do SPADE 4.x
                print(f"🔧 Erro de compatibilidade detectado para {self.jid} - usando modo simulação")
                # Em modo simulação, chamar setup manualmente
                await self.setup()
                return True
            else:
                raise e
        except Exception as e:
            error_msg = str(e).lower()
            if "connection" in error_msg or "refused" in error_msg or "network" in error_msg:
                print(f"🌐 Problema de rede para {self.jid} - usando modo simulação")
                # Em modo simulação, chamar setup manualmente
                await self.setup()
                return True
            else:
                print(f"❌ Erro não tratado para {self.jid}: {e}")
                # Em modo simulação, chamar setup manualmente
                await self.setup()
                return True  # Continuar simulação mesmo com erro
    
    async def stop(self):
        """Override stop method to handle graceful shutdown"""
        if self._is_stopping:
            return  # Evitar múltiplas tentativas de parada
        
        self._is_stopping = True
        
        try:
            # Tentar parar normalmente primeiro
            if hasattr(self, 'client') and self.client and hasattr(self.client, 'disconnect'):
                try:
                    # Desconectar graciosamente
                    await asyncio.wait_for(self.client.disconnect(wait=False), timeout=3.0)
                except asyncio.TimeoutError:
                    print(f"⚠️ Timeout ao desconectar {self.jid}")
                except Exception as e:
                    print(f"⚠️ Erro ao desconectar {self.jid}: {e}")
            
            # Chamar o stop original mas com timeout
            await asyncio.wait_for(super().stop(), timeout=5.0)
            
        except asyncio.TimeoutError:
            print(f"⚠️ Timeout ao parar agente {self.jid} - forçando parada")
            # Forçar parada se necessário
            if hasattr(self, 'client') and self.client:
                try:
                    self.client.abort()
                except:
                    pass
        except Exception as e:
            print(f"⚠️ Erro ao parar agente {self.jid}: {e}")
        
        self._is_stopping = False