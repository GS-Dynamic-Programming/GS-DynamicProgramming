"""
Dados dos municípios do Rio Grande do Sul afetados pelas enchentes de 2024.
IDs baseados em códigos IBGE. Índices de risco sintéticos validados com base
em dados de precipitação e inundação reportados pela Defesa Civil RS / ANA.
Fonte: Defesa Civil RS + malha viária DNIT.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.data_structures import Grafo, BinarySearchTree


# municipio = (id_ibge, nome, indice_risco, custo_atendimento_R$k, populacao)
MUNICIPIOS = [
    (4314902, 'Porto Alegre',         0.72, 1850.0, 1400000),
    (4304606, 'Canoas',               0.81, 1200.0,  340000),
    (4318705, 'São Leopoldo',         0.78,  980.0,  230000),
    (4313409, 'Novo Hamburgo',        0.65,  900.0,  239000),
    (4309209, 'Gravataí',             0.69,  850.0,  280000),
    (4323002, 'Viamão',               0.74,  780.0,  260000),
    (4302303, 'Cachoeirinha',         0.83,  720.0,  130000),
    (4300604, 'Alvorada',             0.88,  650.0,  200000),
    (4306659, 'Eldorado do Sul',      0.91,  420.0,   40000),
    (4309500, 'Guaíba',               0.85,  480.0,  100000),
    (4305207, 'Charqueadas',          0.76,  380.0,   40000),
    (4312427, 'Montenegro',           0.58,  350.0,   60000),
    (4322301, 'Triunfo',              0.62,  280.0,   25000),
    (4318408, 'São Jerônimo',         0.70,  260.0,   23000),
    (4301909, 'Barra do Ribeiro',     0.79,  220.0,   13000),
    (4321303, 'Taquari',              0.67,  300.0,   27000),
    (4311560, 'Lajeado',              0.73,  420.0,   80000),
    (4307625, 'Estrela',              0.61,  310.0,   35000),
    (4306403, 'Encantado',            0.55,  280.0,   24000),
    (4322806, 'Venâncio Aires',       0.59,  350.0,   70000),
    (4313375, 'Nova Santa Rita',      0.86,  280.0,   28000),
    (4315503, 'Portão',               0.71,  260.0,   35000),
    (4308508, 'Estância Velha',       0.68,  290.0,   42000),
    (4317202, 'São Sebastião do Caí', 0.63,  270.0,   25000),
    (4316709, 'Santa Cruz do Sul',    0.52,  520.0,  130000),
    (4306106, 'Cruzeiro do Sul',      0.64,  240.0,   20000),
    (4320107, 'Sinimbu',              0.57,  190.0,   12000),
    (4313300, 'Novo Cabrais',         0.60,  190.0,    7000),
    (4307807, 'Fazenda Vilanova',     0.66,  180.0,   10000),
    (4313730, 'Passo do Sobrado',     0.75,  210.0,   12000),
]

# (id1, id2, horas_deslocamento) — baseado em malha viária DNIT
ARESTAS = [
    (4314902, 4304606, 0.35),   # Porto Alegre - Canoas (BR-116)
    (4314902, 4309209, 0.50),   # Porto Alegre - Gravataí (RS-020)
    (4314902, 4323002, 0.40),   # Porto Alegre - Viamão (RS-040)
    (4314902, 4300604, 0.25),   # Porto Alegre - Alvorada (RS-118)
    (4314902, 4309500, 0.55),   # Porto Alegre - Guaíba (RS-005)
    (4304606, 4318705, 0.25),   # Canoas - São Leopoldo (RS-020)
    (4304606, 4302303, 0.20),   # Canoas - Cachoeirinha (BR-116)
    (4304606, 4313375, 0.30),   # Canoas - Nova Santa Rita (RS-020)
    (4318705, 4313409, 0.25),   # São Leopoldo - Novo Hamburgo (RS-239)
    (4318705, 4315503, 0.30),   # São Leopoldo - Portão (RS-240)
    (4313409, 4308508, 0.15),   # Novo Hamburgo - Estância Velha (RS-239)
    (4313409, 4317202, 0.35),   # Novo Hamburgo - São Sebastião do Caí (RS-122)
    (4309209, 4302303, 0.20),   # Gravataí - Cachoeirinha (RS-020)
    (4300604, 4306659, 0.45),   # Alvorada - Eldorado do Sul (RS-130)
    (4309500, 4306659, 0.35),   # Guaíba - Eldorado do Sul (RS-005)
    (4309500, 4301909, 0.50),   # Guaíba - Barra do Ribeiro (RS-714)
    (4306659, 4305207, 0.50),   # Eldorado do Sul - Charqueadas (RS-401)
    (4305207, 4312427, 0.50),   # Charqueadas - Montenegro (RS-287)
    (4305207, 4322301, 0.35),   # Charqueadas - Triunfo (RS-401)
    (4312427, 4322301, 0.25),   # Montenegro - Triunfo (RS-287)
    (4312427, 4317202, 0.45),   # Montenegro - São Sebastião do Caí (RS-122)
    (4322301, 4321303, 0.40),   # Triunfo - Taquari (RS-130)
    (4318408, 4321303, 0.50),   # São Jerônimo - Taquari (RS-687)
    (4301909, 4318408, 0.75),   # Barra do Ribeiro - São Jerônimo (RS-509)
    (4321303, 4311560, 0.35),   # Taquari - Lajeado (BR-386)
    (4321303, 4307807, 0.25),   # Taquari - Fazenda Vilanova (RS-130)
    (4311560, 4307625, 0.15),   # Lajeado - Estrela (RS-130)
    (4311560, 4306403, 0.55),   # Lajeado - Encantado (RS-332)
    (4307625, 4306403, 0.50),   # Estrela - Encantado (RS-332)
    (4311560, 4322806, 0.65),   # Lajeado - Venâncio Aires (RS-130)
    (4322806, 4316709, 0.80),   # Venâncio Aires - Santa Cruz do Sul (RS-471)
    (4316709, 4306106, 0.55),   # Santa Cruz do Sul - Cruzeiro do Sul (RS-409)
    (4306106, 4320107, 0.45),   # Cruzeiro do Sul - Sinimbu (RS-409)
    (4306106, 4313300, 0.65),   # Cruzeiro do Sul - Novo Cabrais (RS-409)
    (4317202, 4313730, 0.40),   # São Sebastião - Passo do Sobrado (RS-122)
    (4313730, 4305207, 0.35),   # Passo do Sobrado - Charqueadas (RS-401)
]


def criar_grafo_rs() -> Grafo:
    """Constrói o grafo completo do RS com 30 municípios afetados."""
    grafo = Grafo()
    for m in MUNICIPIOS:
        grafo.adicionar_vertice(m)
    for id1, id2, peso in ARESTAS:
        grafo.adicionar_aresta(id1, id2, peso)
    return grafo


def criar_bst_rs(grafo: Grafo) -> BinarySearchTree:
    """Constrói a BST de municípios ordenada por índice de risco."""
    bst = BinarySearchTree()
    for municipio in grafo.vertices.values():
        bst.inserir(municipio)
    return bst


def criar_subgrafo_n_maior_risco(n: int) -> Grafo:
    """
    Retorna subgrafo CONECTADO com N municípios, priorizando os de maior risco.

    Selecionar simplesmente os N municípios de maior índice de risco pode gerar
    um subgrafo desconexo (eles podem não ser vizinhos entre si), inviabilizando
    o cálculo da MST pela Força Bruta. Por isso a expansão começa no município
    de maior risco e, a cada passo, anexa o vizinho de maior risco da fronteira
    de expansão — garantindo conectividade e mantendo o viés por criticidade.
    """
    grafo_completo = criar_grafo_rs()
    municipios_ordenados = sorted(
        grafo_completo.vertices.values(),
        key=lambda m: m[2],
        reverse=True,
    )
    inicio = municipios_ordenados[0][0]

    selecionados = {inicio}
    fronteira = {v for v, _ in grafo_completo.vizinhos(inicio)}

    while len(selecionados) < n and fronteira:
        candidatos = fronteira - selecionados
        if not candidatos:
            break
        proximo = max(candidatos, key=lambda v: grafo_completo.vertices[v][2])
        selecionados.add(proximo)
        fronteira.update(v for v, _ in grafo_completo.vizinhos(proximo))

    return grafo_completo.subgrafo(list(selecionados))


if __name__ == '__main__':
    grafo = criar_grafo_rs()
    bst = criar_bst_rs(grafo)
    print(grafo)
    print(f"BST: {len(bst)} nós, altura={bst.altura()}")
    print("\nTop 5 municípios por risco:")
    for m in bst.percurso_in_order()[-5:][::-1]:
        print(f"  {m[1]:25s} risco={m[2]:.2f}  pop={m[4]:>8,}")