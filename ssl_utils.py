import ssl
import warnings
import asyncio
from contextlib import asynccontextmanager

def setup_ssl_error_handling():
    """
    Configura o tratamento de erros SSL para suprimir avisos verbosos
    e configurar contextos SSL mais permissivos para desenvolvimento
    """
    # Suprimir avisos de SSL
    warnings.filterwarnings('ignore', category=DeprecationWarning, module='ssl')
    
    # Criar contexto SSL permissivo para desenvolvimento
    try:
        ssl._create_default_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    
    print("✅ Configuração SSL inicializada (modo permissivo para desenvolvimento)")

@asynccontextmanager
async def safe_shutdown():
    """
    Context manager para garantir shutdown gracioso de conexões assíncronas
    """
    try:
        yield
    except KeyboardInterrupt:
        print("\n🔻 Interrupção detectada - encerrando de forma segura...")
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")
    finally:
        # Aguardar tarefas pendentes
        try:
            pending = asyncio.all_tasks()
            for task in pending:
                if not task.done():
                    task.cancel()
            await asyncio.gather(*pending, return_exceptions=True)
        except Exception:
            pass
        print("✅ Shutdown completo")