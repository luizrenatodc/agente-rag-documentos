"""Responde perguntas com base em documentos locais e sempre cita a fonte."""
import math
import re
import sys
from collections import Counter
from pathlib import Path

PARADAS = set("a o e de da do das dos em no na nos nas um uma para por com que qual quais como é ao aos se".split())


def tokens(texto):
    return [p for p in re.findall(r"[a-zà-ú0-9]+", texto.lower()) if p not in PARADAS]


def trechos(pasta):
    for arquivo in sorted(Path(pasta).glob("*.md")):
        for bloco in arquivo.read_text(encoding="utf-8").split("\n\n"):
            if bloco.strip() and not bloco.startswith("#"):
                yield arquivo.name, bloco.strip()


class Indice:
    def __init__(self, pasta):
        self.itens = [(fonte, texto, Counter(tokens(texto))) for fonte, texto in trechos(pasta)]
        self.df = Counter(t for _, _, c in self.itens for t in c)

    def idf(self, termo):
        return math.log((1 + len(self.itens)) / (1 + self.df[termo])) + 1

    def buscar(self, pergunta, k=2):
        termos = tokens(pergunta)
        notas = []
        for fonte, texto, c in self.itens:
            nota = sum((c[t] / sum(c.values())) * self.idf(t) for t in termos)
            if nota > 0:
                notas.append((nota, fonte, texto))
        return sorted(notas, key=lambda n: n[0], reverse=True)[:k]


def responder(indice, pergunta, modelo=None):
    achados = indice.buscar(pergunta)
    if not achados:
        return {"resposta": "Não encontrei isso nos documentos.", "fontes": []}
    fontes = sorted({f for _, f, _ in achados})
    contexto = "\n".join(t for _, _, t in achados)
    texto = modelo(pergunta, contexto) if modelo else contexto
    return {"resposta": texto, "fontes": fontes}


if __name__ == "__main__":
    pergunta = " ".join(sys.argv[1:]) or "Quantos dias de férias eu tenho?"
    r = responder(Indice(Path(__file__).parent / "documentos"), pergunta)
    print(r["resposta"], "\nFontes:", ", ".join(r["fontes"]) or "nenhuma")
