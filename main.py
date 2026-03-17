import os
import json
import time
import threading
import requests
import shutil
import hashlib
import datetime
import queue
from pathlib import Path
from tkinter import Tk, simpledialog, filedialog, messagebox
from PIL import Image, ImageDraw
import pystray
from send2trash import send2trash

APP_NAME = "Webhook-Uploader"
BASE_DIR = Path(os.getenv("LOCALAPPDATA")) / APP_NAME
CFG_DIR = BASE_DIR / "cfg"
LOG_DIR = BASE_DIR / "log"

CONFIG_FILE = CFG_DIR / "cfg.json"
LOG_FILE = LOG_DIR / "log.json"
TEMPLATE_FILE = CFG_DIR / "post.txt"
DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

file_lock = threading.RLock()
gui_queue = queue.Queue()
monitoring = True
icon_global = None
send_lock = threading.Lock()


def load_json(path, default):
    with file_lock:
        if not path.exists():
            return default
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default



def save_json(path, data):
    with file_lock:
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving file: {e}")



def load_template():
    with file_lock:
        CFG_DIR.mkdir(parents=True, exist_ok=True)
        if not TEMPLATE_FILE.exists():
            default = """🆕
📄 `{filename}`
📅 `{creation_str}`
🆙 Upload: {upload_str}
___"""
            TEMPLATE_FILE.write_text(default, encoding="utf-8")
            return default
        try:
            with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return """🆕
📄 `{filename}`
📅 `{creation_str}`
🆙 Upload: {upload_str}
___"""


config = load_json(CONFIG_FILE, {"folder": "", "webhook": ""})
sent_history = load_json(LOG_FILE, [])



def create_status_image(active):
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    color = (88, 101, 242) if active else (242, 163, 24)
    d.ellipse((4, 4, 60, 60), fill=color + (255,))
    d.ellipse((16, 16, 48, 48), fill=(30, 31, 34, 255))
    return img



def get_file_hash(path):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None



def file_is_free(path):
    try:
        with open(path, "rb+"):
            return True
    except Exception:
        return False



def send_file(path):
    if not config.get("webhook"):
        return False

    filename = os.path.basename(path)
    error_dir = Path(config["folder"]) / "ERROR"

    try:
        if os.path.getsize(path) / (1024 * 1024) > 25:
            error_dir.mkdir(exist_ok=True)
            shutil.move(path, error_dir / filename)
            return False
    except Exception:
        return False

    file_hash = get_file_hash(path)
    if not file_hash:
        return False

    with file_lock:
        if any(item.get("hash") == file_hash for item in sent_history):
            return False

    if not file_is_free(path):
        return False

    try:
        stat = os.stat(path)
        now_dt = datetime.datetime.now()
        creation_dt = datetime.datetime.fromtimestamp(stat.st_ctime)
        creation_str = f"{DAYS_OF_WEEK[creation_dt.weekday()]}, {creation_dt.strftime('%d/%m/%y %H:%M:%S')}"
        upload_str = f"{DAYS_OF_WEEK[now_dt.weekday()]}, {now_dt.strftime('%d/%m/%y %H:%M:%S')}"

        template = load_template()
        message = template.format(filename=filename, creation_str=creation_str, upload_str=upload_str)

        for attempt in range(4):
            try:
                with open(path, "rb") as f:
                    res = requests.post(
                        config["webhook"],
                        data={"content": message},
                        files={"file": (filename, f)},
                        timeout=15,
                    )

                if res.status_code in [200, 204]:
                    send2trash(os.path.abspath(path))
                    with file_lock:
                        sent_history.append({"file": filename, "hash": file_hash, "date": upload_str})
                    save_json(LOG_FILE, sent_history)
                    return True

                if res.status_code == 429:
                    time.sleep(2 ** attempt)
                    continue

                break
            except Exception:
                time.sleep(2 ** attempt)

        return False
    except Exception:
        return False



def send_now_manual():
    if not config.get("folder"):
        return

    if not send_lock.acquire(blocking=False):
        return

    try:
        files = [
            os.path.join(config["folder"], f)
            for f in os.listdir(config["folder"])
            if os.path.isfile(os.path.join(config["folder"], f))
        ]
        for file in sorted(files, key=os.path.getctime):
            if not monitoring:
                break
            if send_file(file):
                time.sleep(10)
    finally:
        send_lock.release()



def monitoring_loop():
    while True:
        if monitoring and config.get("folder") and config.get("webhook"):
            if send_lock.acquire(blocking=False):
                try:
                    now = time.time()
                    files = [
                        os.path.join(config["folder"], f)
                        for f in os.listdir(config["folder"])
                        if os.path.isfile(os.path.join(config["folder"], f))
                    ]
                    ready = [p for p in files if now - os.path.getctime(p) >= 3600]

                    for file in sorted(ready, key=os.path.getctime):
                        if not monitoring:
                            break
                        if send_file(file):
                            time.sleep(10)
                except Exception:
                    pass
                finally:
                    send_lock.release()

        for _ in range(300):
            if not monitoring:
                break
            time.sleep(1)



def build_hidden_root():
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    return root



def ask_folder_gui():
    root = build_hidden_root()
    try:
        folder = filedialog.askdirectory(title="Select folder to monitor", parent=root)
        if folder:
            config["folder"] = folder
            save_json(CONFIG_FILE, config)
    finally:
        root.destroy()



def ask_webhook_gui():
    root = build_hidden_root()
    try:
        webhook = simpledialog.askstring("Webhook", "Paste the Discord Webhook:", parent=root)
        if webhook:
            webhook = webhook.strip()
            if "discord.com/api/webhooks/" in webhook:
                config["webhook"] = webhook
                save_json(CONFIG_FILE, config)
            else:
                messagebox.showwarning("Invalid Webhook", "The webhook URL seems invalid.", parent=root)
    finally:
        root.destroy()



def clear_history_gui():
    root = build_hidden_root()
    try:
        ok = messagebox.askyesno("Clear History", "Do you want to clear the sent history?", parent=root)
        if ok:
            with file_lock:
                sent_history.clear()
            save_json(LOG_FILE, sent_history)
    finally:
        root.destroy()



def first_run_setup():
    if not config.get("folder"):
        ask_folder_gui()
    if not config.get("webhook"):
        ask_webhook_gui()



def process_gui_queue():
    while True:
        try:
            action = gui_queue.get(timeout=1)
            if action == "setup":
                first_run_setup()
            elif action == "change_folder":
                ask_folder_gui()
            elif action == "change_webhook":
                ask_webhook_gui()
            elif action == "clear_history":
                clear_history_gui()
            elif action == "exit":
                break
        except queue.Empty:
            continue



def toggle_monitoring(icon, item=None):
    global monitoring
    monitoring = not monitoring
    icon.icon = create_status_image(monitoring)
    icon.title = "Discord Uploader (Monitoring)" if monitoring else "Discord Uploader (Paused)"



def action_send_now(icon, item=None):
    threading.Thread(target=send_now_manual, daemon=True).start()



def action_change_folder(icon, item=None):
    gui_queue.put("change_folder")



def action_change_webhook(icon, item=None):
    gui_queue.put("change_webhook")



def action_clear_history(icon, item=None):
    gui_queue.put("clear_history")



def action_open_config(icon, item=None):
    CFG_DIR.mkdir(parents=True, exist_ok=True)
    os.startfile(CFG_DIR)



def action_exit(icon, item=None):
    icon.stop()
    gui_queue.put("exit")



if __name__ == "__main__":
    threading.Thread(target=monitoring_loop, daemon=True).start()
    threading.Thread(target=process_gui_queue, daemon=True).start()

    if not config.get("folder") or not config.get("webhook"):
        gui_queue.put("setup")

    menu = pystray.Menu(
        pystray.MenuItem("Send Now", action_send_now),
        pystray.MenuItem("Pause / Resume", toggle_monitoring),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Change Folder", action_change_folder),
        pystray.MenuItem("Configure Webhook", action_change_webhook),
        pystray.MenuItem("Clear History", action_clear_history),
        pystray.MenuItem("Open Config Folder", action_open_config),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Exit Program", action_exit),
    )

    icon_global = pystray.Icon(
        APP_NAME,
        create_status_image(True),
        "Discord Uploader (Monitoring)",
        menu,
    )
    icon_global.run()
