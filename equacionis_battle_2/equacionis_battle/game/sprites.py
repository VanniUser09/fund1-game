"""
sprites.py
----------------------------------------
Desenha jogador e boss programaticamente (sem assets externos).

COMO SUBSTITUIR POR PNGs:
  Basta colocar arquivos em assets/sprites/ com os nomes:
    player_idle.png, player_attack.png, player_hurt.png
    boss_idle.png,   boss_attack.png,   boss_hurt.png
  e chamar sprites.carregar_externos(caminho_base).
  O jogo detectara os PNGs e usara no lugar dos desenhados.
"""
import os
import math
import pygame
from . import constants as C


# Cache interno de sprites ja renderizados
_cache = {}


# ===================================================================
#  API publica
# ===================================================================
def get_player_sprite(estado: str) -> pygame.Surface:
    """estado: 'idle' | 'attack' | 'hurt'"""
    key = f"player_{estado}"
    if key not in _cache:
        _cache[key] = _desenhar_player(estado)
    return _cache[key]


def get_boss_sprite(estado: str) -> pygame.Surface:
    """estado: 'idle' | 'attack' | 'hurt'"""
    key = f"boss_{estado}"
    if key not in _cache:
        _cache[key] = _desenhar_boss(estado)
    return _cache[key]


def carregar_externos(pasta: str):
    """
    Tenta substituir sprites pelos PNGs da pasta informada.
    Se um arquivo nao existir, mantem o desenho programatico.
    """
    nomes = [
        "player_idle", "player_attack", "player_hurt",
        "boss_idle",   "boss_attack",   "boss_hurt",
    ]
    for nome in nomes:
        caminho = os.path.join(pasta, f"{nome}.png")
        if os.path.isfile(caminho):
            try:
                img = pygame.image.load(caminho).convert_alpha()
                _cache[nome] = img
                print(f"[sprites] carregado: {caminho}")
            except pygame.error as e:
                print(f"[sprites] falhou ao carregar {caminho}: {e}")


# ===================================================================
#  JOGADOR (de costas, com mochila e folha)
# ===================================================================
def _desenhar_player(estado: str) -> pygame.Surface:
    """
    Jogador visto por tras: cabeca, torso coberto por mochila grande,
    pernas, e uma folha branca surgindo nos lados quando em ataque.
    """
    W, H = 160, 200
    surf = pygame.Surface((W, H), pygame.SRCALPHA)

    # sombra no chao
    pygame.draw.ellipse(surf, (0, 0, 0, 80), (20, H - 16, W - 40, 12))

    # pernas (calca azul escura)
    pygame.draw.rect(surf, C.PANTS, (52, 130, 22, 60))
    pygame.draw.rect(surf, C.PANTS, (86, 130, 22, 60))
    # sapatos
    pygame.draw.rect(surf, (30, 25, 20), (48, 182, 28, 10))
    pygame.draw.rect(surf, (30, 25, 20), (84, 182, 28, 10))

    # torso / camisa (so aparece nas laterais da mochila)
    pygame.draw.rect(surf, C.SHIRT, (40, 70, 80, 70))

    # mochila (bloco marrom grande)
    pygame.draw.rect(surf, C.BACKPACK, (44, 72, 72, 75), border_radius=4)
    # sombra lateral da mochila
    pygame.draw.rect(surf, C.BACKPACK_DARK, (44, 72, 8, 75), border_radius=2)
    pygame.draw.rect(surf, C.BACKPACK_DARK, (108, 72, 8, 75), border_radius=2)
    # costura no meio
    pygame.draw.line(surf, C.BACKPACK_DARK, (80, 75), (80, 145), 2)
    # pins da mochila (detalhe nerd)
    pygame.draw.circle(surf, (220, 80, 80), (60, 95), 4)    # vermelho
    pygame.draw.circle(surf, (80, 160, 220), (100, 95), 4)  # azul
    # patch "E=mc²"
    pygame.draw.rect(surf, (240, 230, 200), (58, 115, 44, 14))
    font = pygame.font.SysFont("arial", 9, bold=True)
    txt = font.render("E=mc2", True, (40, 30, 20))
    surf.blit(txt, (61, 116))

    # alcas da mochila (em cima do ombro)
    pygame.draw.rect(surf, C.BACKPACK_DARK, (46, 66, 10, 20), border_radius=2)
    pygame.draw.rect(surf, C.BACKPACK_DARK, (104, 66, 10, 20), border_radius=2)

    # cabeca (nuca com cabelo castanho)
    pygame.draw.ellipse(surf, C.HAIR, (52, 22, 56, 56))
    # brilho do cabelo
    pygame.draw.ellipse(surf, (135, 90, 55), (58, 28, 20, 10))
    # orelhas (faixinhas de pele)
    pygame.draw.rect(surf, C.SKIN, (50, 46, 4, 10), border_radius=2)
    pygame.draw.rect(surf, C.SKIN, (106, 46, 4, 10), border_radius=2)
    # pescoco
    pygame.draw.rect(surf, C.SKIN, (68, 72, 24, 8))

    # bracos / maos segurando folha
    if estado in ("idle", "attack"):
        # braco direito (para o espectador = esquerdo da surface)
        offset_y = -6 if estado == "attack" else 0
        pygame.draw.rect(surf, C.SHIRT, (28, 95 + offset_y, 18, 40))
        pygame.draw.circle(surf, C.SKIN, (37, 135 + offset_y), 9)
        # folha branca sendo erguida (aparece mais no ataque)
        tamanho = 40 if estado == "attack" else 28
        px, py = 8, 110 + offset_y
        if estado == "attack":
            px, py = 6, 80
        pygame.draw.rect(surf, C.PAPER, (px, py, tamanho, tamanho + 6))
        pygame.draw.rect(surf, (180, 170, 150), (px, py, tamanho, tamanho + 6), 1)
        # rabiscos na folha
        for i in range(4):
            y = py + 8 + i * 6
            pygame.draw.line(surf, (80, 80, 100),
                             (px + 4, y), (px + tamanho - 4, y), 1)

        # braco esquerdo (direita da surface)
        pygame.draw.rect(surf, C.SHIRT, (114, 95, 18, 40))
        pygame.draw.circle(surf, C.SKIN, (123, 135), 9)

    # estado HURT: tom avermelhado sobreposto
    if estado == "hurt":
        vermelho = pygame.Surface((W, H), pygame.SRCALPHA)
        vermelho.fill((220, 60, 60, 90))
        surf.blit(vermelho, (0, 0))

    return surf


# ===================================================================
#  BOSS (Equacionis) - silhueta alada flutuante roxa e dourada
# ===================================================================
def _desenhar_boss(estado: str) -> pygame.Surface:
    """
    Figura vertical: aura violeta, asas douradas/roxas em leque,
    corpo escuro alongado e rosto palido. Em ataque, glifo atras.
    Em dano, tudo mais claro com respingos.
    """
    W, H = 260, 300
    surf = pygame.Surface((W, H), pygame.SRCALPHA)

    cx = W // 2

    # --- glifo magico (so no ataque) ---
    if estado == "attack":
        _desenhar_glifo(surf, cx, 140, 130)

    # --- aura violeta ao redor ---
    for r, alpha in [(130, 40), (100, 60), (75, 90)]:
        aura = pygame.Surface((W, H), pygame.SRCALPHA)
        pygame.draw.circle(aura, (*C.BOSS_AURA, alpha), (cx, 140), r)
        surf.blit(aura, (0, 0))

    # --- asas (triangulos em leque) ---
    _desenhar_asas(surf, cx, 120, lado=-1)  # esquerda
    _desenhar_asas(surf, cx, 120, lado=+1)  # direita

    # --- corpo (tunica longa escura) ---
    pontos_corpo = [
        (cx - 35, 110),
        (cx + 35, 110),
        (cx + 55, 230),
        (cx + 25, 270),
        (cx - 25, 270),
        (cx - 55, 230),
    ]
    pygame.draw.polygon(surf, C.BOSS_BODY, pontos_corpo)
    # borda clara
    pygame.draw.polygon(surf, C.BOSS_BODY_LT, pontos_corpo, 2)

    # detalhes dourados na tunica
    pygame.draw.line(surf, C.BOSS_GOLD, (cx, 115), (cx, 265), 2)
    pygame.draw.polygon(surf, C.BOSS_GOLD, [
        (cx - 15, 130), (cx + 15, 130),
        (cx + 10, 150), (cx - 10, 150),
    ])
    # pedra central
    pygame.draw.circle(surf, C.BOSS_GOLD_LT, (cx, 170), 6)
    pygame.draw.circle(surf, (255, 230, 150), (cx, 170), 3)

    # --- ombros / armadura ---
    pygame.draw.polygon(surf, C.BOSS_GOLD, [
        (cx - 40, 105), (cx - 55, 115), (cx - 50, 130), (cx - 30, 120),
    ])
    pygame.draw.polygon(surf, C.BOSS_GOLD, [
        (cx + 40, 105), (cx + 55, 115), (cx + 50, 130), (cx + 30, 120),
    ])

    # --- cabeca ---
    # coroa/elmo dourado
    pygame.draw.polygon(surf, C.BOSS_GOLD, [
        (cx - 22, 70), (cx - 18, 55), (cx - 8, 62),
        (cx, 50), (cx + 8, 62), (cx + 18, 55), (cx + 22, 70),
    ])
    # rosto (oval palido)
    pygame.draw.ellipse(surf, C.BOSS_FACE, (cx - 18, 68, 36, 44))
    # sombra do rosto
    pygame.draw.ellipse(surf, (200, 195, 190), (cx - 18, 68, 36, 44), 1)
    # olhos brilhantes (violeta)
    cor_olho = C.BOSS_EYES if estado != "attack" else (240, 180, 255)
    pygame.draw.circle(surf, cor_olho, (cx - 7, 88), 2)
    pygame.draw.circle(surf, cor_olho, (cx + 7, 88), 2)

    # --- base flutuante (sombra oval) ---
    pygame.draw.ellipse(surf, (0, 0, 0, 120), (cx - 60, 278, 120, 18))

    # --- estado HURT: respingos violeta e clareamento ---
    if estado == "hurt":
        clarao = pygame.Surface((W, H), pygame.SRCALPHA)
        clarao.fill((255, 255, 255, 100))
        surf.blit(clarao, (0, 0))
        # respingos
        import random as _r
        _r.seed(7)
        for _ in range(18):
            x = _r.randint(20, W - 20)
            y = _r.randint(40, H - 40)
            r = _r.randint(2, 6)
            pygame.draw.circle(surf, C.BOSS_AURA_LT, (x, y), r)

    return surf


def _desenhar_asas(surf, cx, cy, lado):
    """Desenha asas em leque; lado = -1 (esq) ou +1 (dir)."""
    base_x = cx + (30 * lado)
    for i in range(5):
        comp = 90 - i * 6
        tip_x = base_x + (comp * 0.9) * lado
        tip_y = cy + (i - 2) * 28
        mid_x = base_x + (comp * 0.4) * lado
        mid_y = cy + (i - 2) * 18
        cor = C.BOSS_BODY if i % 2 == 0 else C.BOSS_GOLD
        pygame.draw.polygon(surf, cor, [
            (base_x, cy + (i - 2) * 10),
            (mid_x, mid_y - 12),
            (tip_x, tip_y),
            (mid_x, mid_y + 12),
        ])
        # borda clara
        pygame.draw.polygon(surf, C.BOSS_GOLD_LT, [
            (base_x, cy + (i - 2) * 10),
            (mid_x, mid_y - 12),
            (tip_x, tip_y),
            (mid_x, mid_y + 12),
        ], 1)


def _desenhar_glifo(surf, cx, cy, raio):
    """Circulo magico atras do boss (so aparece em ataque)."""
    # dois aneis concentricos
    pygame.draw.circle(surf, (150, 90, 210, 180), (cx, cy), raio, 3)
    pygame.draw.circle(surf, (190, 130, 240, 160), (cx, cy), raio - 14, 2)
    # simbolos espalhados em 8 posicoes
    font = pygame.font.SysFont("arial", 16, bold=True)
    simbolos = ["S", "P", "a", "b", "x", "y", "p", "w"]  # ASCII safe
    for i, s in enumerate(simbolos):
        ang = math.radians(i * 45)
        sx = cx + math.cos(ang) * (raio - 7) - 6
        sy = cy + math.sin(ang) * (raio - 7) - 10
        txt = font.render(s, True, (230, 180, 255))
        surf.blit(txt, (sx, sy))
