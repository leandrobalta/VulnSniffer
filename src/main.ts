import * as ts from "typescript";
import simpleGit from "simple-git";
import * as fs from "fs";
import * as path from "path";
import * as readline from "readline";
import { glob } from "glob";


const INPUT_CSV = path.join(__dirname, "repositorios_selecionados.csv");
const OUTPUT_CSV = path.join(__dirname, "resultados_analise_nativo.csv");
const TEMP_DIR = path.join(__dirname, "temp_repos");

const VULN_PATTERNS = [
    {
        id: "DANGEROUS_CORS",
        description: "CORS permissivo (*)",
        properties: ["origin"],
        values: ["*", "true"],
        checkType: "exact"
    },
    {
        id: "TYPEORM_SYNC",
        description: "TypeORM synchronize: true",
        properties: ["synchronize"],
        values: ["true"],
        checkType: "exact"
    },
    {
        id: "HARDCODED_SECRET",
        description: "Segredo chumbado no código",
        properties: ["secret", "password", "apiKey", "api_key", "privateKey"],
        checkType: "hardcoded_string" 
    },
    {
        id: "DEBUG_MODE",
        description: "Modo debug ativado",
        properties: ["debug"],
        values: ["true"],
        checkType: "exact"
    }
];


const git = simpleGit();

const removeDir = (dirPath: string) => {
    if (fs.existsSync(dirPath)) {
        fs.rmSync(dirPath, { recursive: true, force: true });
    }
};

function visitNode(node: ts.Node, sourceFile: ts.SourceFile, findings: string[], filePath: string) {
    
    if (ts.isPropertyAssignment(node)) {
        const nameNode = node.name;
        let propName = "";

        if (ts.isIdentifier(nameNode) || ts.isStringLiteral(nameNode)) {
            propName = nameNode.text;
        }

        const initializer = node.initializer;
        
        const valueText = initializer.getText(sourceFile).replace(/['"`]/g, ""); 

        VULN_PATTERNS.forEach(pattern => {
            if (pattern.properties.includes(propName)) {
                
                if (pattern.checkType === "hardcoded_string") {
                    if (ts.isStringLiteral(initializer) && !valueText.includes("env")) {
                        if (valueText.length > 5) { 
                            findings.push(`[${pattern.id}] ${propName} encontrado com valor fixo em ${path.basename(filePath)}`);
                        }
                    }
                }
                
                else if (pattern.values && pattern.values.includes(valueText)) {
                    if (
                        initializer.kind === ts.SyntaxKind.TrueKeyword || 
                        ts.isStringLiteral(initializer)
                    ) {
                        findings.push(`[${pattern.id}] Configuração '${propName}: ${valueText}' detectada em ${path.basename(filePath)}`);
                    }
                }
            }
        });
    }

    ts.forEachChild(node, (child) => visitNode(child, sourceFile, findings, filePath));
}

function scanFile(filePath: string): string[] {
    const findings: string[] = [];
    
    try {
        const fileContent = fs.readFileSync(filePath, "utf-8");
        
        const sourceFile = ts.createSourceFile(
            filePath,
            fileContent,
            ts.ScriptTarget.Latest, // Versão do ECMA
            true // setParentNodes (útil se precisarmos subir na árvore, mas consome mais memória)
        );

        visitNode(sourceFile, sourceFile, findings, filePath);
        
    } catch (err) {
        console.error(`Erro ao ler arquivo ${filePath}:`, err);
    }
    
    return findings;
}


async function main() {
    console.log("=== Iniciando VulnSniffer - Análise AST Nativa ===");

    if (!fs.existsSync(INPUT_CSV)) {
        console.error(`Arquivo de entrada não encontrado: ${INPUT_CSV}`);
        return;
    }

    if (!fs.existsSync(OUTPUT_CSV)) {
        fs.writeFileSync(OUTPUT_CSV, "RepoURL,Stars,Framework,Vulnerabilidade,Detalhes\n");
    }

    const fileStream = fs.createReadStream(INPUT_CSV);
    const rl = readline.createInterface({ input: fileStream, crlfDelay: Infinity });

    let headerSkipped = false;

    for await (const line of rl) {
        if (!headerSkipped) {
            headerSkipped = true;
            continue;
        }

        const cols = line.split(/,(?=(?:(?:[^"]*"){2})*[^"]*$)/);
        const repoName = cols[0];
        const repoUrl = cols[1];
        const stars = cols[2];
        const framework = cols[3];

        if (!repoUrl || !repoUrl.startsWith("http")) continue;

        console.log(`\n>>> Analisando: ${repoName}`);
        const localPath = path.join(TEMP_DIR, repoName.replace("/", "_"));

        try {
            removeDir(localPath);
            await git.clone(repoUrl, localPath, ["--depth", "1"]);

            const tsFiles = await glob(`${localPath}/**/*.ts`, { 
                ignore: [
                    '**/node_modules/**', 
                    '**/*.spec.ts', 
                    '**/*.test.ts', 
                    '**/*.d.ts'
                ],
                windowsPathsNoEscape: true 
            });

            console.log(`   Arquivos encontrados: ${tsFiles.length}`);
            let vulnFound = false;

            for (const file of tsFiles) {
                const issues = scanFile(file);
                
                if (issues.length > 0) {
                    vulnFound = true;
                    for (const issue of issues) {
                        console.log(`   ⚠️  ${issue}`);
                        const csvLine = `${repoUrl},${stars},${framework},SIM,"${issue.replace(/"/g, "'")}"\n`;
                        fs.appendFileSync(OUTPUT_CSV, csvLine);
                    }
                }
            }

            if (!vulnFound) {
                const csvLine = `${repoUrl},${stars},${framework},NAO,Clean\n`;
                fs.appendFileSync(OUTPUT_CSV, csvLine);
            }

        } catch (error: any) {
            console.error(`   ❌ Erro: ${error.message}`);
        } finally {
            removeDir(localPath);
        }
    }
    
    console.log("\n=== Finalizado ===");
}

main();