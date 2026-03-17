import os
import json
import time
import threading
import requests
import shutil
import hashlib
from pathlib import Path
from send2trash import send2trash
from tkinter import Tk, simpledialog, filedialog, messagebox
from PIL import Image, ImageDraw
import pystray

# CONFIG
APP_NAME = "Webhook_Uploader"
CONFIG_DIR = Path(os.getenv("LOCALAPPDATA")) / APP_NAME
CONFIG_FILE = CONFIG_DIR / "config.json"
LOG_FILE = CONFIG_DIR / "enviados_log.json"

file_lock = threading.Lock()
monitorando = True

def carregar_json(caminho, default):
    with file_lock:
        if not caminho.exists(): return default
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
            print(f"Erro salvar JSON: {e}")

config = carregar_json(CONFIG_FILE, {"pasta": "", "webhook": ""})
historico_enviados = carregar_json(LOG_FILE, [])

def get_file_hash(caminho):
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

# INTERFACE
def pedir_config_gui():
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    root.lift()
    root.focus_force()

    if not config.get("pasta") or not os.path.isdir(config["pasta"]):
        nova_pasta = filedialog.askdirectory(title="Selecione a pasta", parent=root)
        if nova_pasta:
            config["pasta"] = nova_pasta
            salvar_json(CONFIG_FILE, config)

    if not config.get("webhook") or "discord.com/api/webhooks/" not in config["webhook"]:
        novo = simpledialog.askstring("Webhook", "Cole URL Discord:", parent=root)
        if novo and "discord.com/api/webhooks/" in novo:
            config["webhook"] = novo.strip()
            salvar_json(CONFIG_FILE, config)
        elif novo:
            messagebox.showwarning("Aviso", "URL inválida.", parent=root)
    root.destroy()

def trocar_pasta():
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    root.lift()
    root.focus_force()
    nova_pasta = filedialog.askdirectory(title="Nova Pasta Monitorada", parent=root)
    if nova_pasta and os.path.isdir(nova_pasta):
        config["pasta"] = nova_pasta
        salvar_json(CONFIG_FILE, config)
    root.destroy()

def trocar_webhook():
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    root.lift()
    root.focus_force()
    novo_webhook = simpledialog.askstring("Novo Webhook", "Cole o URL do webhook:", parent=root)
    if novo_webhook and "discord.com/api/webhooks/" in novo_webhook:
        config["webhook"] = novo_webhook.strip()
        salvar_json(CONFIG_FILE, config)
    elif novo_webhook:
        messagebox.showwarning("Aviso", "URL inválida.", parent=root)
    root.destroy()

# ARQUIVO LIVRE
def arquivo_esta_livre(caminho):
    try:
        for _ in range(5):
            size1 = os.path.getsize(caminho)
            time.sleep(1.5)
            size2 = os.path.getsize(caminho)
            if size1 != size2: return False
        with open(caminho, 'rb+'): return True
    except Exception: return False

# ENVIO
def enviar_arquivo(caminho):
    if not config.get("webhook"): return False
    nome_arquivo = os.path.basename(caminho)

    try:
        file_hash = get_file_hash(caminho)
        if any(item.get('hash') == file_hash for item in historico_enviados):
            print(f"Ignorado (duplicata): {nome_arquivo}")
            return False
    except:
        return False

    if not arquivo_esta_livre(caminho):
        return False

    try:
        stat = os.stat(caminho)
        data_envio = time.strftime("%d/%m/%Y %H:%M:%S")
        data_criacao = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(stat.st_ctime))
        ext = os.path.splitext(caminho)[1].lower()

        mensagem = f"🆕\n\n📤 **Novo Upload** 📤\n\n📅 Envio: {data_envio}\n\n🕒 Criação: {data_criacao}\n\n📄 Tipo: {ext}\n\n📂 Arquivo: {nome_arquivo}\n\n---"

        for tentativa in range(4):
            try:
                with open(caminho, "rb") as f:
                    res = requests.post(
                        config["webhook"],
                        data={"content": mensagem},
                        files={"file": (nome_arquivo, f)},
                        timeout=60
                    )

                if res.status_code in [200, 204]:
                    send2trash(os.path.abspath(caminho))
                    historico_enviados.append({"arquivo": nome_arquivo, "hash": file_hash, "data": data_envio})
                    if len(historico_enviados) > 2000:
                        historico_enviados[:] = historico_enviados[-2000:]
                    salvar_json(LOG_FILE, historico_enviados)
                    return True

                elif res.status_code == 413:
                    error_dir = Path(config["pasta"]) / "ERROR"
                    error_dir.mkdir(exist_ok=True)
                    shutil.move(caminho, error_dir / nome_arquivo)
                    print(f"Movido ERROR: {nome_arquivo}")
                    return False

                elif res.status_code >= 500 or res.status_code in (429, 408):
                    if tentativa < 3: time.sleep(2 ** tentativa)
                    continue

                else:
                    print(f"Erro {nome_arquivo}: {res.status_code}")
                    return False

            except (requests.exceptions.RequestException, OSError, TimeoutError, ConnectionError) as e:
                if tentativa == 3:
                    print(f"Falha final {nome_arquivo}: {e}")
                    return False
                time.sleep(2 ** tentativa)
        return False

    except Exception as e:
        print(f"Erro {nome_arquivo}: {e}")
        return False

# MONITOR
def loop_monitoramento():
    global monitorando
    while True:
        if monitorando and config.get("pasta") and config.get("webhook"):
            if os.path.isdir(config["pasta"]):
                try:
                    arquivos = [os.path.join(config["pasta"], f) for f in os.listdir(config["pasta"]) if os.path.isfile(os.path.join(config["pasta"], f))]
                    agora = time.time()
                    arquivos = [p for p in arquivos if agora - os.path.getctime(p) >= 3600]
                    arquivos.sort(key=os.path.getctime)
                    for arquivo in arquivos:
                        if not monitorando: break
                        if enviar_arquivo(arquivo):
                            time.sleep(2)
                except Exception as e:
                    print(f"Erro diretório: {e}")
        for _ in range(60):
            if not monitorando: break
            time.sleep(1)

# TRAY
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

# MAIN
if __name__ == "__main__":
    threading.Thread(target=loop_monitoramento, daemon=True).start()
    
    if not config.get("pasta") or not config.get("webhook"):
        pedir_config_gui()

    menu = pystray.Menu(
        pystray.MenuItem("Pausar / Retomar", acao_pausar),
        pystray.MenuItem("Trocar Pasta", lambda: threading.Thread(target=trocar_pasta, daemon=True).start()),
        pystray.MenuItem("Trocar Webhook", lambda: threading.Thread(target=trocar_webhook, daemon=True).start()),
        pystray.MenuItem("Abrir Pasta Config", lambda: os.startfile(CONFIG_DIR)),
        pystray.MenuItem("Sair", acao_sair)
    )
   
    icon = pystray.Icon(APP_NAME, criar_imagem(True), "Webhook Uploader", menu)
    icon.run()