import pandas as pd

df = pd.read_csv('../csv/results_ast_analysis_limpo.csv')

unique_count = df['Repo'].nunique()

print(f"Total de repositórios únicos: {unique_count}")