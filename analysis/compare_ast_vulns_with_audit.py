import pandas as pd

CSV_AUDIT = '../csv/results_audit_limpo.csv'
TOTAL_AMOSTRA_TCC = 72  # total de repos unicos com vulnerabilidades detectadas

try:
    # 1. Carrega o CSV de Auditoria
    df = pd.read_csv(CSV_AUDIT)
    
    # Limpa as colunas removendo espaços para evitar erros de digitação
    df['Repo'] = df['Repo'].astype(str).str.strip()
    df['Status'] = df['Status'].astype(str).str.strip().str.upper()

    # 2. Mapeia o universo de repositórios que geraram algum alerta
    todos_repos_com_alertas = df['Repo'].unique()
    qtd_repos_com_alertas = len(todos_repos_com_alertas)

    # 3. Filtra apenas as linhas classificadas estritamente como 'CORRETO'
    df_correto = df[df['Status'] == 'CORRETO']
    
    # Obtém os repositórios únicos que possuem pelo menos UMA vulnerabilidade real confirmada
    repos_vulneraveis_reais = df_correto['Repo'].unique()
    qtd_repos_reais = len(repos_vulneraveis_reais)

    # 4. Cálculos Estatísticos (Divisões simples)
    porcentagem_sobre_amostra_total = (qtd_repos_reais / TOTAL_AMOSTRA_TCC) * 100
    porcentagem_sobre_alertas = (qtd_repos_reais / qtd_repos_com_alertas) * 100

    # ==============================================================================
    # EXIBIÇÃO DOS RESULTADOS PARA O TEXTO DO TCC
    # ==============================================================================
    print("=" * 70)
    print("📊 RELATÓRIO ESTATÍSTICO DE VULNERABILIDADES REAIS (STATUS: CORRETO)")
    print("=" * 70)
    print(f"🔹 Repositórios únicos com achados REAIS confirmados: {qtd_repos_reais}")
    print(f"🔹 Total de repositórios que geraram alertas iniciais: {qtd_repos_com_alertas}")
    print(f"🔹 Universo total da amostragem do TCC: {TOTAL_AMOSTRA_TCC}\n")
    
    print("-" * 70)
    print("📈 MÉTRICAS E PORCENTAGENS PARA O TEXTO:")
    print("-" * 70)
    print(f"👉 {porcentagem_sobre_amostra_total:.2f}% de todos os repositórios minerados ({TOTAL_AMOSTRA_TCC})")
    print(f"   possuem pelo menos uma vulnerabilidade real confirmada no código.")
    print()
    print(f"👉 {porcentagem_sobre_alertas:.2f}% dos repositórios que dispararam a ferramenta ({qtd_repos_com_alertas})")
    print(f"   tiveram o alerta validado manualmente como uma vulnerabilidade real.")
    print("=" * 70)


    print(f"quantidade de Repos com vulnerabilidades reais confirmadas: {len(repos_vulneraveis_reais)}")

except FileNotFoundError:
    print(f"❌ Erro: O arquivo '{CSV_AUDIT}' não foi encontrado no diretório atual.")
except Exception as e:
    print(f"❌ Ocorreu um erro inesperado: {e}")