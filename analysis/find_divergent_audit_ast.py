import pandas as pd

CSV_AUDIT = '../csv/results_audit_limpo.csv'
CSV_AST = '../csv/results_ast_analysis_limpo.csv'

# Cores para o terminal
CLR_DIF = '\033[1;31m'     # Vermelho para diferenças
CLR_AVISO = '\033[1;33m'   # Amarelo para duplicatas internas
CLR_SUCESSO = '\033[1;32m' # Verde
CLR_RESET = '\033[0m'

try:
    # 1. Carrega os CSVs
    df_audit = pd.read_csv(CSV_AUDIT)
    df_ast = pd.read_csv(CSV_AST)
    
    # Limpa espaços em branco e garante consistência nos tipos de dados
    for df in [df_audit, df_ast]:
        df['Repo'] = df['Repo'].astype(str).str.strip()
        df['File'] = df['File'].astype(str).str.strip()
        df['Line'] = df['Line'].astype(float)  # Força float para bater 11 e 11.0
        df['Type'] = df['Type'].astype(str).str.strip()

    # 2. Cria uma coluna identificadora única (Chave Combinada)
    df_audit['Chave_ID'] = df_audit['Repo'] + " | " + df_audit['File'] + " | Lora: " + df_audit['Line'].astype(str) + " | " + df_audit['Type']
    df_ast['Chave_ID'] = df_ast['Repo'] + " | " + df_ast['File'] + " | Lora: " + df_ast['Line'].astype(str) + " | " + df_ast['Type']

    print(f"📊 Total de linhas brutas lidas:")
    print(f"   - {CSV_AUDIT}: {len(df_audit)} linhas")
    print(f"   - {CSV_AST}: {len(df_ast)} linhas\n")

    # 3. Verificação de Duplicatas Internas (Mesmo ID repetido no próprio arquivo)
    dups_audit = df_audit[df_audit.duplicated(subset=['Chave_ID'], keep=False)]
    dups_ast = df_ast[df_ast.duplicated(subset=['Chave_ID'], keep=False)]

    if not dups_audit.empty:
        print(f"{CLR_AVISO}⚠️  Linhas duplicadas detectadas dentro do {CSV_AUDIT}:{CLR_RESET}")
        for chave in dups_audit['Chave_ID'].unique():
            qtd = len(df_audit[df_audit['Chave_ID'] == chave])
            print(f"   - A vulnerabilidade [{chave}] aparece {qtd} vezes no Audit.")
        print()

    # 4. Cruzamento de dados (Diferenças entre arquivos)
    chaves_audit = set(df_audit['Chave_ID'])
    chaves_ast = set(df_ast['Chave_ID'])

    exclusivos_audit = chaves_audit - chaves_ast
    exclusivos_ast = chaves_ast - chaves_audit

    # ==============================================================================
    # EXIBIÇÃO DO RELATÓRIO DE DIVERGÊNCIAS
    # ==============================================================================
    print("=" * 80)
    print("🔍 RELATÓRIO DE DIVERGÊNCIAS ENCONTRADAS")
    print("=" * 80)

    if exclusivos_audit:
        print(f"{CLR_DIF}🚨 Linhas presentes no AUDIT que NÃO ESTÃO no AST ({len(exclusivos_audit)}):{CLR_RESET}")
        for idx, chave in enumerate(sorted(exclusivos_audit), 1):
            print(f"   {idx}. {chave}")
        print()
    
    if exclusivos_ast:
        print(f"{CLR_DIF}🚨 Linhas presentes no AST que NÃO ESTÃO no AUDIT ({len(exclusivos_ast)}):{CLR_RESET}")
        for idx, chave in enumerate(sorted(exclusivos_ast), 1):
            print(f"   {idx}. {chave}")
        print()

    if not exclusivos_audit and not exclusivos_ast:
        print(f"{CLR_SUCESSO}✅ Sucesso! Estruturalmente todas as chaves únicas mapeadas são idênticas.{CLR_RESET}")
    
    print("=" * 80)

except FileNotFoundError as e:
    print(f"❌ Erro: Arquivo não encontrado - {e}")
except Exception as e:
    print(f"❌ Ocorreu um erro inesperado: {e}")