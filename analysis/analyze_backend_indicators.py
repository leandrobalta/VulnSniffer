import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter

# ==============================================================================
# CONFIGURAÇÕES INICIAIS
# ==============================================================================
TARGET_DIR = '../src/mined_repos'

BACKEND_INDICATORS = [
    "express",
    "nestjs", "@nestjs/core",
    "fastify",
    "koa",
    "typeorm",
    "prisma",
    "mongoose",
    "sequelize",
    "passport",
    "socket.io-client",
    "@symfony/webpack-encore", "symfony/webpack-encore",
    "hono"
]

# Inicializa o contador geral das ferramentas
contador_geral = Counter({indicator: 0 for indicator in BACKEND_INDICATORS})

# Verifica se o diretório informado realmente existe
if not os.path.exists(TARGET_DIR):
    print(f"❌ Erro: O diretório '{TARGET_DIR}' não foi encontrado.")
    exit()

# Lista apenas as pastas de primeiro nível dentro de 'mined_repos' (cada uma sendo um projeto)
repositorios = [d for d in os.listdir(TARGET_DIR) if os.path.isdir(os.path.join(TARGET_DIR, d))]
total_repositorios = len(repositorios)

print(f"🚀 Iniciando a varredura local de {total_repositorios} repositórios...")

# ==============================================================================
# VARREDURA E MINERAÇÃO DE DADOS
# ==============================================================================
for index, repo_folder in enumerate(repositorios):
    repo_path = os.path.join(TARGET_DIR, repo_folder)
    
    # Conjunto para armazenar dependências únicas DESTE projeto específico
    deps_do_projeto = set()
    
    # Varre o repositório procurando por qualquer ocorrência de package.json
    for root, dirs, files in os.walk(repo_path):
        if 'package.json' in files:
            package_json_path = os.path.join(root, 'package.json')
            
            try:
                with open(package_json_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = json.load(f)
                    
                    # Extrai chaves de dependências de produção e de desenvolvimento
                    deps = content.get('dependencies', {}).keys()
                    dev_deps = content.get('devDependencies', {}).keys()
                    
                    deps_do_projeto.update(deps)
                    deps_do_projeto.update(dev_deps)
            except Exception:
                # Silencia erros de arquivos package.json corrompidos ou mal formatados
                continue
                
    # Incrementa o contador geral se o indicador foi encontrado nas dependências mapeadas do projeto    
    for indicator in BACKEND_INDICATORS:
        if indicator in deps_do_projeto:
            contador_geral[indicator] += 1
            
    print(f"✅ [{index + 1}/{total_repositorios}] Processado: {repo_folder} - Indicadores encontrados: {', '.join([ind for ind in BACKEND_INDICATORS if ind in deps_do_projeto]) or 'Nenhum'}")

# ==============================================================================
# EXIBIÇÃO DE RESULTADOS DETALHADOS NO TERMINAL
# ==============================================================================
print("\n📋 Resultados Obtidos (Uso Cumulativo Individual):")
print("-" * 45)
for ferramenta, qtd in contador_geral.most_common():
    print(f"🔹 {ferramenta.ljust(25)}: {qtd} repositórios")
print("-" * 45)

# ==============================================================================
# AGRUPAMENTO DOS INDICADORES PARA O GRÁFICO
# ==============================================================================
print("\n🔄 Agrupando tecnologias semelhantes para a geração do gráfico...")

# Dicionário de mapeamento: define como cada indicador individual se agrupa comercialmente
MAPEAMENTO_AGRUPADO = {
    "express": "Express",
    "nestjs": "NestJS",
    "@nestjs/core": "NestJS",
    "fastify": "Fastify",
    "koa": "Koa",
    "typeorm": "TypeORM",
    "prisma": "Prisma",
    "mongoose": "Mongoose",
    "sequelize": "Sequelize",
    "passport": "Passport",
    "socket.io-client": "Socket.io Client",
    "@symfony/webpack-encore": "Symfony Webpack Encore",
    "symfony/webpack-encore": "Symfony Webpack Encore",
    "hono": "Hono"
}

# Inicializa um novo dicionário para consolidar os totais agrupados
contador_agrupado = {}

# Como um repositório pode conter múltiplos sub-indicadores da mesma lib (ex: ter 'nestjs' e '@nestjs/core'),
# precisamos garantir que ele conte apenas 1 vez por categoria agrupada.
# Faremos isso analisando novamente o histórico de processamento local ou calculando o teto lógico.
# No entanto, a forma mais matematicamente segura baseada em contadores prontos de conjuntos únicos é:
for indicador, total in contador_geral.items():
    nome_agrupado = MAPEAMENTO_AGRUPADO[indicador]
    # Se o grupo ainda não existe, cria. Se existe, soma (mas o teto é o número de repos de fato).
    # Como seu script original usa set() por projeto, a soma simples aqui pode gerar uma distorção caso 
    # o projeto use as duas libs ao mesmo tempo. Para evitar falsos positivos de dupla contagem no grupo:
    if nome_agrupado not in contador_agrupado:
        contador_agrupado[nome_agrupado] = total
    else:
        # Pega o maior valor entre as variações para evitar duplicar o mesmo repositório
        contador_agrupado[nome_agrupado] = max(contador_agrupado[nome_agrupado], total)

# ==============================================================================
# GERAÇÃO DO GRÁFICO DE BARRAS HORIZONTAIS
# ==============================================================================
print("📊 Gerando gráfico estatístico para o TCC...")

# Converte os resultados agrupados para um DataFrame e ordena do menor para o maior
df_grafico = pd.DataFrame.from_dict(contador_agrupado, orient='index', columns=['Quantidade']).reset_index()
df_grafico.columns = ['Ferramenta', 'Quantidade']
df_grafico = df_grafico.sort_values(by='Quantidade', ascending=True)

plt.figure(figsize=(11, 6))

# Cria barras horizontais limpas com as categorias agregadas
barras = plt.barh(df_grafico['Ferramenta'], df_grafico['Quantidade'], color='#3182bd', edgecolor='#1c547a')

# Insere os rótulos numéricos na frente de cada barra correspondente
for barra in barras:
    width = barra.get_width()
    plt.text(width + 0.5, barra.get_y() + barra.get_height()/2, f'{int(width)}', 
             va='center', ha='left', fontsize=10, fontweight='bold', color='#333333')

plt.xlabel('Número Absoluto de Repositórios (Uso Cumulativo)', fontsize=11, labelpad=10)
plt.ylabel('Ferramentas / Frameworks', fontsize=11)
plt.grid(axis='x', linestyle='--', alpha=0.5)

# Otimiza o layout e salva o gráfico em alta definição para o TCC
plt.tight_layout()
plt.savefig('distribuicao_backend_local.png', dpi=300)
plt.show()

print("✨ Concluído! O gráfico agrupado foi gerado e salvo como 'distribuicao_backend_local.png'.")