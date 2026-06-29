"""
knowledge_base.py
=================
Base de Conhecimento do Akinator de Animais.

Domínio: 25 animais × 21 atributos.

Abordagem de Inferência
-----------------------
Eliminação em Espaço de Hipóteses (Hypothesis Space Elimination):
  - Cada animal é uma hipótese.
  - A cada resposta do usuário, eliminamos hipóteses INCOMPATÍVEIS.
  - A próxima pergunta é escolhida por MÁXIMA INFORMAÇÃO (Information Gain).
  - "Não sei" preserva todas as hipóteses (não elimina nada).

Estrutura dos dados
-------------------
ANIMALS  : dict[str, dict[str, int]]
  nome_do_animal -> {atributo: valor}
  valor = 1 (sim), 0 (não), -1 (incerto/não aplicável)

ATTRIBUTES: dict[str, str]
  chave_do_atributo -> texto da pergunta
"""

from __future__ import annotations

# ─────────────────────────────────────────────────────────────────────────────
# 21 ATRIBUTOS (características)
# ─────────────────────────────────────────────────────────────────────────────
ATTRIBUTES: dict[str, str] = {
    "mamifero":         "É um mamífero?",
    "ave":              "É uma ave?",
    "reptil":           "É um réptil?",
    "peixe":            "É um peixe?",
    "anfibio":          "É um anfíbio?",
    "invertebrado":     "É um invertebrado (inseto, aranha, etc.)?",
    "domestico":        "É um animal doméstico (de estimação comum)?",
    "selvagem":         "Vive predominantemente na natureza selvagem?",
    "aquatico":         "Vive na água (total ou parcialmente)?",
    "voa":              "Consegue voar?",
    "carnivoro":        "É carnívoro (se alimenta principalmente de carne)?",
    "herbivoro":        "É herbívoro (se alimenta principalmente de plantas)?",
    "africa":           "É originário / predominante na África?",
    "grande_porte":     "É de grande porte (maior que um cachorro médio)?",
    "penas":            "Tem penas?",
    "pelo":             "Tem pelo ou pelagem?",
    "venenoso":         "É venenoso ou peçonhento?",
    "extinto":          "Está extinto ou é pré-histórico?",
    "miau_latido":      "Faz miau ou emite sons agudos (ao invés de latir/uivar)?",
    "pescoço_longo":    "Tem pescoço visivelmente longo (maior que o tronco)?",
    "nadadeiras":       "Possui nadadeiras ou corpo totalmente adaptado para nadar?",
    "porte_gigante":    "É de porte gigantesco (maior que um ônibus ou elefante)?",
}

# ─────────────────────────────────────────────────────────────────────────────
# 25 ANIMAIS com seus atributos
# ─────────────────────────────────────────────────────────────────────────────
ANIMALS: dict[str, dict[str, int]] = {
    "Leão": {
        "mamifero":1,"ave":0,"reptil":0,"peixe":0,"anfibio":0,"invertebrado":0,
        "domestico":0,"selvagem":1,"aquatico":0,"voa":0,
        "carnivoro":1,"herbivoro":0,"africa":1,"grande_porte":1,
        "penas":0,"pelo":1,"venenoso":0,"extinto":0,
        "miau_latido":1,"pescoço_longo":0,"nadadeiras":0,"porte_gigante":0,
    },
    "Elefante": {
        "mamifero":1,"ave":0,"reptil":0,"peixe":0,"anfibio":0,"invertebrado":0,
        "domestico":0,"selvagem":1,"aquatico":0,"voa":0,
        "carnivoro":0,"herbivoro":1,"africa":1,"grande_porte":1,
        "penas":0,"pelo":0,"venenoso":0,"extinto":0,
        "miau_latido":0,"pescoço_longo":0,"nadadeiras":0,"porte_gigante":1,
    },
    "Pinguim": {
        "mamifero":0,"ave":1,"reptil":0,"peixe":0,"anfibio":0,"invertebrado":0,
        "domestico":0,"selvagem":1,"aquatico":1,"voa":0,
        "carnivoro":1,"herbivoro":0,"africa":0,"grande_porte":0,
        "penas":1,"pelo":0,"venenoso":0,"extinto":0,
        "miau_latido":0,"pescoço_longo":0,"nadadeiras":1,"porte_gigante":0,
    },
    "Golfinho": {
        "mamifero":1,"ave":0,"reptil":0,"peixe":0,"anfibio":0,"invertebrado":0,
        "domestico":0,"selvagem":1,"aquatico":1,"voa":0,
        "carnivoro":1,"herbivoro":0,"africa":0,"grande_porte":1,
        "penas":0,"pelo":0,"venenoso":0,"extinto":0,
        "miau_latido":0,"pescoço_longo":0,"nadadeiras":1,"porte_gigante":0,
    },
    "Tubarão": {
        "mamifero":0,"ave":0,"reptil":0,"peixe":1,"anfibio":0,"invertebrado":0,
        "domestico":0,"selvagem":1,"aquatico":1,"voa":0,
        "carnivoro":1,"herbivoro":0,"africa":0,"grande_porte":1,
        "penas":0,"pelo":0,"venenoso":0,"extinto":0,
        "miau_latido":0,"pescoço_longo":0,"nadadeiras":1,"porte_gigante":0,
    },
    "Águia": {
        "mamifero":0,"ave":1,"reptil":0,"peixe":0,"anfibio":0,"invertebrado":0,
        "domestico":0,"selvagem":1,"aquatico":0,"voa":1,
        "carnivoro":1,"herbivoro":0,"africa":0,"grande_porte":0,
        "penas":1,"pelo":0,"venenoso":0,"extinto":0,
        "miau_latido":0,"pescoço_longo":0,"nadadeiras":0,"porte_gigante":0,
    },
    "Cobra": {
        "mamifero":0,"ave":0,"reptil":1,"peixe":0,"anfibio":0,"invertebrado":0,
        "domestico":0,"selvagem":1,"aquatico":0,"voa":0,
        "carnivoro":1,"herbivoro":0,"africa":0,"grande_porte":0,
        "penas":0,"pelo":0,"venenoso":1,"extinto":0,
        "miau_latido":0,"pescoço_longo":0,"nadadeiras":0,"porte_gigante":0,
    },
    "Sapo": {
        "mamifero":0,"ave":0,"reptil":0,"peixe":0,"anfibio":1,"invertebrado":0,
        "domestico":0,"selvagem":1,"aquatico":1,"voa":0,
        "carnivoro":1,"herbivoro":0,"africa":0,"grande_porte":0,
        "penas":0,"pelo":0,"venenoso":1,"extinto":0,
        "miau_latido":0,"pescoço_longo":0,"nadadeiras":0,"porte_gigante":0,
    },
    "Cachorro": {
        "mamifero":1,"ave":0,"reptil":0,"peixe":0,"anfibio":0,"invertebrado":0,
        "domestico":1,"selvagem":0,"aquatico":0,"voa":0,
        "carnivoro":1,"herbivoro":0,"africa":0,"grande_porte":0,
        "penas":0,"pelo":1,"venenoso":0,"extinto":0,
        "miau_latido":0,"pescoço_longo":0,"nadadeiras":0,"porte_gigante":0,
    },
    "Gato": {
        "mamifero":1,"ave":0,"reptil":0,"peixe":0,"anfibio":0,"invertebrado":0,
        "domestico":1,"selvagem":0,"aquatico":0,"voa":0,
        "carnivoro":1,"herbivoro":0,"africa":0,"grande_porte":0,
        "penas":0,"pelo":1,"venenoso":0,"extinto":0,
        "miau_latido":1,"pescoço_longo":0,"nadadeiras":0,"porte_gigante":0,
    },
    "Cavalo": {
        "mamifero":1,"ave":0,"reptil":0,"peixe":0,"anfibio":0,"invertebrado":0,
        "domestico":1,"selvagem":0,"aquatico":0,"voa":0,
        "carnivoro":0,"herbivoro":1,"africa":0,"grande_porte":1,
        "penas":0,"pelo":1,"venenoso":0,"extinto":0,
        "miau_latido":0,"pescoço_longo":0,"nadadeiras":0,"porte_gigante":0,
    },
    "Baleia": {
        "mamifero":1,"ave":0,"reptil":0,"peixe":0,"anfibio":0,"invertebrado":0,
        "domestico":0,"selvagem":1,"aquatico":1,"voa":0,
        "carnivoro":1,"herbivoro":0,"africa":0,"grande_porte":1,
        "penas":0,"pelo":0,"venenoso":0,"extinto":0,
        "miau_latido":0,"pescoço_longo":0,"nadadeiras":1,"porte_gigante":1,
    },
    "Papagaio": {
        "mamifero":0,"ave":1,"reptil":0,"peixe":0,"anfibio":0,"invertebrado":0,
        "domestico":1,"selvagem":0,"aquatico":0,"voa":1,
        "carnivoro":0,"herbivoro":1,"africa":0,"grande_porte":0,
        "penas":1,"pelo":0,"venenoso":0,"extinto":0,
        "miau_latido":0,"pescoço_longo":0,"nadadeiras":0,"porte_gigante":0,
    },
    "Crocodilo": {
        "mamifero":0,"ave":0,"reptil":1,"peixe":0,"anfibio":0,"invertebrado":0,
        "domestico":0,"selvagem":1,"aquatico":1,"voa":0,
        "carnivoro":1,"herbivoro":0,"africa":1,"grande_porte":1,
        "penas":0,"pelo":0,"venenoso":0,"extinto":0,
        "miau_latido":0,"pescoço_longo":0,"nadadeiras":0,"porte_gigante":0,
    },
    "Gorila": {
        "mamifero":1,"ave":0,"reptil":0,"peixe":0,"anfibio":0,"invertebrado":0,
        "domestico":0,"selvagem":1,"aquatico":0,"voa":0,
        "carnivoro":0,"herbivoro":1,"africa":1,"grande_porte":1,
        "penas":0,"pelo":1,"venenoso":0,"extinto":0,
        "miau_latido":0,"pescoço_longo":0,"nadadeiras":0,"porte_gigante":0,
    },
    "Abelha": {
        "mamifero":0,"ave":0,"reptil":0,"peixe":0,"anfibio":0,"invertebrado":1,
        "domestico":0,"selvagem":1,"aquatico":0,"voa":1,
        "carnivoro":0,"herbivoro":1,"africa":0,"grande_porte":0,
        "penas":0,"pelo":0,"venenoso":1,"extinto":0,
        "miau_latido":0,"pescoço_longo":0,"nadadeiras":0,"porte_gigante":0,
    },
    "Urso Polar": {
        "mamifero":1,"ave":0,"reptil":0,"peixe":0,"anfibio":0,"invertebrado":0,
        "domestico":0,"selvagem":1,"aquatico":0,"voa":0,
        "carnivoro":1,"herbivoro":0,"africa":0,"grande_porte":1,
        "penas":0,"pelo":1,"venenoso":0,"extinto":0,
        "miau_latido":0,"pescoço_longo":0,"nadadeiras":0,"porte_gigante":0,
    },
    "Tartaruga": {
        "mamifero":0,"ave":0,"reptil":1,"peixe":0,"anfibio":0,"invertebrado":0,
        "domestico":1,"selvagem":0,"aquatico":1,"voa":0,
        "carnivoro":0,"herbivoro":1,"africa":0,"grande_porte":0,
        "penas":0,"pelo":0,"venenoso":0,"extinto":0,
        "miau_latido":0,"pescoço_longo":0,"nadadeiras":1,"porte_gigante":0,
    },
    "Morcego": {
        "mamifero":1,"ave":0,"reptil":0,"peixe":0,"anfibio":0,"invertebrado":0,
        "domestico":0,"selvagem":1,"aquatico":0,"voa":1,
        "carnivoro":1,"herbivoro":0,"africa":0,"grande_porte":0,
        "penas":0,"pelo":1,"venenoso":0,"extinto":0,
        "miau_latido":0,"pescoço_longo":0,"nadadeiras":0,"porte_gigante":0,
    },
    "Girafa": {
        "mamifero":1,"ave":0,"reptil":0,"peixe":0,"anfibio":0,"invertebrado":0,
        "domestico":0,"selvagem":1,"aquatico":0,"voa":0,
        "carnivoro":0,"herbivoro":1,"africa":1,"grande_porte":1,
        "penas":0,"pelo":1,"venenoso":0,"extinto":0,
        "miau_latido":0,"pescoço_longo":1,"nadadeiras":0,"porte_gigante":0,
    },
    "Polvos": {
        "mamifero":0,"ave":0,"reptil":0,"peixe":0,"anfibio":0,"invertebrado":1,
        "domestico":0,"selvagem":1,"aquatico":1,"voa":0,
        "carnivoro":1,"herbivoro":0,"africa":0,"grande_porte":0,
        "penas":0,"pelo":0,"venenoso":1,"extinto":0,
        "miau_latido":0,"pescoço_longo":0,"nadadeiras":0,"porte_gigante":0,
    },
    "T-Rex": {
        "mamifero":0,"ave":0,"reptil":1,"peixe":0,"anfibio":0,"invertebrado":0,
        "domestico":0,"selvagem":1,"aquatico":0,"voa":0,
        "carnivoro":1,"herbivoro":0,"africa":0,"grande_porte":1,
        "penas":0,"pelo":0,"venenoso":0,"extinto":1,
        "miau_latido":0,"pescoço_longo":0,"nadadeiras":0,"porte_gigante":1,
    },
    "Lobo": {
        "mamifero":1,"ave":0,"reptil":0,"peixe":0,"anfibio":0,"invertebrado":0,
        "domestico":0,"selvagem":1,"aquatico":0,"voa":0,
        "carnivoro":1,"herbivoro":0,"africa":0,"grande_porte":0,
        "penas":0,"pelo":1,"venenoso":0,"extinto":0,
        "miau_latido":0,"pescoço_longo":0,"nadadeiras":0,"porte_gigante":0,
    },
    "Flamingo": {
        "mamifero":0,"ave":1,"reptil":0,"peixe":0,"anfibio":0,"invertebrado":0,
        "domestico":0,"selvagem":1,"aquatico":1,"voa":1,
        "carnivoro":0,"herbivoro":1,"africa":1,"grande_porte":0,
        "penas":1,"pelo":0,"venenoso":0,"extinto":0,
        "miau_latido":0,"pescoço_longo":1,"nadadeiras":0,"porte_gigante":0,
    },
    "Ornitorrinco": {
        "mamifero":1,"ave":0,"reptil":0,"peixe":0,"anfibio":0,"invertebrado":0,
        "domestico":0,"selvagem":1,"aquatico":1,"voa":0,
        "carnivoro":1,"herbivoro":0,"africa":0,"grande_porte":0,
        "penas":0,"pelo":1,"venenoso":1,"extinto":0,
        "miau_latido":0,"pescoço_longo":0,"nadadeiras":0,"porte_gigante":0,
    },
}
