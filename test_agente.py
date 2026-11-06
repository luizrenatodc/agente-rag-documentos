import unittest
from pathlib import Path

from agente import Indice, responder

INDICE = Indice(Path(__file__).parent / "documentos")


class TestAgente(unittest.TestCase):
    def test_acha_o_documento_certo(self):
        self.assertEqual(responder(INDICE, "Qual o prazo do reembolso de viagem?")["fontes"][0], "reembolso.md")

    def test_sem_modelo_devolve_os_trechos_relevantes(self):
        self.assertIn("30 dias de férias por ano", responder(INDICE, "Quantos dias de férias eu tenho?")["resposta"])

    def test_nao_inventa(self):
        r = responder(INDICE, "xilofone")
        self.assertEqual(r["fontes"], [])
        self.assertIn("Não encontrei", r["resposta"])

    def test_passa_contexto_para_o_modelo(self):
        r = responder(INDICE, "dias de férias", lambda p, c: "ctx:" + c)
        self.assertIn("30 dias", r["resposta"])


if __name__ == "__main__":
    unittest.main()
