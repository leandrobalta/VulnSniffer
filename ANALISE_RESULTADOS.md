# 📊 VulnSniffer - Análise de Resultados

## 📈 Descrição do Script de Análise

O script `analyze_results.py` gera uma análise completa e visual do pipeline de detecção de vulnerabilidades do VulnSniffer, processando os dados de três estágios principais:

### 🔄 Pipeline de Análise

```
MINING (238 repos) → AST ANALYSIS (239 vulns) → AUDIT MANUAL (191 auditadas)
```

---

## 📊 Gráficos Gerados

### **Página 1: Visão Geral do Pipeline** (`analise_completa_1.png`)

#### 1. Funil do Pipeline de Análise
- **Estágios**: Repositórios Selecionados → Vulnerabilidades Detectadas → Vulnerabilidades Auditadas
- **Métricas Chave**:
  - 238 repositórios selecionados no Mining
  - 239 vulnerabilidades encontradas pelo AST (30.7% dos repos)
  - 191 vulnerabilidades auditadas manualmente (80% do total encontrado)

#### 2. Distribuição de Tipos de Vulnerabilidade (Gráfico de Pizza)
Mostra a proporção de cada tipo de vulnerabilidade encontrada:
- **HARDCODED_SECRET**: 51.5% (123 casos)
- **INSECURE_CORS**: 30.1% (72 casos)
- **NESTJS_MASS_ASSIGNMENT**: 11.3% (27 casos)
- **DB_AUTO_SYNC**: 7.1% (17 casos)

#### 3. Resultado da Auditoria Manual (Gráfico de Barras Horizontal)
Classificação final das vulnerabilidades auditadas:
- ❌ **INCORRETO**: 86 casos (45.0%) - Falsos positivos
- ✅ **CORRETO**: 64 casos (33.5%) - Vulnerabilidades reais
- ⏹️ **NAO_SE_APLICA**: 40 casos (20.9%) - Fora do escopo do estudo

#### 4. Top 10 Repositórios com Mais Vulnerabilidades
Ranking dos repositórios que apresentaram mais achados durante a análise AST.

---

### **Página 2: Análises Detalhadas** (`analise_completa_2.png`)

#### 5. Ranking de Tipos de Vulnerabilidade (Gráfico de Barras)
Contagem absoluta de cada tipo de vulnerabilidade com rótulos de quantidade.

#### 6. Análise de Acurácia do Scanner AST
Comparação entre diferentes resultados do audit:
- Verdadeiros Positivos (CORRETO)
- Falsos Positivos (INCORRETO)
- Fora do Escopo (NAO_SE_APLICA)
- Pendentes (DEPENDE)

**Métricas calculadas**:
- Taxa de Acurácia: 33.5%
- Taxa de Falsos Positivos: 45.0%

#### 7. Matriz de Correlação: Tipo vs Status
Heatmap mostrando a distribuição percentual de cada classificação por tipo de vulnerabilidade.

Insights importantes:
- **INSECURE_CORS**: 56.9% confirmado como vulnerabilidade
- **HARDCODED_SECRET**: 76.5% falso positivo (muitos em código de teste)
- **NESTJS_MASS_ASSIGNMENT**: 65.2% confirmado
- **DB_AUTO_SYNC**: 85.7% confirmado

#### 8. Comparação de Repositórios Afetados
- 73 repositórios com vulnerabilidades encontradas
- 45 repositórios com vulnerabilidades confirmadas (verdadeiros positivos)
- 38 repositórios com falsos positivos ou fora do escopo

---

## 📋 Relatório Detalhado

O script também gera um relatório textual completo com:

### ✅ Estatísticas Gerais
```
Mining:           238 repositórios selecionados
AST Analysis:     239 vulnerabilidades encontradas em 73 repositórios
Audit:            191 vulnerabilidades analisadas manualmente
```

### 📊 Distribuição por Status
- INCORRETO: 86 (45.0%)
- CORRETO: 64 (33.5%)
- NAO_SE_APLICA: 40 (20.9%)

### 🎯 Análise por Tipo de Vulnerabilidade

#### INSECURE_CORS (51 auditadas)
- ✅ CORRETO: 29 (56.9%)
- ⏹️ NAO_SE_APLICA: 17 (33.3%)
- ❌ INCORRETO: 5 (9.8%)

#### HARDCODED_SECRET (102 auditadas)
- ❌ INCORRETO: 78 (76.5%) - Principalmente em mock data e testes
- ⏹️ NAO_SE_APLICA: 16 (15.7%)
- ✅ CORRETO: 8 (7.8%)

#### NESTJS_MASS_ASSIGNMENT (23 auditadas)
- ✅ CORRETO: 15 (65.2%)
- ⏹️ NAO_SE_APLICA: 7 (30.4%)
- ❌ INCORRETO: 1 (4.3%)

#### DB_AUTO_SYNC (14 auditadas)
- ✅ CORRETO: 12 (85.7%) - Forte indicador de vulnerabilidade
- ❌ INCORRETO: 2 (14.3%)

---

## 📈 Principais Insights

### 1️⃣ Taxa de Filtragem
- **69.3%** dos repositórios foram filtrados (sem vulnerabilidades)
- 165 repositórios descartados, 73 com achados

### 2️⃣ Taxa de Confirmação
- **33.5%** das vulnerabilidades encontradas são reais (verdadeiros positivos)
- **66.0%** são falsos positivos ou fora do escopo

### 3️⃣ Tipo mais Confiável
- **DB_AUTO_SYNC**: 85.7% de acurácia
- **NESTJS_MASS_ASSIGNMENT**: 65.2% de acurácia
- **INSECURE_CORS**: 56.9% de acurácia
- **HARDCODED_SECRET**: 7.8% de acurácia (muito ruidoso - muitos falsos positivos)

### 4️⃣ Impacto
- **45 repositórios** com vulnerabilidades confirmadas
- **38 repositórios** com falsos positivos (precisam melhorar o detector)

---

## 🔧 Como Executar

```bash
# Instalar dependências
pip3 install pandas matplotlib seaborn

# Executar análise
python3 analyze_results.py
```

Os gráficos serão salvos em:
- `csv/analise_completa_1.png` (4 gráficos)
- `csv/analise_completa_2.png` (4 gráficos)

---

## 📌 Recomendações

### ✅ Pontos Positivos
- Detecção de INSECURE_CORS, DB_AUTO_SYNC e NESTJS_MASS_ASSIGNMENT é relativamente confiável
- Pipeline bem estruturado com múltiplos estágios de validação

### ⚠️ Pontos de Melhoria
- **HARDCODED_SECRET**: Muito ruidoso (76.5% falsos positivos)
  - Recomendação: Melhorar detecção para excluir mock data e arquivos de teste
  - Adicionar filtros para ambiente.ts, mock files, etc.

- **Fora do Escopo**: 20.9% dos achados não se aplicam ao estudo
  - Considerar refinar critérios de seleção de repositórios
  - Ou excluir determinados tipos de arquivo

---

## 📁 Estrutura de Dados

Os dados provêm de três CSVs principais:

### `1st_step_repositorios_selecionados.csv` (Mining)
Repositórios selecionados pelos critérios: backend, TypeScript, potencial acadêmico

### `results_ast_analysis.csv` (AST Analysis)
Vulnerabilidades encontradas pela análise AST com campos:
- Repo, URL, File, Line, Type, Description

### `results_audit.csv` (Audit)
Vulnerabilidades auditadas manualmente com campos:
- Repo, File, Line, Type, Description, **Status**, ReviewerNote

Status possíveis: CORRETO, INCORRETO, NAO_SE_APLICA, DEPENDE

---

## 🎓 Conclusão

O VulnSniffer demonstra ser uma ferramenta útil para detecção de vulnerabilidades em repositórios TypeScript, com especial eficácia em detectar:
- Vulnerabilidades de CORS inseguro (56.9% acurácia)
- Sincronização automática de banco de dados (85.7% acurácia)
- Mass assignment em NestJS (65.2% acurácia)

A próxima etapa seria refinar o detector de hardcoded secrets para reduzir falsos positivos relacionados a dados de teste.
