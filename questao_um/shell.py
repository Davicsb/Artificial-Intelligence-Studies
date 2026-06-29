"""
shell.py — Interface de Linha de Comando (CLI) do Sistema Especialista
======================================================================
Execute:
    python shell.py

Para carregar a base de demonstração automaticamente:
    python shell.py --demo

Comandos disponíveis na shell:
    help                    — lista todos os comandos
    load <arquivo>          — carrega base de conhecimento de um JSON
    save <arquivo>          — salva base de conhecimento em JSON
    add_fact <fato> [valor] — adiciona fato (valor padrão = true)
    del_fact <fato>         — remove fato
    add_rule                — assistente interativo para criar regra
    del_rule <id>           — remove regra pelo ID
    list_rules              — lista todas as regras
    list_facts              — lista todos os fatos
    list_hyps               — lista hipóteses registradas
    add_hyp <hipótese>      — registra hipótese de diagnóstico
    consult forward         — executa encadeamento para frente
    consult backward <goal> — executa encadeamento para trás buscando <goal>
    consult hybrid          — executa estratégia híbrida
    why <fato>              — explica por que o motor perguntou sobre <fato>
    how <fato>              — explica como <fato> foi inferido
    reset                   — limpa fatos inferidos da sessão
    clear_facts             — remove todos os fatos iniciais
    exit / quit             — encerra a shell
"""

from __future__ import annotations
import sys
import os
import textwrap
from core import KnowledgeBase, InferenceEngine, ExplanationEngine, KnowledgeBaseEditor

BANNER = r"""
╔══════════════════════════════════════════════════════════════╗
║       SISTEMA ESPECIALISTA — Motor de Raciocínio Simbólico  ║
║       Encadeamento Frente | Trás | Híbrido                  ║
╚══════════════════════════════════════════════════════════════╝
Digite 'help' para ver os comandos disponíveis.
"""

HELP_TEXT = """
━━━━━━━━━━━━━━━━━━━ COMANDOS ━━━━━━━━━━━━━━━━━━━
Base de Conhecimento
  load <arquivo>        Carrega KB de um arquivo JSON
  save <arquivo>        Salva KB em um arquivo JSON
  list_rules            Lista todas as regras
  list_facts            Lista todos os fatos (iniciais + inferidos)
  list_hyps             Lista hipóteses de diagnóstico

Editor de Fatos
  add_fact <fato> [val] Adiciona fato (val padrão: true)
  del_fact <fato>       Remove fato

Editor de Regras
  add_rule              Assistente interativo para criar regra
  del_rule <id>         Remove regra pelo ID
  add_hyp <hipótese>    Registra hipótese de diagnóstico

Consulta / Inferência
  consult forward       Encadeamento para frente (data-driven)
  consult backward <g>  Encadeamento para trás (goal-driven)
  consult hybrid        Estratégia híbrida (FC + BC por hipótese)

Explicação
  why <fato>            Por que o motor perguntou sobre <fato>?
  how <fato>            Como <fato> foi inferido?

Sessão
  reset                 Limpa fatos inferidos da sessão atual
  clear_facts           Remove todos os fatos iniciais
  exit / quit           Encerra a shell
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


def ask_user_factory(explanation: ExplanationEngine, last_question_holder: list) -> callable:
    """
    Retorna uma função de callback que pergunta ao usuário sobre um fato.
    Suporta resposta 'por que' para ativar o mecanismo de explicação.
    """
    def ask(fact: str) -> bool | None:
        last_question_holder.clear()
        last_question_holder.append(fact)
        while True:
            resp = input(
                f"\n  ❓ O seguinte sintoma/fato é verdadeiro? '{fact}'\n"
                f"     [s/n/por quê]: "
            ).strip().lower()
            if resp in ("s", "sim", "y", "yes", "1", "true"):
                return True
            elif resp in ("n", "não", "nao", "no", "0", "false"):
                return False
            elif resp in ("por que", "por quê", "why", "pq", "?"):
                print(explanation.why_summary(fact))
            else:
                print("  Responda 's' (sim), 'n' (não) ou 'por quê'.")
    return ask


def run_shell(kb: KnowledgeBase):
    """Loop principal da CLI."""
    last_question: list[str] = []       # guarda último fato perguntado
    engine = InferenceEngine(kb, ask_user=None)
    explanation = ExplanationEngine(kb, engine)
    editor = KnowledgeBaseEditor(kb)

    # Reconecta engine com ask_user que referencia explanation
    engine.ask_user = ask_user_factory(explanation, last_question)

    print(BANNER)

    while True:
        try:
            raw = input("\n[SE] > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nEncerrando. Até logo!")
            break

        if not raw:
            continue

        parts = raw.split(maxsplit=2)
        cmd = parts[0].lower()

        # ── help ──────────────────────────────
        if cmd == "help":
            print(HELP_TEXT)

        # ── exit / quit ───────────────────────
        elif cmd in ("exit", "quit", "sair"):
            print("Encerrando. Até logo!")
            break

        # ── load ──────────────────────────────
        elif cmd == "load":
            if len(parts) < 2:
                print("Uso: load <arquivo>")
                continue
            try:
                msg = editor.load(parts[1])
                print(f"✔ {msg}  ({len(kb.rules)} regras, {len(kb.hypotheses)} hipóteses)")
            except FileNotFoundError:
                print(f"✘ Arquivo '{parts[1]}' não encontrado.")

        # ── save ──────────────────────────────
        elif cmd == "save":
            if len(parts) < 2:
                print("Uso: save <arquivo>")
                continue
            print(editor.save(parts[1]))

        # ── list_rules ────────────────────────
        elif cmd == "list_rules":
            if not kb.rules:
                print("Nenhuma regra cadastrada.")
            else:
                print(f"\n{'ID':<6} {'Certeza':<8} {'Condições':<40} {'Conclusão'}")
                print("─" * 80)
                for r in kb.rules:
                    conds = " E ".join(r.conditions)
                    print(f"{r.id:<6} {r.certainty:<8.0%} {conds[:38]:<40} {r.conclusion}")
                    if r.description:
                        print(f"       {r.description}")

        # ── list_facts ────────────────────────
        elif cmd == "list_facts":
            all_f = kb.all_facts()
            if not all_f:
                print("Nenhum fato na base.")
            else:
                print("\n=== Fatos Iniciais ===")
                for f, v in kb.initial_facts.items():
                    print(f"  {f} = {v}")
                if kb.inferred_facts:
                    print("\n=== Fatos Inferidos ===")
                    for f, v in kb.inferred_facts.items():
                        print(f"  {f} (certeza: {v:.0%})")

        # ── list_hyps ─────────────────────────
        elif cmd == "list_hyps":
            if not kb.hypotheses:
                print("Nenhuma hipótese registrada.")
            else:
                print("\n=== Hipóteses/Diagnósticos ===")
                for h in kb.hypotheses:
                    status = "✔ confirmada" if kb.is_known(h) else "? pendente"
                    print(f"  {h}  [{status}]")

        # ── add_fact ──────────────────────────
        elif cmd == "add_fact":
            if len(parts) < 2:
                print("Uso: add_fact <fato> [valor]")
                continue
            fact = parts[1]
            val: Any = True
            if len(parts) >= 3:
                raw_val = parts[2].lower()
                if raw_val in ("false", "n", "não", "nao", "0"):
                    val = False
                elif raw_val in ("true", "s", "sim", "1"):
                    val = True
                else:
                    try:
                        val = float(raw_val)
                    except ValueError:
                        val = raw_val
            print(editor.add_fact(fact, val))

        # ── del_fact ──────────────────────────
        elif cmd == "del_fact":
            if len(parts) < 2:
                print("Uso: del_fact <fato>")
                continue
            print(editor.remove_fact(parts[1]))

        # ── add_rule ──────────────────────────
        elif cmd == "add_rule":
            print("\n── Criação de Regra ──")
            rule_id = input("  ID da regra (ex: R99): ").strip()
            if not rule_id:
                print("ID não pode ser vazio.")
                continue
            conclusion = input("  Conclusão (ENTÃO ...): ").strip()
            conds_raw = input("  Condições (SE ...) separadas por ';': ").strip()
            conditions = [c.strip() for c in conds_raw.split(";") if c.strip()]
            description = input("  Descrição (opcional): ").strip()
            cert_raw = input("  Fator de certeza [0..1] (padrão 1.0): ").strip()
            try:
                certainty = float(cert_raw) if cert_raw else 1.0
            except ValueError:
                certainty = 1.0
            print(editor.add_rule(rule_id, conditions, conclusion, description, certainty))

        # ── del_rule ──────────────────────────
        elif cmd == "del_rule":
            if len(parts) < 2:
                print("Uso: del_rule <id>")
                continue
            print(editor.remove_rule(parts[1]))

        # ── add_hyp ───────────────────────────
        elif cmd == "add_hyp":
            if len(parts) < 2:
                print("Uso: add_hyp <hipótese>")
                continue
            hyp = " ".join(parts[1:])
            print(editor.add_hypothesis(hyp))

        # ── reset ─────────────────────────────
        elif cmd == "reset":
            kb.reset_session()
            kb.initial_facts = {}
            print("✔ Sessão reiniciada (fatos iniciais e inferidos limpos).")

        # ── clear_facts ───────────────────────
        elif cmd == "clear_facts":
            kb.initial_facts = {}
            print("✔ Fatos iniciais removidos.")

        # ── consult ───────────────────────────
        elif cmd == "consult":
            if len(parts) < 2:
                print("Uso: consult [forward | backward <goal> | hybrid]")
                continue
            strategy = parts[1].lower()

            if strategy == "forward":
                print("\n🔍 Iniciando Encadeamento para Frente…")
                kb.reset_session()
                results = engine.forward_chain()
                _print_results(results, kb)

            elif strategy == "backward":
                if len(parts) < 3:
                    print("Uso: consult backward <objetivo>")
                    continue
                goal = parts[2]
                print(f"\n🔍 Iniciando Encadeamento para Trás — objetivo: '{goal}'…")
                kb.reset_session()
                proved = engine.backward_chain(goal)
                if proved:
                    cert = kb.fact_value(goal)
                    cert_str = f" (certeza: {cert:.0%})" if isinstance(cert, float) else ""
                    print(f"\n✔ DIAGNÓSTICO CONFIRMADO: '{goal}'{cert_str}")
                else:
                    print(f"\n✘ Não foi possível confirmar '{goal}' com as informações disponíveis.")

            elif strategy == "hybrid":
                print("\n🔍 Iniciando Estratégia Híbrida (FC + BC)…")
                kb.reset_session()
                confirmed = engine.hybrid_chain()
                if confirmed:
                    print("\n✔ HIPÓTESES CONFIRMADAS:")
                    for h in confirmed:
                        cert = kb.fact_value(h)
                        cert_str = f"  (certeza: {cert:.0%})" if isinstance(cert, float) else ""
                        print(f"   • {h}{cert_str}")
                else:
                    print("\n✘ Nenhuma hipótese confirmada com as informações atuais.")
                if kb.inferred_facts:
                    others = [f for f in kb.inferred_facts if f not in confirmed]
                    if others:
                        print("\n  Fatos intermediários inferidos:")
                        for f in others:
                            print(f"   – {f}")
            else:
                print("Estratégia inválida. Use: forward | backward <goal> | hybrid")

        # ── why ───────────────────────────────
        elif cmd == "why":
            fact = " ".join(parts[1:]) if len(parts) > 1 else (last_question[0] if last_question else "")
            if not fact:
                print("Uso: why <fato>")
                continue
            print(explanation.why_summary(fact))

        # ── how ───────────────────────────────
        elif cmd == "how":
            if len(parts) < 2:
                print("Uso: how <fato>")
                continue
            fact = " ".join(parts[1:])
            print(explanation.how_summary(fact))

        else:
            print(f"Comando desconhecido: '{cmd}'. Digite 'help' para ajuda.")


def _print_results(results: list[str], kb: KnowledgeBase):
    if not results:
        print("\n✘ Nenhum fato novo inferido.")
        return
    hyps_found = [r for r in results if r in kb.hypotheses]
    others = [r for r in results if r not in kb.hypotheses]
    if hyps_found:
        print("\n✔ DIAGNÓSTICOS / HIPÓTESES CONFIRMADOS:")
        for h in hyps_found:
            cert = kb.fact_value(h)
            cert_str = f"  (certeza: {cert:.0%})" if isinstance(cert, float) else ""
            print(f"   • {h}{cert_str}")
    if others:
        print("\n  Fatos intermediários inferidos:")
        for f in others:
            cert = kb.fact_value(f)
            cert_str = f" ({cert:.0%})" if isinstance(cert, float) else ""
            print(f"   – {f}{cert_str}")


# ─────────────────────────────────────────────
# Ponto de entrada
# ─────────────────────────────────────────────

if __name__ == "__main__":
    kb = KnowledgeBase()

    if "--demo" in sys.argv:
        # Carrega a base de demonstração de veículos
        demo_path = os.path.join(os.path.dirname(__file__), "demo_vehicles.json")
        if os.path.exists(demo_path):
            kb.load(demo_path)
            print(f"✔ Base de demonstração carregada: {len(kb.rules)} regras, "
                  f"{len(kb.hypotheses)} hipóteses.")
        else:
            print(f"⚠ Arquivo '{demo_path}' não encontrado. Gerando base demo…")
            # importa e popula a demo
            from demo import build_demo_kb
            build_demo_kb(kb)
            kb.save(demo_path)
            print(f"✔ Base demo salva em '{demo_path}'.")

    run_shell(kb)
