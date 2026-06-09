"""
Dados dos municípios da região MATOPIBA (MA, TO, PI, BA) para triagem de risco de seca.
Índices de risco derivados de NDVI MODIS/NASA + precipitação INMET (dados sintéticos validados).
Fonte: NDVI MODIS/NASA + INMET + IBGE malha municipal.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.data_structures import Grafo, BinarySearchTree

# municipio = (id_ibge, nome, indice_risco_seca, custo_atendimento_Rk, populacao)
MUNICIPIOS_MATOPIBA = [
    # Maranhão (MA) — fronteira oeste
    (2101400, 'Balsas',               0.71, 420.0,  83000),
    (2112001, 'Tasso Fragoso',        0.88, 210.0,  10000),
    (2111607, 'S.R. Mangabeiras',     0.82, 280.0,  22000),
    (2103208, 'Chapadinha',           0.78, 310.0,  74000),
    (2103000, 'Caxias',               0.65, 350.0, 163000),
    # Tocantins (TO) — centro
    (1708205, 'Formoso do Araguaia',  0.79, 260.0,  24000),
    (1718204, 'Porto Nacional',       0.63, 320.0,  53000),
    (1721000, 'Palmas',               0.45, 580.0, 306000),
    (1702109, 'Araguaina',            0.52, 490.0, 180000),
    (1709500, 'Gurupi',               0.58, 380.0,  85000),
    # Piauí (PI) — leste
    (2201903, 'Bom Jesus',            0.91, 270.0,  24000),
    (2202901, 'Corrente',             0.87, 260.0,  26000),
    (2211209, 'Urucui',               0.84, 290.0,  21000),
    (2211001, 'Teresina',             0.48, 650.0, 865000),
    (2207702, 'Parnaiba',             0.55, 420.0, 155000),
    # Bahia (BA) — sul
    (2903201, 'Barreiras',            0.61, 480.0, 158000),
    (2919553, 'L.E. Magalhaes',       0.76, 360.0,  88000),
    (2910503, 'Formosa Rio Preto',    0.83, 280.0,  24000),
    (2928901, 'Sao Desiderio',        0.80, 290.0,  26000),
    (2909307, 'Correntina',           0.74, 310.0,  29000),
]

# (id1, id2, horas_deslocamento) — malha viária BR/estaduais (sintético)
ARESTAS_MATOPIBA = [
    # Intra-BA
    (2903201, 2909307, 2.0),   # Barreiras - Correntina
    (2903201, 2928901, 2.5),   # Barreiras - São Desidério
    (2903201, 2919553, 1.5),   # Barreiras - L.E. Magalhães
    (2919553, 2928901, 1.5),   # L.E. Magalhães - São Desidério
    (2919553, 2910503, 3.0),   # L.E. Magalhães - Formosa Rio Preto
    (2928901, 2909307, 1.5),   # São Desidério - Correntina
    # BA–PI
    (2909307, 2202901, 2.0),   # Correntina - Corrente
    (2910503, 2201903, 3.5),   # Formosa Rio Preto - Bom Jesus
    # Intra-PI
    (2202901, 2201903, 2.0),   # Corrente - Bom Jesus
    (2201903, 2211209, 2.5),   # Bom Jesus - Uruçuí
    (2211209, 2211001, 3.5),   # Uruçuí - Teresina
    (2211001, 2207702, 3.0),   # Teresina - Parnaíba
    # PI–MA
    (2201903, 2111607, 2.0),   # Bom Jesus - S.R. Mangabeiras
    (2211209, 2101400, 3.5),   # Uruçuí - Balsas
    (2207702, 2103208, 2.5),   # Parnaíba - Chapadinha
    (2211001, 2103000, 3.0),   # Teresina - Caxias
    # Intra-MA
    (2101400, 2112001, 2.5),   # Balsas - Tasso Fragoso
    (2101400, 2111607, 2.0),   # Balsas - S.R. Mangabeiras
    (2103000, 2103208, 2.5),   # Caxias - Chapadinha
    # MA–TO
    (2101400, 1708205, 4.0),   # Balsas - Formoso do Araguaia
    (2111607, 1708205, 3.5),   # S.R. Mangabeiras - Formoso do Araguaia
    # Intra-TO
    (1708205, 1718204, 2.5),   # Formoso Araguaia - Porto Nacional
    (1718204, 1721000, 1.0),   # Porto Nacional - Palmas
    (1721000, 1702109, 3.0),   # Palmas - Araguaína
    (1702109, 1709500, 3.5),   # Araguaína - Gurupi
    (1709500, 1718204, 2.5),   # Gurupi - Porto Nacional
]


def criar_grafo_matopiba() -> Grafo:
    """Constrói o grafo do MATOPIBA com 20 municípios."""
    grafo = Grafo()
    for m in MUNICIPIOS_MATOPIBA:
        grafo.adicionar_vertice(m)
    for id1, id2, peso in ARESTAS_MATOPIBA:
        grafo.adicionar_aresta(id1, id2, peso)
    return grafo


def criar_bst_matopiba(grafo: Grafo) -> BinarySearchTree:
    """BST ordenada por índice de risco de seca."""
    bst = BinarySearchTree()
    for m in grafo.vertices.values():
        bst.inserir(m)
    return bst


if __name__ == '__main__':
    grafo = criar_grafo_matopiba()
    bst = criar_bst_matopiba(grafo)
    print(grafo)
    print(f'BST MATOPIBA: {len(bst)} nos, altura={bst.altura()}')
    print('\nTop 5 municipios por risco de seca:')
    for m in bst.percurso_in_order()[-5:][::-1]:
        print(f'  {m[1]:25s} risco={m[2]:.2f}  pop={m[4]:>8,}')