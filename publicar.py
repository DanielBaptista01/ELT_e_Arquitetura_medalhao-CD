# EP01 - CAMADA GOLD: AGREGAÇÃO E PUBLICAÇÃO NO POSTGRESQL

import os
from datetime import datetime, timezone
from pathlib import Path

import psycopg


POSTGRES_URL = os.getenv(
    "POSTGRES_URL",
    "postgresql://postgres:postgres@localhost:5432/pokedex",
)
ARQUIVO_DDL = Path("sql/gold.sql")


def executar_ddl(conexao):
    if not ARQUIVO_DDL.exists():
        raise FileNotFoundError(f"DDL não encontrado: {ARQUIVO_DDL}")
    ddl = ARQUIVO_DDL.read_text(encoding="utf-8")
    with conexao.cursor() as cursor:
        cursor.execute(ddl, prepare=False)


def publicar_ranking_pokemon(cursor):
    cursor.execute(
        """
        INSERT INTO gold.ranking_pokemon (
            pokemon_csv_id, pokemon_nome, total_combates, vitorias, taxa_vitorias
        )
        SELECT
            p.pokemon_csv_id,
            p.nome_exibicao,
            COUNT(*)::INTEGER AS total_combates,
            SUM(f.venceu)::INTEGER AS vitorias,
            AVG(f.venceu::NUMERIC)::NUMERIC(8,6) AS taxa_vitorias
        FROM silver.fato_participacao f
        JOIN silver.dim_pokemon p ON p.pokemon_sk = f.pokemon_sk
        GROUP BY p.pokemon_csv_id, p.nome_exibicao
        """
    )


def publicar_tipo(cursor):
    cursor.execute(
        """
        INSERT INTO gold.taxa_vitorias_por_tipo (
            tipo, total_combates, vitorias, taxa_vitorias
        )
        SELECT
            t.nome,
            COUNT(*)::INTEGER,
            SUM(f.venceu)::INTEGER,
            AVG(f.venceu::NUMERIC)::NUMERIC(8,6)
        FROM silver.fato_participacao f
        JOIN silver.dim_tipo t ON t.tipo_sk = f.tipo_primario_sk
        WHERE NOT t.membro_especial
        GROUP BY t.nome
        """
    )


def publicar_velocidade(cursor):
    cursor.execute(
        """
        INSERT INTO gold.taxa_vitorias_por_faixa_velocidade (
            ordem_faixa, faixa_velocidade, total_confrontos, vitorias, taxa_vitorias
        )
        SELECT
            ordem_faixa,
            faixa_velocidade,
            COUNT(*)::INTEGER,
            SUM(venceu)::INTEGER,
            AVG(venceu::NUMERIC)::NUMERIC(8,6)
        FROM (
            SELECT
                venceu,
                CASE
                    WHEN diferenca_velocidade <= -50 THEN 1
                    WHEN diferenca_velocidade BETWEEN -49 AND -20 THEN 2
                    WHEN diferenca_velocidade BETWEEN -19 AND -1 THEN 3
                    WHEN diferenca_velocidade = 0 THEN 4
                    WHEN diferenca_velocidade BETWEEN 1 AND 19 THEN 5
                    WHEN diferenca_velocidade BETWEEN 20 AND 49 THEN 6
                    ELSE 7
                END AS ordem_faixa,
                CASE
                    WHEN diferenca_velocidade <= -50 THEN '<= -50'
                    WHEN diferenca_velocidade BETWEEN -49 AND -20 THEN '-49 a -20'
                    WHEN diferenca_velocidade BETWEEN -19 AND -1 THEN '-19 a -1'
                    WHEN diferenca_velocidade = 0 THEN '0'
                    WHEN diferenca_velocidade BETWEEN 1 AND 19 THEN '1 a 19'
                    WHEN diferenca_velocidade BETWEEN 20 AND 49 THEN '20 a 49'
                    ELSE '>= 50'
                END AS faixa_velocidade
            FROM silver.fato_participacao
        ) dados
        GROUP BY ordem_faixa, faixa_velocidade
        ORDER BY ordem_faixa
        """
    )


def publicar_multiplicador(cursor):
    cursor.execute(
        """
        INSERT INTO gold.taxa_vitorias_por_multiplicador (
            multiplicador, total_confrontos, vitorias, taxa_vitorias
        )
        WITH confrontos AS (
            SELECT
                f.venceu,
                (
                    ef_primario.multiplicador *
                    CASE
                        WHEN tipo_secundario_defensor.membro_especial THEN 1::NUMERIC
                        ELSE ef_secundario.multiplicador
                    END
                )::NUMERIC(4,2) AS multiplicador
            FROM silver.fato_participacao f
            JOIN silver.efetividade_tipo ef_primario
              ON ef_primario.tipo_atacante_sk = f.tipo_primario_sk
             AND ef_primario.tipo_defensor_sk = f.oponente_tipo_primario_sk
            JOIN silver.dim_tipo tipo_secundario_defensor
              ON tipo_secundario_defensor.tipo_sk = f.oponente_tipo_secundario_sk
            LEFT JOIN silver.efetividade_tipo ef_secundario
              ON ef_secundario.tipo_atacante_sk = f.tipo_primario_sk
             AND ef_secundario.tipo_defensor_sk = f.oponente_tipo_secundario_sk
        )
        SELECT
            multiplicador,
            COUNT(*)::INTEGER,
            SUM(venceu)::INTEGER,
            AVG(venceu::NUMERIC)::NUMERIC(8,6)
        FROM confrontos
        GROUP BY multiplicador
        ORDER BY multiplicador
        """
    )


def publicar_matriz(cursor):
    cursor.execute(
        """
        INSERT INTO gold.matriz_confronto (
            tipo_atacante, tipo_defensor, total_confrontos, vitorias,
            taxa_vitorias, multiplicador_efetividade, expectativa,
            diverge_da_efetividade
        )
        WITH tipos_reais AS (
            SELECT tipo_sk, nome
            FROM silver.dim_tipo
            WHERE NOT membro_especial
        ),
        observado AS (
            SELECT
                f.tipo_primario_sk AS atacante_sk,
                f.oponente_tipo_primario_sk AS defensor_sk,
                COUNT(*)::INTEGER AS total_confrontos,
                SUM(f.venceu)::INTEGER AS vitorias,
                AVG(f.venceu::NUMERIC)::NUMERIC(8,6) AS taxa_vitorias
            FROM silver.fato_participacao f
            GROUP BY f.tipo_primario_sk, f.oponente_tipo_primario_sk
        )
        SELECT
            atacante.nome,
            defensor.nome,
            COALESCE(obs.total_confrontos, 0),
            COALESCE(obs.vitorias, 0),
            obs.taxa_vitorias,
            ef.multiplicador,
            CASE
                WHEN ef.multiplicador > 1 THEN 'vantagem esperada'
                WHEN ef.multiplicador < 1 THEN 'desvantagem esperada'
                ELSE 'neutro'
            END,
            CASE
                WHEN obs.total_confrontos IS NULL OR obs.total_confrontos = 0 THEN NULL
                WHEN ef.multiplicador > 1 AND obs.taxa_vitorias <= 0.5 THEN TRUE
                WHEN ef.multiplicador < 1 AND obs.taxa_vitorias >= 0.5 THEN TRUE
                ELSE FALSE
            END
        FROM tipos_reais atacante
        CROSS JOIN tipos_reais defensor
        JOIN silver.efetividade_tipo ef
          ON ef.tipo_atacante_sk = atacante.tipo_sk
         AND ef.tipo_defensor_sk = defensor.tipo_sk
        LEFT JOIN observado obs
          ON obs.atacante_sk = atacante.tipo_sk
         AND obs.defensor_sk = defensor.tipo_sk
        ORDER BY atacante.nome, defensor.nome
        """
    )


def publicar_primeiro_ataque(cursor):
    cursor.execute(
        """
        INSERT INTO gold.vantagem_primeiro_ataque (
            ordem_ataque, total_confrontos, vitorias, taxa_vitorias
        )
        SELECT
            CASE
                WHEN atacou_primeiro = 1 THEN 'ATACOU_PRIMEIRO'
                ELSE 'ATACOU_SEGUNDO'
            END,
            COUNT(*)::INTEGER,
            SUM(venceu)::INTEGER,
            AVG(venceu::NUMERIC)::NUMERIC(8,6)
        FROM silver.fato_participacao
        GROUP BY atacou_primeiro
        ORDER BY atacou_primeiro DESC
        """
    )


def validar_e_registrar(cursor, inicio):
    tabelas = [
        "ranking_pokemon",
        "taxa_vitorias_por_tipo",
        "taxa_vitorias_por_faixa_velocidade",
        "taxa_vitorias_por_multiplicador",
        "matriz_confronto",
        "vantagem_primeiro_ataque",
    ]

    print("\nContagens da camada Gold:")
    contagens = {}
    for tabela in tabelas:
        cursor.execute(f"SELECT COUNT(*) FROM gold.{tabela}")
        contagem = cursor.fetchone()[0]
        contagens[tabela] = contagem
        print(f"  gold.{tabela}: {contagem}")

    if contagens["ranking_pokemon"] != 800:
        raise RuntimeError("gold.ranking_pokemon deve conter 800 Pokémon.")
    if contagens["taxa_vitorias_por_tipo"] != 18:
        raise RuntimeError("gold.taxa_vitorias_por_tipo deve conter 18 tipos.")
    if contagens["matriz_confronto"] != 324:
        raise RuntimeError("gold.matriz_confronto deve conter 18 x 18 = 324 posições.")
    if contagens["vantagem_primeiro_ataque"] != 2:
        raise RuntimeError("A análise de ordem de ataque deve conter dois grupos.")

    fim = datetime.now(timezone.utc)
    print(f"Publicação Gold iniciada em {inicio.isoformat()}")
    print(f"Publicação Gold concluída em {fim.isoformat()}")


def main():
    inicio = datetime.now(timezone.utc)

    with psycopg.connect(POSTGRES_URL) as conexao:
        executar_ddl(conexao)

        with conexao.cursor() as cursor:
            cursor.execute(
                """
                TRUNCATE TABLE
                    gold.ranking_pokemon,
                    gold.taxa_vitorias_por_tipo,
                    gold.taxa_vitorias_por_faixa_velocidade,
                    gold.taxa_vitorias_por_multiplicador,
                    gold.matriz_confronto,
                    gold.vantagem_primeiro_ataque
                """
            )

            publicar_ranking_pokemon(cursor)
            publicar_tipo(cursor)
            publicar_velocidade(cursor)
            publicar_multiplicador(cursor)
            publicar_matriz(cursor)
            publicar_primeiro_ataque(cursor)
            validar_e_registrar(cursor, inicio)

    print("\nPUBLICAÇÃO GOLD CONCLUÍDA COM SUCESSO")


if __name__ == "__main__":
    main()
