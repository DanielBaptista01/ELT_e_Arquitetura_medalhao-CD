-- EP01 - CAMADA GOLD
-- Tabelas materializadas no grão de cada pergunta de negócio.

CREATE SCHEMA IF NOT EXISTS gold;

CREATE TABLE IF NOT EXISTS gold.ranking_pokemon (
    pokemon_csv_id      INTEGER PRIMARY KEY,
    pokemon_nome        TEXT NOT NULL,
    total_combates      INTEGER NOT NULL,
    vitorias            INTEGER NOT NULL,
    taxa_vitorias       NUMERIC(8,6) NOT NULL
);

CREATE TABLE IF NOT EXISTS gold.taxa_vitorias_por_tipo (
    tipo                TEXT PRIMARY KEY,
    total_combates      INTEGER NOT NULL,
    vitorias            INTEGER NOT NULL,
    taxa_vitorias       NUMERIC(8,6) NOT NULL
);

CREATE TABLE IF NOT EXISTS gold.taxa_vitorias_por_faixa_velocidade (
    ordem_faixa         SMALLINT PRIMARY KEY,
    faixa_velocidade    TEXT NOT NULL UNIQUE,
    total_confrontos    INTEGER NOT NULL,
    vitorias            INTEGER NOT NULL,
    taxa_vitorias       NUMERIC(8,6) NOT NULL
);

CREATE TABLE IF NOT EXISTS gold.taxa_vitorias_por_multiplicador (
    multiplicador       NUMERIC(4,2) PRIMARY KEY,
    total_confrontos    INTEGER NOT NULL,
    vitorias            INTEGER NOT NULL,
    taxa_vitorias       NUMERIC(8,6) NOT NULL
);

CREATE TABLE IF NOT EXISTS gold.matriz_confronto (
    tipo_atacante               TEXT NOT NULL,
    tipo_defensor               TEXT NOT NULL,
    total_confrontos            INTEGER NOT NULL,
    vitorias                    INTEGER NOT NULL,
    taxa_vitorias               NUMERIC(8,6),
    multiplicador_efetividade   NUMERIC(4,2) NOT NULL,
    expectativa                 TEXT NOT NULL,
    diverge_da_efetividade      BOOLEAN,
    PRIMARY KEY (tipo_atacante, tipo_defensor)
);

-- Análise 8 proposta pelo grupo: vantagem de atacar primeiro.
CREATE TABLE IF NOT EXISTS gold.vantagem_primeiro_ataque (
    ordem_ataque        TEXT PRIMARY KEY,
    total_confrontos    INTEGER NOT NULL,
    vitorias            INTEGER NOT NULL,
    taxa_vitorias       NUMERIC(8,6) NOT NULL
);
