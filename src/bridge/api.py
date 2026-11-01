"""API de comunicação IPC exposta ao JavaScript pelo PyWebView."""

from typing import List, Dict, Any, Optional
import webview
from src.core.engine import evaluate_expression, CalculatorError
from src.bridge.receipt import format_receipt_text


class DesktopBridgeApi:
    """Ponte IPC entre a interface gráfica WebView e o motor Python."""

    def __init__(self, window: Optional[Any] = None):
        self._window = window

    def set_window(self, window: Any) -> None:
        """Define a referência da janela ativa."""
        self._window = window

    def calculate(self, expression: str) -> Dict[str, Any]:
        """Avalia uma expressão aritmética recebida da interface web."""
        try:
            result = evaluate_expression(expression)
            return {
                "status": "success",
                "result": result,
                "expression": expression,
                "error": None,
            }
        except CalculatorError as e:
            return {
                "status": "error",
                "result": None,
                "expression": expression,
                "error": str(e),
            }
        except Exception:
            return {
                "status": "error",
                "result": None,
                "expression": expression,
                "error": "ERRO NO CÁLCULO",
            }

    def export_receipt_txt(
        self, tape_entries: List[Dict[str, Any]], filename_hint: str = "recibo_calculadora.txt"
    ) -> Dict[str, Any]:
        """Abre a caixa de diálogo nativa do Windows e salva o extrato da fita em arquivo .txt."""
        if not self._window:
            return {
                "status": "error",
                "saved_path": None,
                "error": "JANELA_NAO_INICIALIZADA",
            }

        try:
            result = self._window.create_file_dialog(
                webview.SAVE_DIALOG,
                directory="",
                save_filename=filename_hint,
                file_types=("Text Files (*.txt)", "*.txt"),
            )

            if not result:
                return {
                    "status": "cancelled",
                    "saved_path": None,
                    "error": None,
                }

            file_path = result[0] if isinstance(result, (list, tuple)) else result

            content = format_receipt_text(tape_entries)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            return {
                "status": "success",
                "saved_path": str(file_path),
                "error": None,
            }
        except (IOError, OSError, PermissionError):
            return {
                "status": "error",
                "saved_path": None,
                "error": "FALHA_GRAVACAO",
            }
        except Exception:
            return {
                "status": "error",
                "saved_path": None,
                "error": "FALHA_GRAVACAO",
            }
