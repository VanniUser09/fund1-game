"""
battle.py (ATUALIZADO)
----------------------------------------
NOVIDADES nesta versao:
  - HP visual suave (hp_display acompanha hp_real gradualmente)
  - Typewriter em todas as mensagens
  - Boss com poses de idle / attack / hurt
  - Glifo sobreposto quando o boss ataca
  - Background PNG no lugar do desenho procedural

A LOGICA DA BATALHA NAO MUDOU: mesma maquina de estados,
mesmo fluxo de menu -> dificuldade -> equacao -> input -> ataque.
"""
import pygame
import random

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
    def reiniciar(self, inventario=None):
        self.player_hp = C.PLAYER_MAX_HP
        self.boss_hp   = C.BOSS_MAX_HP
        # HP visual (acompanha suavemente o HP real)
        self.player_hp_display = float(C.PLAYER_MAX_HP)
        self.boss_hp_display   = float(C.BOSS_MAX_HP)

        self.estado = C.STATE_INTRO

        self.menu_idx        = 0
        self.dificuldade_idx = 0
        self.item_idx        = 0
        self.dificuldade_atual = "facil"
        self.combo = 0
        self.carga_especial = 0
        self.inventario = self._inventario_inicial() if inventario is None else dict(inventario)

        self.equacao_texto   = ""
        self.equacao_solucoes = []
        self.input_texto = ""
        self.nota_aberta = False
        self.nota_texto = ""
        self.resposta_timer = animation.Timer(1)
        self.resposta_tempo_total = 1
        self.defesa_timer = animation.Timer(1)
        self.defesa_tempo_total = C.DEFENSE_TIME_SECONDS.get(self.dificuldade_atual, 8)
        self.defesa_pergunta = ""
        self.defesa_solucao = 0
        self.defesa_input = ""
        self.dano_pendente = 0
        self.defesa_sucesso = False

        # typewriter para mensagens
        self.tw = Typewriter("EQUACIONIS apareceu!")

        self.timer = animation.Timer(C.ANIM_INTRO_DURATION)
        self.proximo_estado = C.STATE_MENU
        self.anim_timer = animation.Timer(1)
        self.ultimo_acerto = True
        self.ultimo_dano = 0
        self.especial_ativado = False
        self.mensagem_aguarda_confirmacao = False

    # -----------------------------------------------------------------
    def _inventario_inicial(self):
        return {
            "pocao": 2,
            "foco": 1,
            "dica": 2,
        }

    # -----------------------------------------------------------------
    # EVENTOS
    # -----------------------------------------------------------------
    def tratar_evento(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            self._tratar_clique(ev.pos)
            return

        if ev.type != pygame.KEYDOWN:
            return

        if self.nota_aberta:
            self._tratar_tecla_nota(ev)
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
            if ev.key in (pygame.K_LEFT, pygame.K_a, pygame.K_UP, pygame.K_w):
                self.menu_idx = (self.menu_idx - 1) % len(ui.OPCOES_MENU)
            elif ev.key in (pygame.K_RIGHT, pygame.K_d, pygame.K_DOWN, pygame.K_s):
                self.menu_idx = (self.menu_idx + 1) % len(ui.OPCOES_MENU)
            elif ev.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_z):
                self._confirmar_menu()
            return

        # DIFICULDADE
        if self.estado == C.STATE_DIFFICULTY:
            if ev.key in (pygame.K_UP, pygame.K_w):
                self.dificuldade_idx = (self.dificuldade_idx - 1) % len(ui.OPCOES_DIF)
            elif ev.key in (pygame.K_DOWN, pygame.K_s):
                self.dificuldade_idx = (self.dificuldade_idx + 1) % len(ui.OPCOES_DIF)
            elif ev.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_z):
                self._iniciar_rodada()
            elif ev.key == pygame.K_ESCAPE:
                self.estado = C.STATE_MENU
            return

        # ITEM SELECT
        if self.estado == C.STATE_ITEM_SELECT:
            if ev.key in (pygame.K_UP, pygame.K_w):
                self.item_idx = (self.item_idx - 1) % len(ui.OPCOES_ITENS)
            elif ev.key in (pygame.K_DOWN, pygame.K_s):
                self.item_idx = (self.item_idx + 1) % len(ui.OPCOES_ITENS)
            elif ev.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_z):
                self._usar_item()
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
                    self._iniciar_timer_resposta()
            elif ev.key == pygame.K_f:
                self.input_texto = ""
                self._iniciar_timer_resposta()
                self._usar_dica_durante_conta()
            return

        # INPUT
        if self.estado == C.STATE_INPUT:
            if ev.key == pygame.K_RETURN:
                self._validar_e_atacar()
            elif ev.key == pygame.K_BACKSPACE:
                self.input_texto = self.input_texto[:-1]
            elif ev.key == pygame.K_ESCAPE:
                self.tw = Typewriter(self._mensagem_equacao_atual())
                self.tw.pular()
                self.estado = C.STATE_EQUATION_SHOW
            elif ev.key == pygame.K_f:
                self._usar_dica_durante_conta()
            else:
                if ev.unicode and len(self.input_texto) < 20 and ev.unicode.isprintable():
                    self.input_texto += ev.unicode
            return

        # DEFESA
        if self.estado == C.STATE_DEFENSE_INPUT:
            if ev.key == pygame.K_RETURN:
                self._validar_defesa()
            elif ev.key == pygame.K_BACKSPACE:
                self.defesa_input = self.defesa_input[:-1]
            else:
                if ev.unicode and ev.unicode.isdigit() and len(self.defesa_input) < 4:
                    self.defesa_input += ev.unicode
            return

        # MESSAGE: ENTER pula
        if self.estado == C.STATE_MESSAGE:
            if ev.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_z):
                if not self.tw.terminou():
                    self.tw.pular()
                elif self.mensagem_aguarda_confirmacao:
                    self.mensagem_aguarda_confirmacao = False
                    self._avancar_mensagem()
                else:
                    self.timer.restante = 0

    # -----------------------------------------------------------------
    def _confirmar_menu(self):
        op = ui.OPCOES_MENU[self.menu_idx]
        if op == "LUTAR":
            self.estado = C.STATE_DIFFICULTY
        elif op == "MOCHILA":
            self.item_idx = 0
            self.estado = C.STATE_ITEM_SELECT

    # -----------------------------------------------------------------
    def _usar_item(self):
        _, item = ui.OPCOES_ITENS[self.item_idx]
        if item == "voltar":
            self.estado = C.STATE_MENU
            return

        if self.inventario.get(item, 0) <= 0:
            self._mostrar_mensagem("Esse item acabou!\nEscolha outro plano.", proximo=C.STATE_ITEM_SELECT)
            return

        self.inventario[item] -= 1
        if item == "pocao":
            antes = self.player_hp
            self.player_hp = min(C.PLAYER_MAX_HP, self.player_hp + C.POTION_HEAL)
            cura = self.player_hp - antes
            self._mostrar_mensagem(f"{C.PLAYER_NAME} usou POCAO!\nRecuperou {cura} de HP.", proximo=C.STATE_MENU)
        elif item == "foco":
            self.carga_especial = min(C.SPECIAL_MAX_CHARGE, self.carga_especial + C.FOCUS_CHARGE_GAIN)
            self._mostrar_mensagem("Voce respirou e focou.\nRAIO LOGICO carregou!", proximo=C.STATE_MENU)
        elif item == "dica":
            self.inventario[item] += 1
            self._mostrar_mensagem(
                "DICA funciona durante a conta.\nAperte F enquanto resolve.",
                proximo=C.STATE_MENU,
                duracao=C.ANIM_MESSAGE_DURATION + 45,
            )

    # -----------------------------------------------------------------
    def _usar_dica_durante_conta(self):
        if self.inventario.get("dica", 0) <= 0:
            self._mostrar_mensagem("Voce nao tem DICA.\nResolva do jeito raiz!",
                                   proximo=C.STATE_INPUT)
            return

        if not self.equacao_solucoes:
            self._mostrar_mensagem("Ainda nao ha conta para analisar.\nEscolha uma dificuldade primeiro.",
                                   proximo=C.STATE_MENU)
            return

        self.inventario["dica"] -= 1
        self._mostrar_mensagem(self._texto_dica(),
                               proximo=C.STATE_INPUT,
                               duracao=C.ANIM_MESSAGE_DURATION + 55,
                               aguardar_confirmacao=True)

    # -----------------------------------------------------------------
    def _texto_dica(self):
        if isinstance(self.equacao_solucoes, dict) and self.equacao_solucoes.get("tipo") == "sistema":
            var = random.choice(["x", "y"])
            valor = self.equacao_solucoes[var]
            pistas = self._pistas_de_valor(var, valor)
        else:
            valores = list(self.equacao_solucoes)
            valor = random.choice(valores)
            alvo = "uma raiz" if self.dificuldade_atual == "dificil" and len(valores) > 1 else "x"
            pistas = self._pistas_de_valor(alvo, valor)

        escolhidas = random.sample(pistas, k=min(2, len(pistas)))
        while len(escolhidas) < 2:
            escolhidas.append("Use essa pista junto da equacao.")
        return f"DICA analisou a conta!\n{escolhidas[0]}\n{escolhidas[1]}"

    # -----------------------------------------------------------------
    def _pistas_de_valor(self, nome, valor):
        pistas = []

        pistas.append(f"{nome} e maior que {valor - random.randint(1, 3)}.")
        pistas.append(f"{nome} e menor que {valor + random.randint(1, 3)}.")

        if valor != 0:
            multiplo = abs(valor) * random.randint(2, 9)
            if valor > 0:
                pistas.append(f"{nome} e divisor de {multiplo}.")
            else:
                pistas.append(f"O modulo de {nome} e divisor de {multiplo}.")
        else:
            pistas.append(f"{nome} nao e divisor valido.")

        if valor > 1:
            if self._eh_primo(valor):
                pistas.append(f"{nome} e um numero primo.")
            else:
                pistas.append(f"{nome} nao e primo.")
        elif valor <= 1:
            pistas.append(f"{nome} nao e primo.")

        return pistas

    # -----------------------------------------------------------------
    def _eh_primo(self, valor):
        if valor < 2:
            return False
        for divisor in range(2, int(valor ** 0.5) + 1):
            if valor % divisor == 0:
                return False
        return True

    # -----------------------------------------------------------------
    def _iniciar_rodada(self):
        _, dif = ui.OPCOES_DIF[self.dificuldade_idx]
        self.dificuldade_atual = dif
        texto, solucoes = gerar_equacao(dif)
        self.equacao_texto = texto
        self.equacao_solucoes = solucoes
        self.input_texto = ""
        self.nota_aberta = False
        self.nota_texto = ""
        self.tw = Typewriter(self._mensagem_equacao_atual())
        self.estado = C.STATE_EQUATION_SHOW

    # -----------------------------------------------------------------
    def _mensagem_equacao_atual(self):
        return f"EQUACIONIS lancou:\n{self.equacao_texto}\n(aperte ENTER para responder)"

    # -----------------------------------------------------------------
    def _iniciar_timer_resposta(self):
        segundos = C.TIME_LIMIT_SECONDS.get(self.dificuldade_atual, 30)
        self.resposta_tempo_total = segundos
        self.resposta_timer = animation.Timer(segundos * C.FPS)

    # -----------------------------------------------------------------
    def _mostrar_botao_nota(self):
        return self.estado in (C.STATE_EQUATION_SHOW, C.STATE_INPUT)

    # -----------------------------------------------------------------
    def _tratar_clique(self, pos):
        if self.nota_aberta:
            if ui.NOTE_CLOSE_RECT.collidepoint(pos):
                self.nota_aberta = False
            return

        if self._mostrar_botao_nota() and ui.NOTE_BUTTON_RECT.collidepoint(pos):
            self.nota_aberta = True
            if not self.nota_texto:
                self.nota_texto = f"Conta:\n{self.equacao_texto}\n\n"
            return

    # -----------------------------------------------------------------
    def _tratar_tecla_nota(self, ev):
        if ev.key == pygame.K_ESCAPE:
            self.nota_aberta = False
            return
        if ev.key == pygame.K_BACKSPACE:
            self.nota_texto = self.nota_texto[:-1]
            return
        if ev.key == pygame.K_RETURN:
            if len(self.nota_texto) < 900:
                self.nota_texto += "\n"
            return
        if ev.key == pygame.K_TAB:
            if len(self.nota_texto) < 900:
                self.nota_texto += "    "
            return
        if ev.unicode and ev.unicode.isprintable() and len(self.nota_texto) < 900:
            self.nota_texto += ev.unicode

    # -----------------------------------------------------------------
    def _validar_e_atacar(self):
        acertou = validar_resposta(self.input_texto, self.equacao_solucoes)
        self.ultimo_acerto = acertou
        if acertou:
            dano = C.DAMAGE_ON_HIT[self.dificuldade_atual]
            self.combo += 1
            self.carga_especial = min(C.SPECIAL_MAX_CHARGE, self.carga_especial + 1)
            self.especial_ativado = False
            if self.carga_especial >= C.SPECIAL_MAX_CHARGE:
                dano += C.SPECIAL_BONUS_DAMAGE
                self.carga_especial = 0
                self.especial_ativado = True
            self.ultimo_dano = dano
            self.boss_hp = max(0, self.boss_hp - dano)
            self.estado = C.STATE_PLAYER_ATTACK
            self.anim_timer = animation.Timer(C.ANIM_ATTACK_DURATION)
        else:
            dano = C.DAMAGE_ON_FAIL[self.dificuldade_atual]
            self.especial_ativado = False
            self.combo = 0
            self._iniciar_defesa(dano)

    # -----------------------------------------------------------------
    def _iniciar_defesa(self, dano):
        a = random.randint(3, 9)
        b = random.randint(3, 9)
        self.defesa_pergunta = f"{a} x {b} = ?"
        self.defesa_solucao = a * b
        self.defesa_input = ""
        self.dano_pendente = dano
        self.defesa_sucesso = False
        segundos = C.DEFENSE_TIME_SECONDS.get(self.dificuldade_atual, 8)
        self.defesa_tempo_total = segundos
        self.defesa_timer = animation.Timer(segundos * C.FPS)
        self.estado = C.STATE_DEFENSE_INPUT

    # -----------------------------------------------------------------
    def _validar_defesa(self):
        try:
            acertou = int(self.defesa_input) == self.defesa_solucao
        except ValueError:
            acertou = False
        self._resolver_defesa(acertou)

    # -----------------------------------------------------------------
    def _resolver_defesa(self, acertou):
        self.defesa_sucesso = acertou
        if acertou:
            dano = max(1, int(self.dano_pendente * C.DEFENSE_DAMAGE_REDUCTION))
        else:
            dano = self.dano_pendente
        self.ultimo_dano = dano
        self.player_hp = max(0, self.player_hp - dano)
        self.estado = C.STATE_BOSS_ATTACK
        self.anim_timer = animation.Timer(C.ANIM_ATTACK_DURATION)

    # -----------------------------------------------------------------
    def _finalizar_vitoria(self):
        recompensas = self._sortear_recompensas()
        for item, qtd in recompensas.items():
            self.inventario[item] = self.inventario.get(item, 0) + qtd

        itens = ", ".join(f"{self._nome_item(item)} x{qtd}"
                          for item, qtd in recompensas.items())
        self._mostrar_mensagem(
            f"EQUACIONIS caiu!\nVoce ganhou {itens}.\nENTER: nova batalha.",
            proximo=C.STATE_RESTART_BATTLE,
            duracao=C.ANIM_MESSAGE_DURATION + 90,
            aguardar_confirmacao=True,
        )

    # -----------------------------------------------------------------
    def _sortear_recompensas(self):
        chances = [
            ("pocao", 0.70),
            ("dica", 0.65),
            ("foco", 0.40),
            ("dica", 0.25),
        ]
        recompensas = {}
        for item, chance in chances:
            if random.random() < chance:
                recompensas[item] = recompensas.get(item, 0) + 1

        if not recompensas:
            item = random.choice(["pocao", "dica", "foco"])
            recompensas[item] = 1
        return recompensas

    # -----------------------------------------------------------------
    def _nome_item(self, item):
        nomes = {
            "pocao": "POCAO",
            "foco": "FOCO",
            "dica": "DICA",
        }
        return nomes.get(item, item.upper())

    # -----------------------------------------------------------------
    def _mostrar_mensagem(self, texto, proximo, duracao=C.ANIM_MESSAGE_DURATION,
                          aguardar_confirmacao=False):
        self.tw = Typewriter(texto)
        self.proximo_estado = proximo
        self.timer = animation.Timer(duracao)
        self.mensagem_aguarda_confirmacao = aguardar_confirmacao
        self.estado = C.STATE_MESSAGE

    # -----------------------------------------------------------------
    def _avancar_mensagem(self):
        if self.proximo_estado == C.STATE_RESTART_BATTLE:
            self.reiniciar(inventario=self.inventario)
        else:
            self.estado = self.proximo_estado

    # -----------------------------------------------------------------
    # UPDATE
    # -----------------------------------------------------------------
    def update(self):
        self.frame += 1
        self.tw.tick()

        # HP visual suave: se aproxima do HP real gradualmente
        self._atualizar_hp_visual()

        if self.estado == C.STATE_MESSAGE:
            if self.mensagem_aguarda_confirmacao:
                return
            self.timer.tick()
            if self.timer.terminou() and self.tw.terminou():
                self._avancar_mensagem()
            return

        if self.estado == C.STATE_INPUT and not self.nota_aberta:
            self.resposta_timer.tick()
            if self.resposta_timer.terminou():
                self.combo = 0
                self.especial_ativado = False
                self._iniciar_defesa(C.DAMAGE_ON_FAIL[self.dificuldade_atual])
            return

        if self.estado == C.STATE_DEFENSE_INPUT:
            self.defesa_timer.tick()
            if self.defesa_timer.terminou():
                self._resolver_defesa(False)
            return

        if self.estado == C.STATE_PLAYER_ATTACK:
            self.anim_timer.tick()
            if self.anim_timer.terminou():
                if self.boss_hp <= 0:
                    if self.boss_hp_display <= 0.5:
                        self._finalizar_vitoria()
                    return
                extra = "\nRAIO LOGICO ativado!" if self.especial_ativado else f"\nCombo atual: {self.combo}."
                self._mostrar_mensagem(
                    f"E super efetivo!\nEQUACIONIS sofreu {self.ultimo_dano} de dano.{extra}",
                    proximo=C.STATE_DIFFICULTY,
                )
            return

        if self.estado == C.STATE_BOSS_ATTACK:
            self.anim_timer.tick()
            if self.anim_timer.terminou():
                if self.player_hp <= 0:
                    if self.player_hp_display <= 0.5:
                        self.estado = C.STATE_DEFEAT
                    return
                if self.defesa_sucesso:
                    msg = f"Defesa correta!\nDano reduzido para {self.ultimo_dano}."
                else:
                    msg = f"EQUACIONIS usou ALGEBRAGEM!\nVoce perdeu {self.ultimo_dano} de HP."
                self._mostrar_mensagem(msg, proximo=C.STATE_DIFFICULTY)
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
        ui.draw_player_platform(surface)

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
        ui.draw_status_line(surface, self.combo, self.carga_especial)
        if self._mostrar_botao_nota():
            ui.draw_note_button(surface, ativo=self.nota_aberta)

        # 4) Painel inferior conforme o estado
        self._render_painel_inferior(surface)

        if self.nota_aberta:
            ui.draw_note_overlay(surface, self.equacao_texto, self.nota_texto)

    # -----------------------------------------------------------------
    def _render_sprites(self, surface):
        boss_pos   = list(C.POS_BOSS)
        player_pos = list(C.POS_PLAYER)

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
            # Mantem a proporcao do PNG para nao deformar o sprite.
            boss_img = _scale_to_fit(boss_frame, max_width=300, max_height=215)
            surface.blit(boss_img, (boss_pos[0], boss_pos[1]))
        else:
            # fallback: sprite procedural
            surface.blit(sprites.get_boss_sprite(boss_state),
                         (boss_pos[0], boss_pos[1]))

        # --- player: usa PNG se disponivel, senao procedural ---
        player_frame = AL.get_player_frame(player_state, self.frame)
        if player_frame is not None:
            # Mantem a proporcao do PNG para nao deformar o sprite.
            player_img = _scale_to_fit(player_frame, max_width=230, max_height=190)
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

        elif e == C.STATE_ITEM_SELECT:
            ui.draw_dialog_box(surface, "Escolha um item da mochila:")
            ui.draw_item_menu(surface, self.item_idx, self.inventario)

        elif e == C.STATE_EQUATION_SHOW:
            ui.draw_dialog_box(surface, self.tw.visivel(),
                               mostrar_seta=self.tw.terminou())

        elif e == C.STATE_INPUT:
            ui.draw_input_box(surface, self.input_texto, self.equacao_texto,
                              self.resposta_timer.restante / C.FPS,
                              self.resposta_tempo_total)

        elif e == C.STATE_DEFENSE_INPUT:
            ui.draw_defense_box(surface, self.defesa_pergunta, self.defesa_input,
                                self.defesa_timer.restante / C.FPS,
                                self.defesa_tempo_total)

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


def _scale_to_fit(image, max_width, max_height):
    largura = image.get_width()
    altura = image.get_height()
    escala = min(max_width / largura, max_height / altura)
    tamanho = (max(1, int(largura * escala)), max(1, int(altura * escala)))
    return pygame.transform.smoothscale(image, tamanho)
