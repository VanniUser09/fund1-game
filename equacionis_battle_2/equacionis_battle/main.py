"""
main.py  (ATUALIZADO)
----------------------------------------
Agora carrega TODOS os assets no inicio via assets_loader.carregar_todos().
Rode com:  python main.py
"""
import os
import sys
import pygame

from game import constants as C
from game import sprites
from game import assets_loader as AL
from game.battle import Battle


def main():
    pygame.init()
    pygame.display.set_caption(C.TITLE)
    screen = pygame.display.set_mode((C.SCREEN_WIDTH, C.SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    # NOVO: carrega todos os PNGs (ui + boss + bg + glifo)
    AL.carregar_todos()

    # Mantem o fallback procedural para o jogador
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

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
