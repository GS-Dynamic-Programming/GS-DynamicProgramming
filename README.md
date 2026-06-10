# Global Solution 2026 — Monitoramento de Riscos Ambientais com Árvores, Grafos e Algoritmos

**Disciplina:** Estruturas de Dados e Algoritmos — FIAP | Dynamic Programming
**Tema:** Força Bruta · Algoritmos Gulosos · Estruturas de Dados

## Integrantes do grupo

| RM | Nome |
|---|---|
| 563995 | Azor Biagioni Tartuce |
| 562077 | João Pedro Ribeiro Palermo |
| 561872 | Enzo Hort Ramos |
| 562169 | Eduardo Santa Rosa Tolentino |
| 562752 | Felipe Campos Vianna Peres |

## 1. Visão geral

O sistema modela municípios brasileiros e suas conexões (rodovias) como um
grafo ponderado, organiza os índices de risco ambiental em uma Árvore Binária
de Busca (BST) implementada do zero e compara duas estratégias algorítmicas
para o problema da Árvore Geradora Mínima (MST) de cobertura:

- **Força Bruta** — enumeração exaustiva de subconjuntos de arestas
  (`itertools.combinations` + Union-Find), usada como oráculo de validação
  para N ≤ 12 vértices;
- **Guloso (Algoritmo de Prim)** — construção incremental da MST com
  `heapq`, usada como solução de produção para instâncias reais.

### Cenários brasileiros implementados

- **Cenário A — Rede de resposta a enchentes no RS**: 30 municípios da região
  metropolitana de Porto Alegre / Vale do Taquari afetados pelas enchentes de
  2024. Pesos das arestas = tempo de deslocamento (horas). Fonte: malha viária
  DNIT + índices de risco sintéticos validados com base em relatórios da
  Defesa Civil RS / ANA.
- **Cenário B — Triagem de risco de seca no MATOPIBA**: 20 municípios da
  região MATOPIBA (MA, TO, PI, BA). Índice de risco derivado de NDVI
  (MODIS/NASA) + precipitação (INMET). O Guloso prioriza o atendimento por
  índice de risco dado um orçamento máximo de deslocamento, consultando a BST.

## 2. Estrutura do repositório

```
.
├── README.md
├── requirements.txt
├── data/
│   ├── raw/                  # Dados brutos dos cenários (RS e MATOPIBA)
│   │   ├── municipios_rs.py
│   │   └── municipios_matopiba.py
│   └── processed/            # Grafos e BSTs serializados (JSON)
├── src/
│   ├── data_structures.py    # Grafo, BST (Node/BinarySearchTree), BFS
│   ├── brute_force.py        # MST e caminho mínimo por força bruta
│   ├── greedy.py             # Prim, Dijkstra, priorização por risco (Cenário B)
│   ├── performance_monitor.py# Medição de tempo, memória e operações
│   └── visualizations.py     # Figuras obrigatórias (grafo+MST, BST, desempenho, gap, explosão)
├── notebooks/
│   └── analise_resultados.ipynb  # Análise interativa, figuras e escala de decisão
├── tests/
│   └── test_algorithms.py    # Testes unitários (pytest)
└── report/
    ├── figures/               # Figuras geradas pelo notebook
    └── relatorio_final.pdf    # Relatório técnico (≤ 4 páginas)
```

## 3. Instalação e execução

### Pré-requisitos

- Python 3.10+

### Passo a passo

```bash
# 1. Criar e ativar um ambiente virtual
python3 -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate          # Windows

# 2. Instalar as dependências
pip install -r requirements.txt

# 3. Rodar os testes automatizados
pytest tests/ -v

# 4. Rodar a análise completa (gera figuras em report/figures/
#    e dados serializados em data/processed/)
jupyter nbconvert --to notebook --execute --inplace notebooks/analise_resultados.ipynb
# ou abra o notebook interativamente:
jupyter notebook notebooks/analise_resultados.ipynb
```

### Execução rápida via terminal (sem notebook)

```bash
# Resumo do grafo e da BST de cada cenário
python3 -m data.raw.municipios_rs
python3 -m data.raw.municipios_matopiba
```

## 4. Descrição dos módulos

| Módulo | Conteúdo |
|---|---|
| `src/data_structures.py` | Classes `Node` e `BinarySearchTree` (inserir, buscar por intervalo de risco, percurso in-order, altura, remover); classe `Grafo` (lista de adjacência ponderada, não-direcionada); função `bfs` (busca em largura com `deque`). |
| `src/brute_force.py` | `brute_force_mst`: enumera todos os subconjuntos de N-1 arestas e retorna a MST de custo mínimo (com Union-Find para validar árvore geradora) — restrito a N ≤ 12. `brute_force_caminho_minimo`: enumera caminhos simples via backtracking recursivo, contando chamadas e caminhos avaliados. `contar_caminhos_por_tamanho`: gera os dados para o gráfico de explosão combinatória. |
| `src/greedy.py` | `prim_mst`: MST pelo Algoritmo de Prim com `heapq`, contadores de operações e dicionário de predecessores. `dijkstra`: caminho mínimo de fonte única. `reconstruir_caminho`: reconstrói a rota a partir dos predecessores. `guloso_prioridade_risco`: prioriza municípios por índice de risco (consulta à BST) dentro de um orçamento máximo (Cenário B). |
| `src/performance_monitor.py` | `medir_desempenho`: mede tempo (`time.perf_counter`) e memória (`tracemalloc`) de qualquer função. `gerar_grafo_benchmark`: gera grafos sintéticos conectados para os testes de escalabilidade. `benchmark_completo`: roda Força Bruta (N ≤ 12) e Prim (todos os N) e retorna os resultados. |
| `src/visualizations.py` | Figuras obrigatórias: grafo com a MST destacada, diagrama da BST, desempenho (tempo/memória × N), gap de otimalidade e explosão combinatória da Força Bruta. |
| `data/raw/municipios_rs.py` | Vértices, arestas, e funções `criar_grafo_rs`, `criar_bst_rs` e `criar_subgrafo_n_maior_risco` (subgrafo conectado dos N municípios de maior risco, usado na validação FB × Guloso). |
| `data/raw/municipios_matopiba.py` | Vértices, arestas, e funções `criar_grafo_matopiba` e `criar_bst_matopiba`. |
| `notebooks/analise_resultados.ipynb` | Executa os dois cenários, gera as 6 figuras, valida FB × Guloso (N=5,8,10,12), mede desempenho (N=5,8,10,12,20,50,100), calcula o gap de otimalidade, apresenta a tabela de estruturas de dados e a escala de decisão, e serializa os grafos/BSTs em `data/processed/`. |
| `tests/test_algorithms.py` | Testes unitários da BST, do Grafo, do BFS, da Força Bruta, do Guloso (Prim/Dijkstra) e validação cruzada FB × Guloso em instâncias reais (N = 5, 8, 10, 12). |

## 5. Principais resultados

- O Guloso (Prim) produz MSTs com **gap de otimalidade de 0%** em relação à
  Força Bruta em todas as instâncias testadas (N = 5, 8, 10, 12, real e
  sintético) — resultado esperado pela propriedade do corte da MST.
- A Força Bruta torna-se inviável a partir de N ≈ 12 (C(|E|, N-1) na casa das
  dezenas de milhares e crescendo super-exponencialmente).
- Detalhes completos, figuras e a escala de decisão estão em
  `notebooks/analise_resultados.ipynb` e `report/relatorio_final.pdf`.

## 6. Fontes de dados e referências

- Defesa Civil RS / ANA / DNIT — enchentes RS 2024
- NDVI MODIS/NASA + INMET + IBGE — risco de seca MATOPIBA
- Cormen, T. et al. (2022). *Introduction to Algorithms*, 4th Ed. MIT Press.
