"""Ponto de entrada do Calculator Fan Desktop App."""

import os
import sys
import webview
from src.bridge.api import DesktopBridgeApi


def get_asset_path(relative_path: str) -> str:
    """Resolve o caminho de assets compatível com execução direta e PyInstaller (--onedir)."""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def main():
    """Inicializa a janela do aplicativo com WebView2 nativo e ponte IPC."""
    api = DesktopBridgeApi()

    # O index.html fica em src/ui/index.html (em dev) ou ui/index.html (no bundle PyInstaller)
    html_path = get_asset_path(os.path.join("ui", "index.html"))
    if not os.path.exists(html_path):
        # Fallback para execução a partir da raiz do repositório em desenvolvimento
        dev_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui", "index.html")
        if os.path.exists(dev_path):
            html_path = dev_path

    # Ícone do aplicativo
    icon_path = get_asset_path(os.path.join("..", "build_scripts", "assets", "app_icon.ico"))
    if not os.path.exists(icon_path):
        icon_path = None

    window = webview.create_window(
        title="Calculator Fan",
        url=html_path,
        js_api=api,
        width=400,
        height=640,
        resizable=False,
        easy_drag=False,
        zoomable=False,
        background_color="#FEFCE8",
    )

    api.set_window(window)

    def on_closed():
        sys.exit(0)

    window.events.closed += on_closed

    webview.start(debug=False, gui="edgechromium")


if __name__ == "__main__":
    main()
