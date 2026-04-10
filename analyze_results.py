import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from pathlib import Path
from collections import Counter

# Configurar estilo
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10

# Caminhos dos CSVs
BASE_DIR = Path(__file__).parent
CSV_DIR = BASE_DIR / "csv"

MINING_CSV = CSV_DIR / "results_mining_javascript.csv"
AST_CSV = CSV_DIR / "results_ast_analysis_javascript.csv"
AUDIT_CSV = CSV_DIR / "results_audit_javascript.csv"

# ==================== CARREGAMENTO DOS DADOS ====================
print("=" * 80)
print("📊 VulnSniffer - Análise Completa de Resultados")
print("=" * 80)

# Carregar CSVs
try:
    mining_df = pd.read_csv(MINING_CSV) if MINING_CSV.exists() else pd.DataFrame()
    ast_df = pd.read_csv(AST_CSV) if AST_CSV.exists() else pd.DataFrame()
    audit_df = pd.read_csv(AUDIT_CSV) if AUDIT_CSV.exists() else pd.DataFrame()
    
    print("\n✅ CSVs carregados com sucesso!")
except Exception as e:
    print(f"❌ Erro ao carregar CSVs: {e}")
    exit(1)

# ==================== ESTATÍSTICAS GERAIS ====================
print("\n" + "=" * 80)
print("📈 ESTATÍSTICAS GERAIS DO PIPELINE")
print("=" * 80)

total_repos_mining = len(mining_df)
total_findings_ast = len(ast_df)
total_audited = len(audit_df)

print(f"\n📌 MINING (Seleção de Repositórios):")
print(f"   Total de repositórios selecionados: {total_repos_mining}")

print(f"\n📌 AST ANALYSIS (Detecção de Vulnerabilidades):")
print(f"   Total de vulnerabilidades encontradas: {total_findings_ast}")
repos_with_vulns = ast_df['Repo'].nunique() if not ast_df.empty else 0
print(f"   Repositórios com vulnerabilidades: {repos_with_vulns}")
print(f"   Taxa de detecção: {(repos_with_vulns/total_repos_mining*100):.1f}% dos repositórios")

print(f"\n📌 AUDIT (Análise Manual):")
print(f"   Total de vulnerabilidades auditadas: {total_audited}")

if not audit_df.empty:
    status_counts = audit_df['Status'].value_counts()
    print(f"   Status de Classificação:")
    for status, count in status_counts.items():
        percentage = (count / total_audited * 100)
        print(f"      • {status}: {count} ({percentage:.1f}%)")

# ==================== GRÁFICO 1: FUNIL DO PIPELINE ====================
print("\n📊 Gerando gráficos...")

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Gráfico 1: Funil do Pipeline
ax1 = axes[0, 0]
stages = ['Repositórios\nSelecionados\n(Mining)', 
          'Vulnerabilidades\nDetectadas\n(AST)', 
          'Vulnerabilidades\nAuditadas\n(Manual)']
values = [total_repos_mining, total_findings_ast, total_audited]
colors = ['#3498db', '#e74c3c', '#f39c12']

bars = ax1.bar(stages, values, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
ax1.set_ylabel('Quantidade', fontsize=12, fontweight='bold')
ax1.set_title('Funil do Pipeline de Análise', fontsize=14, fontweight='bold')
ax1.set_ylim(0, max(values) * 1.1)

# Adicionar valores nas barras
for i, (bar, value) in enumerate(zip(bars, values)):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(value)}',
            ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # Adicionar taxa de filtro
    if i > 0:
        taxa = (values[i] / values[i-1] * 100)
        ax1.text(bar.get_x() + bar.get_width()/2., height * 0.5,
                f'{taxa:.1f}%',
                ha='center', va='center', fontsize=10, 
                color='white', fontweight='bold')

# ==================== GRÁFICO 2: DISTRIBUIÇÃO POR TIPO DE VULNERABILIDADE ====================
ax2 = axes[0, 1]

if not ast_df.empty:
    vuln_types = ast_df['Type'].value_counts()
    colors_vuln = plt.cm.Set3(range(len(vuln_types)))
    
    wedges, texts, autotexts = ax2.pie(vuln_types.values, 
                                         labels=vuln_types.index,
                                         autopct='%1.1f%%',
                                         colors=colors_vuln,
                                         startangle=90,
                                         textprops={'fontsize': 10})
    
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    ax2.set_title('Distribuição de Tipos de Vulnerabilidade (AST)', 
                  fontsize=14, fontweight='bold')
    
    # Adicionar legenda com contagens
    legend_labels = [f'{t}: {c}' for t, c in vuln_types.items()]
    ax2.legend(legend_labels, loc='upper left', bbox_to_anchor=(1.0, 1.0), fontsize=9)

# ==================== GRÁFICO 3: CLASSIFICAÇÃO DO AUDIT ====================
ax3 = axes[1, 0]

if not audit_df.empty:
    status_counts = audit_df['Status'].value_counts()
    colors_status = {
        'CORRETO': '#27ae60',
        'INCORRETO': '#e74c3c',
        'NAO_SE_APLICA': '#95a5a6',
        'DEPENDE': '#f39c12'
    }
    
    bar_colors = [colors_status.get(status, '#34495e') for status in status_counts.index]
    bars = ax3.barh(status_counts.index, status_counts.values, color=bar_colors, 
                     alpha=0.8, edgecolor='black', linewidth=2)
    
    ax3.set_xlabel('Quantidade', fontsize=12, fontweight='bold')
    ax3.set_title('✅ Resultado da Auditoria Manual', fontsize=14, fontweight='bold')
    
    # Adicionar valores nas barras
    for bar in bars:
        width = bar.get_width()
        ax3.text(width, bar.get_y() + bar.get_height()/2.,
                f' {int(width)}',
                ha='left', va='center', fontsize=11, fontweight='bold')
else:
    ax3.text(0.5, 0.5, 'Nenhum dado de auditoria disponível', 
            ha='center', va='center', fontsize=12)
    ax3.set_xlim(0, 1)
    ax3.set_ylim(0, 1)

# ==================== GRÁFICO 4: TOP 10 VULNERABILIDADES POR REPOSITÓRIO ====================
ax4 = axes[1, 1]

if not ast_df.empty:
    repos_vuln_count = ast_df['Repo'].value_counts().head(10)
    
    bars = ax4.barh(range(len(repos_vuln_count)), repos_vuln_count.values, 
                     color='#e74c3c', alpha=0.7, edgecolor='black', linewidth=1.5)
    ax4.set_yticks(range(len(repos_vuln_count)))
    ax4.set_yticklabels(repos_vuln_count.index, fontsize=9)
    ax4.set_xlabel('Quantidade de Vulnerabilidades', fontsize=12, fontweight='bold')
    ax4.set_title('Top 10 Repositórios com Mais Vulnerabilidades', 
                  fontsize=14, fontweight='bold')
    ax4.invert_yaxis()
    
    # Adicionar valores nas barras
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax4.text(width, bar.get_y() + bar.get_height()/2.,
                f' {int(width)}',
                ha='left', va='center', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig(CSV_DIR / 'analise_completa_1_javascript.png', dpi=300, bbox_inches='tight')
print("✅ Gráfico 1 salvo: analise_completa_1_javascript.png")

# ==================== SEGUNDA PÁGINA DE GRÁFICOS ====================
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# ==================== GRÁFICO 5: VULNERABILIDADES POR TIPO (BAR CHART) ====================
ax1 = axes[0, 0]

if not ast_df.empty:
    vuln_types = ast_df['Type'].value_counts()
    colors_bar = plt.cm.Set2(range(len(vuln_types)))
    
    bars = ax1.bar(range(len(vuln_types)), vuln_types.values, 
                    color=colors_bar, alpha=0.8, edgecolor='black', linewidth=2)
    ax1.set_xticks(range(len(vuln_types)))
    ax1.set_xticklabels(vuln_types.index, rotation=45, ha='right')
    ax1.set_ylabel('Quantidade', fontsize=12, fontweight='bold')
    ax1.set_title('Ranking de Tipos de Vulnerabilidade', fontsize=14, fontweight='bold')
    
    # Adicionar valores nas barras
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')

# ==================== GRÁFICO 6: TAXA DE ACURÁCIA DO AST ====================
ax2 = axes[0, 1]

if not audit_df.empty:
    corretos = len(audit_df[audit_df['Status'] == 'CORRETO'])
    incorretos = len(audit_df[audit_df['Status'] == 'INCORRETO'])
    nao_aplica = len(audit_df[audit_df['Status'] == 'NAO_SE_APLICA'])
    depende = len(audit_df[audit_df['Status'] == 'DEPENDE'])
    
    total_classified = corretos + incorretos + nao_aplica + depende
    
    if total_classified > 0:
        # Calcular acurácia (considerando CORRETO como verdadeiro positivo)
        accuracy = (corretos / total_classified * 100)
        false_positive_rate = (incorretos / total_classified * 100)
        
        categories = ['Verdadeiros\nPositivos\n(CORRETO)', 
                     'Falsos\nPositivos\n(INCORRETO)',
                     'Fora do\nEscopo\n(NAO_SE_APLICA)',
                     'Pendentes\n(DEPENDE)']
        values_acc = [corretos, incorretos, nao_aplica, depende]
        colors_acc = ['#27ae60', '#e74c3c', '#95a5a6', '#f39c12']
        
        bars = ax2.bar(categories, values_acc, color=colors_acc, alpha=0.8, 
                       edgecolor='black', linewidth=2)
        ax2.set_ylabel('Quantidade', fontsize=12, fontweight='bold')
        ax2.set_title('Análise de Acurácia do Scanner AST', fontsize=14, fontweight='bold')
        
        # Adicionar valores
        for bar, value in zip(bars, values_acc):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(value)}',
                    ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        # Adicionar taxa de acurácia como texto
        ax2.text(0.5, 0.95, f'Taxa de Acurácia: {accuracy:.1f}% | Taxa de Falsos Positivos: {false_positive_rate:.1f}%',
                transform=ax2.transAxes, ha='center', va='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
                fontsize=11, fontweight='bold')

# ==================== GRÁFICO 7: MATRIZ DE CORRELAÇÃO (TIPO vs STATUS) ====================
ax3 = axes[1, 0]

if not audit_df.empty and len(audit_df['Type'].unique()) > 1:
    # Criar tabela de cruzamento: Tipo de Vulnerabilidade x Status
    crosstab = pd.crosstab(audit_df['Type'], audit_df['Status'])
    
    # Normalizando por linha (percentual dentro de cada tipo)
    crosstab_pct = crosstab.div(crosstab.sum(axis=1), axis=0) * 100
    
    im = ax3.imshow(crosstab_pct.values, cmap='RdYlGn', aspect='auto')
    
    ax3.set_xticks(range(len(crosstab_pct.columns)))
    ax3.set_yticks(range(len(crosstab_pct.index)))
    ax3.set_xticklabels(crosstab_pct.columns, rotation=45, ha='right')
    ax3.set_yticklabels(crosstab_pct.index)
    
    ax3.set_title('Matriz de Correlação: Tipo vs Status (%)', 
                  fontsize=14, fontweight='bold')
    
    # Adicionar valores na matriz
    for i in range(len(crosstab_pct.index)):
        for j in range(len(crosstab_pct.columns)):
            text = ax3.text(j, i, f'{crosstab_pct.values[i, j]:.0f}%',
                           ha="center", va="center", color="black", fontsize=9, fontweight='bold')
    
    plt.colorbar(im, ax=ax3, label='Percentual (%)')

# ==================== GRÁFICO 8: COMPARAÇÃO ANTES/DEPOIS DO AUDIT ====================
ax4 = axes[1, 1]

if not audit_df.empty:
    # Repositórios antes (from AST)
    repos_ast = ast_df['Repo'].nunique() if not ast_df.empty else 0
    
    # Repositórios confirmados como vulneráveis (CORRETO)
    repos_corretos = audit_df[audit_df['Status'] == 'CORRETO']['Repo'].nunique()
    
    # Repositórios descartados (INCORRETO + NAO_SE_APLICA)
    repos_descartados = audit_df[audit_df['Status'].isin(['INCORRETO', 'NAO_SE_APLICA'])]['Repo'].nunique()
    
    categories = ['Repositórios\ncom Vulns\n(AST)', 
                  'Confirmados\nVerdadeiros\n(CORRETO)',
                  'Descartados\n(INCORRETO +\nNAO_SE_APLICA)']
    values_repos = [repos_ast, repos_corretos, repos_descartados]
    colors_repos = ['#3498db', '#27ae60', '#e74c3c']
    
    bars = ax4.bar(categories, values_repos, color=colors_repos, alpha=0.8, 
                   edgecolor='black', linewidth=2)
    ax4.set_ylabel('Quantidade de Repositórios', fontsize=12, fontweight='bold')
    ax4.set_title('Comparação de Repositórios Afetados', fontsize=14, fontweight='bold')
    ax4.set_ylim(0, max(values_repos) * 1.15)
    
    # Adicionar valores
    for bar, value in zip(bars, values_repos):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(value)}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # Adicionar percentuais de filtro
    if repos_ast > 0:
        pct_confirmados = (repos_corretos / repos_ast * 100)
        ax4.text(0.5, 0.85, f'Confirmação: {pct_confirmados:.1f}% | Descarte: {100-pct_confirmados:.1f}%',
                transform=ax4.transAxes, ha='center', va='top',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7),
                fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig(CSV_DIR / 'analise_completa_2_javascript.png', dpi=300, bbox_inches='tight')
print("✅ Gráfico 2 salvo: analise_completa_2_javascript.png")

# ==================== RELATÓRIO DETALHADO ====================
print("\n" + "=" * 80)
print("📋 RELATÓRIO DETALHADO DE ANÁLISES")
print("=" * 80)

print("\n🔍 TIPO DE VULNERABILIDADES ENCONTRADAS (AST):")
if not ast_df.empty:
    for i, (vuln_type, count) in enumerate(ast_df['Type'].value_counts().items(), 1):
        pct = (count / len(ast_df) * 100)
        print(f"   {i}. {vuln_type}: {count} ({pct:.1f}%)")

print("\n📊 DISTRIBUIÇÃO DE STATUS (AUDIT):")
if not audit_df.empty:
    for status, count in audit_df['Status'].value_counts().items():
        pct = (count / len(audit_df) * 100)
        print(f"   • {status}: {count} ({pct:.1f}%)")

print("\n🎯 ANÁLISE POR TIPO DE VULNERABILIDADE (AUDIT):")
if not audit_df.empty:
    for vuln_type in audit_df['Type'].unique():
        type_data = audit_df[audit_df['Type'] == vuln_type]
        print(f"\n   {vuln_type}:")
        print(f"      Total: {len(type_data)}")
        status_breakdown = type_data['Status'].value_counts()
        for status, count in status_breakdown.items():
            pct = (count / len(type_data) * 100)
            print(f"         • {status}: {count} ({pct:.1f}%)")

print("\n📈 ESTATÍSTICAS FINAIS:")
print(f"   Taxa de Filtragem Total: {((total_repos_mining - repos_with_vulns) / total_repos_mining * 100):.1f}%")
print(f"      ({total_repos_mining - repos_with_vulns} repositórios sem vulnerabilidades encontradas)")

if not audit_df.empty:
    taxa_confirmacao = (corretos / total_audited * 100) if total_audited > 0 else 0
    taxa_descarte = ((incorretos + nao_aplica) / total_audited * 100) if total_audited > 0 else 0
    print(f"\n   Taxa de Confirmação (Vulnerabilidades Reais): {taxa_confirmacao:.1f}%")
    print(f"   Taxa de Descarte (Falsos Positivos + Fora do Escopo): {taxa_descarte:.1f}%")
    
    if repos_ast > 0:
        print(f"\n   Repositórios Afetados por Vulnerabilidades Confirmadas: {repos_corretos}")
        print(f"   Repositórios com Falsos Positivos: {repos_descartados}")

print("\n" + "=" * 80)
print("✨ Análise concluída! Verifique os gráficos em: csv/")
print("=" * 80)
