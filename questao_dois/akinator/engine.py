"""
engine.py
=========
Motor de Inferência: Eliminação em Espaço de Hipóteses com Máxima Informação.

Algoritmo central
-----------------
1. Começa com TODAS as hipóteses (animais) ativas.
2. A cada turno, escolhe o ATRIBUTO de maior information gain:
     IG(attr) = H(S) - H(S | attr)
   onde H é a entropia de Shannon e S é o conjunto de hipóteses restantes.
   Na prática: o atributo que divide as hipóteses mais próximo de 50/50
   é o que reduz mais incerteza.
3. O usuário responde Sim / Não / Não Sei.
   - Sim  → mantém apenas hipóteses com attr = 1
   - Não  → mantém apenas hipóteses com attr = 0
   - Não Sei → não elimina; marca atributo como perguntado (não repete)
4. Repete até sobrar 1 hipótese, sem mais perguntas, ou atingir max_questions.

Tratamento de -1 (incerto na base)
-----------------------------------
Hipóteses com valor -1 para um atributo são tratadas como NEUTRAS:
  - Não são eliminadas por nenhuma resposta (nem Sim nem Não).
  - Contribuem com peso 0.5 no cálculo de information gain.
"""

from __future__ import annotations
import math
from knowledge_base import ANIMALS, ATTRIBUTES


class AkinatorEngine:
    """Motor do jogo Akinator."""

    def __init__(self):
        # Hipóteses ativas: todos os animais no início
        self.hypotheses: list[str] = list(ANIMALS.keys())
        # Atributos já perguntados (para não repetir)
        self.asked: set[str] = set()
        # Histórico de perguntas desta sessão
        self.history: list[dict] = []   # [{attr, question, answer}, ...]

    # ──────────────────────────────────────────────────────────────
    # Information Gain
    # ──────────────────────────────────────────────────────────────

    @staticmethod
    def _entropy(values: list[float]) -> float:
        """Entropia de Shannon de uma lista de probabilidades."""
        total = sum(values)
        if total == 0:
            return 0.0
        h = 0.0
        for v in values:
            p = v / total
            if p > 0:
                h -= p * math.log2(p)
        return h

    def _score_attribute(self, attr: str) -> float:
        """
        Calcula o Information Gain de perguntar `attr` dado o conjunto
        atual de hipóteses.

        Hipóteses com valor -1 contribuem 0.5 para cada ramo (Sim e Não),
        simulando incerteza simétrica.
        """
        yes_count = 0.0   # hipóteses compatíveis com Sim
        no_count = 0.0    # hipóteses compatíveis com Não

        for animal in self.hypotheses:
            val = ANIMALS[animal].get(attr, -1)
            if val == 1:
                yes_count += 1
            elif val == 0:
                no_count += 1
            else:  # -1: neutro
                yes_count += 0.5
                no_count += 0.5

        total = yes_count + no_count
        if total == 0:
            return 0.0

        # Entropia antes da pergunta
        h_before = self._entropy([yes_count, no_count])

        # Entropia esperada depois (condicional)
        # Ramo Sim: yes_count hipóteses
        # Ramo Não: no_count hipóteses
        h_yes = self._entropy([yes_count, 0])  # só um ramo — 0 bits
        h_no  = self._entropy([no_count, 0])
        h_after = (yes_count / total) * h_yes + (no_count / total) * h_no

        return h_before - h_after  # quanto de entropia removemos

    def best_question(self) -> str | None:
        """
        Retorna o atributo (chave) de maior Information Gain
        que ainda não foi perguntado. Retorna None se não houver mais.
        """
        candidates = [
            a for a in ATTRIBUTES
            if a not in self.asked
        ]
        if not candidates:
            return None

        # Filtra atributos que realmente discriminam as hipóteses restantes
        useful = [a for a in candidates if self._score_attribute(a) > 0]
        if not useful:
            # nenhum atributo discrimina mais → usa qualquer um não perguntado
            useful = candidates

        return max(useful, key=self._score_attribute)

    # ──────────────────────────────────────────────────────────────
    # Eliminação de Hipóteses
    # ──────────────────────────────────────────────────────────────

    def answer(self, attr: str, response: str) -> None:
        """
        Processa a resposta do usuário e elimina hipóteses incompatíveis.

        Parâmetros
        ----------
        attr     : chave do atributo perguntado
        response : "s" | "n" | "ns"
        """
        self.asked.add(attr)
        self.history.append({
            "attr": attr,
            "question": ATTRIBUTES[attr],
            "answer": response,
        })

        if response == "s":
            # Mantém apenas hipóteses com valor = 1 (ou -1 → neutro)
            self.hypotheses = [
                a for a in self.hypotheses
                if ANIMALS[a].get(attr, -1) != 0
            ]
        elif response == "n":
            # Mantém apenas hipóteses com valor = 0 (ou -1 → neutro)
            self.hypotheses = [
                a for a in self.hypotheses
                if ANIMALS[a].get(attr, -1) != 1
            ]
        # "ns" → não elimina nada

    # ──────────────────────────────────────────────────────────────
    # Estado do jogo
    # ──────────────────────────────────────────────────────────────

    def is_solved(self) -> bool:
        return len(self.hypotheses) == 1

    def top_hypothesis(self) -> str | None:
        """Hipótese mais provável = primeira da lista restante."""
        return self.hypotheses[0] if self.hypotheses else None

    def remaining(self) -> list[str]:
        return list(self.hypotheses)

    def questions_asked(self) -> int:
        return len(self.history)
