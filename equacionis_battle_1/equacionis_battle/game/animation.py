"""
animation.py
----------------------------------------
Utilitarios de animacao por contagem de frames.

- Timer: conta ate terminar; sabe se ainda esta rodando
- shake_offset(t): retorna (dx, dy) para balancar um sprite
- hop_offset(t, duracao): pulinho para cima e volta (usado no ataque)
- bob_offset(frame): flutuacao suave (usado no idle do boss)
"""
import math


class Timer:
    """Conta frames decrescentes. Use tick() a cada loop."""
    def __init__(self, duracao: int):
        self.duracao = duracao
        self.restante = duracao

    def tick(self):
        if self.restante > 0:
            self.restante -= 1

    def terminou(self) -> bool:
        return self.restante <= 0

    def progresso(self) -> float:
        """0.0 no inicio, 1.0 no fim."""
        if self.duracao <= 0:
            return 1.0
        return 1.0 - (self.restante / self.duracao)

    def reiniciar(self, nova_duracao: int = None):
        if nova_duracao is not None:
            self.duracao = nova_duracao
        self.restante = self.duracao


def shake_offset(frame_count: int, intensidade: int = 6):
    """Retorna (dx, dy) oscilante para efeito de tremor."""
    dx = int(math.sin(frame_count * 1.3) * intensidade)
    dy = int(math.cos(frame_count * 1.7) * intensidade / 2)
    return dx, dy


def hop_offset(progresso: float, altura: int = 20):
    """
    Pulinho suave: sobe e volta ao longo de progresso em [0, 1].
    Usa seno de 0 a pi.
    """
    return int(-math.sin(progresso * math.pi) * altura)


def bob_offset(frame_count: int, amplitude: int = 4, velocidade: float = 0.05):
    """Flutuacao lenta para cima e para baixo (usado em idle)."""
    return int(math.sin(frame_count * velocidade) * amplitude)


def flash_alpha(progresso: float, intensidade_max: int = 160) -> int:
    """
    Alpha de branco sobreposto durante o dano.
    Comeca forte, enfraquece ate sumir.
    """
    return max(0, int((1.0 - progresso) * intensidade_max))
