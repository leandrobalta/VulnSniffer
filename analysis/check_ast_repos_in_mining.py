import pandas as pd

# Configuração dos caminhos dos arquivos (ajuste se necessário)
CSV_AST = '../csv/results_ast_analysis_limpo.csv'
CSV_MINING = '../csv/results_mining_limpo.csv'

# Códigos ANSI para deixar o print no terminal muito chamativo (Colorido e Negrito)
CLR_ALERTA = '\033[1;31;43m'  # Texto Vermelho Negrito com Fundo Amarelo
CLR_ERRO = '\033[1;31m'      # Texto Vermelho Negrito
CLR_SUCESSO = '\033[1;32m'   # Texto Verde Negrito
CLR_RESET = '\033[0m'        # Reseta as cores para o padrão

try:
    # 1. Carrega os arquivos CSV
    df_ast = pd.read_csv(CSV_AST)
    df_mining = pd.read_csv(CSV_MINING)
    
    # 2. Garante que as colunas alvo existem nos arquivos correspondentes
    if 'Repo' not in df_ast.columns:
        print(f"{CLR_ERRO}❌ Erro: A coluna 'Repo' não foi encontrada em {CSV_AST}{CLR_RESET}")
        exit()
        
    # ATENÇÃO: Ajuste o nome da coluna abaixo ('Nome' ou 'URL') baseado no seu results_mining_limpo.csv
    coluna_busca_mining = 'Nome' 
    if coluna_busca_mining not in df_mining.columns:
        # Se não for 'Nome', tenta por 'URL' ou pega a primeira coluna disponível
        coluna_busca_mining = df_mining.columns[0]
        print(f"⚠️ Aviso: Usando a coluna '{coluna_busca_mining}' do {CSV_MINING} para comparação.")

    # 3. Transforma os dados da coluna do mining em um conjunto (set) para busca ultra rápida
    repos_no_mining = set(df_mining[coluna_busca_mining].astype(str).str.strip())
    
    # 4. Remove valores nulos e duplicados da análise AST para limpar o loop
    repos_no_ast = df_ast['Repo'].dropna().unique()
    
    print(f"🔄 Iniciando verificação de {len(repos_no_ast)} repositórios do AST contra o banco do Mining...\n")
    
    total_nao_encontrados = 0
    
    # 5. Itera e verifica a presença
    for repo in repos_no_ast:
        repo_limpo = str(repo).strip()
        
        if repo_limpo not in repos_no_mining:
            total_nao_encontrados += 1
            # Print altamente chamativo com fundo amarelo e texto vermelho
            print(f"{CLR_ALERTA}🚨 ALERTA: O repositório '{repo_limpo}' do AST NÃO FOI ENCONTRADO no {CSV_MINING}! 🚨{CLR_RESET}")
            
    # 6. Resumo final da verificação
    print("\n" + "="*60)
    if total_nao_encontrados > 0:
        print(f"{CLR_ERRO}❌ VERIFICAÇÃO CONCLUÍDA: {total_nao_encontrados} repositório(s) do AST estão ausentes no arquivo de mineração.{CLR_RESET}")
    else:
        print(f"{CLR_SUCESSO}✅ VERIFICAÇÃO CONCLUÍDA: Todos os repositórios mapeados no AST constam perfeitamente no arquivo de mineração!{CLR_RESET}")
    print("="*60)

except FileNotFoundError as e:
    print(f"{CLR_ERRO}❌ Erro de arquivo: {e}{CLR_RESET}")
except Exception as e:
    print(f"{CLR_ERRO}❌ Ocorreu um erro inesperado: {e}{CLR_RESET}")