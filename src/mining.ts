import { Octokit } from "octokit";
import * as fs from "fs";
import * as path from "path";
import * as dotenv from "dotenv";

dotenv.config();

const GITHUB_TOKEN = process.env.GITHUB_TOKEN
const OUTPUT_FILE = path.join(__dirname, "repositorios_selecionados.csv");

const SEARCH_QUERIES = [
    // tópicos específicos
    "topic:tcc language:TypeScript",
    "topic:trabalho de conclusao de curso language:TypeScript",
    "topic:trabalho de fim de graduacao language:TypeScript",
    "topic:tfg language:TypeScript",
    "topic:tese language:TypeScript",
    "topic:monografia language:TypeScript",
    "topic:universidade language:TypeScript",
    "topic:academico language:TypeScript",
    "topic:faculdade language:TypeScript",

    // busca livre
    '"trabalho de conclusao de curso" language:TypeScript',
    '"projeto final" universidade language:TypeScript',
    '"academico" language:TypeScript',
    '"monografia" language:TypeScript',
    '"trabalho de fim de graduacao" language:TypeScript',
    '"tfg" language:TypeScript',
    '"tese" language:TypeScript',
    '"monografia" language:TypeScript',
    '"universidade" language:TypeScript',
    '"academico" language:TypeScript',
    '"faculdade" language:TypeScript'
];

const BACKEND_INDICATORS = [
    "express",
    "nestjs", "@nestjs/core",
    "fastify",
    "koa",
    "typeorm",
    "prisma",
    "mongoose",
    "sequelize"
];

const MAX_CHECK_PER_QUERY = 100;


if (!GITHUB_TOKEN) {
    console.error("ERRO: O GITHUB_TOKEN não está definido. Crie um arquivo .env ou defina a variável.");
    process.exit(1);
}

const octokit = new Octokit({ auth: GITHUB_TOKEN });

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

interface AnalysisResult {
    isBackend: boolean;
    info: string;
}

async function analyzeRepo(owner: string, repo: string): Promise<AnalysisResult> {
    try {
        const { data } = await octokit.rest.repos.getContent({
            owner,
            repo,
            path: "package.json",
        });

        if (!("content" in data)) {
            return { isBackend: false, info: "Não foi possível ler o conteúdo do arquivo" };
        }

        const contentEncoded = data.content;
        const contentDecoded = Buffer.from(contentEncoded, "base64").toString("utf-8");
        const packageJson = JSON.parse(contentDecoded);

        const dependencies = { ...packageJson.dependencies, ...packageJson.devDependencies };
        const depKeys = Object.keys(dependencies);

        for (const indicator of BACKEND_INDICATORS) {
            if (depKeys.some(dep => dep.includes(indicator))) {

                const hasReact = depKeys.some(d => d.includes("react"));
                const hasNest = depKeys.some(d => d.includes("nestjs"));

                if (hasReact && !hasNest) {
                    return { isBackend: false, info: "Ignorado (Possível Frontend/Fullstack Monolítico)" };
                }

                return { isBackend: true, info: `Backend Detectado (${indicator})` };
            }
        }

        return { isBackend: false, info: "Nenhuma lib de backend encontrada" };

    } catch (error: any) {
        if (error.status === 404) {
            return { isBackend: false, info: "package.json não encontrado na raiz" };
        }
        return { isBackend: false, info: `Erro na leitura: ${error.message}` };
    }
}

async function main() {
    console.log("=== Iniciando Mineração (MSR) - TypeScript Backend ===");

    if (!fs.existsSync(OUTPUT_FILE)) {
        fs.writeFileSync(OUTPUT_FILE, "Nome,URL,Stars,Framework,Descricao\n");
    }

    const processedIds = new Set<number>();

    for (const query of SEARCH_QUERIES) {
        console.log(`\n---> Buscando por: '${query}'`);

        try {
            const iterator = octokit.paginate.iterator(octokit.rest.search.repos, {
                q: query + " stars:>0",
                sort: "updated",
                order: "desc",
                per_page: 30,
            });

            let checkedCount = 0;

            for await (const { data: repos } of iterator) {
                for (const repo of repos) {
                    if (checkedCount >= MAX_CHECK_PER_QUERY) break;
                    if (processedIds.has(repo.id)) continue;

                    processedIds.add(repo.id);
                    checkedCount++;

                    process.stdout.write(`Verificando: ${repo.full_name}... `);

                    await sleep(1000);

                    const result = await analyzeRepo(repo.owner!.login, repo.name);

                    if (result.isBackend) {
                        console.log(`✅ [ACEITO] - ${result.info}`);

                        const safeDesc = (repo.description || "").replace(/,/g, " ").replace(/\n/g, " ");

                        const csvLine = `${repo.full_name},${repo.clone_url},${repo.stargazers_count},${result.info},"${safeDesc}"\n`;
                        fs.appendFileSync(OUTPUT_FILE, csvLine);

                    } else {
                        console.log(`❌ [IGNORADO] - ${result.info}`);
                    }
                }
                if (checkedCount >= MAX_CHECK_PER_QUERY) break;
            }

        } catch (error: any) {
            if (error.status === 403 || error.status === 429) {
                console.log("\n⚠️ Limite da API atingido. Aguardando 60 segundos...");
                await sleep(60000);
            } else {
                console.error(`\nErro na busca: ${error.message}`);
            }
        }
    }

    console.log(`\n=== Finalizado ===`);
    console.log(`Resultados salvos em: ${OUTPUT_FILE}`);
}

main();