import pandas as pd

# Configuração dos caminhos dos arquivos
CSV_AUDIT = '../csv/results_audit_limpo.csv'
CSV_AST = '../csv/results_ast_analysis_limpo.csv'

# Cores para o terminal
CLR_ERRO = '\033[1;31m'
CLR_SUCESSO = '\033[1;32m'
CLR_RESET = '\033[0m'

try:
    # 1. Carrega os arquivos CSV
    df_audit = pd.read_csv(CSV_AUDIT)
    df_ast = pd.read_csv(CSV_AST)
    
    # 2. Valida se a coluna 'Repo' existe em ambos os arquivos
    if 'Repo' not in df_audit.columns:
        print(f"{CLR_ERRO}❌ Erro: Coluna 'Repo' não encontrada no arquivo {CSV_AUDIT}{CLR_RESET}")
        exit()
    if 'Repo' not in df_ast.columns:
        print(f"{CLR_ERRO}❌ Erro: Coluna 'Repo' não encontrada no arquivo {CSV_AST}{CLR_RESET}")
        exit()

    # 3. Extrai o conjunto (set) de repositórios únicos de cada arquivo, limpando espaços em branco
    repos_audit = set(df_audit['Repo'].dropna().str.strip())
    repos_ast = set(df_ast['Repo'].dropna().str.strip())
    
    print(f"📊 Estatísticas de Leitura:")
    print(f"   - Repos únicos no Audit: {len(repos_audit)}")
    print(f"   - Repos únicos no AST Analysis: {len(repos_ast)}\n")

    # 4. Encontra a diferença (Está no Audit, mas NÃO está no AST)
    faltantes_no_ast = repos_audit - repos_ast

    # ==============================================================================
    # EXIBIÇÃO DO RESULTADO
    # ==============================================================================
    print("=" * 60)
    if faltantes_no_ast:
        print(f"{CLR_ERRO}🚨 REPOSITÓRIOS PRESENTES NO AUDIT QUE NÃO ESTÃO NO AST ({len(faltantes_no_ast)}):{CLR_RESET}")
        print("-" * 60)
        for idx, repo in enumerate(sorted(faltantes_no_ast), 1):
            print(f"  {idx}. {repo}")
    else:
        print(f"{CLR_SUCESSO}✅ Tudo certo! Todos os repositórios do Audit constam no AST Analysis.{CLR_RESET}")
    print("=" * 60)

except FileNotFoundError as e:
    print(f"{CLR_ERRO}❌ Erro de Arquivo: {e}{CLR_RESET}")
except Exception as e:
    print(f"{CLR_ERRO}❌ Ocorreu um erro inesperado: {e}{CLR_RESET}")