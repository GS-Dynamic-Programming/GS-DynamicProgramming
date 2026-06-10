"""
Testes unitários — Global Solution 2026 (Dynamic Programming).

Cobre:
- BinarySearchTree (inserir, buscar, percurso_in_order, altura, remover)
- Grafo (vértices, arestas, vizinhos, subgrafo)
- bfs (conectividade)
- Força Bruta (MST e caminho mínimo)
- Guloso (Prim, Dijkstra, reconstrução de caminho, priorização por risco)
- Validação cruzada FB x Guloso em instâncias pequenas (N <= 12)
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest

from src.data_structures import Node, BinarySearchTree, Grafo, bfs
from src.brute_force import brute_force_mst, brute_force_caminho_minimo
from src.greedy import prim_mst, dijkstra, reconstruir_caminho, guloso_prioridade_risco
from data.raw.municipios_rs import (
    criar_grafo_rs, criar_bst_rs, criar_subgrafo_n_maior_risco,
)
from data.raw.municipios_matopiba import criar_grafo_matopiba, criar_bst_matopiba


# ─────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────

MUNICIPIOS_TESTE = [
    (1, 'Alfa', 0.50, 100.0, 1000),
    (2, 'Beta', 0.20, 200.0, 2000),
    (3, 'Gama', 0.80, 300.0, 3000),
    (4, 'Delta', 0.10, 400.0, 4000),
    (5, 'Epsilon', 0.35, 500.0, 5000),
    (6, 'Zeta', 0.65, 600.0, 6000),
    (7, 'Eta', 0.95, 700.0, 7000),
]


@pytest.fixture
def bst_pequena():
    bst = BinarySearchTree()
    for m in MUNICIPIOS_TESTE:
        bst.inserir(m)
    return bst


@pytest.fixture
def grafo_pequeno():
    """
    Grafo conectado e pequeno (5 vértices, 6 arestas) com MST conhecida.

    Arestas:        Pesos:
      A-B = 1          MST esperada (custo 8):
      A-C = 4            A-B (1) + B-D (2) + B-E (3) + A-C (4)... avaliar via FB
      B-D = 2
      B-E = 3
      C-E = 5
      D-E = 6
    """
    g = Grafo()
    for i, nome in enumerate(['A', 'B', 'C', 'D', 'E']):
        g.adicionar_vertice((i, nome, 0.5, 100.0, 1000))
    g.adicionar_aresta(0, 1, 1.0)  # A-B
    g.adicionar_aresta(0, 2, 4.0)  # A-C
    g.adicionar_aresta(1, 3, 2.0)  # B-D
    g.adicionar_aresta(1, 4, 3.0)  # B-E
    g.adicionar_aresta(2, 4, 5.0)  # C-E
    g.adicionar_aresta(3, 4, 6.0)  # D-E
    return g


# ─────────────────────────────────────────────────────────────
# BinarySearchTree
# ─────────────────────────────────────────────────────────────

class TestBinarySearchTree:
    def test_inserir_aumenta_tamanho(self, bst_pequena):
        assert len(bst_pequena) == len(MUNICIPIOS_TESTE)

    def test_percurso_in_order_eh_crescente(self, bst_pequena):
        riscos = [m[2] for m in bst_pequena.percurso_in_order()]
        assert riscos == sorted(riscos)

    def test_buscar_intervalo(self, bst_pequena):
        resultado = bst_pequena.buscar(0.5, 0.8)
        riscos = sorted(m[2] for m in resultado)
        assert riscos == [0.50, 0.65, 0.80]

    def test_buscar_intervalo_vazio(self, bst_pequena):
        assert bst_pequena.buscar(0.96, 1.0) == []

    def test_altura_arvore_vazia(self):
        assert BinarySearchTree().altura() == 0

    def test_altura_arvore_nao_vazia(self, bst_pequena):
        assert bst_pequena.altura() >= 1
        # altura nunca pode exceder o número de nós
        assert bst_pequena.altura() <= len(bst_pequena)

    def test_remover_folha(self, bst_pequena):
        ids_antes = {m[0] for m in bst_pequena.percurso_in_order()}
        assert bst_pequena.remover(7) is True  # Eta, risco mais alto (folha)
        ids_depois = {m[0] for m in bst_pequena.percurso_in_order()}
        assert ids_depois == ids_antes - {7}
        assert len(bst_pequena) == len(MUNICIPIOS_TESTE) - 1

    def test_remover_no_com_dois_filhos_mantem_propriedade_bst(self, bst_pequena):
        bst_pequena.remover(1)  # Alfa: nó interno (risco 0.50)
        riscos = [m[2] for m in bst_pequena.percurso_in_order()]
        assert riscos == sorted(riscos)
        assert len(bst_pequena) == len(MUNICIPIOS_TESTE) - 1

    def test_remover_inexistente_retorna_false(self, bst_pequena):
        assert bst_pequena.remover(999) is False
        assert len(bst_pequena) == len(MUNICIPIOS_TESTE)


# ─────────────────────────────────────────────────────────────
# Grafo
# ─────────────────────────────────────────────────────────────

class TestGrafo:
    def test_adicionar_vertice_e_aresta(self, grafo_pequeno):
        assert grafo_pequeno.num_vertices == 5
        assert grafo_pequeno.num_arestas == 6

    def test_grafo_eh_nao_direcionado(self, grafo_pequeno):
        vizinhos_a = dict(grafo_pequeno.vizinhos(0))
        vizinhos_b = dict(grafo_pequeno.vizinhos(1))
        assert vizinhos_a[1] == 1.0
        assert vizinhos_b[0] == 1.0

    def test_aresta_duplicada_eh_ignorada(self, grafo_pequeno):
        antes = grafo_pequeno.num_arestas
        grafo_pequeno.adicionar_aresta(1, 0, 99.0)
        assert grafo_pequeno.num_arestas == antes

    def test_obter_todas_arestas(self, grafo_pequeno):
        arestas = grafo_pequeno.obter_todas_arestas()
        assert len(arestas) == grafo_pequeno.num_arestas

    def test_subgrafo_induzido(self, grafo_pequeno):
        sub = grafo_pequeno.subgrafo([0, 1, 3])
        assert sub.num_vertices == 3
        # arestas A-B e B-D pertencem ao subgrafo; A-C, B-E, C-E, D-E não
        assert sub.num_arestas == 2


# ─────────────────────────────────────────────────────────────
# BFS
# ─────────────────────────────────────────────────────────────

class TestBFS:
    def test_bfs_alcanca_todos_os_vertices_em_grafo_conexo(self, grafo_pequeno):
        alcancados = bfs(grafo_pequeno, 0)
        assert set(alcancados.keys()) == set(grafo_pequeno.vertices.keys())

    def test_bfs_distancias_em_saltos(self, grafo_pequeno):
        alcancados = bfs(grafo_pequeno, 0)
        assert alcancados[0] == 0
        assert alcancados[1] == 1  # A-B direta
        assert alcancados[3] == 2  # A-B-D


# ─────────────────────────────────────────────────────────────
# Força Bruta
# ─────────────────────────────────────────────────────────────

class TestBrutForce:
    def test_brute_force_mst_custo_otimo(self, grafo_pequeno):
        mst, custo, contadores = brute_force_mst(grafo_pequeno)
        assert mst is not None
        assert len(mst) == grafo_pequeno.num_vertices - 1
        assert custo == pytest.approx(10.0)  # A-B(1) + B-D(2) + B-E(3) + A-C(4)
        assert contadores['subconjuntos_avaliados'] > 0

    def test_brute_force_caminho_minimo(self, grafo_pequeno):
        caminho, custo, contadores = brute_force_caminho_minimo(grafo_pequeno, 0, 4)
        assert caminho[0] == 0
        assert caminho[-1] == 4
        assert custo == pytest.approx(4.0)  # A-B(1) + B-E(3)
        assert contadores['chamadas_recursivas'] > 0
        assert contadores['caminhos_avaliados'] > 0


# ─────────────────────────────────────────────────────────────
# Guloso
# ─────────────────────────────────────────────────────────────

class TestGreedy:
    def test_prim_mst_custo_igual_ao_otimo(self, grafo_pequeno):
        _, custo_fb, _ = brute_force_mst(grafo_pequeno)
        mst, custo_prim, contadores, _ = prim_mst(grafo_pequeno, 0)
        assert len(mst) == grafo_pequeno.num_vertices - 1
        assert custo_prim == pytest.approx(custo_fb)
        assert contadores['insercoes_heap'] > 0

    def test_dijkstra_distancias_corretas(self, grafo_pequeno):
        dist, pred, _ = dijkstra(grafo_pequeno, 0)
        assert dist[0] == 0.0
        assert dist[1] == pytest.approx(1.0)   # A-B
        assert dist[3] == pytest.approx(3.0)   # A-B-D
        assert dist[4] == pytest.approx(4.0)   # A-B-E

    def test_reconstruir_caminho(self, grafo_pequeno):
        _, pred, _ = dijkstra(grafo_pequeno, 0)
        caminho = reconstruir_caminho(pred, 3)
        assert caminho == [0, 1, 3]

    def test_guloso_prioridade_risco_respeita_orcamento(self):
        grafo = criar_grafo_rs()
        bst = criar_bst_rs(grafo)
        atendidos, custo, _ = guloso_prioridade_risco(grafo, bst, orcamento_max=1000.0)
        assert custo <= 1000.0
        # todos os atendidos devem ter risco >= 0.6 (faixa consultada na BST)
        assert all(m[2] >= 0.6 for m in atendidos)


# ─────────────────────────────────────────────────────────────
# Validação cruzada FB x Guloso em instâncias reais pequenas
# ─────────────────────────────────────────────────────────────

class TestValidacaoCenarioRS:
    @pytest.mark.parametrize("n", [5, 8, 10, 12])
    def test_subgrafo_real_eh_conectado(self, n):
        sub = criar_subgrafo_n_maior_risco(n)
        alcancados = bfs(sub, list(sub.vertices.keys())[0])
        assert len(alcancados) == sub.num_vertices == n

    @pytest.mark.parametrize("n", [5, 8, 10, 12])
    def test_fb_e_prim_concordam_em_instancias_pequenas(self, n):
        sub = criar_subgrafo_n_maior_risco(n)
        _, custo_fb, _ = brute_force_mst(sub)
        _, custo_prim, _, _ = prim_mst(sub, list(sub.vertices.keys())[0])
        assert custo_fb != float('inf')
        assert custo_prim == pytest.approx(custo_fb)


# ─────────────────────────────────────────────────────────────
# Cenário MATOPIBA
# ─────────────────────────────────────────────────────────────

class TestCenarioMatopiba:
    def test_grafo_e_bst_consistentes(self):
        grafo = criar_grafo_matopiba()
        bst = criar_bst_matopiba(grafo)
        assert len(bst) == grafo.num_vertices
        assert grafo.num_vertices == 20

    def test_prim_gera_arvore_geradora_completa(self):
        grafo = criar_grafo_matopiba()
        inicio = list(grafo.vertices.keys())[0]
        mst, custo, _, _ = prim_mst(grafo, inicio)
        assert len(mst) == grafo.num_vertices - 1
        assert custo > 0
