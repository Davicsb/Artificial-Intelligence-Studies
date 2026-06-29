"""
core.py — Motor central do Sistema Especialista
================================================
Contém:
  - KnowledgeBase   : armazenamento e persistência de fatos/regras
  - InferenceEngine : encadeamento para frente, para trás e híbrido
  - ExplanationEngine: responde "Como?" e "Por quê?"
"""

from __future__ import annotations
import json
import copy
from dataclasses import dataclass, field
from typing import Any, Optional


# ─────────────────────────────────────────────
# Estruturas de dados
# ─────────────────────────────────────────────

@dataclass
class Rule:
    """Uma regra no formato  SE condições ENTÃO conclusão."""
    id: str                        # identificador único, ex. "R01"
    conditions: list[str]          # lista de fatos que precisam ser verdadeiros
    conclusion: str                # fato inferido se todas as condições forem verdadeiras
    description: str = ""         # rótulo legível para exibição
    certainty: float = 1.0        # fator de certeza [0..1]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "conditions": self.conditions,
            "conclusion": self.conclusion,
            "description": self.description,
            "certainty": self.certainty,
        }

    @staticmethod
    def from_dict(d: dict) -> "Rule":
        return Rule(
            id=d["id"],
            conditions=d["conditions"],
            conclusion=d["conclusion"],
            description=d.get("description", ""),
            certainty=d.get("certainty", 1.0),
        )


@dataclass
class KnowledgeBase:
    """
    Armazena:
      - initial_facts  : fatos fornecidos pelo usuário antes da consulta
      - inferred_facts : fatos derivados pelo motor de inferência (com fator de certeza)
      - hypotheses     : hipóteses/diagnósticos disponíveis
      - rules          : lista de Rule
    """
    initial_facts: dict[str, Any] = field(default_factory=dict)
    inferred_facts: dict[str, float] = field(default_factory=dict)   # fato -> certeza
    hypotheses: list[str] = field(default_factory=list)
    rules: list[Rule] = field(default_factory=list)

    # ── persistência ──────────────────────────

    def save(self, path: str) -> None:
        data = {
            "initial_facts": self.initial_facts,
            "hypotheses": self.hypotheses,
            "rules": [r.to_dict() for r in self.rules],
        }
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)

    def load(self, path: str) -> None:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        self.initial_facts = data.get("initial_facts", {})
        self.hypotheses = data.get("hypotheses", [])
        self.rules = [Rule.from_dict(r) for r in data.get("rules", [])]
        self.inferred_facts = {}

    # ── acesso a fatos ─────────────────────────

    def all_facts(self) -> dict[str, Any]:
        """Retorna união de fatos iniciais e inferidos."""
        merged = dict(self.initial_facts)
        merged.update({f: v for f, v in self.inferred_facts.items()})
        return merged

    def is_known(self, fact: str) -> bool:
        return fact in self.initial_facts or fact in self.inferred_facts

    def fact_value(self, fact: str) -> Any:
        if fact in self.inferred_facts:
            return self.inferred_facts[fact]
        return self.initial_facts.get(fact)

    def add_fact(self, fact: str, value: Any = True) -> None:
        self.initial_facts[fact] = value

    def retract_fact(self, fact: str) -> bool:
        removed = False
        if fact in self.initial_facts:
            del self.initial_facts[fact]
            removed = True
        if fact in self.inferred_facts:
            del self.inferred_facts[fact]
            removed = True
        return removed

    def add_inferred(self, fact: str, certainty: float = 1.0) -> None:
        self.inferred_facts[fact] = certainty

    def reset_session(self) -> None:
        """Limpa apenas os fatos inferidos (mantém a base de regras)."""
        self.inferred_facts = {}

    # ── acesso a regras ────────────────────────

    def add_rule(self, rule: Rule) -> None:
        # substitui se id já existir
        self.rules = [r for r in self.rules if r.id != rule.id]
        self.rules.append(rule)

    def remove_rule(self, rule_id: str) -> bool:
        before = len(self.rules)
        self.rules = [r for r in self.rules if r.id != rule_id]
        return len(self.rules) < before

    def get_rule(self, rule_id: str) -> Optional[Rule]:
        for r in self.rules:
            if r.id == rule_id:
                return r
        return None

    def rules_concluding(self, fact: str) -> list[Rule]:
        return [r for r in self.rules if r.conclusion == fact]

    def rules_with_condition(self, fact: str) -> list[Rule]:
        return [r for r in self.rules if fact in r.conditions]


# ─────────────────────────────────────────────
# Motor de Inferência
# ─────────────────────────────────────────────

class InferenceEngine:
    """
    Implementa três estratégias:
      1. forward_chain  — encadeamento para frente (data-driven)
      2. backward_chain — encadeamento para trás  (goal-driven)
      3. hybrid_chain   — híbrido (BC seleciona hipóteses; FC expande fatos)

    O parâmetro `ask_user` é uma função callable(fact) -> bool|None
    que solicita informações ao usuário quando o fato não está na base.
    """

    def __init__(self, kb: KnowledgeBase, ask_user=None):
        self.kb = kb
        self.ask_user = ask_user            # callable(fact) -> bool | None
        self.trace: list[dict] = []         # trilha de raciocínio para explicação

    def _reset_trace(self):
        self.trace = []

    def _log(self, event: str, rule: Optional[Rule] = None, fact: str = ""):
        self.trace.append({"event": event, "rule": rule, "fact": fact})

    # ── helpers ───────────────────────────────

    def _check_fact(self, fact: str, asked: set) -> bool:
        """
        Retorna True se o fato é conhecido.
        Se não for, e ask_user estiver definido, pergunta ao usuário.
        """
        if self.kb.is_known(fact):
            return True
        if self.ask_user and fact not in asked:
            asked.add(fact)
            answer = self.ask_user(fact)
            if answer is not None:
                if answer:
                    self.kb.add_fact(fact, True)
                    self._log("user_confirmed", fact=fact)
                    return True
                else:
                    self.kb.add_fact(fact, False)
                    self._log("user_denied", fact=fact)
        return self.kb.initial_facts.get(fact, False) is True

    # ──────────────────────────────────────────
    # 1. ENCADEAMENTO PARA FRENTE
    # ──────────────────────────────────────────

    def forward_chain(self) -> list[str]:
        """
        Aplica regras repetidamente enquanto novos fatos forem derivados.
        Retorna lista de conclusões inferidas.
        Pergunta ao usuário apenas fatos que aparecem como condição de alguma regra.
        """
        self._reset_trace()
        self.kb.reset_session()
        asked: set[str] = set()
        new_inferred = True

        while new_inferred:
            new_inferred = False
            for rule in self.kb.rules:
                if self.kb.is_known(rule.conclusion):
                    continue  # já inferido
                # verifica cada condição
                all_met = True
                for cond in rule.conditions:
                    if not self._check_fact(cond, asked):
                        all_met = False
                        break
                if all_met:
                    cert = min(
                        [self.kb.fact_value(c) if isinstance(self.kb.fact_value(c), float) else 1.0
                         for c in rule.conditions],
                        default=1.0
                    ) * rule.certainty
                    self.kb.add_inferred(rule.conclusion, cert)
                    self._log("forward_fired", rule=rule, fact=rule.conclusion)
                    new_inferred = True

        return list(self.kb.inferred_facts.keys())

    # ──────────────────────────────────────────
    # 2. ENCADEAMENTO PARA TRÁS
    # ──────────────────────────────────────────

    def backward_chain(self, goal: str, visited: Optional[set] = None) -> bool:
        """
        Tenta provar `goal` recursivamente usando as regras.
        Pergunta ao usuário quando não há regra que prove o fato.
        Retorna True se o objetivo foi provado.
        """
        if visited is None:
            visited = set()
            self._reset_trace()

        if self.kb.is_known(goal):
            val = self.kb.fact_value(goal)
            return bool(val) if val is not None else False

        if goal in visited:
            return False
        visited.add(goal)

        rules = self.kb.rules_concluding(goal)
        for rule in rules:
            self._log("backward_try", rule=rule, fact=goal)
            all_conditions_met = True
            cert = rule.certainty
            for cond in rule.conditions:
                if not self.backward_chain(cond, visited):
                    all_conditions_met = False
                    break
                cv = self.kb.fact_value(cond)
                if isinstance(cv, float):
                    cert = min(cert, cv)
            if all_conditions_met:
                self.kb.add_inferred(goal, cert)
                self._log("backward_fired", rule=rule, fact=goal)
                return True

        # sem regra → perguntar ao usuário
        if self.ask_user:
            asked_set: set = set()
            result = self._check_fact(goal, asked_set)
            return result

        return False

    # ──────────────────────────────────────────
    # 3. ESTRATÉGIA HÍBRIDA
    # ──────────────────────────────────────────

    def hybrid_chain(self) -> list[str]:
        """
        1. Executa FC para expandir fatos conhecidos.
        2. Para cada hipótese registrada na KB, usa BC para tentar prová-la.
        3. Retorna todas as hipóteses confirmadas.
        """
        self._reset_trace()
        self.kb.reset_session()

        # Fase 1 — Forward
        asked_fc: set[str] = set()
        new_inferred = True
        while new_inferred:
            new_inferred = False
            for rule in self.kb.rules:
                if self.kb.is_known(rule.conclusion):
                    continue
                all_met = all(
                    self._check_fact(c, asked_fc) for c in rule.conditions
                )
                if all_met:
                    cert = rule.certainty
                    self.kb.add_inferred(rule.conclusion, cert)
                    self._log("hybrid_forward", rule=rule, fact=rule.conclusion)
                    new_inferred = True

        # Fase 2 — Backward para cada hipótese
        confirmed: list[str] = []
        for hyp in self.kb.hypotheses:
            if self.backward_chain(hyp, visited=set()):
                confirmed.append(hyp)
                self._log("hybrid_confirmed", fact=hyp)

        return confirmed


# ─────────────────────────────────────────────
# Mecanismo de Explicação
# ─────────────────────────────────────────────

class ExplanationEngine:
    """
    Responde "Por quê?" e "Como?" baseado na KB e na trilha de raciocínio.
    """

    def __init__(self, kb: KnowledgeBase, engine: InferenceEngine):
        self.kb = kb
        self.engine = engine

    # ── Por quê está perguntando sobre `fact`? ─

    def why(self, fact: str) -> str:
        """
        Explica por que o motor está interessado em `fact`:
        mostra quais regras usam esse fato como condição e o que concluiriam.
        """
        rules = self.kb.rules_with_condition(fact)
        if not rules:
            return (
                f"Estou perguntando sobre '{fact}' porque é um fato primitivo "
                f"necessário para iniciar o raciocínio, mas não encontrei regras "
                f"que o utilizem como condição no momento."
            )
        lines = [f"Estou perguntando sobre '{fact}' porque ele é condição de:"]
        for r in rules:
            other_conds = [c for c in r.conditions if c != fact]
            conds_str = ", ".join(other_conds) if other_conds else "(nenhuma outra)"
            lines.append(
                f"  [{r.id}] {r.description or r.id}: "
                f"SE {fact} (e também: {conds_str}) "
                f"ENTÃO '{r.conclusion}'"
            )
        return "\n".join(lines)

    # ── Como chegou à conclusão `fact`? ────────

    def how(self, fact: str, depth: int = 0, visited: Optional[set] = None) -> str:
        """
        Explica recursivamente como `fact` foi provado,
        listando as regras ativadas e as sub-provas das condições.
        """
        if visited is None:
            visited = set()
        indent = "  " * depth

        if fact in visited:
            return f"{indent}(já explicado: '{fact}')"
        visited.add(fact)

        # Procura regra que inferiu esse fato na trilha
        fired = [
            e["rule"] for e in self.engine.trace
            if e["rule"] is not None
            and e["rule"].conclusion == fact
            and e["event"] in ("forward_fired", "backward_fired", "hybrid_forward", "hybrid_confirmed")
        ]

        if not fired:
            # Fato fornecido diretamente pelo usuário
            val = self.kb.fact_value(fact)
            if val is not None:
                return f"{indent}'{fact}' foi informado diretamente pelo usuário (valor: {val})."
            return f"{indent}'{fact}' não está na base de conhecimento."

        rule = fired[0]
        lines = [
            f"{indent}'{fact}' foi inferido pela regra [{rule.id}]: {rule.description or rule.id}",
            f"{indent}  SE {' E '.join(rule.conditions)} ENTÃO {rule.conclusion}",
            f"{indent}  Certeza: {rule.certainty:.0%}",
            f"{indent}  Prova das condições:",
        ]
        for cond in rule.conditions:
            lines.append(self.how(cond, depth + 2, visited))

        return "\n".join(lines)

    def how_summary(self, fact: str) -> str:
        header = f"\n=== Como '{fact}' foi concluído? ===\n"
        return header + self.how(fact)

    def why_summary(self, fact: str) -> str:
        header = f"\n=== Por que você está perguntando sobre '{fact}'? ===\n"
        return header + self.why(fact)


# ─────────────────────────────────────────────
# Editor da Base de Conhecimento (API)
# ─────────────────────────────────────────────

class KnowledgeBaseEditor:
    """
    API programática para editar a KB.
    A CLI (shell.py) chama esses métodos.
    """

    def __init__(self, kb: KnowledgeBase):
        self.kb = kb

    def add_fact(self, fact: str, value: Any = True) -> str:
        self.kb.add_fact(fact, value)
        return f"Fato '{fact}' = {value} adicionado."

    def remove_fact(self, fact: str) -> str:
        if self.kb.retract_fact(fact):
            return f"Fato '{fact}' removido."
        return f"Fato '{fact}' não encontrado."

    def add_rule(self, rule_id: str, conditions: list[str],
                 conclusion: str, description: str = "",
                 certainty: float = 1.0) -> str:
        rule = Rule(rule_id, conditions, conclusion, description, certainty)
        self.kb.add_rule(rule)
        return f"Regra '{rule_id}' adicionada/atualizada."

    def remove_rule(self, rule_id: str) -> str:
        if self.kb.remove_rule(rule_id):
            return f"Regra '{rule_id}' removida."
        return f"Regra '{rule_id}' não encontrada."

    def add_hypothesis(self, hyp: str) -> str:
        if hyp not in self.kb.hypotheses:
            self.kb.hypotheses.append(hyp)
        return f"Hipótese '{hyp}' adicionada."

    def save(self, path: str) -> str:
        self.kb.save(path)
        return f"Base salva em '{path}'."

    def load(self, path: str) -> str:
        self.kb.load(path)
        return f"Base carregada de '{path}'."
