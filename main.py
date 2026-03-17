import os
import time
import threading
import requests
import mimetypes
from datetime import datetime
from send2trash import send2trash
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw

# ================= CONFIG =================

WEBHOOK_URL = "webhookaqui"
PASTA_MONITORADA = r"G:\My PICS\screenshots"
INTERVALO_ENTRE_ARQUIVOS = 10
INTERVALO_VARREDURA = 60
MAX_RETRIES = 3

# ===========================================

rodando = True
monitoramento_ativo = True
arquivos_enviados = set()

os.makedirs(PASTA_MONITORADA, exist_ok=True)

LOG_ENVIADOS = os.path.join(PASTA_MONITORADA, "enviados.log")
LOG_ERROS = os.path.join(PASTA_MONITORADA, "erros.log")

if os.path.exists(LOG_ENVIADOS):
    with open(LOG_ENVIADOS, "r", encoding="utf-8") as f:
        arquivos_enviados = set(f.read().splitlines())


def registrar_enviado(nome):
    with open(LOG_ENVIADOS, "a", encoding="utf-8") as f:
        f.write(nome + "\n")


def registrar_erro(texto):
    with open(LOG_ERROS, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {texto}\n")


def detectar_tipo(caminho):
    tipo, _ = mimetypes.guess_type(caminho)
    if tipo:
        if "image" in tipo:
            if caminho.lower().endswith(".gif"):
                return "gif"
            return "imagem"
        elif "video" in tipo:
            return "video"
    return "arquivo"


def enviar_arquivo(caminho):
    nome = os.path.basename(caminho)
    tipo = detectar_tipo(caminho)
    data_criacao = datetime.fromtimestamp(os.path.getctime(caminho))

    mensagem = f"📁 Novo {tipo}\n🕒 Criado em: {data_criacao.strftime('%d/%m/%Y %H:%M:%S')}"

    for tentativa in range(MAX_RETRIES):
        try:
            with open(caminho, "rb") as f:
                r = requests.post(
                    WEBHOOK_URL,
                    data={"content": mensagem},
                    files={"file": f},
                    timeout=15
                )
            if r.status_code in (200, 204):
                return True
        except Exception as e:
            if tentativa == MAX_RETRIES - 1:
                registrar_erro(f"Falha ao enviar {nome}: {str(e)}")
        time.sleep(2)
    return False


def monitorar():
    global rodando, monitoramento_ativo

    while rodando:
        if not monitoramento_ativo:
            time.sleep(1)
            continue

        try:
            arquivos = sorted(os.listdir(PASTA_MONITORADA))

            for arquivo in arquivos:

                if not monitoramento_ativo:
                    break

                caminho = os.path.join(PASTA_MONITORADA, arquivo)

                if not os.path.isfile(caminho):
                    continue

                if arquivo.endswith(".log"):
                    continue

                if arquivo in arquivos_enviados:
                    continue

                sucesso = enviar_arquivo(caminho)

                if sucesso:
                    registrar_enviado(arquivo)
                    arquivos_enviados.add(arquivo)
                    send2trash(caminho)

                    # Intervalo entre envios
                    time.sleep(INTERVALO_ENTRE_ARQUIVOS)

        except Exception as e:
            registrar_erro(f"Erro geral: {str(e)}")

        time.sleep(INTERVALO_VARREDURA)


def criar_icone(cor):
    img = Image.new("RGB", (64, 64), (25, 25, 25))
    draw = ImageDraw.Draw(img)
    draw.rectangle((16, 16, 48, 48), fill=cor)
    return img


def atualizar_icone(icon):
    if monitoramento_ativo:
        icon.icon = criar_icone((0, 180, 255))  # Azul = ativo
        icon.title = "Uploader (Ativo)"
    else:
        icon.icon = criar_icone((200, 60, 60))  # Vermelho = pausado
        icon.title = "Uploader (Pausado)"


def pausar(icon, item):
    global monitoramento_ativo
    monitoramento_ativo = False
    atualizar_icone(icon)


def retomar(icon, item):
    global monitoramento_ativo
    monitoramento_ativo = True
    atualizar_icone(icon)


def sair(icon, item):
    global rodando
    rodando = False
    icon.stop()


def iniciar_tray():
    icon = pystray.Icon(
        "Uploader",
        criar_icone((0, 180, 255)),
        "Uploader (Ativo)",
        menu=pystray.Menu(
            item("Pausar", pausar),
            item("Retomar", retomar),
            item("Sair", sair)
        )
    )

    threading.Thread(target=monitorar, daemon=True).start()
    icon.run()


if __name__ == "__main__":
    iniciar_tray()