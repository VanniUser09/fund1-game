# Equacionis — Batalha Matemática no Estilo Pokémon Emerald

Jogo 2D em Python/Pygame que reproduz a composição visual de uma batalha clássica de Pokémon (jogador de costas na parte inferior, boss flutuando na superior, barras de HP, caixa de diálogo e menu de ação), com uma mecânica própria: o boss lança equações de 1º e 2º grau, e você ataca digitando a resposta no formato Python (`x=3`).

![estilo](https://img.shields.io/badge/engine-pygame-1abc9c) ![python](https://img.shields.io/badge/python-3.10%2B-blue)

---

## Estrutura de arquivos

```
equacionis_battle/
├── main.py                 # Ponto de entrada. Loop principal do pygame.
├── requirements.txt        # Dependências (pygame)
├── README.md               # Este arquivo
├── assets/
│   └── sprites/            # (opcional) PNGs para substituir os sprites desenhados
└── game/
    ├── __init__.py
    ├── constants.py        # HP, dano, cores, estados, velocidades de animação
    ├── equations.py        # Gerador e validador de equações
    ├── sprites.py          # Desenho procedural de jogador e boss
    ├── animation.py        # Timers, shake, hop, bob, flash
    ├── ui.py               # Barras de HP, caixa de diálogo, menu, input, tela final
    └── battle.py           # Máquina de estados da batalha
```

---

## Como rodar

Python 3.10 ou superior.

```bash
# 1) Crie um ambiente virtual (recomendado)
python -m venv .venv
source .venv/bin/activate       # Linux / macOS
# .venv\Scripts\activate        # Windows

# 2) Instale a dependência
pip install -r requirements.txt

# 3) Rode o jogo
python main.py
```

### Controles

| Tecla | Ação |
|-------|------|
| Setas / WASD | Navegar nos menus |
| ENTER, SPACE ou Z | Confirmar / avançar |
| ESC | Voltar um passo no menu (ou fechar na tela final) |
| BACKSPACE | Apagar caractere durante o input |
| R | Reiniciar depois de vitória ou derrota |

---

## Fluxo da batalha

```
INTRO ("EQUACIONIS apareceu!")
   |
   v
MENU (LUTAR / MOCHILA / EQUACAO / FUGIR)
   |   LUTAR ou EQUACAO
   v
DIFICULDADE (FACIL / MEDIO / DIFICIL)
   |
   v
EQUATION_SHOW  ("EQUACIONIS lançou: 2x + 3 = 11")
   |
   v
INPUT  (você digita sua resposta, ex: x=4)
   |
   +-- acertou? --> PLAYER_ATTACK (dano no boss) --> MESSAGE --> volta a DIFICULDADE
   |
   +-- errou?   --> BOSS_ATTACK   (dano em você) --> MESSAGE --> volta a DIFICULDADE

Quando HP do boss chega a 0 -> VITÓRIA
Quando HP do jogador chega a 0 -> DERROTA (tecla R reinicia)
```

---

## Explicação da validação das respostas

A função `validar_resposta(resposta, solucoes)` em `game/equations.py` faz:

1. Converte tudo para minúsculas e tira espaços.
2. Substitui toda ocorrência de `x=` por vírgula, unificando formatos.
3. Extrai todos os inteiros (positivos e negativos) com regex `-?\d+`.
4. Considera acerto se **qualquer** número digitado estiver na lista de soluções corretas.

Formatos aceitos (todos passam):

| Entrada | Interpretada como |
|---------|-------------------|
| `x=3` | 3 |
| `X = -3` | -3 |
| ` x = 5 ` | 5 |
| `x=3,-2` | 3, -2 |
| `x=3, x=-2` | 3, -2 |
| `7` | 7 (também aceita só o número) |

Para equações de 2º grau com duas raízes, digitar **qualquer uma delas** já conta como acerto. Se preferir exigir as duas, basta mudar a linha final de `validar_resposta`:

```python
# Exige TODAS as raízes (modo difícil de verdade):
return set(valores) == set(solucoes)
```

---

## Pontos do código para você personalizar

### 1) Mudar HP inicial
`game/constants.py`:
```python
PLAYER_MAX_HP = 100
BOSS_MAX_HP   = 200
```

### 2) Mudar o dano por dificuldade
`game/constants.py`:
```python
DAMAGE_ON_HIT = {
    "facil":   5,
    "medio":   10,
    "dificil": 20,
}
DAMAGE_ON_FAIL = {
    "facil":   5,
    "medio":   10,
    "dificil": 15,
}
```

### 3) Ajustar faixa de números nas equações
`game/equations.py`, funções `_gerar_primeiro_grau_simples`, `_gerar_primeiro_grau_intermediario` e `_gerar_segundo_grau`. Exemplo para deixar o “difícil” mais difícil:

```python
def _gerar_segundo_grau():
    r1 = random.randint(-9, 9)   # antes era -5, 5
    r2 = random.randint(-9, 9)
    ...
```

### 4) Adicionar uma quarta dificuldade
Em `game/ui.py` adicione na lista `OPCOES_DIF`, em `constants.py` adicione a chave no dicionário `DAMAGE_ON_HIT` e em `equations.py` adicione uma função geradora. A máquina de estados pega automaticamente.

### 5) Nomes, níveis e cores da UI
`game/constants.py`:
```python
PLAYER_NAME  = "NERD"
PLAYER_LEVEL = 25
BOSS_NAME    = "EQUACIONIS"
BOSS_LEVEL   = 80
```
Toda a paleta também está nesse arquivo (`SKIN`, `HAIR`, `BACKPACK`, `BOSS_AURA`, etc.).

### 6) Trocar os sprites por PNGs reais

Coloque em `assets/sprites/` os arquivos:
```
player_idle.png
player_attack.png
player_hurt.png
boss_idle.png
boss_attack.png
boss_hurt.png
```
Recomendações de tamanho: jogador ~160×200 px, boss ~260×300 px, fundo transparente.

O `main.py` já chama `sprites.carregar_externos("assets/sprites")` no início. Qualquer PNG presente substitui automaticamente o sprite desenhado programaticamente. Se só tiver `boss_idle.png`, só o boss idle é trocado — os outros continuam desenhados.

### 7) Ajustar animações
`game/constants.py`:
```python
ANIM_ATTACK_DURATION  = 45    # frames da animação de ataque
ANIM_DAMAGE_DURATION  = 30    # flash de dano
ANIM_MESSAGE_DURATION = 90    # tempo das mensagens intermediárias
```

Para mudar o *tipo* de movimento (shake, pulo, flutuação) olhe em `game/animation.py`: as funções `shake_offset`, `hop_offset` e `bob_offset` estão documentadas e são chamadas dentro de `battle.py → render()`.

---

## Sistema de animação em três estados

Cada sprite tem três versões: `idle`, `attack`, `hurt`.

No `battle.py → render()`, o estado do sprite muda conforme o estado da batalha:

| Estado da batalha | Jogador | Boss |
|-------------------|---------|------|
| INTRO, MENU, DIFFICULTY, EQUATION_SHOW, INPUT | `idle` | `idle` + flutuação |
| PLAYER_ATTACK (1ª metade) | `attack` + pulinho + desloca pra frente | `idle` |
| PLAYER_ATTACK (2ª metade) | `attack` | `hurt` + shake |
| BOSS_ATTACK (1ª metade) | `idle` | `attack` + glifo mágico |
| BOSS_ATTACK (2ª metade) | `hurt` + shake | `attack` |

Os offsets de posição (`hop_offset`, `shake_offset`) são somados à posição base do sprite antes do `blit`, o que dá o efeito de pulo/tremor sem frames extras.

---

## Teste rápido das equações sem abrir o jogo

```bash
python -m game.equations
```

Saída esperada (exemplo):
```
[facil] x + 6 = 13  -> solucoes = [7]
[medio] 3x - 4 = 2  -> solucoes = [2]
[dificil] x^2 - x - 6 = 0  -> solucoes = [3, -2]

Validacao:
  OK  'x=3' vs [3] -> True
  OK  'X = -3' vs [-3] -> True
  ...
```

---

## Checklist de entrega (o que foi construído)

- [x] Código completo funcional (Pygame)
- [x] Arquitetura modular (equações, sprites, animação, UI, batalha, constantes)
- [x] Layout estilo Pokémon: jogador inferior de costas, boss superior flutuante
- [x] Barras de HP coloridas (verde → amarelo → vermelho) com nome e level
- [x] Caixa de diálogo inferior + menu de ação (LUTAR/MOCHILA/EQUAÇÃO/FUGIR)
- [x] Sistema de turnos
- [x] Gerador de equações 1º e 2º grau com três dificuldades
- [x] Validação aceitando `x=3`, `x = 3`, `-3`, etc.
- [x] Dano configurável por dificuldade (5 / 10 / 20)
- [x] Animações idle, ataque e dano + shake, hop e bob
- [x] Tela de vitória e derrota com reinício (tecla R)
- [x] Glifo mágico atrás do boss durante o ataque
- [x] Sprites trocáveis por PNGs sem tocar na lógica

Bons estudos e boas batalhas algébricas!
