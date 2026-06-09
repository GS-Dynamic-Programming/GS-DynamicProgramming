"""
Estruturas de dados para o sistema de monitoramento de riscos ambientais.
Cenários A (RS enchentes) e B (MATOPIBA seca) — FIAP Global Solution 2026
"""

from collections import deque


# ─────────────────────────────────────────────────────────────
# Árvore Binária de Busca (BST) — municípios por índice de risco
# ─────────────────────────────────────────────────────────────

class Node:
    __slots__ = ('municipio', 'left', 'right')

    def __init__(self, municipio: tuple):
        # municipio = (id_municipio, nome, indice_risco, custo_atendimento, populacao)
        self.municipio = municipio
        self.left = None
        self.right = None

    @property
    def risco(self) -> float:
        return self.municipio[2]

    @property
    def id(self) -> int:
        return self.municipio[0]


class BinarySearchTree:
    def __init__(self):
        self.root = None
        self._tamanho = 0

    def inserir(self, municipio: tuple) -> None:
        self.root = self._inserir(self.root, municipio)
        self._tamanho += 1

    def _inserir(self, node, municipio):
        if node is None:
            return Node(municipio)
        if municipio[2] < node.risco:
            node.left = self._inserir(node.left, municipio)
        elif municipio[2] > node.risco:
            node.right = self._inserir(node.right, municipio)
        else:
            # empate de risco: usa id como desempate para manter propriedade BST
            if municipio[0] < node.id:
                node.left = self._inserir(node.left, municipio)
            else:
                node.right = self._inserir(node.right, municipio)
        return node

    def buscar(self, r_min: float, r_max: float) -> list:
        """Retorna todos os municípios com índice de risco em [r_min, r_max]."""
        resultado = []
        self._buscar(self.root, r_min, r_max, resultado)
        return resultado

    def _buscar(self, node, r_min, r_max, resultado):
        if node is None:
            return
        # poda: só vai à esquerda se ainda pode haver nós >= r_min
        if node.risco > r_min:
            self._buscar(node.left, r_min, r_max, resultado)
        if r_min <= node.risco <= r_max:
            resultado.append(node.municipio)
        # poda: só vai à direita se ainda pode haver nós <= r_max
        if node.risco < r_max:
            self._buscar(node.right, r_min, r_max, resultado)

    def percurso_in_order(self) -> list:
        """Retorna municípios em ordem crescente de risco."""
        resultado = []
        self._in_order(self.root, resultado)
        return resultado

    def _in_order(self, node, resultado):
        if node is None:
            return
        self._in_order(node.left, resultado)
        resultado.append(node.municipio)
        self._in_order(node.right, resultado)

    def altura(self) -> int:
        return self._altura(self.root)

    def _altura(self, node) -> int:
        if node is None:
            return 0
        return 1 + max(self._altura(node.left), self._altura(node.right))

    def remover(self, id_municipio: int) -> bool:
        """Remove nó pelo id e reequilibra ponteiros. Retorna False se não encontrado."""
        risco = self._buscar_risco_por_id(self.root, id_municipio)
        if risco is None:
            return False
        self.root = self._remover(self.root, id_municipio, risco)
        self._tamanho -= 1
        return True

    def _buscar_risco_por_id(self, node, id_municipio):
        if node is None:
            return None
        if node.id == id_municipio:
            return node.risco
        left = self._buscar_risco_por_id(node.left, id_municipio)
        if left is not None:
            return left
        return self._buscar_risco_por_id(node.right, id_municipio)

    def _remover(self, node, id_municipio, risco):
        if node is None:
            return None
        if risco < node.risco or (risco == node.risco and id_municipio < node.id):
            node.left = self._remover(node.left, id_municipio, risco)
        elif risco > node.risco or (risco == node.risco and id_municipio > node.id):
            node.right = self._remover(node.right, id_municipio, risco)
        else:
            # nó encontrado
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left
            # substitui pelo sucessor in-order (mínimo da subárvore direita)
            sucessor = self._minimo(node.right)
            node.municipio = sucessor.municipio
            node.right = self._remover(node.right, sucessor.id, sucessor.risco)
        return node

    def _minimo(self, node):
        while node.left is not None:
            node = node.left
        return node

    def __len__(self) -> int:
        return self._tamanho


# ─────────────────────────────────────────────────────────────
# Grafo de municípios — dicionário de listas de adjacência
# ─────────────────────────────────────────────────────────────

class Grafo:
    """
    Grafo não-direcionado ponderado.
    Escolha por lista de adjacência (vs matriz): O(V+E) de espaço — eficiente
    para grafos esparsos como redes viárias onde E << V².
    Operações de percurso (BFS/DFS, Prim, Dijkstra) iteram apenas vizinhos reais.
    """

    def __init__(self):
        self.vertices: dict = {}       # {id: (id, nome, risco, custo, pop)}
        self.adjacencia: dict = {}     # {id: [(vizinho_id, peso), ...]}
        self._num_arestas: int = 0
        self._arestas_existentes: set = set()

    def adicionar_vertice(self, municipio: tuple) -> None:
        id_m = municipio[0]
        self.vertices[id_m] = municipio
        if id_m not in self.adjacencia:
            self.adjacencia[id_m] = []

    def adicionar_aresta(self, id1: int, id2: int, peso: float) -> None:
        chave = (min(id1, id2), max(id1, id2))
        if chave in self._arestas_existentes:
            return
        self.adjacencia[id1].append((id2, peso))
        self.adjacencia[id2].append((id1, peso))
        self._arestas_existentes.add(chave)
        self._num_arestas += 1

    def vizinhos(self, id_v: int) -> list:
        return self.adjacencia.get(id_v, [])

    def obter_todas_arestas(self) -> list:
        """Retorna lista de (u, v, peso) sem duplicatas."""
        return [(u, v, w)
                for u, v in self._arestas_existentes
                for w in [next(p for vv, p in self.adjacencia[u] if vv == v)]]

    def subgrafo(self, ids: list) -> 'Grafo':
        """Retorna subgrafo induzido pelos ids fornecidos."""
        ids_set = set(ids)
        sub = Grafo()
        for id_v in ids:
            sub.adicionar_vertice(self.vertices[id_v])
        for u, v in self._arestas_existentes:
            if u in ids_set and v in ids_set:
                peso = next(p for vv, p in self.adjacencia[u] if vv == v)
                sub.adicionar_aresta(u, v, peso)
        return sub

    @property
    def num_vertices(self) -> int:
        return len(self.vertices)

    @property
    def num_arestas(self) -> int:
        return self._num_arestas

    def __repr__(self) -> str:
        return f"Grafo(V={self.num_vertices}, E={self.num_arestas})"


# ─────────────────────────────────────────────────────────────
# BFS — Busca em Largura usando deque (seção 2.3: Fila/deque)
# ─────────────────────────────────────────────────────────────

def bfs(grafo: Grafo, id_origem: int) -> dict:
    """
    Busca em Largura a partir de id_origem usando deque como fila FIFO.
    Retorna {id_vertice: distancia_em_saltos} para todos os vértices alcançáveis.
    Uso: verificar conectividade do grafo de risco; calcular hop-distance.
    """
    visitados = {id_origem: 0}
    fila = deque([id_origem])

    while fila:
        atual = fila.popleft()
        for vizinho, _ in grafo.vizinhos(atual):
            if vizinho not in visitados:
                visitados[vizinho] = visitados[atual] + 1
                fila.append(vizinho)

    return visitados
