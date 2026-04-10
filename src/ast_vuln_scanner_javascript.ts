import * as ts from "typescript";
import simpleGit from "simple-git";
import * as fs from "fs";
import * as path from "path";
import * as readline from "readline";
import { glob } from "glob";

console.log(__dirname);

const INPUT_CSV = path.join(__dirname, "../csv/results_mining_javascript.csv");
const OUTPUT_CSV = path.join(__dirname, "../csv/results_ast_analysis_javascript.csv");
const TEMP_DIR = path.join(__dirname, "temp_repos_js");

const git = simpleGit();

interface Finding {
    type: string;
    description: string;
    line: number;
}

class JavaScriptVulnerabilityScanner {
    private findings: Finding[] = [];
    private sourceFile: ts.SourceFile;

    constructor(sourceFile: ts.SourceFile) {
        this.sourceFile = sourceFile;
    }

    public scan(): Finding[] {
        this.visit(this.sourceFile);
        return this.findings;
    }

    private addFinding(node: ts.Node, type: string, description: string) {
        const { line } = this.sourceFile.getLineAndCharacterOfPosition(node.getStart());
        this.findings.push({ type, description, line: line + 1 });
    }

    private isHardcoded(node: ts.Node): boolean {
        // Checks if it's a raw string and NOT an environment variable access
        if (ts.isStringLiteral(node)) {
            const text = node.text.toLowerCase();
            return !text.includes("process.env") && !text.includes("env.") && text.length > 3;
        }
        return false;
    }

    private visit(node: ts.Node) {
        // 1. Check Property Assignments (Objects, Config files, TypeORM)
        if (ts.isPropertyAssignment(node)) {
            const propName = node.name.getText(this.sourceFile).replace(/['"`]/g, "");
            const initializer = node.initializer;
            const value = initializer.getText(this.sourceFile).replace(/['"`]/g, "");

            // Hardcoded Secrets
            const sensitiveKeys = ["secret", "password", "apikey", "jwt", "token"];
            if (sensitiveKeys.some(key => propName.toLowerCase().includes(key)) && this.isHardcoded(initializer)) {
                this.addFinding(node, "HARDCODED_SECRET", `Potential hardcoded secret in property: ${propName}`);
            }

            // Database & Debug Misconfigs
            if (propName === "synchronize" && value === "true") {
                this.addFinding(node, "DB_AUTO_SYNC", "Database synchronization enabled (Risk of data loss)");
            }
            if (propName === "debug" && value === "true") {
                this.addFinding(node, "DEBUG_MODE_ON", "Debug mode enabled in configuration");
            }
        }

        // 2. Check Function Calls (Express/NestJS Middlewares)
        if (ts.isCallExpression(node)) {
            const callText = node.expression.getText(this.sourceFile);

            // Insecure CORS
            if (callText.includes("cors") || callText.includes("enableCors")) {
                const args = node.arguments;
                if (args.length === 0 || args.some(arg => arg.getText(this.sourceFile).includes("*"))) {
                    this.addFinding(node, "INSECURE_CORS", "Permissive CORS policy (Wildcard detected)");
                }
            }
        }

        // 3. Check New Expressions (NestJS Pipes)
        if (ts.isNewExpression(node)) {
            const className = node.expression.getText(this.sourceFile);
            if (className === "ValidationPipe") {
                const arg = node.arguments?.[0];
                if (!arg || !arg.getText(this.sourceFile).includes("whitelist: true")) {
                    this.addFinding(node, "NESTJS_MASS_ASSIGNMENT", "ValidationPipe missing 'whitelist: true'");
                }
            }
        }

        ts.forEachChild(node, (child) => this.visit(child));
    }
}

async function main() {
    console.log("=== Starting VulnSniffer - JavaScript AST Analysis ===");

    if (!fs.existsSync(OUTPUT_CSV)) {
        fs.writeFileSync(OUTPUT_CSV, "Repo,URL,File,Line,Type,Description\n");
    }

    const fileStream = fs.createReadStream(INPUT_CSV);
    const rl = readline.createInterface({ input: fileStream, crlfDelay: Infinity });

    let headerSkipped = false;
    let totalRepos = 0;
    let processedRepos = 0;
    let foundVulnerabilities = 0;

    for await (const line of rl) {
        if (!headerSkipped) { headerSkipped = true; continue; }

        const cols = line.split(/,(?=(?:(?:[^"]*"){2})*[^"]*$)/);
        const [repoName, repoUrl] = [cols[0].replace(/^"/, "").replace(/"$/, ""), 
                                      cols[1].replace(/^"/, "").replace(/"$/, "")];

        if (!repoUrl || !repoUrl.startsWith("http")) continue;

        totalRepos++;
        const localPath = path.join(TEMP_DIR, repoName.replace(/\//g, "_"));

        try {
            if (fs.existsSync(localPath)) fs.rmSync(localPath, { recursive: true, force: true });
            
            console.log(`\n📥 [${repoName}] Cloning repository...`);
            await git.clone(repoUrl, localPath, ["--depth", "1"]);
            processedRepos++;

            // Buscar arquivos JavaScript e TypeScript
            const jsFiles = await glob(`${localPath}/**/*.{js,jsx,ts,tsx}`, { 
                ignore: ['**/node_modules/**', '**/*.spec.ts', '**/*.test.ts', '**/*.spec.js', 
                        '**/*.test.js', '**/*.d.ts', '**/dist/**', '**/build/**']
            });

            if (jsFiles.length === 0) {
                console.log(`   ⚠️  No JavaScript/TypeScript files found`);
                continue;
            }

            console.log(`   ✅ Found ${jsFiles.length} files to analyze`);

            for (const file of jsFiles) {
                try {
                    const content = fs.readFileSync(file, "utf-8");
                    const sourceFile = ts.createSourceFile(
                        file, 
                        content, 
                        ts.ScriptTarget.Latest, 
                        true,
                        ts.ScriptKind.JS
                    );
                    
                    const scanner = new JavaScriptVulnerabilityScanner(sourceFile);
                    const results = scanner.scan();

                    results.forEach(issue => {
                        const relativePath = path.relative(localPath, file);
                        console.log(`      ⚠️  [${issue.type}] ${relativePath}:${issue.line}`);
                        const csvLine = `"${repoName}","${repoUrl}","${relativePath}",${issue.line},"${issue.type}","${issue.description}"\n`;
                        fs.appendFileSync(OUTPUT_CSV, csvLine);
                        foundVulnerabilities++;
                    });
                } catch (fileErr: any) {
                    console.error(`      ❌ Error analyzing file: ${fileErr.message}`);
                }
            }
        } catch (err: any) {
            console.error(`   ❌ Error processing ${repoName}: ${err.message}`);
        } finally {
            if (fs.existsSync(localPath)) fs.rmSync(localPath, { recursive: true, force: true });
        }
    }

    console.log("\n" + "=".repeat(70));
    console.log("=== JavaScript AST Analysis Finished ===");
    console.log(`Total Repositories: ${totalRepos}`);
    console.log(`Successfully Processed: ${processedRepos}`);
    console.log(`Vulnerabilities Found: ${foundVulnerabilities}`);
    console.log(`Output CSV: ${OUTPUT_CSV}`);
    console.log("=".repeat(70));
}

if (!fs.existsSync(TEMP_DIR)) fs.mkdirSync(TEMP_DIR, { recursive: true });
main();
