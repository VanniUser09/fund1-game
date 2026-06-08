"""
assets_loader.py (ATUALIZADO)
----------------------------------------
Agora carrega tambem:
  - sprites do jogador (nerd_idle, nerd_attack, nerd_hurt)
  - fonte Pokemon Classic (assets/fonts/PokemonClassic.ttf)

Se um PNG ou a fonte nao existir, o jogo cai em fallback.
"""
import os
import pygame
from . import constants as C


_frames = {}
_ui = {}
_bg = None
_glyph = None
_fonte_caminho = None


def carregar_todos():
    """Chame uma unica vez em main.py apos pygame.display.set_mode()."""
    global _bg, _glyph, _fonte_caminho

    _bg    = _carregar(C.ASSETS_SPRITES, "bg_battle.png")
    _glyph = _carregar(C.ASSETS_SPRITES, "glifo_object.png")

    # sprites do boss: uma pose por estado (idle / attack / hurt)
    _frames["boss_idle"]   = _filtrar([_carregar(C.ASSETS_SPRITES, "boss_idle1_sem_background.png")])
    _frames["boss_attack"] = _filtrar([_carregar(C.ASSETS_SPRITES, "boss_attack1.png")])
    _frames["boss_hurt"]   = _filtrar([_carregar(C.ASSETS_SPRITES, "boss_hurt1.png")])

    # sprites do jogador (so 1 frame por estado por enquanto)
    _frames["player_idle"]   = _filtrar([_carregar(C.ASSETS_SPRITES, "nerd_idle.png")])
    _frames["player_attack"] = _filtrar([_carregar(C.ASSETS_SPRITES, "nerd_attack.png")])
    _frames["player_hurt"]   = _filtrar([_carregar(C.ASSETS_SPRITES, "nerd_hurt.png")])

    # HUD
    for nome in ["hud_hp_enemy", "hud_hp_player", "hud_menuaction",
                 "hud_dialogbox_big", "hud_dialogbox_small", "hud_textbox",
                 "hud_red_arrow", "hud_black_arrow"]:
        _ui[nome] = _carregar(C.ASSETS_UI, f"{nome}.png")

    # fonte Pokemon Classic
    caminho_fonte = os.path.join(C.ASSETS_FONTS, "PokemonClassic.ttf")
    if os.path.isfile(caminho_fonte):
        _fonte_caminho = caminho_fonte
        print(f"[assets] fonte carregada: {caminho_fonte}")
    else:
        print(f"[assets] fonte NAO encontrada: {caminho_fonte} (usando Arial)")


def _filtrar(lista):
    return [x for x in lista if x is not None]


def _carregar(pasta, nome):
    caminho = os.path.join(pasta, nome)
    if not os.path.isfile(caminho):
        print(f"[assets] nao encontrado: {caminho}")
        return None
    try:
        return pygame.image.load(caminho).convert_alpha()
    except pygame.error as e:
        print(f"[assets] erro ao carregar {caminho}: {e}")
        return None


# ---------------- API ----------------
def get_boss_frame(estado: str, frame_counter: int):
    key = f"boss_{estado}"
    lista = _frames.get(key) or []
    if not lista:
        return None
    return lista[0]


def get_player_frame(estado: str, frame_counter: int = 0):
    """Retorna a pose do jogador: idle, attack ou hurt."""
    key = f"player_{estado}"
    lista = _frames.get(key) or []
    if not lista:
        return None
    return lista[0]


def get_ui(nome: str):
    return _ui.get(nome)


def get_background():
    return _bg


def get_glyph():
    return _glyph


def get_fonte(tamanho: int) -> pygame.font.Font:
    """
    Retorna a fonte Pokemon Classic no tamanho pedido.
    Se nao carregou, retorna Arial bold como fallback.
    """
    if _fonte_caminho is not None:
        try:
            return pygame.font.Font(_fonte_caminho, tamanho)
        except pygame.error:
            pass
    return pygame.font.SysFont("arial", tamanho, bold=True)
