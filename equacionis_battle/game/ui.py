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
#  FONTES (agora usa Pokemon Classic via assets_loader)
# ===================================================================
_fonts = {}
def _font(tamanho, bold=True):
    # bold eh ignorado - a fonte Pokemon Classic ja tem peso proprio
    if tamanho not in _fonts:
        _fonts[tamanho] = AL.get_fonte(tamanho)
    return _fonts[tamanho]


def _fit_font(texto, tamanho, largura_max, minimo=7):
    texto = str(texto)
    for atual in range(tamanho, minimo - 1, -1):
        fonte = _font(atual)
        if fonte.size(texto)[0] <= largura_max:
            return fonte
    return _font(minimo)


def _draw_fit(surface, texto, rect, tamanho, cor, align="center", minimo=7):
    fonte = _fit_font(texto, tamanho, rect.width, minimo)
    txt = fonte.render(str(texto), True, cor)
    if align == "left":
        x = rect.x
    elif align == "right":
        x = rect.right - txt.get_width()
    else:
        x = rect.centerx - txt.get_width() // 2
    y = rect.centery - txt.get_height() // 2
    surface.blit(txt, (x, y))
    return txt


def _draw_dialog_line(surface, texto, x, y, largura, tamanho=11):
    fonte = _fit_font(texto, tamanho, largura, minimo=8)
    txt = fonte.render(texto, True, (245, 240, 220))
    surface.blit(txt, (x, y))


# ===================================================================
#  PROPORCAO DAS BARRAS VERDES DENTRO DOS ASSETS
# ===================================================================
# (x_ini%, x_fim%, y_ini%, y_fim%) em relacao ao tamanho do asset
BAR_PROP_ENEMY  = (144/439, 377/439, 139/234, 153/234)
BAR_PROP_PLAYER = (171/471, 403/471, 159/293, 173/293)

# Tamanhos finais das HUDs na tela
HP_ENEMY_SIZE  = (260, 138)
HP_PLAYER_SIZE = (280, 175)


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


def draw_player_platform(surface):
    x, y, w, h = C.POS_PLAYER_PLATFORM
    pygame.draw.ellipse(surface, (202, 207, 198), (x, y, w, h))
    pygame.draw.ellipse(surface, (237, 234, 223), (x + 8, y + 7, w - 16, h - 14))
    pygame.draw.ellipse(surface, (222, 219, 207), (x + 42, y + 13, w - 84, h - 26))
    pygame.draw.arc(surface, (245, 241, 229), (x + 24, y + 11, w - 48, h - 22),
                    2.8, 5.8, 3)


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

    # ---- texto: cada campo tem seu retangulo para nao se sobrepor ----
    if mostrar_exp:
        nome_rect = pygame.Rect(x + 34, y + 39, 142, 24)
        lv_rect = pygame.Rect(x + 182, y + 39, 50, 24)
        _draw_fit(surface, nome, nome_rect, 13, C.BORDER_DARK,
                  align="left", minimo=8)
        _draw_fit(surface, f"Lv{level}", lv_rect, 10, C.BORDER_DARK,
                  align="right", minimo=7)
    else:
        y_texto = y + int(bh * 0.14)
        nome_rect = pygame.Rect(x + int(bw * 0.08), y_texto,
                                int(bw * 0.62), int(bh * 0.16))
        lv_rect = pygame.Rect(x + int(bw * 0.69), y_texto + 2,
                              int(bw * 0.22), int(bh * 0.14))
        _draw_fit(surface, nome, nome_rect, 12, C.BORDER_DARK,
                  align="left", minimo=8)
        _draw_fit(surface, f"Lv{level}", lv_rect, 10, C.BORDER_DARK,
                  align="right", minimo=7)

    # HP numerico acima da barra.
    if mostrar_exp:
        hp_int = int(hp)
        hp_rect = pygame.Rect(x + 151, y + 72, 92, 20)
        _draw_fit(surface, f"{hp_int}/{hp_max}", hp_rect, 9,
                  C.BORDER_DARK, align="right", minimo=8)
    else:
        hp_int = int(hp)
        hp_rect = pygame.Rect(x + 122, y + 62, 96, 18)
        _draw_fit(surface, f"{hp_int}/{hp_max}", hp_rect, 8,
                  C.BORDER_DARK, align="right", minimo=7)


# ===================================================================
#  CAIXA DE DIALOGO
# ===================================================================
DIALOG_SIZE = (460, 130)
DIALOG_TEXT_X = 40
DIALOG_TEXT_Y = 27
DIALOG_TEXT_W = 380
DIALOG_LINE_GAP = 28
NOTE_BUTTON_RECT = pygame.Rect(735, 406, 48, 48)
NOTE_WINDOW_RECT = pygame.Rect(80, 76, 640, 420)
NOTE_CLOSE_RECT = pygame.Rect(NOTE_WINDOW_RECT.right - 44, NOTE_WINDOW_RECT.y + 14, 30, 30)

def draw_dialog_box(surface, texto_visivel: str, mostrar_seta: bool = False):
    asset = AL.get_ui("hud_dialogbox_big")
    if asset is None:
        return

    dx, dy = C.POS_DIALOG
    caixa = pygame.transform.smoothscale(asset, DIALOG_SIZE)
    surface.blit(caixa, (dx, dy))

    linhas = texto_visivel.split("\n")
    for i, linha in enumerate(linhas[:3]):
        _draw_dialog_line(surface, linha,
                          dx + DIALOG_TEXT_X,
                          dy + DIALOG_TEXT_Y + i * DIALOG_LINE_GAP,
                          DIALOG_TEXT_W,
                          tamanho=11)

    if mostrar_seta:
        _desenhar_seta_piscando(surface,
                                dx + DIALOG_SIZE[0] - 40,
                                dy + DIALOG_SIZE[1] - 42)


# ===================================================================
#  MENU DE ACAO (LUTAR / MOCHILA)
# ===================================================================
OPCOES_MENU = ["LUTAR", "MOCHILA"]
MENU_SIZE   = (290, 130)

def draw_action_menu(surface, indice_selecionado: int):
    asset = AL.get_ui("hud_menuaction")
    if asset is None:
        return
    mx, my = C.POS_MENU
    caixa = pygame.transform.smoothscale(asset, MENU_SIZE)
    surface.blit(caixa, (mx, my))

    for i, opcao in enumerate(OPCOES_MENU):
        cell = pygame.Rect(mx + 58, my + 30 + i * 42,
                           MENU_SIZE[0] - 112, 24)
        _draw_fit(surface, opcao, cell, 10, C.BORDER_DARK,
                  align="center", minimo=7)
        if i == indice_selecionado:
            _desenhar_seta_menu(surface, cell.x - 22, cell.centery - 7)


# ===================================================================
#  SELECAO DE DIFICULDADE
# ===================================================================
OPCOES_DIF = [("FACIL", "facil"), ("MEDIO", "medio"), ("DIFICIL", "dificil"), ("MESTRE", "mestre")]
OPCOES_ITENS = [("POCAO", "pocao"), ("FOCO", "foco"), ("DICA", "dica"), ("VOLTAR", "voltar")]

def draw_difficulty_menu(surface, indice_selecionado: int):
    asset = AL.get_ui("hud_menuaction")
    if asset is None:
        return
    mx, my = C.POS_MENU
    caixa = pygame.transform.smoothscale(asset, MENU_SIZE)
    surface.blit(caixa, (mx, my))

    for i, (label, _) in enumerate(OPCOES_DIF):
        cell = pygame.Rect(mx + 54, my + 17 + i * 23, MENU_SIZE[0] - 108, 18)
        _draw_fit(surface, label, cell, 9, C.BORDER_DARK, align="center", minimo=7)
        if i == indice_selecionado:
            _desenhar_seta_menu(surface, cell.x - 20, cell.centery - 7)


def draw_item_menu(surface, indice_selecionado: int, inventario: dict):
    asset = AL.get_ui("hud_menuaction")
    if asset is None:
        return
    mx, my = C.POS_MENU
    caixa = pygame.transform.smoothscale(asset, MENU_SIZE)
    surface.blit(caixa, (mx, my))

    for i, (label, key) in enumerate(OPCOES_ITENS):
        sufixo = "" if key == "voltar" else f" x{inventario.get(key, 0)}"
        cell = pygame.Rect(mx + 54, my + 17 + i * 23, MENU_SIZE[0] - 108, 18)
        _draw_fit(surface, f"{label}{sufixo}", cell, 9,
                  C.BORDER_DARK, align="center", minimo=7)
        if i == indice_selecionado:
            _desenhar_seta_menu(surface, cell.x - 20, cell.centery - 7)


def draw_status_line(surface, combo: int, carga: int):
    texto = f"COMBO {combo}   RAIO {carga}/{C.SPECIAL_MAX_CHARGE}"
    rect = pygame.Rect(510, 444, 218, 24)
    painel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(painel, (20, 35, 45, 180), painel.get_rect(), border_radius=5)
    pygame.draw.rect(painel, (230, 210, 150, 180), painel.get_rect(), 1, border_radius=5)
    surface.blit(painel, rect.topleft)
    _draw_fit(surface, texto, rect.inflate(-12, -4), 9,
              (245, 240, 220), align="center", minimo=7)


def draw_note_button(surface, ativo=False):
    rect = NOTE_BUTTON_RECT
    sombra = rect.move(3, 4)
    pygame.draw.rect(surface, (20, 25, 35, 120), sombra, border_radius=6)
    pygame.draw.rect(surface, (238, 230, 190), rect, border_radius=6)
    pygame.draw.rect(surface, C.BORDER_DARK, rect, 3, border_radius=6)

    papel = pygame.Rect(rect.x + 13, rect.y + 8, 24, 32)
    pygame.draw.rect(surface, (255, 250, 220), papel, border_radius=2)
    pygame.draw.rect(surface, (70, 60, 70), papel, 2, border_radius=2)
    pygame.draw.polygon(surface, (218, 205, 170), [
        (papel.right - 8, papel.y),
        (papel.right, papel.y + 8),
        (papel.right - 8, papel.y + 8),
    ])
    for i in range(3):
        y = papel.y + 13 + i * 7
        pygame.draw.line(surface, (95, 90, 105),
                         (papel.x + 5, y), (papel.right - 5, y), 1)
    if ativo:
        pygame.draw.rect(surface, (90, 210, 180), rect.inflate(4, 4), 2, border_radius=7)


def draw_note_overlay(surface, equacao: str, texto: str):
    overlay = pygame.Surface((C.SCREEN_WIDTH, C.SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    surface.blit(overlay, (0, 0))

    rect = NOTE_WINDOW_RECT
    pygame.draw.rect(surface, (248, 239, 196), rect, border_radius=8)
    pygame.draw.rect(surface, (70, 58, 68), rect, 4, border_radius=8)
    pygame.draw.rect(surface, (226, 210, 160), rect.inflate(-16, -16), 2, border_radius=5)

    _draw_fit(surface, "RASCUNHO", pygame.Rect(rect.x + 28, rect.y + 16, 220, 28),
              13, C.BORDER_DARK, align="left", minimo=9)
    _draw_fit(surface, "ESC para fechar", pygame.Rect(rect.x + 300, rect.y + 18, 220, 24),
              8, (95, 80, 90), align="right", minimo=7)

    pygame.draw.rect(surface, (210, 85, 85), NOTE_CLOSE_RECT, border_radius=5)
    pygame.draw.rect(surface, C.BORDER_DARK, NOTE_CLOSE_RECT, 2, border_radius=5)
    _draw_fit(surface, "X", NOTE_CLOSE_RECT.inflate(-6, -6), 12,
              C.WHITE, align="center", minimo=8)

    eq_rect = pygame.Rect(rect.x + 28, rect.y + 58, rect.width - 56, 64)
    pygame.draw.rect(surface, (255, 250, 222), eq_rect, border_radius=5)
    pygame.draw.rect(surface, (160, 140, 105), eq_rect, 2, border_radius=5)
    _draw_fit(surface, "Equacao:", pygame.Rect(eq_rect.x + 14, eq_rect.y + 8, 120, 20),
              8, (90, 75, 75), align="left", minimo=7)
    for i, linha in enumerate(equacao.split("\n")[:2]):
        _draw_fit(surface, linha, pygame.Rect(eq_rect.x + 150, eq_rect.y + 7 + i * 24,
                                              eq_rect.width - 170, 22),
                  11, C.BORDER_DARK, align="left", minimo=8)

    area = pygame.Rect(rect.x + 28, rect.y + 136, rect.width - 56, rect.height - 166)
    pygame.draw.rect(surface, (255, 253, 232), area, border_radius=5)
    pygame.draw.rect(surface, (130, 115, 92), area, 2, border_radius=5)

    fonte = pygame.font.SysFont("consolas", 18, bold=False)
    cursor = "|" if (pygame.time.get_ticks() // 450) % 2 == 0 else ""
    linhas = _wrap_note_text(f"{texto}{cursor}", fonte, area.width - 24)
    max_linhas = max(1, (area.height - 18) // 22)
    linhas = linhas[-max_linhas:]
    for i, linha in enumerate(linhas):
        txt = fonte.render(linha, True, (40, 38, 45))
        surface.blit(txt, (area.x + 12, area.y + 10 + i * 22))


def _wrap_note_text(texto, fonte, largura_max):
    linhas_prontas = []
    for bloco in texto.split("\n"):
        if not bloco:
            linhas_prontas.append("")
            continue
        atual = ""
        for palavra in bloco.split(" "):
            tentativa = palavra if not atual else f"{atual} {palavra}"
            if fonte.size(tentativa)[0] <= largura_max:
                atual = tentativa
            else:
                if atual:
                    linhas_prontas.append(atual)
                while fonte.size(palavra)[0] > largura_max and len(palavra) > 1:
                    corte = len(palavra)
                    while corte > 1 and fonte.size(palavra[:corte])[0] > largura_max:
                        corte -= 1
                    linhas_prontas.append(palavra[:corte])
                    palavra = palavra[corte:]
                atual = palavra
        linhas_prontas.append(atual)
    return linhas_prontas


# ===================================================================
#  CAIXA DE INPUT
# ===================================================================
INPUT_SIZE = (760, 130)

def draw_input_box(surface, texto_digitado: str, equacao: str,
                   tempo_restante=None, tempo_total=None):
    asset = AL.get_ui("hud_textbox") or AL.get_ui("hud_dialogbox_big")
    if asset is None:
        return

    ix, iy = C.POS_INPUT
    caixa = pygame.transform.smoothscale(asset, INPUT_SIZE)
    surface.blit(caixa, (ix, iy))

    linhas_equacao = equacao.split("\n")
    for i, linha in enumerate(linhas_equacao[:2]):
        prefixo = "Resolva:  " if i == 0 else "          "
        line_rect = pygame.Rect(ix + 28, iy + 13 + i * 22,
                                INPUT_SIZE[0] - 220, 22)
        _draw_fit(surface, f"{prefixo}{linha}", line_rect, 12,
                  (245, 240, 220), align="left", minimo=8)

    if tempo_restante is not None and tempo_total:
        _draw_timer_pill(surface, ix + INPUT_SIZE[0] - 178, iy + 16,
                         tempo_restante, tempo_total)

    # campo de input com cursor piscante (consolas mono para o input em si)
    cursor = "|" if (pygame.time.get_ticks() // 400) % 2 == 0 else " "
    prompt = f"> {texto_digitado}{cursor}"
    for tamanho in range(28, 15, -1):
        fonte_in = pygame.font.SysFont("consolas", tamanho, bold=True)
        if fonte_in.size(prompt)[0] <= INPUT_SIZE[0] - 60:
            break
    txt = fonte_in.render(prompt, True, (110, 230, 180))
    surface.blit(txt, (ix + 28, iy + 64))

    dica_rect = pygame.Rect(ix + 28, iy + INPUT_SIZE[1] - 29,
                            INPUT_SIZE[0] - 56, 20)
    _draw_fit(surface, "ENTER confirma - F usa DICA - BACKSPACE apaga",
              dica_rect, 9, (200, 200, 210), align="center", minimo=7)


def draw_defense_box(surface, pergunta: str, texto_digitado: str,
                     tempo_restante, tempo_total):
    asset = AL.get_ui("hud_textbox") or AL.get_ui("hud_dialogbox_big")
    if asset is None:
        return

    ix, iy = C.POS_INPUT
    caixa = pygame.transform.smoothscale(asset, INPUT_SIZE)
    surface.blit(caixa, (ix, iy))

    _draw_fit(surface, "DEFESA!", pygame.Rect(ix + 28, iy + 14, 150, 24),
              13, (245, 230, 120), align="left", minimo=9)
    _draw_fit(surface, pergunta, pygame.Rect(ix + 170, iy + 14, 350, 24),
              13, (245, 240, 220), align="left", minimo=8)
    _draw_timer_pill(surface, ix + INPUT_SIZE[0] - 178, iy + 16,
                     tempo_restante, tempo_total)

    fonte_in = pygame.font.SysFont("consolas", 30, bold=True)
    cursor = "|" if (pygame.time.get_ticks() // 400) % 2 == 0 else " "
    prompt = f"> {texto_digitado}{cursor}"
    txt = fonte_in.render(prompt, True, (120, 235, 190))
    surface.blit(txt, (ix + 28, iy + 58))

    dica_rect = pygame.Rect(ix + 28, iy + INPUT_SIZE[1] - 29,
                            INPUT_SIZE[0] - 56, 20)
    _draw_fit(surface, "Resolva a tabuada para reduzir o dano",
              dica_rect, 9, (200, 200, 210), align="center", minimo=7)


def _draw_timer_pill(surface, x, y, restante, total):
    rect = pygame.Rect(x, y, 150, 24)
    proporcao = 0 if total <= 0 else max(0.0, min(1.0, restante / total))
    pygame.draw.rect(surface, (25, 34, 42), rect, border_radius=6)
    pygame.draw.rect(surface, (225, 210, 150), rect, 2, border_radius=6)

    bar = pygame.Rect(rect.x + 7, rect.y + 15, rect.width - 14, 5)
    pygame.draw.rect(surface, (70, 55, 55), bar, border_radius=2)
    cor = (100, 220, 130) if proporcao > 0.45 else (240, 205, 70) if proporcao > 0.2 else (230, 85, 80)
    pygame.draw.rect(surface, cor,
                     (bar.x, bar.y, int(bar.width * proporcao), bar.height),
                     border_radius=2)
    segundos = max(0, int(restante + 0.999))
    _draw_fit(surface, f"TEMPO {segundos}s",
              pygame.Rect(rect.x + 8, rect.y + 1, rect.width - 16, 13),
              7, (245, 240, 220), align="center", minimo=6)


# ===================================================================
#  TELAS FINAIS
# ===================================================================
def draw_end_screen(surface, vitoria: bool):
    overlay = pygame.Surface((C.SCREEN_WIDTH, C.SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 190))
    surface.blit(overlay, (0, 0))

    if vitoria:
        titulo, sub, cor = "VITORIA!", "EQUACIONIS foi derrotado!", (230, 210, 90)
    else:
        titulo, sub, cor = "DERROTA", "Voce foi nocauteado pela algebra...", (220, 90, 90)

    _draw_fit(surface, titulo, pygame.Rect(140, 165, 520, 64), 38,
              cor, align="center", minimo=20)
    _draw_fit(surface, sub, pygame.Rect(120, 250, 560, 32), 13,
              C.WHITE, align="center", minimo=8)

    btn = pygame.Rect(C.SCREEN_WIDTH // 2 - 140, 340, 280, 54)
    pygame.draw.rect(surface, C.CREAM, btn, border_radius=8)
    pygame.draw.rect(surface, C.BORDER_DARK, btn, 3, border_radius=8)
    _draw_fit(surface, "Jogar novamente [R]", btn.inflate(-24, -12),
              12, C.BORDER_DARK, align="center", minimo=8)

    _draw_fit(surface, "R para reiniciar  -  ESC para sair",
              pygame.Rect(120, 410, 560, 28), 11,
              (200, 200, 210), align="center", minimo=8)


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
