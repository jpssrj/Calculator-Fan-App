"""Formatador de extrato de auditoria textual em formato de recibo fiscal."""

from typing import List, Dict, Any


def format_receipt_text(tape_entries: List[Dict[str, Any]]) -> str:
    """Formata a fita de auditoria como um recibo fiscal em texto monoespaçado UTF-8.

    Largura padrão: 36 colunas.
    """
    width = 36
    border = "=" * width
    divider = "-" * width

    lines = [
        border,
        "CALCULATOR FAN".center(width),
        "RECIBO DE AUDITORIA FISCAL".center(width),
        "PRECISAO DECIMAL128 (34 DIGITOS)".center(width),
        border,
        "",
    ]

    if not tape_entries:
        lines.append("NENHUM REGISTRO NA SESSAO".center(width))
        lines.append("")
    else:
        for idx, entry in enumerate(tape_entries, 1):
            ts = entry.get("timestamp", "--:--:--")
            expr = entry.get("expression", "")
            res = entry.get("result", "")

            lines.append(f"#{idx:02d} [{ts}]")
            lines.append(f"  {expr}")
            lines.append(f"= {res}".rjust(width))
            lines.append(divider)

    lines.append("")
    lines.append(border)
    count_str = f"TOTAL DE REGISTROS: {len(tape_entries)}"
    lines.append(count_str.center(width))
    lines.append("EXTRATO AUDITAVEL VOLATIL".center(width))
    lines.append(border)

    return "\n".join(lines) + "\n"
