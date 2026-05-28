import pandas as pd
import matplotlib.pyplot as plt

def analisar_categorias_vulnerabilidades(csv_path):
    # 1. Carregar o arquivo CSV
    df = pd.read_csv(csv_path)
    
    # 2. Filtrar apenas pelos casos confirmados (Status == 'CORRETO')
    df_confirmados = df[df['Status'] == 'CORRETO']
    
    if df_confirmados.empty:
        print("Nenhum caso confirmado ('CORRETO') foi encontrado no arquivo.")
        return

    # 3. Contar a quantidade de ocorrências por categoria de falha (coluna 'Type')
    contagem_categorias = df_confirmados['Type'].value_counts()
    
    # Ordenar de forma crescente para que a maior barra apareça no topo do gráfico horizontal
    contagem_categorias = contagem_categorias.sort_values(ascending=True)
    
    # Exibir os dados formatados no console
    print("=== Casos Confirmados por Categoria ===")
    for categoria, total in contagem_categorias.sort_values(ascending=False).items():
        print(f"- {categoria}: {total} casos")
    print("=======================================")
    
    # 4. Geração do Gráfico de Barras Horizontais
    plt.figure(figsize=(10, 6))
    
    # Criar as barras horizontais com uma cor sólida e elegante
    barras = plt.barh(
        contagem_categorias.index, 
        contagem_categorias.values, 
        color='#e63946',  # Vermelho corporativo
        edgecolor='#b7091f',
        height=0.6
    )
    
    # Adicionar os números/rótulos exatos ao lado de cada barra
    for barra in barras:
        largura_barra = barra.get_width()
        plt.text(
            largura_barra + 0.3,                 # Posição X (um pouco à frente da barra)
            barra.get_y() + barra.get_height()/2, # Posição Y (centralizado na barra)
            f'{int(largura_barra)}',             # Texto a ser exibido
            va='center', 
            ha='left', 
            fontsize=11, 
            weight='bold'
        )
    
    # Customização estética do gráfico
    # Volume de Casos Confirmados por Categoria de Falha
    #plt.title('', fontsize=14, weight='bold', pad=20)
    plt.xlabel('Quantidade de Casos Detectados', fontsize=12, weight='bold', labelpad=10)
    plt.ylabel('Categoria de Falha (Type)', fontsize=12, weight='bold', labelpad=10)
    
    # Ajustar limites do eixo X para dar espaço aos números impressos ao lado das barras
    plt.xlim(0, max(contagem_categorias.values) * 1.15)
    
    # Ativar linhas de grade verticais discretas para auxiliar a leitura
    plt.grid(axis='x', linestyle='--', alpha=0.5)
    plt.gca().set_axisbelow(True) # Garante que a grade fique atrás das barras
    
    plt.tight_layout()
    
    # Salvar o gráfico como imagem
    plt.savefig('vulnerabilidades_por_categoria.png', dpi=300)
    print("\nGráfico gerado com sucesso e salvo como 'vulnerabilidades_por_categoria.png'!")
    
    # Exibir o gráfico na tela
    plt.show()

if __name__ == "__main__":
    analisar_categorias_vulnerabilidades('../typescript_results/results_audit.csv')
