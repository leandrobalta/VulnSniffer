# 🔍 VulnSniffer - Análise Completa de Resultados

## 📚 Documentação do Script de Análise e Relatórios

Este diretório contém todos os scripts e relatórios gerados pelo pipeline de análise de vulnerabilidades do VulnSniffer.

---

## 📁 Arquivos Principais

### **Python Script**
- **`analyze_results.py`** - Script principal que processa os 3 CSVs e gera toda a análise

### **CSVs de Dados**
1. **`1st_step_repositorios_selecionados.csv`** - Repositórios selecionados no Mining (238)
2. **`results_ast_analysis.csv`** - Vulnerabilidades encontradas pelo AST (239)
3. **`results_audit.csv`** - Vulnerabilidades analisadas manualmente (191)

### **Relatórios Gerados**
- **`analise_completa_1.png`** - Gráficos: Funil, Distribuição, Status, Top 10
- **`analise_completa_2.png`** - Gráficos: Ranking, Acurácia, Matriz, Comparação
- **`relatorio_analise.html`** - Relatório interativo completo (ABRIR NO NAVEGADOR)

### **Documentação**
- **`ANALISE_RESULTADOS.md`** - Análise detalhada em Markdown
- **`README.md`** - Este arquivo

---

## 🚀 Como Usar

### 1️⃣ Instalar Dependências
```bash
pip3 install pandas matplotlib seaborn
```

### 2️⃣ Executar o Script
```bash
python3 analyze_results.py
```

### 3️⃣ Visualizar Resultados

**Para ver gráficos em alta qualidade:**
```bash
# Linux/Mac
open csv/analise_completa_1.png
open csv/analise_completa_2.png

# Ou visualizar o relatório HTML no navegador
open csv/relatorio_analise.html
```

**Para ler o relatório textual:**
```bash
cat ANALISE_RESULTADOS.md
```

---

## 📊 O Que Cada Arquivo Contém

### `analise_completa_1.png` (4 Gráficos)
1. **Funil do Pipeline** - Mostra a progressão: Mining → AST → Audit
2. **Distribuição de Tipos** - Pizza chart mostrando % de cada vulnerabilidade
3. **Resultado da Auditoria** - Status final (CORRETO, INCORRETO, NAO_SE_APLICA)
4. **Top 10 Repositórios** - Ranking dos repos com mais vulnerabilidades

### `analise_completa_2.png` (4 Gráficos)
1. **Ranking de Vulnerabilidades** - Contagem total por tipo
2. **Análise de Acurácia** - Comparação Verdadeiros vs Falsos Positivos
3. **Matriz Tipo vs Status** - Heatmap de correlação
4. **Comparação de Repositórios** - Antes/depois do audit

### `relatorio_analise.html`
Dashboard interativo com:
- Métricas principais em cards
- Tabelas com dados detalhados
- Visualização dos gráficos PNG
- Recomendações e insights
- Formatação responsiva para apresentação

---

## 📈 Principais Métricas

### Pipeline de Filtragem
```
Mining: 238 repositórios
  ↓ (30.7% com vulnerabilidades)
AST Analysis: 239 vulnerabilidades encontradas em 73 repos
  ↓ (80% auditadas)
Audit Manual: 191 vulnerabilidades analisadas
```

### Resultado da Auditoria
| Status | Quantidade | Percentual |
|--------|-----------|-----------|
| ❌ INCORRETO | 86 | 45.0% |
| ✅ CORRETO | 64 | 33.5% |
| ⏹️ NAO_SE_APLICA | 40 | 20.9% |

### Acurácia por Tipo
| Tipo | Acurácia | Confiabilidade |
|------|----------|----------------|
| DB_AUTO_SYNC | 85.7% | ⭐⭐⭐⭐⭐ |
| NESTJS_MASS_ASSIGNMENT | 65.2% | ⭐⭐⭐ |
| INSECURE_CORS | 56.9% | ⭐⭐ |
| HARDCODED_SECRET | 7.8% | ⭐ |

---

## 🎯 Insights Principais

### ✅ Pontos Positivos
1. **DB_AUTO_SYNC** é altamente confiável (85.7% acurácia)
   - Sincronização automática de BD realmente representa risco
   - Priorizar correção destes achados

2. **NESTJS_MASS_ASSIGNMENT** tem boa detecção (65.2% acurácia)
   - Muitos dos achados são reais
   - Indicador importante para segurança NestJS

3. **INSECURE_CORS** atinge 56.9% de acurácia
   - Mais de metade dos achados são confirmados
   - Problema comum em projetos acadêmicos

### ⚠️ Pontos de Melhoria
1. **HARDCODED_SECRET muito ruidoso** (76.5% falsos positivos)
   - Principalmente em dados de teste/mock
   - Necessário filtrar arquivos .spec.ts, mock-*.ts

2. **Fora do Escopo** (20.9% dos achados)
   - Refinar critérios de seleção no Mining
   - Focar em backends TypeScript autênticos

3. **Falsos Positivos** (45% dos achados)
   - Melhorar regras de detecção
   - Implementar mais contexto na análise AST

---

## 💾 Como os CSVs São Estruturados

### `1st_step_repositorios_selecionados.csv`
```csv
Repo,URL
KayoRonald/euajudo-back-end,https://github.com/KayoRonald/euajudo-back-end.git
...
```

### `results_ast_analysis.csv`
```csv
Repo,URL,File,Line,Type,Description
KayoRonald/euajudo-back-end,https://...,src/shared/http/server.ts,15,INSECURE_CORS,...
...
```

### `results_audit.csv`
```csv
Repo,File,Line,Type,Description,Status,ReviewerNote
KayoRonald/euajudo-back-end,src/shared/http/server.ts,15,INSECURE_CORS,...,INCORRETO,Manual audit done
...
```

---

## 🔧 Personalizações Possíveis

### Modificar o Script Python
Se quiser adicionar novas métricas, editar `analyze_results.py`:

```python
# Adicionar nova métrica
nova_metrica = df[df['Status'] == 'NOVO_STATUS'].count()

# Criar novo gráfico
fig, ax = plt.subplots()
ax.bar(labels, values)
ax.set_title('Meu Novo Gráfico')
plt.savefig('novo_grafico.png')
```

### Gerar Relatório em PDF
```bash
# Instalar dependência
pip3 install pdfkit wkhtmltopdf

# Converter HTML para PDF
pdfkit.from_file('relatorio_analise.html', 'relatorio_final.pdf')
```

---

## 📋 Checklist para Apresentação

- [ ] Abrir `relatorio_analise.html` no navegador
- [ ] Mostrar gráficos em `analise_completa_1.png` e `analise_completa_2.png`
- [ ] Destacar métrica de acurácia (33.5% verdadeiros positivos)
- [ ] Mencionar problema com HARDCODED_SECRET (76.5% falsos positivos)
- [ ] Ressaltar força do DB_AUTO_SYNC (85.7% acurácia)
- [ ] Discutir recomendações de melhoria

---

## 🎓 Conclusão

O VulnSniffer demonstra ser uma ferramenta promissora para detecção de vulnerabilidades em repositórios TypeScript, especialmente para:

✅ **Muito Eficaz:**
- Detecção de DB_AUTO_SYNC (85.7%)
- Detecção de NESTJS_MASS_ASSIGNMENT (65.2%)

⚠️ **Requer Melhoria:**
- Redução de falsos positivos em HARDCODED_SECRET
- Refinamento de critérios de seleção

📈 **Próximos Passos:**
1. Implementar filtros para excluir dados de teste
2. Melhorar análise de contexto no AST
3. Expandir tipos de vulnerabilidades detectadas
4. Aumentar base de repositórios para validação

---

## 📞 Informações Técnicas

**Linguagem:** Python 3.x  
**Dependências:** pandas, matplotlib, seaborn  
**Formato de Saída:** PNG (300 DPI), HTML (responsivo), Markdown  
**Tempo de Execução:** ~5-10 segundos  

---

*Desenvolvido com ❤️ para análise de segurança em repositórios TypeScript acadêmicos e profissionais.*
