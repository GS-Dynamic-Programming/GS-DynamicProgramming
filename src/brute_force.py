"""
Força Bruta — enumeração exaustiva para validação e demonstração de explosão combinatória.
Restrito a N ≤ 12 vértices.
"""

from itertools import combinations


class _UnionFind:
    def __init__(self, ids: list):
        self._parent = {x: x for x in ids}
        self._rank = {x: 0 for x in ids}

    def find(self, x):
        if self._parent[x] != x:
            self._parent[x] = self.find(self._parent[x])
        return self._parent[x]

    def union(self, x, y) -> bool:
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        if self._rank[px] < self._rank[py]:
            px, py = py, px
        self._parent[py] = px
        if self._rank[px] == self._rank[py]:
            self._rank[px] += 1
        return True


def _forma_arvore_geradora(arestas: list, ids: list) -> bool:
    n = len(ids)
    if len(arestas) != n - 1:
        return False
    uf = _UnionFind(ids)
    for u, v, _ in arestas:
        if not uf.union(u, v):
            return False
    raiz = uf.find(ids[0])
    return all(uf.find(i) == raiz for i in ids)


def brute_force_mst(grafo):
    """
    Encontra a MST de menor peso enumerando todos os subconjuntos de (n-1) arestas.
    Demonstra explosão combinatória: C(|E|, n-1) cresce rapidamente com N.

    Retorna: (mst_arestas, custo_total, contadores)
    """
    ids = list(grafo.vertices.keys())
    n = len(ids)
    arestas = grafo.obter_todas_arestas()

    contadores = {
        'subconjuntos_avaliados': 0,
        'arvores_validas': 0,
        'total_possiveis': 0,
    }

    melhor_custo = float('inf')
    melhor_mst = None

    from math import comb
    contadores['total_possiveis'] = comb(len(arestas), n - 1)

    for combo in combinations(arestas, n - 1):
        contadores['subconjuntos_avaliados'] += 1

        custo = sum(w for _, _, w in combo)
        # poda por custo antes de verificar conectividade
        if custo >= melhor_custo:
            continue

        if _forma_arvore_geradora(list(combo), ids):
            contadores['arvores_validas'] += 1
            melhor_custo = custo
            melhor_mst = list(combo)

    return melhor_mst, melhor_custo, contadores


def brute_force_caminho_minimo(grafo, origem_id: int, destino_id: int):
    """
    Enumera todos os caminhos simples entre origem e destino com backtracking.
    Retorna o caminho de menor custo.

    Retorna: (caminho, custo, contadores)
    """
    contadores = {'chamadas_recursivas': 0, 'caminhos_avaliados': 0}
    melhor = {'custo': float('inf'), 'caminho': None}

    def backtrack(atual, visitados, caminho, custo):
        contadores['chamadas_recursivas'] += 1

        if atual == destino_id:
            contadores['caminhos_avaliados'] += 1
            if custo < melhor['custo']:
                melhor['custo'] = custo
                melhor['caminho'] = list(caminho)
            return

        for vizinho, peso in grafo.vizinhos(atual):
            if vizinho not in visitados:
                visitados.add(vizinho)
                caminho.append(vizinho)
                backtrack(vizinho, visitados, caminho, custo + peso)
                caminho.pop()
                visitados.remove(vizinho)

    visitados = {origem_id}
    backtrack(origem_id, visitados, [origem_id], 0.0)
    return melhor['caminho'], melhor['custo'], contadores


def contar_caminhos_por_tamanho(grafo, origem_id: int, tamanhos: list) -> dict:
    """
    Para cada N em tamanhos, conta quantos caminhos existem a partir de origem.
    Usado para gerar o gráfico de explosão combinatória.
    """
    import time
    resultados = {}
    for n in tamanhos:
        ids = list(grafo.vertices.keys())[:n]
        sub = grafo.subgrafo(ids)
        if origem_id not in sub.vertices:
            continue
        destinos = [i for i in ids if i != origem_id]
        if not destinos:
            continue
        destino = destinos[-1]
        inicio = time.perf_counter()
        _, _, cnt = brute_force_caminho_minimo(sub, origem_id, destino)
        tempo = (time.perf_counter() - inicio) * 1000
        resultados[n] = {
            'chamadas': cnt['chamadas_recursivas'],
            'caminhos': cnt['caminhos_avaliados'],
            'tempo_ms': tempo,
        }
    return resultados
