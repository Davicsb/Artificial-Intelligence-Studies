# Estrutura de Arquivos da Pasta `questao_um`

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

* **`SISTEMA ESPECIALISTA PARA DIAGNÓSTICO E RECOMENDAÇÃO DE AÇÕES.pdf`**: PDF com o relátorio pedido para composição de nota.

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

---

# Estrutura de Arquivos da Pasta `questao_dois/akinator`

Um sistema baseado em conhecimento inspirado no famoso jogo *Akinator*, projetado para identificar um animal pensado pelo usuário através de uma sequência otimizada de perguntas booleanas.

## Arquitetura e Algoritmo Central

* **Domínio Amplo:** Base de dados populada com **25 entidades** únicas (animais) mapeadas sobre uma matriz de **21 atributos** discriminantes (ex: *é mamífero?*, *voa?*, *tem pescoço longo?*).
* **Busca no Espaço de Hipóteses:** O motor começa considerando todos os animais como candidatos válidos e vai podando a lista dinamicamente com base nas respostas.
* **Máxima Informação (Information Gain):** O sistema não faz perguntas aleatórias. A cada turno, calcula-se a **Entropia de Shannon** do conjunto atual de candidatos. O atributo que divide o espaço de busca o mais próximo possível de 50/50 (maior ganho de informação) é escolhido para a próxima pergunta.
* **Resistência à Incerteza:** O sistema aceita as respostas `Sim`, `Não` e `Não Sei` (`ns`). Respostas "Não Sei" ou valores neutros (definidos como `-1` na base) não eliminam hipóteses, garantindo estabilidade ao jogo mesmo diante da dúvida humana.
* **SISTEMA INTELIGENTE DE PERGUNTAS E RESPOSTAS (AKINATOR DE ANIMAIS).pdf**: PDF com o relátorio pedido para composição de nota.

## Como Jogar e Extrair Métricas (Questão 2.1)

1. **Modo Jogo Interativo (Interface Humana):**
Pense em um animal presente na base (ex: *Leão, Pinguim, Ornitorrinco, Baleia*) e tente desafiar o sistema executando:
```bash
cd questao_dois/akinator
python akinator.py

```

*O sistema exibirá qual é o palpite mais provável da Inteligência Artificial em tempo real antes de cada pergunta.*
2. **Modo Experimentos (Simulador Automatizado):**
O professor exigiu testes estatísticos de acerto e eficiência. Para rodar a bateria de simulações completa e extrair os dados prontos para o relatório técnico, execute:
```bash
python test_metrics.py

```


*Este script simula partidas para os 25 animais sob condições ideais e sob estresse (inserindo 20% de respostas "Não Sei"), gerando tabelas de performance, histogramas de distribuição de perguntas e taxas de acerto percentuais.*

---

## Requisitos Técnicos Atendidos

* Código escrito em conformidade com o **Python 3.10+**.
* Uso estrito de tipagem estática (*Type Hinting*) com suporte a referências futuras (`__future__.annotations`).
* Arquitetura puramente simbólica, sem dependência de bibliotecas externas de Machine Learning de terceiros (toda a lógica matemática de Entropia e Grafos foi implementada utilizando as bibliotecas nativas `math` e `json`).

---

# Estrutura de Arquivos da Pasta `questao_dois/ontologia`

Um sistema inteligente de recomendação de filmes construído sobre os pilares da **Web Semântica**, utilizando a linguagem OWL 2.0 e processamento lógico direto em Python. O sistema infere recomendações com base no perfil do usuário utilizando raciocínio semântico, sem a necessidade de condicionais tradicionais (`if/else`).

## Arquitetura e Recursos Implementados
* **Ontologia OWL 2.0:** Modelagem de domínio completa contendo mais de 10 classes (ex: `Filme`, `Diretor`, `Genero`) e 15 propriedades (Object e Data properties, como `temAtor` e `notaIMDB`).
* **Motor de Raciocínio (Reasoner):** Integração com o motor **HermiT** através da biblioteca `Owlready2`. O reasoner é responsável por garantir a consistência da base e realizar a classificação automática de indivíduos (ex: inferir que "Matrix" é um `FilmeFiccao` com base nas suas propriedades).
* **Regras Semânticas (SWRL):** A lógica de recomendação foi implementada puramente através de regras da Web Semântica. Exemplo: `Usuario(?u), Filme(?f), gostaDeAtor(?u, ?a), temAtor(?f, ?a) -> recomendadoPara(?u, ?f)`.
* **Justificativas Dinâmicas:** O sistema não apenas recomenda o filme, mas extrai a justificativa lógica cruzando as interseções de grafos geradas pelo motor de inferência.

## Como Executar e Testar (Questão 2.3)

1. **Pré-requisitos:**
   Certifique-se de ter a biblioteca `owlready2` instalada e o Java configurado na sua máquina (necessário para rodar o motor HermiT).
   ```bash
   pip install owlready2

```

2. **Execução do Sistema:**
Navegue até a pasta da ontologia e execute o script principal. O sistema irá compilar as regras, rodar o motor de inferência em tempo real e exibir o resultado.
```bash
cd questao_dois/ontologia
python sistema_recomendacao.py

```


3. **Resultados e Entregáveis:**
Ao rodar o comando acima, duas coisas acontecerão:
* O terminal exibirá o painel do **Sistema de Recomendação**, listando os filmes indicados para o usuário de teste e a *justificativa semântica* de cada escolha.
* O sistema exportará automaticamente o arquivo físico **`ontologia_filmes.owl`**, que contém todo o grafo de conhecimento (incluindo as inferências feitas pelo HermiT) pronto para ser aberto em softwares como o *Protégé*.
* O relatório também está presente em **SISTEMA DE RECOMENDAÇÃO BASEADO EM ONTOLOGIAS.pdf**



```

```
