"""
constants.py
----------------------------------------
Centraliza TODAS as configurações ajustáveis do jogo.
Marlon: para alterar HP, dano ou cores, mexa aqui.
"""

# ---------- Tela ----------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TITLE = "Equacionis - Batalha Matematica"

# ---------- Cores (paleta baseada na referencia visual) ----------
WHITE        = (255, 255, 255)
BLACK        = (0, 0, 0)
CREAM        = (248, 240, 210)   # fundo de caixas estilo Pokemon
DARK_CREAM   = (180, 160, 120)
BORDER_DARK  = (60, 50, 70)
BORDER_BLUE  = (25, 42, 68)
GRAY         = (100, 100, 110)
LIGHT_GRAY   = (200, 200, 210)

# Barras de HP
HP_GREEN  = (110, 200, 90)
HP_YELLOW = (240, 200, 60)
HP_RED    = (220, 80, 70)
EXP_BLUE  = (80, 160, 230)
GOLD      = (210, 170, 60)

# Jogador (nerd de costas)
SKIN     = (238, 198, 165)
HAIR     = (105, 65, 35)
SHIRT    = (235, 235, 235)
PANTS    = (55, 70, 100)
BACKPACK = (130, 80, 45)
BACKPACK_DARK = (90, 55, 30)
PAPER    = (250, 248, 230)

# Boss (Equacionis)
BOSS_AURA    = (120, 70, 170)
BOSS_AURA_LT = (170, 110, 210)
BOSS_BODY    = (45, 25, 65)
BOSS_BODY_LT = (85, 50, 115)
BOSS_GOLD    = (215, 175, 70)
BOSS_GOLD_LT = (245, 210, 110)
BOSS_FACE    = (230, 225, 220)
BOSS_EYES    = (180, 120, 230)

# Arena
ARENA_SKY_TOP    = (28, 38, 55)
ARENA_SKY_BOTTOM = (70, 85, 115)
ARENA_FLOOR_1    = (185, 165, 130)
ARENA_FLOOR_2    = (160, 140, 105)

# ---------- HP inicial ----------
PLAYER_MAX_HP = 100
BOSS_MAX_HP   = 200

# ---------- Dano por dificuldade ----------
# Dano causado no boss quando o jogador acerta
DAMAGE_ON_HIT = {
    "facil":   5,
    "medio":   10,
    "dificil": 20,
}

# Dano recebido pelo jogador quando erra (proporcional a dificuldade)
DAMAGE_ON_FAIL = {
    "facil":   5,
    "medio":   10,
    "dificil": 15,
}

# ---------- Niveis mostrados na UI ----------
PLAYER_NAME  = "NERD"
PLAYER_LEVEL = 25
BOSS_NAME    = "EQUACIONIS"
BOSS_LEVEL   = 80

# ---------- Estados da batalha ----------
STATE_INTRO            = "intro"
STATE_MENU             = "menu"
STATE_DIFFICULTY       = "difficulty"
STATE_EQUATION_SHOW    = "equation_show"
STATE_INPUT            = "input"
STATE_PLAYER_ATTACK    = "player_attack"
STATE_BOSS_ATTACK      = "boss_attack"
STATE_MESSAGE          = "message"
STATE_VICTORY          = "victory"
STATE_DEFEAT           = "defeat"

# ---------- Velocidades de animacao (em frames a 60fps) ----------
ANIM_INTRO_DURATION   = 60    # "Equacionis apareceu!"
ANIM_ATTACK_DURATION  = 45    # animacao de ataque
ANIM_DAMAGE_DURATION  = 30    # flash de dano
ANIM_MESSAGE_DURATION = 90    # mensagens intermediarias

# =====================================================================
# NOVO: integracao de assets (a partir daqui tudo foi adicionado)
# =====================================================================
import os

# Caminhos das pastas
ASSETS_SPRITES = os.path.join("assets", "sprites")
ASSETS_UI      = os.path.join("assets", "ui")

# Quantidade de frames dos sprites do boss
FRAMES_BOSS_IDLE   = 4
FRAMES_BOSS_ATTACK = 2
FRAMES_BOSS_HURT   = 4
FRAME_DURATION     = 10   # frames que cada imagem fica visivel (a 60fps = ~166ms)

# HP visual suave (o visual desliza, o HP real cai de uma vez)
HP_ANIM_SPEED = 0.8       # quantos pontos de HP o visual diminui por frame

# Typewriter (escrita gradual do texto)
TYPEWRITER_CHARS_PER_FRAME = 0.5   # caracteres por frame (~30 chars/s)

# Posicionamento das HUDs em pixels (ajuste fino se quiser mover)
POS_HP_BOSS    = (20, 40)
POS_HP_PLAYER  = (490, 290)
POS_BOSS       = (480, 90)   # canto superior direito da arena
POS_PLAYER     = (110, 300)  # inferior esquerdo da arena
POS_DIALOG     = (20, 470)   # caixa inferior
POS_MENU       = (490, 470)  # menu direita inferior
POS_INPUT      = (20, 470)   # input usa area inteira inferior
