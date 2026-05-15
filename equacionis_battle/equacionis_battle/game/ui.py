"""
ui.py  (REESCRITO - agora usa PNGs dos assets)
----------------------------------------
Funcoes de desenho que usam os assets de HUD e renderizam texto dinamico
por cima (nome, level, HP numerico, mensagens).

As coordenadas das barras verdes dentro dos PNGs foram medidas uma vez:
  hud_hp_enemy  (439x234): barra em x=144-377, y=139-153  (234x15 px)
  hud_hp_player (471x293): barra em x=171-403, y=159-173  (233x15 px)

Sao tratadas como PROPORCOES do PNG, entao funciona se for escalado.
"""
import pygame
from . import constants as C
from . import assets_loader as AL


# ===================================================================
#  FONTES (carrega uma vez - arial bold eh bem legivel)
# ===================================================================
_fonts = {}
def _font(tamanho, bold=True):
    key = (tamanho, bold)
    if key not in _fonts:
        _fonts[key] = pygame.font.SysFont("arial", tamanho, bold=bold)
    return _fonts[key]


# ===================================================================
#  PROPORCAO DAS BARRAS VERDES DENTRO DOS ASSETS
# ===================================================================
# (x_ini%, x_fim%, y_ini%, y_fim%) em relacao ao tamanho do asset
BAR_PROP_ENEMY  = (144/439, 377/439, 139/234, 153/234)
BAR_PROP_PLAYER = (171/471, 403/471, 159/293, 173/293)

# Tamanhos finais das HUDs na tela
HP_ENEMY_SIZE  = (280, 149)
HP_PLAYER_SIZE = (300, 187)


# ===================================================================
#  ARENA (background PNG)
# ===================================================================
def draw_arena(surface):
    bg = AL.get_background()
    if bg is None:
        # fallback simples
        surface.fill(C.ARENA_SKY_BOTTOM)
        return
    # escala o bg para cobrir toda a tela acima da caixa inferior
    escalado = pygame.transform.smoothscale(bg, (C.SCREEN_WIDTH, C.SCREEN_HEIGHT))
    surface.blit(escalado, (0, 0))


# ===================================================================
#  CAIXA DE HP (usa o PNG e sobrepoe texto + mascara da barra)
# ===================================================================
def draw_hp_box(surface, x, y, nome, level, hp, hp_max, mostrar_exp=False):
    """
    Desenha a caixa de HP usando a imagem real.
    hp pode ser FLOAT (HP visual suave) - a barra reflete isso.
    """
    asset_key = "hud_hp_player" if mostrar_exp else "hud_hp_enemy"
    asset = AL.get_ui(asset_key)
    if asset is None:
        return  # sem asset, nao desenha

    size = HP_PLAYER_SIZE if mostrar_exp else HP_ENEMY_SIZE
    prop = BAR_PROP_PLAYER if mostrar_exp else BAR_PROP_ENEMY

    # escala e desenha a caixa
    caixa = pygame.transform.smoothscale(asset, size)
    surface.blit(caixa, (x, y))

    # ---- mascara da barra de HP perdido ----
    bw, bh = size
    bar_x1 = int(bw * prop[0])
    bar_x2 = int(bw * prop[1])
    bar_y1 = int(bh * prop[2])
    bar_y2 = int(bh * prop[3])
    bar_w  = bar_x2 - bar_x1
    bar_h  = bar_y2 - bar_y1

    proporcao = max(0.0, min(1.0, hp / hp_max))
    preenchido = int(bar_w * proporcao)
    falta      = bar_w - preenchido

    if falta > 0:
        # cobre a parte direita da barra com cor escura
        pygame.draw.rect(surface, (60, 50, 40),
                         (x + bar_x1 + preenchido, y + bar_y1, falta, bar_h))

    # muda a cor da parte restante conforme o HP cai
    if proporcao < 0.5 and preenchido > 0:
        cor = C.HP_YELLOW if proporcao >= 0.2 else C.HP_RED
        pygame.draw.rect(surface, cor,
                         (x + bar_x1, y + bar_y1, preenchido, bar_h))

    # ---- texto: nome e level em cima ----
    txt_nome = _font(int(bh * 0.17)).render(nome, True, C.BORDER_DARK)
    surface.blit(txt_nome, (x + int(bw * 0.08), y + int(bh * 0.08)))
    txt_lv = _font(int(bh * 0.13)).render(f"Lv.{level}", True, C.BORDER_DARK)
    surface.blit(txt_lv, (x + bw - txt_lv.get_width() - int(bw * 0.06),
                          y + int(bh * 0.12)))

    # HP numerico abaixo da barra (somente no HUD do jogador)
    if mostrar_exp:
        hp_int = int(hp)
        txt_hp = _font(int(bh * 0.11)).render(f"{hp_int}/ {hp_max}", True, C.BORDER_DARK)
        surface.blit(txt_hp, (x + bw - txt_hp.get_width() - int(bw * 0.1),
                              y + bar_y2 + int(bh * 0.05)))


# ===================================================================
#  CAIXA DE DIALOGO
# ===================================================================
DIALOG_SIZE = (460, 130)

def draw_dialog_box(surface, texto_visivel: str, mostrar_seta: bool = False):
    asset = AL.get_ui("hud_dialogbox_big")
    if asset is None:
        return

    dx, dy = C.POS_DIALOG
    caixa = pygame.transform.smoothscale(asset, DIALOG_SIZE)
    surface.blit(caixa, (dx, dy))

    fonte = _font(20)
    linhas = texto_visivel.split("\n")
    for i, linha in enumerate(linhas[:3]):
        txt = fonte.render(linha, True, (245, 240, 220))
        surface.blit(txt, (dx + 28, dy + 28 + i * 28))

    if mostrar_seta:
        _desenhar_seta_piscando(surface,
                                dx + DIALOG_SIZE[0] - 40,
                                dy + DIALOG_SIZE[1] - 42)


# ===================================================================
#  MENU DE ACAO (LUTAR / MOCHILA / EQUACAO / FUGIR)
# ===================================================================
OPCOES_MENU = ["LUTAR", "MOCHILA", "EQUACAO", "FUGIR"]
MENU_SIZE   = (290, 130)

def draw_action_menu(surface, indice_selecionado: int):
    asset = AL.get_ui("hud_menuaction")
    if asset is None:
        return
    mx, my = C.POS_MENU
    caixa = pygame.transform.smoothscale(asset, MENU_SIZE)
    surface.blit(caixa, (mx, my))

    fonte = _font(20)
    col_w = MENU_SIZE[0] // 2
    row_h = MENU_SIZE[1] // 2
    for i, opcao in enumerate(OPCOES_MENU):
        col = i % 2
        row = i // 2
        ox = mx + col * col_w + 45
        oy = my + row * row_h + 28
        txt = fonte.render(opcao, True, C.BORDER_DARK)
        surface.blit(txt, (ox, oy))
        if i == indice_selecionado:
            _desenhar_seta_menu(surface, ox - 20, oy + 4)


# ===================================================================
#  SELECAO DE DIFICULDADE
# ===================================================================
OPCOES_DIF = [("FACIL", "facil"), ("MEDIO", "medio"), ("DIFICIL", "dificil")]

def draw_difficulty_menu(surface, indice_selecionado: int):
    asset = AL.get_ui("hud_menuaction")
    if asset is None:
        return
    mx, my = C.POS_MENU
    caixa = pygame.transform.smoothscale(asset, MENU_SIZE)
    surface.blit(caixa, (mx, my))

    fonte = _font(19)
    for i, (label, _) in enumerate(OPCOES_DIF):
        ox = mx + 45
        oy = my + 18 + i * 30
        txt = fonte.render(label, True, C.BORDER_DARK)
        surface.blit(txt, (ox, oy))
        if i == indice_selecionado:
            _desenhar_seta_menu(surface, ox - 20, oy + 4)


# ===================================================================
#  CAIXA DE INPUT
# ===================================================================
INPUT_SIZE = (760, 130)

def draw_input_box(surface, texto_digitado: str, equacao: str):
    asset = AL.get_ui("hud_textbox") or AL.get_ui("hud_dialogbox_big")
    if asset is None:
        return

    ix, iy = C.POS_INPUT
    caixa = pygame.transform.smoothscale(asset, INPUT_SIZE)
    surface.blit(caixa, (ix, iy))

    # label da equacao
    fonte_lbl = _font(18)
    lbl = fonte_lbl.render(f"Resolva:  {equacao}", True, (245, 240, 220))
    surface.blit(lbl, (ix + 28, iy + 20))

    # campo de input com cursor piscante
    fonte_in = pygame.font.SysFont("consolas", 28, bold=True)
    cursor = "|" if (pygame.time.get_ticks() // 400) % 2 == 0 else " "
    prompt = f"> {texto_digitado}{cursor}"
    txt = fonte_in.render(prompt, True, (110, 230, 180))
    surface.blit(txt, (ix + 28, iy + 58))

    fonte_dica = _font(13)
    dica = fonte_dica.render("ENTER para confirmar | BACKSPACE para apagar",
                             True, (200, 200, 210))
    surface.blit(dica, (ix + 28, iy + INPUT_SIZE[1] - 28))


# ===================================================================
#  TELAS FINAIS
# ===================================================================
def draw_end_screen(surface, vitoria: bool):
    overlay = pygame.Surface((C.SCREEN_WIDTH, C.SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 190))
    surface.blit(overlay, (0, 0))

    fonte_t = _font(56)
    fonte_s = _font(22)

    if vitoria:
        titulo, sub, cor = "VITORIA!", "EQUACIONIS foi derrotado!", (230, 210, 90)
    else:
        titulo, sub, cor = "DERROTA", "Voce foi nocauteado pela algebra...", (220, 90, 90)

    txt_t = fonte_t.render(titulo, True, cor)
    surface.blit(txt_t, (C.SCREEN_WIDTH // 2 - txt_t.get_width() // 2, 180))

    txt_s = fonte_s.render(sub, True, C.WHITE)
    surface.blit(txt_s, (C.SCREEN_WIDTH // 2 - txt_s.get_width() // 2, 260))

    btn = pygame.Rect(C.SCREEN_WIDTH // 2 - 140, 340, 280, 54)
    pygame.draw.rect(surface, C.CREAM, btn, border_radius=8)
    pygame.draw.rect(surface, C.BORDER_DARK, btn, 3, border_radius=8)
    txt_b = _font(20).render("Jogar novamente [R]", True, C.BORDER_DARK)
    surface.blit(txt_b, (btn.centerx - txt_b.get_width() // 2,
                         btn.centery - txt_b.get_height() // 2))

    dica = fonte_s.render("Pressione R para reiniciar  |  ESC para sair",
                          True, (200, 200, 210))
    surface.blit(dica, (C.SCREEN_WIDTH // 2 - dica.get_width() // 2, 420))


# ===================================================================
#  HELPERS: setas
# ===================================================================
def _desenhar_seta_menu(surface, x, y):
    asset = AL.get_ui("hud_black_arrow")
    if asset is not None:
        mini = pygame.transform.smoothscale(asset, (14, 14))
        surface.blit(mini, (x, y))
    else:
        pygame.draw.polygon(surface, C.BORDER_DARK,
                            [(x, y), (x + 12, y + 6), (x, y + 12)])


def _desenhar_seta_piscando(surface, x, y):
    if (pygame.time.get_ticks() // 350) % 2 == 0:
        asset = AL.get_ui("hud_red_arrow")
        if asset is not None:
            mini = pygame.transform.smoothscale(asset, (22, 16))
            surface.blit(mini, (x, y))
        else:
            pygame.draw.polygon(surface, (220, 60, 60),
                                [(x, y), (x + 20, y), (x + 10, y + 14)])
