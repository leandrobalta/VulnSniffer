import matplotlib.pyplot as plt
import numpy as np

# Configuração dos dados
categorias = [
    'NESTJS_MASS_ASSIGNMENT\n(2 de 2 casos)',
    'HARDCODED_SECRET\n(5 de 7 casos)',
    'INSECURE_CORS\n(2 de 3 casos)',
    'DB_AUTO_SYNC\n(1 de 3 casos)'
]
porcentagens = [100.0, 71.43, 66.67, 33.33]

# Configuração da paleta de cores (Gradiente baseado na taxa de concordância)
cores = ['#2e7d32', '#1565c0', '#f57c00', '#d32f2f']

# Inicializa a figura
fig, ax = plt.subplots(figsize=(10, 6), dpi=100)

# Cria as barras horizontais
barras = ax.barh(categorias, porcentagens, color=cores, edgecolor='black', height=0.6)

# Customização do eixo X (Porcentagem)
ax.set_xlim(0, 115)  # Margem extra para os rótulos não cortarem
ax.set_xlabel('Taxa de Concordância (%)', fontsize=12, fontweight='bold', labelpad=10)

# Título do gráfico
# ax.set_title('Taxa de Concordância com o Especialista por Categoria de Vulnerabilidade', 
#              fontsize=14, fontweight='bold', pad=20)

# Inverte o eixo Y para que a maior concordância fique no topo
ax.invert_yaxis()

# Adiciona linhas de grade verticais discretas para facilitar a leitura
ax.grid(axis='x', linestyle='--', alpha=0.5)
ax.set_axisbelow(True)

# Remove as bordas (spines) desnecessárias para um visual mais limpo
for spine in ['top', 'right']:
    ax.spines[spine].set_visible(False)

# Adiciona os rótulos com os valores textuais no final de cada barra
for barra in barras:
    width = barra.get_width()
    ax.text(width + 1.5,          # Posição X do texto
            barra.get_y() + barra.get_height()/2, # Posição Y do texto
            f'{width:.2f}%',      # Texto formatado
            ha='left',            # Alinhamento horizontal
            va='center',          # Alinhamento vertical
            fontsize=11, 
            fontweight='bold')

# Ajusta o layout para evitar cortes
plt.tight_layout()

# Exibe o gráfico na tela
plt.show()

# Caso queira salvar a imagem diretamente em formato pronto para o artigo, descomente a linha abaixo:
#plt.savefig('expert_agreement.png', dpi=300)