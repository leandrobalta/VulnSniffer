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

console.log(SEARCH_QUERIES)

console.log(SEARCH_QUERIES.map(q => q.replace(/language:TypeScript/g, "language:JavaScript")))