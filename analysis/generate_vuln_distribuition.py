import pandas as pd

CSV_INPUT = '../csv/results_audit_limpo.csv'
CSV_OUTPUT = '../csv/vuln_distribuition.csv'

try:
    # 1. Carrega o CSV de auditoria
    df = pd.read_csv(CSV_INPUT)
    
    # Limpa as strings para evitar divergências por espaços em branco
    df['Type'] = df['Type'].astype(str).str.strip()
    df['Repo'] = df['Repo'].astype(str).str.strip()
    df['Status'] = df['Status'].astype(str).str.strip().str.upper()

    # 2. Totalizador geral de instâncias confirmadas (para o cálculo do percentual)
    total_instancias_reais_geral = len(df[df['Status'] == 'CORRETO'])

    # Lista para armazenar as linhas do novo relatório
    dados_distribuicao = []

    # 3. Agrupa e analisa por categoria de vulnerabilidade (coluna Type)
    categorias = df['Type'].unique()

    for cat in categorias:
        # Filtra o DataFrame apenas para a categoria atual
        df_cat = df[df['Type'] == cat]
        
        # Total de alertas disparados pelo scanner para esta categoria (Bruto)
        alertas_totais_categoria = len(df_cat)
        
        # Filtra apenas os confirmados manualmente como reais (CORRETO)
        df_cat_confirmado = df_cat[df_cat['Status'] == 'CORRETO']
        instancias_confirmadas = len(df_cat_confirmado)
        
        # Se o scanner achou algo mas nada foi confirmado real, define os valores como zero
        if instancias_confirmadas == 0:
            percentual_do_total = 0.0
            projetos_afetados = 0
            acuracia_scanner = 0.0
        else:
            # Percentual que esta categoria representa sobre o TOTAL de vulnerabilidades reais do TCC
            percentual_do_total = (instancias_confirmadas / total_instancias_reais_geral) * 100
            
            # Contagem de repositórios ÚNICOS afetados por esta vulnerabilidade real
            projetos_afetados = df_cat_confirmado['Repo'].nunique()
            
            # Taxa de acurácia (Confirmações / Alertas Brutos do Scanner)
            acuracia_scanner = (instancias_confirmadas / alertas_totais_categoria) * 100

        # Alimenta a lista de dados
        dados_distribuicao.append({
            'categoria_vulnerabilidade': cat,
            'instancias_confirmadas': instancias_confirmadas,
            'percentual_do_total': round(percentual_do_total, 2),
            'projetos_affected': projetos_afetados,
            'acuracia_scanner_%': round(acuracia_scanner, 2)
        })

    # 4. Converte em DataFrame e ordena pelas categorias com maior impacto real
    df_resultado = pd.DataFrame(dados_distribuicao)
    df_resultado = df_resultado.sort_values(by='instancias_confirmadas', ascending=False)

    # 5. Salva o novo arquivo CSV solicitado
    df_resultado.to_csv(CSV_OUTPUT, index=False, encoding='utf-8')
    
    # ==============================================================================
    # PRÉ-VISUALIZAÇÃO NO TERMINAL
    # ==============================================================================
    print("\n" + "="*85)
    print(f"✅ Arquivo '{CSV_OUTPUT}' gerado com sucesso!")
    print("="*85)
    print(df_resultado.to_string(index=False))
    print("="*85)

except FileNotFoundError:
    print(f"❌ Erro: O arquivo de entrada '{CSV_INPUT}' não foi localizado.")
except Exception as e:
    print(f"❌ Ocorreu um erro inesperado durante o processamento: {e}")