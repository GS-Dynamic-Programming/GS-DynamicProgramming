"""
Algoritmo Guloso — Prim para Árvore Geradora Mínima (MST).
Escolha justificada: Prim com heap é ideal para grafos densos/conexos como redes viárias,
pois opera sobre vértices (O((V+E) log V)) sem precisar ordenar todas as arestas.
"""

import heapq


def prim_mst(grafo, id_inicio: int):
    """
    Constrói a MST a partir de id_inicio adicionando sempre a aresta de menor
    peso que conecta um vértice novo à árvore já construída.

    Critério local guloso: a cada passo, escolhe a aresta de menor peso disponível.
    Prova informal de corretude: pelo Teorema do Corte, a aresta mais leve cruzando
    qualquer corte pertence a alguma MST (Cormen et al., 2022, Cap. 21).

    Retorna: (mst_arestas, custo_total, contadores, predecessores)
    """
    visitados = set()
    mst_arestas = []
    custo_total = 0.0
    predecessores = {id_inicio: None}
    custos_minimos = {v: float('inf') for v in grafo.vertices}
    custos_minimos[id_inicio] = 0.0

    contadores = {
        'insercoes_heap': 0,
        'extractions_heap': 0,
        'arestas_relaxadas': 0,
    }

    heap = [(0.0, id_inicio, id_inicio)]
    contadores['insercoes_heap'] += 1

    while heap:
        peso, origem, destino = heapq.heappop(heap)
        contadores['extractions_heap'] += 1

        if destino in visitados:
            continue

        visitados.add(destino)

        if origem != destino:
            mst_arestas.append((origem, destino, peso))
            custo_total += peso

        for vizinho, w in grafo.vizinhos(destino):
            contadores['arestas_relaxadas'] += 1
            if vizinho not in visitados and w < custos_minimos[vizinho]:
                custos_minimos[vizinho] = w
                predecessores[vizinho] = destino
                heapq.heappush(heap, (w, destino, vizinho))
                contadores['insercoes_heap'] += 1

    return mst_arestas, custo_total, contadores, predecessores


def dijkstra(grafo, id_origem: int):
    """
    Caminho mínimo de fonte única — encontra a rota mais rápida de Porto Alegre
    a cada município afetado (usado como análise complementar à MST).

    Retorna: (distancias, predecessores, contadores)
    """
    dist = {v: float('inf') for v in grafo.vertices}
    dist[id_origem] = 0.0
    pred = {id_origem: None}
    contadores = {'insercoes_heap': 0, 'extractions_heap': 0, 'relaxamentos': 0}

    heap = [(0.0, id_origem)]
    contadores['insercoes_heap'] += 1

    while heap:
        d, u = heapq.heappop(heap)
        contadores['extractions_heap'] += 1

        if d > dist[u]:
            continue

        for v, w in grafo.vizinhos(u):
            contadores['relaxamentos'] += 1
            nova_dist = dist[u] + w
            if nova_dist < dist[v]:
                dist[v] = nova_dist
                pred[v] = u
                heapq.heappush(heap, (nova_dist, v))
                contadores['insercoes_heap'] += 1

    return dist, pred, contadores


def reconstruir_caminho(predecessores: dict, destino_id: int) -> list:
    """Reconstrói o caminho do origem até destino a partir do dicionário de predecessores."""
    caminho = []
    atual = destino_id
    while atual is not None:
        caminho.append(atual)
        atual = predecessores.get(atual)
    caminho.reverse()
    return caminho


def guloso_prioridade_risco(grafo, bst, orcamento_max: float):
    """
    Determina a ordem ótima de atendimento priorizando municípios críticos
    dentro de um orçamento máximo de deslocamento.

    Critério guloso: ordena por risco decrescente e seleciona enquanto cabe no orçamento.
    Usa a BST para consultar municípios com índice de risco >= 0.6.

    Retorna: (municipios_atendidos, custo_total, ids_fronteira)
    """
    municipios_criticos = bst.buscar(0.6, 1.0)
    municipios_criticos.sort(key=lambda m: m[2], reverse=True)

    atendidos = []
    custo_acumulado = 0.0
    ids_fronteira = set()

    for municipio in municipios_criticos:
        custo = municipio[3]
        if custo_acumulado + custo <= orcamento_max:
            atendidos.append(municipio)
            custo_acumulado += custo
            ids_fronteira.add(municipio[0])

    return atendidos, custo_acumulado, ids_fronteira