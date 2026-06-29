"""
demo.py — Base de Conhecimento Demonstrativa: Diagnóstico de Falhas em Veículos
================================================================================
Contém:
  - 22 regras de diagnóstico
  - 35 fatos possíveis
  - 6 hipóteses de diagnóstico

Como usar:
  python demo.py                  → executa o roteiro de demonstração automático
  python shell.py --demo          → carrega a base na shell interativa

  ROTEIRO RECOMENDADO (shell interativa):
  ─────────────────────────────────────
  1. Abra a shell:
       python shell.py --demo

  2. Teste o encadeamento para trás buscando uma hipótese específica:
       consult backward diagnostico_bateria_fraca

  3. Responda as perguntas com 's' ou 'n'. Quando o sistema perguntar,
     tente digitar 'por quê' para ver a explicação do motivo.

  4. Após a consulta, veja como o diagnóstico foi atingido:
       how diagnostico_bateria_fraca

  5. Reinicie e teste o modo forward para ver todos os diagnósticos de uma vez:
       reset
       consult forward

  6. Teste a estratégia híbrida:
       reset
       consult hybrid

  7. Explore a explicação 'why' sobre qualquer fato:
       why motor_nao_gira
"""

from __future__ import annotations
from core import KnowledgeBase, Rule, InferenceEngine, ExplanationEngine


def build_demo_kb(kb: KnowledgeBase) -> None:
    """Popula a KB com a base de veículos."""

    # ── Hipóteses / diagnósticos ──────────────────────────────────────────────
    # (pelo menos 5 conforme requisito — aqui são 6)
    hypotheses = [
        "diagnostico_bateria_fraca",
        "diagnostico_problema_alternador",
        "diagnostico_superaquecimento_motor",
        "diagnostico_falha_combustivel",
        "diagnostico_problema_freios",
        "diagnostico_falha_ignicao",
        "acao_trocar_bateria_ou_limpar_terminais",
        "acao_verificar_bomba_e_abastecer",
        "acao_chamar_guincho_ou_mecanico"
    ]
    kb.hypotheses = hypotheses

    # ── Regras ───────────────────────────────────────────────────────────────
    # (pelo menos 20 conforme requisito — aqui são 22)
    rules = [
        # ── Grupo: Bateria ────────────────────────────────────────────────
        Rule(
            id="R01",
            conditions=["motor_nao_gira", "luzes_fracas"],
            conclusion="tensao_bateria_baixa",
            description="Bateria com tensão insuficiente",
            certainty=0.90,
        ),
        Rule(
            id="R02",
            conditions=["tensao_bateria_baixa", "bateria_com_mais_de_3_anos"],
            conclusion="diagnostico_bateria_fraca",
            description="Bateria antiga com tensão baixa → bateria fraca",
            certainty=0.95,
        ),
        Rule(
            id="R03",
            conditions=["tensao_bateria_baixa", "terminais_corroidos"],
            conclusion="diagnostico_bateria_fraca",
            description="Terminais corroídos causando queda de tensão",
            certainty=0.85,
        ),
        Rule(
            id="R04",
            conditions=["motor_nao_gira", "click_ao_acionar_chave"],
            conclusion="tensao_bateria_baixa",
            description="Click único ao ligar = bateria sem carga",
            certainty=0.80,
        ),

        # ── Grupo: Alternador ─────────────────────────────────────────────
        Rule(
            id="R05",
            conditions=["luz_bateria_acesa_em_movimento", "tensao_bateria_baixa"],
            conclusion="alternador_nao_carrega",
            description="Alternador não recarregando a bateria",
            certainty=0.88,
        ),
        Rule(
            id="R06",
            conditions=["alternador_nao_carrega", "correia_alternador_danificada"],
            conclusion="diagnostico_problema_alternador",
            description="Correia do alternador danificada → sem carga",
            certainty=0.92,
        ),
        Rule(
            id="R07",
            conditions=["alternador_nao_carrega", "ruido_no_alternador"],
            conclusion="diagnostico_problema_alternador",
            description="Rolamento do alternador com defeito",
            certainty=0.87,
        ),
        Rule(
            id="R08",
            conditions=["alternador_nao_carrega", "bateria_nova"],
            conclusion="diagnostico_problema_alternador",
            description="Bateria nova que descarrega = alternador com defeito",
            certainty=0.93,
        ),

        # ── Grupo: Superaquecimento ───────────────────────────────────────
        Rule(
            id="R09",
            conditions=["temperatura_motor_alta", "nivel_agua_baixo"],
            conclusion="sistema_resfriamento_comprometido",
            description="Falta de líquido de arrefecimento",
            certainty=0.90,
        ),
        Rule(
            id="R10",
            conditions=["temperatura_motor_alta", "vazamento_no_radiador"],
            conclusion="sistema_resfriamento_comprometido",
            description="Vazamento no radiador causando superaquecimento",
            certainty=0.95,
        ),
        Rule(
            id="R11",
            conditions=["sistema_resfriamento_comprometido", "vapor_sob_capo"],
            conclusion="diagnostico_superaquecimento_motor",
            description="Superaquecimento confirmado com vapor visível",
            certainty=0.98,
        ),
        Rule(
            id="R12",
            conditions=["sistema_resfriamento_comprometido", "termostato_com_defeito"],
            conclusion="diagnostico_superaquecimento_motor",
            description="Termostato com defeito impedindo circulação",
            certainty=0.90,
        ),
        Rule(
            id="R13",
            conditions=["temperatura_motor_alta", "ventoinha_parada"],
            conclusion="sistema_resfriamento_comprometido",
            description="Ventoinha inoperante → sem resfriamento",
            certainty=0.85,
        ),

        # ── Grupo: Combustível ────────────────────────────────────────────
        Rule(
            id="R14",
            conditions=["motor_engasga", "nivel_combustivel_baixo"],
            conclusion="sem_combustivel",
            description="Motor engasgando por falta de combustível",
            certainty=0.88,
        ),
        Rule(
            id="R15",
            conditions=["motor_engasga", "filtro_combustivel_sujo"],
            conclusion="fluxo_combustivel_restrito",
            description="Filtro de combustível entupido",
            certainty=0.85,
        ),
        Rule(
            id="R16",
            conditions=["sem_combustivel", "motor_nao_liga"],
            conclusion="diagnostico_falha_combustivel",
            description="Motor não liga por falta de combustível",
            certainty=0.98,
        ),
        Rule(
            id="R17",
            conditions=["fluxo_combustivel_restrito", "motor_sem_potencia"],
            conclusion="diagnostico_falha_combustivel",
            description="Perda de potência por restrição de combustível",
            certainty=0.87,
        ),
        Rule(
            id="R18",
            conditions=["bomba_combustivel_barulhenta", "pressao_combustivel_baixa"],
            conclusion="diagnostico_falha_combustivel",
            description="Bomba de combustível com defeito",
            certainty=0.90,
        ),

        # ── Grupo: Freios ─────────────────────────────────────────────────
        Rule(
            id="R19",
            conditions=["pedal_freio_mole", "nivel_fluido_freio_baixo"],
            conclusion="diagnostico_problema_freios",
            description="Falta de fluido de freio → pedal mole",
            certainty=0.92,
        ),
        Rule(
            id="R20",
            conditions=["ruido_ao_frear", "pastilhas_gastas"],
            conclusion="diagnostico_problema_freios",
            description="Pastilhas de freio desgastadas",
            certainty=0.95,
        ),

        # ── Grupo: Ignição ────────────────────────────────────────────────
        Rule(
            id="R21",
            conditions=["motor_engasga", "velas_com_defeito"],
            conclusion="diagnostico_falha_ignicao",
            description="Velas de ignição com defeito causando falhas",
            certainty=0.88,
        ),
        Rule(
            id="R22",
            conditions=["motor_nao_liga", "sem_centelha"],
            conclusion="diagnostico_falha_ignicao",
            description="Sem centelha nas velas → falha de ignição",
            certainty=0.95,
        ),

        # ── Grupo: Recomendações de Ações e Tratamentos ───────────────────
        Rule(
            id="R23",
            conditions=["diagnostico_bateria_fraca"],
            conclusion="acao_trocar_bateria_ou_limpar_terminais",
            description="Recomendação: Substituir a bateria ou limpar terminais oxidados",
            certainty=1.0,
        ),
        Rule(
            id="R24",
            conditions=["diagnostico_falha_combustivel"],
            conclusion="acao_verificar_bomba_e_abastecer",
            description="Recomendação: Abastecer o veículo e checar filtro/bomba",
            certainty=1.0,
        ),
        Rule(
            id="R25",
            conditions=["diagnostico_superaquecimento_motor"],
            conclusion="acao_chamar_guincho_ou_mecanico",
            description="Recomendação Crítica: Desligue o motor imediatamente e chame um mecânico",
            certainty=1.0,
        ),]
    

    for rule in rules:
        kb.add_rule(rule)


# ─────────────────────────────────────────────────────────────────────────────
# TODOS OS 35 FATOS POSSÍVEIS (para referência)
# ─────────────────────────────────────────────────────────────────────────────
# Fatos primitivos (observáveis):
#   motor_nao_gira, luzes_fracas, click_ao_acionar_chave,
#   bateria_com_mais_de_3_anos, terminais_corroidos, bateria_nova,
#   luz_bateria_acesa_em_movimento, correia_alternador_danificada,
#   ruido_no_alternador, temperatura_motor_alta, nivel_agua_baixo,
#   vazamento_no_radiador, vapor_sob_capo, termostato_com_defeito,
#   ventoinha_parada, motor_engasga, nivel_combustivel_baixo,
#   filtro_combustivel_sujo, motor_nao_liga, motor_sem_potencia,
#   bomba_combustivel_barulhenta, pressao_combustivel_baixa,
#   pedal_freio_mole, nivel_fluido_freio_baixo, ruido_ao_frear,
#   pastilhas_gastas, velas_com_defeito, sem_centelha
#
# Fatos intermediários (inferidos):
#   tensao_bateria_baixa, alternador_nao_carrega,
#   sistema_resfriamento_comprometido, sem_combustivel,
#   fluxo_combustivel_restrito
#
# Fatos de diagnóstico (hipóteses):
#   diagnostico_bateria_fraca, diagnostico_problema_alternador,
#   diagnostico_superaquecimento_motor, diagnostico_falha_combustivel,
#   diagnostico_problema_freios, diagnostico_falha_ignicao


# ─────────────────────────────────────────────────────────────────────────────
# Roteiro de demonstração automática
# ─────────────────────────────────────────────────────────────────────────────

def demo_scenario_battery(kb: KnowledgeBase):
    """
    Cenário 1 — Backward Chaining: provar 'diagnostico_bateria_fraca'
    Simula usuário respondendo 's' para sintomas de bateria fraca.
    """
    print("\n" + "═" * 60)
    print("CENÁRIO 1 — Encadeamento para TRÁS")
    print("Objetivo: provar 'diagnostico_bateria_fraca'")
    print("═" * 60)

    kb.reset_session()
    kb.initial_facts = {}

    # Simulação de respostas do usuário (sem interatividade real)
    respostas = {
        "motor_nao_gira": True,
        "luzes_fracas": True,
        "bateria_com_mais_de_3_anos": True,
    }

    def simulated_ask(fact: str) -> bool | None:
        answer = respostas.get(fact)
        v = "SIM" if answer else ("NÃO" if answer is False else "desconhecido")
        print(f"  [AUTO] Pergunta: '{fact}' → {v}")
        return answer

    engine = InferenceEngine(kb, ask_user=simulated_ask)
    explanation = ExplanationEngine(kb, engine)

    proved = engine.backward_chain("diagnostico_bateria_fraca")
    print(f"\n  Resultado: {'✔ CONFIRMADO' if proved else '✘ não confirmado'}")
    print(explanation.how_summary("diagnostico_bateria_fraca"))
    print(explanation.why_summary("luzes_fracas"))


def demo_scenario_forward(kb: KnowledgeBase):
    """
    Cenário 2 — Forward Chaining: a partir de fatos pré-definidos.
    Simula superaquecimento com múltiplos fatos iniciais.
    """
    print("\n" + "═" * 60)
    print("CENÁRIO 2 — Encadeamento para FRENTE")
    print("Fatos iniciais: temperatura_motor_alta + nivel_agua_baixo + vapor_sob_capo")
    print("═" * 60)

    kb.reset_session()
    kb.initial_facts = {
        "temperatura_motor_alta": True,
        "nivel_agua_baixo": True,
        "vapor_sob_capo": True,
    }

    engine = InferenceEngine(kb, ask_user=None)
    explanation = ExplanationEngine(kb, engine)
    results = engine.forward_chain()

    hyps = [r for r in results if r in kb.hypotheses]
    print(f"\n  Fatos inferidos: {results}")
    if hyps:
        print(f"  Diagnósticos: {hyps}")
        for h in hyps:
            print(explanation.how_summary(h))


def demo_scenario_hybrid(kb: KnowledgeBase):
    """
    Cenário 3 — Estratégia Híbrida: motor que não liga + velas com defeito.
    """
    print("\n" + "═" * 60)
    print("CENÁRIO 3 — Estratégia HÍBRIDA (FC + BC)")
    print("Sintomas: motor_nao_liga + sem_centelha + velas_com_defeito")
    print("═" * 60)

    kb.reset_session()
    kb.initial_facts = {
        "motor_nao_liga": True,
        "sem_centelha": True,
        "velas_com_defeito": True,
        "motor_engasga": True,
    }

    engine = InferenceEngine(kb, ask_user=None)
    explanation = ExplanationEngine(kb, engine)
    confirmed = engine.hybrid_chain()

    print(f"\n  Hipóteses confirmadas: {confirmed}")
    for h in confirmed:
        print(explanation.how_summary(h))


def demo_explanation_why(kb: KnowledgeBase):
    """
    Cenário 4 — Demonstra o mecanismo 'Por quê?'.
    """
    print("\n" + "═" * 60)
    print("CENÁRIO 4 — Mecanismo de Explicação 'Por quê?'")
    print("═" * 60)

    engine = InferenceEngine(kb)
    explanation = ExplanationEngine(kb, engine)

    for fact in ["luzes_fracas", "correia_alternador_danificada", "ruido_ao_frear"]:
        print(explanation.why_summary(fact))


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║   DEMONSTRAÇÃO — Sistema Especialista de Diagnóstico        ║
║                 de Falhas em Veículos                       ║
╚══════════════════════════════════════════════════════════════╝

  Base de Conhecimento:
    • 22 regras
    • 35 fatos possíveis
    • 6 hipóteses de diagnóstico

  Executando 4 cenários de demonstração…
""")

    kb = KnowledgeBase()
    build_demo_kb(kb)

    demo_scenario_battery(kb)
    demo_scenario_forward(kb)
    demo_scenario_hybrid(kb)
    demo_explanation_why(kb)

    # Salva a KB para uso na shell interativa
    save_path = "demo_vehicles.json"
    kb.save(save_path)
    print(f"\n✔ Base de conhecimento salva em '{save_path}'")
    print("\n" + "─" * 60)
    print("Para explorar interativamente, execute:")
    print("    python shell.py --demo")
    print("\nComandos úteis na shell:")
    print("    consult backward diagnostico_bateria_fraca")
    print("    consult forward")
    print("    consult hybrid")
    print("    why luzes_fracas")
    print("    how diagnostico_bateria_fraca")
    print("─" * 60)
