import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Carregar os dois estados dos dados
df_ast = pd.read_csv('../csv/results_ast_analysis_limpo.csv')
df_audit = pd.read_csv('../csv/results_audit_limpo.csv')

# Contar alertas iniciais encontrados pela AST
ast_counts = df_ast['Type'].value_counts()

# Contar apenas os confirmados na auditoria manual
audit_confirmados = df_audit[df_audit['Status'] == 'CORRETO']['Type'].value_counts()

# Alinhar os indexes para garantir que as categorias batam perfeitamente
categorias = ast_counts.index.union(audit_confirmados.index)
valores_ast = [ast_counts.get(cat, 0) for cat in categorias]
valores_audit = [audit_confirmados.get(cat, 0) for cat in categorias]

x = np.arange(len(categorias))
largura = 0.35

fig, ax = plt.subplots(figsize=(12, 7))
barra_ast = ax.bar(x - largura/2, valores_ast, largura, label='Alertas Brutos (AST)', color='#457b9d')
barra_audit = ax.bar(x + largura/2, valores_audit, largura, label='Confirmados (Auditoria)', color='#e63946')

ax.set_ylabel('Quantidade de Ocorrências', fontsize=12, weight='bold')
#ax.set_title('Precisão da Análise AST vs. Validação da Auditoria Manual', fontsize=14, weight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels(categorias, rotation=15, ha='right', fontsize=10, weight='bold')
ax.legend(fontsize=11)
ax.grid(axis='y', linestyle='--', alpha=0.5)

# Adicionar rótulos de dados no topo das barras
def adicionar_rotulos(barras):
    for barra in barras:
        alt = barra.get_height()
        ax.annotate(f'{int(alt)}',
                    xy=(barra.get_x() + barra.get_width() / 2, alt),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=10, weight='bold')

adicionar_rotulos(barra_ast)
adicionar_rotulos(barra_audit)

plt.tight_layout()
plt.savefig('ast_vs_auditoria.png', dpi=300)
plt.show()