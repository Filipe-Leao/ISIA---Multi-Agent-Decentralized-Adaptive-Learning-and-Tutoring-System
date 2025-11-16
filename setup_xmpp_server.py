"""
Script para configurar servidor XMPP local para desenvolvimento
"""
import subprocess
import sys
import os
import platform

def install_prosody_windows():
    """Instala Prosody no Windows usando chocolatey ou manual"""
    print("🏗️ Tentando instalar Prosody no Windows...")
    
    # Verificar se chocolatey está disponível
    try:
        subprocess.run(["choco", "--version"], check=True, capture_output=True)
        print("✅ Chocolatey encontrado, instalando Prosody...")
        subprocess.run(["choco", "install", "prosody", "-y"], check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Chocolatey não encontrado")
        print("📥 Baixe Prosody manualmente de: https://prosody.im/download/windows")
        return False

def install_prosody_linux():
    """Instala Prosody no Linux"""
    print("🏗️ Instalando Prosody no Linux...")
    try:
        # Ubuntu/Debian
        subprocess.run(["sudo", "apt", "update"], check=True)
        subprocess.run(["sudo", "apt", "install", "-y", "prosody"], check=True)
        return True
    except subprocess.CalledProcessError:
        try:
            # CentOS/RHEL/Fedora
            subprocess.run(["sudo", "yum", "install", "-y", "prosody"], check=True)
            return True
        except subprocess.CalledProcessError:
            print("❌ Falha na instalação automática")
            return False

def setup_prosody_config():
    """Configura Prosody para desenvolvimento local"""
    config_content = """
-- Configuração básica do Prosody para desenvolvimento
-- Arquivo: /etc/prosody/prosody.cfg.lua (Linux) ou data\\prosody.cfg.lua (Windows)

admins = { }

modules_enabled = {
    "roster";
    "saslauth";
    "tls";
    "disco";
    "carbons";
    "pep";
    "private";
    "blocklist";
    "vcard4";
    "vcard_legacy";
    "limits";
    "version";
    "uptime";
    "time";
    "ping";
    "register";
    "mam";
    "csi_simple";
    "carbons";
}

allow_registration = true;
c2s_require_encryption = false;
s2s_require_encryption = false;

authentication = "internal_plain";

VirtualHost "localhost"
    enabled = true;

pidfile = "/var/run/prosody/prosody.pid";
"""
    
    print("📝 Configuração recomendada para Prosody:")
    print(config_content)
    
    # Criar arquivo de configuração local
    config_file = "prosody_dev.cfg.lua"
    with open(config_file, 'w') as f:
        f.write(config_content)
    
    print(f"✅ Configuração salva em: {config_file}")
    print("🔧 Para usar esta configuração:")
    print("   prosody --config=prosody_dev.cfg.lua")

def check_and_start_prosody():
    """Verifica se Prosody está rodando e tenta iniciá-lo"""
    try:
        # Verificar se prosody está instalado
        result = subprocess.run(["prosody", "--version"], capture_output=True, text=True)
        print(f"✅ Prosody encontrado: {result.stdout.strip()}")
        
        # Tentar iniciar prosody
        print("🚀 Iniciando Prosody...")
        subprocess.Popen(["prosody", "--config=prosody_dev.cfg.lua"])
        print("✅ Prosody iniciado em segundo plano")
        return True
        
    except FileNotFoundError:
        print("❌ Prosody não encontrado no sistema")
        return False

def main():
    """Função principal"""
    print("🔧 Configurador de Servidor XMPP para SPADE")
    print("="*50)
    
    system = platform.system()
    
    print(f"🖥️ Sistema operacional detectado: {system}")
    
    if system == "Windows":
        if not install_prosody_windows():
            print("\n📋 INSTRUÇÕES MANUAIS:")
            print("1. Baixe Prosody de https://prosody.im/download/windows")
            print("2. Instale seguindo as instruções")
            print("3. Execute este script novamente")
            return
    elif system == "Linux":
        if not install_prosody_linux():
            print("❌ Falha na instalação automática")
            return
    else:
        print("❌ Sistema não suportado para instalação automática")
        print("📋 Instale Prosody manualmente: https://prosody.im/download")
        return
    
    # Configurar Prosody
    setup_prosody_config()
    
    # Tentar iniciar
    if check_and_start_prosody():
        print("\n🎉 Prosody configurado e iniciado com sucesso!")
        print("🌐 Servidor XMPP disponível em: localhost:5222")
        print("👥 Registros permitidos para desenvolvimento")
        print("\n🚀 Agora você pode executar a simulação SPADE!")
    else:
        print("\n❌ Problemas na inicialização do Prosody")
        print("🔧 Verifique a instalação manualmente")

if __name__ == "__main__":
    main()