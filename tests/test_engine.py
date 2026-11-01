"""Testes unitários do motor de precisão matemática AST e Decimal128."""

import pytest
from src.core.engine import (
    evaluate_expression,
    format_decimal,
    CalculatorError,
    DivisionByZeroError,
    SecuritySyntaxError,
)
from decimal import Decimal


def test_basic_arithmetic():
    """Valida as 4 operações aritméticas fundamentais."""
    assert evaluate_expression("1 + 1") == "2"
    assert evaluate_expression("10 - 4") == "6"
    assert evaluate_expression("6 * 7") == "42"
    assert evaluate_expression("15 / 3") == "5"


def test_decimal_precision_ieee754():
    """Valida a eliminação das imprecisões do float binário padrão."""
    # O clássico 0.1 + 0.2 que no float binário resulta em 0.30000000000000004
    assert evaluate_expression("0.1 + 0.2") == "0.3"
    assert evaluate_expression("0.3 - 0.1") == "0.2"
    assert evaluate_expression("0.7 * 0.1") == "0.07"
    assert evaluate_expression("1 / 8") == "0.125"


def test_formatting_no_scientific_notation_for_integers():
    """Garante que inteiros terminados em zero não sofram notação científica indesejada (1E+2)."""
    assert evaluate_expression("100 / 10") == "10"
    assert evaluate_expression("10 * 10") == "100"
    assert evaluate_expression("1000 + 0") == "1000"
    assert evaluate_expression("5000000") == "5000000"
    assert format_decimal(Decimal("100")) == "100"
    assert format_decimal(Decimal("10.5000")) == "10.5"
    assert format_decimal(Decimal("0.0000")) == "0"


def test_operator_precedence_and_parentheses():
    """Garante a precedência formal de operadores matemáticos e parênteses."""
    assert evaluate_expression("2 + 3 * 4") == "14"
    assert evaluate_expression("(2 + 3) * 4") == "20"
    assert evaluate_expression("10 - 2 * 3 + 4 / 2") == "6"
    assert evaluate_expression("(10 - 2) * (3 + 4) / 2") == "28"
    assert evaluate_expression("((2 + 3) * 2 - 2) / 2") == "4"


def test_unary_operators():
    """Garante tratamento correto de sinais unários positivos e negativos."""
    assert evaluate_expression("-5 + 3") == "-2"
    assert evaluate_expression("+5 + -3") == "2"
    assert evaluate_expression("-(-5)") == "5"
    assert evaluate_expression("5 * -2") == "-10"


def test_division_by_zero():
    """Garante captura controlada de divisão por zero."""
    with pytest.raises(DivisionByZeroError) as exc_info:
        evaluate_expression("10 / 0")
    assert "DIVISÃO POR ZERO" in str(exc_info.value)

    with pytest.raises(DivisionByZeroError):
        evaluate_expression("5 / (2 - 2)")


def test_security_rejection_of_unauthorized_nodes():
    """Garante rejeição de qualquer tentativa de injeção ou nós não autorizados."""
    # Chamadas de função e importações
    with pytest.raises(CalculatorError):
        evaluate_expression("__import__('os').system('calc')")

    with pytest.raises(CalculatorError):
        evaluate_expression("eval('1 + 1')")

    with pytest.raises(CalculatorError):
        evaluate_expression("open('secret.txt')")

    # Acesso a atributos
    with pytest.raises(CalculatorError):
        evaluate_expression("(1).__class__")

    # Operadores não autorizados (YAGNI / Escopo de 4 operações)
    with pytest.raises(CalculatorError):
        evaluate_expression("2 ** 3")

    with pytest.raises(CalculatorError):
        evaluate_expression("5 % 2")


def test_visual_operator_sanitization():
    """Garante substituição de símbolos visuais × e ÷."""
    assert evaluate_expression("10 × 5") == "50"
    assert evaluate_expression("20 ÷ 4") == "5"
    assert evaluate_expression("(15 × 2) ÷ 6") == "5"


def test_edge_cases():
    """Garante estabilidade para entradas vazias ou com espaços."""
    assert evaluate_expression("") == "0"
    assert evaluate_expression("   ") == "0"
    assert evaluate_expression("  42  ") == "42"
