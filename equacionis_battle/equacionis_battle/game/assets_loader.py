"""
assets_loader.py  (NOVO)
----------------------------------------
Carrega TODOS os PNGs (sprites do boss, UI, background, glifo) uma unica vez
no inicio do jogo, e disponibiliza por chave string.

Estrutura esperada de pastas:
  assets/
    sprites/  (boss_idle1..4, boss_attack1..2, boss_hurt1..4, bg_battle, glifo_object)
    ui/       (hud_hp_enemy, hud_hp_player, hud_menuaction, hud_dialogbox_big,
               hud_dialogbox_small, hud_textbox, hud_red_arrow, hud_black_arrow)

Se um PNG nao existir, o jogo continua rodando (usa fallback procedural).
"""
import os
import pygame
from . import constants as C


_frames = {}   # boss_idle -> [Surface, Surface, ...]
_ui = {}       # hud_* -> Surface
_bg = None
_glyph = None


def carregar_todos():
    """Chame uma unica vez em main.py apos pygame.display.set_mode()."""
    global _bg, _glyph

    # background e glifo
    _bg    = _carregar(C.ASSETS_SPRITES, "bg_battle.png")
    _glyph = _carregar(C.ASSETS_SPRITES, "glifo_object.png")

    # sprites animados do boss
    _frames["boss_idle"]   = _carregar_lista(C.ASSETS_SPRITES, "boss_idle",   C.FRAMES_BOSS_IDLE)
    _frames["boss_attack"] = _carregar_lista(C.ASSETS_SPRITES, "boss_attack", C.FRAMES_BOSS_ATTACK)
    _frames["boss_hurt"]   = _carregar_lista(C.ASSETS_SPRITES, "boss_hurt",   C.FRAMES_BOSS_HURT)

    # elementos de UI
    for nome in ["hud_hp_enemy", "hud_hp_player", "hud_menuaction",
                 "hud_dialogbox_big", "hud_dialogbox_small", "hud_textbox",
                 "hud_red_arrow", "hud_black_arrow"]:
        _ui[nome] = _carregar(C.ASSETS_UI, f"{nome}.png")


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


def _carregar_lista(pasta, prefixo, quantidade):
    """Carrega prefixo1.png, prefixo2.png ..."""
    frames = []
    for i in range(1, quantidade + 1):
        img = _carregar(pasta, f"{prefixo}{i}.png")
        if img is not None:
            frames.append(img)
    return frames


# ---------------- API ----------------
def get_boss_frame(estado: str, frame_counter: int) -> pygame.Surface:
    """
    estado: 'idle' | 'attack' | 'hurt'
    frame_counter: numero crescente de frames do loop principal.
    Retorna o frame correto animando ciclicamente.
    """
    key = f"boss_{estado}"
    lista = _frames.get(key) or []
    if not lista:
        return None
    idx = (frame_counter // C.FRAME_DURATION) % len(lista)
    return lista[idx]


def get_ui(nome: str) -> pygame.Surface:
    return _ui.get(nome)


def get_background() -> pygame.Surface:
    return _bg


def get_glyph() -> pygame.Surface:
    return _glyph
