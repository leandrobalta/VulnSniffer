import pandas as pd

# Nome do seu arquivo CSV
CSV_FILE = '../csv/results_mining_limpo.csv'

try:
    # Carrega o arquivo CSV
    df = pd.read_csv(CSV_FILE)
    
    # Encontra as linhas que são exatamente duplicadas (mantém a primeira ocorrência e mostra as cópias)
    duplicados = df[df.duplicated(keep='first')]
    
    # Conta o total de registros idênticos encontrados
    total_duplicados = len(duplicados)
    
    print(f"🔍 Análise concluída no arquivo: {CSV_FILE}")
    print(f"⚠️ Total de linhas exatamente duplicadas encontradas: {total_duplicados}\n")
    
    if total_duplicados > 0:
        print("📋 Linhas duplicadas identificadas:")
        print("-" * 80)
        print(duplicados)
        print("-" * 80)
        
        # Opcional: Descomente a linha abaixo se quiser salvar os duplicados em um novo arquivo para examinar
        # duplicados.to_csv('linhas_duplicadas.csv', index=False)
    else:
        print("✨ Excelente! Nenhuma linha exatamente igual foi detectada.")
        
    # df.drop_duplicates(keep='first').to_csv('../csv/results_audit_limpo.csv', index=False)
    # print("💾 Arquivo limpo salvo com sucesso como 'results_audit_limpo.csv'.")

except FileNotFoundError:
    print(f"❌ Erro: O arquivo '{CSV_FILE}' não foi encontrado no diretório atual.")