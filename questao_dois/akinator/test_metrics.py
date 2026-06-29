"""
test_metrics.py
===============
Script de Teste Simulado para Extração de Métricas.

Como executar
-------------
    python test_metrics.py

O que faz
---------
Para cada um dos 25 animais da base de conhecimento, simula uma partida
em que o "usuário" conhece perfeitamente o animal e responde com base nos
atributos reais da KB (sempre Sim ou Não, nunca Não Sei).

Métricas geradas
----------------
  - Número de perguntas por animal
  - Número médio de perguntas até o acerto
  - Taxa de acerto (%)
  - Casos de falha (ambiguidade irresolvível ou esgotamento de perguntas)
  - Distribuição de perguntas (histograma)
  - Relatório detalhado por animal

Configurações
-------------
  USE_NS_PROB : probabilidade de responder "Não Sei" (simula incerteza do
                usuário). Defina como 0.0 para cenário ideal, 0.2 para
                simulação realista com 20% de respostas "Não sei".
"""

from __future__ import annotations
import random
import statistics
from collections import Counter, defaultdict
from engine import AkinatorEngine
from knowledge_base import ANIMALS, ATTRIBUTES


# ─────────────────────────────────────────────────────────────────────────────
# Configurações da simulação
# ─────────────────────────────────────────────────────────────────────────────
USE_NS_PROB: float = 0.0       # 0.0 = ideal (sem "Não sei"); 0.2 = 20% Não Sei
MAX_QUESTIONS: int = len(ATTRIBUTES)
RANDOM_SEED: int = 42
# ─────────────────────────────────────────────────────────────────────────────


def simulate_game(target_animal: str, ns_prob: float = 0.0) -> dict:
    """
    Simula uma partida completa onde o usuário pensou em `target_animal`.

    Estratégia de resposta
    ----------------------
    - Consulta o valor real na KB para cada atributo perguntado.
    - Com probabilidade `ns_prob`, responde "ns" em vez da resposta correta
      (simula incerteza).
    - Valor -1 na KB → responde "ns" (genuinamente incerto).

    Retorna dict com métricas da partida.
    """
    rng = random.Random(RANDOM_SEED + hash(target_animal))
    engine = AkinatorEngine()
    result = {
        "animal": target_animal,
        "questions_asked": 0,
        "solved": False,
        "correct_guess": False,
        "guessed": None,
        "remaining_count": 0,
        "question_log": [],       # [(attr, resposta_dada, valor_real)]
    }

    for _ in range(MAX_QUESTIONS):
        # Verifica condição de vitória
        if engine.is_solved():
            guess = engine.top_hypothesis()
            result["solved"] = True
            result["correct_guess"] = (guess == target_animal)
            result["guessed"] = guess
            result["remaining_count"] = 1
            break

        if len(engine.remaining()) == 0:
            result["guessed"] = None
            result["remaining_count"] = 0
            break

        attr = engine.best_question()
        if attr is None:
            # Sem mais perguntas: verifica se top hypothesis é correta
            guess = engine.top_hypothesis()
            result["guessed"] = guess
            result["remaining_count"] = len(engine.remaining())
            # Considera "solved" se acertou mesmo sem pergunta
            result["solved"] = (guess == target_animal)
            result["correct_guess"] = (guess == target_animal)
            break

        # Determina a resposta correta
        real_val = ANIMALS[target_animal].get(attr, -1)
        if real_val == -1:
            response = "ns"
        elif rng.random() < ns_prob:
            response = "ns"   # simula incerteza do usuário
        elif real_val == 1:
            response = "s"
        else:
            response = "n"

        result["question_log"].append((attr, response, real_val))
        result["questions_asked"] += 1
        engine.answer(attr, response)

    # Se saiu do loop sem definir guessed
    if result["guessed"] is None and engine.top_hypothesis():
        guess = engine.top_hypothesis()
        result["guessed"] = guess
        result["remaining_count"] = len(engine.remaining())
        result["correct_guess"] = (guess == target_animal)
        result["solved"] = result["correct_guess"]

    return result


def run_all_simulations(ns_prob: float = USE_NS_PROB) -> list[dict]:
    """Executa simulação para todos os animais e retorna lista de resultados."""
    results = []
    for animal in ANIMALS:
        r = simulate_game(animal, ns_prob=ns_prob)
        results.append(r)
    return results


def print_report(results: list[dict], ns_prob: float) -> None:
    """Imprime o relatório completo de métricas."""

    total = len(results)
    correct = [r for r in results if r["correct_guess"]]
    wrong   = [r for r in results if not r["correct_guess"]]

    questions_list = [r["questions_asked"] for r in correct]
    all_questions  = [r["questions_asked"] for r in results]

    print("=" * 60)
    print("         RELATÓRIO DE MÉTRICAS — AKINATOR DE ANIMAIS")
    print("=" * 60)
    print(f"  Animais testados      : {total}")
    print(f"  Probabilidade Não Sei : {ns_prob:.0%}")
    print()

    # ── Acurácia ────────────────────────────────────────────────
    accuracy = len(correct) / total * 100
    print(f"  Taxa de acerto        : {len(correct)}/{total}  ({accuracy:.1f}%)")
    print(f"  Casos de falha/empate : {len(wrong)}")
    print()

    # ── Perguntas (acertos) ──────────────────────────────────────
    if questions_list:
        print(f"  Perguntas (apenas acertos):")
        print(f"    Média   : {statistics.mean(questions_list):.2f}")
        print(f"    Mediana : {statistics.median(questions_list):.1f}")
        print(f"    Mínimo  : {min(questions_list)}")
        print(f"    Máximo  : {max(questions_list)}")
        if len(questions_list) > 1:
            print(f"    Desvio  : {statistics.stdev(questions_list):.2f}")
    print()

    # ── Histograma ───────────────────────────────────────────────
    hist = Counter(all_questions)
    print("  Distribuição de perguntas (todos os animais):")
    print(f"    {'Perguntas':<12} {'Animais':<8} Gráfico")
    for n in sorted(hist):
        bar = "█" * hist[n]
        print(f"    {n:<12} {hist[n]:<8} {bar}")
    print()

    # ── Tabela por animal ─────────────────────────────────────────
    print(f"  {'Animal':<20} {'Perguntas':<12} {'Acertou?':<10} {'Palpite'}")
    print("  " + "─" * 56)
    for r in sorted(results, key=lambda x: x["questions_asked"]):
        ok = "✔" if r["correct_guess"] else "✘"
        guess = r["guessed"] or "—"
        print(f"  {r['animal']:<20} {r['questions_asked']:<12} {ok:<10} {guess}")
    print()

    # ── Falhas ────────────────────────────────────────────────────
    if wrong:
        print("  DETALHES DOS CASOS DE FALHA:")
        for r in wrong:
            print(f"    • {r['animal']} → palpite: {r['guessed']}  "
                  f"(restavam {r['remaining_count']} hipóteses, "
                  f"{r['questions_asked']} perguntas)")
        print()

    # ── Atributos mais usados ─────────────────────────────────────
    attr_usage: Counter = Counter()
    for r in results:
        for attr, _, _ in r["question_log"]:
            attr_usage[attr] += 1

    print("  Top 8 atributos mais perguntados:")
    for attr, cnt in attr_usage.most_common(8):
        print(f"    {ATTRIBUTES[attr][:45]:<47} {cnt}x")
    print()

    print("=" * 60)


def run_sensitivity_analysis() -> None:
    """
    Análise de sensibilidade: executa simulações com diferentes
    probabilidades de resposta 'Não Sei' (0%, 10%, 20%, 30%).
    Útil para o relatório acadêmico.
    """
    print("\n" + "=" * 60)
    print("      ANÁLISE DE SENSIBILIDADE — Impacto do 'Não Sei'")
    print("=" * 60)
    print(f"  {'P(Não Sei)':<14} {'Acerto%':<12} {'Média Pergs':<14} {'Falhas'}")
    print("  " + "─" * 50)

    for prob in [0.0, 0.10, 0.20, 0.30]:
        random.seed(RANDOM_SEED)
        results = run_all_simulations(ns_prob=prob)
        correct = [r for r in results if r["correct_guess"]]
        qs = [r["questions_asked"] for r in correct]
        acc = len(correct) / len(results) * 100
        avg_q = statistics.mean(qs) if qs else float("inf")
        fails = len(results) - len(correct)
        print(f"  {prob:<14.0%} {acc:<12.1f} {avg_q:<14.2f} {fails}")

    print()


if __name__ == "__main__":
    print("\n🔬 Iniciando simulações...\n")

    # Cenário 1: Ideal (usuário sabe tudo)
    results_ideal = run_all_simulations(ns_prob=0.0)
    print_report(results_ideal, ns_prob=0.0)

    # Cenário 2: Realista (20% de respostas Não Sei)
    print("\n" + "─" * 60)
    print("  [CENÁRIO REALISTA — 20% de respostas 'Não Sei']")
    print("─" * 60)
    results_realistic = run_all_simulations(ns_prob=0.20)
    print_report(results_realistic, ns_prob=0.20)

    # Análise de sensibilidade
    run_sensitivity_analysis()

    print("✅ Métricas geradas com sucesso.")
    print("   Use os dados acima no seu relatório.\n")
