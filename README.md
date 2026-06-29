# Questão 1 - Ferramenta para Construção de Sistemas Especialistas

Este diretório contém a implementação de uma ferramenta genérica para a construção de sistemas baseados em conhecimento, voltada a tarefas de diagnóstico e recomendação de ações/tratamentos. A solução segue a arquitetura conceitual de um agente baseado em conhecimento, separando motor de inferência, base de regras e interface com o usuário.

## Estrutura de Arquivos da Pasta `questao_um`

A pasta contém os seguintes arquivos principais que compõem o sistema:

* **`core.py`**: É o motor central do Sistema Especialista[cite: 1]. Este arquivo implementa os principais componentes do agente:
  * Armazenamento e persistência de fatos e regras (`KnowledgeBase`)[cite: 1].
  * Motor de Raciocínio (`InferenceEngine`) com suporte a encadeamento para frente, para trás e híbrido[cite: 1].
  * Mecanismo de Explicação (`ExplanationEngine`) que responde às perguntas "Como?" e "Por quê?"[cite: 1].
  * API do Editor da Base de Conhecimento (`KnowledgeBaseEditor`) para manutenção dos elementos sem alterar código[cite: 1].

* **`shell.py`**: Interface de Linha de Comando (CLI) interativa do Sistema Especialista[cite: 4]. Permite que especialistas de domínio e usuários interajam com o sistema para carregar bases, adicionar/remover fatos e regras, realizar consultas interativas e solicitar explicações[cite: 4].

* **`demo.py`**: Script de demonstração contendo uma Base de Conhecimento para Diagnóstico de Falhas em Veículos[cite: 2]. Ele popula a base com regras, fatos e hipóteses, e executa um roteiro automático demonstrando os três cenários de encadeamento e as explicações do sistema[cite: 2].

* **`demo_vehicles.json`**: Arquivo de persistência contendo a base de conhecimento (fatos iniciais, hipóteses de diagnóstico/ações e regras no formato SE-ENTÃO) estruturada em formato JSON[cite: 3]. Pode ser carregado diretamente pela CLI[cite: 4].

* **`__pycache__/`**: Pasta gerada automaticamente pelo Python contendo os binários compilados dos scripts para otimização de execução.

## Como Executar?

O sistema foi desenhado para funcionar de duas maneiras: execução de cenários automáticos ou interface interativa.

### 1. Roteiro Automático de Demonstração
Para ver o sistema resolvendo problemas automaticamente (sem necessidade de interação), execute:
```bash
python demo.py

```

Isso rodará 4 cenários demonstrando o encadeamento para frente, para trás, híbrido e o mecanismo de explicação, além de gerar/atualizar o arquivo `demo_vehicles.json`.

### 2. Interface Interativa (Shell)

Para interagir com o sistema, fazer consultas manuais e testar o diagnóstico dinamicamente, abra a CLI carregando a base de demonstração:

```bash
python shell.py --demo

```

### Principais Comandos da Shell

Uma vez dentro do prompt `[SE] >`, você pode utilizar os seguintes comandos:

* `help`: Lista todos os comandos disponíveis.


* `consult hybrid`: Inicia o diagnóstico usando a estratégia híbrida, fazendo perguntas dinâmicas ao usuário.


* `consult backward <objetivo>`: Tenta provar uma hipótese ou recomendação específica.


* `how <fato>`: Explica a árvore de decisão de como o sistema chegou a uma conclusão.


* `why <fato>`: *(Use "por quê" durante as perguntas do consult)* Explica o motivo pelo qual o sistema está solicitando uma informação.


* `list_rules` / `list_facts`: Lista o estado atual da base de conhecimento.


* `add_rule`: Inicia um assistente interativo para criar novas regras no sistema.



```

```