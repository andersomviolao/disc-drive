import os
import sys
import json
import time
import threading
import requests
from pathlib import Path
from send2trash import send2trash
from tkinter import Tk, simpledialog, filedialog, messagebox
from PIL import Image, ImageDraw
import pystray

# ==============================
# CONFIGURAÇÃO E LOCKS
# ==============================
APP_NAME = "Webhook_Uploader"
CONFIG_DIR = Path(os.getenv("LOCALAPPDATA")) / APP_NAME
CONFIG_FILE = CONFIG_DIR / "config.json"
LOG_FILE = CONFIG_DIR / "enviados_log.json"

# Lock para garantir que leitura/escrita de arquivos não ocorram simultaneamente
file_lock = threading.Lock()
monitorando = True

def carregar_json(caminho, default):
    with file_lock:
        if not caminho.exists():
            return default
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return default

def salvar_json(caminho, data):
    with file_lock:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        try:
            with open(caminho, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Erro ao salvar JSON: {e}")

# Inicialização das configurações e histórico
config = carregar_json(CONFIG_FILE, {"pasta": "", "webhook": ""})
historico_enviados = carregar_json(LOG_FILE, [])

# ==============================
# INTERFACE (REFINADA)
# ==============================
def pedir_config_gui():
    """Abre janela de configuração com reforço de foco para não abrir 'atrás'"""
    root = Tk()
    root.withdraw()
    
    # Força a janela a aparecer na frente de todas as outras
    root.attributes("-topmost", True)
    root.lift()
    root.focus_force()
    
    # Seleção de Pasta
    if not config.get("pasta") or not os.path.isdir(config["pasta"]):
        nova_pasta = filedialog.askdirectory(title="Selecione a pasta a ser monitorada", parent=root)
        if nova_pasta:
            config["pasta"] = nova_pasta
            salvar_json(CONFIG_FILE, config)

    # Configuração do Webhook
    if not config.get("webhook") or "discord.com/api/webhooks/" not in config["webhook"]:
        novo_webhook = simpledialog.askstring("Webhook", "Cole o URL do webhook do Discord:", parent=root)
        if novo_webhook and "discord.com/api/webhooks/" in novo_webhook:
            config["webhook"] = novo_webhook.strip()
            salvar_json(CONFIG_FILE, config)
        elif novo_webhook:
            messagebox.showwarning("Aviso", "URL de Webhook inválida.", parent=root)
    
    root.destroy()

# ==============================
# LÓGICA DE INTEGRIDADE E ENVIO
# ==============================
def arquivo_esta_livre(caminho):
    """Verifica se o arquivo pode ser aberto (não está sendo gravado por outro app)"""
    try:
        # Tenta abrir para leitura e escrita. Se falhar, o Windows bloqueou o acesso.
        with open(caminho, 'rb+'):
            return True
    except (IOError, OSError):
        return False

def enviar_arquivo(caminho):
    if not config.get("webhook"): return False
    
    nome_arquivo = os.path.basename(caminho)

    # --- NOVO: VERIFICAÇÃO DE DUPLICIDADE ---
    # Verifica se este nome de arquivo já está no nosso histórico (limitado aos últimos 1000)
    com_lock = carregar_json(LOG_FILE, []) # Recarrega para garantir que está sincronizado
    if any(item['arquivo'] == nome_arquivo for item in com_lock):
        print(f"Arquivo ignorado (já enviado anteriormente): {nome_arquivo}")
        # Opcional: Você pode decidir se quer excluir o arquivo repetido ou apenas ignorar.
        # Se quiser que ele saia da pasta mesmo sendo repetido, descomente a linha abaixo:
        # send2trash(os.path.abspath(caminho))
        return False
    # ---------------------------------------

    if not arquivo_esta_livre(caminho):
        return False

    try:
        if os.path.getsize(caminho) > 8 * 1024 * 1024:
            return False

        stat = os.stat(caminho)
        data_envio = time.strftime("%d/%m/%Y %H:%M:%S")
        data_criacao = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(stat.st_ctime))
        ext = os.path.splitext(caminho)[1].lower()

        # Formatação da mensagem conforme solicitado
        mensagem = (
            f"🆕\n\n"
            f"📤 **Novo Upload** 📤\n\n"
            f"📅 Envio: {data_envio}\n\n"
            f"🕒 Criação: {data_criacao}\n\n"
            f"📄 Tipo: {ext}\n\n"
            f"📂 Arquivo: {nome_arquivo}\n\n"
            f"---"
        )

        with open(caminho, "rb") as f:
            res = requests.post(
                config["webhook"],
                data={"content": mensagem},
                files={"file": (nome_arquivo, f)},
                timeout=30
            )
        
        if res.status_code in [200, 204]:
            time.sleep(1) 
            send2trash(os.path.abspath(caminho))
            
            global historico_enviados
            historico_enviados.append({
                "arquivo": nome_arquivo,
                "data": data_envio
            })
            
            if len(historico_enviados) > 1000:
                historico_enviados = historico_enviados[-1000:]
                
            salvar_json(LOG_FILE, historico_enviados)
            return True
        return False
    except Exception as e:
        print(f"Erro: {e}")
        return False

# ==============================
# MONITORAMENTO
# ==============================
def loop_monitoramento():
    global monitorando
    while True:
        if monitorando and config.get("pasta") and config.get("webhook"):
            if os.path.isdir(config["pasta"]):
                try:
                    arquivos = [os.path.join(config["pasta"], f) for f in os.listdir(config["pasta"]) 
                               if os.path.isfile(os.path.join(config["pasta"], f))]
                    
                    # Ordena por data de criação (mais antigos primeiro)
                    arquivos.sort(key=lambda x: os.path.getctime(x))

                    for arquivo in arquivos:
                        if not monitorando: break
                        if enviar_arquivo(arquivo):
                            time.sleep(2) # Pausa curta entre arquivos bem-sucedidos
                except Exception as e:
                    print(f"Erro ao ler diretório: {e}")

            # Ciclo de checagem a cada 30 segundos
            for _ in range(30): 
                if not monitorando: break
                time.sleep(1)
        else:
            time.sleep(2)

# ==============================
# TRAY (BANDEJA DO SISTEMA)
# ==============================
def criar_imagem(ativo):
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cor = (0, 200, 255) if ativo else (255, 200, 0)
    d.ellipse((4, 4, 60, 60), fill=cor + (255,))
    d.ellipse((18, 18, 46, 46), fill=(30, 30, 30, 255))
    return img

def acao_pausar(icon):
    global monitorando
    monitorando = not monitorando
    icon.icon = criar_imagem(monitorando)

def acao_sair(icon):
    icon.stop()
    os._exit(0)

# ==============================
# EXECUÇÃO PRINCIPAL
# ==============================
if __name__ == "__main__":
    # Inicia o monitor em segundo plano
    threading.Thread(target=loop_monitoramento, daemon=True).start()

    # Se estiver faltando configuração, chama a GUI
    if not config["pasta"] or not config["webhook"]:
        threading.Thread(target=pedir_config_gui, daemon=True).start()

    # Criação do Menu do Tray
    menu = pystray.Menu(
        pystray.MenuItem("Pausar / Retomar", acao_pausar),
        pystray.MenuItem("Configurações", lambda: threading.Thread(target=pedir_config_gui).start()),
        pystray.MenuItem("Abrir Pasta Config", lambda: os.startfile(CONFIG_DIR)),
        pystray.MenuItem("Sair", acao_sair)
    )
    
    icon = pystray.Icon(APP_NAME, criar_imagem(True), "Webhook Uploader", menu)
    icon.run()