import sys
import os
import json
import time
import math
import base64
import colorsys
import threading
import requests
import shutil
import hashlib
import datetime
import traceback
import subprocess
import re
import queue
from pathlib import Path
try:
    import ctypes
except Exception:
    ctypes = None
try:
    from ctypes import wintypes
except Exception:
    wintypes = None
from send2trash import send2trash
from PySide6.QtCore import Qt, Signal, QObject, QEasingCurve, QPropertyAnimation, QTimer, QRect, QSize, QRectF, QByteArray, QPoint, QBuffer, QIODevice
from PySide6.QtGui import QColor, QCursor, QFont, QIcon, QPainter, QPainterPath, QPen, QPixmap, QBrush, QLinearGradient, QIntValidator, QImage, QImageReader
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QFrame, QHBoxLayout, QLabel, QLineEdit, QSystemTrayIcon, QPushButton, QStackedWidget, QGraphicsOpacityEffect, QFileDialog, QScrollArea, QTextEdit, QSizePolicy, QGridLayout
try:
    import winreg
except Exception:
    winreg = None
APP_NAME = 'disc-drive'
APP_DIR_NAME = 'disc-drive'
APP_VERSION = '3.0.29'
WINDOW_WIDTH = 560
WINDOW_HEIGHT = 380

def get_runtime_dir() -> Path:
    try:
        if getattr(sys, 'frozen', False):
            return Path(sys.executable).resolve().parent
        if '__file__' in globals():
            return Path(__file__).resolve().parent
        return Path(sys.argv[0]).resolve().parent
    except Exception:
        return Path.cwd()
RUNTIME_DIR = get_runtime_dir()
LOCAL_FFMPEG_PATH = RUNTIME_DIR / 'ffmpeg' / 'bin' / 'ffmpeg.exe'
BASE_DIR = Path(os.getenv('LOCALAPPDATA', str(Path.home()))) / APP_DIR_NAME
CONFIG_FILE = BASE_DIR / 'config.json'
LOG_FILE = BASE_DIR / 'sent_log.json'
FILES_DIR = RUNTIME_DIR / 'files'
DEFAULT_PLACEHOLDER_IMAGE_FILE = FILES_DIR / 'default-img.png'
AVATAR_IMAGE_FILE = BASE_DIR / 'avatar.png'
AVATAR_MODE_WEBHOOK = 'webhook'
AVATAR_MODE_DEFAULT = 'default'
AVATAR_MODE_MANUAL = 'manual'
THUMBS_DIR = BASE_DIR / 'thumbs-log'
THUMB_TILE_SIZE = 64
THUMB_CACHE_DIMENSION = 300
THUMB_HOME_VISIBLE_COUNT = 7
THUMB_LOG_LIMIT = 1000
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp'}
VIDEO_EXTENSIONS = {'.mp4', '.mov', '.m4v', '.avi', '.mkv', '.webm', '.wmv', '.mpeg', '.mpg', '.m2ts', '.ts'}
SUPPORTED_MEDIA_EXTENSIONS = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS
DAYS_OF_WEEK = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
BG = '#0f1012'
PANEL = '#151618'
TEXT = '#d8d8d8'
MUTED = '#7f7f7f'
FIELD_BG = '#222428'
FIELD_TEXT = '#e9ecf2'
BLUE = '#5865F2'
YELLOW = '#f2b01e'
ICON_GRAY = '#7a7f89'
HOVER_DARK = '#222428'
RED = '#ff5f73'
GREEN = '#4fd18b'
CARD = '#1a1c20'
CARD_BORDER = '#252830'
DEFAULT_EMBED_COLOR = BLUE
FONT_TINY = 8
FONT_BASE = 9
FONT_MEDIUM = 10
FONT_LARGE = 11
FONT_TITLE = 12
DEFAULT_WAIT_TIME = 3600
DEFAULT_POST_INTERVAL = 10
MONITOR_CHECK_INTERVAL = 5
STARTUP_REG_PATH = 'Software\\Microsoft\\Windows\\CurrentVersion\\Run'
file_lock = threading.RLock()
thumb_lock = threading.RLock()
send_lock = threading.Lock()
sending_event = threading.Event()
thumbnail_task_queue = queue.Queue()
thumbnail_generation_epoch = 0
monitoring = False
stop_event = threading.Event()

def set_window_pos_safely(widget, *, x=None, y=None, width=None, height=None, move=True, resize=True):
    if not move and (not resize):
        return
    if x is None:
        x = widget.x()
    if y is None:
        y = widget.y()
    if width is None:
        width = widget.width()
    if height is None:
        height = widget.height()
    if sys.platform.startswith('win') and ctypes is not None:
        try:
            hwnd = int(widget.winId())
            flags = 4 | 16
            if not move:
                flags |= 2
            if not resize:
                flags |= 1
            ctypes.windll.user32.SetWindowPos(hwnd, 0, int(x), int(y), int(width), int(height), flags)
            return
        except Exception as exc:
            pass
    if move and resize:
        widget.setGeometry(int(x), int(y), int(width), int(height))
    elif move:
        widget.move(int(x), int(y))
    elif resize:
        widget.resize(int(width), int(height))

def enforce_fixed_window_size(widget, *, width=WINDOW_WIDTH, height=WINDOW_HEIGHT):
    widget.setMinimumSize(width, height)
    widget.setMaximumSize(width, height)
    widget.setBaseSize(width, height)
    if widget.width() != width or widget.height() != height:
        set_window_pos_safely(widget, width=width, height=height, move=False, resize=True)

def load_json(path: Path, default):
    with file_lock:
        if not path.exists():
            return default
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return default

def save_json(path: Path, data):
    with file_lock:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

def default_template_text():
    return '🆕\n📄 `{filename}`\n📅 `{creation_str}`\n🆙 Upload: {upload_str}\n___'

def normalize_multiline_text(value, default: str) -> str:
    text = value if isinstance(value, str) else default
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    return text

def normalize_int(value, default: int, minimum: int=0) -> int:
    try:
        parsed = int(value)
    except Exception:
        return default
    return max(minimum, parsed)

def load_template():
    return normalize_multiline_text(config.get('post_template', default_template_text()), default_template_text())

def save_template(text: str):
    config['post_template'] = normalize_multiline_text(text, default_template_text())
    save_config()

def get_timer_enabled() -> bool:
    return bool(config.get('timer_enabled', True))

def get_delay_minutes() -> int:
    return normalize_int(config.get('delay_minutes', max(1, DEFAULT_WAIT_TIME // 60)), max(1, DEFAULT_WAIT_TIME // 60), minimum=1)

def get_wait_time_seconds() -> int:
    if not get_timer_enabled():
        return 0
    return get_delay_minutes() * 60

def get_post_interval_seconds() -> int:
    return normalize_int(config.get('post_interval_seconds', DEFAULT_POST_INTERVAL), DEFAULT_POST_INTERVAL, minimum=0)

def get_custom_webhook_name() -> str:
    return str(config.get('webhook_custom_name', '') or '').strip()

def get_effective_webhook_name(override_name: str | None=None) -> str:
    if override_name is not None:
        name = str(override_name or '').strip()
        return name or APP_NAME
    return get_custom_webhook_name() or APP_NAME

def parse_hex_color(value: str):
    text = (value or '').strip().upper()
    if text.startswith('#'):
        text = text[1:]
    if len(text) == 3 and all((c in '0123456789ABCDEF' for c in text)):
        text = ''.join((c * 2 for c in text))
    if len(text) == 6 and all((c in '0123456789ABCDEF' for c in text)):
        return f'#{text}'
    return None

def normalize_hex_color(value: str, default: str=DEFAULT_EMBED_COLOR) -> str:
    parsed = parse_hex_color(value)
    if parsed:
        return parsed
    return parse_hex_color(default) or BLUE

def discord_color_int(hex_color: str) -> int:
    return int(normalize_hex_color(hex_color)[1:], 16)

def render_template_text(template: str, filename: str, creation_str: str, upload_str: str) -> str:
    return template.replace('{filename}', filename).replace('{creation_str}', creation_str).replace('{upload_str}', upload_str)

def get_windows_creation_timestamp(path) -> float | None:
    if os.name != 'nt' or ctypes is None or wintypes is None:
        return None
    GENERIC_READ = 2147483648
    FILE_SHARE_READ = 1
    FILE_SHARE_WRITE = 2
    FILE_SHARE_DELETE = 4
    OPEN_EXISTING = 3
    FILE_ATTRIBUTE_NORMAL = 128
    INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value

    class FILETIME(ctypes.Structure):
        _fields_ = [('dwLowDateTime', wintypes.DWORD), ('dwHighDateTime', wintypes.DWORD)]
    kernel32 = ctypes.windll.kernel32
    CreateFileW = kernel32.CreateFileW
    CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    CreateFileW.restype = wintypes.HANDLE
    GetFileTime = kernel32.GetFileTime
    GetFileTime.argtypes = [wintypes.HANDLE, ctypes.POINTER(FILETIME), ctypes.POINTER(FILETIME), ctypes.POINTER(FILETIME)]
    GetFileTime.restype = wintypes.BOOL
    CloseHandle = kernel32.CloseHandle
    CloseHandle.argtypes = [wintypes.HANDLE]
    CloseHandle.restype = wintypes.BOOL
    handle = CreateFileW(str(path), GENERIC_READ, FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE, None, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, None)
    if handle == INVALID_HANDLE_VALUE:
        return None
    try:
        creation_time = FILETIME()
        if not GetFileTime(handle, ctypes.byref(creation_time), None, None):
            return None
        ticks = creation_time.dwHighDateTime << 32 | creation_time.dwLowDateTime
        if ticks <= 0:
            return None
        return (ticks - 116444736000000000) / 10000000.0
    finally:
        try:
            CloseHandle(handle)
        except Exception:
            pass

def get_file_creation_timestamp(path) -> float:
    path = str(path)
    if os.name == 'nt':
        try:
            timestamp = get_windows_creation_timestamp(path)
            if timestamp is not None and timestamp > 0:
                return float(timestamp)
        except Exception:
            pass
    try:
        stat = Path(path).stat()
        birth = getattr(stat, 'st_birthtime', None)
        if birth is not None and birth > 0:
            return float(birth)
    except Exception:
        pass
    try:
        timestamp = os.path.getctime(path)
        if timestamp > 0:
            return float(timestamp)
    except Exception:
        pass
    try:
        return float(Path(path).stat().st_mtime)
    except Exception:
        return time.time()

def format_file_creation_string(path) -> str:
    creation_dt = datetime.datetime.fromtimestamp(get_file_creation_timestamp(path))
    return f"{DAYS_OF_WEEK[creation_dt.weekday()]}, {creation_dt.strftime('%d/%m/%y %H:%M:%S')}"

def normalize_config(raw):
    raw = raw if isinstance(raw, dict) else {}
    legacy_wait_seconds = normalize_int(raw.get('wait_time_seconds', DEFAULT_WAIT_TIME), DEFAULT_WAIT_TIME, minimum=0)
    default_delay_minutes = max(1, round(legacy_wait_seconds / 60)) if legacy_wait_seconds > 0 else max(1, DEFAULT_WAIT_TIME // 60)
    return {'folder': raw.get('folder', ''), 'webhook': raw.get('webhook', ''), 'start_with_windows': bool(raw.get('start_with_windows', False)), 'delete_after_send': bool(raw.get('delete_after_send', True)), 'use_embed': bool(raw.get('use_embed', False)), 'embed_color': normalize_hex_color(raw.get('embed_color', DEFAULT_EMBED_COLOR)), 'post_template': normalize_multiline_text(raw.get('post_template', default_template_text()), default_template_text()), 'timer_enabled': bool(raw.get('timer_enabled', legacy_wait_seconds > 0)), 'delay_minutes': normalize_int(raw.get('delay_minutes', default_delay_minutes), default_delay_minutes, minimum=1), 'post_interval_seconds': normalize_int(raw.get('post_interval_seconds', DEFAULT_POST_INTERVAL), DEFAULT_POST_INTERVAL, minimum=0), 'webhook_custom_name': str(raw.get('webhook_custom_name', '') or '').strip(), 'webhook_default_name': str(raw.get('webhook_default_name', '') or '').strip(), 'webhook_default_source': str(raw.get('webhook_default_source', '') or '').strip(), 'avatar_mode': AVATAR_MODE_MANUAL if str(raw.get('avatar_mode', AVATAR_MODE_WEBHOOK) or AVATAR_MODE_WEBHOOK).strip().lower() in {'custom', AVATAR_MODE_MANUAL} else AVATAR_MODE_DEFAULT if str(raw.get('avatar_mode', AVATAR_MODE_WEBHOOK) or AVATAR_MODE_WEBHOOK).strip().lower() == AVATAR_MODE_DEFAULT else AVATAR_MODE_WEBHOOK, 'monitoring_enabled': bool(raw.get('monitoring_enabled', True)), 'window_x': normalize_int(raw.get('window_x', -1), -1, minimum=-1), 'window_y': normalize_int(raw.get('window_y', -1), -1, minimum=-1)}
config = normalize_config(load_json(CONFIG_FILE, {}))
monitoring = bool(config.get('monitoring_enabled', True))
sent_history = load_json(LOG_FILE, [])
if not isinstance(sent_history, list):
    sent_history = []

class UISignals(QObject):
    status_changed = Signal(bool)
    toast = Signal(str, str)
    refresh_fields = Signal()
    thumbnail_changed = Signal(str, bool)
    managed_window_deactivated = Signal()
signals = UISignals()

class CompactStackedWidget(QStackedWidget):

    def sizeHint(self):
        current = self.currentWidget()
        if current is not None:
            return current.sizeHint()
        return QSize(0, 0)

    def minimumSizeHint(self):
        return QSize(0, 0)
TRAY_ICON_SIZE = 64
TRAY_ICON_CENTER = TRAY_ICON_SIZE // 2
TRAY_RING_RADIUS = 23
TRAY_DOT_RADIUS = 5
TRAY_DOT_COUNT = 12
TRAY_BLUE = QColor(BLUE)
TRAY_YELLOW = QColor(255, 210, 0)
TRAY_GREEN = QColor(0, 220, 120)

def draw_tray_ring(color: QColor) -> QIcon:
    pix = QPixmap(TRAY_ICON_SIZE, TRAY_ICON_SIZE)
    pix.fill(Qt.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.Antialiasing)
    pen = QPen(color)
    pen.setWidth(8)
    painter.setPen(pen)
    painter.setBrush(Qt.NoBrush)
    painter.drawEllipse(TRAY_ICON_CENTER - TRAY_RING_RADIUS, TRAY_ICON_CENTER - TRAY_RING_RADIUS, TRAY_RING_RADIUS * 2, TRAY_RING_RADIUS * 2)
    painter.end()
    return QIcon(pix)

def draw_tray_sending(rotation: float) -> QIcon:
    pix = QPixmap(TRAY_ICON_SIZE, TRAY_ICON_SIZE)
    pix.fill(Qt.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.Antialiasing)
    pen = QPen(TRAY_BLUE)
    pen.setWidth(8)
    painter.setPen(pen)
    painter.setBrush(Qt.NoBrush)
    painter.drawEllipse(TRAY_ICON_CENTER - TRAY_RING_RADIUS, TRAY_ICON_CENTER - TRAY_RING_RADIUS, TRAY_RING_RADIUS * 2, TRAY_RING_RADIUS * 2)
    painter.setPen(Qt.NoPen)
    painter.setBrush(QBrush(TRAY_GREEN))
    for i in range(TRAY_DOT_COUNT):
        angle = i / TRAY_DOT_COUNT * 2 * math.pi + rotation
        x = TRAY_ICON_CENTER + math.cos(angle) * TRAY_RING_RADIUS
        y = TRAY_ICON_CENTER + math.sin(angle) * TRAY_RING_RADIUS
        painter.drawEllipse(int(x - TRAY_DOT_RADIUS), int(y - TRAY_DOT_RADIUS), TRAY_DOT_RADIUS * 2, TRAY_DOT_RADIUS * 2)
    painter.end()
    return QIcon(pix)

def create_tray_icon(active: bool, sending: bool=False, rotation: float=0.0) -> QIcon:
    if sending:
        return draw_tray_sending(rotation)
    return draw_tray_ring(TRAY_BLUE if active else TRAY_YELLOW)

def save_config():
    global config
    config = normalize_config(config)
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    FILES_DIR.mkdir(parents=True, exist_ok=True)
    save_json(CONFIG_FILE, config)
    signals.refresh_fields.emit()
_last_avatar_sync_key = None

def reset_avatar_sync_cache():
    global _last_avatar_sync_key
    _last_avatar_sync_key = None

def current_webhook_identity_key(webhook_url: str | None=None) -> str:
    webhook_url = (webhook_url or config.get('webhook', '') or '').strip()
    if not webhook_url:
        return ''
    return hashlib.sha256(webhook_url.encode('utf-8')).hexdigest()

def webhook_defaults_match_current() -> bool:
    return bool(config.get('webhook_default_source', '')) and config.get('webhook_default_source', '') == current_webhook_identity_key()

def aspect_fit_rect(target_rect: QRectF, source_width: float, source_height: float) -> QRectF:
    if source_width <= 0 or source_height <= 0:
        return target_rect
    scale = min(target_rect.width() / source_width, target_rect.height() / source_height)
    width = source_width * scale
    height = source_height * scale
    x = target_rect.x() + (target_rect.width() - width) / 2
    y = target_rect.y() + (target_rect.height() - height) / 2
    return QRectF(x, y, width, height)

def save_window_position(widget):
    try:
        config['window_x'] = int(widget.x())
        config['window_y'] = int(widget.y())
        save_config()
    except Exception as exc:
        pass

def get_saved_window_position():
    x = normalize_int(config.get('window_x', -1), -1, minimum=-1)
    y = normalize_int(config.get('window_y', -1), -1, minimum=-1)
    if x < 0 or y < 0:
        return None
    return (x, y)

def get_available_screen_geometries():
    screens = QApplication.screens() or []
    geometries = [screen.availableGeometry() for screen in screens if screen is not None]
    if not geometries:
        primary = QApplication.primaryScreen()
        if primary is not None:
            geometries.append(primary.availableGeometry())
    return geometries

def get_preferred_screen_geometry():
    try:
        cursor_pos = QCursor.pos()
        screen = QApplication.screenAt(cursor_pos)
        if screen is not None:
            return screen.availableGeometry()
    except Exception:
        pass
    primary = QApplication.primaryScreen()
    if primary is not None:
        return primary.availableGeometry()
    geometries = get_available_screen_geometries()
    if geometries:
        return geometries[0]
    return QRect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)

def is_window_position_valid(x: int, y: int, width: int=WINDOW_WIDTH, height: int=WINDOW_HEIGHT) -> bool:
    window_rect = QRect(int(x), int(y), int(width), int(height))
    for geometry in get_available_screen_geometries():
        if geometry.contains(window_rect):
            return True
    return False

def pick_best_screen_geometry_for_window(x: int, y: int, width: int=WINDOW_WIDTH, height: int=WINDOW_HEIGHT):
    geometries = get_available_screen_geometries()
    if not geometries:
        return get_preferred_screen_geometry()
    window_rect = QRect(int(x), int(y), int(width), int(height))
    window_center = window_rect.center()
    for geometry in geometries:
        if geometry.contains(window_rect):
            return geometry
    screen = QApplication.screenAt(window_center)
    if screen is not None:
        return screen.availableGeometry()

    def distance_to_geometry_center(geometry):
        center = geometry.center()
        dx = center.x() - window_center.x()
        dy = center.y() - window_center.y()
        return dx * dx + dy * dy
    return min(geometries, key=distance_to_geometry_center)

def clamp_window_position(x: int, y: int, width: int=WINDOW_WIDTH, height: int=WINDOW_HEIGHT):
    geometry = pick_best_screen_geometry_for_window(x, y, width, height)
    max_x = max(geometry.left(), geometry.right() - width + 1)
    max_y = max(geometry.top(), geometry.bottom() - height + 1)
    clamped_x = min(max(int(x), geometry.left()), max_x)
    clamped_y = min(max(int(y), geometry.top()), max_y)
    return (clamped_x, clamped_y)

def square_pixmap_from_pixmap(pixmap: QPixmap, size: int=256):
    if pixmap is None or pixmap.isNull():
        return None
    scaled = pixmap.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
    x = max(0, (scaled.width() - size) // 2)
    y = max(0, (scaled.height() - size) // 2)
    return scaled.copy(x, y, size, size)

def square_pixmap_from_file(path: Path, size: int=256):
    pixmap = QPixmap(str(path))
    if pixmap.isNull():
        return None
    return square_pixmap_from_pixmap(pixmap, size=size)
_last_default_placeholder_status = None

def cleanup_obsolete_avatar_files():
    return

def pixmap_to_data_uri(pixmap: QPixmap | None):
    try:
        if pixmap is None or pixmap.isNull():
            return None
        byte_array = QByteArray()
        buffer = QBuffer(byte_array)
        if not buffer.open(QIODevice.WriteOnly):
            return None
        saved = pixmap.save(buffer, 'PNG')
        buffer.close()
        if not saved:
            return None
        encoded = base64.b64encode(bytes(byte_array)).decode('ascii')
        return f'data:image/png;base64,{encoded}'
    except Exception as exc:
        return None

def delete_avatar_file(path: Path, log_name: str):
    try:
        if path.exists():
            path.unlink()
    except Exception as exc:
        pass

def ensure_default_profile_image(force_refresh: bool=True):
    global _last_default_placeholder_status
    try:
        FILES_DIR.mkdir(parents=True, exist_ok=True)
        usable = is_usable_image_file(DEFAULT_PLACEHOLDER_IMAGE_FILE)
        state = 'ready' if usable else 'missing'
        file_key = 'missing'
        if DEFAULT_PLACEHOLDER_IMAGE_FILE.exists():
            stat = DEFAULT_PLACEHOLDER_IMAGE_FILE.stat()
            file_key = f'{stat.st_size}:{stat.st_mtime_ns}'
        status_key = f'{state}:{file_key}'
        if force_refresh or _last_default_placeholder_status != status_key:
            _last_default_placeholder_status = status_key
        return usable
    except Exception as exc:
        return False

def get_avatar_mode() -> str:
    value = str(config.get('avatar_mode', AVATAR_MODE_WEBHOOK) or AVATAR_MODE_WEBHOOK).strip().lower()
    if value in {AVATAR_MODE_WEBHOOK, AVATAR_MODE_DEFAULT, AVATAR_MODE_MANUAL}:
        return value
    if value == 'custom':
        return AVATAR_MODE_MANUAL
    if value == 'auto':
        return AVATAR_MODE_WEBHOOK
    return AVATAR_MODE_WEBHOOK

def save_custom_profile_image(source_path: str):
    source = Path(source_path)
    cropped = square_pixmap_from_file(source, size=256)
    if cropped is None:
        return (False, 'Could not open the selected image.')
    AVATAR_IMAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not cropped.save(str(AVATAR_IMAGE_FILE), 'PNG'):
        return (False, 'Could not save the profile image.')
    cleanup_obsolete_avatar_files()
    config['avatar_mode'] = AVATAR_MODE_MANUAL
    reset_avatar_sync_cache()
    save_config()
    return (True, str(AVATAR_IMAGE_FILE))

def remove_custom_profile_image():
    delete_avatar_file(AVATAR_IMAGE_FILE, 'webhook_avatar_deleted')
    cleanup_obsolete_avatar_files()
    config['avatar_mode'] = AVATAR_MODE_DEFAULT
    reset_avatar_sync_cache()
    save_config()
    return True

def image_file_to_data_uri(path: Path):
    try:
        if not path.exists():
            return None
        pixmap = square_pixmap_from_file(path, size=256) or QPixmap(str(path))
        return pixmap_to_data_uri(pixmap)
    except Exception as exc:
        return None

def is_usable_image_file(path: Path | None) -> bool:
    try:
        if path is None or not Path(path).exists():
            return False
        pixmap = QPixmap(str(path))
        return not pixmap.isNull()
    except Exception:
        return False

def should_use_custom_avatar() -> bool:
    return get_avatar_mode() == AVATAR_MODE_MANUAL and is_usable_image_file(AVATAR_IMAGE_FILE)

def should_use_webhook_default_avatar() -> bool:
    return get_avatar_mode() == AVATAR_MODE_WEBHOOK and webhook_defaults_match_current() and is_usable_image_file(AVATAR_IMAGE_FILE)

def should_use_local_default_avatar() -> bool:
    return ensure_default_profile_image(force_refresh=False)

def get_effective_avatar_file() -> Path | None:
    if should_use_custom_avatar() or should_use_webhook_default_avatar():
        return AVATAR_IMAGE_FILE
    if should_use_local_default_avatar():
        return DEFAULT_PLACEHOLDER_IMAGE_FILE
    return None

def should_refresh_webhook_avatar_cache(webhook_url: str | None=None, force: bool=False) -> bool:
    webhook_url = (webhook_url or config.get('webhook', '') or '').strip()
    if not webhook_url:
        return False
    if get_avatar_mode() != AVATAR_MODE_WEBHOOK:
        return False
    if force:
        return True
    identity_key = current_webhook_identity_key(webhook_url)
    if config.get('webhook_default_source', '') != identity_key:
        return True
    return not is_usable_image_file(AVATAR_IMAGE_FILE)

def refresh_avatar_state(webhook_url: str | None=None, force_fetch: bool=False, sync_remote: bool=False):
    webhook_url = (webhook_url or config.get('webhook', '') or '').strip()
    ensure_default_profile_image(force_refresh=False)
    cleanup_obsolete_avatar_files()
    cache_updated = False
    if webhook_url and should_refresh_webhook_avatar_cache(webhook_url, force=force_fetch):
        cache_updated = capture_webhook_defaults(webhook_url)
    if sync_remote and webhook_url:
        return sync_webhook_avatar(force=True)
    return cache_updated if webhook_url else should_use_local_default_avatar()

def capture_webhook_defaults(webhook_url: str | None=None):
    webhook_url = (webhook_url or config.get('webhook', '') or '').strip()
    if not webhook_url:
        return False
    identity_key = current_webhook_identity_key(webhook_url)
    try:
        response = requests.get(webhook_url, timeout=12)
        if response.status_code != 200:
            delete_avatar_file(AVATAR_IMAGE_FILE, 'webhook_avatar_deleted')
            cleanup_obsolete_avatar_files()
            config['webhook_default_source'] = identity_key
            config['avatar_mode'] = AVATAR_MODE_DEFAULT
            save_config()
            return False
        data = response.json() if response.content else {}
        config['webhook_default_name'] = str(data.get('name') or '').strip()
        avatar_hash = data.get('avatar')
        AVATAR_IMAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
        avatar_saved = False
        if avatar_hash and data.get('id'):
            avatar_url = f"https://cdn.discordapp.com/avatars/{data.get('id')}/{avatar_hash}.png?size=256"
            avatar_response = requests.get(avatar_url, timeout=12)
            if avatar_response.status_code == 200 and avatar_response.content:
                pixmap = QPixmap()
                if pixmap.loadFromData(avatar_response.content):
                    squared = square_pixmap_from_pixmap(pixmap, size=256) or pixmap
                    avatar_saved = squared.save(str(AVATAR_IMAGE_FILE), 'PNG')
                if avatar_saved:
                    pass
                else:
                    delete_avatar_file(AVATAR_IMAGE_FILE, 'webhook_avatar_deleted')
            else:
                delete_avatar_file(AVATAR_IMAGE_FILE, 'webhook_avatar_deleted')
        else:
            delete_avatar_file(AVATAR_IMAGE_FILE, 'webhook_avatar_deleted')
        cleanup_obsolete_avatar_files()
        config['webhook_default_source'] = identity_key
        config['avatar_mode'] = AVATAR_MODE_WEBHOOK if avatar_saved else AVATAR_MODE_DEFAULT
        reset_avatar_sync_cache()
        save_config()
        return avatar_saved
    except Exception as exc:
        delete_avatar_file(AVATAR_IMAGE_FILE, 'webhook_avatar_deleted')
        cleanup_obsolete_avatar_files()
        config['webhook_default_source'] = identity_key
        config['avatar_mode'] = AVATAR_MODE_DEFAULT
        save_config()
        return False

def get_avatar_sync_key() -> str:
    webhook_key = current_webhook_identity_key()
    if not webhook_key:
        return ''
    avatar_mode = get_avatar_mode()
    avatar_file = get_effective_avatar_file()
    if avatar_file is not None and avatar_file.exists():
        source = f'{avatar_mode}:{avatar_file.name}:{avatar_file.stat().st_mtime_ns}'
    else:
        source = f'{avatar_mode}:none'
    return f'{webhook_key}|{source}'

def sync_webhook_avatar(force: bool=False):
    global _last_avatar_sync_key
    webhook_url = (config.get('webhook', '') or '').strip()
    if not webhook_url:
        return False
    if get_avatar_mode() == AVATAR_MODE_WEBHOOK and should_refresh_webhook_avatar_cache(webhook_url, force=False):
        capture_webhook_defaults(webhook_url)
    sync_key = get_avatar_sync_key()
    if sync_key and (not force) and (_last_avatar_sync_key == sync_key):
        return True
    avatar_file = get_effective_avatar_file()
    avatar_payload = image_file_to_data_uri(avatar_file) if avatar_file is not None else None
    source = avatar_file.name if avatar_file is not None else 'none'
    last_status_code = None
    try:
        for attempt in range(3):
            response = requests.patch(webhook_url, json={'avatar': avatar_payload}, timeout=15)
            last_status_code = response.status_code
            if response.status_code in (200, 204):
                _last_avatar_sync_key = sync_key
                time.sleep(0.35)
                return True
            if response.status_code != 429:
                break
            time.sleep(0.8)
        return False
    except Exception as exc:
        return False

def _thumbnail_sort_key(path: Path):
    return path.name

def ensure_thumbs_dir():
    THUMBS_DIR.mkdir(parents=True, exist_ok=True)

def iter_saved_thumbnail_files(limit: int | None=None):
    with thumb_lock:
        if not THUMBS_DIR.exists():
            return []
        files = [path for path in THUMBS_DIR.iterdir() if path.is_file() and path.suffix.lower() == '.png']
    files.sort(key=_thumbnail_sort_key, reverse=True)
    if limit is not None:
        return files[:limit]
    return files

def prune_thumbnail_log(limit: int=THUMB_LOG_LIMIT):
    files = iter_saved_thumbnail_files()
    for path in files[limit:]:
        try:
            path.unlink()
        except Exception as exc:
            pass

def clear_thumbnail_log():
    global thumbnail_generation_epoch
    with thumb_lock:
        thumbnail_generation_epoch += 1
        if THUMBS_DIR.exists():
            for path in THUMBS_DIR.iterdir():
                if path.is_file():
                    try:
                        path.unlink()
                    except Exception as exc:
                        pass

def make_thumbnail_storage_name(filename: str) -> str:
    stem = Path(filename).stem
    safe_stem = re.sub('[^A-Za-z0-9._-]+', '_', stem).strip('._') or 'file'
    safe_stem = safe_stem[:80]
    stamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f')[:-3]
    return f'{stamp}_{safe_stem}.png'

def create_empty_thumbnail_image(size: int=THUMB_TILE_SIZE):
    image = QImage(size, size, QImage.Format_ARGB32)
    image.fill(Qt.transparent)
    return image

def scaled_thumbnail_image(image: QImage, max_dimension: int=THUMB_CACHE_DIMENSION):
    if image.isNull():
        return None
    return image.scaled(max_dimension, max_dimension, Qt.KeepAspectRatio, Qt.SmoothTransformation)

def save_thumbnail_image_to_path(image: QImage, target: Path):
    ensure_thumbs_dir()
    with thumb_lock:
        saved = image.save(str(target), 'PNG')
    if saved:
        prune_thumbnail_log()
    return saved

def load_image_for_thumbnail(source_path: Path):
    reader = QImageReader(str(source_path))
    reader.setAutoTransform(True)
    image = reader.read()
    if image.isNull():
        return None
    return image

def get_local_ffmpeg_path():
    if LOCAL_FFMPEG_PATH.exists():
        return str(LOCAL_FFMPEG_PATH)
    return None

def extract_video_frame_with_ffmpeg(source_path: Path):
    ffmpeg_path = get_local_ffmpeg_path()
    if not ffmpeg_path:
        return None
    startupinfo = None
    creationflags = 0
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        creationflags = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
    commands = [[ffmpeg_path, '-hide_banner', '-loglevel', 'error', '-ss', '0.50', '-i', str(source_path), '-frames:v', '1', '-f', 'image2pipe', '-vcodec', 'png', '-'], [ffmpeg_path, '-hide_banner', '-loglevel', 'error', '-ss', '0.00', '-i', str(source_path), '-frames:v', '1', '-f', 'image2pipe', '-vcodec', 'png', '-']]
    for cmd in commands:
        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20, startupinfo=startupinfo, creationflags=creationflags)
            if result.returncode == 0 and result.stdout:
                image = QImage.fromData(result.stdout)
                if not image.isNull():
                    return image
        except Exception as exc:
            break
    return None

def extract_shell_thumbnail_image(source_path: Path, requested_size: int=256):
    if os.name != 'nt' or ctypes is None or wintypes is None:
        return None
    try:

        class GUID(ctypes.Structure):
            _fields_ = [('Data1', wintypes.DWORD), ('Data2', wintypes.WORD), ('Data3', wintypes.WORD), ('Data4', ctypes.c_ubyte * 8)]

            def __init__(self, value: str):
                super().__init__()
                import uuid
                parsed = uuid.UUID(value)
                self.Data1, self.Data2, self.Data3, rest = (parsed.fields[0], parsed.fields[1], parsed.fields[2], parsed.bytes[8:])
                self.Data4[:] = rest

        class SIZE(ctypes.Structure):
            _fields_ = [('cx', ctypes.c_long), ('cy', ctypes.c_long)]

        class BITMAP(ctypes.Structure):
            _fields_ = [('bmType', ctypes.c_long), ('bmWidth', ctypes.c_long), ('bmHeight', ctypes.c_long), ('bmWidthBytes', ctypes.c_long), ('bmPlanes', ctypes.c_ushort), ('bmBitsPixel', ctypes.c_ushort), ('bmBits', ctypes.c_void_p)]

        class BITMAPINFOHEADER(ctypes.Structure):
            _fields_ = [('biSize', wintypes.DWORD), ('biWidth', ctypes.c_long), ('biHeight', ctypes.c_long), ('biPlanes', wintypes.WORD), ('biBitCount', wintypes.WORD), ('biCompression', wintypes.DWORD), ('biSizeImage', wintypes.DWORD), ('biXPelsPerMeter', ctypes.c_long), ('biYPelsPerMeter', ctypes.c_long), ('biClrUsed', wintypes.DWORD), ('biClrImportant', wintypes.DWORD)]

        class RGBQUAD(ctypes.Structure):
            _fields_ = [('rgbBlue', ctypes.c_ubyte), ('rgbGreen', ctypes.c_ubyte), ('rgbRed', ctypes.c_ubyte), ('rgbReserved', ctypes.c_ubyte)]

        class BITMAPINFO(ctypes.Structure):
            _fields_ = [('bmiHeader', BITMAPINFOHEADER), ('bmiColors', RGBQUAD * 1)]
        shell32 = ctypes.windll.shell32
        ole32 = ctypes.windll.ole32
        gdi32 = ctypes.windll.gdi32
        user32 = ctypes.windll.user32
        ole32.CoInitialize(None)
        try:
            iid = GUID('bcc18b79-ba16-442f-80c4-8a59c30c463b')
            factory_ptr = ctypes.c_void_p()
            shell32.SHCreateItemFromParsingName.argtypes = [wintypes.LPCWSTR, ctypes.c_void_p, ctypes.POINTER(GUID), ctypes.POINTER(ctypes.c_void_p)]
            shell32.SHCreateItemFromParsingName.restype = ctypes.c_long
            hr = shell32.SHCreateItemFromParsingName(str(source_path), None, ctypes.byref(iid), ctypes.byref(factory_ptr))
            if hr != 0 or not factory_ptr.value:
                return None
            vtable = ctypes.cast(factory_ptr, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
            release = ctypes.WINFUNCTYPE(ctypes.c_ulong, ctypes.c_void_p)(vtable[2])
            get_image = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, SIZE, ctypes.c_int, ctypes.POINTER(wintypes.HBITMAP))(vtable[3])
            SIIGBF_BIGGERSIZEOK = 1
            SIIGBF_THUMBNAILONLY = 8
            flags = SIIGBF_BIGGERSIZEOK | SIIGBF_THUMBNAILONLY
            hbitmap = wintypes.HBITMAP()
            hr = get_image(factory_ptr, SIZE(requested_size, requested_size), flags, ctypes.byref(hbitmap))
            release(factory_ptr)
            if hr != 0 or not hbitmap.value:
                return None
            bmp = BITMAP()
            if not gdi32.GetObjectW(hbitmap, ctypes.sizeof(BITMAP), ctypes.byref(bmp)):
                gdi32.DeleteObject(hbitmap)
                return None
            width = int(bmp.bmWidth)
            height = int(bmp.bmHeight)
            if width <= 0 or height <= 0:
                gdi32.DeleteObject(hbitmap)
                return None
            bmi = BITMAPINFO()
            bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
            bmi.bmiHeader.biWidth = width
            bmi.bmiHeader.biHeight = -height
            bmi.bmiHeader.biPlanes = 1
            bmi.bmiHeader.biBitCount = 32
            bmi.bmiHeader.biCompression = 0
            buffer = ctypes.create_string_buffer(width * height * 4)
            hdc = user32.GetDC(None)
            try:
                result = gdi32.GetDIBits(hdc, hbitmap, 0, height, buffer, ctypes.byref(bmi), 0)
            finally:
                user32.ReleaseDC(None, hdc)
                gdi32.DeleteObject(hbitmap)
            if result == 0:
                return None
            image = QImage(buffer.raw, width, height, width * 4, QImage.Format_ARGB32)
            copied = image.copy()
            if copied.isNull():
                return None
            return copied
        finally:
            ole32.CoUninitialize()
    except Exception as exc:
        return None

def extract_source_thumbnail_image(source_path: Path):
    suffix = source_path.suffix.lower()
    image = None
    if suffix in IMAGE_EXTENSIONS:
        image = load_image_for_thumbnail(source_path)
        if image is not None and (not image.isNull()):
            return image
    if suffix in VIDEO_EXTENSIONS:
        image = extract_video_frame_with_ffmpeg(source_path)
        if image is not None and (not image.isNull()):
            return image
        image = extract_shell_thumbnail_image(source_path, requested_size=256)
        if image is not None and (not image.isNull()):
            return image
    image = extract_shell_thumbnail_image(source_path, requested_size=256)
    if image is not None and (not image.isNull()):
        return image
    return None

def is_supported_media_file(file_path) -> bool:
    try:
        return Path(file_path).suffix.lower() in SUPPORTED_MEDIA_EXTENSIONS
    except Exception:
        return False

def get_thumbnail_generation_epoch():
    with thumb_lock:
        return thumbnail_generation_epoch

def reserve_sent_thumbnail(original_filename: str):
    target = THUMBS_DIR / make_thumbnail_storage_name(original_filename)
    placeholder = create_empty_thumbnail_image()
    if not save_thumbnail_image_to_path(placeholder, target):
        return None
    return target

def create_sent_thumbnail(target_path: Path, source_path: str):
    path = Path(source_path)
    target = Path(target_path)
    if not path.exists():
        return False
    try:
        image = extract_source_thumbnail_image(path)
        if image is None or image.isNull():
            return False
        thumb_image = scaled_thumbnail_image(image, THUMB_CACHE_DIMENSION)
        if thumb_image is None or thumb_image.isNull():
            return False
        saved = save_thumbnail_image_to_path(thumb_image, target)
        if not saved:
            return False
        return True
    except Exception as exc:
        return False

def delete_sent_source_file(path: str):
    source = Path(path)
    if not source.exists():
        return
    try:
        send2trash(os.path.abspath(str(source)))
    except Exception as exc:
        pass

def queue_thumbnail_generation(source_path: str, target_path: Path, delete_after_send: bool):
    task = {'source_path': str(source_path), 'target_path': str(target_path), 'delete_after_send': bool(delete_after_send), 'epoch': get_thumbnail_generation_epoch()}
    thumbnail_task_queue.put(task)

def remove_reserved_thumbnail(target_path: Path):
    target = Path(target_path)
    try:
        if target.exists():
            target.unlink()
    except Exception as exc:
        pass

def thumbnail_worker_loop():
    while not stop_event.is_set():
        try:
            task = thumbnail_task_queue.get(timeout=0.4)
        except queue.Empty:
            continue
        try:
            if task is None:
                break
            source_path = task.get('source_path', '')
            target_path = Path(task.get('target_path', ''))
            task_epoch = int(task.get('epoch', -1))
            current_epoch = get_thumbnail_generation_epoch()
            generated = False
            if target_path and task_epoch == current_epoch:
                generated = create_sent_thumbnail(target_path, source_path)
                if not generated:
                    remove_reserved_thumbnail(target_path)
            if task.get('delete_after_send', False):
                delete_sent_source_file(source_path)
            if target_path and task_epoch == current_epoch:
                signals.thumbnail_changed.emit(str(target_path), False)
        except Exception as exc:
            pass
        finally:
            try:
                thumbnail_task_queue.task_done()
            except Exception:
                pass

def get_startup_command() -> str:
    script_path = Path(sys.argv[0]).resolve()
    if getattr(sys, 'frozen', False):
        return f'"{Path(sys.executable).resolve()}"'
    exe = Path(sys.executable).resolve()
    if exe.name.lower() == 'python.exe':
        alt = exe.with_name('pythonw.exe')
        if alt.exists():
            exe = alt
    return f'"{exe}" "{script_path}"'

def set_start_with_windows(enabled: bool):
    if winreg is None:
        raise RuntimeError('Windows registry is unavailable.')
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_REG_PATH, 0, winreg.KEY_SET_VALUE) as key:
        if enabled:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, get_startup_command())
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
            except FileNotFoundError:
                pass

def get_file_hash(path):
    h = hashlib.sha256()
    try:
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None

def file_is_free(path):
    try:
        with open(path, 'rb+'):
            return True
    except Exception:
        return False

def is_valid_webhook(text: str) -> bool:
    text = (text or '').strip()
    if not text:
        return False
    lowered = text.lower()
    return lowered.startswith('https://discord.com/api/webhooks/') or lowered.startswith('https://discordapp.com/api/webhooks/')

def clip_embed_description(text: str) -> str:
    return text if len(text) <= 4096 else text[:4093] + '...'

def is_embed_image_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in {'.png', '.jpg', '.jpeg', '.gif', '.webp'}

def build_message_payload(message: str, use_embed: bool, embed_color: str, filename: str | None=None, username: str | None=None):
    username = (username or '').strip()
    if use_embed:
        embed = {'description': clip_embed_description(message), 'color': discord_color_int(embed_color)}
        if filename and is_embed_image_file(filename):
            embed['image'] = {'url': f'attachment://{filename}'}
        payload = {'embeds': [embed]}
        if username:
            payload['username'] = username
        return {'payload_json': json.dumps(payload, ensure_ascii=False)}
    payload = {'content': message}
    if username:
        payload['username'] = username
    return payload

def build_test_message(template_text: str | None=None) -> str:
    now_dt = datetime.datetime.now()
    now_str = f"{DAYS_OF_WEEK[now_dt.weekday()]}, {now_dt.strftime('%d/%m/%y %H:%M:%S')}"
    template_source = load_template() if template_text is None else template_text
    template = normalize_multiline_text(template_source, default_template_text())
    return render_template_text(template, 'example.png', now_str, now_str)

def send_test_message(template_text: str | None=None, use_embed: bool | None=None, webhook_name: str | None=None):
    webhook = (config.get('webhook') or '').strip()
    if not webhook:
        return (False, 'Enter a webhook before testing.')
    sync_webhook_avatar()
    message = build_test_message(template_text)
    use_embed = bool(config.get('use_embed', False)) if use_embed is None else bool(use_embed)
    embed_color = normalize_hex_color(config.get('embed_color', DEFAULT_EMBED_COLOR))
    display_name = get_effective_webhook_name(webhook_name)
    payload = build_message_payload(message, use_embed, embed_color, username=display_name or None)
    try:
        res = requests.post(webhook, data=payload, timeout=12)
        if res.status_code in (200, 204):
            return (True, 'Test sent successfully.')
        if res.status_code == 404:
            return (False, 'Webhook not found.')
        if res.status_code == 401:
            return (False, 'Webhook unauthorized.')
        return (False, f'Test failed ({res.status_code}).')
    except Exception as exc:
        return (False, 'Could not test the webhook.')

def is_sent_history_duplicate(filename: str, file_hash: str) -> bool:
    filename = (filename or '').strip()
    file_hash = (file_hash or '').strip()
    if not filename or not file_hash:
        return False
    for item in sent_history:
        if not isinstance(item, dict):
            continue
        logged_filename = str(item.get('file', '')).strip()
        logged_hash = str(item.get('hash', '')).strip()
        if logged_filename == filename and logged_hash == file_hash:
            return True
    return False

def finalize_sent_file(path, filename, file_hash, upload_str):
    reserved_thumbnail_path = reserve_sent_thumbnail(filename)
    with file_lock:
        sent_history.append({'file': filename, 'hash': file_hash, 'date': upload_str})
    save_json(LOG_FILE, sent_history)
    delete_after_send = bool(config.get('delete_after_send', True))
    thumbnail_saved = reserved_thumbnail_path is not None
    if reserved_thumbnail_path is not None:
        signals.thumbnail_changed.emit(str(reserved_thumbnail_path), True)
        queue_thumbnail_generation(path, reserved_thumbnail_path, delete_after_send=delete_after_send)
    elif delete_after_send:
        delete_sent_source_file(path)

def send_file(path):
    webhook = (config.get('webhook') or '').strip()
    if not webhook:
        return False
    filename = os.path.basename(path)
    watched_folder = config.get('folder', '')
    error_dir = Path(watched_folder) / 'fail' if watched_folder else None
    try:
        size_mb = os.path.getsize(path) / (1024 * 1024)
        if size_mb > 25:
            if error_dir is not None:
                error_dir.mkdir(exist_ok=True)
                shutil.move(path, error_dir / filename)
            return False
    except Exception as exc:
        return False
    file_hash = get_file_hash(path)
    if not file_hash:
        return False
    with file_lock:
        if is_sent_history_duplicate(filename, file_hash):
            return False
    if not file_is_free(path):
        return False
    try:
        now_dt = datetime.datetime.now()
        creation_str = format_file_creation_string(path)
        upload_str = f"{DAYS_OF_WEEK[now_dt.weekday()]}, {now_dt.strftime('%d/%m/%y %H:%M:%S')}"
        sync_webhook_avatar()
        template = load_template()
        message = render_template_text(template, filename, creation_str, upload_str)
        use_embed = bool(config.get('use_embed', False))
        embed_color = normalize_hex_color(config.get('embed_color', DEFAULT_EMBED_COLOR))
        display_name = get_effective_webhook_name()
        for attempt in range(4):
            try:
                with open(path, 'rb') as f:
                    sending_event.set()
                    try:
                        payload = build_message_payload(message, use_embed, embed_color, filename=filename, username=display_name or None)
                        res = requests.post(webhook, data=payload, files={'file': (filename, f)}, timeout=15)
                    finally:
                        sending_event.clear()
                if res.status_code in [200, 204]:
                    finalize_sent_file(path, filename, file_hash, upload_str)
                    return True
                if res.status_code == 429:
                    time.sleep(2 ** attempt)
                    continue
                break
            except Exception as exc:
                sending_event.clear()
                time.sleep(2 ** attempt)
        return False
    except Exception as exc:
        return False

def send_now_manual():
    if not config.get('folder'):
        signals.toast.emit('error', 'Select a folder first.')
        return
    folder = config.get('folder', '')
    if not os.path.isdir(folder):
        signals.toast.emit('error', 'The watched folder does not exist.')
        return
    if not send_lock.acquire(blocking=False):
        signals.toast.emit('warning', 'A send operation is already in progress.')
        return
    try:
        files = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)) and is_supported_media_file(f)]
        sent_any = False
        for file in sorted(files, key=get_file_creation_timestamp):
            if stop_event.is_set():
                break
            if send_file(file):
                sent_any = True
                signals.toast.emit('success', f'Sent: {os.path.basename(file)}')
                for _ in range(get_post_interval_seconds()):
                    if stop_event.is_set():
                        break
                    time.sleep(1)
        if not sent_any:
            signals.toast.emit('info', 'No file is available to send right now.')
    except Exception as exc:
        traceback.print_exc()
        signals.toast.emit('error', 'Send now failed.')
    finally:
        send_lock.release()
        signals.refresh_fields.emit()

def monitoring_loop():
    global monitoring
    while not stop_event.is_set():
        if monitoring and config.get('folder') and config.get('webhook'):
            folder = config.get('folder', '')
            if os.path.isdir(folder) and send_lock.acquire(blocking=False):
                try:
                    now = time.time()
                    files = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)) and is_supported_media_file(f)]
                    ready = [p for p in files if now - get_file_creation_timestamp(p) >= get_wait_time_seconds()]
                    if files or ready:
                        pass
                    for file in sorted(ready, key=get_file_creation_timestamp):
                        if stop_event.is_set() or not monitoring:
                            break
                        if send_file(file):
                            signals.toast.emit('success', f'Sent automatically: {os.path.basename(file)}')
                            for _ in range(get_post_interval_seconds()):
                                if stop_event.is_set() or not monitoring:
                                    break
                                time.sleep(1)
                except Exception as exc:
                    traceback.print_exc()
                finally:
                    send_lock.release()
        for _ in range(MONITOR_CHECK_INTERVAL):
            if stop_event.is_set():
                break
            time.sleep(1)

class HoverButton(QPushButton):

    def __init__(self, text, size=36, tooltip='', bg='transparent', hover=HOVER_DARK, fg=TEXT, font_size=15):
        super().__init__(text)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(tooltip)
        self._bg = bg
        self._hover = hover
        self._fg = fg
        self._size = size
        self.setFixedSize(size, size)
        self.setFont(QFont('Segoe UI Symbol', font_size))
        self.apply_style(False)

    def apply_style(self, hovered):
        bg = self._hover if hovered else self._bg
        self.setStyleSheet(f'\n            QPushButton {{\n                background: {bg};\n                color: {self._fg};\n                border: none;\n                border-radius: {self._size // 2}px;\n            }}\n            ')

    def enterEvent(self, event):
        self.apply_style(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.apply_style(False)
        super().leaveEvent(event)

class ToggleSwitch(QPushButton):
    toggled_visual = Signal(bool)

    def __init__(self, checked=False):
        super().__init__()
        self.setCheckable(True)
        self.setChecked(checked)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(52, 28)
        self.clicked.connect(lambda: self.toggled_visual.emit(self.isChecked()))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(1, 1, -1, -1)
        radius = rect.height() / 2
        bg = QColor(BLUE if self.isChecked() else '#363943')
        painter.setPen(Qt.NoPen)
        painter.setBrush(bg)
        painter.drawRoundedRect(rect, radius, radius)
        knob_size = rect.height() - 6
        x = rect.right() - knob_size - 3 if self.isChecked() else rect.left() + 3
        knob_rect = (x, rect.top() + 3, knob_size, knob_size)
        painter.setBrush(QColor('#ffffff'))
        painter.drawEllipse(*knob_rect)
        painter.end()

class ColorSwatchButton(QPushButton):

    def __init__(self, hex_color=DEFAULT_EMBED_COLOR):
        super().__init__()
        self._hovered = False
        self._color = normalize_hex_color(hex_color)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip('Embed color')
        self.setFixedSize(30, 30)
        self.apply_style()

    def set_color(self, hex_color):
        self._color = normalize_hex_color(hex_color)
        self.apply_style()

    def apply_style(self):
        border = '#ffffff' if self._hovered else '#2f343d'
        self.setStyleSheet(f'\n            QPushButton {{\n                background: {self._color};\n                border: 2px solid {border};\n                border-radius: 15px;\n            }}\n            ')

    def enterEvent(self, event):
        self._hovered = True
        self.apply_style()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self.apply_style()
        super().leaveEvent(event)

class AvatarPreview(QWidget):
    clicked = Signal()

    def __init__(self, size=44, parent=None):
        super().__init__(parent)
        self._size = size
        self._pixmap = None
        self._hovered = False
        self.setFixedSize(size, size)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip('Choose custom webhook image')

    def set_image_path(self, image_path: str | None):
        pixmap = QPixmap(str(image_path)) if image_path else QPixmap()
        self._pixmap = pixmap if not pixmap.isNull() else None
        self.update()

    def enterEvent(self, event):
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(1, 1, -1, -1)
        path = QPainterPath()
        path.addEllipse(rect)
        painter.fillPath(path, QColor(BLUE))
        painter.setClipPath(path)
        if self._pixmap is not None and (not self._pixmap.isNull()):
            scaled = self._pixmap.scaled(rect.width(), rect.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            x = rect.x() + (rect.width() - scaled.width()) // 2
            y = rect.y() + (rect.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
        painter.setClipping(False)
        border_color = QColor(BLUE if self._hovered else '#2f343d')
        painter.setPen(QPen(border_color, 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(rect)
        painter.end()

class ColorSpectrumBox(QWidget):
    colorChanged = Signal(float, float)

    def __init__(self, hue=0.0, sat=1.0, val=1.0, parent=None):
        super().__init__(parent)
        self._hue = max(0.0, min(1.0, hue))
        self._sat = max(0.0, min(1.0, sat))
        self._val = max(0.0, min(1.0, val))
        self.setMinimumSize(250, 180)
        self.setCursor(Qt.CrossCursor)

    def set_hsv(self, hue, sat, val):
        self._hue = max(0.0, min(1.0, hue))
        self._sat = max(0.0, min(1.0, sat))
        self._val = max(0.0, min(1.0, val))
        self.update()

    def set_hue(self, hue):
        self._hue = max(0.0, min(1.0, hue))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(1, 1, -1, -1)
        path = QPainterPath()
        path.addRoundedRect(rect, 16, 16)
        painter.setClipPath(path)
        hue_color = QColor.fromHsvF(self._hue, 1.0, 1.0)
        painter.fillRect(rect, hue_color)
        white_grad = QLinearGradient(rect.topLeft(), rect.topRight())
        white_grad.setColorAt(0.0, QColor(255, 255, 255, 255))
        white_grad.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.fillRect(rect, white_grad)
        black_grad = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        black_grad.setColorAt(0.0, QColor(0, 0, 0, 0))
        black_grad.setColorAt(1.0, QColor(0, 0, 0, 255))
        painter.fillRect(rect, black_grad)
        painter.setClipping(False)
        pen = QPen(QColor('#2f343d'))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)
        px = rect.left() + self._sat * rect.width()
        py = rect.top() + (1.0 - self._val) * rect.height()
        painter.setPen(QPen(QColor('#ffffff'), 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(int(px) - 6, int(py) - 6, 12, 12)
        painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._update_from_pos(event.position())
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self._update_from_pos(event.position())
        super().mouseMoveEvent(event)

    def _update_from_pos(self, pos):
        rect = self.rect().adjusted(1, 1, -1, -1)
        if rect.width() <= 0 or rect.height() <= 0:
            return
        x = max(rect.left(), min(rect.right(), pos.x()))
        y = max(rect.top(), min(rect.bottom(), pos.y()))
        self._sat = (x - rect.left()) / max(1, rect.width())
        self._val = 1.0 - (y - rect.top()) / max(1, rect.height())
        self.update()
        self.colorChanged.emit(self._sat, self._val)

class HueSlider(QWidget):
    hueChanged = Signal(float)

    def __init__(self, hue=0.0, parent=None):
        super().__init__(parent)
        self._hue = max(0.0, min(1.0, hue))
        self.setFixedHeight(18)
        self.setCursor(Qt.PointingHandCursor)

    def set_hue(self, hue):
        self._hue = max(0.0, min(1.0, hue))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(1, 1, -1, -1)
        path = QPainterPath()
        path.addRoundedRect(rect, 9, 9)
        grad = QLinearGradient(rect.topLeft(), rect.topRight())
        stops = [(0.0, '#ff0000'), (1 / 6, '#ffff00'), (2 / 6, '#00ff00'), (3 / 6, '#00ffff'), (4 / 6, '#0000ff'), (5 / 6, '#ff00ff'), (1.0, '#ff0000')]
        for pos, color in stops:
            grad.setColorAt(pos, QColor(color))
        painter.fillPath(path, grad)
        painter.setPen(QPen(QColor('#2f343d'), 1))
        painter.drawPath(path)
        x = rect.left() + self._hue * rect.width()
        painter.setPen(QPen(QColor('#ffffff'), 2))
        painter.setBrush(QColor(15, 16, 18))
        painter.drawEllipse(int(x) - 6, rect.center().y() - 6, 12, 12)
        painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._update_from_pos(event.position().x())
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self._update_from_pos(event.position().x())
        super().mouseMoveEvent(event)

    def _update_from_pos(self, x):
        rect = self.rect().adjusted(1, 1, -1, -1)
        if rect.width() <= 0:
            return
        x = max(rect.left(), min(rect.right(), x))
        self._hue = (x - rect.left()) / max(1, rect.width())
        self.update()
        self.hueChanged.emit(self._hue)

class EmbedColorPopup(QWidget):
    colorChanged = Signal(str)
    colorSaved = Signal(str)

    def __init__(self, initial_hex=DEFAULT_EMBED_COLOR, parent=None):
        super().__init__(parent)
        self._closing = False
        self._syncing_hex = False
        self.selected_hex = normalize_hex_color(initial_hex)
        self._hue, self._sat, self._val = self.hex_to_hsv(self.selected_hex)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        panel = QFrame()
        panel.setObjectName('embedColorPopup')
        panel.setStyleSheet(f"\n            QFrame#embedColorPopup {{\n                background: {PANEL};\n                border: 1px solid #23262d;\n                border-radius: 18px;\n            }}\n            QLabel {{\n                color: {TEXT};\n                font: 700 9px 'Segoe UI';\n                background: transparent;\n                border: none;\n            }}\n            QLineEdit {{\n                background: {FIELD_BG};\n                color: {FIELD_TEXT};\n                border: 1px solid #2c3038;\n                border-radius: 12px;\n                padding: 0 12px;\n                min-height: 32px;\n                font: 700 9px 'Segoe UI';\n            }}\n            QLineEdit:focus {{\n                border: 1px solid {BLUE};\n            }}\n            QLineEdit::placeholder {{\n                color: #6f7580;\n            }}\n            ")
        outer.addWidget(panel)
        root = QVBoxLayout(panel)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)
        self.spectrum = ColorSpectrumBox(self._hue, self._sat, self._val)
        self.spectrum.setMinimumSize(238, 156)
        self.spectrum.colorChanged.connect(self.on_sv_changed)
        root.addWidget(self.spectrum)
        self.hue_slider = HueSlider(self._hue)
        self.hue_slider.hueChanged.connect(self.on_hue_changed)
        root.addWidget(self.hue_slider)
        bottom = QHBoxLayout()
        bottom.setContentsMargins(0, 0, 0, 0)
        bottom.setSpacing(10)
        self.preview = QLabel()
        self.preview.setFixedSize(28, 28)
        bottom.addWidget(self.preview, 0, Qt.AlignVCenter)
        hex_col = QVBoxLayout()
        hex_col.setContentsMargins(0, 0, 0, 0)
        hex_col.setSpacing(4)
        self.hex_label = QLabel('Hex')
        self.hex_label.setStyleSheet(f"color:{TEXT}; font: 700 9px 'Segoe UI';")
        hex_col.addWidget(self.hex_label)
        self.hex_input = QLineEdit(self.selected_hex)
        self.hex_input.setPlaceholderText(BLUE)
        self.hex_input.setMaxLength(7)
        self.hex_input.textChanged.connect(self.on_hex_text_changed)
        self.hex_input.editingFinished.connect(self.on_hex_editing_finished)
        hex_col.addWidget(self.hex_input)
        bottom.addLayout(hex_col, 1)
        root.addLayout(bottom)
        self.update_preview(self.selected_hex)

    @staticmethod
    def hex_to_hsv(hex_color):
        color = QColor(normalize_hex_color(hex_color))
        r, g, b, _ = color.getRgbF()
        return colorsys.rgb_to_hsv(r, g, b)

    def show_anchored(self, anchor_widget, boundary_widget=None):
        self.adjustSize()
        anchor_global = anchor_widget.mapToGlobal(anchor_widget.rect().topLeft())
        anchor_rect = QRect(anchor_global, anchor_widget.size())
        screen = anchor_widget.screen() or QApplication.primaryScreen()
        area = screen.availableGeometry() if screen else QApplication.primaryScreen().availableGeometry()
        margin = 8
        candidates = [(anchor_rect.left() - self.width() + anchor_rect.width(), anchor_rect.top() - self.height() - margin), (anchor_rect.left() - self.width() + anchor_rect.width(), anchor_rect.bottom() + margin), (anchor_rect.right() + margin, anchor_rect.top()), (anchor_rect.left() - self.width() - margin, anchor_rect.top())]

        def clamp(x, y):
            x = max(area.left() + 6, min(x, area.right() - self.width() - 6))
            y = max(area.top() + 6, min(y, area.bottom() - self.height() - 6))
            return (x, y)
        x, y = candidates[0]
        for cx, cy in candidates:
            if area.left() <= cx <= area.right() - self.width() and area.top() <= cy <= area.bottom() - self.height():
                x, y = (cx, cy)
                break
        x, y = clamp(x, y)
        if boundary_widget and boundary_widget.isVisible():
            parent_global = boundary_widget.mapToGlobal(boundary_widget.rect().topLeft())
            parent_rect = QRect(parent_global, boundary_widget.size())
            x = max(parent_rect.left() + 8, min(x, parent_rect.right() - self.width() - 8))
            y = max(parent_rect.top() + 8, min(y, parent_rect.bottom() - self.height() - 8))
        self.move(int(x), int(y))
        self.show()
        self.raise_()
        self.activateWindow()

    def update_preview(self, hex_color):
        self.preview.setStyleSheet(f'background:{hex_color}; border:2px solid #2f343d; border-radius:14px;')

    def set_selected_hex(self, hex_color, sync_hsv=True, sync_hex=True, emit_live=True):
        normalized = normalize_hex_color(hex_color)
        self.selected_hex = normalized
        if sync_hsv:
            self._hue, self._sat, self._val = self.hex_to_hsv(normalized)
            self.hue_slider.set_hue(self._hue)
            self.spectrum.set_hsv(self._hue, self._sat, self._val)
        self.update_preview(normalized)
        if sync_hex:
            self._syncing_hex = True
            self.hex_input.setText(normalized)
            self._syncing_hex = False
        if emit_live:
            self.colorChanged.emit(normalized)

    def on_sv_changed(self, sat, val):
        self._sat = sat
        self._val = val
        color = QColor.fromHsvF(self._hue, self._sat, self._val)
        self.set_selected_hex(color.name().upper(), sync_hsv=False, sync_hex=True, emit_live=True)

    def on_hue_changed(self, hue):
        self._hue = hue
        self.spectrum.set_hue(hue)
        color = QColor.fromHsvF(self._hue, self._sat, self._val)
        self.set_selected_hex(color.name().upper(), sync_hsv=False, sync_hex=True, emit_live=True)

    def on_hex_text_changed(self, text):
        if self._syncing_hex:
            return
        parsed = parse_hex_color(text)
        if not parsed:
            return
        self.set_selected_hex(parsed, sync_hsv=True, sync_hex=False, emit_live=True)

    def on_hex_editing_finished(self):
        parsed = parse_hex_color(self.hex_input.text())
        self._syncing_hex = True
        self.hex_input.setText(parsed or self.selected_hex)
        self._syncing_hex = False

    def commit_and_close(self):
        if self._closing:
            return
        self._closing = True
        self.colorSaved.emit(self.selected_hex)
        self.hide()

    def hideEvent(self, event):
        if not self._closing:
            self._closing = True
            self.colorSaved.emit(self.selected_hex)
        super().hideEvent(event)

    def showEvent(self, event):
        self._closing = False
        super().showEvent(event)

class RoundedPanel(QWidget):

    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet('background: transparent;')

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(1, 1, -1, -1)
        path = QPainterPath()
        path.addRoundedRect(rect, 22, 22)
        painter.fillPath(path, QColor(PANEL))
        pen = QPen(QColor('#1c1d21'))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawPath(path)
        painter.end()
        super().paintEvent(event)

class PageBase(QWidget):

    def __init__(self, title, subtitle):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(10)
        top = QVBoxLayout()
        top.setSpacing(1)
        self.title = QLabel(title)
        self.title.setStyleSheet(f"color:{BLUE}; font: 700 12px 'Segoe UI';")
        top.addWidget(self.title)
        self.subtitle = QLabel(subtitle)
        self.subtitle.setWordWrap(True)
        self.subtitle.setStyleSheet(f"color:{MUTED}; font: 500 9px 'Segoe UI';")
        top.addWidget(self.subtitle)
        root.addLayout(top)
        self.body = QVBoxLayout()
        self.body.setSpacing(10)
        root.addLayout(self.body, 1)

    def minimumSizeHint(self):
        return QSize(0, 0)

class HomeValueRow(QFrame):

    def __init__(self, window, title, button_text, handler):
        super().__init__()
        self.setStyleSheet(f'\n            QFrame {{\n                background: {CARD};\n                border: 1px solid {CARD_BORDER};\n                border-radius: 16px;\n            }}\n            QLabel {{\n                background: transparent;\n                border: none;\n            }}\n            ')
        root = QHBoxLayout(self)
        root.setContentsMargins(14, 10, 10, 10)
        root.setSpacing(10)
        left = QVBoxLayout()
        left.setSpacing(2)
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(f"color:{TEXT}; font: 700 10px 'Segoe UI';")
        left.addWidget(self.title_label)
        self.value_label = QLabel('')
        self.value_label.setWordWrap(False)
        self.value_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.value_label.setStyleSheet(f"color:{FIELD_TEXT}; font: 500 9px 'Segoe UI'; background: transparent; border: none;")
        self.value_label.setMinimumHeight(18)
        left.addWidget(self.value_label)
        root.addLayout(left, 1)
        self.button = window.make_small_button(button_text, handler)
        self.button.setFixedSize(78, 28)
        root.addWidget(self.button, 0, Qt.AlignVCenter)

    def set_value(self, text, placeholder):
        value = (text or '').strip()
        self.value_label.setText(value if value else placeholder)
        self.value_label.setStyleSheet(f"color:{(FIELD_TEXT if value else '#6f7580')}; font: 500 9px 'Segoe UI'; background: transparent; border: none;")

class ThumbnailTile(QLabel):

    def __init__(self, size: int=THUMB_TILE_SIZE, parent=None):
        super().__init__(parent)
        self._size = size
        self.thumb_path = ''
        self._pixmap = QPixmap()
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(f'background:{CARD}; border:1px solid {CARD_BORDER}; border-radius:12px;')
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.opacity_effect.setOpacity(1.0)
        self.setGraphicsEffect(self.opacity_effect)

    def set_opacity(self, value: float):
        self.opacity_effect.setOpacity(value)

    def set_thumbnail(self, thumb_path: Path | str):
        self.thumb_path = str(thumb_path) if thumb_path else ''
        pixmap = QPixmap(self.thumb_path) if self.thumb_path else QPixmap()
        self._pixmap = pixmap
        self.update()

    def clear_thumbnail(self):
        self.thumb_path = ''
        self._pixmap = QPixmap()
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self._pixmap.isNull():
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        inner = self.rect().adjusted(1, 1, -1, -1)
        clip = QPainterPath()
        clip.addRoundedRect(QRectF(inner), 11, 11)
        painter.setClipPath(clip)
        pixmap = self._pixmap
        pw = max(1, pixmap.width())
        ph = max(1, pixmap.height())
        scale = max(inner.width() / pw, inner.height() / ph)
        draw_w = max(1, int(round(pw * scale)))
        draw_h = max(1, int(round(ph * scale)))
        draw_x = inner.x() + (inner.width() - draw_w) / 2
        draw_y = inner.y() + (inner.height() - draw_h) / 2
        painter.drawPixmap(QRectF(draw_x, draw_y, draw_w, draw_h), pixmap, QRectF(0, 0, pw, ph))

class ThumbnailStrip(QWidget):

    def __init__(self, tile_size: int=THUMB_TILE_SIZE, visible_count: int=THUMB_HOME_VISIBLE_COUNT, spacing: int=8, parent=None):
        super().__init__(parent)
        self.tile_size = tile_size
        self.visible_count = visible_count
        self.spacing = spacing
        self.visible_tiles = []
        self._animations = []
        total_width = tile_size * visible_count + spacing * max(0, visible_count - 1)
        self.setFixedSize(total_width, tile_size)
        self.setStyleSheet('background: transparent;')

    def slot_x(self, index: int) -> int:
        return index * (self.tile_size + self.spacing)

    def has_items(self) -> bool:
        return bool(self.visible_tiles)

    def stop_animations(self):
        for anim in list(self._animations):
            try:
                anim.stop()
            except Exception:
                pass
        self._animations.clear()

    def _track_animation(self, animation):
        self._animations.append(animation)

        def cleanup():
            if animation in self._animations:
                self._animations.remove(animation)
        animation.finished.connect(cleanup)
        animation.start()

    def clear_tiles(self):
        self.stop_animations()
        for tile in self.visible_tiles:
            tile.hide()
            tile.deleteLater()
        self.visible_tiles = []

    def set_paths(self, paths):
        self.clear_tiles()
        for index, path in enumerate(paths[:self.visible_count]):
            tile = ThumbnailTile(self.tile_size, self)
            tile.set_thumbnail(path)
            tile.move(self.slot_x(index), 0)
            tile.set_opacity(1.0)
            tile.show()
            self.visible_tiles.append(tile)

    def refresh_from_disk(self, animate: bool=False, new_path: str=''):
        paths = [str(path) for path in iter_saved_thumbnail_files(limit=self.visible_count)]
        current_paths = [tile.thumb_path for tile in self.visible_tiles]
        if not animate or not new_path or (not paths):
            self.set_paths(paths)
            return
        if str(new_path) in current_paths:
            self.update_tile_content(str(new_path))
            return
        if str(new_path) != paths[0]:
            self.set_paths(paths)
            return
        self.animate_insert(str(new_path))

    def update_tile_content(self, thumb_path: str) -> bool:
        thumb_path = str(thumb_path)
        for tile in self.visible_tiles:
            if tile.thumb_path == thumb_path:
                tile.set_thumbnail(thumb_path)
                return True
        return False

    def animate_insert(self, new_path: str):
        existing_paths = [tile.thumb_path for tile in self.visible_tiles]
        if new_path in existing_paths:
            self.update_tile_content(new_path)
            return
        self.stop_animations()
        outgoing_tile = self.visible_tiles[-1] if len(self.visible_tiles) >= self.visible_count else None
        moving_tiles = self.visible_tiles[:-1] if outgoing_tile else list(self.visible_tiles)
        new_tile = ThumbnailTile(self.tile_size, self)
        new_tile.set_thumbnail(new_path)
        new_tile.move(self.slot_x(0), 0)
        new_tile.set_opacity(0.0)
        new_tile.show()
        new_tile.raise_()
        fade_in = QPropertyAnimation(new_tile.opacity_effect, b'opacity', self)
        fade_in.setDuration(180)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(QEasingCurve.OutCubic)
        self._track_animation(fade_in)
        for index, tile in enumerate(moving_tiles, start=1):
            move_anim = QPropertyAnimation(tile, b'pos', self)
            move_anim.setDuration(220)
            move_anim.setStartValue(tile.pos())
            move_anim.setEndValue(QPoint(self.slot_x(index), 0))
            move_anim.setEasingCurve(QEasingCurve.InOutCubic)
            self._track_animation(move_anim)
        if outgoing_tile is not None:
            fade_out = QPropertyAnimation(outgoing_tile.opacity_effect, b'opacity', self)
            fade_out.setDuration(140)
            fade_out.setStartValue(outgoing_tile.opacity_effect.opacity())
            fade_out.setEndValue(0.0)
            fade_out.setEasingCurve(QEasingCurve.OutCubic)

            def dispose_outgoing(tile=outgoing_tile):
                tile.hide()
                tile.deleteLater()
            fade_out.finished.connect(dispose_outgoing)
            self._track_animation(fade_out)
        self.visible_tiles = [new_tile] + moving_tiles[:self.visible_count - 1]

class HomePage(PageBase):

    def __init__(self, window):
        super().__init__(f'{APP_NAME} v{APP_VERSION}', 'Simple monitoring, polished visuals, and everything inside the same interface.')
        self.window = window
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 2)
        left = QVBoxLayout()
        left.setSpacing(1)
        left.addWidget(self.title)
        left.addWidget(self.subtitle)
        header.addLayout(left, 1)
        self.cfg_btn = HoverButton('⚙', size=18, tooltip='Settings', bg='transparent', hover='#1d2025', fg='#6f7580', font_size=8)
        self.cfg_btn.clicked.connect(self.window.open_settings_page)
        header.addWidget(self.cfg_btn, 0, Qt.AlignTop | Qt.AlignRight)
        self.layout().insertLayout(0, header)
        self.layout().removeItem(self.layout().itemAt(1))
        self.webhook_row = HomeValueRow(self.window, 'Webhook', 'Edit', self.window.open_webhook_page)
        self.body.addWidget(self.webhook_row)
        self.folder_row = HomeValueRow(self.window, 'Watched Folder', 'Edit', self.window.open_folder_page)
        self.body.addWidget(self.folder_row)
        self.history_wrap = QWidget()
        self.history_wrap.setStyleSheet('background: transparent;')
        self.history_layout = QVBoxLayout(self.history_wrap)
        self.history_layout.setContentsMargins(0, 0, 0, 0)
        self.history_layout.setSpacing(6)
        self.history_label = QLabel('History')
        self.history_label.setStyleSheet(f"color:{TEXT}; font: 700 9px 'Segoe UI'; background: transparent; border: none;")
        self.history_layout.addWidget(self.history_label)
        self.thumb_strip = ThumbnailStrip(parent=self.history_wrap)
        self.history_layout.addWidget(self.thumb_strip, 0, Qt.AlignLeft)
        self.body.addWidget(self.history_wrap)
        self.history_wrap.hide()
        self.body.addStretch(1)
        bottom = QHBoxLayout()
        bottom.setContentsMargins(0, 0, 0, 0)
        bottom.addStretch(1)
        bottom.setSpacing(8)
        self.pause_btn = self.window.make_small_button('Pause', self.window.toggle_monitoring, accent=BLUE)
        self.pause_btn.setFixedSize(102, 30)
        bottom.addWidget(self.pause_btn)
        self.send_now_btn = self.window.make_small_button('Send Now', self.window.start_send_now, accent=BLUE)
        self.send_now_btn.setFixedSize(102, 30)
        bottom.addWidget(self.send_now_btn)
        self.body.addLayout(bottom)

    def refresh(self):
        self.webhook_row.set_value(config.get('webhook', ''), 'No webhook configured')
        self.folder_row.set_value(config.get('folder', ''), 'No folder selected')
        self.refresh_thumbnails()
        self.update_pause_visual()

    def refresh_thumbnails(self):
        self.thumb_strip.refresh_from_disk(animate=False)
        self.history_wrap.setVisible(self.thumb_strip.has_items())

    def on_thumbnail_changed(self, thumb_path: str, animate: bool):
        if animate:
            self.thumb_strip.refresh_from_disk(animate=True, new_path=thumb_path)
        else:
            updated = self.thumb_strip.update_tile_content(thumb_path)
            if not updated and (not self.thumb_strip.has_items()):
                self.thumb_strip.refresh_from_disk(animate=False)
        self.history_wrap.setVisible(self.thumb_strip.has_items())

    def update_pause_visual(self):
        if monitoring:
            self.pause_btn.setText('Pause')
            self.pause_btn.setStyleSheet(self.window.small_button_style(enabled=True, accent=BLUE))
            self.pause_btn.setToolTip('Pause monitoring')
        else:
            self.pause_btn.setText('Run')
            self.pause_btn.setStyleSheet(self.window.small_button_style(enabled=True, accent=YELLOW, hover='#ffca52', text_color='#1e1a10'))
            self.pause_btn.setToolTip('Resume monitoring')

class WebhookPage(PageBase):

    def __init__(self, window):
        super().__init__('Edit Webhook', 'Type or paste the full Discord webhook URL.')
        self.window = window
        self.body.addSpacing(8)
        self.input = QLineEdit()
        self.input.setPlaceholderText('https://discord.com/api/webhooks/...')
        self.input.setMinimumHeight(38)
        self.input.setStyleSheet(self.window.input_style())
        self.body.addWidget(self.input)
        buttons = QHBoxLayout()
        self.back_btn = self.window.make_secondary_button('← Back', self.window.go_home)
        self.save_btn = self.window.make_primary_button('Save', self.save)
        buttons.addWidget(self.back_btn)
        buttons.addStretch(1)
        buttons.addWidget(self.save_btn)
        self.body.addLayout(buttons)
        self.body.addStretch(1)

    def refresh(self):
        self.input.setText(config.get('webhook', ''))
        self.input.setFocus()
        self.input.selectAll()

    def save(self):
        text = self.input.text().strip()
        if not is_valid_webhook(text):
            self.window.show_message('error', 'Paste a valid webhook URL.')
            return
        previous_webhook = str(config.get('webhook', '') or '').strip()
        webhook_changed = previous_webhook != text
        config['webhook'] = text
        if webhook_changed:
            delete_avatar_file(AVATAR_IMAGE_FILE, 'webhook_avatar_deleted')
            cleanup_obsolete_avatar_files()
            config['webhook_default_source'] = ''
            config['avatar_mode'] = AVATAR_MODE_WEBHOOK
        reset_avatar_sync_cache()
        save_config()
        refresh_avatar_state(text, force_fetch=webhook_changed or get_avatar_mode() == AVATAR_MODE_WEBHOOK, sync_remote=True)
        self.window.show_message('success', 'Webhook updated.')
        self.window.go_home()

class FolderPage(PageBase):

    def __init__(self, window):
        super().__init__('Edit Watched Folder', 'Choose the folder through the Windows browser instead of typing the path manually.')
        self.window = window
        self.body.addSpacing(8)
        row = QHBoxLayout()
        row.setSpacing(10)
        self.input = QLineEdit()
        self.input.setPlaceholderText('No folder selected')
        self.input.setMinimumHeight(38)
        self.input.setReadOnly(True)
        self.input.setStyleSheet(self.window.input_style())
        row.addWidget(self.input, 1)
        self.browse_btn = self.window.make_secondary_button('Browse', self.browse_folder)
        self.browse_btn.setMinimumHeight(38)
        row.addWidget(self.browse_btn)
        self.body.addLayout(row)
        buttons = QHBoxLayout()
        self.back_btn = self.window.make_secondary_button('← Back', self.window.go_home)
        self.save_btn = self.window.make_primary_button('Save', self.save)
        buttons.addWidget(self.back_btn)
        buttons.addStretch(1)
        buttons.addWidget(self.save_btn)
        self.body.addLayout(buttons)
        self.body.addStretch(1)

    def refresh(self):
        self.input.setText(config.get('folder', ''))

    def browse_folder(self):
        current = config.get('folder', '') or str(Path.home())
        selected = QFileDialog.getExistingDirectory(self.window, 'Select Watched Folder', current, QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        if selected:
            self.input.setText(selected)

    def save(self):
        text = self.input.text().strip().strip('"')
        if not text:
            self.window.show_message('error', 'Select a valid folder.')
            return
        path = Path(text)
        if not path.exists() or not path.is_dir():
            self.window.show_message('error', 'The selected folder does not exist.')
            return
        config['folder'] = str(path)
        save_config()
        self.window.show_message('success', 'Watched folder updated.')
        self.window.go_home()

class PostTemplatePage(PageBase):

    def __init__(self, window):
        super().__init__('Customize Post', 'Edit the raw content that will be sent together with the file on Discord.')
        self.window = window
        self._loading = False
        self.color_popup = None
        self.body.addSpacing(4)
        preview_row = QHBoxLayout()
        preview_row.setContentsMargins(0, 0, 0, 0)
        preview_row.setSpacing(10)
        self.avatar_preview = AvatarPreview(44)
        self.avatar_preview.clicked.connect(self.choose_profile_image)
        preview_row.addWidget(self.avatar_preview, 0, Qt.AlignVCenter)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(APP_NAME)
        self.name_input.setMinimumHeight(40)
        self.name_input.setStyleSheet(self.window.preview_name_style())
        self.name_input.editingFinished.connect(self.on_name_editing_finished)
        self.name_input.textChanged.connect(self.on_name_text_changed)
        preview_row.addWidget(self.name_input, 1)
        self.clear_profile_btn = self.window.make_small_button('Clear', self.remove_profile_image)
        self.clear_profile_btn.setFixedSize(82, 30)
        self.clear_profile_btn.setToolTip('Clear current image and custom name')
        preview_row.addWidget(self.clear_profile_btn, 0, Qt.AlignVCenter)
        self.body.addLayout(preview_row)
        self.editor = QTextEdit()
        self.editor.setPlaceholderText('Type the post content here...')
        self.editor.setStyleSheet(self.window.text_edit_style())
        self.editor.textChanged.connect(self.on_editor_text_changed)
        self.editor.setMinimumHeight(108)
        self.body.addWidget(self.editor, 1)
        self.help_label = QLabel('Variables: {filename}  •  {creation_str}  •  {upload_str}')
        self.help_label.setWordWrap(True)
        self.help_label.setStyleSheet(f"color:{MUTED}; font: 500 8px 'Segoe UI';")
        self.body.addWidget(self.help_label)
        buttons = QHBoxLayout()
        buttons.setContentsMargins(0, 0, 0, 0)
        buttons.setSpacing(8)
        self.back_btn = self.window.make_secondary_button('← Back', self.back_to_settings)
        self.back_btn.setFixedSize(88, 30)
        buttons.addWidget(self.back_btn)
        self.test_btn = self.window.make_small_button('Test Webhook', self.test_webhook)
        self.test_btn.setFixedSize(108, 30)
        buttons.addWidget(self.test_btn)
        buttons.addStretch(1)
        self.color_btn = ColorSwatchButton(config.get('embed_color', DEFAULT_EMBED_COLOR))
        self.color_btn.clicked.connect(self.toggle_embed_color_popup)
        buttons.addWidget(self.color_btn, 0, Qt.AlignVCenter)
        self.embed_label = QLabel('Embed')
        self.embed_label.setStyleSheet(f"color:{TEXT}; font: 700 9px 'Segoe UI';")
        buttons.addWidget(self.embed_label, 0, Qt.AlignVCenter)
        self.embed_toggle = ToggleSwitch(config.get('use_embed', False))
        self.embed_toggle.clicked.connect(self.toggle_embed)
        buttons.addWidget(self.embed_toggle, 0, Qt.AlignVCenter)
        self.body.addLayout(buttons)

    def update_embed_controls_visibility(self):
        use_embed = self.embed_toggle.isChecked()
        self.color_btn.setVisible(use_embed)
        if not use_embed and self.color_popup is not None and self.color_popup.isVisible():
            self.color_popup.commit_and_close()

    def update_profile_preview(self):
        avatar_file = get_effective_avatar_file()
        self.avatar_preview.set_image_path(str(avatar_file) if avatar_file is not None else None)
        current_avatar_is_default = False
        if avatar_file is not None:
            try:
                current_avatar_is_default = Path(avatar_file).resolve() == DEFAULT_PLACEHOLDER_IMAGE_FILE.resolve()
            except Exception:
                current_avatar_is_default = str(avatar_file) == str(DEFAULT_PLACEHOLDER_IMAGE_FILE)
        has_custom_name = bool((self.name_input.text() or '').strip()) or bool(get_custom_webhook_name())
        has_clearable_avatar = get_avatar_mode() != AVATAR_MODE_DEFAULT
        has_custom_state = has_clearable_avatar or has_custom_name
        self.clear_profile_btn.setEnabled(has_custom_state)
        self.clear_profile_btn.setStyleSheet(self.window.small_button_style(enabled=has_custom_state, accent=BLUE))
        self.name_input.setPlaceholderText(APP_NAME)

    def refresh(self):
        self._loading = True
        self.editor.setPlainText(load_template())
        self.name_input.setText(get_custom_webhook_name())
        self.update_profile_preview()
        self.embed_toggle.setChecked(bool(config.get('use_embed', False)))
        self.update_embed_controls_visibility()
        self.color_btn.set_color(config.get('embed_color', DEFAULT_EMBED_COLOR))
        if self.color_popup is not None and self.color_popup.isVisible():
            self.color_popup.set_selected_hex(config.get('embed_color', DEFAULT_EMBED_COLOR), sync_hsv=True, sync_hex=True, emit_live=False)
        has_webhook = bool((config.get('webhook') or '').strip())
        self.test_btn.setEnabled(has_webhook)
        self.test_btn.setStyleSheet(self.window.small_button_style(enabled=has_webhook, accent=BLUE))
        self._loading = False
        self.editor.setFocus()
        cursor = self.editor.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.editor.setTextCursor(cursor)

    def on_editor_text_changed(self):
        if self._loading:
            return

    def on_name_text_changed(self):
        if self._loading:
            return
        self.update_profile_preview()
        self.save_template(show_feedback=False)

    def on_name_editing_finished(self):
        if self._loading:
            return
        self.update_profile_preview()
        self.save_template(show_feedback=False)

    def toggle_embed(self):
        config['use_embed'] = self.embed_toggle.isChecked()
        self.update_embed_controls_visibility()
        save_config()

    def ensure_color_popup(self):
        if self.color_popup is None:
            self.color_popup = EmbedColorPopup(config.get('embed_color', DEFAULT_EMBED_COLOR), self.window)
            self.color_popup.colorChanged.connect(self.on_embed_color_live_changed)
            self.color_popup.colorSaved.connect(self.on_embed_color_saved)
        return self.color_popup

    def toggle_embed_color_popup(self):
        if not self.embed_toggle.isChecked():
            if self.color_popup is not None and self.color_popup.isVisible():
                self.color_popup.commit_and_close()
            return
        popup = self.ensure_color_popup()
        if popup.isVisible():
            popup.commit_and_close()
            return
        popup.set_selected_hex(config.get('embed_color', DEFAULT_EMBED_COLOR), sync_hsv=True, sync_hex=True, emit_live=False)
        popup.show_anchored(self.color_btn, self.window)

    def on_embed_color_live_changed(self, hex_color):
        self.color_btn.set_color(hex_color)

    def on_embed_color_saved(self, hex_color):
        normalized = normalize_hex_color(hex_color)
        config['embed_color'] = normalized
        save_config()
        self.color_btn.set_color(normalized)

    def choose_profile_image(self):
        start_dir = str(Path.home())
        selected, _ = QFileDialog.getOpenFileName(self.window, 'Choose Webhook Profile Image', start_dir, 'Images (*.png *.jpg *.jpeg *.webp *.gif *.bmp)')
        if not selected:
            return
        ok, message = save_custom_profile_image(selected)
        if not ok:
            self.window.show_message('error', message)
            return
        self.save_template(show_feedback=False)
        self.update_profile_preview()
        if (config.get('webhook') or '').strip():
            sync_webhook_avatar(force=True)
        self.window.show_message('success', 'Webhook image updated.')

    def remove_profile_image(self):
        had_avatar_state = get_avatar_mode() != AVATAR_MODE_DEFAULT
        had_custom_name = bool((self.name_input.text() or '').strip()) or bool(get_custom_webhook_name())
        if not had_avatar_state and (not had_custom_name):
            return
        if not remove_custom_profile_image():
            self.window.show_message('error', 'Could not reset the webhook image.')
            return
        self.name_input.clear()
        self.save_template(show_feedback=False)
        self.update_profile_preview()
        if (config.get('webhook') or '').strip():
            sync_webhook_avatar(force=True)
        self.window.show_message('success', 'Webhook image reset to default and custom name cleared.')

    def test_webhook(self):
        ok, msg = send_test_message(self.editor.toPlainText(), self.embed_toggle.isChecked(), webhook_name=self.name_input.text())
        self.window.show_message('success' if ok else 'error', msg)

    def save_template(self, show_feedback=False):
        if self.color_popup is not None and self.color_popup.isVisible():
            self.color_popup.commit_and_close()
        config['post_template'] = normalize_multiline_text(self.editor.toPlainText(), default_template_text())
        config['webhook_custom_name'] = str(self.name_input.text() or '').strip()
        save_config()
        if show_feedback:
            self.window.show_message('success', 'Post settings saved.')

    def back_to_settings(self):
        self.save_template(show_feedback=True)
        self.window.open_settings_page()

class SettingRow(QFrame):

    def __init__(self, title, subtitle, right_widget):
        super().__init__()
        self.setObjectName('settingRow')
        self.setStyleSheet(f'\n            QFrame#settingRow {{\n                background: {CARD};\n                border: 1px solid {CARD_BORDER};\n                border-radius: 16px;\n            }}\n            QLabel {{\n                background: transparent;\n                border: none;\n            }}\n            ')
        root = QHBoxLayout(self)
        root.setContentsMargins(14, 12, 14, 12)
        root.setSpacing(10)
        left = QVBoxLayout()
        left.setSpacing(2)
        t = QLabel(title)
        t.setStyleSheet(f"color:{TEXT}; font: 700 10px 'Segoe UI';")
        left.addWidget(t)
        s = QLabel(subtitle)
        s.setWordWrap(True)
        s.setStyleSheet(f"color:{MUTED}; font: 500 9px 'Segoe UI';")
        left.addWidget(s)
        root.addLayout(left, 1)
        root.addWidget(right_widget, 0, Qt.AlignVCenter)

class SettingsPage(PageBase):

    def __init__(self, window):
        super().__init__('Settings', 'Everything is saved immediately whenever you change an option.')
        self.window = window
        back_row = QHBoxLayout()
        self.back_btn = self.window.make_secondary_button('← Back', self.window.go_home)
        back_row.addWidget(self.back_btn)
        back_row.addStretch(1)
        self.body.addLayout(back_row)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet(self.window.scrollbar_style('QScrollArea'))
        self.scroll_host = QWidget()
        self.scroll_host.setStyleSheet('background: transparent;')
        self.scroll_body = QVBoxLayout(self.scroll_host)
        self.scroll_body.setContentsMargins(0, 0, 4, 0)
        self.scroll_body.setSpacing(10)
        self.scroll.setWidget(self.scroll_host)
        self.body.addWidget(self.scroll, 1)
        self.delete_toggle = ToggleSwitch(config.get('delete_after_send', True))
        self.delete_toggle.clicked.connect(self.toggle_delete_after_send)
        self.scroll_body.addWidget(SettingRow('Delete after send', 'On: moves the file to the Recycle Bin. Off: keeps the file and avoids duplicates through the log.', self.delete_toggle))
        clear_wrap = QWidget()
        clear_wrap.setStyleSheet('background: transparent;')
        clear_layout = QHBoxLayout(clear_wrap)
        clear_layout.setContentsMargins(0, 0, 0, 0)
        self.clear_log_btn = self.window.make_small_button('Clear Log', self.clear_log, accent=YELLOW)
        clear_layout.addWidget(self.clear_log_btn)
        self.scroll_body.addWidget(SettingRow('Clear Log', 'Deletes the history of already sent files and allows them to be sent again.', clear_wrap))
        self.start_toggle = ToggleSwitch(config.get('start_with_windows', False))
        self.start_toggle.clicked.connect(self.toggle_startup)
        self.scroll_body.addWidget(SettingRow('Start with Windows', 'Starts hidden in the system tray when Windows launches.', self.start_toggle))
        post_wrap = QWidget()
        post_wrap.setStyleSheet('background: transparent;')
        post_layout = QHBoxLayout(post_wrap)
        post_layout.setContentsMargins(0, 0, 0, 0)
        self.post_btn = self.window.make_small_button('Edit Post', self.window.open_post_template_page)
        post_layout.addWidget(self.post_btn)
        self.scroll_body.addWidget(SettingRow('Customize Post', 'Opens a page to edit the post text, webhook name, webhook image, and embed settings.', post_wrap))
        timer_wrap = QWidget()
        timer_wrap.setStyleSheet('background: transparent;')
        timer_layout = QHBoxLayout(timer_wrap)
        timer_layout.setContentsMargins(0, 0, 0, 0)
        timer_layout.setSpacing(6)
        self.timer_input = QLineEdit()
        self.timer_input.setValidator(QIntValidator(1, 999999, self))
        self.timer_input.setAlignment(Qt.AlignCenter)
        self.timer_input.setFixedSize(42, 28)
        self.timer_input.setStyleSheet(self.window.compact_input_style())
        self.timer_input.editingFinished.connect(self.on_timer_input_finished)
        timer_layout.addWidget(self.timer_input, 0, Qt.AlignVCenter)
        self.timer_toggle = ToggleSwitch(get_timer_enabled())
        self.timer_toggle.clicked.connect(self.toggle_timer)
        timer_layout.addWidget(self.timer_toggle, 0, Qt.AlignVCenter)
        self.scroll_body.addWidget(SettingRow('Post Timer', 'Off: sends instantly. On: waits the configured number of minutes before sending new posts.', timer_wrap))
        open_wrap = QWidget()
        open_wrap.setStyleSheet('background: transparent;')
        open_layout = QHBoxLayout(open_wrap)
        open_layout.setContentsMargins(0, 0, 0, 0)
        self.open_cfg_btn = self.window.make_small_button('Open Folder', self.open_config_folder)
        open_layout.addWidget(self.open_cfg_btn)
        self.scroll_body.addWidget(SettingRow('Configuration Folder', str(BASE_DIR), open_wrap))
        self.version_value = self.window.make_info_value()
        self.scroll_body.addWidget(SettingRow('App Version', 'Current version in use.', self.version_value))
        self.scroll_body.addStretch(1)

    def refresh(self):
        self.start_toggle.setChecked(config.get('start_with_windows', False))
        self.delete_toggle.setChecked(config.get('delete_after_send', True))
        self.timer_toggle.setChecked(get_timer_enabled())
        self.timer_input.setText(str(get_delay_minutes()))
        self.update_timer_visibility()
        self.version_value.setText(APP_VERSION)

    def current_delay_minutes(self) -> int:
        text = (self.timer_input.text() or '').strip()
        if text.isdigit():
            return max(1, int(text))
        return get_delay_minutes()

    def update_timer_visibility(self):
        visible = self.timer_toggle.isChecked()
        self.timer_input.setVisible(visible)

    def toggle_startup(self):
        enabled = self.start_toggle.isChecked()
        try:
            set_start_with_windows(enabled)
            config['start_with_windows'] = enabled
            save_config()
            self.window.show_message('success', 'Start with Windows updated.')
        except Exception:
            self.start_toggle.setChecked(not enabled)
            self.window.show_message('error', 'Could not change the Start with Windows setting.')

    def toggle_delete_after_send(self):
        config['delete_after_send'] = self.delete_toggle.isChecked()
        save_config()
        self.window.show_message('success', 'Delete option updated.')

    def toggle_timer(self):
        self.update_timer_visibility()
        if self.timer_toggle.isChecked() and (not self.timer_input.text().strip()):
            self.timer_input.setText(str(get_delay_minutes()))
        config['timer_enabled'] = self.timer_toggle.isChecked()
        config['delay_minutes'] = self.current_delay_minutes()
        save_config()
        self.window.show_message('success', 'Post timer updated.')

    def on_timer_input_finished(self):
        self.timer_input.setText(str(self.current_delay_minutes()))
        config['delay_minutes'] = self.current_delay_minutes()
        save_config()
        self.window.show_message('success', 'Post timer updated.')

    def clear_log(self):
        clear_sent_log()
        self.window.show_message('success', 'Send log cleared.')

    def open_config_folder(self):
        BASE_DIR.mkdir(parents=True, exist_ok=True)
        try:
            os.startfile(str(BASE_DIR))
            self.window.show_message('info', f'{APP_NAME} folder opened.')
        except Exception:
            self.window.show_message('error', f'Could not open the {APP_NAME} folder.')

def clear_sent_log():
    global sent_history
    with file_lock:
        sent_history = []
    save_json(LOG_FILE, sent_history)
    clear_thumbnail_log()
    signals.refresh_fields.emit()

class MainWindow(QWidget):

    def __init__(self, tray_icon):
        super().__init__()
        self.tray_icon = tray_icon
        self.drag_pos = None
        self.is_dragging = False
        self.anim = None
        self._drag_origin = None
        self._geometry_fix_pending = False
        self._enforcing_geometry = False
        self.setWindowTitle(f'{APP_NAME} v{APP_VERSION}')
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint | Qt.MSWindowsFixedSizeDialogHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setMinimumSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setMaximumSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setBaseSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 12, 12, 12)
        self.panel = RoundedPanel()
        outer.addWidget(self.panel)
        root = QVBoxLayout(self.panel)
        root.setContentsMargins(16, 14, 16, 12)
        root.setSpacing(10)
        self.stack = CompactStackedWidget()
        self.stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        root.addWidget(self.stack, 1)
        self.message_label = QLabel('')
        self.message_label.setMinimumHeight(16)
        self.message_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.message_label.setStyleSheet(f"color:{MUTED}; font: 600 9px 'Segoe UI';")
        root.addWidget(self.message_label)
        self.home_page = HomePage(self)
        self.webhook_page = WebhookPage(self)
        self.folder_page = FolderPage(self)
        self.settings_page = SettingsPage(self)
        self.post_template_page = PostTemplatePage(self)
        for page in [self.home_page, self.webhook_page, self.folder_page, self.settings_page, self.post_template_page]:
            page.setMinimumSize(0, 0)
            page.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.stack.addWidget(page)
        self.message_timer = QTimer(self)
        self.message_timer.setSingleShot(True)
        self.message_timer.timeout.connect(self.clear_message)
        signals.status_changed.connect(self.on_status_changed)
        signals.toast.connect(self.show_message)
        signals.refresh_fields.connect(self.refresh_all)
        signals.thumbnail_changed.connect(self.home_page.on_thumbnail_changed)
        self.refresh_all()
        self.go_home(animated=False)

    def input_style(self):
        return f"\n        QLineEdit {{\n            background: {FIELD_BG};\n            color: {FIELD_TEXT};\n            border: 1px solid #2c3038;\n            border-radius: 16px;\n            padding: 0 14px;\n            font: 600 9px 'Segoe UI';\n        }}\n        QLineEdit:focus {{ border: 1px solid {BLUE}; }}\n        QLineEdit::placeholder {{ color: #6f7580; }}\n        "

    def scrollbar_style(self, selector='QScrollArea'):
        return f'\n        {selector} {{\n            background: transparent;\n            border: none;\n        }}\n        QScrollBar:vertical {{\n            background: transparent;\n            border: none;\n            width: 8px;\n            margin: 6px 0 6px 0;\n        }}\n        QScrollBar::handle:vertical {{\n            background: #2a2d34;\n            border: none;\n            border-radius: 4px;\n            min-height: 24px;\n        }}\n        QScrollBar::handle:vertical:hover {{\n            background: #343944;\n        }}\n        QScrollBar::handle:vertical:pressed {{\n            background: #3d4451;\n        }}\n        QScrollBar::add-line:vertical,\n        QScrollBar::sub-line:vertical {{\n            height: 0px;\n            background: transparent;\n            border: none;\n        }}\n        QScrollBar::add-page:vertical,\n        QScrollBar::sub-page:vertical {{\n            background: transparent;\n            border: none;\n        }}\n        QScrollBar:horizontal {{\n            background: transparent;\n            border: none;\n            height: 0px;\n            margin: 0;\n        }}\n        QScrollBar::handle:horizontal,\n        QScrollBar::add-line:horizontal,\n        QScrollBar::sub-line:horizontal,\n        QScrollBar::add-page:horizontal,\n        QScrollBar::sub-page:horizontal {{\n            background: transparent;\n            border: none;\n            width: 0px;\n        }}\n        '

    def text_edit_style(self):
        return f"\n        QTextEdit {{\n            background: {FIELD_BG};\n            color: {FIELD_TEXT};\n            border: 1px solid #2c3038;\n            border-radius: 18px;\n            padding: 10px 12px;\n            font: 600 9px 'Segoe UI';\n        }}\n        QTextEdit:focus {{ border: 1px solid {BLUE}; }}\n        {self.scrollbar_style('QTextEdit')}\n        "

    def preview_name_style(self):
        return f"\n        QLineEdit {{\n            background: transparent;\n            color: {FIELD_TEXT};\n            border: none;\n            padding: 0 2px;\n            font: 700 10px 'Segoe UI';\n        }}\n        QLineEdit:focus {{\n            border: none;\n        }}\n        QLineEdit::placeholder {{\n            color: {FIELD_TEXT};\n        }}\n        "

    def compact_input_style(self):
        return f"\n        QLineEdit {{\n            background: {FIELD_BG};\n            color: {FIELD_TEXT};\n            border: 1px solid #2c3038;\n            border-radius: 12px;\n            padding: 0 6px;\n            font: 700 9px 'Segoe UI';\n        }}\n        QLineEdit:focus {{ border: 1px solid {BLUE}; }}\n        QLineEdit::placeholder {{ color: #6f7580; }}\n        "

    def make_primary_button(self, text, handler):
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(handler)
        btn.setStyleSheet(f"\n            QPushButton {{\n                background: {BLUE};\n                color: white;\n                border: none;\n                border-radius: 13px;\n                padding: 7px 14px;\n                font: 700 9px 'Segoe UI';\n            }}\n            QPushButton:hover {{ background: {BLUE}; }}\n            ")
        return btn

    def make_secondary_button(self, text, handler):
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(handler)
        btn.setStyleSheet(f"\n            QPushButton {{\n                background: #24272d;\n                color: {TEXT};\n                border: 1px solid #30343d;\n                border-radius: 13px;\n                padding: 7px 12px;\n                font: 700 9px 'Segoe UI';\n            }}\n            QPushButton:hover {{ background: #2b3038; }}\n            ")
        return btn

    def small_button_style(self, enabled=True, accent=BLUE, hover=None, text_color=None):
        if enabled:
            bg = accent
            fg = text_color or '#ffffff'
            if hover is None:
                if accent == BLUE:
                    hover = BLUE
                elif accent == YELLOW:
                    hover = '#ffca52'
                else:
                    hover = accent
        else:
            bg = '#2d3138'
            fg = '#6e7480'
            hover = '#2d3138'
        return f"\n        QPushButton {{\n            background: {bg};\n            color: {fg};\n            border: none;\n            border-radius: 12px;\n            padding: 7px 12px;\n            font: 700 9px 'Segoe UI';\n        }}\n        QPushButton:hover {{ background: {hover}; }}\n        "

    def make_small_button(self, text, handler, accent=BLUE):
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(handler)
        btn.setMinimumHeight(28)
        btn.setMinimumWidth(74)
        btn.setStyleSheet(self.small_button_style(True, accent=accent))
        return btn

    def make_info_value(self):
        label = QLabel('')
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        label.setStyleSheet(f"color:{TEXT}; font: 600 9px 'Segoe UI'; background: transparent; border: none;")
        return label

    def refresh_all(self):
        self.home_page.refresh()
        self.settings_page.refresh()
        if hasattr(self, 'post_template_page'):
            self.post_template_page.update_profile_preview()

    def save_post_template_if_needed(self, show_feedback=False):
        if self.stack.currentWidget() is self.post_template_page:
            self.post_template_page.save_template(show_feedback=show_feedback)

    def switch_page(self, page, animated=True):
        current = self.stack.currentWidget()
        if current is self.post_template_page and page is not self.post_template_page:
            self.post_template_page.save_template()
        page.refresh()
        self.stack.setCurrentWidget(page)
        if animated:
            effect = QGraphicsOpacityEffect(page)
            page.setGraphicsEffect(effect)
            self.anim = QPropertyAnimation(effect, b'opacity', self)
            self.anim.setDuration(170)
            self.anim.setStartValue(0.35)
            self.anim.setEndValue(1.0)
            self.anim.setEasingCurve(QEasingCurve.OutCubic)
            self.anim.start()
            self.anim.finished.connect(lambda: page.setGraphicsEffect(None))

    def go_home(self, animated=True):
        self.switch_page(self.home_page, animated)

    def open_webhook_page(self):
        self.switch_page(self.webhook_page)

    def open_folder_page(self):
        self.switch_page(self.folder_page)

    def open_settings_page(self):
        self.switch_page(self.settings_page)

    def open_post_template_page(self):
        self.switch_page(self.post_template_page)

    def show_message(self, kind, text):
        colors = {'success': GREEN, 'error': RED, 'warning': YELLOW, 'info': MUTED}
        self.message_label.setStyleSheet(f"color:{colors.get(kind, MUTED)}; font: 700 9px 'Segoe UI';")
        self.message_label.setText(text)
        self.message_timer.start(4200)

    def clear_message(self):
        self.message_label.setText('')

    def start_send_now(self):
        self.save_post_template_if_needed()
        thread = threading.Thread(target=send_now_manual, daemon=True)
        thread.start()

    def toggle_monitoring(self):
        global monitoring
        monitoring = not monitoring
        config['monitoring_enabled'] = monitoring
        save_config()
        signals.status_changed.emit(monitoring)

    def on_status_changed(self, active):
        self.home_page.update_pause_visual()

    def toggle_visible(self):
        if self.isVisible():
            self.save_post_template_if_needed()
            self.hide()
        else:
            self.show_near_tray()

    def ensure_expected_geometry(self):
        if self._enforcing_geometry:
            return
        self._enforcing_geometry = True
        try:
            if self.windowState() != Qt.WindowNoState:
                self.setWindowState(Qt.WindowNoState)
            enforce_fixed_window_size(self, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
        finally:
            self._enforcing_geometry = False

    def schedule_geometry_fix(self):
        if self._geometry_fix_pending:
            return
        self._geometry_fix_pending = True
        QTimer.singleShot(0, self.apply_scheduled_geometry_fix)

    def apply_scheduled_geometry_fix(self):
        self._geometry_fix_pending = False
        self.ensure_expected_geometry()

    def hide_to_tray(self):
        self.save_post_template_if_needed()
        save_window_position(self)
        self.is_dragging = False
        self.drag_pos = None
        self.hide()
        self.clear_message()

    def hideEvent(self, event):
        self.save_post_template_if_needed()
        save_window_position(self)
        super().hideEvent(event)

    def show_near_tray(self):
        self.refresh_all()
        self.ensure_expected_geometry()
        saved_pos = get_saved_window_position()
        restored = False
        if saved_pos is not None:
            x, y = clamp_window_position(saved_pos[0], saved_pos[1])
            restored = is_window_position_valid(saved_pos[0], saved_pos[1])
            if not restored or x != int(saved_pos[0]) or y != int(saved_pos[1]):
                config['window_x'] = int(x)
                config['window_y'] = int(y)
                save_config()
        else:
            screen = get_preferred_screen_geometry()
            x = screen.right() - WINDOW_WIDTH - 20
            y = screen.bottom() - WINDOW_HEIGHT - 50
            x, y = clamp_window_position(x, y)
            config['window_x'] = int(x)
            config['window_y'] = int(y)
            save_config()
        set_window_pos_safely(self, x=x, y=y, move=True, resize=False)
        self.show()
        self.raise_()
        self.activateWindow()
        self.ensure_expected_geometry()

    def exit_app(self):
        self.save_post_template_if_needed()
        save_window_position(self)
        stop_event.set()
        self.hide()
        self.tray_icon.hide()
        QApplication.quit()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.ensure_expected_geometry()
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self._drag_origin = self.pos()
            self.is_dragging = True
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.drag_pos is not None and event.buttons() & Qt.LeftButton:
            target = event.globalPosition().toPoint() - self.drag_pos
            set_window_pos_safely(self, x=target.x(), y=target.y(), move=True, resize=False)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.is_dragging:
            start_pos = self._drag_origin if self._drag_origin is not None else self.pos()
            end_pos = self.pos()
        self.drag_pos = None
        self.is_dragging = False
        self._drag_origin = None
        self.ensure_expected_geometry()
        save_window_position(self)
        super().mouseReleaseEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._enforcing_geometry:
            return
        if event.size().width() != WINDOW_WIDTH or event.size().height() != WINDOW_HEIGHT:
            self.ensure_expected_geometry()

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == event.Type.WindowStateChange and self.windowState() != Qt.WindowNoState:
            self.ensure_expected_geometry()
        if event.type() == event.Type.ActivationChange and (not self.isActiveWindow()) and self.isVisible():
            signals.managed_window_deactivated.emit()

    def showEvent(self, event):
        self.ensure_expected_geometry()
        super().showEvent(event)

    def sizeHint(self):
        return QSize(WINDOW_WIDTH, WINDOW_HEIGHT)

    def minimumSizeHint(self):
        return QSize(WINDOW_WIDTH, WINDOW_HEIGHT)

class TrayExitBubble(QWidget):

    def __init__(self, on_exit, parent=None):
        super().__init__(parent)
        self.on_exit = on_exit
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        self.exit_btn = QPushButton('Quit')
        self.exit_btn.setCursor(Qt.PointingHandCursor)
        self.exit_btn.clicked.connect(self.handle_exit)
        self.exit_btn.setFixedSize(92, 30)
        self.exit_btn.setStyleSheet(f"\n            QPushButton {{\n                background: #24272d;\n                color: {TEXT};\n                border: none;\n                border-radius: 11px;\n                font: 700 9px 'Segoe UI';\n                padding: 4px 10px;\n                text-align: center;\n            }}\n            QPushButton:hover {{\n                background: #2b3038;\n            }}\n            QPushButton:pressed {{\n                background: #20242b;\n            }}\n        ")
        outer.addWidget(self.exit_btn)
        self.hide()

    def handle_exit(self):
        self.hide()
        self.on_exit()

    def show_near_cursor(self):
        self.adjustSize()
        pos = QCursor.pos()
        x = max(0, pos.x() - self.width() + 6)
        y = max(0, pos.y() - self.height() - 6)
        self.move(x, y)
        self.show()
        self.raise_()
        self.activateWindow()

    def focusOutEvent(self, event):
        self.hide()
        super().focusOutEvent(event)

class TrayController(QObject):

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.tray = QSystemTrayIcon(create_tray_icon(True), app)
        self.tray.setToolTip(f'{APP_NAME} v{APP_VERSION}')
        self.rotation = 0.0
        self._last_static_state = None
        self.window = MainWindow(self.tray)
        self.exit_bubble = TrayExitBubble(self.exit_app)
        self.tray.activated.connect(self.on_tray_activated)
        signals.status_changed.connect(self.sync_pause_action)
        self.focus_loss_timer = QTimer(self)
        self.focus_loss_timer.setSingleShot(True)
        self.focus_loss_timer.setInterval(120)
        self.focus_loss_timer.timeout.connect(self.handle_focus_loss)
        self.app.focusChanged.connect(self.on_focus_changed)
        self.app.applicationStateChanged.connect(self.on_application_state_changed)
        signals.managed_window_deactivated.connect(self.on_managed_window_deactivated)
        self.tray_timer = QTimer(self)
        self.tray_timer.setInterval(80)
        self.tray_timer.timeout.connect(self.refresh_tray_icon)
        self.tray_timer.start()
        self.sync_pause_action(monitoring)
        self.tray.show()

    def start_send_now(self):
        thread = threading.Thread(target=send_now_manual, daemon=True)
        thread.start()

    def toggle_monitoring(self):
        global monitoring
        monitoring = not monitoring
        config['monitoring_enabled'] = monitoring
        save_config()
        signals.status_changed.emit(monitoring)

    def open_settings(self):
        self.window.open_settings_page()
        self.window.show_near_tray()

    def refresh_tray_icon(self, force=False):
        sending = sending_event.is_set()
        active = monitoring
        if sending:
            if self._last_static_state != 'sending':
                pass
            self.rotation += 0.35
            self.tray.setIcon(create_tray_icon(active, sending=True, rotation=self.rotation))
            self._last_static_state = 'sending'
            return
        state_key = 'normal' if active else 'paused'
        if force or self._last_static_state != state_key:
            self.tray.setIcon(create_tray_icon(active, sending=False))
            self._last_static_state = state_key

    def sync_pause_action(self, active):
        self.window.home_page.update_pause_visual()
        self.refresh_tray_icon(force=True)

    def on_focus_changed(self, old, now):
        if self.window.is_dragging:
            self.focus_loss_timer.stop()
            return
        if now is None:
            self.focus_loss_timer.start()
        else:
            self.focus_loss_timer.stop()

    def on_application_state_changed(self, state):
        if self.window.is_dragging:
            self.focus_loss_timer.stop()
            return
        active_state = getattr(Qt.ApplicationState, 'ApplicationActive', Qt.ApplicationActive)
        if state == active_state:
            self.focus_loss_timer.stop()
        else:
            self.focus_loss_timer.start()

    def on_managed_window_deactivated(self):
        if self.window.is_dragging:
            self.focus_loss_timer.stop()
            return
        self.focus_loss_timer.start()

    def iter_managed_windows(self):
        managed = [self.window, self.exit_bubble]
        seen = {id(self.window), id(self.exit_bubble)}
        for widget in QApplication.topLevelWidgets():
            if id(widget) in seen:
                continue
            parent = widget.parentWidget()
            if parent is self.window or self.window.isAncestorOf(widget):
                managed.append(widget)
                seen.add(id(widget))
        return managed

    def hide_interface_to_tray(self):
        if self.window.is_dragging:
            return
        for widget in self.iter_managed_windows():
            if widget is not self.window:
                widget.hide()
        self.window.hide_to_tray()

    def handle_focus_loss(self):
        if self.window.is_dragging:
            return
        visible_windows = [widget for widget in self.iter_managed_windows() if widget.isVisible()]
        if not visible_windows:
            return
        if QApplication.activeModalWidget() is not None or QApplication.activePopupWidget() is not None:
            return
        active_window = QApplication.activeWindow()
        if active_window in visible_windows:
            return
        for widget in visible_windows:
            focus_widget = widget.focusWidget()
            if focus_widget is not None and focus_widget.hasFocus():
                return
        self.hide_interface_to_tray()

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.Context:
            self.exit_bubble.show_near_cursor()
            return
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick, QSystemTrayIcon.MiddleClick):
            self.exit_bubble.hide()
            self.window.toggle_visible()

    def exit_app(self):
        self.window.save_post_template_if_needed()
        save_window_position(self.window)
        stop_event.set()
        self.window.hide()
        self.tray.hide()
        QApplication.quit()

def ensure_first_run(window: MainWindow):
    if not config.get('webhook'):
        window.open_webhook_page()
        window.show_near_tray()
        return
    if not config.get('folder'):
        window.open_folder_page()
        window.show_near_tray()
        return
if __name__ == '__main__':
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    FILES_DIR.mkdir(parents=True, exist_ok=True)
    cleanup_obsolete_avatar_files()
    ensure_thumbs_dir()
    save_config()
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    ensure_default_profile_image(force_refresh=True)
    controller = TrayController(app)
    refresh_avatar_state(force_fetch=False, sync_remote=False)
    ensure_first_run(controller.window)
    thumb_worker = threading.Thread(target=thumbnail_worker_loop, daemon=True)
    thumb_worker.start()
    worker = threading.Thread(target=monitoring_loop, daemon=True)
    worker.start()
    exit_code = app.exec()
    try:
        thumbnail_task_queue.put_nowait(None)
    except Exception:
        pass
    sys.exit(exit_code)