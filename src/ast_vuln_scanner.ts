import * as ts from "typescript";
import simpleGit from "simple-git";
import * as fs from "fs";
import * as path from "path";
import * as readline from "readline";
import { glob } from "glob";

console.log(__dirname)

const INPUT_CSV = path.join(__dirname, "csv/results_mining.csv");
const OUTPUT_CSV = path.join(__dirname, "csv/results_ast_analysis.csv");
const TEMP_DIR = path.join(__dirname, "temp_repos");

const git = simpleGit();

interface Finding {
    type: string;
    description: string;
    line: number;
}

class VulnerabilityScanner {
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
            return !text.includes("process.env") && text.length > 3;
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
    console.log("=== Starting VulnSniffer - Unified AST Analysis ===");

    if (!fs.existsSync(OUTPUT_CSV)) {
        fs.writeFileSync(OUTPUT_CSV, "Repo,URL,File,Line,Type,Description\n");
    }

    const fileStream = fs.createReadStream(INPUT_CSV);
    const rl = readline.createInterface({ input: fileStream, crlfDelay: Infinity });

    let headerSkipped = false;

    for await (const line of rl) {
        if (!headerSkipped) { headerSkipped = true; continue; }

        const cols = line.split(/,(?=(?:(?:[^"]*"){2})*[^"]*$)/);
        const [repoName, repoUrl] = [cols[0], cols[1]];

        if (!repoUrl || !repoUrl.startsWith("http")) continue;

        const localPath = path.join(TEMP_DIR, repoName.replace("/", "_"));

        try {
            if (fs.existsSync(localPath)) fs.rmSync(localPath, { recursive: true, force: true });
            await git.clone(repoUrl, localPath, ["--depth", "1"]);

            const tsFiles = await glob(`${localPath}/**/*.ts`, { 
                ignore: ['**/node_modules/**', '**/*.spec.ts', '**/*.test.ts', '**/*.d.ts'] 
            });

            for (const file of tsFiles) {
                const content = fs.readFileSync(file, "utf-8");
                const sourceFile = ts.createSourceFile(file, content, ts.ScriptTarget.Latest, true);
                
                const scanner = new VulnerabilityScanner(sourceFile);
                const results = scanner.scan();

                results.forEach(issue => {
                    const relativePath = path.relative(localPath, file);
                    console.log(`   ⚠️  [${issue.type}] in ${repoName}: ${relativePath}:${issue.line}`);
                    const csvLine = `"${repoName}","${repoUrl}","${relativePath}",${issue.line},"${issue.type}","${issue.description}"\n`;
                    fs.appendFileSync(OUTPUT_CSV, csvLine);
                });
            }
        } catch (err: any) {
            console.error(`   ❌ Error processing ${repoName}: ${err.message}`);
        } finally {
            if (fs.existsSync(localPath)) fs.rmSync(localPath, { recursive: true, force: true });
        }
    }
    console.log("\n=== Analysis Finished ===");
}

main();