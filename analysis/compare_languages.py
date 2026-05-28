#!/usr/bin/env python3
"""
Comparative Analysis: TypeScript vs JavaScript
Análise comparativa de vulnerabilidades detectadas em projetos backend acadêmicos
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np

# Configuração
CSV_DIR = Path('./csv')
OUTPUT_DIR = Path('./csv')

# Cores para as linguagens
COLORS = {
    'TypeScript': '#2c3e50',
    'JavaScript': '#f39c12'
}

# ==================== CARREGAMENTO DE DADOS ====================
print("📥 Carregando dados...")

# AST Analysis
ast_ts = pd.read_csv(CSV_DIR / 'results_ast_analysis.csv')
ast_js = pd.read_csv(CSV_DIR / 'results_ast_analysis_javascript.csv')

# Audit Results
audit_ts = pd.read_csv(CSV_DIR / 'results_audit.csv')
audit_js = pd.read_csv(CSV_DIR / 'results_audit_javascript.csv')

# Mining (Repos Selecionados)
mining_ts = pd.read_csv(CSV_DIR / 'results_mining.csv')
mining_js = pd.read_csv(CSV_DIR / 'results_mining_javascript.csv')

print(f"✅ Dados carregados com sucesso!")

# ==================== CÁLCULO DE MÉTRICAS ====================
print("\n📊 Calculando métricas comparativas...\n")

metrics = {
    'TypeScript': {
        'repos': len(mining_ts),
        'vulnerabilities': len(ast_ts),
        'repos_with_vulns': ast_ts['Repo'].nunique() if not ast_ts.empty else 0,
        'audited': len(audit_ts),
        'detection_rate': (ast_ts['Repo'].nunique() / len(mining_ts) * 100) if not ast_ts.empty else 0,
    },
    'JavaScript': {
        'repos': len(mining_js),
        'vulnerabilities': len(ast_js),
        'repos_with_vulns': ast_js['Repo'].nunique() if not ast_js.empty else 0,
        'audited': len(audit_js),
        'detection_rate': (ast_js['Repo'].nunique() / len(mining_js) * 100) if not ast_js.empty else 0,
    }
}

# Imprimir resumo
for lang, data in metrics.items():
    print(f"\n🔹 {lang}:")
    print(f"   Repositórios analisados: {data['repos']}")
    print(f"   Vulnerabilidades encontradas: {data['vulnerabilities']}")
    print(f"   Repositórios com vulnerabilidades: {data['repos_with_vulns']}")
    print(f"   Taxa de detecção: {data['detection_rate']:.1f}%")
    print(f"   Vulnerabilidades auditadas: {data['audited']}")

# ==================== GRÁFICO 1: COMPARAÇÃO GERAL ====================
print("\n📊 Gerando gráficos de comparação...")

fig = plt.figure(figsize=(14, 10))
gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

# Gráfico 1: Repositórios e Vulnerabilidades
ax1 = fig.add_subplot(gs[0, 0])

categories = ['Repositórios\nAnalisados', 'Vulnerabilidades\nEncontradas', 'Reqs com\nVulnerabilidades']
ts_values = [metrics['TypeScript']['repos'], metrics['TypeScript']['vulnerabilities'], metrics['TypeScript']['repos_with_vulns']]
js_values = [metrics['JavaScript']['repos'], metrics['JavaScript']['vulnerabilities'], metrics['JavaScript']['repos_with_vulns']]

x = np.arange(len(categories))
width = 0.35

bars1 = ax1.bar(x - width/2, ts_values, width, label='TypeScript', color=COLORS['TypeScript'], alpha=0.8, edgecolor='black', linewidth=1.5)
bars2 = ax1.bar(x + width/2, js_values, width, label='JavaScript', color=COLORS['JavaScript'], alpha=0.8, edgecolor='black', linewidth=1.5)

ax1.set_ylabel('Quantidade', fontsize=11, fontweight='bold')
ax1.set_title('Comparação: Repositórios e Vulnerabilidades Encontradas', fontsize=13, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(categories, fontsize=10)
ax1.legend(fontsize=10, loc='upper left')
ax1.grid(axis='y', alpha=0.3, linestyle='--')

# Adicionar valores nas barras
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=9, fontweight='bold')

# Gráfico 2: Taxa de Detecção
ax2 = fig.add_subplot(gs[0, 1])

languages = ['TypeScript', 'JavaScript']
detection_rates = [metrics['TypeScript']['detection_rate'], metrics['JavaScript']['detection_rate']]
colors_list = [COLORS['TypeScript'], COLORS['JavaScript']]

bars = ax2.bar(languages, detection_rates, color=colors_list, alpha=0.8, edgecolor='black', linewidth=2)
ax2.set_ylabel('Taxa de Detecção (%)', fontsize=11, fontweight='bold')
ax2.set_title('Taxa de Repositórios com Vulnerabilidades', fontsize=13, fontweight='bold')
ax2.set_ylim(0, 100)
ax2.grid(axis='y', alpha=0.3, linestyle='--')

# Adicionar valores nas barras
for bar, rate in zip(bars, detection_rates):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height,
            f'{rate:.1f}%',
            ha='center', va='bottom', fontsize=11, fontweight='bold')

# Gráfico 3: Distribuição de Tipos de Vulnerabilidade - TypeScript
ax3 = fig.add_subplot(gs[1, 0])

if not ast_ts.empty:
    vuln_types_ts = ast_ts['Type'].value_counts()
    colors_pie = plt.cm.Set3(range(len(vuln_types_ts)))
    
    wedges, texts, autotexts = ax3.pie(vuln_types_ts.values,
                                         labels=vuln_types_ts.index,
                                         autopct='%1.1f%%',
                                         colors=colors_pie,
                                         startangle=90,
                                         textprops={'fontsize': 9})
    
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    ax3.set_title(f'TypeScript: Tipos de Vulnerabilidade (n={len(vuln_types_ts)})', fontsize=12, fontweight='bold')
else:
    ax3.text(0.5, 0.5, 'Sem dados', ha='center', va='center', fontsize=12)

# Gráfico 4: Distribuição de Tipos de Vulnerabilidade - JavaScript
ax4 = fig.add_subplot(gs[1, 1])

if not ast_js.empty:
    vuln_types_js = ast_js['Type'].value_counts()
    colors_pie = plt.cm.Set3(range(len(vuln_types_js)))
    
    wedges, texts, autotexts = ax4.pie(vuln_types_js.values,
                                         labels=vuln_types_js.index,
                                         autopct='%1.1f%%',
                                         colors=colors_pie,
                                         startangle=90,
                                         textprops={'fontsize': 9})
    
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    ax4.set_title(f'JavaScript: Tipos de Vulnerabilidade (n={len(vuln_types_js)})', fontsize=12, fontweight='bold')
else:
    ax4.text(0.5, 0.5, 'Sem dados', ha='center', va='center', fontsize=12)

plt.savefig(OUTPUT_DIR / 'comparacao_linguagens_1.png', dpi=300, bbox_inches='tight')
print("✅ Gráfico 1 salvo: comparacao_linguagens_1.png")
plt.close()

# ==================== GRÁFICO 2: RESULTADOS DA AUDITORIA ====================
fig = plt.figure(figsize=(14, 8))
gs = fig.add_gridspec(1, 2, hspace=0.3, wspace=0.3)

# Preparar dados de auditoria
status_order = ['CORRETO', 'INCORRETO', 'NAO_SE_APLICA', 'DEPENDE']
colors_status = {
    'CORRETO': '#27ae60',
    'INCORRETO': '#e74c3c',
    'NAO_SE_APLICA': '#95a5a6',
    'DEPENDE': '#f39c12'
}

# TypeScript
ax1 = fig.add_subplot(gs[0, 0])
if not audit_ts.empty:
    status_ts = audit_ts['Status'].value_counts().reindex(status_order, fill_value=0)
    bar_colors_ts = [colors_status.get(s, '#34495e') for s in status_ts.index]
    
    bars = ax1.barh(status_ts.index, status_ts.values, color=bar_colors_ts, alpha=0.8, edgecolor='black', linewidth=1.5)
    ax1.set_xlabel('Quantidade', fontsize=11, fontweight='bold')
    ax1.set_title('TypeScript: Resultado da Auditoria Manual', fontsize=12, fontweight='bold')
    ax1.grid(axis='x', alpha=0.3, linestyle='--')
    
    # Adicionar valores nas barras
    for bar in bars:
        width = bar.get_width()
        ax1.text(width, bar.get_y() + bar.get_height()/2.,
                f' {int(width)}',
                ha='left', va='center', fontsize=10, fontweight='bold')
else:
    ax1.text(0.5, 0.5, 'Sem dados de auditoria', ha='center', va='center', fontsize=11)
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)

# JavaScript
ax2 = fig.add_subplot(gs[0, 1])
if not audit_js.empty:
    status_js = audit_js['Status'].value_counts().reindex(status_order, fill_value=0)
    bar_colors_js = [colors_status.get(s, '#34495e') for s in status_js.index]
    
    bars = ax2.barh(status_js.index, status_js.values, color=bar_colors_js, alpha=0.8, edgecolor='black', linewidth=1.5)
    ax2.set_xlabel('Quantidade', fontsize=11, fontweight='bold')
    ax2.set_title('JavaScript: Resultado da Auditoria Manual', fontsize=12, fontweight='bold')
    ax2.grid(axis='x', alpha=0.3, linestyle='--')
    
    # Adicionar valores nas barras
    for bar in bars:
        width = bar.get_width()
        ax2.text(width, bar.get_y() + bar.get_height()/2.,
                f' {int(width)}',
                ha='left', va='center', fontsize=10, fontweight='bold')
else:
    ax2.text(0.5, 0.5, 'Sem dados de auditoria', ha='center', va='center', fontsize=11)
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)

plt.savefig(OUTPUT_DIR / 'comparacao_linguagens_2_auditoria.png', dpi=300, bbox_inches='tight')
print("✅ Gráfico 2 salvo: comparacao_linguagens_2_auditoria.png")
plt.close()

# ==================== GRÁFICO 3: CONTAGEM DE VULNERABILIDADES POR TIPO ====================
fig = plt.figure(figsize=(14, 8))
ax = fig.add_subplot(111)

if not ast_ts.empty and not ast_js.empty:
    # Obter todos os tipos únicos
    all_types = sorted(set(ast_ts['Type'].unique()) | set(ast_js['Type'].unique()))
    
    ts_counts = ast_ts['Type'].value_counts()
    js_counts = ast_js['Type'].value_counts()
    
    ts_values = [ts_counts.get(t, 0) for t in all_types]
    js_values = [js_counts.get(t, 0) for t in all_types]
    
    x = np.arange(len(all_types))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, ts_values, width, label='TypeScript', color=COLORS['TypeScript'], alpha=0.8, edgecolor='black', linewidth=1.5)
    bars2 = ax.bar(x + width/2, js_values, width, label='JavaScript', color=COLORS['JavaScript'], alpha=0.8, edgecolor='black', linewidth=1.5)
    
    ax.set_ylabel('Quantidade de Vulnerabilidades', fontsize=12, fontweight='bold')
    ax.set_title('Comparação: Vulnerabilidades por Tipo', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(all_types, fontsize=10, rotation=45, ha='right')
    ax.legend(fontsize=11, loc='upper right')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Adicionar valores nas barras
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}',
                        ha='center', va='bottom', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'comparacao_linguagens_3_tipos.png', dpi=300, bbox_inches='tight')
print("✅ Gráfico 3 salvo: comparacao_linguagens_3_tipos.png")
plt.close()

# ==================== GRÁFICO 4: RESUMO EXECUTIVO ====================
fig = plt.figure(figsize=(14, 6))
ax = fig.add_subplot(111)
ax.axis('off')

# Criar tabela de comparação
summary_data = {
    'Métrica': [
        'Repositórios Analisados',
        'Vulnerabilidades Encontradas',
        'Repositórios com Vulnerabilidades',
        'Taxa de Detecção',
        'Vulnerabilidades Auditadas'
    ],
    'TypeScript': [
        f"{metrics['TypeScript']['repos']}",
        f"{metrics['TypeScript']['vulnerabilities']}",
        f"{metrics['TypeScript']['repos_with_vulns']}",
        f"{metrics['TypeScript']['detection_rate']:.1f}%",
        f"{metrics['TypeScript']['audited']}"
    ],
    'JavaScript': [
        f"{metrics['JavaScript']['repos']}",
        f"{metrics['JavaScript']['vulnerabilities']}",
        f"{metrics['JavaScript']['repos_with_vulns']}",
        f"{metrics['JavaScript']['detection_rate']:.1f}%",
        f"{metrics['JavaScript']['audited']}"
    ]
}

summary_df = pd.DataFrame(summary_data)

# Criar tabela
table = ax.table(cellText=summary_df.values, 
                colLabels=summary_df.columns,
                cellLoc='center',
                loc='center',
                colWidths=[0.35, 0.25, 0.25])

table.auto_set_font_size(False)
table.set_fontsize(11)
table.scale(1, 2.5)

# Estilizar cabeçalho
for i in range(len(summary_df.columns)):
    cell = table[(0, i)]
    cell.set_facecolor('#2c3e50')
    cell.set_text_props(weight='bold', color='white')

# Estilizar linhas alternadas
for i in range(1, len(summary_df) + 1):
    for j in range(len(summary_df.columns)):
        cell = table[(i, j)]
        if i % 2 == 0:
            cell.set_facecolor('#ecf0f1')
        else:
            cell.set_facecolor('#ffffff')

plt.title('Resumo Comparativo: TypeScript vs JavaScript', fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'comparacao_linguagens_4_resumo.png', dpi=300, bbox_inches='tight')
print("✅ Gráfico 4 salvo: comparacao_linguagens_4_resumo.png")
plt.close()

# ==================== RELATÓRIO TEXTUAL ====================
print("\n" + "="*70)
print("📋 RELATÓRIO DE COMPARAÇÃO: TYPESCRIPT VS JAVASCRIPT")
print("="*70)

print("\n🔹 ANÁLISE DE REPOSITÓRIOS:")
print(f"   • TypeScript: {metrics['TypeScript']['repos']} repositórios")
print(f"   • JavaScript: {metrics['JavaScript']['repos']} repositórios")
diff_repos = metrics['TypeScript']['repos'] - metrics['JavaScript']['repos']
print(f"   • Diferença: {abs(diff_repos)} repositórios ({'TS' if diff_repos > 0 else 'JS'} tem mais)")

print("\n🔹 ANÁLISE DE VULNERABILIDADES DETECTADAS:")
print(f"   • TypeScript: {metrics['TypeScript']['vulnerabilities']} vulnerabilidades")
print(f"   • JavaScript: {metrics['JavaScript']['vulnerabilities']} vulnerabilidades")
diff_vulns = metrics['TypeScript']['vulnerabilities'] - metrics['JavaScript']['vulnerabilities']
print(f"   • Diferença: {abs(diff_vulns)} vulnerabilidades ({'TS' if diff_vulns > 0 else 'JS'} tem mais)")

print("\n🔹 TAXA DE DETECÇÃO:")
print(f"   • TypeScript: {metrics['TypeScript']['detection_rate']:.1f}%")
print(f"   • JavaScript: {metrics['JavaScript']['detection_rate']:.1f}%")
diff_rate = metrics['TypeScript']['detection_rate'] - metrics['JavaScript']['detection_rate']
print(f"   • Diferença: {abs(diff_rate):.1f}% ({'TS' if diff_rate > 0 else 'JS'} tem taxa maior)")

print("\n🔹 VULNERABILIDADES AUDITADAS:")
print(f"   • TypeScript: {metrics['TypeScript']['audited']} auditadas")
print(f"   • JavaScript: {metrics['JavaScript']['audited']} auditadas")

print("\n" + "="*70)
print("✅ Análise concluída com sucesso!")
print("="*70)
print("\n📊 Gráficos gerados:")
print("   1. comparacao_linguagens_1.png - Comparação geral")
print("   2. comparacao_linguagens_2_auditoria.png - Resultados da auditoria")
print("   3. comparacao_linguagens_3_tipos.png - Vulnerabilidades por tipo")
print("   4. comparacao_linguagens_4_resumo.png - Resumo executivo")
print("\n")
