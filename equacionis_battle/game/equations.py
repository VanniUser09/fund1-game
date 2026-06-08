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
  x=2,y=-1     |  2,-1        (para sistemas)
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
    dificil -> 2 grau:          x² + bx + c = 0
    mestre  -> sistema 2x2:     ax + by = c / dx + ey = f
    """
    if dificuldade == "facil":
        return _gerar_primeiro_grau_simples()
    if dificuldade == "medio":
        return _gerar_primeiro_grau_intermediario()
    if dificuldade == "dificil":
        return _gerar_segundo_grau()
    return _gerar_sistema_linear()


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
    Expande para x² + bx + c = 0.
    """
    r1 = random.randint(-5, 5)
    r2 = random.randint(-5, 5)

    soma = r1 + r2
    prod = r1 * r2
    termo_b = -soma   # coeficiente de x
    termo_c = prod

    partes = ["x²"]
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


def _formatar_termo(coef, var, primeiro=False):
    sinal = "" if primeiro or coef < 0 else "+ "
    if coef < 0:
        sinal = "- " if not primeiro else "-"
    valor = abs(coef)
    coef_txt = "" if valor == 1 else str(valor)
    return f"{sinal}{coef_txt}{var}"


def _gerar_sistema_linear():
    """Gera um sistema 2x2 com solucao inteira unica."""
    x = random.randint(-5, 5)
    y = random.randint(-5, 5)

    while True:
        a = random.randint(1, 5)
        b = random.randint(-5, 5) or 1
        d = random.randint(1, 5)
        e = random.randint(-5, 5) or -1
        if a * e - b * d != 0:
            break

    c = a * x + b * y
    f = d * x + e * y
    linha1 = f"{_formatar_termo(a, 'x', True)} {_formatar_termo(b, 'y')} = {c}"
    linha2 = f"{_formatar_termo(d, 'x', True)} {_formatar_termo(e, 'y')} = {f}"
    return f"{linha1}\n{linha2}", {"tipo": "sistema", "x": x, "y": y}


# ===================================================================
#  VALIDACAO
# ===================================================================
def validar_resposta(resposta_str: str, solucoes: list) -> bool:
    """
    Recebe o que o jogador digitou e a lista de solucoes corretas.
    Aceita qualquer uma das raizes como resposta correta (para simplificar).
    Para sistemas, exige x e y corretos.
    """
    if not resposta_str:
        return False

    # Normaliza: minusculas, sem espacos
    s = resposta_str.lower().replace(" ", "")

    if isinstance(solucoes, dict) and solucoes.get("tipo") == "sistema":
        pares = {var: int(valor) for var, valor in re.findall(r"([xy])=(-?\d+)", s)}
        if pares:
            return pares.get("x") == solucoes["x"] and pares.get("y") == solucoes["y"]

        numeros_sistema = re.findall(r"-?\d+", s)
        if len(numeros_sistema) >= 2:
            try:
                return int(numeros_sistema[0]) == solucoes["x"] and int(numeros_sistema[1]) == solucoes["y"]
            except ValueError:
                return False
        return False

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
    for dif in ["facil", "medio", "dificil", "mestre"]:
        texto, sols = gerar_equacao(dif)
        print(f"[{dif}] {texto}  -> solucoes = {sols}")

    # teste do validador
    testes = [
        ("x=3",      [3],      True),
        ("X = -3",   [-3],     True),
        (" x = 5 ",  [5],      True),
        ("x=3,-2",   [3, -2],  True),
        ("7",        [7],      True),
        ("x=2,y=-1", {"tipo": "sistema", "x": 2, "y": -1}, True),
        ("2,-1",     {"tipo": "sistema", "x": 2, "y": -1}, True),
        ("x=4",      [3],      False),
        ("",         [1],      False),
        ("abc",      [1],      False),
    ]
    print("\nValidacao:")
    for entrada, sols, esperado in testes:
        got = validar_resposta(entrada, sols)
        ok = "OK" if got == esperado else "FAIL"
        print(f"  {ok}  '{entrada}' vs {sols} -> {got}")
