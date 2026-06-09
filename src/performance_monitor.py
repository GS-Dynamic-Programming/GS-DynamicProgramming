"""
Módulo de monitoramento de desempenho.
Mede tempo (time.perf_counter), memória (tracemalloc) e operações elementares.
"""

import time
import tracemalloc
import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.data_structures import Grafo


class ResultadoDesempenho:
    def __init__(self, algoritmo: str, n: int, tempo_ms: float,
                 memoria_mb: float, operacoes: int, custo_solucao: float):
        self.algoritmo = algoritmo
        self.n = n
        self.tempo_ms = tempo_ms
        self.memoria_mb = memoria_mb
        self.operacoes = operacoes
        self.custo_solucao = custo_solucao

    def __repr__(self) -> str:
        return (f"[{self.algoritmo:15s}] N={self.n:4d} | "
                f"Tempo={self.tempo_ms:8.3f}ms | "
                f"Mem={self.memoria_mb:.4f}MB | "
                f"Ops={self.operacoes:8d} | "
                f"Custo={self.custo_solucao:.3f}")


def medir_desempenho(func, *args, **kwargs):
    """
    Executa func(*args, **kwargs) e retorna (resultado, tempo_ms, memoria_mb).
    """
    tracemalloc.start()
    inicio = time.perf_counter()

    resultado = func(*args, **kwargs)

    fim = time.perf_counter()
    _, pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    tempo_ms = (fim - inicio) * 1000
    memoria_mb = pico / (1024 * 1024)
    return resultado, tempo_ms, memoria_mb


def gerar_grafo_benchmark(n: int, seed: int = 42) -> Grafo:
    """
    Gera grafo conectado aleatório com n vértices para experimentos de benchmark.
    Garante conectividade via spanning tree aleatório + arestas extras esparsas.
    """
    random.seed(seed)
    g = Grafo()

    for i in range(n):
        risco = round(random.uniform(0.3, 1.0), 2)
        g.adicionar_vertice((
            i,
            f'M{i:03d}',
            risco,
            round(random.uniform(100.0, 2000.0), 1),
            random.randint(5000, 500000),
        ))

    ids = list(range(n))
    random.shuffle(ids)

    # spanning tree aleatório para garantir conectividade
    for i in range(1, n):
        peso = round(random.uniform(0.5, 5.0), 2)
        g.adicionar_aresta(ids[i - 1], ids[i], peso)

    # arestas extras (grafo esparso: ~n/2 arestas adicionais)
    adicionadas = 0
    tentativas = n * 3
    while adicionadas < n // 2 and tentativas > 0:
        u = random.randint(0, n - 1)
        v = random.randint(0, n - 1)
        if u != v:
            peso = round(random.uniform(0.5, 5.0), 2)
            antes = g.num_arestas
            g.adicionar_aresta(u, v, peso)
            if g.num_arestas > antes:
                adicionadas += 1
        tentativas -= 1

    return g


def benchmark_completo(tamanhos: list) -> list:
    """
    Executa benchmark de Força Bruta e Prim para cada tamanho N.
    Força Bruta apenas para N <= 12 (restrição de explosão combinatória).

    Retorna lista de ResultadoDesempenho.
    """
    from src.brute_force import brute_force_mst
    from src.greedy import prim_mst

    resultados = []

    for n in tamanhos:
        grafo = gerar_grafo_benchmark(n)
        id_inicio = list(grafo.vertices.keys())[0]

        # ── Força Bruta ──────────────────────────────────────
        if n <= 12:
            resultado_fb, tempo_ms, mem_mb = medir_desempenho(brute_force_mst, grafo)
            mst_fb, custo_fb, contadores_fb = resultado_fb
            ops_fb = contadores_fb['subconjuntos_avaliados']
            resultados.append(ResultadoDesempenho(
                'Força Bruta', n, tempo_ms, mem_mb, ops_fb, custo_fb or 0.0
            ))
            print(resultados[-1])

        resultado_prim, tempo_ms, mem_mb = medir_desempenho(prim_mst, grafo, id_inicio)
        mst_p, custo_p, contadores_p, _ = resultado_prim
        ops_p = contadores_p['insercoes_heap'] + contadores_p['arestas_relaxadas']
        resultados.append(ResultadoDesempenho(
            'Prim (Guloso)', n, tempo_ms, mem_mb, ops_p, custo_p
        ))
        print(resultados[-1])

    return resultados