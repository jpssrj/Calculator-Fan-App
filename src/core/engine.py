"""Motor aritmético de alta precisão em passada única via AST e decimal.Decimal."""

import ast
from decimal import Decimal, DivisionByZero, InvalidOperation, Overflow, getcontext

# Configura precisão de 34 dígitos decimais (padrão IEEE 754 decimal128)
getcontext().prec = 34


class CalculatorError(Exception):
    """Exceção base para erros na calculadora."""

    pass


class DivisionByZeroError(CalculatorError):
    """Tentativa de divisão por zero."""

    pass


class SecuritySyntaxError(CalculatorError):
    """Sintaxe inválida ou uso de nós não autorizados na AST."""

    pass


def format_decimal(val: Decimal) -> str:
    """Formata um Decimal sem notação científica espúria e sem zeros redundantes."""
    s = f"{val:f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s if s != "-0" else "0"


class ASTAritmeticEvaluator:
    """Avaliador recursivo em passada única para expressões aritméticas seguras."""

    def evaluate(self, node: ast.AST) -> Decimal:
        if isinstance(node, ast.Expression):
            return self.evaluate(node.body)

        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float, Decimal)):
                return Decimal(str(node.value))
            raise SecuritySyntaxError("SINTAXE INVÁLIDA")

        if isinstance(node, ast.UnaryOp):
            operand = self.evaluate(node.operand)
            if isinstance(node.op, ast.UAdd):
                return +operand
            if isinstance(node.op, ast.USub):
                return -operand
            raise SecuritySyntaxError("SINTAXE INVÁLIDA")

        if isinstance(node, ast.BinOp):
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)

            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                if right == 0:
                    raise DivisionByZeroError("DIVISÃO POR ZERO")
                try:
                    return left / right
                except DivisionByZero:
                    raise DivisionByZeroError("DIVISÃO POR ZERO")

            raise SecuritySyntaxError("SINTAXE INVÁLIDA")

        # Qualquer outro tipo de nó (Call, Attribute, Name, Pow, Mod, List, etc.)
        raise SecuritySyntaxError("SINTAXE INVÁLIDA")


def evaluate_expression(expr: str) -> str:
    """Valida, calcula e formata uma expressão matemática com precisão decimal128.

    Args:
        expr: String com a expressão (ex: '25.5 * (4 + 6) / 2')

    Returns:
        Resultado formatado como string limpa.

    Raises:
        DivisionByZeroError: Se houver tentativa de divisão por zero.
        CalculatorError: Se houver erro de sintaxe, operação inválida ou overflow.
    """
    if not expr or not expr.strip():
        return "0"

    # Sanitização de operadores visuais comuns
    sanitized = expr.strip().replace("×", "*").replace("÷", "/")

    try:
        parsed = ast.parse(sanitized, mode="eval")
    except SyntaxError:
        raise CalculatorError("SINTAXE INVÁLIDA")

    evaluator = ASTAritmeticEvaluator()

    try:
        result = evaluator.evaluate(parsed)
        return format_decimal(result)
    except DivisionByZeroError:
        raise
    except DivisionByZero:
        raise DivisionByZeroError("DIVISÃO POR ZERO")
    except InvalidOperation:
        raise CalculatorError("OPERAÇÃO INVÁLIDA")
    except Overflow:
        raise CalculatorError("ESTOURO DE CAPACIDADE")
    except CalculatorError:
        raise
    except Exception:
        raise CalculatorError("SINTAXE INVÁLIDA")
