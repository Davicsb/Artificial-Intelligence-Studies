"""
akinator.py
===========
Interface CLI do Akinator de Animais.

Como jogar
----------
  python akinator.py

Fluxo:
  1. Pense em um animal da lista.
  2. Responda as perguntas com:
       s   → Sim
       n   → Não
       ns  → Não sei
  3. O sistema exibe a hipótese mais provável a cada passo.
  4. Encerra quando acerta ou esgota as perguntas.
"""

from __future__ import annotations
from engine import AkinatorEngine
from knowledge_base import ATTRIBUTES

BANNER = r"""
╔══════════════════════════════════════════════════════════╗
║           🐾  AKINATOR DE ANIMAIS  🐾                   ║
║     Pensou em um animal? Eu vou adivinhar!              ║
╚══════════════════════════════════════════════════════════╝
Responda apenas: s (Sim)  |  n (Não)  |  ns (Não sei)
"""

MAX_QUESTIONS = len(ATTRIBUTES)  # limite superior: todos os atributos


def ask(question: str, q_num: int, total_remaining: int, top: str) -> str:
    """
    Exibe a pergunta e coleta resposta válida.
    Também mostra a hipótese mais provável antes de perguntar.
    """
    print(f"\n  💡 Hipótese atual mais provável: {top}")
    print(f"     (Restam {total_remaining} possibilidade(s))")
    print(f"\n  Pergunta {q_num}: {question}")

    while True:
        ans = input("  Sua resposta [s/n/ns]: ").strip().lower()
        if ans in ("s", "sim", "yes", "y"):
            return "s"
        if ans in ("n", "nao", "não", "no"):
            return "n"
        if ans in ("ns", "nao sei", "não sei", "?", "nr"):
            return "ns"
        print("  ⚠ Resposta inválida. Use apenas: s | n | ns")


def run_game() -> dict:
    """
    Executa uma partida interativa.
    Retorna métricas: {solved, animal_guessed, questions_asked, remaining}.
    """
    print(BANNER)
    input("  Pressione ENTER quando tiver pensado em um animal...\n")

    engine = AkinatorEngine()
    q_num = 0

    while True:
        # Verificações de parada
        if engine.is_solved():
            animal = engine.top_hypothesis()
            print(f"\n  🎉 Acho que sei! É o(a): ✨ {animal.upper()} ✨")
            correct = input("  Acertei? [s/n]: ").strip().lower()
            if correct in ("s", "sim"):
                print(f"  🏆 Acertei em {engine.questions_asked()} perguntas!\n")
                return {
                    "solved": True,
                    "animal_guessed": animal,
                    "questions_asked": engine.questions_asked(),
                    "remaining": engine.remaining(),
                }
            else:
                print("  😢 Errei desta vez. Qual animal você pensou?")
                real = input("  Animal: ").strip()
                print(f"  Vou aprender com isso! ('{real}' ainda não está bem na minha base.)\n")
                return {
                    "solved": False,
                    "animal_guessed": animal,
                    "questions_asked": engine.questions_asked(),
                    "remaining": engine.remaining(),
                }

        if len(engine.remaining()) == 0:
            print("\n  ❌ Eliminei todas as hipóteses! Não conheço esse animal.")
            return {
                "solved": False,
                "animal_guessed": None,
                "questions_asked": engine.questions_asked(),
                "remaining": [],
            }

        attr = engine.best_question()
        if attr is None:
            # Sem mais perguntas úteis
            top = engine.top_hypothesis()
            remaining = engine.remaining()
            print(f"\n  🤔 Fiquei sem perguntas! Meu melhor palpite é: {top}")
            print(f"     Outras possibilidades: {remaining}")
            correct = input("  Acertei? [s/n]: ").strip().lower()
            solved = correct in ("s", "sim")
            return {
                "solved": solved,
                "animal_guessed": top,
                "questions_asked": engine.questions_asked(),
                "remaining": remaining,
            }

        q_num += 1
        top = engine.top_hypothesis() or "?"
        response = ask(ATTRIBUTES[attr], q_num, len(engine.remaining()), top)
        engine.answer(attr, response)

    # nunca alcançado, mas por completude
    return {"solved": False, "animal_guessed": None,
            "questions_asked": q_num, "remaining": engine.remaining()}


def play_again() -> bool:
    again = input("  Jogar novamente? [s/n]: ").strip().lower()
    return again in ("s", "sim")


if __name__ == "__main__":
    while True:
        result = run_game()
        if not play_again():
            print("\n  Até logo! 🐾\n")
            break
        print("\n" + "─" * 56 + "\n")
