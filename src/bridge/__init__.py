"""Camada de ponte IPC para integração do PyWebView com o motor Python."""

from src.bridge.api import DesktopBridgeApi
from src.bridge.receipt import format_receipt_text

__all__ = ["DesktopBridgeApi", "format_receipt_text"]
