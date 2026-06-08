"""
main.py
----------------------------------------
Loop async necessario para rodar no navegador via Pygbag.
Localmente:  python main.py
Navegador:   python -m pygbag --build .
"""
import asyncio
import os
import sys
import pygame

from game import constants as C
from game import sprites
from game import assets_loader as AL
from game.battle import Battle


async def main():
    pygame.init()
    pygame.display.set_caption(C.TITLE)
    screen = pygame.display.set_mode((C.SCREEN_WIDTH, C.SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    AL.carregar_todos()
    sprites.carregar_externos(os.path.join("assets", "sprites"))

    batalha = Battle()

    rodando = True
    while rodando:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                rodando = False
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                if batalha.estado in (C.STATE_VICTORY, C.STATE_DEFEAT):
                    rodando = False
                else:
                    batalha.tratar_evento(ev)
            else:
                batalha.tratar_evento(ev)

        batalha.update()
        batalha.render(screen)
        pygame.display.flip()
        clock.tick(C.FPS)
        await asyncio.sleep(0)

    pygame.quit()


asyncio.run(main())
