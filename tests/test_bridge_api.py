"""Testes unitários da ponte IPC DesktopBridgeApi e da formatação de recibo."""

from unittest.mock import Mock
from src.bridge.api import DesktopBridgeApi
from src.bridge.receipt import format_receipt_text


def test_bridge_calculate_success():
    """Valida o contrato de retorno IPC em cálculo bem-sucedido."""
    api = DesktopBridgeApi()
    res = api.calculate("25.5 * (4 + 6) / 2")

    assert res["status"] == "success"
    assert res["result"] == "127.5"
    assert res["expression"] == "25.5 * (4 + 6) / 2"
    assert res["error"] is None


def test_bridge_calculate_division_by_zero():
    """Valida o contrato de erro amigável em divisão por zero."""
    api = DesktopBridgeApi()
    res = api.calculate("10 / 0")

    assert res["status"] == "error"
    assert res["result"] is None
    assert res["error"] == "DIVISÃO POR ZERO"


def test_bridge_calculate_syntax_error():
    """Valida o contrato de erro para expressões inválidas."""
    api = DesktopBridgeApi()
    res = api.calculate("10 + * 2")

    assert res["status"] == "error"
    assert res["result"] is None
    assert res["error"] == "SINTAXE INVÁLIDA"


def test_bridge_export_receipt_window_not_initialized():
    """Valida erro quando chamado sem janela vinculada."""
    api = DesktopBridgeApi()
    res = api.export_receipt_txt([{"timestamp": "12:00:00", "expression": "1+1", "result": "2"}])

    assert res["status"] == "error"
    assert res["error"] == "JANELA_NAO_INICIALIZADA"


def test_bridge_export_receipt_cancelled():
    """Valida retorno quando o usuário clica em cancelar no diálogo de salvamento."""
    mock_window = Mock()
    mock_window.create_file_dialog.return_value = None

    api = DesktopBridgeApi(window=mock_window)
    res = api.export_receipt_txt([{"timestamp": "12:00:00", "expression": "1+1", "result": "2"}])

    assert res["status"] == "cancelled"
    assert res["saved_path"] is None
    assert res["error"] is None


def test_bridge_export_receipt_success(tmp_path):
    """Valida a gravação real de arquivo em disco a partir da ponte IPC."""
    target_file = tmp_path / "recibo_teste.txt"

    mock_window = Mock()
    mock_window.create_file_dialog.return_value = (str(target_file),)

    api = DesktopBridgeApi(window=mock_window)
    entries = [
        {"timestamp": "10:15:30", "expression": "100 + 50", "result": "150"},
        {"timestamp": "10:16:00", "expression": "150 / 2", "result": "75"},
    ]
    res = api.export_receipt_txt(entries)

    assert res["status"] == "success"
    assert res["saved_path"] == str(target_file)
    assert res["error"] is None

    # Valida o conteúdo gravado em disco
    assert target_file.exists()
    content = target_file.read_text(encoding="utf-8")
    assert "CALCULATOR FAN" in content
    assert "100 + 50" in content
    assert "= 150" in content
    assert "TOTAL DE REGISTROS: 2" in content


def test_format_receipt_text_empty():
    """Valida formatação de recibo com fita vazia."""
    text = format_receipt_text([])
    assert "NENHUM REGISTRO NA SESSAO" in text
    assert "TOTAL DE REGISTROS: 0" in text
