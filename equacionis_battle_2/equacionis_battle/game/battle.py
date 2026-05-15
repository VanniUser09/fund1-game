"""
battle.py (ATUALIZADO)
----------------------------------------
NOVIDADES nesta versao:
  - HP visual suave (hp_display acompanha hp_real gradualmente)
  - Typewriter em todas as mensagens
  - Boss animado com multiplos frames (4 idle / 2 attack / 4 hurt)
  - Glifo sobreposto quando o boss ataca
  - Background PNG no lugar do desenho procedural

A LOGICA DA BATALHA NAO MUDOU: mesma maquina de estados,
mesmo fluxo de menu -> dificuldade -> equacao -> input -> ataque.
"""
import pygame

from . import constants as C
from . import sprites, ui, animation
from . import assets_loader as AL
from .equations import gerar_equacao, validar_resposta
from .typewriter import Typewriter


class Battle:
    def __init__(self):
        self.frame = 0
        self.reiniciar()

    # -----------------------------------------------------------------
    def reiniciar(self):
        self.player_hp = C.PLAYER_MAX_HP
        self.boss_hp   = C.BOSS_MAX_HP
        # HP visual (acompanha suavemente o HP real)
        self.player_hp_display = float(C.PLAYER_MAX_HP)
        self.boss_hp_display   = float(C.BOSS_MAX_HP)

        self.estado = C.STATE_INTRO

        self.menu_idx        = 0
        self.dificuldade_idx = 0
        self.dificuldade_atual = "facil"

        self.equacao_texto   = ""
        self.equacao_solucoes = []
        self.input_texto = ""

        # typewriter para mensagens
        self.tw = Typewriter("EQUACIONIS apareceu!")

        self.timer = animation.Timer(C.ANIM_INTRO_DURATION)
        self.proximo_estado = C.STATE_MENU
        self.anim_timer = animation.Timer(1)
        self.ultimo_acerto = True

    # -----------------------------------------------------------------
    # EVENTOS
    # -----------------------------------------------------------------
    def tratar_evento(self, ev):
        if ev.type != pygame.KEYDOWN:
            return

        # telas finais
        if self.estado in (C.STATE_VICTORY, C.STATE_DEFEAT):
            if ev.key == pygame.K_r:
                self.reiniciar()
            return

        # INTRO
        if self.estado == C.STATE_INTRO:
            # primeiro ENTER: pula o typewriter; segundo: avanca
            if ev.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_z):
                if not self.tw.terminou():
                    self.tw.pular()
                else:
                    self.estado = C.STATE_MENU
            return

        # MENU
        if self.estado == C.STATE_MENU:
            if ev.key in (pygame.K_LEFT, pygame.K_a):
                self.menu_idx = (self.menu_idx - 1) % 4
            elif ev.key in (pygame.K_RIGHT, pygame.K_d):
                self.menu_idx = (self.menu_idx + 1) % 4
            elif ev.key in (pygame.K_UP, pygame.K_w):
                self.menu_idx = (self.menu_idx - 2) % 4
            elif ev.key in (pygame.K_DOWN, pygame.K_s):
                self.menu_idx = (self.menu_idx + 2) % 4
            elif ev.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_z):
                self._confirmar_menu()
            return

        # DIFICULDADE
        if self.estado == C.STATE_DIFFICULTY:
            if ev.key in (pygame.K_UP, pygame.K_w):
                self.dificuldade_idx = (self.dificuldade_idx - 1) % 3
            elif ev.key in (pygame.K_DOWN, pygame.K_s):
                self.dificuldade_idx = (self.dificuldade_idx + 1) % 3
            elif ev.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_z):
                self._iniciar_rodada()
            elif ev.key == pygame.K_ESCAPE:
                self.estado = C.STATE_MENU
            return

        # EQUATION_SHOW: ENTER pula typewriter ou vai pro INPUT
        if self.estado == C.STATE_EQUATION_SHOW:
            if ev.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_z):
                if not self.tw.terminou():
                    self.tw.pular()
                else:
                    self.estado = C.STATE_INPUT
                    self.input_texto = ""
            return

        # INPUT
        if self.estado == C.STATE_INPUT:
            if ev.key == pygame.K_RETURN:
                self._validar_e_atacar()
            elif ev.key == pygame.K_BACKSPACE:
                self.input_texto = self.input_texto[:-1]
            elif ev.key == pygame.K_ESCAPE:
                self.estado = C.STATE_EQUATION_SHOW
            else:
                if ev.unicode and len(self.input_texto) < 20 and ev.unicode.isprintable():
                    self.input_texto += ev.unicode
            return

        # MESSAGE: ENTER pula
        if self.estado == C.STATE_MESSAGE:
            if ev.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_z):
                if not self.tw.terminou():
                    self.tw.pular()
                else:
                    self.timer.restante = 0

    # -----------------------------------------------------------------
    def _confirmar_menu(self):
        op = ui.OPCOES_MENU[self.menu_idx]
        if op in ("LUTAR", "EQUACAO"):
            self.estado = C.STATE_DIFFICULTY
        elif op == "MOCHILA":
            self._mostrar_mensagem("Mochila vazia...\nSo tem formulas aqui.",
                                   proximo=C.STATE_MENU)
        elif op == "FUGIR":
            self._mostrar_mensagem("Nao e possivel fugir!\nEQUACIONIS bloqueou a saida.",
                                   proximo=C.STATE_MENU)

    # -----------------------------------------------------------------
    def _iniciar_rodada(self):
        _, dif = ui.OPCOES_DIF[self.dificuldade_idx]
        self.dificuldade_atual = dif
        texto, solucoes = gerar_equacao(dif)
        self.equacao_texto = texto
        self.equacao_solucoes = solucoes
        self.input_texto = ""
        mensagem = f"EQUACIONIS lancou:\n{texto}\n(aperte ENTER para responder)"
        self.tw = Typewriter(mensagem)
        self.estado = C.STATE_EQUATION_SHOW

    # -----------------------------------------------------------------
    def _validar_e_atacar(self):
        acertou = validar_resposta(self.input_texto, self.equacao_solucoes)
        self.ultimo_acerto = acertou
        if acertou:
            dano = C.DAMAGE_ON_HIT[self.dificuldade_atual]
            self.boss_hp = max(0, self.boss_hp - dano)
            self.estado = C.STATE_PLAYER_ATTACK
            self.anim_timer = animation.Timer(C.ANIM_ATTACK_DURATION)
        else:
            dano = C.DAMAGE_ON_FAIL[self.dificuldade_atual]
            self.player_hp = max(0, self.player_hp - dano)
            self.estado = C.STATE_BOSS_ATTACK
            self.anim_timer = animation.Timer(C.ANIM_ATTACK_DURATION)

    # -----------------------------------------------------------------
    def _mostrar_mensagem(self, texto, proximo, duracao=C.ANIM_MESSAGE_DURATION):
        self.tw = Typewriter(texto)
        self.proximo_estado = proximo
        self.timer = animation.Timer(duracao)
        self.estado = C.STATE_MESSAGE

    # -----------------------------------------------------------------
    # UPDATE
    # -----------------------------------------------------------------
    def update(self):
        self.frame += 1
        self.tw.tick()

        # HP visual suave: se aproxima do HP real gradualmente
        self._atualizar_hp_visual()

        if self.estado == C.STATE_MESSAGE:
            self.timer.tick()
            if self.timer.terminou() and self.tw.terminou():
                self.estado = self.proximo_estado
            return

        if self.estado == C.STATE_PLAYER_ATTACK:
            self.anim_timer.tick()
            if self.anim_timer.terminou():
                if self.boss_hp <= 0 and self.boss_hp_display <= 0.5:
                    self.estado = C.STATE_VICTORY
                elif self.anim_timer.terminou():
                    dano = C.DAMAGE_ON_HIT[self.dificuldade_atual]
                    self._mostrar_mensagem(
                        f"E super efetivo!\nEQUACIONIS sofreu {dano} de dano.",
                        proximo=C.STATE_DIFFICULTY,
                    )
            return

        if self.estado == C.STATE_BOSS_ATTACK:
            self.anim_timer.tick()
            if self.anim_timer.terminou():
                if self.player_hp <= 0 and self.player_hp_display <= 0.5:
                    self.estado = C.STATE_DEFEAT
                else:
                    dano = C.DAMAGE_ON_FAIL[self.dificuldade_atual]
                    self._mostrar_mensagem(
                        f"EQUACIONIS usou ALGEBRAGEM!\nVoce perdeu {dano} de HP.",
                        proximo=C.STATE_DIFFICULTY,
                    )
            return

        if self.estado == C.STATE_INTRO:
            self.timer.tick()

    # -----------------------------------------------------------------
    def _atualizar_hp_visual(self):
        # Player
        if self.player_hp_display > self.player_hp:
            self.player_hp_display = max(self.player_hp,
                                         self.player_hp_display - C.HP_ANIM_SPEED)
        elif self.player_hp_display < self.player_hp:
            self.player_hp_display = min(self.player_hp,
                                         self.player_hp_display + C.HP_ANIM_SPEED)
        # Boss
        if self.boss_hp_display > self.boss_hp:
            self.boss_hp_display = max(self.boss_hp,
                                       self.boss_hp_display - C.HP_ANIM_SPEED)
        elif self.boss_hp_display < self.boss_hp:
            self.boss_hp_display = min(self.boss_hp,
                                       self.boss_hp_display + C.HP_ANIM_SPEED)

    # -----------------------------------------------------------------
    # RENDER
    # -----------------------------------------------------------------
    def render(self, surface):
        # 1) Background
        ui.draw_arena(surface)

        # 2) Sprites de boss e jogador (com offsets de animacao)
        self._render_sprites(surface)

        # 3) Caixas de HP com HP visual suave
        ui.draw_hp_box(surface, C.POS_HP_BOSS[0], C.POS_HP_BOSS[1],
                       C.BOSS_NAME, C.BOSS_LEVEL,
                       self.boss_hp_display, C.BOSS_MAX_HP)
        ui.draw_hp_box(surface, C.POS_HP_PLAYER[0], C.POS_HP_PLAYER[1],
                       C.PLAYER_NAME, C.PLAYER_LEVEL,
                       self.player_hp_display, C.PLAYER_MAX_HP,
                       mostrar_exp=True)

        # 4) Painel inferior conforme o estado
        self._render_painel_inferior(surface)

    # -----------------------------------------------------------------
    def _render_sprites(self, surface):
        boss_pos   = list(C.POS_BOSS)
        player_pos = list(C.POS_PLAYER)

        # flutuacao suave do boss
        boss_pos[1] += animation.bob_offset(self.frame, amplitude=5, velocidade=0.04)

        # decide estados de animacao
        boss_state   = "idle"
        player_state = "idle"
        mostrar_glifo = False

        if self.estado == C.STATE_PLAYER_ATTACK:
            p = self.anim_timer.progresso()
            player_state = "attack"
            player_pos[0] += int(p * 30) if p < 0.5 else int((1 - p) * 30)
            player_pos[1] += animation.hop_offset(p, altura=10)
            if p > 0.5:
                boss_state = "hurt"
                dx, dy = animation.shake_offset(self.frame, 6)
                boss_pos[0] += dx
                boss_pos[1] += dy

        elif self.estado == C.STATE_BOSS_ATTACK:
            p = self.anim_timer.progresso()
            boss_state = "attack"
            mostrar_glifo = True
            boss_pos[1] += int(p * 8)
            if p > 0.5:
                player_state = "hurt"
                dx, dy = animation.shake_offset(self.frame, 7)
                player_pos[0] += dx
                player_pos[1] += dy

        # --- glifo magico (atras do boss) ---
        if mostrar_glifo:
            glifo = AL.get_glyph()
            if glifo is not None:
                gsize = (220, 220)
                g_esc = pygame.transform.smoothscale(glifo, gsize)
                # posiciona atras do boss
                surface.blit(g_esc, (boss_pos[0] - 20, boss_pos[1] + 20))

        # --- boss: frame animado do PNG ---
        boss_frame = AL.get_boss_frame(boss_state, self.frame)
        if boss_frame is not None:
            # boss grande e centralizado
            tamanho_destino = (260, 280)
            boss_img = pygame.transform.smoothscale(boss_frame, tamanho_destino)
            surface.blit(boss_img, (boss_pos[0], boss_pos[1]))
        else:
            # fallback: sprite procedural
            surface.blit(sprites.get_boss_sprite(boss_state),
                         (boss_pos[0], boss_pos[1]))

        # --- player: usa PNG se disponivel, senao procedural ---
        player_frame = AL.get_player_frame(player_state, self.frame)
        if player_frame is not None:
            # tamanho de destino: jogador fica grande, perto do primeiro plano
            tamanho_destino = (180, 280)
            player_img = pygame.transform.scale(player_frame, tamanho_destino)
            surface.blit(player_img, (player_pos[0], player_pos[1]))
        else:
            player_sprite = sprites.get_player_sprite(player_state)
            surface.blit(player_sprite, (player_pos[0], player_pos[1]))

    # -----------------------------------------------------------------
    def _render_painel_inferior(self, surface):
        e = self.estado

        if e == C.STATE_INTRO:
            ui.draw_dialog_box(surface, self.tw.visivel(),
                               mostrar_seta=self.tw.terminou())

        elif e == C.STATE_MENU:
            ui.draw_dialog_box(surface, f"O que {C.PLAYER_NAME} fara?")
            ui.draw_action_menu(surface, self.menu_idx)

        elif e == C.STATE_DIFFICULTY:
            ui.draw_dialog_box(surface, "Escolha a dificuldade\nda proxima equacao:")
            ui.draw_difficulty_menu(surface, self.dificuldade_idx)

        elif e == C.STATE_EQUATION_SHOW:
            ui.draw_dialog_box(surface, self.tw.visivel(),
                               mostrar_seta=self.tw.terminou())

        elif e == C.STATE_INPUT:
            ui.draw_input_box(surface, self.input_texto, self.equacao_texto)

        elif e == C.STATE_MESSAGE:
            ui.draw_dialog_box(surface, self.tw.visivel(),
                               mostrar_seta=self.tw.terminou())

        elif e == C.STATE_PLAYER_ATTACK:
            ui.draw_dialog_box(surface, f"{C.PLAYER_NAME} usou EQUACAO!")

        elif e == C.STATE_BOSS_ATTACK:
            ui.draw_dialog_box(surface, f"{C.BOSS_NAME} usou ALGEBRAGEM!")

        elif e == C.STATE_VICTORY:
            ui.draw_end_screen(surface, vitoria=True)

        elif e == C.STATE_DEFEAT:
            ui.draw_end_screen(surface, vitoria=False)
