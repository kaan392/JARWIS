"""
Uygulama açma — Windows için os.startfile / start komutu ile çalışır.
"""

import os
import shutil
import subprocess


APP_ALIASES = {
    "edge":              "msedge",
    "microsoft edge":    "msedge",
    "chrome":            "chrome",
    "google chrome":     "chrome",
    "firefox":           "firefox",
    "terminal":          "cmd",
    "cmd":               "cmd",
    "powershell":        "powershell",
    "explorer":          "explorer",
    "dosya gezgini":     "explorer",
    "file explorer":     "explorer",
    "spotify":           "Spotify",
    "vscode":            "code",
    "vs code":           "code",
    "code":              "code",
    "discord":           "Discord",
    "slack":             "Slack",
    "whatsapp":          "WhatsApp",
    "whatsapp desktop":  "WhatsApp",
    "whatsapp app":      "WhatsApp",
    "whatsapp web":      "https://web.whatsapp.com/",
    "whatsapp web sitesi": "https://web.whatsapp.com/",
    "telegram":          "Telegram",
    "zoom":              "Zoom",
    "notepad":           "notepad",
    "notlar":            "notepad",
    "not defteri":       "notepad",
    "word":              "winword",
    "excel":             "excel",
    "powerpoint":        "powerpnt",
    "calculator":        "calc",
    "hesap makinesi":    "calc",
    "task manager":      "taskmgr",
    "görev yöneticisi":  "taskmgr",
    "settings":          "ms-settings:",
    "ayarlar":           "ms-settings:",
    "paint":             "mspaint",
    "wordpad":           "wordpad",
    "snipping tool":     "SnippingTool",
    "ekran alıntısı":    "SnippingTool",
    "photos":            "ms-photos:",
    "fotoğraflar":       "ms-photos:",
    "maps":              "bingmaps:",
    "haritalar":         "bingmaps:",
    "mail":              "outlookmail:",
    "calendar":          "outlookcal:",
    "takvim":            "outlookcal:",
    "store":             "ms-windows-store:",
    "mağaza":            "ms-windows-store:",
    "music":             "mswindowsmusic:",
    "müzik":             "mswindowsmusic:",
    "notion":            "Notion",
}

URI_SCHEMES = {
    "ms-settings:", "ms-photos:", "bingmaps:", "outlookmail:",
    "outlookcal:", "ms-windows-store:", "mswindowsmusic:",
}

URI_APP_SCHEMES = {
    "whatsapp": "whatsapp://",
    "whatsapp desktop": "whatsapp://",
    "whatsapp app": "whatsapp://",
    "whatsapp web": "https://web.whatsapp.com/",
    "whatsapp web sitesi": "https://web.whatsapp.com/",
}

CLOSE_ALIASES = {
    "edge": ["msedge.exe"],
    "microsoft edge": ["msedge.exe"],
    "chrome": ["chrome.exe"],
    "google chrome": ["chrome.exe"],
    "firefox": ["firefox.exe"],
    "terminal": ["cmd.exe", "powershell.exe"],
    "cmd": ["cmd.exe"],
    "powershell": ["powershell.exe"],
    "explorer": ["explorer.exe"],
    "dosya gezgini": ["explorer.exe"],
    "spotify": ["spotify.exe"],
    "vscode": ["Code.exe", "code.exe"],
    "vs code": ["Code.exe", "code.exe"],
    "code": ["Code.exe", "code.exe"],
    "discord": ["Discord.exe"],
    "slack": ["slack.exe"],
    "whatsapp": ["WhatsApp.exe"],
    "telegram": ["Telegram.exe"],
    "zoom": ["Zoom.exe"],
    "notepad": ["notepad.exe"],
    "word": ["WINWORD.EXE"],
    "excel": ["EXCEL.EXE"],
    "powerpoint": ["POWERPNT.EXE"],
    "calculator": ["Calculator.exe", "calc.exe"],
    "hesap makinesi": ["Calculator.exe", "calc.exe"],
    "task manager": ["Taskmgr.exe"],
    "görev yöneticisi": ["Taskmgr.exe"],
}


def _open_uri(uri: str) -> bool:
    try:
        os.startfile(uri)
        return True
    except Exception:
        return False


def _taskkill_process(process_name: str) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            ["taskkill", "/IM", process_name, "/F"],
            capture_output=True,
            text=True,
            shell=False,
            timeout=12,
        )
        output = (result.stdout or "") + (result.stderr or "")
        output = output.strip()
        return result.returncode == 0, output or f"{process_name} kapatma komutu gönderildi."
    except Exception as exc:
        return False, str(exc)


def close_app(app_name: str) -> str:
    if not app_name:
        return "Kapatılacak uygulama adı belirtilmedi."

    normalized = app_name.lower().strip()
    process_names = CLOSE_ALIASES.get(normalized)
    if not process_names:
        resolved = APP_ALIASES.get(normalized, app_name)
        if resolved.lower().endswith(".exe"):
            process_names = [resolved]
        else:
            process_names = [f"{resolved}.exe"]

    results = []
    any_success = False
    for proc in process_names:
        ok, detail = _taskkill_process(proc)
        if ok:
            any_success = True
        results.append(f"{proc}: {'OK' if ok else 'FAIL'} ({detail})")

    if any_success:
        return f"{app_name} kapatıldı. " + " ".join(results)
    return f"{app_name} kapatılamadı. Denenenler: " + " ".join(results)


def open_app(app_name: str) -> str:
    if not app_name:
        return "Uygulama adı belirtilmedi."

    normalized = app_name.lower().strip()
    resolved = APP_ALIASES.get(normalized, app_name)

    if normalized in URI_APP_SCHEMES:
        if _open_uri(URI_APP_SCHEMES[normalized]):
            return f"{app_name} açıldı."
        return f"{app_name} açılmaya çalışıldı ancak URI açma başarısız oldu."

    # URI scheme (ms-settings: vb.)
    if any(resolved.startswith(scheme) for scheme in URI_SCHEMES):
        try:
            os.startfile(resolved)
            return f"{app_name} açıldı."
        except Exception as e:
            return f"'{app_name}' açılamadı: {e}"

    # PATH'teki executable
    exe_path = shutil.which(resolved)
    if exe_path:
        try:
            subprocess.Popen([exe_path], shell=False)
            return f"{app_name} açıldı."
        except Exception as e:
            return f"'{app_name}' açılamadı: {e}"

    # start komutu (Windows shell'i aracılığıyla)
    try:
        result = subprocess.run(
            f'start "" "{resolved}"',
            shell=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return f"{app_name} açıldı."
    except Exception:
        pass

    # os.startfile son çare
    try:
        os.startfile(resolved)
        return f"{app_name} açıldı."
    except Exception as e:
        return f"'{app_name}' bulunamadı veya açılamadı: {e}"
