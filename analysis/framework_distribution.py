import pandas as pd
import matplotlib.pyplot as plt

# Carregar dados de mineração
df_mining = pd.read_csv('typescript_results/results_mining.csv')

# Limpar e extrair os nomes dos frameworks para exibição
df_mining['Framework_Clean'] = df_mining['Framework'].str.replace('Backend Detectado \(', '', regex=True).str.replace('\)', '', regex=True)
framework_counts = df_mining['Framework_Clean'].value_counts().sort_values(ascending=True)

# Configuração do gráfico de barras horizontais (limpo e sem poluição)
plt.figure(figsize=(10, 5))
cores = ['#1d3557', '#457b9d', '#a8dadc', '#e63946']

barras = plt.barh(framework_counts.index, framework_counts.values, color=cores[-len(framework_counts):], edgecolor='#1d3557', height=0.55)

# Adicionar o número exato à frente de cada barra
for barra in barras:
    largura = barra.get_width()
    plt.text(
        largura + 1, 
        barra.get_y() + barra.get_height()/2, 
        f'{int(largura)}', 
        va='center', ha='left', fontsize=11, weight='bold'
    )

#plt.title('Distribuição Absoluta de Frameworks/Tecnologias na Amostra', fontsize=13, weight='bold', pad=15)
plt.xlabel('Quantidade de Repositórios Detectados', fontsize=11, weight='bold', labelpad=10)
plt.ylabel('Framework / Driver', fontsize=11, weight='bold', labelpad=10)
plt.xlim(0, max(framework_counts.values) * 1.1)
plt.grid(axis='x', linestyle='--', alpha=0.4)
plt.gca().set_axisbelow(True)

plt.tight_layout()
plt.savefig('distribuicao_frameworks.png', dpi=300)
plt.show()