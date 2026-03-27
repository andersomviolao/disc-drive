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
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QFrame, QHBoxLayout, QLabel, QLineEdit, QSystemTrayIcon, QPushButton, QStackedWidget, QGraphicsOpacityEffect, QFileDialog, QScrollArea, QTextEdit, QSizePolicy, QScrollBar
try:
    import winreg
except Exception:
    winreg = None
APP_NAME = 'disc-drive'
APP_DIR_NAME = 'disc-drive'
APP_VERSION = '3.0.60'
WINDOW_WIDTH = 560
WINDOW_HEIGHT = 380

BTN_H = 28
BTN_MIN_W = 80
BTN_BORDER = 1
BTN_RADIUS = BTN_H // 2

INPUT_H = 28
TIMER_INPUT_W = 42
HEX_INPUT_H = 28
POST_EDITOR_PAD_X = 12
POST_EDITOR_PAD_Y = 10
POST_EDITOR_FRAME_EXTRA = 2
INPUT_BORDER = 1
INPUT_RADIUS = INPUT_H // 2

TOGGLE_W = 52
TOGGLE_H = 28
TOGGLE_BORDER = 1

COLOR_BTN_SIZE = 28
COLOR_BTN_BORDER = 1
COLOR_BTN_RADIUS = COLOR_BTN_SIZE // 2

AVATAR_SIZE = 46
AVATAR_BORDER = 1

COLOR_PREVIEW_SIZE = 28
COLOR_PREVIEW_BORDER = 1
COLOR_PREVIEW_RADIUS = COLOR_PREVIEW_SIZE // 2

HUE_SLIDER_H = 14
HUE_SLIDER_BORDER = 1
HUE_SLIDER_RADIUS = HUE_SLIDER_H // 2

COLOR_AREA_MIN_W = 200
COLOR_AREA_H = 128
COLOR_AREA_BORDER = 1
COLOR_AREA_RADIUS = 14

POPUP_BORDER = 1
POPUP_RADIUS = 16

FONT_FAMILY = 'Segoe UI'
FONT_FAMILY_SYMBOL = 'Segoe UI Symbol'
FONT_WEIGHT_MEDIUM = 500
FONT_WEIGHT_SEMIBOLD = 600
FONT_WEIGHT_BOLD = 700

WINDOW_OUTER_MARGIN = 12
WINDOW_PANEL_MARGIN_LEFT = 16
WINDOW_PANEL_MARGIN_TOP = 14
WINDOW_PANEL_MARGIN_RIGHT = 16
WINDOW_PANEL_MARGIN_BOTTOM = 12
WINDOW_ROOT_SPACING = 10

SCROLLBAR_RIGHT_INSET = 0
SCROLLBAR_EXTERNAL_OFFSET = 6

CARD_INNER_ROW_SPACING = 12
EMBED_ROW_SPACING = 8
TIMER_ROW_SPACING = 6

POPUP_PADDING_X = 12
POPUP_PADDING_Y = 12
POPUP_CONTENT_SPACING = 10
POPUP_LABEL_INDENT = 38

SCROLLBAR_WIDTH = 4
SCROLLBAR_RADIUS = 2
SCROLLBAR_MARGIN_TOP = 6
SCROLLBAR_MARGIN_BOTTOM = 6
SCROLLBAR_MIN_HANDLE_H = 24

STATUS_LABEL_MIN_H = 16

ALIGN_LEFT_VCENTER = Qt.AlignLeft | Qt.AlignVCenter
ALIGN_LEFT_BOTTOM = Qt.AlignLeft | Qt.AlignBottom
ALIGN_VCENTER = Qt.AlignVCenter

PAGE_SKELETON_ROOT_MARGINS = (0, 0, 0, 0)
PAGE_SKELETON_ROOT_SPACING = 10
PAGE_SKELETON_MIN_CONTENT_W = WINDOW_WIDTH - WINDOW_OUTER_MARGIN * 2 - WINDOW_PANEL_MARGIN_LEFT - WINDOW_PANEL_MARGIN_RIGHT

PAGE_SKELETON_HEADER_MARGINS = (0, 0, 0, 0)
PAGE_SKELETON_HEADER_MIN_H = 0
PAGE_SKELETON_HEADER_TEXT_SPACING = 1
PAGE_SKELETON_TITLE_ALIGNMENT = ALIGN_LEFT_BOTTOM
PAGE_SKELETON_SUBTITLE_ALIGNMENT = ALIGN_LEFT_VCENTER
PAGE_SKELETON_TOP_ROW_MARGINS = (0, 0, 0, 0)
PAGE_SKELETON_TOP_ROW_SPACING = 8

PAGE_SKELETON_BODY_MARGINS = (0, 0, 0, 0)
PAGE_SKELETON_SECTION_STACK_SPACING = 10
PAGE_SKELETON_BODY_SECTION_SPACING = PAGE_SKELETON_SECTION_STACK_SPACING
PAGE_SKELETON_SCROLL_CONTENT_MARGINS = (0, 0, 0, 0)
PAGE_SKELETON_SCROLL_CONTENT_SPACING = PAGE_SKELETON_SECTION_STACK_SPACING
PAGE_SKELETON_HISTORY_MARGINS = (0, 0, 0, 0)
PAGE_SKELETON_HISTORY_SPACING = 8


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
THUMB_HOME_COLUMNS = 6
THUMB_HOME_ROWS = 5
THUMB_HOME_VISIBLE_COUNT = THUMB_HOME_COLUMNS * THUMB_HOME_ROWS
THUMB_HOME_SPACING = 8
THUMB_LOG_LIMIT = 1000
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp'}
VIDEO_EXTENSIONS = {'.mp4', '.mov', '.m4v', '.avi', '.mkv', '.webm', '.wmv', '.mpeg', '.mpg', '.m2ts', '.ts'}
SUPPORTED_MEDIA_EXTENSIONS = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS
DAYS_OF_WEEK = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
PANEL = '#151618'
TEXT = '#d8d8d8'
MUTED = '#7f7f7f'
FIELD_BG = '#222428'
FIELD_TEXT = '#e9ecf2'
BLUE = '#5865F2'
YELLOW = '#f2b01e'
HOVER_DARK = '#222428'
RED = '#ff5f73'
GREEN = '#4fd18b'
CARD = '#1a1c20'
CARD_BORDER = '#252830'
CARD_BORDER_W = 1
CARD_RADIUS = 16
CARD_PADDING_X = 14
CARD_PADDING_Y = 12
CARD_TEXT_SPACING = 2
CARD_CONTENT_SPACING = 10
CARD_PROFILE_MIN_H = 108
CARD_POST_CONTENT_MIN_H = 0
DEFAULT_EMBED_COLOR = BLUE
FONT_TINY = 8
FONT_BASE = 9
FONT_MEDIUM = 10
FONT_TITLE = 12
PAGE_SKELETON_TITLE_COLOR = BLUE
PAGE_SKELETON_SUBTITLE_COLOR = MUTED
PAGE_SKELETON_TITLE_FONT_SIZE = FONT_TITLE
PAGE_SKELETON_SUBTITLE_FONT_SIZE = FONT_BASE
PAGE_SKELETON_TITLE_FONT_WEIGHT = FONT_WEIGHT_BOLD
PAGE_SKELETON_SUBTITLE_FONT_WEIGHT = FONT_WEIGHT_MEDIUM

PAGE_SKELETON_CARD_FRAME_MARGINS = (CARD_PADDING_X, CARD_PADDING_Y, CARD_PADDING_X, CARD_PADDING_Y)
PAGE_SKELETON_CARD_TEXT_SPACING = CARD_TEXT_SPACING
PAGE_SKELETON_CARD_CONTENT_SPACING = CARD_CONTENT_SPACING
PAGE_SKELETON_CARD_MIN_H = 0
PAGE_SKELETON_PROFILE_CARD_MIN_H = CARD_PROFILE_MIN_H
PAGE_SKELETON_POST_CARD_MIN_H = CARD_POST_CONTENT_MIN_H
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


def card_frame_style(object_name: str) -> str:
    return f'''
        QFrame#{object_name} {{
            background: {CARD};
            border: {CARD_BORDER_W}px solid {CARD_BORDER};
            border-radius: {CARD_RADIUS}px;
        }}
        QLabel {{
            background: transparent;
            border: none;
        }}
    '''

def font_css(size: int, weight: int=FONT_WEIGHT_SEMIBOLD, family: str=FONT_FAMILY) -> str:
    return f"{weight} {size}px '{family}'"

def transparent_row_style() -> str:
    return 'background: transparent;'

def set_layout_margins(layout, margins):
    layout.setContentsMargins(*margins)

def make_inline_controls_row(*widgets, spacing=CARD_INNER_ROW_SPACING):
    wrap = QWidget()
    wrap.setStyleSheet(transparent_row_style())
    layout = QHBoxLayout(wrap)
    set_layout_margins(layout, (0, 0, 0, 0))
    layout.setSpacing(spacing)
    for widget in widgets:
        if widget is None:
            layout.addStretch(1)
        else:
            layout.addWidget(widget, 0, ALIGN_VCENTER)
    return (wrap, layout)

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
    default_delay_minutes = max(1, DEFAULT_WAIT_TIME // 60)
    return {'folder': raw.get('folder', ''), 'webhook': raw.get('webhook', ''), 'start_with_windows': bool(raw.get('start_with_windows', False)), 'delete_after_send': bool(raw.get('delete_after_send', True)), 'use_embed': bool(raw.get('use_embed', False)), 'embed_color': normalize_hex_color(raw.get('embed_color', DEFAULT_EMBED_COLOR)), 'post_template': normalize_multiline_text(raw.get('post_template', default_template_text()), default_template_text()), 'timer_enabled': bool(raw.get('timer_enabled', True)), 'delay_minutes': normalize_int(raw.get('delay_minutes', default_delay_minutes), default_delay_minutes, minimum=1), 'post_interval_seconds': normalize_int(raw.get('post_interval_seconds', DEFAULT_POST_INTERVAL), DEFAULT_POST_INTERVAL, minimum=0), 'webhook_custom_name': str(raw.get('webhook_custom_name', '') or '').strip(), 'webhook_default_source': str(raw.get('webhook_default_source', '') or '').strip(), 'avatar_mode': AVATAR_MODE_MANUAL if str(raw.get('avatar_mode', AVATAR_MODE_WEBHOOK) or AVATAR_MODE_WEBHOOK).strip().lower() in {'custom', AVATAR_MODE_MANUAL} else AVATAR_MODE_DEFAULT if str(raw.get('avatar_mode', AVATAR_MODE_WEBHOOK) or AVATAR_MODE_WEBHOOK).strip().lower() == AVATAR_MODE_DEFAULT else AVATAR_MODE_WEBHOOK, 'monitoring_enabled': bool(raw.get('monitoring_enabled', True)), 'window_x': normalize_int(raw.get('window_x', -1), -1, minimum=-1), 'window_y': normalize_int(raw.get('window_y', -1), -1, minimum=-1)}
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

def delete_avatar_file(path: Path):
    try:
        if path.exists():
            path.unlink()
    except Exception as exc:
        pass

def create_default_profile_image() -> bool:
    try:
        FILES_DIR.mkdir(parents=True, exist_ok=True)
        pixmap = QPixmap(256, 256)
        pixmap.fill(QColor(BLUE))
        return pixmap.save(str(DEFAULT_PLACEHOLDER_IMAGE_FILE), 'PNG')
    except Exception:
        return False

def ensure_default_profile_image(force_refresh: bool=True):
    try:
        FILES_DIR.mkdir(parents=True, exist_ok=True)
        if is_usable_image_file(DEFAULT_PLACEHOLDER_IMAGE_FILE):
            return True
        delete_avatar_file(DEFAULT_PLACEHOLDER_IMAGE_FILE)
        return create_default_profile_image() and is_usable_image_file(DEFAULT_PLACEHOLDER_IMAGE_FILE)
    except Exception:
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
    cropped = square_pixmap_from_file(Path(source_path), size=256)
    if cropped is None:
        return (False, 'Could not open the selected image.')
    AVATAR_IMAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not cropped.save(str(AVATAR_IMAGE_FILE), 'PNG'):
        return (False, 'Could not save the profile image.')
    config['avatar_mode'] = AVATAR_MODE_MANUAL
    reset_avatar_sync_cache()
    save_config()
    return (True, str(AVATAR_IMAGE_FILE))

def remove_custom_profile_image():
    delete_avatar_file(AVATAR_IMAGE_FILE)
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
            delete_avatar_file(AVATAR_IMAGE_FILE)
            config['webhook_default_source'] = identity_key
            config['avatar_mode'] = AVATAR_MODE_DEFAULT
            save_config()
            return False
        data = response.json() if response.content else {}
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
                if not avatar_saved:
                    delete_avatar_file(AVATAR_IMAGE_FILE)
            else:
                delete_avatar_file(AVATAR_IMAGE_FILE)
        else:
            delete_avatar_file(AVATAR_IMAGE_FILE)
        config['webhook_default_source'] = identity_key
        config['avatar_mode'] = AVATAR_MODE_WEBHOOK if avatar_saved else AVATAR_MODE_DEFAULT
        reset_avatar_sync_cache()
        save_config()
        return avatar_saved
    except Exception as exc:
        delete_avatar_file(AVATAR_IMAGE_FILE)
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
    try:
        for attempt in range(3):
            response = requests.patch(webhook_url, json={'avatar': avatar_payload}, timeout=15)
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
        with open(path, 'rb'):
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
                    pass
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
        self.setFont(QFont(FONT_FAMILY_SYMBOL, font_size))
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
        self.setFixedSize(TOGGLE_W, TOGGLE_H)
        self.clicked.connect(lambda: self.toggled_visual.emit(self.isChecked()))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(1, 1, -1, -1)
        radius = rect.height() / 2
        bg = QColor(BLUE if self.isChecked() else '#363943')
        painter.setPen(QPen(QColor('#30343d'), TOGGLE_BORDER))
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
        self.setFixedSize(COLOR_BTN_SIZE, COLOR_BTN_SIZE)
        self.apply_style()

    def set_color(self, hex_color):
        self._color = normalize_hex_color(hex_color)
        self.apply_style()

    def apply_style(self):
        border = '#ffffff' if self._hovered else '#30343d'
        self.setStyleSheet(f'\n            QPushButton {{\n                background: {self._color};\n                border: {COLOR_BTN_BORDER}px solid {border};\n                border-radius: {COLOR_BTN_RADIUS}px;\n            }}\n            ')

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

    def __init__(self, size=AVATAR_SIZE, parent=None):
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
        border_color = QColor('#ffffff' if self._hovered else '#30343d')
        painter.setPen(QPen(border_color, AVATAR_BORDER))
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
        self.setMinimumSize(COLOR_AREA_MIN_W, COLOR_AREA_H)
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
        path.addRoundedRect(rect, COLOR_AREA_RADIUS, COLOR_AREA_RADIUS)
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
        pen = QPen(QColor('#30343d'))
        pen.setWidth(COLOR_AREA_BORDER)
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
        self.setFixedHeight(HUE_SLIDER_H)
        self.setCursor(Qt.PointingHandCursor)

    def set_hue(self, hue):
        self._hue = max(0.0, min(1.0, hue))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(1, 1, -1, -1)
        path = QPainterPath()
        path.addRoundedRect(rect, HUE_SLIDER_RADIUS, HUE_SLIDER_RADIUS)
        grad = QLinearGradient(rect.topLeft(), rect.topRight())
        stops = [(0.0, '#ff0000'), (1 / 6, '#ffff00'), (2 / 6, '#00ff00'), (3 / 6, '#00ffff'), (4 / 6, '#0000ff'), (5 / 6, '#ff00ff'), (1.0, '#ff0000')]
        for pos, color in stops:
            grad.setColorAt(pos, QColor(color))
        painter.fillPath(path, grad)
        painter.setPen(QPen(QColor('#2f343d'), HUE_SLIDER_BORDER))
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
        panel.setStyleSheet(f"\n            QFrame#embedColorPopup {{\n                background: {PANEL};\n                border: {POPUP_BORDER}px solid #23262d;\n                border-radius: {POPUP_RADIUS}px;\n            }}\n            QLabel {{\n                color: {TEXT};\n                font: {font_css(FONT_BASE, FONT_WEIGHT_BOLD)};\n                background: transparent;\n                border: none;\n            }}\n            QLineEdit {{\n                background: {FIELD_BG};\n                color: {FIELD_TEXT};\n                border: {INPUT_BORDER}px solid #2c3038;\n                border-radius: {INPUT_RADIUS}px;\n                padding: 0 12px;\n                min-height: {HEX_INPUT_H}px;\n                font: {font_css(FONT_BASE, FONT_WEIGHT_BOLD)};\n            }}\n            QLineEdit:focus {{\n                border: {BTN_BORDER}px solid {BLUE};\n            }}\n            QLineEdit::placeholder {{\n                color: #6f7580;\n            }}\n            ")
        outer.addWidget(panel)
        root = QVBoxLayout(panel)
        root.setContentsMargins(POPUP_PADDING_X, POPUP_PADDING_Y, POPUP_PADDING_X, POPUP_PADDING_Y)
        root.setSpacing(POPUP_CONTENT_SPACING)
        self.spectrum = ColorSpectrumBox(self._hue, self._sat, self._val)
        self.spectrum.setMinimumSize(COLOR_AREA_MIN_W, COLOR_AREA_H)
        self.spectrum.colorChanged.connect(self.on_sv_changed)
        root.addWidget(self.spectrum)
        self.hue_slider = HueSlider(self._hue)
        self.hue_slider.hueChanged.connect(self.on_hue_changed)
        root.addWidget(self.hue_slider)
        label_row = QHBoxLayout()
        label_row.setContentsMargins(POPUP_LABEL_INDENT, 0, 0, 0)
        label_row.setSpacing(0)
        self.hex_label = QLabel('Hex')
        self.hex_label.setStyleSheet(f"color:{TEXT}; font: {font_css(FONT_BASE, FONT_WEIGHT_BOLD)};")
        label_row.addWidget(self.hex_label, 0, ALIGN_LEFT_BOTTOM)
        label_row.addStretch(1)
        root.addLayout(label_row)
        bottom = QHBoxLayout()
        bottom.setContentsMargins(0, 0, 0, 0)
        bottom.setSpacing(POPUP_CONTENT_SPACING)
        self.preview = QLabel()
        self.preview.setFixedSize(COLOR_PREVIEW_SIZE, COLOR_PREVIEW_SIZE)
        bottom.addWidget(self.preview, 0, ALIGN_VCENTER)
        self.hex_input = QLineEdit(self.selected_hex)
        self.hex_input.setPlaceholderText(BLUE)
        self.hex_input.setMaxLength(7)
        self.hex_input.setFixedHeight(HEX_INPUT_H)
        self.hex_input.textChanged.connect(self.on_hex_text_changed)
        self.hex_input.editingFinished.connect(self.on_hex_editing_finished)
        bottom.addWidget(self.hex_input, 1, ALIGN_VCENTER)
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
        self.preview.setStyleSheet(f'background:{hex_color}; border:{COLOR_PREVIEW_BORDER}px solid #30343d; border-radius:{COLOR_PREVIEW_RADIUS}px;')

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
        pen.setWidth(COLOR_AREA_BORDER)
        painter.setPen(pen)
        painter.drawPath(path)
        painter.end()
        super().paintEvent(event)

class PageBase(QWidget):

    def __init__(self, title, subtitle):
        super().__init__()
        self.setMinimumWidth(PAGE_SKELETON_MIN_CONTENT_W)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)

        root = QVBoxLayout(self)
        set_layout_margins(root, PAGE_SKELETON_ROOT_MARGINS)
        root.setSpacing(PAGE_SKELETON_ROOT_SPACING)

        self.header = QWidget()
        self.header.setStyleSheet(transparent_row_style())
        self.header.setMinimumHeight(PAGE_SKELETON_HEADER_MIN_H)
        header_layout = QVBoxLayout(self.header)
        set_layout_margins(header_layout, PAGE_SKELETON_HEADER_MARGINS)
        header_layout.setSpacing(PAGE_SKELETON_HEADER_TEXT_SPACING)

        self.title = QLabel(title)
        self.title.setStyleSheet(f"color:{PAGE_SKELETON_TITLE_COLOR}; font: {font_css(PAGE_SKELETON_TITLE_FONT_SIZE, PAGE_SKELETON_TITLE_FONT_WEIGHT)};")
        header_layout.addWidget(self.title, 0, PAGE_SKELETON_TITLE_ALIGNMENT)

        self.subtitle = QLabel(subtitle)
        self.subtitle.setWordWrap(True)
        self.subtitle.setStyleSheet(f"color:{PAGE_SKELETON_SUBTITLE_COLOR}; font: {font_css(PAGE_SKELETON_SUBTITLE_FONT_SIZE, PAGE_SKELETON_SUBTITLE_FONT_WEIGHT)};")
        header_layout.addWidget(self.subtitle, 0, PAGE_SKELETON_SUBTITLE_ALIGNMENT)

        root.addWidget(self.header)

        self.body = QVBoxLayout()
        set_layout_margins(self.body, PAGE_SKELETON_BODY_MARGINS)
        self.body.setSpacing(PAGE_SKELETON_BODY_SECTION_SPACING)
        root.addLayout(self.body, 1)

    def make_page_top_row(self):
        row = QHBoxLayout()
        set_layout_margins(row, PAGE_SKELETON_TOP_ROW_MARGINS)
        row.setSpacing(PAGE_SKELETON_TOP_ROW_SPACING)
        return row

    def make_page_scroll_area(self, window, *, spacing=PAGE_SKELETON_SCROLL_CONTENT_SPACING):
        self.scroll = ExternalScrollPane(window)
        self.scroll_host = QWidget()
        self.scroll_host.setStyleSheet(transparent_row_style())
        self.scroll_host.setMinimumWidth(PAGE_SKELETON_MIN_CONTENT_W)
        self.scroll_body = QVBoxLayout(self.scroll_host)
        set_layout_margins(self.scroll_body, PAGE_SKELETON_SCROLL_CONTENT_MARGINS)
        self.scroll_body.setSpacing(spacing)
        self.scroll.setWidget(self.scroll_host)
        self.body.addWidget(self.scroll, 1)

    def minimumSizeHint(self):
        return QSize(0, 0)

class ExternalScrollPane(QWidget):

    def __init__(self, window, parent=None):
        super().__init__(parent)
        self.window = window
        self.setStyleSheet(transparent_row_style())

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet(self.window.scroll_container_style('QScrollArea'))
        root.addWidget(self.scroll, 1)

        self.scrollbar = QScrollBar(Qt.Vertical, self)
        self.scrollbar.setCursor(Qt.PointingHandCursor)
        self.scrollbar.setFixedWidth(SCROLLBAR_WIDTH)
        self.scrollbar.setStyleSheet(self.window.scrollbar_style('QScrollBar'))
        self.scrollbar.hide()
        self.scrollbar.raise_()

        internal_bar = self.scroll.verticalScrollBar()
        internal_bar.rangeChanged.connect(self.sync_from_internal_range)
        internal_bar.valueChanged.connect(self.sync_from_internal_value)
        self.scrollbar.valueChanged.connect(self.sync_to_internal_value)

    def setWidget(self, widget):
        self.scroll.setWidget(widget)
        QTimer.singleShot(0, self.refresh_scrollbar)

    def widget(self):
        return self.scroll.widget()

    def verticalScrollBar(self):
        return self.scrollbar

    def scroll_to_top(self):
        self.scrollbar.setValue(0)

    def scrollbar_parent(self):
        overlay_parent = getattr(self.window, 'panel', None) or self.window
        return overlay_parent or self.parentWidget() or self

    def ensure_scrollbar_parent(self):
        target_parent = self.scrollbar_parent()
        if self.scrollbar.parentWidget() is target_parent:
            return target_parent
        visible = self.scrollbar.isVisible()
        self.scrollbar.setParent(target_parent)
        self.scrollbar.setStyleSheet(self.window.scrollbar_style('QScrollBar'))
        self.scrollbar.setCursor(Qt.PointingHandCursor)
        self.scrollbar.setFixedWidth(SCROLLBAR_WIDTH)
        self.scrollbar.setVisible(visible)
        self.scrollbar.raise_()
        return target_parent

    def update_scrollbar_geometry(self):
        target_parent = self.ensure_scrollbar_parent()
        top_left = self.mapTo(target_parent, QPoint(0, 0)) if target_parent is not self else QPoint(0, 0)
        x = top_left.x() + self.width() - SCROLLBAR_WIDTH - SCROLLBAR_RIGHT_INSET + SCROLLBAR_EXTERNAL_OFFSET
        y = top_left.y() + SCROLLBAR_MARGIN_TOP
        h = max(0, self.height() - SCROLLBAR_MARGIN_TOP - SCROLLBAR_MARGIN_BOTTOM)
        self.scrollbar.setGeometry(x, y, SCROLLBAR_WIDTH, h)
        self.scrollbar.raise_()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_scrollbar_geometry()

    def moveEvent(self, event):
        super().moveEvent(event)
        self.update_scrollbar_geometry()

    def showEvent(self, event):
        super().showEvent(event)
        self.scrollbar.setVisible(self.scroll.verticalScrollBar().maximum() > self.scroll.verticalScrollBar().minimum())
        QTimer.singleShot(0, self.update_scrollbar_geometry)

    def hideEvent(self, event):
        super().hideEvent(event)
        self.scrollbar.hide()

    def refresh_scrollbar(self):
        internal_bar = self.scroll.verticalScrollBar()
        self.sync_from_internal_range(internal_bar.minimum(), internal_bar.maximum())
        self.sync_from_internal_value(internal_bar.value())
        self.update_scrollbar_geometry()

    def sync_from_internal_range(self, minimum, maximum):
        internal_bar = self.scroll.verticalScrollBar()
        self.scrollbar.blockSignals(True)
        self.scrollbar.setRange(minimum, maximum)
        self.scrollbar.setPageStep(internal_bar.pageStep())
        self.scrollbar.setSingleStep(internal_bar.singleStep())
        self.scrollbar.blockSignals(False)
        self.scrollbar.setVisible(self.isVisible() and (maximum > minimum))
        self.update_scrollbar_geometry()

    def sync_from_internal_value(self, value):
        internal_bar = self.scroll.verticalScrollBar()
        self.scrollbar.blockSignals(True)
        self.scrollbar.setValue(value)
        self.scrollbar.setPageStep(internal_bar.pageStep())
        self.scrollbar.setSingleStep(internal_bar.singleStep())
        self.scrollbar.blockSignals(False)
        self.scrollbar.setVisible(self.isVisible() and (internal_bar.maximum() > internal_bar.minimum()))
        self.update_scrollbar_geometry()

    def sync_to_internal_value(self, value):
        internal_bar = self.scroll.verticalScrollBar()
        if internal_bar.value() != value:
            internal_bar.setValue(value)


class ThumbnailTile(QLabel):

    def __init__(self, size: int=THUMB_TILE_SIZE, parent=None):
        super().__init__(parent)
        self._size = size
        self.thumb_path = ''
        self._pixmap = QPixmap()
        self.setAlignment(Qt.AlignCenter)
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.opacity_effect.setOpacity(1.0)
        self.setGraphicsEffect(self.opacity_effect)
        self.set_tile_size(size)

    def set_tile_size(self, size: int):
        self._size = max(1, int(size))
        radius = max(10, min(12, self._size // 5))
        self.setFixedSize(self._size, self._size)
        self.setStyleSheet(f'background:{CARD}; border:{CARD_BORDER_W}px solid {CARD_BORDER}; border-radius:{radius}px;')
        self.update()

    def set_opacity(self, value: float):
        self.opacity_effect.setOpacity(value)

    def set_thumbnail(self, thumb_path: Path | str):
        self.thumb_path = str(thumb_path) if thumb_path else ''
        pixmap = QPixmap(self.thumb_path) if self.thumb_path else QPixmap()
        self._pixmap = pixmap
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

    def __init__(self, tile_size: int=THUMB_TILE_SIZE, visible_count: int=THUMB_HOME_VISIBLE_COUNT, columns: int=THUMB_HOME_COLUMNS, spacing: int=THUMB_HOME_SPACING, row_spacing: int=THUMB_HOME_SPACING, parent=None):
        super().__init__(parent)
        self.base_tile_size = tile_size
        self.tile_size = tile_size
        self.visible_count = visible_count
        self.max_columns = max(1, columns)
        self.spacing = max(0, spacing)
        self.row_spacing = max(0, row_spacing)
        self.visible_tiles = []
        self._animations = []
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(self._height_for_count(0))
        self.setStyleSheet('background: transparent;')

    def _row_counts(self, total_items: int) -> list[int]:
        remaining = max(0, min(total_items, self.visible_count))
        counts = []
        while remaining > 0:
            take = min(self.max_columns, remaining)
            counts.append(take)
            remaining -= take
        return counts

    def _effective_tile_size(self) -> int:
        if self.max_columns <= 1:
            return max(1, self.base_tile_size)
        available_width = max(0, self.width())
        if available_width <= 0:
            return max(1, self.base_tile_size)
        total_spacing = self.spacing * max(0, self.max_columns - 1)
        computed = int((available_width - total_spacing) / self.max_columns)
        return max(1, computed)

    def _height_for_count(self, total_items: int) -> int:
        row_count = len(self._row_counts(total_items))
        if row_count <= 0:
            return 0
        tile_size = self._effective_tile_size()
        return tile_size * row_count + self.row_spacing * max(0, row_count - 1)

    def slot_pos(self, index: int, total_items: int | None=None) -> QPoint:
        if total_items is None:
            total_items = len(self.visible_tiles)
        if total_items <= 0:
            return QPoint(0, 0)
        tile_size = self._effective_tile_size()
        row = index // self.max_columns
        column = index % self.max_columns
        x = column * (tile_size + self.spacing)
        y = row * (tile_size + self.row_spacing)
        return QPoint(int(x), int(y))

    def _apply_geometry(self, total_items: int):
        self.tile_size = self._effective_tile_size()
        target_height = self._height_for_count(total_items)
        self.setFixedHeight(target_height)
        for tile in self.visible_tiles:
            tile.set_tile_size(self.tile_size)

    def relayout_tiles(self):
        total_items = len(self.visible_tiles)
        self._apply_geometry(total_items)
        for index, tile in enumerate(self.visible_tiles):
            tile.move(self.slot_pos(index, total_items))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.relayout_tiles()

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
        self._apply_geometry(0)

    def set_paths(self, paths):
        self.clear_tiles()
        visible_paths = paths[:self.visible_count]
        self._apply_geometry(len(visible_paths))
        for index, path in enumerate(visible_paths):
            tile = ThumbnailTile(self.tile_size, self)
            tile.set_thumbnail(path)
            tile.move(self.slot_pos(index, len(visible_paths)))
            tile.set_opacity(1.0)
            tile.show()
            self.visible_tiles.append(tile)
        QTimer.singleShot(0, self.relayout_tiles)

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
        final_total = min(len(moving_tiles) + 1, self.visible_count)
        self._apply_geometry(final_total)

        new_tile = ThumbnailTile(self.tile_size, self)
        new_tile.set_thumbnail(new_path)
        new_tile.move(self.slot_pos(0, final_total))
        new_tile.set_opacity(0.0)
        new_tile.show()
        new_tile.raise_()

        fade_in = QPropertyAnimation(new_tile.opacity_effect, b'opacity', self)
        fade_in.setDuration(140)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(QEasingCurve.OutCubic)
        self._track_animation(fade_in)

        for index, tile in enumerate(moving_tiles, start=1):
            move_anim = QPropertyAnimation(tile, b'pos', self)
            move_anim.setDuration(170)
            move_anim.setStartValue(tile.pos())
            move_anim.setEndValue(self.slot_pos(index, final_total))
            move_anim.setEasingCurve(QEasingCurve.OutCubic)
            self._track_animation(move_anim)

        if outgoing_tile is not None:
            fade_out = QPropertyAnimation(outgoing_tile.opacity_effect, b'opacity', self)
            fade_out.setDuration(120)
            fade_out.setStartValue(outgoing_tile.opacity_effect.opacity())
            fade_out.setEndValue(0.0)
            fade_out.setEasingCurve(QEasingCurve.OutCubic)

            def dispose_outgoing(tile=outgoing_tile):
                tile.hide()
                tile.deleteLater()

            fade_out.finished.connect(dispose_outgoing)
            self._track_animation(fade_out)

        self.visible_tiles = [new_tile] + moving_tiles[:self.visible_count - 1]
        QTimer.singleShot(0, self.relayout_tiles)

class HomePage(PageBase):


    def __init__(self, window):
        super().__init__(f'{APP_NAME} v{APP_VERSION}', 'Simple monitoring, polished visuals, and everything inside the same interface.')
        self.window = window

        top_row = self.make_page_top_row()
        self.pause_btn = self.window.make_small_button('Pause', self.window.toggle_monitoring, accent=BLUE)
        self.pause_btn.setMinimumWidth(BTN_MIN_W)
        top_row.addWidget(self.pause_btn)
        top_row.addStretch(1)
        self.cfg_btn = self.window.make_secondary_button('Settings', self.window.open_settings_page)
        self.cfg_btn.setToolTip('Settings')
        self.cfg_btn.setMinimumWidth(BTN_MIN_W)
        top_row.addWidget(self.cfg_btn)
        self.body.addLayout(top_row)

        self.make_page_scroll_area(self.window)

        self.history_card = CardSection('Recent Uploads', 'Latest sent files appear here in the same card layout used by the other pages.')
        self.history_card.setMinimumHeight(PAGE_SKELETON_CARD_MIN_H)
        set_layout_margins(self.history_card.content_layout, PAGE_SKELETON_HISTORY_MARGINS)
        self.history_card.content_layout.setSpacing(PAGE_SKELETON_HISTORY_SPACING)
        self.thumb_strip = ThumbnailStrip(parent=self.history_card)
        self.history_card.content_layout.addWidget(self.thumb_strip)
        self.scroll_body.addWidget(self.history_card)
        self.scroll_body.addStretch(1)
        self.history_card.hide()

    def refresh(self):
        self.refresh_thumbnails()
        self.update_pause_visual()

    def refresh_thumbnails(self):
        self.thumb_strip.refresh_from_disk(animate=False)
        self.history_card.setVisible(self.thumb_strip.has_items())
        self.scroll_host.adjustSize()
        self.scroll.refresh_scrollbar()

    def on_thumbnail_changed(self, thumb_path: str, animate: bool):
        if animate:
            self.thumb_strip.refresh_from_disk(animate=True, new_path=thumb_path)
        else:
            updated = self.thumb_strip.update_tile_content(thumb_path)
            if not updated and (not self.thumb_strip.has_items()):
                self.thumb_strip.refresh_from_disk(animate=False)
        self.history_card.setVisible(self.thumb_strip.has_items())
        self.scroll_host.adjustSize()
        self.scroll.refresh_scrollbar()

    def update_pause_visual(self):
        if monitoring:
            self.pause_btn.setText('Pause')
            self.pause_btn.setStyleSheet(self.window.small_button_style(enabled=True, accent=BLUE))
            self.pause_btn.setToolTip('Pause monitoring')
        else:
            self.pause_btn.setText('Run')
            self.pause_btn.setStyleSheet(self.window.small_button_style(enabled=True, accent=YELLOW, hover='#ffca52', text_color='#1e1a10'))
            self.pause_btn.setToolTip('Resume monitoring')


class AutoHeightTextEdit(QTextEdit):

    heightChanged = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptRichText(False)
        self.setLineWrapMode(QTextEdit.WidgetWidth)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.document().setDocumentMargin(0)
        self.document().documentLayout().documentSizeChanged.connect(self.update_dynamic_height)

    def _target_height(self) -> int:
        line_height = self.fontMetrics().lineSpacing()
        document_height = math.ceil(self.document().documentLayout().documentSize().height())
        content_height = max(line_height, document_height)
        return int(content_height + POST_EDITOR_PAD_Y * 2 + POST_EDITOR_FRAME_EXTRA)

    def update_dynamic_height(self):
        target = self._target_height()
        if self.height() != target:
            self.setFixedHeight(target)
            self.heightChanged.emit(target)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        QTimer.singleShot(0, self.update_dynamic_height)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self.update_dynamic_height)


class PostTemplatePage(PageBase):

    def __init__(self, window):
        super().__init__('Customize Post', 'Edit the raw content that will be sent together with the file on Discord.')
        self.window = window
        self._loading = False
        self.color_popup = None

        top_row = self.make_page_top_row()
        self.back_btn = self.window.make_secondary_button('← Back', self.back_to_settings)
        top_row.addWidget(self.back_btn)
        top_row.addStretch(1)
        self.test_btn = self.window.make_small_button('Test Webhook', self.test_webhook)
        self.test_btn.setMinimumWidth(BTN_MIN_W)
        top_row.addWidget(self.test_btn)
        self.body.addLayout(top_row)

        self.make_page_scroll_area(self.window)

        self.profile_card = CardSection('Webhook Profile', 'Choose the avatar, set the webhook name, or clear the current custom data.')
        self.profile_card.setMinimumHeight(PAGE_SKELETON_PROFILE_CARD_MIN_H)
        profile_wrap, profile_row = make_inline_controls_row(spacing=CARD_INNER_ROW_SPACING)
        self.avatar_preview = AvatarPreview(AVATAR_SIZE)
        self.avatar_preview.clicked.connect(self.choose_profile_image)
        profile_row.addWidget(self.avatar_preview, 0, ALIGN_VCENTER)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(APP_NAME)
        self.name_input.setFixedHeight(INPUT_H)
        self.name_input.setStyleSheet(self.window.input_style())
        self.name_input.editingFinished.connect(self.on_name_editing_finished)
        self.name_input.textChanged.connect(self.on_name_text_changed)
        profile_row.addWidget(self.name_input, 1)
        self.clear_profile_btn = self.window.make_small_button('Clear', self.remove_profile_image)
        self.clear_profile_btn.setMinimumWidth(BTN_MIN_W)
        self.clear_profile_btn.setToolTip('Clear current image and custom name')
        profile_row.addWidget(self.clear_profile_btn, 0, ALIGN_VCENTER)
        self.profile_card.content_layout.addWidget(profile_wrap)
        self.scroll_body.addWidget(self.profile_card)

        embed_wrap, embed_layout = make_inline_controls_row(spacing=EMBED_ROW_SPACING)
        self.color_btn = ColorSwatchButton(config.get('embed_color', DEFAULT_EMBED_COLOR))
        self.color_btn.clicked.connect(self.toggle_embed_color_popup)
        embed_layout.addWidget(self.color_btn, 0, ALIGN_VCENTER)
        self.embed_toggle = ToggleSwitch(config.get('use_embed', False))
        self.embed_toggle.clicked.connect(self.toggle_embed)
        embed_layout.addWidget(self.embed_toggle, 0, ALIGN_VCENTER)
        self.embed_card = SettingRow('Embed', 'Enable embed mode and choose the accent color that will be used on Discord.', embed_wrap)
        self.scroll_body.addWidget(self.embed_card)

        self.content_card = CardSection('Post Content', 'Edit the message template that will be sent together with the file.')
        self.content_card.setMinimumHeight(PAGE_SKELETON_POST_CARD_MIN_H)
        self.content_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        self.editor = AutoHeightTextEdit()
        self.editor.setPlaceholderText('Type the post content here...')
        self.editor.setStyleSheet(self.window.post_editor_style())
        self.editor.textChanged.connect(self.on_editor_text_changed)
        self.editor.heightChanged.connect(self.on_editor_height_changed)
        self.content_card.content_layout.addWidget(self.editor)
        self.help_label = QLabel('Variables: {filename}  •  {creation_str}  •  {upload_str}')
        self.help_label.setWordWrap(True)
        self.help_label.setStyleSheet(f"color:{MUTED}; font: {font_css(FONT_TINY, FONT_WEIGHT_MEDIUM)};")
        self.content_card.content_layout.addWidget(self.help_label)
        self.scroll_body.addWidget(self.content_card)
        self.scroll_body.addStretch(1)

    def update_embed_controls_visibility(self):
        use_embed = self.embed_toggle.isChecked()
        self.color_btn.setVisible(use_embed)
        if not use_embed and self.color_popup is not None and self.color_popup.isVisible():
            self.color_popup.commit_and_close()

    def update_profile_preview(self):
        avatar_file = get_effective_avatar_file()
        self.avatar_preview.set_image_path(str(avatar_file) if avatar_file is not None else None)
        has_custom_name = bool((self.name_input.text() or '').strip()) or bool(get_custom_webhook_name())
        has_clearable_avatar = get_avatar_mode() != AVATAR_MODE_DEFAULT
        has_custom_state = has_clearable_avatar or has_custom_name
        self.clear_profile_btn.setEnabled(has_custom_state)
        self.clear_profile_btn.setStyleSheet(self.window.small_button_style(enabled=has_custom_state, accent=BLUE))
        self.name_input.setPlaceholderText(APP_NAME)

    def refresh(self):
        self._loading = True
        self.editor.setPlainText(load_template())
        self.editor.update_dynamic_height()
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
        self.scroll.scroll_to_top()
        self._loading = False
        self.editor.setFocus()
        cursor = self.editor.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.editor.setTextCursor(cursor)

    def on_editor_text_changed(self):
        if self._loading:
            return
        self.save_template(show_feedback=False)

    def on_editor_height_changed(self, _height):
        self.content_card.updateGeometry()
        self.scroll_host.adjustSize()
        self.scroll.refresh_scrollbar()

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

class BaseCardFrame(QFrame):

    def __init__(self, object_name: str, title: str, subtitle: str=''):
        super().__init__()
        self.setObjectName(object_name)
        self.setStyleSheet(card_frame_style(object_name))
        self.setMinimumHeight(PAGE_SKELETON_CARD_MIN_H)
        self.root = QVBoxLayout(self)
        set_layout_margins(self.root, PAGE_SKELETON_CARD_FRAME_MARGINS)
        self.root.setSpacing(PAGE_SKELETON_CARD_CONTENT_SPACING)
        self.text_block = QWidget()
        self.text_block.setStyleSheet(transparent_row_style())
        self.text_layout = QVBoxLayout(self.text_block)
        set_layout_margins(self.text_layout, (0, 0, 0, 0))
        self.text_layout.setSpacing(PAGE_SKELETON_CARD_TEXT_SPACING)
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(f"color:{TEXT}; font: {font_css(FONT_MEDIUM, FONT_WEIGHT_BOLD)};")
        self.text_layout.addWidget(self.title_label)
        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setWordWrap(True)
        self.subtitle_label.setStyleSheet(f"color:{MUTED}; font: {font_css(FONT_BASE, FONT_WEIGHT_MEDIUM)};")
        self.text_layout.addWidget(self.subtitle_label)
        self.subtitle_label.setVisible(bool(subtitle))

    def set_subtitle(self, subtitle):
        self.subtitle_label.setText(subtitle)
        self.subtitle_label.setVisible(bool(subtitle))

class SettingRow(BaseCardFrame):

    def __init__(self, title, subtitle, right_widget):
        super().__init__('settingRow', title, subtitle)
        row = QHBoxLayout()
        set_layout_margins(row, (0, 0, 0, 0))
        row.setSpacing(PAGE_SKELETON_CARD_CONTENT_SPACING)
        row.addWidget(self.text_block, 1)
        row.addWidget(right_widget, 0, ALIGN_VCENTER)
        self.root.addLayout(row)

class CardSection(BaseCardFrame):

    def __init__(self, title, subtitle=''):
        super().__init__('cardSection', title, subtitle)
        self.root.addWidget(self.text_block)
        self.content_layout = QVBoxLayout()
        set_layout_margins(self.content_layout, (0, 0, 0, 0))
        self.content_layout.setSpacing(PAGE_SKELETON_CARD_CONTENT_SPACING)
        self.root.addLayout(self.content_layout)

class SettingsPage(PageBase):

    def __init__(self, window):
        super().__init__('Settings', 'Everything is saved immediately whenever you change an option.')
        self.window = window
        back_row = self.make_page_top_row()
        self.back_btn = self.window.make_secondary_button('← Back', self.window.go_home)
        back_row.addWidget(self.back_btn)
        back_row.addStretch(1)
        self.body.addLayout(back_row)
        self.make_page_scroll_area(self.window)

        webhook_wrap, webhook_layout = make_inline_controls_row()
        self.webhook_paste_btn = self.window.make_small_button('Paste', self.paste_webhook)
        webhook_layout.addWidget(self.webhook_paste_btn)
        self.webhook_row = SettingRow('Webhook', '', webhook_wrap)
        self.scroll_body.addWidget(self.webhook_row)

        folder_wrap, folder_layout = make_inline_controls_row()
        self.folder_browse_btn = self.window.make_small_button('Browse', self.browse_folder)
        folder_layout.addWidget(self.folder_browse_btn)
        self.watched_folder_row = SettingRow('Watched Folder', '', folder_wrap)
        self.scroll_body.addWidget(self.watched_folder_row)

        self.delete_toggle = ToggleSwitch(config.get('delete_after_send', True))
        self.delete_toggle.clicked.connect(self.toggle_delete_after_send)
        self.scroll_body.addWidget(SettingRow('Delete after send', 'On: moves the file to the Recycle Bin. Off: keeps the file and avoids duplicates through the log.', self.delete_toggle))
        clear_wrap, clear_layout = make_inline_controls_row()
        self.clear_log_btn = self.window.make_small_button('Clear Log', self.clear_log, accent=YELLOW)
        clear_layout.addWidget(self.clear_log_btn)
        self.scroll_body.addWidget(SettingRow('Clear Log', 'Deletes the history of already sent files and allows them to be sent again.', clear_wrap))
        self.start_toggle = ToggleSwitch(config.get('start_with_windows', False))
        self.start_toggle.clicked.connect(self.toggle_startup)
        self.scroll_body.addWidget(SettingRow('Start with Windows', 'Starts hidden in the system tray when Windows launches.', self.start_toggle))
        post_wrap, post_layout = make_inline_controls_row()
        self.post_btn = self.window.make_small_button('Edit Post', self.window.open_post_template_page)
        post_layout.addWidget(self.post_btn)
        self.scroll_body.addWidget(SettingRow('Customize Post', 'Opens a page to edit the post text, webhook name, webhook image, and embed settings.', post_wrap))
        timer_wrap, timer_layout = make_inline_controls_row(spacing=TIMER_ROW_SPACING)
        self.timer_input = QLineEdit()
        self.timer_input.setValidator(QIntValidator(1, 999999, self))
        self.timer_input.setAlignment(Qt.AlignCenter)
        self.timer_input.setFixedSize(TIMER_INPUT_W, INPUT_H)
        self.timer_input.setStyleSheet(self.window.compact_input_style())
        self.timer_input.editingFinished.connect(self.on_timer_input_finished)
        timer_layout.addWidget(self.timer_input, 0, ALIGN_VCENTER)
        self.timer_toggle = ToggleSwitch(get_timer_enabled())
        self.timer_toggle.clicked.connect(self.toggle_timer)
        timer_layout.addWidget(self.timer_toggle, 0, ALIGN_VCENTER)
        self.scroll_body.addWidget(SettingRow('Post Timer', 'Delay before sending new posts.', timer_wrap))
        open_wrap, open_layout = make_inline_controls_row()
        self.open_cfg_btn = self.window.make_small_button('Open Folder', self.open_config_folder)
        open_layout.addWidget(self.open_cfg_btn)
        self.scroll_body.addWidget(SettingRow('Configuration Folder', str(BASE_DIR), open_wrap))
        self.version_value = self.window.make_info_value()
        self.scroll_body.addWidget(SettingRow('App Version', 'Current version in use.', self.version_value))
        self.scroll_body.addStretch(1)

    def refresh(self):
        self.update_webhook_row_subtitle()
        self.update_folder_row_subtitle()
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

    def format_webhook_subtitle(self, webhook: str) -> str:
        webhook = str(webhook or '').strip()
        if not webhook:
            return 'No webhook set.'
        prefixes = (
            'https://discord.com/api/webhooks/',
            'https://discordapp.com/api/webhooks/',
        )
        for prefix in prefixes:
            if webhook.startswith(prefix):
                rest = webhook[len(prefix):]
                if len(rest) <= 22:
                    return webhook
                return f"{prefix}{rest[:8]}...{rest[-8:]}"
        if len(webhook) <= 52:
            return webhook
        return f"{webhook[:36]}...{webhook[-10:]}"

    def update_webhook_row_subtitle(self):
        webhook = str(config.get('webhook', '') or '').strip()
        subtitle = self.format_webhook_subtitle(webhook)
        self.webhook_row.set_subtitle(subtitle)
        self.webhook_row.subtitle_label.setToolTip(webhook)

    def paste_webhook(self):
        clipboard = QApplication.clipboard()
        text = str(clipboard.text() or '').strip()
        if not is_valid_webhook(text):
            self.window.show_message('error', 'Clipboard does not contain a valid webhook URL.')
            return
        previous_webhook = str(config.get('webhook', '') or '').strip()
        webhook_changed = previous_webhook != text
        config['webhook'] = text
        if webhook_changed:
            delete_avatar_file(AVATAR_IMAGE_FILE)
            config['webhook_default_source'] = ''
            config['avatar_mode'] = AVATAR_MODE_WEBHOOK
        reset_avatar_sync_cache()
        save_config()
        self.update_webhook_row_subtitle()
        refresh_avatar_state(text, force_fetch=webhook_changed or get_avatar_mode() == AVATAR_MODE_WEBHOOK, sync_remote=True)
        self.window.show_message('success', 'Webhook updated.')

    def update_folder_row_subtitle(self):
        folder = str(config.get('folder', '') or '').strip()
        subtitle = folder if folder else 'No folder selected.'
        self.watched_folder_row.set_subtitle(subtitle)

    def browse_folder(self):
        current = str(config.get('folder', '') or '').strip() or str(Path.home())
        selected = QFileDialog.getExistingDirectory(self.window, 'Select Watched Folder', current, QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        if not selected:
            return
        path = Path(selected)
        if not path.exists() or not path.is_dir():
            self.window.show_message('error', 'The selected folder does not exist.')
            return
        config['folder'] = str(path)
        save_config()
        self.update_folder_row_subtitle()
        self.window.show_message('success', 'Watched folder updated.')

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
        outer.setContentsMargins(WINDOW_OUTER_MARGIN, WINDOW_OUTER_MARGIN, WINDOW_OUTER_MARGIN, WINDOW_OUTER_MARGIN)
        outer.setSpacing(0)
        self.panel = RoundedPanel()
        outer.addWidget(self.panel)
        root = QVBoxLayout(self.panel)
        root.setContentsMargins(WINDOW_PANEL_MARGIN_LEFT, WINDOW_PANEL_MARGIN_TOP, WINDOW_PANEL_MARGIN_RIGHT, WINDOW_PANEL_MARGIN_BOTTOM)
        root.setSpacing(WINDOW_ROOT_SPACING)
        self.stack = CompactStackedWidget()
        self.stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        root.addWidget(self.stack, 1)
        self.message_label = QLabel('')
        self.message_label.setMinimumHeight(STATUS_LABEL_MIN_H)
        self.message_label.setAlignment(ALIGN_LEFT_VCENTER)
        self.message_label.setStyleSheet(f"color:{MUTED}; font: {font_css(FONT_BASE, FONT_WEIGHT_SEMIBOLD)};")
        root.addWidget(self.message_label)
        self.home_page = HomePage(self)
        self.settings_page = SettingsPage(self)
        self.post_template_page = PostTemplatePage(self)
        for page in [self.home_page, self.settings_page, self.post_template_page]:
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
        return f"""
        QLineEdit {{
            background: {FIELD_BG};
            color: {FIELD_TEXT};
            border: {BTN_BORDER}px solid #30343d;
            border-radius: {INPUT_RADIUS}px;
            padding: 0 12px;
            min-height: {INPUT_H}px;
            font: {font_css(FONT_BASE, FONT_WEIGHT_SEMIBOLD)};
        }}
        QLineEdit:focus {{ border: {BTN_BORDER}px solid {BLUE}; }}
        QLineEdit::placeholder {{ color: #6f7580; }}
        """
    def scroll_container_style(self, selector='QScrollArea'):
        return f"""
        {selector} {{
            background: transparent;
            border: none;
        }}
        """

    def scrollbar_style(self, selector='QScrollBar'):
        return f"""
        {selector}:vertical {{
            background: transparent;
            border: none;
            width: {SCROLLBAR_WIDTH}px;
            margin: {SCROLLBAR_MARGIN_TOP}px 0 {SCROLLBAR_MARGIN_BOTTOM}px 0;
        }}
        {selector}::handle:vertical {{
            background: #2a2d34;
            border: none;
            border-radius: {SCROLLBAR_RADIUS}px;
            min-height: {SCROLLBAR_MIN_HANDLE_H}px;
        }}
        {selector}::handle:vertical:hover {{
            background: #343944;
        }}
        {selector}::handle:vertical:pressed {{
            background: #3d4451;
        }}
        {selector}::add-line:vertical,
        {selector}::sub-line:vertical {{
            height: 0px;
            background: transparent;
            border: none;
        }}
        {selector}::add-page:vertical,
        {selector}::sub-page:vertical {{
            background: transparent;
            border: none;
        }}
        {selector}:horizontal {{
            background: transparent;
            border: none;
            height: 0px;
            margin: 0;
        }}
        {selector}::handle:horizontal,
        {selector}::add-line:horizontal,
        {selector}::sub-line:horizontal,
        {selector}::add-page:horizontal,
        {selector}::sub-page:horizontal {{
            background: transparent;
            border: none;
            width: 0px;
        }}
        """

    def post_editor_style(self):
        return f"\n        QTextEdit {{\n            background: {FIELD_BG};\n            color: {FIELD_TEXT};\n            border: 1px solid #2c3038;\n            border-radius: {BTN_RADIUS}px;\n            padding: {POST_EDITOR_PAD_Y}px {POST_EDITOR_PAD_X}px;\n            font: {font_css(FONT_BASE, FONT_WEIGHT_SEMIBOLD)};\n        }}\n        QTextEdit:focus {{ border: {BTN_BORDER}px solid {BLUE}; }}\n        "

    def compact_input_style(self):
        return f"""
        QLineEdit {{
            background: {FIELD_BG};
            color: {FIELD_TEXT};
            border: {BTN_BORDER}px solid #30343d;
            border-radius: {INPUT_RADIUS}px;
            padding: 0 8px;
            min-height: {INPUT_H}px;
            font: {font_css(FONT_BASE, FONT_WEIGHT_BOLD)};
        }}
        QLineEdit:focus {{ border: {BTN_BORDER}px solid {BLUE}; }}
        QLineEdit::placeholder {{ color: #6f7580; }}
        """
    def make_secondary_button(self, text, handler):
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(handler)
        btn.setFixedHeight(BTN_H)
        btn.setMinimumWidth(BTN_MIN_W)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: #24272d;
                color: {TEXT};
                border: {BTN_BORDER}px solid #30343d;
                border-radius: {BTN_RADIUS}px;
                padding: 0 12px;
                font: {font_css(FONT_BASE, FONT_WEIGHT_BOLD)};
            }}
            QPushButton:hover {{ background: #2b3038; }}
            QPushButton:pressed {{ background: #20242b; }}
            """)
        return btn
    def small_button_style(self, enabled=True, accent=BLUE, hover=None, text_color=None):
        if enabled:
            bg = accent
            fg = text_color or '#ffffff'
            border = accent
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
            border = '#30343d'
            hover = '#2d3138'
        return f"""
        QPushButton {{
            background: {bg};
            color: {fg};
            border: {BTN_BORDER}px solid {border};
            border-radius: {BTN_RADIUS}px;
            padding: 0 12px;
            font: {font_css(FONT_BASE, FONT_WEIGHT_BOLD)};
        }}
        QPushButton:hover {{ background: {hover}; }}
        QPushButton:pressed {{ background: {hover}; }}
        """
    def make_small_button(self, text, handler, accent=BLUE):
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(handler)
        btn.setFixedHeight(BTN_H)
        btn.setMinimumWidth(BTN_MIN_W)
        btn.setStyleSheet(self.small_button_style(True, accent=accent))
        return btn

    def make_info_value(self):
        label = QLabel('')
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        label.setStyleSheet(f"color:{TEXT}; font: {font_css(FONT_BASE, FONT_WEIGHT_SEMIBOLD)}; background: transparent; border: none;")
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


    def open_settings_page(self):
        self.switch_page(self.settings_page)

    def open_post_template_page(self):
        self.switch_page(self.post_template_page)

    def show_message(self, kind, text):
        colors = {'success': GREEN, 'error': RED, 'warning': YELLOW, 'info': MUTED}
        self.message_label.setStyleSheet(f"color:{colors.get(kind, MUTED)}; font: {font_css(FONT_BASE, FONT_WEIGHT_BOLD)};")
        self.message_label.setText(text)
        self.message_timer.start(4200)

    def clear_message(self):
        self.message_label.setText('')

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
        self.exit_btn.setMinimumSize(BTN_MIN_W, BTN_H)
        self.exit_btn.setStyleSheet(f"\n            QPushButton {{\n                background: #24272d;\n                color: {TEXT};\n                border: {BTN_BORDER}px solid #30343d;\n                border-radius: {BTN_RADIUS}px;\n                font: {font_css(FONT_BASE, FONT_WEIGHT_BOLD)};\n                padding: 0 12px;\n                text-align: center;\n            }}\n            QPushButton:hover {{\n                background: #2b3038;\n            }}\n            QPushButton:pressed {{\n                background: #20242b;\n            }}\n        ")
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

    def refresh_tray_icon(self, force=False):
        sending = sending_event.is_set()
        active = monitoring
        if sending:
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
    if not config.get('webhook') or not config.get('folder'):
        window.open_settings_page()
        window.show_near_tray()
        return
if __name__ == '__main__':
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    FILES_DIR.mkdir(parents=True, exist_ok=True)
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