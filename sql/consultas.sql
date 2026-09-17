-- ============================================================
-- EP01 - CONSULTAS FINAIS
-- Análises 1 e 2: schema silver
-- Análises 3 a 8: leitura direta de UMA tabela gold, sem agregação/junção
-- ============================================================

-- ------------------------------------------------------------
-- ANÁLISE 1
-- Quantidade de Pokémon por tipo primário e geração (matriz).
-- ------------------------------------------------------------
SELECT
    tipo_primario AS tipo,
    COUNT(*) FILTER (WHERE geracao_num = 1) AS geracao_1,
    COUNT(*) FILTER (WHERE geracao_num = 2) AS geracao_2,
    COUNT(*) FILTER (WHERE geracao_num = 3) AS geracao_3,
    COUNT(*) FILTER (WHERE geracao_num = 4) AS geracao_4,
    COUNT(*) FILTER (WHERE geracao_num = 5) AS geracao_5,
    COUNT(*) FILTER (WHERE geracao_num = 6) AS geracao_6,
    COUNT(*) AS total
FROM silver.dim_pokemon
GROUP BY tipo_primario
ORDER BY tipo_primario;


-- ------------------------------------------------------------
-- ANÁLISE 2A
-- Média de cada atributo de status por tipo primário.
-- ------------------------------------------------------------
SELECT
    tipo_primario AS tipo,
    ROUND(AVG(hp), 2) AS hp_medio,
    ROUND(AVG(ataque), 2) AS ataque_medio,
    ROUND(AVG(defesa), 2) AS defesa_media,
    ROUND(AVG(ataque_especial), 2) AS ataque_especial_medio,
    ROUND(AVG(defesa_especial), 2) AS defesa_especial_media,
    ROUND(AVG(velocidade), 2) AS velocidade_media,
    ROUND(AVG((hp + defesa + defesa_especial) / 3.0), 2) AS resistencia_media
FROM silver.dim_pokemon
GROUP BY tipo_primario
ORDER BY tipo_primario;

-- ANÁLISE 2B: tipo de maior velocidade média.
SELECT
    tipo_primario AS tipo,
    ROUND(AVG(velocidade), 2) AS velocidade_media
FROM silver.dim_pokemon
GROUP BY tipo_primario
ORDER BY velocidade_media DESC, tipo
LIMIT 1;

-- ANÁLISE 2C: tipo de maior resistência média.
-- Resistência foi definida pelo grupo como a média simples de HP, Defesa e Defesa Especial.
SELECT
    tipo_primario AS tipo,
    ROUND(AVG((hp + defesa + defesa_especial) / 3.0), 2) AS resistencia_media
FROM silver.dim_pokemon
GROUP BY tipo_primario
ORDER BY resistencia_media DESC, tipo
LIMIT 1;

-- ANÁLISE 2D: verifica se algum tipo lidera simultaneamente os seis atributos médios.
WITH medias AS (
    SELECT
        tipo_primario AS tipo,
        AVG(hp) AS hp,
        AVG(ataque) AS ataque,
        AVG(defesa) AS defesa,
        AVG(ataque_especial) AS ataque_especial,
        AVG(defesa_especial) AS defesa_especial,
        AVG(velocidade) AS velocidade
    FROM silver.dim_pokemon
    GROUP BY tipo_primario
), maximos AS (
    SELECT
        MAX(hp) AS hp,
        MAX(ataque) AS ataque,
        MAX(defesa) AS defesa,
        MAX(ataque_especial) AS ataque_especial,
        MAX(defesa_especial) AS defesa_especial,
        MAX(velocidade) AS velocidade
    FROM medias
)
SELECT m.tipo
FROM medias m
CROSS JOIN maximos x
WHERE m.hp = x.hp
  AND m.ataque = x.ataque
  AND m.defesa = x.defesa
  AND m.ataque_especial = x.ataque_especial
  AND m.defesa_especial = x.defesa_especial
  AND m.velocidade = x.velocidade;


-- ------------------------------------------------------------
-- ANÁLISE 3
-- Taxa de vitórias por Pokémon.
-- Corte adotado: mínimo de 50 combates. A coluna total_combates permanece
-- materializada na Gold, portanto o corte pode ser alterado sem reprocessar.
-- ------------------------------------------------------------
-- 10 maiores taxas.
SELECT pokemon_csv_id, pokemon_nome, total_combates, vitorias, taxa_vitorias
FROM gold.ranking_pokemon
WHERE total_combates >= 50
ORDER BY taxa_vitorias DESC, total_combates DESC, pokemon_nome
LIMIT 10;

-- 10 menores taxas.
SELECT pokemon_csv_id, pokemon_nome, total_combates, vitorias, taxa_vitorias
FROM gold.ranking_pokemon
WHERE total_combates >= 50
ORDER BY taxa_vitorias ASC, total_combates DESC, pokemon_nome
LIMIT 10;


-- ------------------------------------------------------------
-- ANÁLISE 4
-- Taxa de vitórias por tipo primário.
-- ------------------------------------------------------------
SELECT tipo, total_combates, vitorias, taxa_vitorias
FROM gold.taxa_vitorias_por_tipo
ORDER BY taxa_vitorias DESC, total_combates DESC, tipo;


-- ------------------------------------------------------------
-- ANÁLISE 5
-- Relação entre diferença de velocidade e vitória.
-- ------------------------------------------------------------
SELECT ordem_faixa, faixa_velocidade, total_confrontos, vitorias, taxa_vitorias
FROM gold.taxa_vitorias_por_faixa_velocidade
ORDER BY ordem_faixa;


-- ------------------------------------------------------------
-- ANÁLISE 6
-- Relação entre vantagem de tipo e vitória.
-- O multiplicador considera o tipo primário atacante contra os dois tipos
-- do defensor; quando não há tipo secundário, o segundo fator vale 1.
-- ------------------------------------------------------------
SELECT multiplicador, total_confrontos, vitorias, taxa_vitorias
FROM gold.taxa_vitorias_por_multiplicador
ORDER BY multiplicador;


-- ------------------------------------------------------------
-- ANÁLISE 7A
-- Matriz 18 x 18: taxa observada e efetividade do tipo primário.
-- ------------------------------------------------------------
SELECT
    tipo_atacante,
    tipo_defensor,
    total_confrontos,
    vitorias,
    taxa_vitorias,
    multiplicador_efetividade,
    expectativa,
    diverge_da_efetividade
FROM gold.matriz_confronto
ORDER BY tipo_atacante, tipo_defensor;

-- ANÁLISE 7B: apenas posições que contradizem a direção esperada pela efetividade.
SELECT
    tipo_atacante,
    tipo_defensor,
    total_confrontos,
    taxa_vitorias,
    multiplicador_efetividade,
    expectativa
FROM gold.matriz_confronto
WHERE diverge_da_efetividade IS TRUE
ORDER BY tipo_atacante, tipo_defensor;


-- ------------------------------------------------------------
-- ANÁLISE 8 - PROPOSTA DO GRUPO
-- Pergunta: atacar primeiro está associado a maior taxa de vitórias?
-- Essa análise usa uma capacidade não exigida pelas sete anteriores:
-- a ordem original First_pokemon/Second_pokemon do combats.csv.
-- ------------------------------------------------------------
SELECT ordem_ataque, total_confrontos, vitorias, taxa_vitorias
FROM gold.vantagem_primeiro_ataque
ORDER BY ordem_ataque;
