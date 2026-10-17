import os
import sys
import json
import collections
import ctypes
import hashlib
import ipaddress
import queue
import shutil
import socket
import subprocess
import tempfile
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk
import libtorrent as lt
import i18n
from i18n import LANGUAGES, pl, resolve_language, set_language, tr

try:
    import psutil
except Exception:
    psutil = None

try:
    import pystray
    from PIL import Image
    HAS_TRAY = True
except Exception:
    HAS_TRAY = False

APP = "Alf Torrent"
FW_RULE = "Alf Torrent"
CFG_DIR = os.path.join(os.getenv("APPDATA") or os.path.expanduser("~"), "AlfTorrent")
CFG_FILE = os.path.join(CFG_DIR, "config.json")
RESUME_DIR = os.path.join(CFG_DIR, "resume")
TORRENTS_DIR = os.path.join(CFG_DIR, "torrents")
IPC_PORT = 47653                      # instância única (só 127.0.0.1)
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


# ---------------------------------------------------------------- aspeto
C = {"bg": "#090c13", "side": "#0b0f17", "card": "#0e131c", "card2": "#131a26", "hover": "#171f2d",
     "border": "#1a2130", "text": "#e7ebf3", "muted": "#8791a5", "dim": "#586177",
     "blue": "#2f8fff", "blue_hi": "#1f7ae6", "blue_bg": "#10243f",
     "green": "#21c48a", "green_bg": "#0f2a24", "amber": "#d9a441", "amber_bg": "#2a2210",
     "red": "#e5534b", "red_bg": "#2e1517", "gray_bg": "#1a2030"}
BLUE, GREEN, GREY = C["blue"], C["green"], C["dim"]
AMBER, RED = C["amber"], C["red"]
VERSION = "2.0"

_ICONS = {}


def icon(name, color="#8791a5", size=18):
    """Ícones de linha desenhados em código (sem ficheiros nem fontes externas)."""
    key = (name, color, size)
    if key in _ICONS:
        return _ICONS[key]
    from PIL import Image, ImageDraw
    S = size * 8
    k = S / 24.0
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    w = max(2, int(round(1.9 * k)))
    r = w / 2.0

    def line(pts, close=False):
        pp = [(x * k, y * k) for x, y in pts]
        if close:
            pp.append(pp[0])
        d.line(pp, fill=color, width=w, joint="curve")
        for x, y in pp:
            d.ellipse((x - r, y - r, x + r, y + r), fill=color)

    def circ(cx, cy, rad, fill=False):
        bb = ((cx - rad) * k, (cy - rad) * k, (cx + rad) * k, (cy + rad) * k)
        if fill:
            d.ellipse(bb, fill=color)
        else:
            d.ellipse(bb, outline=color, width=w)

    def rrect(x0, y0, x1, y1, rad):
        d.rounded_rectangle((x0 * k, y0 * k, x1 * k, y1 * k), radius=rad * k, outline=color, width=w)

    def arc(x0, y0, x1, y1, a0, a1):
        d.arc((x0 * k, y0 * k, x1 * k, y1 * k), a0, a1, fill=color, width=w)

    shield = [(12, 3), (19.5, 6), (19.5, 12), (17, 16.5), (12, 21), (7, 16.5), (4.5, 12), (4.5, 6)]
    page = [(6, 3), (14, 3), (19, 8), (19, 21), (6, 21)]
    if name == "download":
        line([(12, 4), (12, 15)]); line([(7, 10.5), (12, 15.5), (17, 10.5)]); line([(5, 20), (19, 20)])
    elif name == "upload":
        line([(12, 20), (12, 9)]); line([(7, 13.5), (12, 8.5), (17, 13.5)]); line([(5, 4), (19, 4)])
    elif name == "list":
        rrect(3.5, 4.5, 9.5, 10.5, 1.5); rrect(3.5, 13.5, 9.5, 19.5, 1.5)
        line([(13, 7.5), (20.5, 7.5)]); line([(13, 16.5), (20.5, 16.5)])
    elif name == "pause":
        rrect(6, 4.5, 10, 19.5, 1.2); rrect(14, 4.5, 18, 19.5, 1.2)
    elif name == "play":
        line([(8, 5), (19, 12), (8, 19)], close=True)
    elif name == "folder":
        line([(3, 7), (3, 18.5), (21, 18.5), (21, 9), (11.5, 9), (9.5, 6), (3, 6)], close=True)
    elif name == "more":
        circ(5, 12, 1.7, True); circ(12, 12, 1.7, True); circ(19, 12, 1.7, True)
    elif name == "search":
        circ(11, 11, 6.5); line([(16, 16), (20.5, 20.5)])
    elif name == "clock":
        circ(12, 12, 8.5); line([(12, 7), (12, 12), (15.5, 14)])
    elif name == "sliders":
        line([(4, 6), (20, 6)]); line([(4, 12), (20, 12)]); line([(4, 18), (20, 18)])
        circ(9, 6, 2.3); circ(15, 12, 2.3); circ(8, 18, 2.3)
    elif name == "network":
        line([(8, 5), (8, 19)]); line([(4.5, 15.5), (8, 19), (11.5, 15.5)])
        line([(16, 19), (16, 5)]); line([(12.5, 8.5), (16, 5), (19.5, 8.5)])
    elif name == "chev-right":
        line([(9, 6), (15, 12), (9, 18)])
    elif name == "link":
        rrect(1.5, 9, 13.5, 15, 3); rrect(10.5, 9, 22.5, 15, 3)
        im = im.rotate(-45, resample=Image.BICUBIC)
    elif name == "plus":
        line([(12, 5), (12, 19)]); line([(5, 12), (19, 12)])
    elif name == "file":
        line(page, close=True); line([(14, 3), (14, 8), (19, 8)])
    elif name == "file-play":
        line(page, close=True); line([(14, 3), (14, 8), (19, 8)]); line([(10, 11.5), (15, 14.5), (10, 17.5)], close=True)
    elif name == "users":
        circ(9, 8, 3.3); arc(3, 14, 15, 28, 180, 360); circ(17, 8.5, 2.6); arc(14, 14, 22, 24, 200, 340)
    elif name == "drive":
        rrect(3, 13, 21, 20, 3); line([(3, 13), (5.6, 5.5), (18.4, 5.5), (21, 13)]); circ(7, 16.5, 1.0, True)
    elif name == "check":
        line([(5, 12.5), (10, 17.5), (19, 7)])
    elif name == "shield":
        line(shield, close=True)
    elif name == "shield-check":
        line(shield, close=True); line([(8.5, 12), (11, 14.5), (15.5, 9.5)])
    elif name == "info":
        circ(12, 12, 9); line([(12, 11), (12, 17)]); circ(12, 7.6, 0.7, True)
    else:
        circ(12, 12, 6)
    out = im.resize((size * 2, size * 2), Image.LANCZOS)
    ci = ctk.CTkImage(light_image=out, dark_image=out, size=(size, size))
    _ICONS[key] = ci
    return ci

ENC_LABELS = {"Desativada": "disabled", "Preferida": "enabled", "Obrigatória": "forced"}
SEARCH_KINDS = {"Vídeo": "movies", "Áudio": "audio", "Software": "software",
                "Livros e textos": "texts", "Tudo": ""}

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# ---------------------------------------------------------------- utilitários
def resource_path(name):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)


def dec(text):
    """Separador decimal do idioma: vírgula em português, ponto nos restantes."""
    return text.replace(".", ",") if i18n.LANG == "pt" else text


def fmt_size(n):
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return dec(f"{n:.1f} {unit}")
        n /= 1024
    return dec(f"{n:.1f} PB")


def fmt_speed(n):
    return fmt_size(n) + "/s"


def fmt_eta(seconds):
    seconds = int(seconds)
    if seconds > 86400 * 7:
        return "∞"
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h} h {m:02d} min"
    if m:
        return f"{m} min"
    return f"{s} s"


def size_parts(n):
    """(número, unidade) com vírgula decimal, para os cartões grandes."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            txt = f"{n:.0f}" if unit == "B" else f"{n:.1f}"
            return dec(txt), unit
        n /= 1024


def short_path(p, n=40):
    p = p.replace("\\", "/")
    return p if len(p) <= n else "…" + p[-(n - 1):]


VIDEO_HINTS = (".mkv", ".mp4", ".avi", "1080p", "720p", "2160p", "480p", "web-dl", "webrip",
               "bluray", "x264", "x265", "h264", "h265", "hdtv", "dvdrip", "movie")


def is_video(name):
    n = (name or "").lower()
    return any(h in n for h in VIDEO_HINTS)


FILTER_LABELS = {"all": "Transferências", "down": "A transferir", "seed": "A partilhar", "paused": "Em pausa"}
PAGE_LABELS = {"geral": "Geral", "rede": "Rede e limites", "agenda": "Agendamento"}
BADGES = {   # tipo -> (texto, cor do texto, cor de fundo, ícone)
    "down": ("A transferir", "blue", "blue_bg", "download"),
    "seed": ("A partilhar", "green", "green_bg", "check"),
    "done": ("Concluído", "green", "green_bg", "check"),
    "paused": ("Em pausa", "muted", "gray_bg", "pause"),
    "queued": ("Em fila", "amber", "amber_bg", "clock"),
    "sched": ("Agendado", "amber", "amber_bg", "clock"),
    "check": ("A verificar ficheiros", "blue", "blue_bg", "search"),
    "meta": ("A obter metadados", "blue", "blue_bg", "link"),
    "blocked": ("Bloqueado (sem VPN)", "red", "red_bg", "shield"),
}


def draw_spark(cv, values, color):
    cv.delete("all")
    w, h = int(cv["width"]), int(cv["height"])
    mx = max(values)
    n = len(values)
    pts = []
    for i, v in enumerate(values):
        x = 2 + i * (w - 4) / (n - 1)
        y = h - 4 - (v / mx) * (h - 10) if mx > 0 else h - 4
        pts += [x, y]
    cv.create_line(*pts, fill=color if mx > 0 else C["border"], width=2, smooth=True,
                   capstyle="round", joinstyle="round")


def short(text, n=80):
    return text if len(text) <= n else text[: n - 1] + "…"


def load_cfg():
    default = {
        "save_path": os.path.join(os.path.expanduser("~"), "Downloads"),
        "down_kb": 0, "up_kb": 0, "port": 6881, "max_active": 3,
        "torrents": [], "fw_asked": False,
        "watch_enabled": False, "watch_path": "", "roots": [],
        "close_to_tray": True, "tray_tip_shown": False,
        "encryption": "enabled", "bind_iface": "", "discreet": True, "language": "auto",
        "sched_enabled": False, "sched_start": "01:00", "sched_end": "08:00",
    }
    try:
        with open(CFG_FILE, "r", encoding="utf-8") as f:
            default.update(json.load(f))
    except Exception:
        pass
    return default


def save_cfg(cfg):
    os.makedirs(CFG_DIR, exist_ok=True)
    with open(CFG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


# --------------------------------------------------- rede, horário e pesquisa
def iface_ipv4(name):
    """IPv4 de um adaptador de rede ligado (None se não existir ou estiver em baixo)."""
    if psutil is None:
        return None
    try:
        st = psutil.net_if_stats().get(name)
        if st is None or not st.isup:
            return None
        for a in psutil.net_if_addrs().get(name, []):
            if a.family == socket.AF_INET and not a.address.startswith("169.254."):
                return a.address
    except Exception:
        pass
    return None


def list_ifaces():
    out = []
    if psutil is None:
        return out
    try:
        for name in psutil.net_if_addrs():
            ip = iface_ipv4(name)
            if ip and not ip.startswith("127."):
                out.append((name, ip))
    except Exception:
        pass
    return out


def local_ip():
    """IP deste PC na rede local (não envia pacotes)."""
    try:
        sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sk.connect(("10.255.255.255", 1))
        ip = sk.getsockname()[0]
        sk.close()
        return ip
    except OSError:
        return None


def parse_hm(text):
    h, m = text.strip().split(":")
    h, m = int(h), int(m)
    if not (0 <= h < 24 and 0 <= m < 60):
        raise ValueError(text)
    return h * 60 + m


def fmt_hm(minutes):
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def in_window(now_min, start, end):
    if start == end:
        return True
    if start < end:
        return start <= now_min < end
    return now_min >= start or now_min < end      # atravessa a meia-noite


def http_get(url, timeout=20):
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": "AlfTorrent/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(25 * 1024 * 1024)


def _first(value):
    return value[0] if isinstance(value, list) and value else value


def ia_search(term, mediatype, rows=30):
    """Pesquisa no Internet Archive (conteúdo livre / domínio público)."""
    import urllib.parse
    q = f"({term}) AND mediatype:{mediatype}" if mediatype else term
    params = [("q", q), ("fl[]", "identifier"), ("fl[]", "title"), ("fl[]", "item_size"),
              ("fl[]", "downloads"), ("sort[]", "downloads desc"), ("rows", str(rows)),
              ("page", "1"), ("output", "json")]
    data = http_get("https://archive.org/advancedsearch.php?" + urllib.parse.urlencode(params))
    docs = json.loads(data.decode("utf-8"))["response"]["docs"]
    out = []
    for d in docs:
        ident = _first(d.get("identifier"))
        if not ident:
            continue
        try:
            size = int(_first(d.get("item_size")) or 0)
        except (TypeError, ValueError):
            size = 0
        try:
            downloads = int(_first(d.get("downloads")) or 0)
        except (TypeError, ValueError):
            downloads = 0
        out.append({"id": ident, "title": str(_first(d.get("title")) or ident),
                    "size": size, "downloads": downloads})
    return out


# ------------------------------------------------------------------ firewall
def _nowin():
    return getattr(subprocess, "CREATE_NO_WINDOW", 0)


def fw_rule_exists():
    try:
        r = subprocess.run(
            ["netsh", "advfirewall", "firewall", "show", "rule", f"name={FW_RULE}"],
            capture_output=True, creationflags=_nowin())
        return r.returncode == 0
    except Exception:
        return False


def _run_admin(cmdline):
    ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", "cmd.exe", f"/c {cmdline}", None, 0)
    return ret > 32


def fw_add_rule():
    exe = sys.executable
    base = (f'netsh advfirewall firewall add rule name="{FW_RULE}" '
            f'program="{exe}" enable=yes action=allow profile=any')
    return _run_admin(f"{base} dir=in & {base} dir=out")


def fw_remove_rule():
    return _run_admin(f'netsh advfirewall firewall delete rule name="{FW_RULE}"')


# ------------------------------------------- integração com o Windows (registo)
def app_command():
    """Comando que volta a lançar este programa."""
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'
    exe = sys.executable
    pw = os.path.join(os.path.dirname(exe), "pythonw.exe")
    if os.path.exists(pw):
        exe = pw
    return f'"{exe}" "{os.path.abspath(__file__)}"'


def autostart_enabled():
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as k:
            winreg.QueryValueEx(k, "AlfTorrent")
            return True
    except Exception:
        return False


def set_autostart(on):
    import winreg
    with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as k:
        if on:
            winreg.SetValueEx(k, "AlfTorrent", 0, winreg.REG_SZ, app_command() + " --tray")
        else:
            try:
                winreg.DeleteValue(k, "AlfTorrent")
            except FileNotFoundError:
                pass


def register_associations():
    """Regista o programa como opção para .torrent e magnet: (sem administrador).
    O Windows 10/11 obriga o utilizador a confirmar o programa por defeito."""
    import winreg

    def setv(path, name, value, kind=winreg.REG_SZ):
        with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_WRITE) as k:
            winreg.SetValueEx(k, name, 0, kind, value)

    cmd = app_command()
    icon = f'"{sys.executable}",0' if getattr(sys, "frozen", False) else resource_path("AlfTorrent.ico")
    cls = r"Software\Classes"

    setv(rf"{cls}\AlfTorrent.torrent", "", tr("Ficheiro Torrent"))
    setv(rf"{cls}\AlfTorrent.torrent\DefaultIcon", "", icon)
    setv(rf"{cls}\AlfTorrent.torrent\shell\open\command", "", f'{cmd} "%1"')
    setv(rf"{cls}\.torrent\OpenWithProgids", "AlfTorrent.torrent", b"", winreg.REG_NONE)

    setv(rf"{cls}\AlfTorrent.magnet", "", "URL:Magnet Link")
    setv(rf"{cls}\AlfTorrent.magnet", "URL Protocol", "")
    setv(rf"{cls}\AlfTorrent.magnet\DefaultIcon", "", icon)
    setv(rf"{cls}\AlfTorrent.magnet\shell\open\command", "", f'{cmd} "%1"')

    cap = r"Software\AlfTorrent\Capabilities"
    setv(cap, "ApplicationName", APP)
    setv(cap, "ApplicationDescription", tr("Cliente BitTorrent"))
    setv(rf"{cap}\FileAssociations", ".torrent", "AlfTorrent.torrent")
    setv(rf"{cap}\UrlAssociations", "magnet", "AlfTorrent.magnet")
    setv(r"Software\RegisteredApplications", "AlfTorrent", cap)


# --------------------------------------------------------- instância única (IPC)
def send_to_running(args):
    """Se já existe uma instância, entrega-lhe os argumentos e devolve True."""
    try:
        with socket.create_connection(("127.0.0.1", IPC_PORT), timeout=1.5) as c:
            c.sendall((json.dumps(args) + "\n").encode("utf-8"))
        return True
    except OSError:
        return False


# ------------------------------------------------------------------ aplicação
class App(ctk.CTk):
    def __init__(self, start_hidden=False, initial_args=None):
        super().__init__()
        self.title(APP)
        self.geometry("1280x820")
        self.minsize(1040, 680)
        self.after(250, lambda: self._try_icon(self))

        self.cfg = load_cfg()
        set_language(resolve_language(self.cfg.get("language", "auto")))
        self.items = {}          # iid -> {"src","save","key","h","w", ...}
        self.counter = 0
        self._order = []
        self._tick = 0
        self.filter, self.sort, self.query = "all", tr("Fila"), ""
        self._view_sig = None
        self.page = "transfers"
        self.spark_d = collections.deque([0] * 40, maxlen=40)
        self.spark_u = collections.deque([0] * 40, maxlen=40)
        self._selftest = None
        self._net_events = {"listen_ok": [], "listen_fail": [], "map_ok": [], "map_err": [], "dht_nodes": None, "ext_ip": None}
        self._watch_seen = {}
        self.cmd_q = queue.Queue()
        self.tray = None

        self.net_blocked = False
        self.bound_ip = None
        self._sched_state = self.sched_allowed()
        net, ok, self.bound_ip = self.net_settings()
        self.net_blocked = not ok
        settings = {
            "download_rate_limit": self.cfg["down_kb"] * 1024,
            "upload_rate_limit": self.cfg["up_kb"] * 1024,
            "active_downloads": self.effective_active(),
            "active_seeds": 10000,       # biblioteca grande: todos a partilhar
            "active_limit": 10000,
            # nunca "dar por concluída" a partilha de um torrent (rácio 2,0 / 24 h por defeito)
            "share_ratio_limit": 1_000_000_000,
            "seed_time_ratio_limit": 1_000_000_000,
            "seed_time_limit": 2_000_000_000,
            "alert_mask": (lt.alert.category_t.status_notification | lt.alert.category_t.error_notification
                           | lt.alert.category_t.port_mapping_notification),
        }
        settings.update(net)
        settings.update(self.enc_settings())
        settings.update(self.perf_settings())
        self.ses = lt.session(settings)
        if self.net_blocked:             # VPN em baixo no arranque: nada sai
            self.ses.pause()
        self.apply_priority()

        self._build_ui()
        self.update_fw_label()
        self.update_net_label()
        self.update_sched_label()

        for t in self.cfg.get("torrents", []):
            self.add_source(t["src"], t["save"], persist=False, quiet=True,
                            paused=t.get("paused", False),
                            dl_kb=t.get("dl_kb", 0), ul_kb=t.get("ul_kb", 0))
        self.reorder_cards(force=True)

        self.start_ipc()
        self.start_tray()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.after(1000, self.refresh)
        self.after(250, self.poll_commands)
        self.after(6000, self.scan_watch)
        self.after(2000, self.check_network)
        self.after(700, self.first_run_firewall)

        if start_hidden and self.tray:
            self.withdraw()
        if initial_args:
            self.after(900, lambda: self.handle_args(initial_args))

    def _try_icon(self, win):
        try:
            win.iconbitmap(resource_path("AlfTorrent.ico"))
        except Exception:
            pass

    # ---- UI
    def _build_ui(self):
        self.configure(fg_color=C["bg"])
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.nav, self.tabw, self.pages = {}, {}, {}
        self._cache = {}
        self._build_sidebar()
        main = ctk.CTkFrame(self, fg_color=C["bg"], corner_radius=0)
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(2, weight=1)
        self._build_topbar(main)
        ctk.CTkFrame(main, height=1, corner_radius=0, fg_color=C["border"]).grid(row=1, column=0, sticky="ew")
        host = ctk.CTkFrame(main, fg_color=C["bg"], corner_radius=0)
        host.grid(row=2, column=0, sticky="nsew")
        host.grid_columnconfigure(0, weight=1)
        host.grid_rowconfigure(0, weight=1)
        self._build_transfers_page(host)
        self._build_geral_page(host)
        self._build_rede_page(host)
        self._build_agenda_page(host)
        ctk.CTkFrame(main, height=1, corner_radius=0, fg_color=C["border"]).grid(row=3, column=0, sticky="ew")
        self._build_statusbar(main)
        self.show_page("transfers")
        self.update_storage()

    # ---- barra lateral
    def _build_sidebar(self):
        side = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=C["side"])
        side.grid(row=0, column=0, sticky="nsew")
        side.grid_propagate(False)
        side.grid_columnconfigure(0, weight=1)
        side.grid_rowconfigure(50, weight=1)

        logo = ctk.CTkFrame(side, fg_color="transparent")
        logo.grid(row=0, column=0, sticky="ew", padx=16, pady=(22, 18))
        try:
            from PIL import Image
            big = Image.open(resource_path("AlfTorrent.ico")).convert("RGBA").resize((72, 72), Image.LANCZOS)
            ctk.CTkLabel(logo, text="", image=ctk.CTkImage(light_image=big, dark_image=big,
                                                          size=(36, 36))).pack(side="left")
        except Exception:
            pass
        ctk.CTkLabel(logo, text="Alf Torrent", font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=C["text"]).pack(side="left", padx=(10, 0))

        r = 1
        r = self._nav_section(side, r, tr("BIBLIOTECA"))
        for key, label, ic in (("all", tr("Transferências"), "list"), ("down", tr("A transferir"), "download"),
                               ("seed", tr("A partilhar"), "upload"), ("paused", tr("Em pausa"), "pause")):
            self._nav_item(side, r, key, label, ic, True, lambda k=key: self.go_filter(k))
            r += 1
        ctk.CTkFrame(side, height=1, corner_radius=0, fg_color=C["border"]).grid(
            row=r, column=0, sticky="ew", padx=16, pady=(14, 4))
        r += 1
        r = self._nav_section(side, r, tr("PREFERÊNCIAS"))
        for key, label, ic in (("geral", tr("Geral"), "sliders"), ("rede", tr("Rede e limites"), "network"),
                               ("agenda", tr("Agendamento"), "clock")):
            self._nav_item(side, r, key, label, ic, False, lambda k=key: self.show_page(k))
            r += 1

        stor = ctk.CTkFrame(side, fg_color="transparent")
        stor.grid(row=51, column=0, sticky="ew", padx=18, pady=(0, 10))
        stor.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(stor, text="", image=icon("drive", C["muted"], 16)).grid(row=0, column=0, padx=(0, 8))
        ctk.CTkLabel(stor, text=tr("Armazenamento"), anchor="w", text_color=C["muted"],
                     font=ctk.CTkFont(size=13)).grid(row=0, column=1, sticky="w")
        ctk.CTkButton(stor, text="", image=icon("folder", C["muted"], 16), width=28, height=28,
                      fg_color="transparent", hover_color=C["hover"],
                      command=self.choose_folder).grid(row=0, column=2)
        self.stor_bar = ctk.CTkProgressBar(stor, height=5, corner_radius=3, fg_color=C["card2"],
                                           progress_color=BLUE)
        self.stor_bar.set(0)
        self.stor_bar.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(10, 8))
        self.stor_text = ctk.CTkLabel(stor, text="", anchor="w", text_color=C["text"], font=ctk.CTkFont(size=12))
        self.stor_text.grid(row=2, column=0, columnspan=3, sticky="w")
        self.stor_path = ctk.CTkLabel(stor, text="", anchor="w", text_color=C["dim"], font=ctk.CTkFont(size=11))
        self.stor_path.grid(row=3, column=0, columnspan=3, sticky="w")

        ctk.CTkFrame(side, height=1, corner_radius=0, fg_color=C["border"]).grid(
            row=52, column=0, sticky="ew", padx=16)
        foot = ctk.CTkFrame(side, fg_color="transparent")
        foot.grid(row=53, column=0, sticky="ew", padx=18, pady=12)
        foot.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(foot, text=f"{APP} v{VERSION}", anchor="w", text_color=C["muted"],
                     font=ctk.CTkFont(size=12)).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(foot, text="", image=icon("info", C["muted"], 16), width=28, height=28,
                      fg_color="transparent", hover_color=C["hover"], command=self.about).grid(row=0, column=1)
        self.lang_toggle = ctk.CTkSegmentedButton(
            foot, values=["Português", "English"], command=self.change_language, height=28,
            fg_color=C["card2"], selected_color=C["blue"], selected_hover_color=C["blue_hi"],
            unselected_color=C["card2"], unselected_hover_color=C["hover"], text_color=C["text"],
            font=ctk.CTkFont(size=12))
        self.lang_toggle.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        self.lang_toggle.set({"pt": "Português", "en": "English"}[i18n.LANG])

    def _nav_section(self, parent, r, text):
        ctk.CTkLabel(parent, text=text, anchor="w", text_color=C["dim"],
                     font=ctk.CTkFont(size=11, weight="bold")).grid(row=r, column=0, sticky="w", padx=22, pady=(8, 6))
        return r + 1

    def _nav_item(self, parent, r, key, text, ic, count, command):
        f = ctk.CTkFrame(parent, height=40, corner_radius=8, fg_color="transparent")
        f.grid(row=r, column=0, sticky="ew", padx=12, pady=2)
        f.grid_propagate(False)
        f.grid_columnconfigure(1, weight=1)
        il = ctk.CTkLabel(f, text="", image=icon(ic, C["muted"], 18))
        il.grid(row=0, column=0, padx=(12, 10), pady=10)
        tl = ctk.CTkLabel(f, text=text, anchor="w", text_color=C["muted"], font=ctk.CTkFont(size=14))
        tl.grid(row=0, column=1, sticky="w")
        widgets = [f, il, tl]
        cl = None
        if count:
            cl = ctk.CTkLabel(f, text="0", width=26, height=20, corner_radius=6, fg_color=C["card2"],
                              text_color=C["muted"], font=ctk.CTkFont(size=11))
            cl.grid(row=0, column=2, padx=(0, 10))
            widgets.append(cl)
        for wdg in widgets:
            wdg.bind("<Button-1>", lambda e, c=command: c())
            wdg.bind("<Enter>", lambda e, k=key: self._nav_hover(k, True))
            wdg.bind("<Leave>", lambda e, k=key: self._nav_hover(k, False))
        self.nav[key] = {"frame": f, "icon": il, "text": tl, "count": cl, "ic": ic, "active": False, "hover": False}

    def _nav_hover(self, key, on):
        n = self.nav[key]
        if n["hover"] != on:
            n["hover"] = on
            self._nav_style(key)

    def _nav_style(self, key):
        n = self.nav[key]
        if n["active"]:
            bg, col, cbg = C["blue_bg"], C["blue"], "#163457"
        else:
            bg, col, cbg = (C["hover"] if n["hover"] else "transparent"), C["muted"], C["card2"]
        n["frame"].configure(fg_color=bg)
        n["icon"].configure(fg_color="transparent", image=icon(n["ic"], col, 18))
        n["text"].configure(fg_color="transparent", text_color=col)
        if n["count"] is not None:
            n["count"].configure(fg_color=cbg, text_color=col)

    def set_nav_active(self, key):
        for k, n in self.nav.items():
            n["active"] = (k == key)
            n["hover"] = False
            self._nav_style(k)

    # ---- barra superior e de estado
    def _build_topbar(self, main):
        bar = ctk.CTkFrame(main, height=58, corner_radius=0, fg_color=C["bg"])
        bar.grid(row=0, column=0, sticky="ew")
        bar.grid_propagate(False)
        inner = ctk.CTkFrame(bar, fg_color="transparent")
        inner.place(x=32, rely=0.5, anchor="w")
        self.crumb_icon = ctk.CTkLabel(inner, text="", image=icon("folder", C["muted"], 16))
        self.crumb_icon.pack(side="left")
        self.crumb_a = ctk.CTkLabel(inner, text=tr("Biblioteca"), text_color=C["muted"], font=ctk.CTkFont(size=13))
        self.crumb_a.pack(side="left", padx=(8, 8))
        ctk.CTkLabel(inner, text="", image=icon("chev-right", C["dim"], 14)).pack(side="left")
        self.crumb_b = ctk.CTkLabel(inner, text=tr("Transferências"), text_color=C["text"], font=ctk.CTkFont(size=13))
        self.crumb_b.pack(side="left", padx=(8, 0))

    def _build_statusbar(self, main):
        bar = ctk.CTkFrame(main, height=38, corner_radius=0, fg_color=C["bg"])
        bar.grid(row=4, column=0, sticky="ew")
        bar.grid_propagate(False)
        bar.grid_columnconfigure(1, weight=1)
        left = ctk.CTkFrame(bar, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w", padx=(32, 0), pady=6)
        self.foot_icon = ctk.CTkLabel(left, text="", image=icon("shield", C["dim"], 15))
        self.foot_icon.pack(side="left")
        self.foot_net = ctk.CTkLabel(left, text="", text_color=C["muted"], font=ctk.CTkFont(size=12))
        self.foot_net.pack(side="left", padx=(8, 0))
        self.flash = ctk.CTkLabel(bar, text="", anchor="w", font=ctk.CTkFont(size=12))
        self.flash.grid(row=0, column=1, sticky="w", padx=22)
        right = ctk.CTkFrame(bar, fg_color="transparent")
        right.grid(row=0, column=2, sticky="e", padx=(0, 32), pady=6)
        ctk.CTkLabel(right, text="", image=icon("folder", C["dim"], 15)).pack(side="left")
        self.foot_path = ctk.CTkLabel(right, text="", text_color=C["muted"], font=ctk.CTkFont(size=12))
        self.foot_path.pack(side="left", padx=(6, 8))
        ctk.CTkLabel(right, text="·", text_color=C["dim"]).pack(side="left")
        self.foot_sched = ctk.CTkLabel(right, text=tr("Sem agendamento"), text_color=C["muted"],
                                       font=ctk.CTkFont(size=12))
        self.foot_sched.pack(side="left", padx=(8, 0))

    # ---- fábricas de controlos
    def _btn(self, parent, text, command, kind="secondary", ic=None, width=None, height=38):
        if kind == "primary":
            fg, hov, tc, bw, bc = C["blue"], C["blue_hi"], "#ffffff", 0, C["blue"]
        elif kind == "danger":
            fg, hov, tc, bw, bc = C["red_bg"], "#3a1a1d", C["red"], 1, "#4a2327"
        else:
            fg, hov, tc, bw, bc = C["card"], C["hover"], C["text"], 1, C["border"]
        img = icon(ic, tc, 16) if ic else None
        w = width or max(96, 8 * len(text) + 40 + (26 if img else 0))
        return ctk.CTkButton(parent, text=text, command=command, image=img, compound="left", width=w,
                             height=height, corner_radius=8, fg_color=fg, hover_color=hov, text_color=tc,
                             border_width=bw, border_color=bc,
                             font=ctk.CTkFont(size=13, weight="bold" if kind == "primary" else "normal"))

    def _entry(self, parent, var, width=140, justify="right", readonly=False, placeholder=""):
        return ctk.CTkEntry(parent, textvariable=var, width=width, height=36, corner_radius=8,
                            fg_color=C["bg"], border_color=C["border"], border_width=1, text_color=C["text"],
                            justify=justify, placeholder_text=placeholder,
                            state="readonly" if readonly else "normal")

    def _switch(self, parent, command):
        return ctk.CTkSwitch(parent, text="", command=command, width=46, progress_color=C["blue"],
                             button_color="#ffffff", button_hover_color="#e6e6e6", fg_color="#2a3448")

    def _menu(self, parent, values, command, width=200):
        return ctk.CTkOptionMenu(parent, values=values, command=command, width=width, height=36,
                                 corner_radius=8, fg_color=C["bg"], button_color=C["card2"],
                                 button_hover_color=C["hover"], text_color=C["text"],
                                 dropdown_fg_color=C["card2"], dropdown_hover_color=C["hover"],
                                 dropdown_text_color=C["text"], font=ctk.CTkFont(size=13),
                                 dynamic_resizing=False)

    def _settings_page(self, host, key, title, subtitle):
        page = ctk.CTkScrollableFrame(host, fg_color=C["bg"], corner_radius=0)
        page.grid_columnconfigure(0, weight=1)
        self.pages[key] = page
        head = ctk.CTkFrame(page, fg_color="transparent")
        head.grid(row=0, column=0, sticky="ew", padx=32, pady=(28, 20))
        ctk.CTkLabel(head, text=title, font=ctk.CTkFont(size=30, weight="bold"), text_color=C["text"]).pack(anchor="w")
        ctk.CTkLabel(head, text=subtitle, font=ctk.CTkFont(size=13), text_color=C["muted"]).pack(anchor="w", pady=(4, 0))
        page._alf_rows = 1
        return page

    def _group(self, page, title):
        g = ctk.CTkFrame(page, corner_radius=12, fg_color=C["card"], border_width=1, border_color=C["border"])
        g.grid(row=page._alf_rows, column=0, sticky="ew", padx=32, pady=(0, 18))
        page._alf_rows += 1
        g.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(g, text=title.upper(), text_color=C["dim"], font=ctk.CTkFont(size=11, weight="bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=22, pady=(18, 0))
        g._alf_r = 1
        return g

    def _srow(self, g, title, desc=None):
        if g._alf_r > 1:
            ctk.CTkFrame(g, height=1, corner_radius=0, fg_color="#19212f").grid(
                row=g._alf_r, column=0, columnspan=2, sticky="ew", padx=22)
            g._alf_r += 1
        r = g._alf_r
        g._alf_r += 1
        left = ctk.CTkFrame(g, fg_color="transparent")
        left.grid(row=r, column=0, sticky="w", padx=(22, 12), pady=14)
        ctk.CTkLabel(left, text=title, anchor="w", text_color=C["text"], font=ctk.CTkFont(size=14)).pack(anchor="w")
        if desc:
            ctk.CTkLabel(left, text=desc, anchor="w", justify="left", wraplength=470, text_color=C["muted"],
                         font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(3, 0))
        right = ctk.CTkFrame(g, fg_color="transparent")
        right.grid(row=r, column=1, sticky="e", padx=(0, 22), pady=14)
        return right

    # ---- página: transferências
    def _build_transfers_page(self, host):
        page = ctk.CTkScrollableFrame(host, fg_color=C["bg"], corner_radius=0)
        page.grid_columnconfigure(0, weight=1)
        self.pages["transfers"] = page
        pad = 32

        head = ctk.CTkFrame(page, fg_color="transparent")
        head.grid(row=0, column=0, sticky="ew", padx=pad, pady=(28, 20))
        head.grid_columnconfigure(0, weight=1)
        tb = ctk.CTkFrame(head, fg_color="transparent")
        tb.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(tb, text=tr("Transferências"), font=ctk.CTkFont(size=30, weight="bold"),
                     text_color=C["text"]).pack(anchor="w")
        ctk.CTkLabel(tb, text=tr("Tudo o que está a chegar. Tudo o que está a partilhar."),
                     font=ctk.CTkFont(size=13), text_color=C["muted"]).pack(anchor="w", pady=(4, 0))
        bt = ctk.CTkFrame(head, fg_color="transparent")
        bt.grid(row=0, column=1, sticky="e")
        self._btn(bt, tr("Pesquisar"), self.open_search, "secondary", "search").pack(side="left", padx=(0, 10))
        self._btn(bt, tr("Link magnet"), self.add_magnet, "secondary", "link").pack(side="left", padx=(0, 10))
        self._btn(bt, tr("Adicionar torrent"), self.add_files, "primary", "plus").pack(side="left")

        stats = ctk.CTkFrame(page, fg_color="transparent")
        stats.grid(row=1, column=0, sticky="ew", padx=pad)
        stats.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="stat")
        self.stat = {}
        self._stat_card(stats, 0, "dl", tr("Velocidade de download"), "download", BLUE, True)
        self._stat_card(stats, 1, "ul", tr("Velocidade de upload"), "upload", GREEN, True)
        self._stat_card(stats, 2, "act", tr("Transferências ativas"), "list", None, False)
        self._stat_card(stats, 3, "tot", tr("Total transferido"), "drive", None, False)

        tabrow = ctk.CTkFrame(page, fg_color="transparent")
        tabrow.grid(row=2, column=0, sticky="ew", padx=pad, pady=(30, 0))
        tabrow.grid_columnconfigure(10, weight=1)
        for i, (key, label) in enumerate((("all", tr("Todas")), ("down", tr("A transferir")),
                                          ("seed", tr("A partilhar")), ("paused", tr("Em pausa")))):
            tf = ctk.CTkFrame(tabrow, fg_color="transparent")
            tf.grid(row=0, column=i, padx=(0, 26), sticky="s")
            inner = ctk.CTkFrame(tf, fg_color="transparent")
            inner.pack(pady=(4, 10))
            lab = ctk.CTkLabel(inner, text=label, text_color=C["muted"], font=ctk.CTkFont(size=14, weight="bold"))
            lab.pack(side="left")
            cnt = ctk.CTkLabel(inner, text="0", width=24, height=20, corner_radius=6, fg_color=C["card2"],
                               text_color=C["muted"], font=ctk.CTkFont(size=11))
            cnt.pack(side="left", padx=(8, 0))
            line = ctk.CTkFrame(tf, width=10, height=2, corner_radius=0, fg_color="transparent")
            line.pack(fill="x")
            for wdg in (tf, inner, lab, cnt):
                wdg.bind("<Button-1>", lambda e, k=key: self.go_filter(k))
            self.tabw[key] = {"label": lab, "count": cnt, "line": line}
        sbox = ctk.CTkFrame(tabrow, corner_radius=8, fg_color=C["card"], border_width=1,
                            border_color=C["border"], height=38)
        sbox.grid(row=0, column=11, sticky="e", pady=(0, 8))
        ctk.CTkLabel(sbox, text="", image=icon("search", C["muted"], 16)).pack(side="left", padx=(12, 0))
        self.search_entry = ctk.CTkEntry(sbox, width=220, height=34, border_width=0, fg_color="transparent",
                                         placeholder_text=tr("Pesquisar transferências…"), text_color=C["text"])
        self.search_entry.pack(side="left", padx=(4, 8))
        self.search_entry.bind("<KeyRelease>", lambda e: self.on_search())

        ctk.CTkFrame(page, height=1, corner_radius=0, fg_color=C["border"]).grid(
            row=3, column=0, sticky="ew", padx=pad)
        sub = ctk.CTkFrame(page, fg_color="transparent")
        sub.grid(row=4, column=0, sticky="ew", padx=pad, pady=(14, 10))
        sub.grid_columnconfigure(0, weight=1)
        self.sub_count = ctk.CTkLabel(sub, text=tr("0 transferências"), text_color=C["muted"], font=ctk.CTkFont(size=13))
        self.sub_count.grid(row=0, column=0, sticky="w")
        self.pause_all_btn = ctk.CTkButton(sub, text=tr("Pausar todas"), image=icon("pause", C["muted"], 16),
                                           compound="left", width=130, height=32, fg_color="transparent",
                                           hover_color=C["hover"], text_color=C["muted"],
                                           font=ctk.CTkFont(size=13), command=self.pause_all)
        self.pause_all_btn.grid(row=0, column=1, padx=(0, 6))
        self.sort_menu = ctk.CTkOptionMenu(sub, values=[tr("Fila"), tr("Mais recentes"), tr("Nome"), tr("Progresso"), tr("Tamanho")],
                                           width=140, height=32, fg_color=C["bg"], button_color=C["bg"],
                                           button_hover_color=C["hover"], text_color=C["muted"],
                                           dropdown_fg_color=C["card2"], dropdown_hover_color=C["hover"],
                                           dropdown_text_color=C["text"], font=ctk.CTkFont(size=13),
                                           command=self.set_sort)
        self.sort_menu.set(tr("Fila"))
        self.sort_menu.grid(row=0, column=2)

        self.list = ctk.CTkFrame(page, fg_color="transparent")
        self.list.grid(row=5, column=0, sticky="ew", padx=pad, pady=(0, 30))
        self.empty = ctk.CTkLabel(self.list, text="", text_color=C["dim"], justify="center",
                                  font=ctk.CTkFont(size=14))

    def _stat_card(self, parent, col, key, label, ic, color, spark):
        card = ctk.CTkFrame(parent, corner_radius=12, fg_color=C["card"], border_width=1,
                            border_color=C["border"], height=132)
        card.grid(row=0, column=col, sticky="ew", padx=(0 if col == 0 else 7, 0 if col == 3 else 7))
        card.grid_propagate(False)
        head = ctk.CTkFrame(card, fg_color="transparent")
        head.grid(row=0, column=0, sticky="w", padx=20, pady=(18, 0))
        ctk.CTkLabel(head, text="", image=icon(ic, color or C["muted"], 16)).pack(side="left")
        ctk.CTkLabel(head, text=label, text_color=C["muted"], font=ctk.CTkFont(size=12)).pack(side="left", padx=(8, 0))
        num = ctk.CTkFrame(card, fg_color="transparent")
        num.grid(row=1, column=0, sticky="w", padx=20, pady=(8, 0))
        big = ctk.CTkLabel(num, text="0", text_color=C["text"], font=ctk.CTkFont(size=29, weight="bold"))
        big.pack(side="left")
        unit = ctk.CTkLabel(num, text="", text_color=C["muted"], font=ctk.CTkFont(size=13))
        unit.pack(side="left", padx=(8, 0), pady=(10, 0))
        subf = ctk.CTkFrame(card, fg_color="transparent")
        subf.grid(row=2, column=0, sticky="w", padx=20, pady=(4, 0))
        sa = ctk.CTkLabel(subf, text="", text_color=C["muted"], font=ctk.CTkFont(size=12))
        sa.pack(side="left")
        sb = ctk.CTkLabel(subf, text="", text_color=C["muted"], font=ctk.CTkFont(size=12))
        sb.pack(side="left", padx=(8, 0))
        cv = None
        if spark:
            cv = tk.Canvas(card, width=70, height=32, bg=C["card"], highlightthickness=0, bd=0)
            cv.place(relx=1.0, y=60, x=-16, anchor="ne")
        self.stat[key] = {"big": big, "unit": unit, "a": sa, "b": sb, "cv": cv, "color": color}

    # ---- páginas de preferências
    def _build_geral_page(self, host):
        page = self._settings_page(host, "geral", tr("Geral"), tr("Pasta de destino, automatização e integração com o Windows."))
        g = self._group(page, tr("Idioma"))
        right = self._srow(g, tr("Idioma da interface"), tr("Muda de imediato."))
        self.lang_menu = self._menu(right, list(LANGUAGES.values()), self.change_language, 220)
        self.lang_menu.pack()
        self.lang_menu.set(LANGUAGES[i18n.LANG])

        g = self._group(page, tr("Destino"))
        self.save_var = ctk.StringVar(value=self.cfg["save_path"])
        right = self._srow(g, tr("Pasta de destino"), tr("Onde as novas transferências são guardadas."))
        self._entry(right, self.save_var, 320, "left", True).pack(side="left", padx=(0, 10))
        self._btn(right, tr("Alterar…"), self.choose_folder, "secondary", "folder").pack(side="left")

        g = self._group(page, tr("Pasta vigiada"))
        right = self._srow(g, tr("Adicionar automaticamente"),
                           tr("Os ficheiros .torrent largados na pasta são adicionados e verificados sozinhos."))
        self.sw_watch = self._switch(right, self.toggle_watch)
        self.sw_watch.pack()
        if self.cfg["watch_enabled"]:
            self.sw_watch.select()
        self.watch_var = ctk.StringVar(value=self.cfg["watch_path"] or tr("Nenhuma pasta escolhida"))
        right = self._srow(g, tr("Pasta a vigiar"))
        self._entry(right, self.watch_var, 320, "left", True, tr("Escolhe uma pasta")).pack(side="left", padx=(0, 10))
        self._btn(right, tr("Escolher…"), self.choose_watch, "secondary", "folder").pack(side="left")

        g = self._group(page, "Windows")
        right = self._srow(g, tr("Iniciar com o Windows"), tr("Arranca já escondido na bandeja."))
        self.sw_auto = self._switch(right, self.toggle_autostart)
        self.sw_auto.pack()
        if autostart_enabled():
            self.sw_auto.select()
        right = self._srow(g, tr("Fechar para a bandeja"), tr("Continua a transferir e a partilhar em segundo plano."))
        self.sw_tray = self._switch(right, self.toggle_tray_close)
        self.sw_tray.pack()
        if self.cfg.get("close_to_tray", True):
            self.sw_tray.select()
        if not HAS_TRAY:
            self.sw_tray.configure(state="disabled")
        right = self._srow(g, tr("Ficheiros .torrent e links magnet"),
                           tr("Regista o programa; o Windows pede-te para o escolheres como predefinido."))
        self._btn(right, tr("Associar…"), self.associate, "secondary").pack()

        g = self._group(page, tr("Desempenho"))
        right = self._srow(g, tr("Modo discreto"),
                           tr("Prioridade baixa, menos ligações em simultâneo e sem atualizar o ecrã quando a "
                           "janela está escondida."))
        self.sw_discreet = self._switch(right, self.toggle_discreet)
        self.sw_discreet.pack()
        if self.cfg.get("discreet", True):
            self.sw_discreet.select()

    def _build_rede_page(self, host):
        page = self._settings_page(host, "rede", tr("Rede e limites"), tr("Velocidade, fila, privacidade e firewall."))
        g = self._group(page, tr("Velocidade e fila"))
        self.down_var = ctk.StringVar(value=str(self.cfg["down_kb"]))
        self.up_var = ctk.StringVar(value=str(self.cfg["up_kb"]))
        self.port_var = ctk.StringVar(value=str(self.cfg["port"]))
        self.max_var = ctk.StringVar(value=str(self.cfg["max_active"]))
        for title, desc, var in ((tr("Limite de download (KB/s)"), tr("0 = sem limite."), self.down_var),
                                 (tr("Limite de upload (KB/s)"), tr("0 = sem limite."), self.up_var),
                                 (tr("Transferências ativas"), tr("As restantes ficam em fila."), self.max_var),
                                 (tr("Porta de ligação"), tr("Entre 1025 e 65535."), self.port_var)):
            self._entry(self._srow(g, title, desc), var, 110, "right").pack()
        right = self._srow(g, tr("Aplicar alterações"), tr("Os limites aplicam-se de imediato."))
        self._btn(right, tr("Aplicar"), self.apply_limits, "primary").pack()

        g = self._group(page, tr("Privacidade"))
        right = self._srow(g, tr("Encriptação do tráfego"),
                           tr("Ajuda contra a limitação de velocidade do operador. «Obrigatória» só liga a peers "
                           "compatíveis. Não esconde o teu IP."))
        self.enc_menu = self._menu(right, [tr(k) for k in ENC_LABELS], self.change_encryption, 180)
        self.enc_menu.pack()
        cur_enc = self.cfg.get("encryption", "enabled")
        self.enc_menu.set(tr(next((k for k, v in ENC_LABELS.items() if v == cur_enc), "Preferida")))
        right = self._srow(g, tr("Ligação à VPN"),
                           tr("Escolhe o adaptador da tua VPN. Se cair, todas as transferências e partilhas são "
                           "bloqueadas até voltar."))
        self.iface_map = {}
        self.iface_menu = self._menu(right, [tr("Todas (sem proteção)")], self.choose_iface, 250)
        self.iface_menu.pack(side="left", padx=(0, 10))
        self._btn(right, tr("Atualizar"), self.refresh_ifaces, "secondary").pack(side="left")
        if psutil is None:
            self.iface_menu.configure(state="disabled")
        right = self._srow(g, tr("Estado da proteção"))
        self.net_label = ctk.CTkLabel(right, text="", font=ctk.CTkFont(size=13))
        self.net_label.pack()
        self.refresh_ifaces()

        g = self._group(page, tr("Diagnóstico de partilha"))
        right = self._srow(g, tr("Testar ligação"),
                           tr("Mostra quantos peers estão ligados, se há ligações de entrada (porta acessível) e "
                           "se alguém está a pedir dados teus."))
        self._btn(right, tr("Testar agora"), self.run_diag, "primary", "search").pack()
        right = self._srow(g, tr("Testar upload (local)"),
                           tr("Um peer de teste local descarrega uns MB de um torrent completo da lista. Prova que o "
                           "programa envia dados e que o ecrã os mostra."))
        self._btn(right, tr("Testar upload"), self.upload_selftest, "secondary", "upload").pack()
        right = self._srow(g, tr("Resultado"))
        self.diag_label = ctk.CTkLabel(right, text=tr("Ainda não testado."), justify="left", wraplength=520,
                                       text_color=C["muted"], font=ctk.CTkFont(size=13))
        self.diag_label.pack(anchor="e")

        g = self._group(page, tr("Firewall do Windows"))
        right = self._srow(g, tr("Regra de entrada e saída"), tr("Permite as ligações deste programa na Firewall."))
        self.fw_label = ctk.CTkLabel(right, text="", font=ctk.CTkFont(size=13))
        self.fw_label.pack(side="left", padx=(0, 14))
        self._btn(right, tr("Criar regra"), self.create_fw, "primary").pack(side="left", padx=(0, 8))
        self._btn(right, tr("Remover"), self.remove_fw, "secondary").pack(side="left")

    def _build_agenda_page(self, host):
        page = self._settings_page(host, "agenda", tr("Agendamento"), tr("Descarrega apenas nas horas que escolheres."))
        g = self._group(page, tr("Horário de transferência"))
        right = self._srow(g, tr("Transferir só neste horário"),
                           tr("Fora do horário os downloads esperam; a partilha (upload) continua."))
        self.sw_sched = self._switch(right, self.save_schedule)
        self.sw_sched.pack()
        if self.cfg["sched_enabled"]:
            self.sw_sched.select()
        self.sched_start_var = ctk.StringVar(value=self.cfg["sched_start"])
        self.sched_end_var = ctk.StringVar(value=self.cfg["sched_end"])
        self._entry(self._srow(g, tr("Início"), tr("Formato HH:MM, por exemplo 01:00.")),
                    self.sched_start_var, 110, "center").pack()
        self._entry(self._srow(g, tr("Fim"), tr("Aceita horários que passam da meia-noite (23:00 às 07:00).")),
                    self.sched_end_var, 110, "center").pack()
        right = self._srow(g, tr("Estado"))
        self.sched_label = ctk.CTkLabel(right, text="", font=ctk.CTkFont(size=13))
        self.sched_label.pack(side="left", padx=(0, 14))
        self._btn(right, tr("Guardar horário"), self.save_schedule, "primary").pack(side="left")

    # ---- navegação, filtros e ordenação
    def show_page(self, name):
        for p in self.pages.values():
            p.grid_remove()
        self.pages[name].grid(row=0, column=0, sticky="nsew")
        self.page = name
        if name == "transfers":
            key, a, b, ic = self.filter, tr("Biblioteca"), tr(FILTER_LABELS[self.filter]), "folder"
        else:
            key, a, b, ic = name, tr("Preferências"), tr(PAGE_LABELS[name]), "sliders"
        self.set_nav_active(key)
        self.crumb_a.configure(text=a)
        self.crumb_b.configure(text=b)
        self.crumb_icon.configure(image=icon(ic, C["muted"], 16))
        if name == "transfers":
            self.set_tab_style()

    def go_filter(self, key):
        self.filter = key
        self.show_page("transfers")
        self.apply_view(force=True)

    def set_tab_style(self):
        for k, t in self.tabw.items():
            on = (k == self.filter)
            t["label"].configure(text_color=C["text"] if on else C["muted"])
            t["line"].configure(fg_color=C["blue"] if on else "transparent")

    def set_sort(self, label):
        self.sort = label
        self.apply_view(force=True)

    def on_search(self):
        self.query = self.search_entry.get().strip().lower()
        self.apply_view(force=True)

    def apply_view(self, force=False):
        q = self.query
        qpos = {iid: i for i, (iid, _) in enumerate(self.ordered_items())}
        rows = []
        for iid, it in self.items.items():
            v = it.get("v") or {"cat": "down", "name": "", "prog": 0, "size": 0}
            if self.filter != "all" and v["cat"] != self.filter:
                continue
            if q and q not in v["name"].lower():
                continue
            rows.append((iid, v))
        s = self.sort
        if s == tr("Mais recentes"):
            rows.sort(key=lambda r: -int(r[0]))
        elif s == tr("Nome"):
            rows.sort(key=lambda r: r[1]["name"].lower())
        elif s == tr("Progresso"):
            rows.sort(key=lambda r: -r[1]["prog"])
        elif s == tr("Tamanho"):
            rows.sort(key=lambda r: -r[1]["size"])
        else:
            rows.sort(key=lambda r: qpos.get(r[0], 0))
        n = len(rows)
        self._cset(self._cache, "subcount", self.sub_count, text=tr("{n} transferência{s}", n=n, s='s' if n != 1 else ''))
        sig = (self.filter, q, s, tuple(r[0] for r in rows))
        if sig == self._view_sig and not force:
            return
        self._view_sig = sig
        for it in self.items.values():
            it["w"]["card"].pack_forget()
        self.empty.pack_forget()
        if not rows:
            msg = (tr("Sem transferências.\nAdiciona um ficheiro .torrent, um link magnet ou usa a pesquisa.")
                   if not self.items else tr("Nenhuma transferência neste filtro."))
            self.empty.configure(text=msg)
            self.empty.pack(pady=70)
        for iid, _ in rows:
            self.items[iid]["w"]["card"].pack(fill="x", pady=(0, 12))

    def _cset(self, cache, key, widget, **kw):
        sig = tuple(sorted((k, str(v)) for k, v in kw.items()))
        if cache.get(key) != sig:
            cache[key] = sig
            widget.configure(**kw)

    def _set(self, it, key, widget, **kw):
        self._cset(it["w"]["cache"], key, widget, **kw)

    def about(self):
        messagebox.showinfo(APP, tr("{app} v{version}\n\nCliente BitTorrent baseado no libtorrent {lt_version}.\n\nDados e definições:\n{data_dir}", app=APP, version=VERSION, lt_version=lt.__version__, data_dir=CFG_DIR))

    def update_storage(self):
        path = self.save_var.get()
        try:
            probe = path if os.path.exists(path) else (os.path.dirname(path) or path)
            u = shutil.disk_usage(probe)
            used = u.total - u.free
            self.stor_bar.set(used / u.total if u.total else 0)
            self.stor_text.configure(text=tr("{used} de {total}", used=fmt_size(used), total=fmt_size(u.total)))
        except Exception:
            self.stor_text.configure(text="—")
        self.stor_path.configure(text=short_path(path, 28))
        self.foot_path.configure(text=short_path(path, 46))

    # ---- ações dos cartões
    def pause_all(self):
        any_running = False
        for it in self.items.values():
            fl = it["h"].flags()
            if not (bool(fl & lt.torrent_flags.paused) and not bool(fl & lt.torrent_flags.auto_managed)):
                any_running = True
        for it in self.items.values():
            h = it["h"]
            if any_running:
                h.unset_flags(lt.torrent_flags.auto_managed)
                h.pause()
            else:
                h.set_flags(lt.torrent_flags.auto_managed)
                h.resume()
        self.persist_list()

    def item_menu(self, iid, widget):
        it = self.items.get(iid)
        if not it:
            return
        m = tk.Menu(self, tearoff=0, bg=C["card2"], fg=C["text"], activebackground=C["blue_bg"],
                    activeforeground=C["text"], bd=0, relief="flat", font=("Segoe UI", 10))
        m.add_command(label=tr("Detalhes e peers…"), command=lambda: self.details_dialog(iid))
        m.add_command(label=tr("Abrir pasta"), command=lambda: self.open_folder(iid))
        m.add_command(label=tr("Limites do torrent…"), command=lambda: self.limits_dialog(iid))
        m.add_separator()
        m.add_command(label=tr("Subir na fila"), command=lambda: self.move_queue(iid, -1))
        m.add_command(label=tr("Descer na fila"), command=lambda: self.move_queue(iid, +1))
        m.add_command(label=tr("Verificar ficheiros"), command=lambda: self.recheck(iid))
        m.add_command(label=tr("Copiar link magnet"), command=lambda: self.copy_magnet(iid))
        m.add_separator()
        m.add_command(label=tr("Remover da lista"), command=lambda: self.remove_item(iid, False))
        m.add_command(label=tr("Remover e apagar ficheiros…"), command=lambda: self.remove_item(iid, True))
        try:
            m.tk_popup(widget.winfo_rootx(), widget.winfo_rooty() + widget.winfo_height())
        finally:
            m.grab_release()

    def run_diag(self):
        self.diag_label.configure(text=tr("A medir…"), text_color=C["muted"])
        try:
            self.ses.post_dht_stats()
        except Exception:
            pass
        self.after(1600, self._finish_diag)

    def _finish_diag(self):
        self.handle_alerts()
        ev = self._net_events
        tot = inc = wants = leech = ntor = 0
        for it in self.items.values():
            try:
                s = it["h"].status()
                peers = it["h"].get_peer_info()
            except Exception:
                continue
            ntor += 1
            for pr in peers:
                tot += 1
                if not (pr.flags & lt.peer_info.local_connection):
                    inc += 1
                if pr.flags & lt.peer_info.remote_interested:
                    wants += 1
            if s.num_incomplete > 0:
                leech += s.num_incomplete
        port = int(self.cfg["port"])
        sev, lines = 0, []

        real = self.ses.listen_port()
        if ev["listen_fail"] and not ev["listen_ok"]:
            lines.append(tr("Escuta: FALHOU ({error}). Outro programa (por exemplo outro cliente de torrents) pode estar a usar a porta {port}.", error=ev['listen_fail'][-1], port=port))
            sev = 2
        elif real and real != port:
            lines.append(tr("Escuta: a porta {port} estava ocupada e o programa usa a {real}. Abre a {real} no router.", port=port, real=real))
            sev = max(sev, 1)
        else:
            lines.append(tr("Escuta: porta {port} ativa.", port=real or port))

        if self.cfg.get("bind_iface"):
            lines.append(tr("Mapeamento automático (UPnP/NAT-PMP): desligado com a VPN; a porta tem de ser aberta "
                         "no fornecedor da VPN."))
        elif ev["map_ok"]:
            lines.append(tr("Mapeamento automático no router: ") + ev["map_ok"][-1] + " ✓")
        elif ev["map_err"]:
            lines.append(tr("Mapeamento automático no router FALHOU: ") + ev["map_err"][-1])
            sev = max(sev, 1)
        else:
            lines.append(tr("Mapeamento automático (UPnP/NAT-PMP): o router não respondeu. Se ninguém se ligar a ti, "
                         "abre a porta manualmente no router."))
            sev = max(sev, 1)

        try:
            running = self.ses.is_dht_running()
        except Exception:
            running = False
        nodes = ev.get("dht_nodes")
        if not running:
            lines.append(tr("DHT: inativo."))
            sev = max(sev, 1)
        elif nodes:
            lines.append(tr("DHT: ativo, {nodes} nós.", nodes=nodes))
        else:
            lines.append(tr("DHT: ativo mas com 0 nós (a ligar-se; se ficar a 0, a tua rede pode estar a bloqueá-lo)."))

        vpn_note = tr(" Com a VPN escolhida o UPnP está desligado.") if self.cfg.get("bind_iface") else ""
        if self.net_blocked:
            lines.append(tr("Bloqueado: a VPN escolhida está em baixo."))
            sev = 2
        elif ntor == 0:
            lines.append(tr("Não há torrents na lista."))
        elif tot == 0:
            lines.append(tr("Sem peers ligados em {count} torrent(s): ninguém está ligado a ti neste momento. Vê os trackers em «Detalhes e peers…».{vpn_note}", count=ntor, vpn_note=vpn_note))
            sev = max(sev, 1)
        elif inc == 0:
            lines.append(tr("Peers ligados: {tot}, mas nenhum se ligou a ti: só tu te ligas a eles. A porta {port} parece fechada (router, firewall ou VPN) e isso reduz muito o upload.{vpn_note}", tot=tot, port=real or port, vpn_note=vpn_note))
            sev = max(sev, 1)
        else:
            lines.append(tr("Peers ligados: {tot}, dos quais {incoming} se ligaram a ti (porta acessível). A pedir dados teus: {wants}. Leechers no enxame segundo os trackers: {leech}.", tot=tot, incoming=inc, wants=wants, leech=leech))
        ext = ev.get("ext_ip")
        if ext:
            try:
                cg = ipaddress.ip_address(ext) in ipaddress.ip_network("100.64.0.0/10")
            except ValueError:
                cg = False
            if cg:
                lines.append(tr("O teu IP público ({ext}) está na gama de CGNAT: o operador partilha o IP e não é possível abrir portas (só com IP público dedicado ou VPN com redirecionamento).", ext=ext))
                sev = max(sev, 1)
            else:
                lines.append(tr("Endereço público visto pelos peers: {ext}. Se for diferente do IP WAN que o teu router mostra, o operador usa CGNAT e não dá para abrir portas.", ext=ext))
        lip = local_ip()
        if lip and not self.cfg.get("bind_iface") and (inc == 0 or sev >= 1):
            lines.append(tr("Para abrir a porta: no router, redireciona TCP e UDP {port} para {ip} (o IP deste PC) e reserva esse IP para o PC.", port=real or port, ip=lip))
        lines.append(tr("(Medição do momento: repete se ninguém estava a descarregar.)"))
        self.diag_label.configure(text="\n".join(lines), text_color=[GREEN, AMBER, RED][sev])

    def upload_selftest(self):
        """Peer de teste local descarrega uns MB de um torrent completo: prova o envio e o ecrã."""
        if self._selftest:
            return
        if self.net_blocked:
            self.diag_label.configure(text=tr("A VPN escolhida está em baixo: tudo bloqueado."), text_color=RED)
            return
        cand = None
        for it in self.items.values():
            try:
                s = it["h"].status()
                if int(s.state) in (4, 5) and s.has_metadata and it["h"].torrent_file() is not None:
                    cand = it
                    break
            except Exception:
                pass
        if cand is None:
            self.diag_label.configure(text=tr("Precisas de pelo menos um torrent completo na lista para este teste."),
                                      text_color=AMBER)
            return
        port = self.ses.listen_port()
        if not port:
            self.diag_label.configure(text=tr("O programa não está a escutar em nenhuma porta."), text_color=RED)
            return
        tmp = tempfile.mkdtemp(prefix="alft_teste_")
        try:
            ts = lt.session({"listen_interfaces": "127.0.0.1:0", "enable_dht": False, "enable_lsd": False,
                             "enable_upnp": False, "enable_natpmp": False,
                             "download_rate_limit": 1_000_000, "ignore_limits_on_local_network": False})
            p = lt.add_torrent_params()
            p.ti = cand["h"].torrent_file()
            p.save_path = tmp
            th = ts.add_torrent(p)
            th.connect_peer((self.bound_ip or "127.0.0.1", port))
        except Exception as e:
            shutil.rmtree(tmp, ignore_errors=True)
            self.diag_label.configure(text=tr("Não foi possível preparar o teste: {error}", error=e), text_color=RED)
            return
        self._selftest = {"ts": ts, "th": th, "tmp": tmp, "cand": cand, "seen": [],
                          "up0": cand["h"].status().total_payload_upload}
        self.diag_label.configure(text=tr("A testar o upload (7 s)…"), text_color=C["muted"])
        for ms in (2500, 4500, 6500):
            self.after(ms, self._selftest_sample)
        self.after(7200, self._selftest_finish)

    def _selftest_sample(self):
        st = self._selftest
        if st:
            try:
                st["seen"].append(st["cand"]["w"]["ul"].cget("text").strip())
            except Exception:
                pass

    def _selftest_finish(self):
        st, self._selftest = self._selftest, None
        if not st:
            return
        seen = [t for t in st["seen"] if not t.startswith("0,0")]
        try:
            up = st["cand"]["h"].status().total_payload_upload - st["up0"]
            ts_stat = st["th"].status()
            peers = ts_stat.num_peers
        except Exception:
            up = peers = 0
        try:
            st["ts"].remove_torrent(st["th"], lt.options_t.delete_files)
        except Exception:
            pass
        tmp = st["tmp"]
        st.clear()
        shutil.rmtree(tmp, ignore_errors=True)
        self.after(4000, lambda: shutil.rmtree(tmp, ignore_errors=True))
        self._selftest_result(up, peers, seen)

    def _selftest_result(self, up, peers, seen):
        if up > 0 and seen:
            txt, col = (tr("✓ O programa enviou {size} para um peer de teste e o cartão mostrou ↑ {speed}. O envio e o ecrã funcionam; se não há upload real, a causa está na rede (porta, router, trackers ou falta de leechers). Usa «Testar agora» para ver qual.", size=fmt_size(up), speed=seen[-1])), GREEN
        elif up > 0:
            txt, col = (tr("O programa enviou {size}, mas o cartão não mostrou velocidade de upload: defeito de visualização.", size=fmt_size(up))), RED
        elif peers == 0:
            txt, col = (tr("O peer de teste não conseguiu ligar-se ao programa. A escuta local está com problemas "
                        "(outro programa na porta, firewall ou VPN a bloquear).")), RED
        else:
            txt, col = (tr("O peer de teste ligou-se mas não recebeu dados. Verifica se o torrent está mesmo completo "
                        "(«Verificar ficheiros» no menu do cartão).")), AMBER
        self.diag_label.configure(text=txt, text_color=col)

    def _diagnose(self, s, peers, inc, wants):
        if self.net_blocked:
            return tr("Tudo bloqueado: a VPN escolhida está em baixo.")
        if s.progress < 1:
            return tr("Este torrent ainda não está completo; está a transferir.")
        if not peers:
            return tr("Sem peers ligados: ninguém está a pedir dados teus neste momento.")
        if wants == 0 and s.num_incomplete == 0:
            return tr("Os peers ligados são seeds e, segundo o tracker, não há leechers: sem leechers não há upload.")
        if wants == 0:
            return tr("Peers ligados: {peers}, mas nenhum está a pedir dados teus.", peers=len(peers))
        if inc == 0:
            return (tr("A pedir dados: {wants}, mas todas as ligações foram iniciadas por ti; nenhuma de entrada. A porta {port} pode estar fechada.", wants=wants, port=self.cfg['port']))
        return tr("A pedir dados: {wants}. Upload ativo: {up_speed}.", wants=wants, up_speed=fmt_speed(s.upload_payload_rate))

    def _details_text(self, it):
        h = it["h"]
        try:
            s = h.status()
            peers = h.get_peer_info()
            trackers = h.trackers()
        except Exception as e:
            return tr("Não foi possível ler o estado: {error}", error=e)
        inc = sum(1 for pr in peers if not (pr.flags & lt.peer_info.local_connection))
        wants = sum(1 for pr in peers if pr.flags & lt.peer_info.remote_interested)
        try:
            ih = str(s.info_hashes.get_best())
        except Exception:
            ih = "—"
        L = [tr("RESUMO"), "  " + self._diagnose(s, peers, inc, wants), "",
             tr("ESTADO"),
             tr("  Progresso: {progress:.1f}%   ·   Tamanho: {size}", progress=s.progress * 100, size=fmt_size(s.total_wanted)),
             tr("  Partilhado no total: {uploaded}   ·   Descarregado no total: {downloaded}", uploaded=fmt_size(s.all_time_upload), downloaded=fmt_size(s.all_time_download)),
             tr("  Velocidade (dados): ↓ {down_speed}   ↑ {up_speed}", down_speed=fmt_speed(s.download_payload_rate), up_speed=fmt_speed(s.upload_payload_rate)),
             tr("  Pasta: {path}", path=it['save']), f"  Hash: {ih}", "",
             tr("ENXAME"),
             tr("  Peers ligados: {peers} (conhecidos: {known})   ·   seeds ligados: {seeds}", peers=len(peers), known=s.list_peers, seeds=s.num_seeds),
             tr("  Ligações recebidas (porta acessível): {incoming}   ·   iniciadas por ti: {outgoing}", incoming=inc, outgoing=len(peers) - inc),
             tr("  A pedir dados teus: {wants}", wants=wants)]
        if s.num_complete >= 0 or s.num_incomplete >= 0:
            L.append(tr("  Segundo o tracker: {seeds} seeds, {leechers} leechers", seeds=max(s.num_complete, 0), leechers=max(s.num_incomplete, 0)))
        else:
            L.append(tr("  Segundo o tracker: desconhecido (ainda sem resposta)"))
        L += ["", tr("TRACKERS")]
        if not trackers:
            L.append(tr("  Sem trackers (só DHT e peers conhecidos)."))
        for t in trackers:
            eps = t.get("endpoints") or []
            if not eps:
                L.append(tr("  {url}\n     sem resposta ainda", url=short(t.get('url', '?'), 70)))
                continue
            e = eps[0]
            msg = e.get("message") or (tr("a contactar…") if e.get("updating") else tr("sem mensagem"))
            sc, si = e.get("scrape_complete", -1), e.get("scrape_incomplete", -1)
            sw = tr("   ·   {seeds} seeds, {leechers} leechers", seeds=max(sc, 0), leechers=max(si, 0)) if (sc >= 0 or si >= 0) else ""
            L.append(tr("  {url}\n     {msg}{sw}   ·   falhas: {fails}", url=short(t.get('url', '?'), 70), msg=msg, sw=sw, fails=e.get('fails', 0)))
        L += ["", tr("PEERS LIGADOS")]
        if not peers:
            L.append(tr("  Nenhum."))
        for pr in sorted(peers, key=lambda x: -x.payload_up_speed)[:40]:
            cli = pr.client.decode("utf-8", "replace") if isinstance(pr.client, bytes) else str(pr.client)
            origem = tr("saída") if (pr.flags & lt.peer_info.local_connection) else tr("entrada")
            quer = tr("pede dados") if (pr.flags & lt.peer_info.remote_interested) else ""
            L.append(f"  {str(pr.ip[0]) + ':' + str(pr.ip[1]):<24} {short(cli, 20):<20} "
                     f"↓ {fmt_speed(pr.payload_down_speed):>11}  ↑ {fmt_speed(pr.payload_up_speed):>11}  "
                     f"{origem:<8}{quer}")
        return "\n".join(L)

    def details_dialog(self, iid):
        it = self.items.get(iid)
        if not it:
            return
        win = ctk.CTkToplevel(self, fg_color=C["bg"])
        win.title(tr("Detalhes do torrent"))
        win.geometry("940x640")
        win.transient(self)
        win.after(250, lambda: self._try_icon(win))
        try:
            nm = it["h"].status().name or "Torrent"
        except Exception:
            nm = "Torrent"
        ctk.CTkLabel(win, text=short(nm, 80), font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=C["text"]).pack(anchor="w", padx=22, pady=(18, 2))
        ctk.CTkLabel(win, text=tr("Atualiza a cada segundo. Mostra só dados de ficheiros (sem tráfego de protocolo)."),
                     text_color=C["muted"]).pack(anchor="w", padx=22)
        tb = ctk.CTkTextbox(win, fg_color=C["card"], text_color=C["text"], border_width=1,
                            border_color=C["border"], corner_radius=10, wrap="none", font=("Consolas", 12))
        tb.pack(fill="both", expand=True, padx=22, pady=16)

        def tick():
            try:
                if not win.winfo_exists() or iid not in self.items:
                    return
                pos = tb.yview()[0]
                tb.configure(state="normal")
                tb.delete("1.0", "end")
                tb.insert("1.0", self._details_text(it))
                tb.configure(state="disabled")
                tb.yview_moveto(pos)
                win.after(1000, tick)
            except Exception:
                pass
        tick()

    def recheck(self, iid):
        it = self.items.get(iid)
        if it:
            try:
                it["h"].force_recheck()
                self.show_flash(tr("A verificar ficheiros…"), BLUE)
            except Exception:
                pass

    def copy_magnet(self, iid):
        it = self.items.get(iid)
        if not it:
            return
        try:
            self.clipboard_clear()
            self.clipboard_append(lt.make_magnet_uri(it["h"]))
            self.show_flash(tr("✓ Link magnet copiado"))
        except Exception:
            self.show_flash(tr("Não foi possível copiar o link"), RED)

    def show_flash(self, text, color=GREEN):
        self.flash.configure(text=text, text_color=color)
        self.after(3500, lambda: self.flash.configure(text=""))

    # ---- helpers
    # ---- rede: encriptação, ligação à VPN, desempenho
    def net_settings(self):
        """(definições, ligação_ok, ip) conforme o adaptador de rede escolhido."""
        port = int(self.cfg["port"])
        name = self.cfg.get("bind_iface", "")
        if not name:
            return ({"listen_interfaces": f"0.0.0.0:{port},[::]:{port}", "outgoing_interfaces": "",
                     "enable_upnp": True, "enable_natpmp": True}, True, None)
        ip = iface_ipv4(name)
        if ip:
            return ({"listen_interfaces": f"{ip}:{port}", "outgoing_interfaces": ip,
                     "enable_upnp": False, "enable_natpmp": False}, True, ip)
        return ({"listen_interfaces": f"127.0.0.1:{port}", "outgoing_interfaces": "127.0.0.1",
                 "enable_upnp": False, "enable_natpmp": False}, False, None)

    def enc_settings(self):
        pol = {"disabled": lt.enc_policy.pe_disabled, "enabled": lt.enc_policy.pe_enabled,
               "forced": lt.enc_policy.pe_forced}.get(self.cfg.get("encryption", "enabled"),
                                                       lt.enc_policy.pe_enabled)
        return {"out_enc_policy": int(pol), "in_enc_policy": int(pol),
                "allowed_enc_level": int(lt.enc_level.pe_both), "prefer_rc4": False}

    def perf_settings(self):
        if self.cfg.get("discreet", True):
            return {"connections_limit": 120, "aio_threads": 4}
        return {"connections_limit": 200, "aio_threads": 10}

    def apply_priority(self):
        try:
            k = ctypes.windll.kernel32
            k.GetCurrentProcess.restype = ctypes.c_void_p
            k.SetPriorityClass.argtypes = [ctypes.c_void_p, ctypes.c_uint]
            k.SetPriorityClass(k.GetCurrentProcess(), 0x4000 if self.cfg.get("discreet", True) else 0x20)
        except Exception:
            pass

    def toggle_discreet(self):
        self.cfg["discreet"] = bool(self.sw_discreet.get())
        save_cfg(self.cfg)
        self.ses.apply_settings(self.perf_settings())
        self.apply_priority()

    def change_encryption(self, label):
        self.cfg["encryption"] = {tr(k): v for k, v in ENC_LABELS.items()}.get(label, "enabled")
        save_cfg(self.cfg)
        self.ses.apply_settings(self.enc_settings())
        self.show_flash(tr("✓ Encriptação: {mode}", mode=label.lower()))

    def rebind(self):
        """Aplica a ligação ao adaptador escolhido; se desapareceu, bloqueia tudo."""
        s, ok, ip = self.net_settings()
        if not ok and not self.net_blocked:
            self.net_blocked = True
            self.ses.pause()
        self.ses.apply_settings(s)
        self.bound_ip = ip
        if ok and self.net_blocked:
            self.net_blocked = False
            self.ses.resume()
        self.update_net_label()

    def check_network(self):
        try:
            name = self.cfg.get("bind_iface", "")
            if name:
                ip = iface_ipv4(name)
                if ip is None and not self.net_blocked:
                    self.rebind()
                    self.notify(tr("Ligação VPN perdida: transferências bloqueadas."))
                elif ip is not None and (self.net_blocked or ip != self.bound_ip):
                    was_blocked = self.net_blocked
                    self.rebind()
                    if was_blocked:
                        self.notify(tr("VPN reposta: transferências retomadas."))
        except Exception:
            pass
        finally:
            self.after(2000, self.check_network)

    def update_net_label(self):
        name = self.cfg.get("bind_iface", "")
        if not name:
            txt, col, ic, icol, foot = (tr("●  Sem proteção: usa todas as ligações"), AMBER, "shield", C["dim"],
                                        tr("Ligação direta (sem VPN)"))
        elif self.net_blocked:
            txt, col, ic, icol, foot = (tr("●  «{name}» em baixo: tudo bloqueado", name=name), RED, "shield", RED,
                                        tr("VPN em baixo: tudo bloqueado"))
        else:
            txt, col, ic, icol, foot = (tr("●  Protegido: só via «{name}»", name=name), GREEN, "shield-check", GREEN,
                                        tr("Protegido via «{name}»", name=name))
        self.net_label.configure(text=txt, text_color=col)
        self.foot_icon.configure(image=icon(ic, icol, 15))
        self.foot_net.configure(text=foot, text_color=col if name else C["muted"])

    def refresh_ifaces(self):
        self.iface_map = {tr("Todas (sem proteção)"): ""}
        for name, ip in list_ifaces():
            self.iface_map[f"{name} — {ip}"] = name
        cur = self.cfg.get("bind_iface", "")
        if cur and cur not in self.iface_map.values():
            self.iface_map[tr("{name} — (desligada)", name=cur)] = cur
        self.iface_menu.configure(values=list(self.iface_map))
        for label, name in self.iface_map.items():
            if name == cur:
                self.iface_menu.set(label)
                break

    def choose_iface(self, label):
        name = self.iface_map.get(label, "")
        if name and iface_ipv4(name) is None and not messagebox.askyesno(
                APP, tr("O adaptador «{name}» está desligado.\n\nAs transferências ficam bloqueadas até ele voltar. Continuar?", name=name)):
            self.refresh_ifaces()
            return
        self.cfg["bind_iface"] = name
        save_cfg(self.cfg)
        self.rebind()

    # ---- agendamento
    def sched_allowed(self):
        if not self.cfg.get("sched_enabled"):
            return True
        try:
            a, b = parse_hm(self.cfg["sched_start"]), parse_hm(self.cfg["sched_end"])
        except Exception:
            return True
        t = time.localtime()
        return in_window(t.tm_hour * 60 + t.tm_min, a, b)

    def effective_active(self):
        return max(1, int(self.cfg["max_active"])) if self._sched_state else 0

    def apply_schedule(self, force=False):
        allowed = self.sched_allowed()
        if force or allowed != self._sched_state:
            self._sched_state = allowed
            self.ses.apply_settings({"active_downloads": self.effective_active()})
            self.update_sched_label()

    def update_sched_label(self):
        a, b = self.cfg.get("sched_start", ""), self.cfg.get("sched_end", "")
        if not self.cfg.get("sched_enabled"):
            txt, col, foot, fcol = tr("●  Sem agendamento"), C["muted"], tr("Sem agendamento"), C["muted"]
        elif self._sched_state:
            txt, col, foot, fcol = tr("●  Dentro do horário: a transferir"), GREEN, tr("Horário {start}–{end}", start=a, end=b), GREEN
        else:
            txt, col, foot, fcol = (tr("●  Fora do horário: downloads em espera"), AMBER,
                                    tr("Fora do horário ({start}–{end})", start=a, end=b), AMBER)
        self.sched_label.configure(text=txt, text_color=col)
        self.foot_sched.configure(text=foot, text_color=fcol)

    def save_schedule(self):
        on = bool(self.sw_sched.get())
        try:
            a, b = parse_hm(self.sched_start_var.get()), parse_hm(self.sched_end_var.get())
        except Exception:
            self.show_flash(tr("Horário inválido (usa HH:MM, ex. 01:30)"), RED)
            if on:
                self.sw_sched.deselect()
                on = False
            self.cfg["sched_enabled"] = False
            save_cfg(self.cfg)
            self.apply_schedule(force=True)
            return
        self.cfg.update(sched_enabled=on, sched_start=fmt_hm(a), sched_end=fmt_hm(b))
        self.sched_start_var.set(fmt_hm(a))
        self.sched_end_var.set(fmt_hm(b))
        save_cfg(self.cfg)
        self.apply_schedule(force=True)
        self.show_flash(tr("✓ Horário guardado"))

    # ---- pesquisa (Internet Archive)
    def open_search(self):
        win = ctk.CTkToplevel(self, fg_color=C["bg"])
        win.title(tr("Pesquisar torrents"))
        win.geometry("780x580")
        win.transient(self)
        win.after(250, lambda: self._try_icon(win))
        bold = ctk.CTkFont(size=14, weight="bold")

        ctk.CTkLabel(win, text=tr("Pesquisar no Internet Archive"), font=ctk.CTkFont(size=18, weight="bold")).pack(
            anchor="w", padx=18, pady=(16, 0))
        ctk.CTkLabel(win, text=tr("Filmes, música, software e livros de domínio público ou de licença livre. "
                               "Sem anúncios nem pop-ups."), text_color="gray60").pack(anchor="w", padx=18)
        top = ctk.CTkFrame(win, fg_color="transparent")
        top.pack(fill="x", padx=18, pady=10)
        entry = ctk.CTkEntry(top, placeholder_text=tr("O que procuras?"))
        entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        kind = ctk.CTkOptionMenu(top, values=[tr(k) for k in SEARCH_KINDS], width=140)
        kind.pack(side="left", padx=(0, 8))
        go_btn = ctk.CTkButton(top, text=tr("Pesquisar"), width=100)
        go_btn.pack(side="left")
        status = ctk.CTkLabel(win, text="", text_color="gray60", anchor="w")
        status.pack(fill="x", padx=18)
        results = ctk.CTkScrollableFrame(win, fg_color=C["bg"])
        results.pack(fill="both", expand=True, padx=18, pady=(4, 16))

        q = queue.Queue()
        buttons = {}

        def setb(ident, **kw):
            try:
                buttons[ident].configure(**kw)
            except Exception:
                pass

        def go(event=None):
            term = entry.get().strip()
            if not term:
                return
            status.configure(text=tr("A pesquisar…"), text_color="gray60")
            for w in results.winfo_children():
                w.destroy()
            buttons.clear()
            mt = {tr(k): v for k, v in SEARCH_KINDS.items()}[kind.get()]

            def work():
                try:
                    q.put(("results", ia_search(term, mt)))
                except Exception as e:
                    q.put(("error", str(e)))
            threading.Thread(target=work, daemon=True).start()

        def render(docs):
            if not docs:
                status.configure(text=tr("Sem resultados."), text_color="gray60")
                return
            status.configure(text=tr("{count} resultados (os mais descarregados primeiro)", count=len(docs)),
                             text_color="gray60")
            for d in docs:
                row = ctk.CTkFrame(results, corner_radius=10, fg_color=C["card"], border_width=1,
                                   border_color=C["border"])
                row.pack(fill="x", pady=4, padx=2)
                row.grid_columnconfigure(0, weight=1)
                ctk.CTkLabel(row, text=short(d["title"], 70), anchor="w", font=bold).grid(
                    row=0, column=0, sticky="ew", padx=12, pady=(8, 0))
                ctk.CTkLabel(row, text=tr("{size}   ·   {downloads} descargas   ·   {id}", size=fmt_size(d['size']), downloads=d['downloads'], id=d['id']),
                             anchor="w", text_color="gray60", font=ctk.CTkFont(size=12)).grid(
                    row=1, column=0, sticky="ew", padx=12, pady=(0, 8))
                b = ctk.CTkButton(row, text=tr("Adicionar"), width=96, command=lambda i=d["id"]: add(i))
                b.grid(row=0, column=1, rowspan=2, padx=12)
                buttons[d["id"]] = b

        def add(ident):
            setb(ident, text=tr("A obter…"), state="disabled")

            def work():
                try:
                    url = f"https://archive.org/download/{ident}/{ident}_archive.torrent"
                    q.put(("torrent", ident, http_get(url)))
                except Exception:
                    q.put(("torrent_err", ident))
            threading.Thread(target=work, daemon=True).start()

        def poll():
            try:
                while True:
                    m = q.get_nowait()
                    if m[0] == "results":
                        render(m[1])
                    elif m[0] == "error":
                        status.configure(text=tr("Erro na pesquisa: {error}", error=short(m[1], 80)), text_color=RED)
                    elif m[0] == "torrent":
                        res = self.add_source(self.store_torrent_bytes(m[2]), self.save_var.get(), quiet=True)
                        setb(m[1], text={"ok": tr("✓ Adicionado"), "dup": tr("Já existe")}.get(res, tr("Erro")))
                    elif m[0] == "torrent_err":
                        setb(m[1], text=tr("Sem torrent"), state="disabled")
            except queue.Empty:
                pass
            try:
                if win.winfo_exists():
                    win.after(150, poll)
            except Exception:
                pass

        go_btn.configure(command=go)
        entry.bind("<Return>", go)
        win.after(200, entry.focus)
        poll()

    def choose_folder(self):
        d = filedialog.askdirectory(initialdir=self.save_var.get() or None)
        if d:
            self.save_var.set(os.path.normpath(d))
            self.cfg["save_path"] = os.path.normpath(d)
            save_cfg(self.cfg)
            self.update_storage()

    def apply_limits(self):
        try:
            down = max(0, int(self.down_var.get()))
            up = max(0, int(self.up_var.get()))
            port = int(self.port_var.get())
            active = int(self.max_var.get())
            if not 1025 <= port <= 65535 or not 1 <= active <= 50:
                raise ValueError
        except ValueError:
            self.show_flash(tr("Valores inválidos (porta 1025–65535, ativas 1–50)"), RED)
            return
        port_changed = port != self.cfg["port"]
        self.cfg.update(down_kb=down, up_kb=up, port=port, max_active=active)
        save_cfg(self.cfg)
        s = {"download_rate_limit": down * 1024, "upload_rate_limit": up * 1024,
             "active_downloads": self.effective_active()}
        self.ses.apply_settings(s)
        if port_changed:
            self.rebind()
        self.show_flash(tr("✓ Aplicado"))

    # ---- biblioteca: onde procurar ficheiros já existentes
    def library_roots(self):
        default = self.save_var.get()
        return [default] + [r for r in self.cfg.get("roots", []) if r != default and os.path.isdir(r)]

    def remember_root(self, d):
        roots = self.cfg.setdefault("roots", [])
        if d not in roots:
            roots.append(d)
            save_cfg(self.cfg)

    def _find_existing(self, name, roots):
        for r in roots:
            if os.path.exists(os.path.join(r, name)):
                return r
        return None

    def _ask_existing(self, name, roots):
        dest = roots[0]
        r = messagebox.askyesnocancel(
            APP, tr("Não encontrei «{name}» em:\n{dest}\n\nJá tens estes ficheiros noutra pasta?\n\nSim – escolher a pasta onde estão (só valida e partilha)\nNão – transferir para a pasta de destino\nCancelar – não adicionar", name=name, dest=dest))
        if r is None:
            return None
        if not r:
            return dest
        d = filedialog.askdirectory(title=tr("Pasta onde estão os ficheiros de {name}", name=name))
        if not d:
            return None
        d = os.path.normpath(d)
        if os.path.basename(d) == name:          # escolheu a própria pasta do filme
            d = os.path.dirname(d)
        if os.path.exists(os.path.join(d, name)):
            roots.append(d)                      # reutiliza no resto do lote
            self.remember_root(d)                # e nas próximas vezes
            return d
        if messagebox.askyesno(
                APP, tr("Não encontrei «{name}» nessa pasta (o nome tem de ser igual ao do torrent).\n\nAdicionar mesmo assim? Os ficheiros serão transferidos de novo.", name=name)):
            return d
        return None

    # ---- adicionar
    def add_files(self):
        files = filedialog.askopenfilenames(title=tr("Escolher ficheiros .torrent"),
                                            filetypes=[("Torrent", "*.torrent")])
        if files:
            self.add_torrent_paths(files, interactive=True)

    def add_torrent_paths(self, files, interactive=True):
        roots = self.library_roots()
        for f in files:
            self.add_torrent_file(f, roots, interactive)

    def add_torrent_file(self, f, roots, interactive=True):
        """Devolve 'ok', 'dup', 'invalid', 'cancel' ou 'error'."""
        try:
            ti = lt.torrent_info(f)
            name = ti.name()
        except Exception as e:
            if interactive:
                messagebox.showerror(APP, tr("Ficheiro .torrent inválido:\n{file}\n{error}", file=f, error=e))
            return "invalid"
        if self._is_duplicate(ti):
            if interactive:
                self.show_flash(tr("Já existe: {name}", name=short(name, 40)), AMBER)
            return "dup"
        save = self._find_existing(name, roots)
        if save is not None:
            if interactive:
                self.show_flash(tr("✓ Ficheiros encontrados, a verificar…"))
        elif interactive:
            save = self._ask_existing(name, roots)
            if save is None:
                return "cancel"
        else:
            save = roots[0]
        return self.add_source(self.store_torrent(f), save, quiet=not interactive)

    def store_torrent(self, f):
        """Guarda uma cópia do .torrent na pasta da app (não depende do original)."""
        try:
            with open(f, "rb") as fh:
                data = fh.read()
            os.makedirs(TORRENTS_DIR, exist_ok=True)
            dest = os.path.join(TORRENTS_DIR, hashlib.sha1(data).hexdigest() + ".torrent")
            if not os.path.exists(dest):
                with open(dest, "wb") as out:
                    out.write(data)
            return dest
        except OSError:
            return f

    def store_torrent_bytes(self, data):
        os.makedirs(TORRENTS_DIR, exist_ok=True)
        dest = os.path.join(TORRENTS_DIR, hashlib.sha1(data).hexdigest() + ".torrent")
        if not os.path.exists(dest):
            with open(dest, "wb") as out:
                out.write(data)
        return dest

    def add_magnet(self):
        m = ctk.CTkInputDialog(text=tr("Cola o link magnet:"), title=APP).get_input()
        if not m:
            return
        m = m.strip()
        if m.startswith("magnet:"):
            self.add_source(m, self.save_var.get())
        else:
            messagebox.showerror(APP, tr("Link magnet inválido."))

    def _is_duplicate(self, ti):
        try:
            return self.ses.find_torrent(ti.info_hashes().get_best()).is_valid()
        except Exception:
            return False

    def add_source(self, src, save, persist=True, quiet=False, paused=False, dl_kb=0, ul_kb=0):
        """Devolve 'ok', 'dup' ou 'error'."""
        key = hashlib.sha1(src.encode("utf-8")).hexdigest()
        rpath = os.path.join(RESUME_DIR, key + ".fastresume")
        try:
            p = None
            if os.path.exists(rpath):                # retoma rápida: evita reverificar tudo
                try:
                    with open(rpath, "rb") as f:
                        p = lt.read_resume_data(f.read())
                    if not src.startswith("magnet:"):
                        p.ti = lt.torrent_info(src)
                except Exception:
                    p = None
            if p is None:
                if src.startswith("magnet:"):
                    p = lt.parse_magnet_uri(src)
                else:
                    p = lt.add_torrent_params()
                    p.ti = lt.torrent_info(src)
            p.save_path = save
            try:
                ih = p.ti.info_hashes().get_best() if p.ti is not None else p.info_hashes.get_best()
                if self.ses.find_torrent(ih).is_valid():
                    if not quiet:
                        self.show_flash(tr("Já existe na lista"), AMBER)
                    return "dup"
            except Exception:
                pass
            h = self.ses.add_torrent(p)
        except Exception as e:
            if not quiet:
                messagebox.showerror(APP, tr("Não foi possível adicionar:\n{error}", error=e))
            return "error"

        if paused:
            h.unset_flags(lt.torrent_flags.auto_managed)
            h.pause()
        if dl_kb:
            h.set_download_limit(dl_kb * 1024)
        if ul_kb:
            h.set_upload_limit(ul_kb * 1024)

        self.counter += 1
        iid = str(self.counter)
        self.items[iid] = {"src": src, "save": save, "h": h, "key": key,
                           "dl_kb": dl_kb, "ul_kb": ul_kb, "w": self._make_card(iid),
                           "v": {"cat": "down", "name": "", "prog": 0, "size": 0}}
        self.apply_view(force=True)
        if persist:
            self.persist_list()
        return "ok"

    def _make_card(self, iid):
        card = ctk.CTkFrame(self.list, corner_radius=12, fg_color=C["card"], border_width=1,
                            border_color=C["border"])
        card.grid_columnconfigure(1, weight=1)

        tile = ctk.CTkFrame(card, width=48, height=48, corner_radius=10, fg_color=C["card2"])
        tile.grid(row=0, column=0, rowspan=2, padx=(20, 16), pady=(20, 0), sticky="n")
        tile.grid_propagate(False)
        tile_icon = ctk.CTkLabel(tile, text="", image=icon("file", C["muted"], 20))
        tile_icon.place(relx=0.5, rely=0.5, anchor="center")

        name = ctk.CTkLabel(card, text=tr("A carregar…"), anchor="w", text_color=C["text"],
                            font=ctk.CTkFont(size=15, weight="bold"))
        name.grid(row=0, column=1, sticky="ew", pady=(20, 0))
        subf = ctk.CTkFrame(card, fg_color="transparent")
        subf.grid(row=1, column=1, sticky="w", pady=(2, 0))
        size = ctk.CTkLabel(subf, text="—", text_color=C["muted"], font=ctk.CTkFont(size=12))
        size.pack(side="left")
        ctk.CTkLabel(subf, text="·", text_color=C["dim"]).pack(side="left", padx=8)
        path = ctk.CTkLabel(subf, text="", image=icon("folder", C["dim"], 14), compound="left",
                            text_color=C["muted"], font=ctk.CTkFont(size=12))
        path.pack(side="left")

        act = ctk.CTkFrame(card, fg_color="transparent")
        act.grid(row=0, column=2, rowspan=2, padx=(8, 14), pady=(14, 0), sticky="ne")

        def ibtn(ic, cmd):
            b = ctk.CTkButton(act, text="", image=icon(ic, C["muted"], 18), width=36, height=36,
                              corner_radius=8, fg_color="transparent", hover_color=C["hover"], command=cmd)
            b.pack(side="left", padx=1)
            return b

        ibtn("folder", lambda: self.open_folder(iid))
        b_pause = ibtn("pause", lambda: self.toggle_pause(iid))
        b_more = ibtn("more", None)
        b_more.configure(command=lambda: self.item_menu(iid, b_more))

        bar = ctk.CTkProgressBar(card, height=4, corner_radius=2, fg_color=C["card2"], progress_color=BLUE)
        bar.set(0)
        bar.grid(row=2, column=1, sticky="ew", pady=(16, 0))
        pct = ctk.CTkLabel(card, text="0%", anchor="e", width=56, text_color=C["muted"], font=ctk.CTkFont(size=12))
        pct.grid(row=2, column=2, sticky="e", padx=(0, 20), pady=(16, 0))

        sf = ctk.CTkFrame(card, fg_color="transparent")
        sf.grid(row=3, column=1, sticky="w", pady=(12, 18))

        def stat(ic):
            return ctk.CTkLabel(sf, text="", image=icon(ic, C["dim"], 14), compound="left",
                                text_color=C["muted"], font=ctk.CTkFont(size=12))

        dl = stat("download")
        dl.pack(side="left", padx=(0, 20))
        ul = stat("upload")
        ul.pack(side="left", padx=(0, 20))
        peers = stat("users")
        peers.pack(side="left", padx=(0, 20))
        eta = stat("clock")                      # só aparece quando há tempo estimado

        badge = ctk.CTkLabel(card, text="", height=24, corner_radius=6, compound="left",
                             font=ctk.CTkFont(size=11, weight="bold"), fg_color=C["gray_bg"],
                             text_color=C["muted"])
        badge.grid(row=3, column=2, sticky="e", padx=(0, 20), pady=(12, 18))

        # clicar no cartão abre a pasta (só quando terminou)
        for wdg in (card, name, subf, size, bar, pct, sf):
            wdg.bind("<Button-1>", lambda e: self.open_folder(iid, only_done=True))
        return {"card": card, "tile_icon": tile_icon, "name": name, "size": size, "path": path, "bar": bar,
                "pct": pct, "dl": dl, "ul": ul, "peers": peers, "eta": eta, "badge": badge,
                "pause": b_pause, "cache": {}}

    # ---- ordem / fila
    def ordered_items(self):
        def key(entry):
            iid, it = entry
            try:
                pos = it["h"].queue_position()
            except Exception:
                pos = -1
            return (0, pos, int(iid)) if pos >= 0 else (1, 0, int(iid))
        return sorted(self.items.items(), key=key)

    def reorder_cards(self, force=False):
        self.apply_view(force)

    def move_queue(self, iid, direction):
        it = self.items.get(iid)
        if not it:
            return
        try:
            if direction < 0:
                it["h"].queue_position_up()
            else:
                it["h"].queue_position_down()
        except Exception:
            return
        self.persist_list()
        self.after(150, lambda: self.reorder_cards())

    def persist_list(self):
        out = []
        for iid, it in self.ordered_items():
            try:
                fl = it["h"].flags()
                manual = bool(fl & lt.torrent_flags.paused) and not bool(fl & lt.torrent_flags.auto_managed)
            except Exception:
                manual = False
            out.append({"src": it["src"], "save": it["save"], "paused": manual,
                        "dl_kb": it.get("dl_kb", 0), "ul_kb": it.get("ul_kb", 0)})
        self.cfg["torrents"] = out
        save_cfg(self.cfg)

    def toggle_pause(self, iid):
        it = self.items.get(iid)
        if not it:
            return
        h = it["h"]
        fl = h.flags()
        manual = bool(fl & lt.torrent_flags.paused) and not bool(fl & lt.torrent_flags.auto_managed)
        if manual:
            h.set_flags(lt.torrent_flags.auto_managed)
            h.resume()
        else:
            h.unset_flags(lt.torrent_flags.auto_managed)
            h.pause()
        self.persist_list()

    def limits_dialog(self, iid):
        it = self.items.get(iid)
        if not it:
            return
        win = ctk.CTkToplevel(self, fg_color=C["bg"])
        win.title(tr("Limites do torrent"))
        win.geometry("340x240")
        win.resizable(False, False)
        win.transient(self)
        win.after(250, lambda: self._try_icon(win))
        win.after(200, win.grab_set)

        try:
            title = short(it["h"].status().name or "Torrent", 38)
        except Exception:
            title = "Torrent"
        ctk.CTkLabel(win, text=title, font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=20, pady=(18, 2))
        ctk.CTkLabel(win, text=tr("0 = sem limite (usa o limite geral)"), text_color="gray55").pack(
            anchor="w", padx=20)
        dl = ctk.StringVar(value=str(it.get("dl_kb", 0)))
        ul = ctk.StringVar(value=str(it.get("ul_kb", 0)))
        grid = ctk.CTkFrame(win, fg_color="transparent")
        grid.pack(fill="x", padx=20, pady=10)
        grid.grid_columnconfigure(0, weight=1)
        for r, (label, var) in enumerate(((tr("Download (KB/s)"), dl), (tr("Upload (KB/s)"), ul))):
            ctk.CTkLabel(grid, text=label).grid(row=r, column=0, sticky="w", pady=5)
            ctk.CTkEntry(grid, width=100, textvariable=var, justify="right").grid(row=r, column=1, pady=5)
        err = ctk.CTkLabel(win, text="", text_color=RED)
        err.pack(anchor="w", padx=20)

        def apply():
            try:
                d = max(0, int(dl.get()))
                u = max(0, int(ul.get()))
            except ValueError:
                err.configure(text=tr("Usa números inteiros."))
                return
            it["dl_kb"], it["ul_kb"] = d, u
            it["h"].set_download_limit(d * 1024 if d else -1)
            it["h"].set_upload_limit(u * 1024 if u else -1)
            self.persist_list()
            win.destroy()

        ctk.CTkButton(win, text=tr("Guardar"), command=apply).pack(fill="x", padx=20, pady=(6, 0))

    def open_folder(self, iid, only_done=False):
        it = self.items.get(iid)
        if not it:
            return
        try:
            s = it["h"].status()
            if only_done and int(s.state) not in (4, 5):
                return
            base = getattr(s, "save_path", None) or it["save"]
            path = os.path.normpath(os.path.join(base, s.name)) if s.name else os.path.normpath(base)
            if os.path.isdir(path):
                os.startfile(path)
            elif os.path.isfile(path):
                subprocess.Popen(f'explorer /select,"{path}"')
            else:
                os.startfile(os.path.normpath(base))
        except Exception as e:
            messagebox.showerror(APP, tr("Não foi possível abrir a pasta:\n{error}", error=e))

    def remove_item(self, iid, delete_files=None):
        it = self.items.get(iid)
        if not it:
            return
        if delete_files is None:
            r = messagebox.askyesnocancel(APP, tr("Apagar também os ficheiros transferidos?"))
            if r is None:
                return
            delete_files = r
        elif delete_files:
            try:
                nm = short(it["h"].status().name or tr("este torrent"), 50)
            except Exception:
                nm = tr("este torrent")
            if not messagebox.askyesno(APP, tr("Apagar «{name}» e os ficheiros transferidos?", name=nm)):
                return
        try:
            if delete_files:
                self.ses.remove_torrent(it["h"], lt.options_t.delete_files)
            else:
                self.ses.remove_torrent(it["h"])
        except Exception:
            pass
        it["w"]["card"].destroy()
        try:
            os.remove(os.path.join(RESUME_DIR, it["key"] + ".fastresume"))
        except OSError:
            pass
        del self.items[iid]
        self.persist_list()
        self.apply_view(force=True)

    # ---- dados de retoma rápida
    def handle_alerts(self):
        """Processa alertas e grava os dados de retoma rápida. Devolve nº de respostas."""
        done = 0
        for a in self.ses.pop_alerts():
            if isinstance(a, lt.save_resume_data_alert):
                done += 1
                for it in self.items.values():
                    if it["h"] == a.handle:
                        try:
                            os.makedirs(RESUME_DIR, exist_ok=True)
                            buf = lt.write_resume_data_buf(a.params)
                            with open(os.path.join(RESUME_DIR, it["key"] + ".fastresume"), "wb") as f:
                                f.write(buf)
                        except Exception:
                            pass
                        break
            elif isinstance(a, lt.save_resume_data_failed_alert):
                done += 1
            elif isinstance(a, lt.listen_succeeded_alert):
                self._net_events["listen_ok"].append(f"{getattr(a, 'address', '?')}:{getattr(a, 'port', '?')}")
            elif isinstance(a, lt.listen_failed_alert):
                try:
                    msg = a.error.message()
                except Exception:
                    msg = str(getattr(a, "error", "erro"))
                self._net_events["listen_fail"].append(f"{getattr(a, 'address', '?')}:{getattr(a, 'port', '?')} — {msg}")
            elif isinstance(a, lt.portmap_alert):
                kind = "UPnP" if int(getattr(a, "map_type", 1)) == 1 else "NAT-PMP"
                self._net_events["map_ok"].append(tr("porta externa {port} ({kind})", port=getattr(a, 'external_port', '?'), kind=kind))
            elif isinstance(a, lt.portmap_error_alert):
                try:
                    msg = a.error.message()
                except Exception:
                    msg = str(getattr(a, "error", "erro"))
                self._net_events["map_err"].append(msg)
            elif isinstance(a, getattr(lt, "external_ip_alert", ())):
                self._net_events["ext_ip"] = str(getattr(a, "external_address", "")) or None
            elif isinstance(a, lt.dht_stats_alert):
                try:
                    self._net_events["dht_nodes"] = sum(
                        (r["num_nodes"] if isinstance(r, dict) else r.num_nodes) for r in a.routing_table)
                except Exception:
                    pass
            for k in ("listen_ok", "listen_fail", "map_ok", "map_err"):
                if len(self._net_events[k]) > 10:
                    del self._net_events[k][:-10]
        return done

    def request_resume(self):
        n = 0
        flag = getattr(lt.torrent_handle, "save_info_dict", 0)
        for it in self.items.values():
            h = it["h"]
            try:
                if h.is_valid() and h.status().has_metadata:
                    h.save_resume_data(flag)
                    n += 1
            except Exception:
                pass
        return n

    # ---- pasta vigiada
    def choose_watch(self):
        d = filedialog.askdirectory(title=tr("Pasta vigiada (.torrent)"))
        if d:
            d = os.path.normpath(d)
            self.cfg["watch_path"] = d
            save_cfg(self.cfg)
            self.watch_var.set(d)

    def toggle_watch(self):
        on = bool(self.sw_watch.get())
        if on and not self.cfg.get("watch_path"):
            self.sw_watch.deselect()
            self.show_flash(tr("Escolhe primeiro a pasta a vigiar"), AMBER)
            return
        self.cfg["watch_enabled"] = on
        save_cfg(self.cfg)

    def scan_watch(self):
        try:
            folder = self.cfg.get("watch_path")
            if self.cfg.get("watch_enabled") and folder and os.path.isdir(folder):
                self._scan_watch_folder(folder)
        except Exception:
            pass
        finally:
            self.after(6000, self.scan_watch)

    def _scan_watch_folder(self, folder):
        for fn in os.listdir(folder):
            if not fn.lower().endswith(".torrent"):
                continue
            f = os.path.join(folder, fn)
            try:
                if not os.path.isfile(f):
                    continue
                size = os.path.getsize(f)
            except OSError:
                continue
            if self._watch_seen.get(f) != size:      # só processa quando o tamanho estabilizou
                self._watch_seen[f] = size
                continue
            self._watch_seen.pop(f, None)
            res = self.add_torrent_file(f, self.library_roots(), interactive=False)
            self._move_to(f, os.path.join(folder, "adicionados" if res in ("ok", "dup") else "erros"))
            if res == "ok":
                self.show_flash(f"+ {short(fn, 40)}")

    def _move_to(self, f, folder):
        try:
            os.makedirs(folder, exist_ok=True)
            dest = os.path.join(folder, os.path.basename(f))
            if os.path.exists(dest):
                base, ext = os.path.splitext(dest)
                dest = f"{base}.{int(time.time())}{ext}"
            shutil.move(f, dest)
        except OSError:
            pass

    # ---- Windows: arranque, associações, bandeja
    def toggle_autostart(self):
        try:
            set_autostart(bool(self.sw_auto.get()))
        except Exception as e:
            self.show_flash(tr("Erro: {error}", error=e), RED)

    def change_language(self, label):
        """Aceita o nome do idioma (menu das Preferências) ou o do seletor da barra lateral."""
        codes = {v: k for k, v in LANGUAGES.items()}
        codes.update({"Português": "pt", "English": "en"})
        code = codes.get(label)
        if not code or code == i18n.LANG:
            return
        self.cfg["language"] = code
        save_cfg(self.cfg)
        self.after(60, lambda: self.set_language_live(code))     # depois de o botão terminar o seu clique

    def set_language_live(self, code):
        """Muda o idioma já: reconstrói a interface mantendo página, filtro e ordenação."""
        sort_keys = ["Fila", "Mais recentes", "Nome", "Progresso", "Tamanho"]
        src_sort = next((k for k in sort_keys if tr(k) == self.sort), "Fila")
        page = self.page
        set_language(code)
        self.sort, self.query, self._view_sig = tr(src_sort), "", None
        for child in self.winfo_children():
            child.destroy()
        self._build_ui()
        for iid, it in self.items.items():
            it["w"] = self._make_card(iid)
        self.sort_menu.set(self.sort)
        self.show_page(page)
        self.update_fw_label()
        self.update_net_label()
        self.update_sched_label()
        self.apply_view(force=True)
        self.refresh_tray_menu()

    def _tray_menu(self):
        return pystray.Menu(
            pystray.MenuItem(tr("Abrir"), lambda icon, item: self.cmd_q.put(("show",)), default=True),
            pystray.MenuItem(tr("Sair"), lambda icon, item: self.cmd_q.put(("quit",))))

    def refresh_tray_menu(self):
        if self.tray:
            try:
                self.tray.menu = self._tray_menu()
                self.tray.update_menu()
            except Exception:
                pass

    def toggle_tray_close(self):
        self.cfg["close_to_tray"] = bool(self.sw_tray.get())
        save_cfg(self.cfg)

    def associate(self):
        try:
            register_associations()
        except Exception as e:
            self.show_flash(tr("Erro: {error}", error=e), RED)
            return
        messagebox.showinfo(
            APP, tr("Programa registado.\n\nO Windows exige que confirmes tu o programa por defeito. "
                 "Vou abrir as Definições: procura «Alf Torrent» e escolhe-o para .torrent e MAGNET."))
        try:
            os.startfile("ms-settings:defaultapps")
        except Exception:
            pass

    def start_tray(self):
        if not HAS_TRAY:
            return
        try:
            try:
                img = Image.open(resource_path("AlfTorrent.ico")).convert("RGBA")
            except Exception:
                img = Image.new("RGBA", (64, 64), (59, 130, 246, 255))
            self.tray = pystray.Icon("AlfTorrent", img, APP, self._tray_menu())
            self.tray.run_detached()
        except Exception:
            self.tray = None

    def notify(self, msg):
        if self.tray:
            try:
                self.tray.notify(msg, APP)
            except Exception:
                pass

    def show_window(self):
        self.deiconify()
        self.lift()
        self.focus_force()
        self.attributes("-topmost", True)
        self.after(250, lambda: self.attributes("-topmost", False))

    # ---- instância única
    def start_ipc(self):
        try:
            srv = socket.socket()
            srv.bind(("127.0.0.1", IPC_PORT))
            srv.listen(5)
        except OSError:
            return

        def loop():
            while True:
                try:
                    conn, _ = srv.accept()
                except OSError:
                    return
                try:
                    conn.settimeout(2)
                    data = b""
                    while not data.endswith(b"\n") and len(data) < 65536:
                        chunk = conn.recv(4096)
                        if not chunk:
                            break
                        data += chunk
                    args = json.loads(data.decode("utf-8"))
                    if isinstance(args, list):
                        self.cmd_q.put(("args", [a for a in args if isinstance(a, str)]))
                except Exception:
                    pass
                finally:
                    conn.close()

        threading.Thread(target=loop, daemon=True).start()

    def poll_commands(self):
        try:
            while True:
                cmd = self.cmd_q.get_nowait()
                if cmd[0] == "show":
                    self.show_window()
                elif cmd[0] == "args":
                    self.handle_args(cmd[1])
                elif cmd[0] == "quit":
                    self.quit_app()
                    return
        except queue.Empty:
            pass
        self.after(250, self.poll_commands)

    def handle_args(self, args):
        """Ficheiros .torrent / links magnet vindos do Explorador ou do navegador."""
        files = []
        for a in args:
            if a.startswith("magnet:"):
                self.add_source(a, self.save_var.get())
            elif a.lower().endswith(".torrent") and os.path.isfile(a):
                files.append(a)
        if args:
            self.show_window()
        if files:
            self.add_torrent_paths(files, interactive=True)

    # ---- firewall
    def update_fw_label(self):
        ok = fw_rule_exists()
        self.fw_label.configure(text=tr("●  Regra ativa") if ok else tr("●  Sem regra"),
                                text_color=GREEN if ok else AMBER)

    def first_run_firewall(self):
        if self.cfg.get("fw_asked") or self.state() == "withdrawn":
            return
        self.cfg["fw_asked"] = True
        save_cfg(self.cfg)
        if not fw_rule_exists() and messagebox.askyesno(
                APP, tr("Queres criar uma regra na Firewall do Windows para permitir ligações "
                     "a este programa? (Pede permissões de administrador)")):
            self.create_fw()

    def create_fw(self):
        if fw_rule_exists():
            self.show_flash(tr("A regra já existe"))
        elif fw_add_rule():
            self.show_flash(tr("Confirma o pedido do Windows (UAC)"), AMBER)
            self.after(5000, self.update_fw_label)
        else:
            self.show_flash(tr("Sem permissões de administrador"), RED)

    def remove_fw(self):
        if not fw_rule_exists():
            self.show_flash(tr("Não há regra para remover"))
        elif fw_remove_rule():
            self.show_flash(tr("Confirma o pedido do Windows (UAC)"), AMBER)
            self.after(5000, self.update_fw_label)

    # ---- atualização periódica
    def refresh(self):
        visible = False
        try:
            visible = self.state() in ("normal", "zoomed")
            self.handle_alerts()
            self._tick += 1
            if self._tick % 300 == 0:
                self.request_resume()
            if self._tick % 30 == 0 and visible:
                self.update_storage()
            self.apply_schedule()
            d = {"tot_d": 0, "tot_u": 0, "n_dl": 0, "n_seed": 0, "n_active": 0, "all_dl": 0, "all_ul": 0}
            cnt = {"all": 0, "down": 0, "seed": 0, "paused": 0}
            for iid, it in list(self.items.items()):
                try:
                    s = it["h"].status()
                    fl = it["h"].flags()
                except Exception:
                    continue
                paused_flag = bool(fl & lt.torrent_flags.paused)
                auto = bool(fl & lt.torrent_flags.auto_managed)
                manual = paused_flag and not auto
                queued = paused_flag and auto
                st = int(s.state)
                done = st in (4, 5)
                d["tot_d"] += s.download_payload_rate
                d["tot_u"] += s.upload_payload_rate
                d["all_dl"] += s.all_time_download
                d["all_ul"] += s.all_time_upload

                if self.net_blocked:
                    kind = "blocked"
                elif manual:
                    kind = "paused"
                elif queued and not done and not self._sched_state:
                    kind = "sched"
                elif queued:
                    kind = "queued"
                elif st in (1, 7):
                    kind = "check"
                elif st == 2:
                    kind = "meta"
                elif st == 5:
                    kind = "seed"
                elif st == 4:
                    kind = "done"
                else:
                    kind = "down"

                cat = "paused" if manual else ("seed" if done else "down")
                cnt["all"] += 1
                cnt[cat] += 1
                if kind == "down":
                    d["n_dl"] += 1
                if kind == "seed":
                    d["n_seed"] += 1
                if kind in ("down", "seed", "done", "check", "meta"):
                    d["n_active"] += 1
                it["v"] = {"cat": cat, "name": s.name or "", "prog": s.progress, "size": s.total_wanted}

                if st == 3 and not paused_flag:
                    it["seen_dl"] = True
                if done and it.get("seen_dl") and not it.get("notified"):
                    it["notified"] = True
                    self.notify(tr("Concluído: {name}", name=short(s.name, 60)))

                if visible:                          # janela escondida: não mexer nos widgets
                    self._update_card(it, s, kind, manual)

            self.spark_d.append(d["tot_d"])
            self.spark_u.append(d["tot_u"])
            if visible:
                self._update_stats(d, cnt)
                self.apply_view()
        finally:
            self.after(1000 if visible else 3000, self.refresh)

    def _update_card(self, it, s, kind, manual):
        w = it["w"]
        prog = max(0.0, min(1.0, s.progress))
        self._set(it, "name", w["name"], text=short(s.name, 100) if s.name else tr("A obter metadados…"))
        self._set(it, "size", w["size"], text=fmt_size(s.total_wanted) if s.total_wanted else "—")
        self._set(it, "path", w["path"], text=" " + short_path(it["save"], 44))
        self._set(it, "tile", w["tile_icon"],
                  image=icon("file-play" if is_video(s.name) else "file", C["muted"], 20))
        label, col, bg, ic = BADGES[kind]
        self._set(it, "badge", w["badge"], text="  " + tr(label), text_color=C[col], fg_color=C[bg],
                  image=icon(ic, C[col], 12))
        bar_col = C["blue"] if kind in ("down", "check", "meta") else (C["green"] if kind in ("seed", "done") else C["dim"])
        self._set(it, "barc", w["bar"], progress_color=bar_col)
        if abs(w["cache"].get("prog", -1) - prog) > 0.0005:
            w["cache"]["prog"] = prog
            w["bar"].set(prog)
        self._set(it, "pct", w["pct"], text="100%" if prog >= 1 else dec(f"{prog * 100:.1f}%"))

        down_on = s.download_payload_rate > 0
        self._set(it, "dl", w["dl"], text=" " + fmt_speed(s.download_payload_rate),
                  text_color=C["blue"] if down_on else C["muted"],
                  image=icon("download", C["blue"] if down_on else C["dim"], 14))
        up_on = s.upload_payload_rate > 0
        self._set(it, "ul", w["ul"], text=" " + fmt_speed(s.upload_payload_rate),
                  text_color=C["green"] if up_on else C["muted"],
                  image=icon("upload", C["green"] if up_on else C["dim"], 14))
        swarm = ""
        if s.num_complete >= 0 or s.num_incomplete >= 0:
            swarm = tr("   ·   enxame: {seeds} seeds, {leechers} leechers", seeds=max(s.num_complete, 0), leechers=max(s.num_incomplete, 0))
        self._set(it, "peers", w["peers"],
                  text=tr(" {n} peer{s}{swarm}", n=s.num_peers, s='s' if s.num_peers != 1 else '', swarm=swarm))

        remaining = s.total_wanted - s.total_wanted_done
        eta = fmt_eta(remaining / s.download_payload_rate) if (kind == "down" and s.download_payload_rate > 0 and remaining > 0) else ""
        if eta:
            self._set(it, "eta", w["eta"], text=" " + eta)
            if not w["cache"].get("eta_vis"):
                w["eta"].pack(side="left")
                w["cache"]["eta_vis"] = True
        elif w["cache"].get("eta_vis"):
            w["eta"].pack_forget()
            w["cache"]["eta_vis"] = False
        self._set(it, "pause", w["pause"], image=icon("play" if manual else "pause", C["muted"], 18))

    def _update_stats(self, d, cnt):
        st, c = self.stat, self._cache
        b, u = size_parts(d["tot_d"])
        self._cset(c, "dl_big", st["dl"]["big"], text=b)
        self._cset(c, "dl_unit", st["dl"]["unit"], text=u + "/s")
        n = d["n_dl"]
        self._cset(c, "dl_sub", st["dl"]["a"], text=tr("{n} transferência{s} em curso", n=n, s='s' if n != 1 else ''))
        b, u = size_parts(d["tot_u"])
        self._cset(c, "ul_big", st["ul"]["big"], text=b)
        self._cset(c, "ul_unit", st["ul"]["unit"], text=u + "/s")
        n = d["n_seed"]
        self._cset(c, "ul_sub", st["ul"]["a"], text=tr("{n} torrent{s} a partilhar", n=n, s='s' if n != 1 else ''))
        self._cset(c, "act_big", st["act"]["big"], text=str(d["n_active"]))
        self._cset(c, "act_unit", st["act"]["unit"], text=f"/ {cnt['all']}")
        self._cset(c, "act_a", st["act"]["a"], text=tr("{n} a transferir", n=cnt['down']), text_color=C["blue"])
        self._cset(c, "act_b", st["act"]["b"], text=tr("·  {n} a partilhar", n=cnt['seed']))
        b, u = size_parts(d["all_dl"] if d["all_dl"] else d["all_ul"])
        self._cset(c, "tot_big", st["tot"]["big"], text=b)
        self._cset(c, "tot_unit", st["tot"]["unit"], text=u)
        self._cset(c, "tot_a", st["tot"]["a"], text=tr("↑ {size} partilhados", size=fmt_size(d['all_ul'])) if d["all_ul"] else "",
                   text_color=C["green"])
        draw_spark(st["dl"]["cv"], list(self.spark_d), C["blue"])
        draw_spark(st["ul"]["cv"], list(self.spark_u), C["green"])
        for key in ("all", "down", "seed", "paused"):
            self._cset(c, "nav_" + key, self.nav[key]["count"], text=str(cnt[key]))
            self._cset(c, "tab_" + key, self.tabw[key]["count"], text=str(cnt[key]))
        running = cnt["all"] - cnt["paused"] > 0
        self._cset(c, "pall", self.pause_all_btn, text=tr("Pausar todas") if running else tr("Retomar todas"),
                   image=icon("pause" if running else "play", C["muted"], 16))

    # ---- fechar
    def on_close(self):
        if self.tray and self.cfg.get("close_to_tray", True):
            self.withdraw()
            if not self.cfg.get("tray_tip_shown"):
                self.cfg["tray_tip_shown"] = True
                save_cfg(self.cfg)
                self.notify(tr("Continua a transferir e a partilhar em segundo plano. "
                            "Usa o ícone junto ao relógio para abrir ou sair."))
            return
        self.quit_app()

    def quit_app(self):
        self.cfg["save_path"] = self.save_var.get()
        self.persist_list()
        if self.tray:
            try:
                self.tray.stop()
            except Exception:
                pass
        self.withdraw()
        n = self.request_resume()
        deadline = time.time() + 15
        while n > 0 and time.time() < deadline:
            self.ses.wait_for_alert(500)
            n -= self.handle_alerts()
        self.destroy()


if __name__ == "__main__":
    argv = sys.argv[1:]
    tray_start = "--tray" in argv
    args = [a for a in argv if a != "--tray"]
    # já há uma instância? entrega-lhe os ficheiros/links e sai
    if send_to_running(args if args else ([] if tray_start else ["--show"])):
        sys.exit(0)
    App(start_hidden=tray_start, initial_args=args).mainloop()
