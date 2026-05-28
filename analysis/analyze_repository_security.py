import pandas as pd
import matplotlib.pyplot as plt

def analisar_repositorios(csv_path):
    # 1. Carregar o arquivo CSV
    df = pd.read_csv(csv_path)
    
    # Remover linhas que não possuem identificação de repositório
    df = df.dropna(subset=['Repo'])
    
    # 2. Contagem de repositórios únicos no total
    todos_repositorios = set(df['Repo'].unique())
    total_unicos = len(todos_repositorios)
    
    # 3. Identificar repositórios vulneráveis (pelo menos um status 'CORRETO')
    repos_vulneraveis = set(df[df['Status'] == 'CORRETO']['Repo'].unique())
    total_vulneraveis = len(repos_vulneraveis)
    
    # 4. Identificar repositórios seguros (o restante)
    repos_seguros = todos_repositorios - repos_vulneraveis
    total_seguros = len(repos_seguros)
    
    # Exibir métricas no console
    print(f"=== Resumo da Análise ===")
    print(f"Total de Repositórios Únicos: {total_unicos}")
    print(f"Repositórios Vulneráveis: {total_vulneraveis}")
    print(f"Repositórios Seguros: {total_seguros}")
    print(f"=========================")
    
    # 5. Geração do Gráfico de Pizza
    labels = ['Repositórios Vulneráveis', 'Repositórios Seguros']
    valores = [total_vulneraveis, total_seguros]
    cores = ['#e63946', '#2a9d8f'] # Tons agradáveis de vermelho e verde/azul
    explode = (0.05, 0) # Destacar ligeiramente a fatia de vulneráveis
    
    plt.figure(figsize=(7, 7))
    plt.pie(
        valores, 
        explode=explode, 
        labels=labels, 
        colors=cores, 
        autopct='%1.1f%%',
        shadow=False, 
        startangle=140,
        textprops={'fontsize': 12, 'weight': 'bold'}
    )
    
    plt.title(f'(Total: {total_unicos} Repositórios Únicos)', fontsize=14, weight='bold', pad=20)
    plt.tight_layout()
    
    # Salvar o gráfico como imagem
    plt.savefig('proporcao_repositorios.png', dpi=300)
    print("Gráfico gerado com sucesso e salvo como 'proporcao_repositorios.png'!")
    
    # Exibir o gráfico em tela
    plt.show()

# Executar a função passando o seu arquivo mapeado
if __name__ == "__main__":
    analisar_repositorios('typescript_results/results_audit.csv')