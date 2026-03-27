import * as fs from "fs";
import * as path from "path";
import simpleGit from "simple-git";
import csv from "csv-parser";
import { highlight } from "cli-highlight";
//import { Select } from "enquirer";
import { prompt } from "enquirer";

const INPUT_CSV = "src/results_ast_analysis.csv";
const VALIDATED_CSV = "src/validated_vulnerabilities.csv";
const TEMP_DIR = path.join(__dirname, "audit_repos");

const git = simpleGit();

if (!fs.existsSync(VALIDATED_CSV)) {
    fs.writeFileSync(VALIDATED_CSV, "Repo,File,Line,Type,Description,Status,ReviewerNote\n");
}

/**
 * Busca e lê o README do projeto (tenta variações de extensão)
 */
function getReadme(repoPath: string): string {
    const files = fs.readdirSync(repoPath);
    const readmeFile = files.find(f => f.toLowerCase().startsWith("readme"));
    if (readmeFile) {
        return fs.readFileSync(path.join(repoPath, readmeFile), "utf-8");
    }
    return "No README.md found for this project.";
}

/**
 * Lê o arquivo completo e adiciona um marcador na linha vulnerável
 */
function getFullFileWithMarker(filePath: string, targetLine: number): string {
    const content = fs.readFileSync(filePath, "utf-8");
    const lines = content.split("\n");
    
    return lines.map((lineText, index) => {
        const currentLineNum = index + 1;
        const isTarget = currentLineNum === targetLine;
        const prefix = isTarget ? " 🔥 [VULN] " : "           ";
        return `${prefix}${currentLineNum.toString().padStart(4, ' ')} | ${lineText}`;
    }).join("\n");
}

async function startAudit() {
    const records: any[] = [];
    console.log("--- Loading findings for manual review ---");

    fs.createReadStream(INPUT_CSV)
        .pipe(csv())
        .on("data", (data) => records.push(data))
        .on("end", async () => {
            for (const record of records) {
                const { Repo, URL, File, Line, Type, Description } = record;
                const repoPath = path.join(TEMP_DIR, Repo.replace("/", "_"));
                const lineNum = parseInt(Line);

                try {
                    // 1. Clonagem (se necessário)
                    if (!fs.existsSync(repoPath)) {
                        console.log(`\nDownloading ${Repo}...`);
                        await git.clone(URL, repoPath, ["--depth", "1"]);
                    }

                    // --- PASSO 1: CONTEXTO DO PROJETO ---
                    console.clear();
                    console.log(`\n================================================================`);
                    console.log(`STEP 1: PROJECT CONTEXT - ${Repo}`);
                    console.log(`CSV Description: ${Description || "N/A"}`);
                    console.log(`================================================================\n`);
                    
                    const readme = getReadme(repoPath);
                    console.log("--- README.md ---");
                    // Mostra apenas os primeiros 1000 caracteres do README para não inundar o terminal
                    console.log(readme.substring(0, 1500) + (readme.length > 1500 ? "\n... (truncated)" : ""));
                    
                    await prompt({
                        type: 'select',
                        name: 'ready',
                        message: 'Read context. Ready to see the code?',
                        choices: [{ name: 'yes', message: 'Show Code & Vulnerability' }]
                    });

                    // --- PASSO 2: ANÁLISE DO CÓDIGO ---
                    console.clear();
                    console.log(`\n================================================================`);
                    console.log(`STEP 2: CODE ANALYSIS`);
                    console.log(`FILE: ${File} | LINE: ${Line}`);
                    console.log(`VULN TYPE: ${Type}`);
                    console.log(`================================================================\n`);

                    const fullPath = path.join(repoPath, File);
                    if (fs.existsSync(fullPath)) {
                        const markedCode = getFullFileWithMarker(fullPath, lineNum);
                        console.log(highlight(markedCode, { language: "typescript" }));
                        
                        console.log("\n----------------------------------------------------------------");

                        // --- PASSO 3: CLASSIFICAÇÃO ---
                        const response = await prompt<{ status: string }>({
                            type: 'select',
                            name: 'status',
                            message: 'Final Classification:',
                            choices: [
                                { name: 'CORRETO', message: '✅ Correto (É uma vulnerabilidade)' },
                                { name: 'INCORRETO', message: '❌ Incorreto (Falso positivo/Não é vulnerabilidade)' },
                                { name: 'DEPENDE', message: '⚠️ Depende (É vulnerabilidade, mas pode não se aplicar ao estudo)' },
                                { name: 'NAO_SE_APLICA', message: '⏹️ Não se aplica (Independente do resultado, fora do escopo)' },
                                { name: 'SKIP', message: '⏭️ Pular este item' }
                            ]
                        });

                        const status = response.status;

                        if (status !== 'SKIP') {
                            const csvLine = `"${Repo}","${File}",${Line},"${Type}","${Description}","${status}","Manual audit done"\n`;
                            fs.appendFileSync(VALIDATED_CSV, csvLine);
                        }
                    } else {
                        console.log("File not found locally.");
                        await new Promise(r => setTimeout(r, 2000));
                    }

                } catch (err: any) {
                    console.error(`Error auditing ${Repo}: ${err.message}`);
                }
            }
            console.log("\n=== Audit Session Finished ===");
        });
}

if (!fs.existsSync(TEMP_DIR)) fs.mkdirSync(TEMP_DIR);
startAudit();