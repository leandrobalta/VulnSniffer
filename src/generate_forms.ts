import * as fs from "fs";
import * as path from "path";
import csv from "csv-parser";

// Configuração de caminhos baseada no seu ambiente
const AUDIT_CSV = path.join(__dirname, "../csv/results_audit.csv");
const MINING_CSV = path.join(__dirname, "../csv/results_mining.csv");
const REPOS_DIR = path.join(__dirname, "audit_repos"); 
const OUTPUT_MD = path.join(__dirname, "dados_questionario.md");

interface AuditRecord {
    Repo: string;
    File: string;
    Line: string;
    Type: string;
    Description: string;
    Status: string;
}

interface MiningRecord {
    Nome: string;
    Framework: string;
    Descricao: string;
    URL: string;
}

// Carrega as descrições e metadados originais da mineração
function carregarMetadadosMineracao(): Promise<Map<string, MiningRecord>> {
    return new Promise((resolve) => {
        const mapa = new Map<string, MiningRecord>();
        if (!fs.existsSync(MINING_CSV)) {
            resolve(mapa);
            return;
        }
        fs.createReadStream(MINING_CSV)
            .pipe(csv())
            .on("data", (data: any) => {
                mapa.set(data.Nome, {
                    Nome: data.Nome,
                    Framework: data.Framework || "Não detectado",
                    Descricao: data.Descricao || "Sem descrição disponível.",
                    URL: data.URL || ""
                });
            })
            .on("end", () => resolve(mapa));
    });
}

// Extrai o trecho de código baseado na linha do alerta (5 linhas antes e 5 depois)
function extrairTrechoCodigo(repo: string, filePath: string, targetLine: number): string {
    const fullPath = path.join(REPOS_DIR, repo, filePath);
    if (!fs.existsSync(fullPath)) {
        return `// [ERRO] Arquivo não encontrado localmente: ${filePath}`;
    }

    const content = fs.readFileSync(fullPath, "utf-8");
    const lines = content.split("\n");
    
    // Ajuste para índice 0 do array
    const centerIndex = targetLine - 1;
    const start = Math.max(0, centerIndex - 5);
    const end = Math.min(lines.length - 1, centerIndex + 5);

    let snippet = "";
    for (let i = start; i <= end; i++) {
        const prefix = (i === centerIndex) ? "👉 " : "   ";
        snippet += `${prefix}${i + 1}: ${lines[i]}\n`;
    }
    return snippet;
}

// Tenta ler as primeiras linhas do README local para dar mais contexto
function obterTrechoReadme(repo: string): string {
    const possíveisNomes = ["README.md", "readme.md", "README.MD"];
    for (const nome of possíveisNomes) {
        const readmePath = path.join(REPOS_DIR, repo, nome);
        if (fs.existsSync(readmePath)) {
            const content = fs.readFileSync(readmePath, "utf-8");
            // Pega os primeiros 600 caracteres para não estourar o tamanho do formulário
            return content.substring(0, 600).trim() + "...";
        }
    }
    return "README local não encontrado.";
}

async function processarQuestionario() {
    console.log("⏳ Carregando dados de mineração e auditoria...");
    const mapaMining = await carregarMetadadosMineracao();
    
    const reposProcessados = new Set<string>();
    let outputContent = "# Dados para o Questionário de Especialista\n\n";
    outputContent += "Utilize este arquivo para copiar e colar os blocos de perguntas no Google Forms.\n\n---\n\n";

    let totalPerguntas = 0;

    fs.createReadStream(AUDIT_CSV)
        .pipe(csv())
        .on("data", (row: AuditRecord) => {
            // Garante a regra: Apenas 1 vulnerabilidade única por Repositório
            if (!reposProcessados.has(row.Repo) && row.Repo && row.File) {
                reposProcessados.add(row.Repo);
                totalPerguntas++;

                const numLinha = parseInt(row.Line, 10);
                const trechoCodigo = extrairTrechoCodigo(row.Repo, row.File, numLinha);
                const dadosMinados = mapaMining.get(row.Repo);
                const trechoReadme = obterTrechoReadme(row.Repo);

                // Monta o bloco formatado em Markdown
                outputContent += `## QUESTÃO ${totalPerguntas}: Repositório [${row.Repo}]\n\n`;
                outputContent += `**Contexto do Projeto (GitHub/Mineração):**\n${dadosMinados ? dadosMinados.Descricao : "Sem descrição."}\n\n`;
                outputContent += `**Framework Utilizado:** ${dadosMinados ? dadosMinados.Framework : "Não identificado"}\n\n`;
                outputContent += `**Link do Repositório:** ${dadosMinados ? dadosMinados.URL : `https://github.com/${row.Repo}`}\n\n`;
                outputContent += `**Resumo do README (Primeiros caracteres):**\n\`\`\`text\n${trechoReadme}\n\`\`\`\n\n`;
                outputContent += `**Alerta Detectado pela AST:** ${row.Type} - ${row.Description}\n`;
                outputContent += `**Arquivo:** \`${row.File}\` (Linha alvo: ${row.Line})\n\n`;
                outputContent += `**Trecho do Código Fonte:**\n\`\`\`typescript\n${trechoCodigo}\`\`\`\n\n`;
                outputContent += `**Sua Classificação (Gabarito Oculto):** ${row.Status}\n\n`;
                outputContent += `**Opções para o Especialista:**\n[ ] CORRETO (Existe vulnerabilidade real)\n[ ] INCORRETO / NÃO SE APLICA (Falso positivo)\n\n`;
                outputContent += "--- \n\n";
            }
        })
        .on("end", () => {
            fs.writeFileSync(OUTPUT_MD, outputContent, "utf-8");
            console.log(`\n✨ Sucesso! Foram geradas ${totalPerguntas} questões únicas.`);
            console.log(`📂 Arquivo salvo em: ${OUTPUT_MD}`);
        });
}

processarQuestionario();