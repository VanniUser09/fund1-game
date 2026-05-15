"""
equations.py
----------------------------------------
Gerador e validador de equacoes matematicas.

- gerar_equacao(dificuldade) -> (texto, lista_de_solucoes)
- validar_resposta(resposta, solucoes) -> bool

FORMATO ACEITO do jogador:
  x=3          |  x = 3
  x=-3         |  X = -3
  x=3,-2       |  x=3, x=-2   (para 2 grau)
  3            |  -3          (so o numero, tambem vale)
"""
import random
import re


# ===================================================================
#  GERACAO
# ===================================================================
def gerar_equacao(dificuldade: str):
    """
    Retorna (texto_para_exibir, [solucoes_inteiras]).

    facil   -> 1 grau simples:  x + b = c
    medio   -> 1 grau com coef: ax + b = c
    dificil -> 2 grau:          x^2 + bx + c = 0
    """
    if dificuldade == "facil":
        return _gerar_primeiro_grau_simples()
    if dificuldade == "medio":
        return _gerar_primeiro_grau_intermediario()
    return _gerar_segundo_grau()


def _gerar_primeiro_grau_simples():
    """x + b = c ou x - b = c, com x e b inteiros pequenos."""
    x = random.randint(1, 9)
    b = random.randint(1, 9)
    if random.choice([True, False]):
        c = x + b
        texto = f"x + {b} = {c}"
    else:
        c = x - b
        if c >= 0:
            texto = f"x - {b} = {c}"
        else:
            texto = f"x - {b} = {c}"
    return texto, [x]


def _gerar_primeiro_grau_intermediario():
    """ax + b = c, com a entre 2 e 5 e x podendo ser negativo."""
    a = random.randint(2, 5)
    x = random.randint(-5, 9)
    b = random.randint(-9, 9)
    c = a * x + b
    if b >= 0:
        texto = f"{a}x + {b} = {c}"
    else:
        texto = f"{a}x - {abs(b)} = {c}"
    return texto, [x]


def _gerar_segundo_grau():
    """
    Gera (x - r1)(x - r2) = 0 garantindo raizes inteiras.
    Expande para x^2 + bx + c = 0.
    """
    r1 = random.randint(-5, 5)
    r2 = random.randint(-5, 5)

    soma = r1 + r2
    prod = r1 * r2
    termo_b = -soma   # coeficiente de x
    termo_c = prod

    partes = ["x^2"]
    if termo_b > 0:
        partes.append(f"+ {termo_b}x")
    elif termo_b < 0:
        partes.append(f"- {abs(termo_b)}x")
    # se termo_b == 0 nada e adicionado

    if termo_c > 0:
        partes.append(f"+ {termo_c}")
    elif termo_c < 0:
        partes.append(f"- {abs(termo_c)}")

    texto = " ".join(partes) + " = 0"
    solucoes = list(set([r1, r2]))   # elimina duplicata se r1 == r2
    return texto, solucoes


# ===================================================================
#  VALIDACAO
# ===================================================================
def validar_resposta(resposta_str: str, solucoes: list) -> bool:
    """
    Recebe o que o jogador digitou e a lista de solucoes corretas.
    Aceita qualquer uma das raizes como resposta correta (para simplificar).
    """
    if not resposta_str:
        return False

    # Normaliza: minusculas, sem espacos
    s = resposta_str.lower().replace(" ", "")

    # Remove "x=" em qualquer ocorrencia, troca por virgula
    s = s.replace("x=", ",")

    # Extrai todos os inteiros (com sinal) do que sobrou
    numeros = re.findall(r"-?\d+", s)
    if not numeros:
        return False

    try:
        valores = [int(n) for n in numeros]
    except ValueError:
        return False

    # Acerto se pelo menos um valor informado for uma das solucoes
    return any(v in solucoes for v in valores)


# ===================================================================
#  TESTE RAPIDO (rode "python -m game.equations" pra conferir)
# ===================================================================
if __name__ == "__main__":
    for dif in ["facil", "medio", "dificil"]:
        texto, sols = gerar_equacao(dif)
        print(f"[{dif}] {texto}  -> solucoes = {sols}")

    # teste do validador
    testes = [
        ("x=3",      [3],      True),
        ("X = -3",   [-3],     True),
        (" x = 5 ",  [5],      True),
        ("x=3,-2",   [3, -2],  True),
        ("7",        [7],      True),
        ("x=4",      [3],      False),
        ("",         [1],      False),
        ("abc",      [1],      False),
    ]
    print("\nValidacao:")
    for entrada, sols, esperado in testes:
        got = validar_resposta(entrada, sols)
        ok = "OK" if got == esperado else "FAIL"
        print(f"  {ok}  '{entrada}' vs {sols} -> {got}")
