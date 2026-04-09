import * as fs from "fs";
import * as path from "path";
import simpleGit from "simple-git";
import csv from "csv-parser";
import { highlight } from "cli-highlight";
import { prompt } from "enquirer";

console.log(__dirname);

const AUDIT_CSV = path.join(__dirname, "../csv/results_audit.csv");
const TEMP_DIR = path.join(__dirname, "audit_repos");

const git = simpleGit();

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

/**
 * Carrega registros com status 'DEPENDE' do CSV
 */
function getDependeRecords(): any[] {
    const dependeRecords: any[] = [];
    
    if (!fs.existsSync(AUDIT_CSV)) {
        console.error("❌ results_audit.csv not found!");
        return dependeRecords;
    }
    
    const content = fs.readFileSync(AUDIT_CSV, "utf-8");
    const lines = content.split("\n");
    
    for (let i = 1; i < lines.length; i++) {
        const line = lines[i].trim();
        if (!line) continue;
        
        // Parse CSV com suporte a aspas
        const match = line.match(/"([^"]+)","([^"]+)",(\d+),"([^"]+)","([^"]*)","([^"]+)","([^"]*)"/);
        if (match) {
            const [, repo, file, lineNum, type, description, status, reviewerNote] = match;
            
            if (status === "DEPENDE") {
                dependeRecords.push({
                    Repo: repo,
                    File: file,
                    Line: parseInt(lineNum),
                    Type: type,
                    Description: description,
                    Status: status,
                    ReviewerNote: reviewerNote,
                    LineIndex: i // Armazena o índice da linha original para atualização
                });
            }
        }
    }
    
    return dependeRecords;
}

/**
 * Atualiza um registro específico no CSV
 */
function updateDependeRecord(lineIndex: number, newStatus: string, newNote: string): void {
    const content = fs.readFileSync(AUDIT_CSV, "utf-8");
    const lines = content.split("\n");
    
    if (lineIndex >= 0 && lineIndex < lines.length) {
        const line = lines[lineIndex];
        const match = line.match(/"([^"]+)","([^"]+)",(\d+),"([^"]+)","([^"]*)","([^"]+)","([^"]*)"/);
        
        if (match) {
            const [, repo, file, lineNum, type, description] = match;
            lines[lineIndex] = `"${repo}","${file}",${lineNum},"${type}","${description}","${newStatus}","${newNote}"`;
            fs.writeFileSync(AUDIT_CSV, lines.join("\n"));
        }
    }
}

async function startReview() {
    const dependeRecords = getDependeRecords();
    
    if (dependeRecords.length === 0) {
        console.log("✅ No records with status 'DEPENDE' found!");
        return;
    }
    
    console.log(`\n📊 Found ${dependeRecords.length} records with status 'DEPENDE'\n`);
    
    let processedCount = 0;

    for (const record of dependeRecords) {
        const { Repo, File, Line, Type, Description, ReviewerNote, LineIndex } = record;
        const repoPath = path.join(TEMP_DIR, Repo.replace("/", "_"));
        const lineNum = parseInt(Line);
        processedCount++;

        try {
            // 1. Clonagem (se necessário)
            if (!fs.existsSync(repoPath)) {
                console.log(`\n📥 [${Repo}] Downloading repository...`);
                await git.clone(`https://github.com/${Repo}.git`, repoPath, ["--depth", "1"]);
            }

            // --- PASSO 1: CONTEXTO DO PROJETO ---
            console.clear();
            console.log(`\n================================================================`);
            console.log(`📋 STEP 1: PROJECT CONTEXT`);
            console.log(`Repository: ${Repo}`);
            console.log(`Review ${processedCount}/${dependeRecords.length} (Status: DEPENDE)`);
            console.log(`================================================================\n`);
            
            console.log(`🔍 Finding Details:`);
            console.log(`   Type: ${Type}`);
            console.log(`   Location: ${File}:${Line}`);
            console.log(`   Description: ${Description || "N/A"}`);
            console.log(`   Previous Note: ${ReviewerNote || "N/A"}\n`);
            
            const readme = getReadme(repoPath);
            console.log("--- 📖 README.md ---");
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
            console.log(`🔎 STEP 2: CODE ANALYSIS`);
            console.log(`Repository: ${Repo}`);
            console.log(`FILE: ${File} | LINE: ${Line}`);
            console.log(`VULN TYPE: ${Type}`);
            console.log(`================================================================\n`);

            const fullPath = path.join(repoPath, File);
            if (fs.existsSync(fullPath)) {
                const markedCode = getFullFileWithMarker(fullPath, lineNum);
                console.log(highlight(markedCode, { language: "typescript" }));
                
                console.log("\n----------------------------------------------------------------");

                // --- PASSO 3: RECLASSIFICAÇÃO ---
                const responseStatus = await prompt<{ status: string }>({
                    type: 'select',
                    name: 'status',
                    message: `[${Repo}] Update Classification:`,
                    choices: [
                        { name: 'CORRETO', message: '✅ Correto (É uma vulnerabilidade)' },
                        { name: 'INCORRETO', message: '❌ Incorreto (Falso positivo/Não é vulnerabilidade)' },
                        { name: 'NAO_SE_APLICA', message: '⏹️ Não se aplica (Fora do escopo)' },
                        { name: 'DEPENDE', message: '⚠️ Manter como DEPENDE (Precisa mais análise)' },
                        { name: 'SKIP', message: '⏭️ Pular este item' }
                    ]
                });

                const finalStatus = responseStatus.status;

                if (finalStatus !== 'SKIP') {
                    // Se escolher DEPENDE, pede uma nota de revisão
                    let reviewNote = "";
                    if (finalStatus === 'DEPENDE') {
                        const noteResponse = await prompt<{ note: string }>({
                            type: 'input',
                            name: 'note',
                            message: `[${Repo}] Add review note for next analysis:`,
                            initial: ReviewerNote || ""
                        });
                        reviewNote = noteResponse.note;
                    }

                    updateDependeRecord(LineIndex, finalStatus, reviewNote);
                    console.log(`\n✅ [${Repo}] Updated to: ${finalStatus}`);
                } else {
                    console.log(`\n⏭️  [${Repo}] Skipped by user`);
                }
            } else {
                console.log(`❌ [${Repo}] File not found locally: ${fullPath}`);
                await new Promise(r => setTimeout(r, 2000));
            }

        } catch (err: any) {
            console.error(`❌ [${Repo}] Error reviewing: ${err.message}`);
        } finally {
            // Não deleta repositórios para manter cache
            // if (fs.existsSync(repoPath)) fs.rmSync(repoPath, { recursive: true, force: true });
        }
    }
    
    console.log("\n================================================================");
    console.log(`✨ Review Session Finished`);
    console.log(`Total DEPENDE records processed: ${processedCount}`);
    console.log(`================================================================\n`);
}

if (!fs.existsSync(TEMP_DIR)) fs.mkdirSync(TEMP_DIR);
startReview();
