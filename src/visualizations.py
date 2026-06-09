"""
Visualizações obrigatórias — Global Solution 2026.
Todas as figuras incluem título, legenda, fonte e interpretação.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.cm as cm
import networkx as nx


# ─────────────────────────────────────────────
# Figura 1: Grafo com MST destacada
# ─────────────────────────────────────────────

def plotar_grafo_mst(grafo, mst_arestas: list,
                     titulo: str = "Rede de Municípios do RS — MST de Resposta a Enchentes"):
    G = nx.Graph()
    mst_set = {(min(u, v), max(u, v)) for u, v, _ in mst_arestas}

    for id_v, dados in grafo.vertices.items():
        G.add_node(id_v, label=dados[1], risco=dados[2])

    for u, v in grafo._arestas_existentes:
        peso = next(p for vv, p in grafo.adjacencia[u] if vv == v)
        G.add_edge(u, v, weight=peso)

    fig, ax = plt.subplots(figsize=(15, 10))
    pos = nx.spring_layout(G, seed=42, k=2.5)

    riscos = [G.nodes[n]['risco'] for n in G.nodes()]
    norm = plt.Normalize(vmin=0, vmax=1)
    cmap = cm.RdYlGn_r

    nx.draw_networkx_nodes(G, pos, node_color=riscos, cmap=cmap,
                           vmin=0, vmax=1, node_size=500, ax=ax)

    arestas_normais = [(u, v) for u, v in G.edges()
                       if (min(u, v), max(u, v)) not in mst_set]
    arestas_mst = [(u, v) for u, v in G.edges()
                   if (min(u, v), max(u, v)) in mst_set]

    nx.draw_networkx_edges(G, pos, edgelist=arestas_normais,
                           edge_color='#cccccc', width=1.0, ax=ax)
    nx.draw_networkx_edges(G, pos, edgelist=arestas_mst,
                           edge_color='#c0392b', width=3.5, ax=ax)

    labels = {n: G.nodes[n]['label'][:12] for n in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=6, ax=ax)

    mst_weights = {(u, v): f"{G[u][v]['weight']:.1f}h"
                   for u, v in arestas_mst}
    nx.draw_networkx_edge_labels(G, pos, mst_weights, font_size=6, ax=ax)

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    plt.colorbar(sm, ax=ax, label='Índice de Risco (0 = baixo, 1 = crítico)', shrink=0.7)

    patch_mst = mpatches.Patch(color='#c0392b', label=f'Aresta MST ({len(mst_arestas)} rotas)')
    patch_out = mpatches.Patch(color='#cccccc', label='Rota não-MST')
    ax.legend(handles=[patch_mst, patch_out], loc='upper left', fontsize=9)

    ax.set_title(titulo, fontsize=14, fontweight='bold', pad=15)
    ax.axis('off')

    custo_mst = sum(w for _, _, w in mst_arestas)
    fig.text(0.5, 0.01,
             f'Fonte: Malha viária DNIT + Defesa Civil RS | '
             f'V={grafo.num_vertices} municípios, E={grafo.num_arestas} rodovias | '
             f'Custo MST={custo_mst:.2f}h deslocamento',
             ha='center', fontsize=8, style='italic', color='#555555')

    plt.tight_layout()
    return fig


# ─────────────────────────────────────────────
# Figura 2: Diagrama visual da BST
# ─────────────────────────────────────────────

def plotar_bst(bst, titulo: str = "BST — Municípios do RS por Índice de Risco"):
    if bst.root is None:
        return None

    # calcula posições de cada nó recursivamente
    posicoes = {}
    cmap = cm.RdYlGn_r

    def calcular_pos(node, x, y, dx):
        if node is None:
            return
        posicoes[node.id] = (x, y, node.risco, node.municipio[1])
        calcular_pos(node.left,  x - dx, y - 0.18, max(dx / 2, 0.02))
        calcular_pos(node.right, x + dx, y - 0.18, max(dx / 2, 0.02))

    calcular_pos(bst.root, 0.5, 0.92, 0.28)

    fig, ax = plt.subplots(figsize=(16, 9))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_title(titulo, fontsize=14, fontweight='bold')

    def desenhar(node):
        if node is None:
            return
        x, y, risco, nome = posicoes[node.id]
        cor = cmap(risco)
        circle = plt.Circle((x, y), 0.025, color=cor, zorder=3, ec='#333333', lw=0.8)
        ax.add_patch(circle)
        nome_curto = nome[:11]
        ax.text(x, y, f'{risco:.2f}', ha='center', va='center',
                fontsize=6, fontweight='bold', zorder=4, color='white')
        ax.text(x, y + 0.035, nome_curto, ha='center', va='bottom',
                fontsize=5.5, zorder=4)
        if node.left and node.left.id in posicoes:
            lx, ly, *_ = posicoes[node.left.id]
            ax.plot([x, lx], [y - 0.025, ly + 0.025], 'k-', lw=0.8, zorder=2)
        if node.right and node.right.id in posicoes:
            rx, ry, *_ = posicoes[node.right.id]
            ax.plot([x, rx], [y - 0.025, ry + 0.025], 'k-', lw=0.8, zorder=2)
        desenhar(node.left)
        desenhar(node.right)

    desenhar(bst.root)

    norm = plt.Normalize(0, 1)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    plt.colorbar(sm, ax=ax, label='Índice de Risco', shrink=0.5,
                 orientation='horizontal', pad=0.05)

    ax.text(0.5, 0.03,
            f'Fonte: Defesa Civil RS | BST com {len(bst)} nós | Altura={bst.altura()} | '
            f'Chave de ordenação: índice de risco (esquerda < pai < direita)',
            ha='center', fontsize=8, style='italic', color='#555555')

    plt.tight_layout()
    return fig


# ─────────────────────────────────────────────
# Figura 3: Desempenho Força Bruta 
# ─────────────────────────────────────────────

def plotar_desempenho(resultados: list,
                      titulo: str = "Desempenho Comparativo: Força Bruta vs Prim (Guloso)"):
    fb = [r for r in resultados if r.algoritmo == 'Força Bruta']
    gr = [r for r in resultados if r.algoritmo == 'Prim (Guloso)']

    fb_ns = [r.n for r in fb]
    fb_ts = [r.tempo_ms for r in fb]
    fb_ms = [r.memoria_mb for r in fb]

    gr_ns = [r.n for r in gr]
    gr_ts = [r.tempo_ms for r in gr]
    gr_ms = [r.memoria_mb for r in gr]

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    axes[0].plot(fb_ns, fb_ts, 'o-', color='#e74c3c', label='Força Bruta',
                 lw=2, ms=8, markerfacecolor='white', markeredgewidth=2)
    axes[0].plot(gr_ns, gr_ts, 's-', color='#27ae60', label='Prim (Guloso)',
                 lw=2, ms=8, markerfacecolor='white', markeredgewidth=2)
    axes[0].set_xlabel('N (número de vértices)', fontsize=11)
    axes[0].set_ylabel('Tempo de execução (ms)', fontsize=11)
    axes[0].set_title('Tempo × N', fontsize=12, fontweight='bold')
    axes[0].legend(fontsize=10)
    axes[0].grid(True, alpha=0.3)
    axes[0].set_yscale('log')

    axes[1].plot(fb_ns, fb_ms, 'o-', color='#e74c3c', label='Força Bruta',
                 lw=2, ms=8, markerfacecolor='white', markeredgewidth=2)
    axes[1].plot(gr_ns, gr_ms, 's-', color='#27ae60', label='Prim (Guloso)',
                 lw=2, ms=8, markerfacecolor='white', markeredgewidth=2)
    axes[1].set_xlabel('N (número de vértices)', fontsize=11)
    axes[1].set_ylabel('Memória alocada (MB)', fontsize=11)
    axes[1].set_title('Memória × N', fontsize=12, fontweight='bold')
    axes[1].legend(fontsize=10)
    axes[1].grid(True, alpha=0.3)

    fig.suptitle(titulo, fontsize=14, fontweight='bold')

    fonte = ('Fonte: Experimentos com grafos sinteticos | '
             'Forca Bruta restrita a N<=12 (explosao combinatoria)')
    fig.text(0.5, 0.01, fonte, ha='center', fontsize=7.5,
             style='italic', color='#555555')

    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    return fig




def plotar_gap_otimalidade(resultados: list,
                           titulo: str = "Gap de Otimalidade: Greedy (Prim) vs Solução Ótima (Força Bruta)"):
    fb_map = {r.n: r.custo_solucao for r in resultados if r.algoritmo == 'Força Bruta'}
    gr_map = {r.n: r.custo_solucao for r in resultados if r.algoritmo == 'Prim (Guloso)'}

    ns = sorted(set(fb_map) & set(gr_map))
    gaps = []
    for n in ns:
        if fb_map[n] > 0:
            gaps.append((gr_map[n] - fb_map[n]) / fb_map[n] * 100)
        else:
            gaps.append(0.0)

    fig, ax = plt.subplots(figsize=(10, 5))

    cores = ['#e74c3c' if g > 5 else '#f39c12' if g > 0.5 else '#27ae60' for g in gaps]
    bars = ax.bar(ns, gaps, color=cores, edgecolor='white', linewidth=0.5, width=0.6)

    max_gap = max(gaps) if gaps else 0
    # garante que o eixo Y tem sempre altura visível
    ax.set_ylim(-0.5, max(max_gap * 1.5 + 0.5, 2.0))

    for bar, gap in zip(bars, gaps):
        ax.text(bar.get_x() + bar.get_width() / 2,
                max(bar.get_height(), 0) + 0.05,
                f'{gap:.2f}%', ha='center', va='bottom', fontsize=9)

    ax.axhline(0, color='black', lw=1)
    ax.set_xlabel('N (numero de vertices)', fontsize=11)
    ax.set_ylabel('Gap de Otimalidade (%)', fontsize=11)
    ax.set_title(titulo, fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')

    patch_ok = mpatches.Patch(color='#27ae60', label='Gap <= 0.5% (quase otimo)')
    patch_warn = mpatches.Patch(color='#f39c12', label='0.5% < Gap <= 5%')
    patch_bad = mpatches.Patch(color='#e74c3c', label='Gap > 5%')
    ax.legend(handles=[patch_ok, patch_warn, patch_bad], fontsize=9, loc='upper right')

    fig.text(0.5, 0.01,
             'Gap = (custo_Prim - custo_otimo) / custo_otimo x 100% | '
             'Fonte: Experimentos com grafos sinteticos (semente=42)',
             ha='center', fontsize=8, style='italic', color='#555555')

    plt.tight_layout(rect=[0, 0.05, 1, 1])
    return fig




def plotar_explosao_combinatoria(dados_fb: dict,
                                 titulo: str = "Explosão Combinatória — Força Bruta vs Prim"):
    """
    dados_fb: {n: {'chamadas': int, 'tempo_ms': float}} para Força Bruta
    """
    ns = sorted(dados_fb.keys())
    chamadas = [dados_fb[n]['chamadas'] for n in ns]
    tempos_fb = [dados_fb[n]['tempo_ms'] for n in ns]

    fig, ax1 = plt.subplots(figsize=(10, 6))

    color1 = '#e74c3c'
    ax1.semilogy(ns, chamadas, 'o-', color=color1, lw=2, ms=8,
                 markerfacecolor='white', markeredgewidth=2, label='Chamadas recursivas (FB)')
    ax1.set_xlabel('N (número de vértices)', fontsize=11)
    ax1.set_ylabel('Nº de subconjuntos avaliados (escala log)', fontsize=10, color=color1)
    ax1.tick_params(axis='y', labelcolor=color1)

    ax2 = ax1.twinx()
    color2 = '#8e44ad'
    ax2.plot(ns, tempos_fb, 's--', color=color2, lw=2, ms=8,
             markerfacecolor='white', markeredgewidth=2, label='Tempo FB (ms)')
    ax2.set_ylabel('Tempo de execução (ms)', fontsize=10, color=color2)
    ax2.tick_params(axis='y', labelcolor=color2)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, fontsize=9, loc='upper left')

    ax1.set_title(titulo, fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)

    fig.text(0.5, 0.01,
             'A Força Bruta se torna inviável a partir de N≈10 (tempo exponencial C(|E|, N-1)). '
             'Prim resolve N=478 em milissegundos.',
             ha='center', fontsize=8, style='italic', color='#555555')

    plt.tight_layout()
    return fig