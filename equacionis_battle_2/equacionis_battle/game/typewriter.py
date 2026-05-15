"""
typewriter.py  (NOVO)
----------------------------------------
Escreve um texto aos poucos, caractere por caractere (efeito Pokemon).
Uso:
    tw = Typewriter("Equacionis apareceu!")
    # a cada frame:
    tw.tick()
    texto_visivel = tw.visivel()
    if tw.terminou(): ...
    tw.pular()  # mostra tudo (usuario apertou ENTER)
"""
from . import constants as C


class Typewriter:
    def __init__(self, texto: str = "", velocidade: float = None):
        self.velocidade = velocidade or C.TYPEWRITER_CHARS_PER_FRAME
        self.definir(texto)

    def definir(self, texto: str):
        self.texto_completo = texto
        self.progresso_f = 0.0

    def tick(self):
        if self.progresso_f < len(self.texto_completo):
            self.progresso_f += self.velocidade

    def visivel(self) -> str:
        return self.texto_completo[: int(self.progresso_f)]

    def terminou(self) -> bool:
        return self.progresso_f >= len(self.texto_completo)

    def pular(self):
        self.progresso_f = len(self.texto_completo)
