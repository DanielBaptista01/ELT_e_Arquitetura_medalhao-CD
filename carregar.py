# EP01 - CAMADA SILVER: CONCILIAÇÃO, LIMPEZA E MODELAGEM DIMENSIONAL

import os
import re
import unicodedata
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import psycopg
from pymongo import MongoClient


MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
POSTGRES_URL = os.getenv(
    "POSTGRES_URL",
    "postgresql://postgres:postgres@localhost:5432/pokedex",
)
BANCO_BRONZE = "pokedex_bronze"
ARQUIVO_DDL = Path("sql/silver.sql")

GERACOES = {
    1: ("Geração I", "Kanto"),
    2: ("Geração II", "Johto"),
    3: ("Geração III", "Hoenn"),
    4: ("Geração IV", "Sinnoh"),
    5: ("Geração V", "Unova"),
    6: ("Geração VI", "Kalos"),
}

ALIASES_CSV_PARA_API = {
    "basculin": "basculin-red-striped",
    "zygardehalf": "zygarde-50",
    "hoopaconfined": "hoopa",
}

TOKENS_GENERICOS_FORMA = {"forme", "form", "mode", "cloak", "size"}


def inteiro(valor, padrao=None):
    if valor in (None, ""):
        return padrao
    return int(valor)


def booleano_texto(valor):
    return str(valor).strip().lower() == "true"


def normalizar_cabecalho_csv(nome):
    """Normaliza apenas o nome da coluna para localizar o campo bruto na Silver."""
    texto = unicodedata.normalize("NFKD", str(nome))
    texto = "".join(ch for ch in texto if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", "", texto.lower())


def campo_csv(linha, nome, obrigatorio=True):
    """
    Lê um campo do pokemon.csv preservado na Bronze.

    Além do cabeçalho original, aceita uma representação legada criada por uma
    versão anterior da extração, na qual o MongoDB interpretou "Sp. Atk" e
    "Sp. Def" como caminhos e os armazenou sob o subdocumento "Sp".
    """
    if nome in linha:
        return linha[nome]

    # Compatibilidade temporária com Bronze produzida antes da correção do
    # replace_one em extrair.py: {"Sp": {"Atk": "...", "Def": "..."}}.
    if nome in {"Sp. Atk", "Sp. Def"}:
        sp = linha.get("Sp")
        if isinstance(sp, dict):
            subcampo = "Atk" if nome == "Sp. Atk" else "Def"
            if subcampo in sp:
                return sp[subcampo]

    alvo = normalizar_cabecalho_csv(nome)
    correspondencias = [
        chave for chave in linha
        if not str(chave).startswith("_")
        and normalizar_cabecalho_csv(chave) == alvo
    ]

    if len(correspondencias) == 1:
        return linha[correspondencias[0]]

    if not obrigatorio:
        return None

    campos = sorted(str(chave) for chave in linha if not str(chave).startswith("_"))
    raise KeyError(
        f"Campo {nome!r} não encontrado no documento pokemon_csv. "
        f"Campos disponíveis: {campos}"
    )


def nome_recurso_url(url):
    if not url:
        return None
    partes = [parte for parte in url.rstrip("/").split("/") if parte]
    return partes[-1] if partes else None


def id_recurso_url(url):
    valor = nome_recurso_url(url)
    return int(valor) if valor and valor.isdigit() else None


def tokens_nome(nome):
    """Normaliza nomes sem depender de uma lista fixa de todas as formas."""
    if not nome:
        return []

    texto = str(nome).replace("♀", " f ").replace("♂", " m ")
    texto = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", texto)
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(ch for ch in texto if not unicodedata.combining(ch))
    texto = texto.lower()
    texto = re.sub(r"[^a-z0-9]+", " ", texto)

    tokens = [t for t in texto.split() if t and t not in TOKENS_GENERICOS_FORMA]

    sem_repeticao = []
    vistos = set()
    for token in tokens:
        if token not in vistos:
            sem_repeticao.append(token)
            vistos.add(token)
    return sem_repeticao


def nome_compacto(nome):
    return "".join(tokens_nome(nome))


def assinatura_nome(nome):
    return "|".join(sorted(tokens_nome(nome)))


def nomes_tipos_api(documento_pokemon):
    tipos = sorted(documento_pokemon.get("types", []), key=lambda item: item.get("slot", 0))
    return [item.get("type", {}).get("name", "").lower() for item in tipos]


def nome_aninhado(documento, campo):
    valor = documento.get(campo)
    if isinstance(valor, dict):
        return valor.get("name")
    return None


def derivar_raridade(especie, lendario_csv, conciliado):
    if not conciliado or especie is None:
        return "LENDARIO" if lendario_csv else "COMUM"
    if especie.get("is_mythical"):
        return "MITICO"
    if especie.get("is_legendary"):
        return "LENDARIO"
    if especie.get("is_baby"):
        return "BEBE"
    return "COMUM"


def tratar_habitat(especie, geracao, conciliado):
    if not conciliado or especie is None:
        return None, "DESCONHECIDO"

    habitat = nome_aninhado(especie, "habitat")
    if habitat:
        return habitat, "INFORMADO"

    if geracao >= 4:
        return None, "NAO_APLICAVEL"

    return None, "DADO_AUSENTE"


def executar_ddl(conexao):
    if not ARQUIVO_DDL.exists():
        raise FileNotFoundError(f"DDL não encontrado: {ARQUIVO_DDL}")
    ddl = ARQUIVO_DDL.read_text(encoding="utf-8")
    with conexao.cursor() as cursor:
        cursor.execute(ddl, prepare=False)


def carregar_geracoes(cursor):
    mapa = {}
    for numero, (nome, regiao) in GERACOES.items():
        cursor.execute(
            """
            INSERT INTO silver.dim_geracao (numero, nome, regiao)
            VALUES (%s, %s, %s)
            RETURNING geracao_sk
            """,
            (numero, nome, regiao),
        )
        mapa[numero] = cursor.fetchone()[0]
    return mapa


def carregar_tipos(cursor, db):
    docs_tipos = list(db["tipos"].find({"id": {"$gte": 1, "$lte": 18}}))
    if len(docs_tipos) != 18:
        raise RuntimeError(
            f"Esperados 18 tipos reais (IDs 1..18) na Bronze; encontrados {len(docs_tipos)}."
        )

    mapa_nome = {}
    mapa_id = {}
    docs_por_nome = {}

    for doc in sorted(docs_tipos, key=lambda item: item["id"]):
        nome = doc["name"].lower()
        cursor.execute(
            """
            INSERT INTO silver.dim_tipo (pokeapi_tipo_id, nome, membro_especial)
            VALUES (%s, %s, FALSE)
            RETURNING tipo_sk
            """,
            (int(doc["id"]), nome),
        )
        sk = cursor.fetchone()[0]
        mapa_nome[nome] = sk
        mapa_id[int(doc["id"])] = sk
        docs_por_nome[nome] = doc

    cursor.execute(
        """
        INSERT INTO silver.dim_tipo (pokeapi_tipo_id, nome, membro_especial)
        VALUES (0, 'sem_tipo_secundario', TRUE)
        RETURNING tipo_sk
        """
    )
    tipo_sem_secundario_sk = cursor.fetchone()[0]
    mapa_nome["sem_tipo_secundario"] = tipo_sem_secundario_sk

    return mapa_nome, mapa_id, docs_por_nome, tipo_sem_secundario_sk


def carregar_efetividade(cursor, mapa_tipo_nome, docs_tipo_nome):
    nomes_reais = sorted(docs_tipo_nome)
    linhas = []

    for nome_atacante in nomes_reais:
        doc = docs_tipo_nome[nome_atacante]
        relacoes = doc.get("damage_relations", {})
        dobro = {item["name"] for item in relacoes.get("double_damage_to", [])}
        metade = {item["name"] for item in relacoes.get("half_damage_to", [])}
        zero = {item["name"] for item in relacoes.get("no_damage_to", [])}

        for nome_defensor in nomes_reais:
            multiplicador = 1.0
            if nome_defensor in dobro:
                multiplicador = 2.0
            elif nome_defensor in metade:
                multiplicador = 0.5
            elif nome_defensor in zero:
                multiplicador = 0.0

            linhas.append(
                (
                    mapa_tipo_nome[nome_atacante],
                    mapa_tipo_nome[nome_defensor],
                    multiplicador,
                )
            )

    cursor.executemany(
        """
        INSERT INTO silver.efetividade_tipo
            (tipo_atacante_sk, tipo_defensor_sk, multiplicador)
        VALUES (%s, %s, %s)
        """,
        linhas,
    )

    if len(linhas) != 324:
        raise RuntimeError(f"Matriz de efetividade incompleta: {len(linhas)} pares.")


def preparar_indices_pokeapi(db):
    especies = {int(doc["id"]): doc for doc in db["especies"].find({})}
    formas = list(db["pokemon"].find({}))

    por_nome_api = {}
    por_compacto = defaultdict(list)
    por_assinatura = defaultdict(list)

    for forma in formas:
        nome = forma.get("name")
        if not nome:
            continue
        por_nome_api[nome.lower()] = forma
        por_compacto[nome_compacto(nome)].append(forma)
        por_assinatura[assinatura_nome(nome)].append(forma)

    return especies, formas, por_nome_api, por_compacto, por_assinatura


def filtrar_candidatos(candidatos, linha_csv, especies):
    if not candidatos:
        return []

    geracao_csv = inteiro(linha_csv.get("Generation"))
    tipos_csv = [linha_csv.get("Type 1", "").strip().lower()]
    if linha_csv.get("Type 2", "").strip():
        tipos_csv.append(linha_csv["Type 2"].strip().lower())

    filtrados = []
    for forma in candidatos:
        especie_id = id_recurso_url(forma.get("species", {}).get("url"))
        especie = especies.get(especie_id)
        geracao_api = None
        if especie:
            geracao_api = id_recurso_url(especie.get("generation", {}).get("url"))

        if geracao_api is not None and geracao_api != geracao_csv:
            continue
        if nomes_tipos_api(forma) != tipos_csv:
            continue
        filtrados.append(forma)

    return filtrados or candidatos


def resolver_forma(linha_csv, especies, por_nome_api, por_compacto, por_assinatura):
    nome_csv = (linha_csv.get("Name") or "").strip()
    if not nome_csv:
        return None, "NOME_AUSENTE", "membro especial: nome ausente no pokemon.csv"

    compacto = nome_compacto(nome_csv)

    alias_api = ALIASES_CSV_PARA_API.get(compacto)
    if alias_api and alias_api in por_nome_api:
        return por_nome_api[alias_api], "CONCILIADO", f"alias explícito {nome_csv} -> {alias_api}"

    candidatos = list(por_compacto.get(compacto, []))
    estrategia = "normalização compacta"

    if not candidatos:
        candidatos = list(por_assinatura.get(assinatura_nome(nome_csv), []))
        estrategia = "assinatura de tokens independente de ordem"

    candidatos = filtrar_candidatos(candidatos, linha_csv, especies)

    if len(candidatos) == 1:
        return candidatos[0], "CONCILIADO", estrategia

    if len(candidatos) > 1:
        marcadores = {
            "mega", "primal", "attack", "defense", "speed", "altered",
            "origin", "sky", "therian", "incarnate", "black", "white",
            "resolute", "ordinary", "aria", "pirouette", "zen", "standard",
            "blade", "shield", "average", "small", "large", "super",
            "unbound", "confined", "male", "female", "half",
        }
        tokens = set(tokens_nome(nome_csv))
        quer_alternativa = bool(tokens & marcadores)
        preferidos = [f for f in candidatos if bool(f.get("is_default")) != quer_alternativa]
        if len(preferidos) == 1:
            return preferidos[0], "CONCILIADO", estrategia + " + desempate is_default"

        candidatos = sorted(candidatos, key=lambda f: int(f.get("id", 10**9)))
        return candidatos[0], "CONCILIADO", estrategia + " + desempate por menor id"

    return None, "NAO_CONCILIADO", "nenhuma forma da PokéAPI correspondeu ao nome/tipos/geração"


def carregar_pokemon(cursor, db, mapa_tipo_nome, mapa_geracao):
    linhas_csv = list(db["pokemon_csv"].find({}))
    linhas_csv.sort(key=lambda doc: int(doc["#"]))
    if len(linhas_csv) != 800:
        raise RuntimeError(f"Esperados 800 registros em pokemon_csv; encontrados {len(linhas_csv)}.")

    especies, _, por_nome_api, por_compacto, por_assinatura = preparar_indices_pokeapi(db)

    mapa_csv = {}
    nao_conciliados = []

    for linha in linhas_csv:
        csv_id = int(linha["#"])
        nome_csv = (linha.get("Name") or "").strip() or None
        forma, status, estrategia = resolver_forma(
            linha, especies, por_nome_api, por_compacto, por_assinatura
        )

        conciliado = forma is not None
        especie = None
        especie_id = None
        if forma:
            especie_id = id_recurso_url(forma.get("species", {}).get("url"))
            especie = especies.get(especie_id)

        geracao = int(linha["Generation"])
        geracao_nome, regiao = GERACOES[geracao]
        tipo_primario = linha["Type 1"].strip().lower()
        tipo_secundario = (linha.get("Type 2") or "").strip().lower() or None
        lendario_csv = booleano_texto(linha.get("Legendary"))

        if tipo_primario not in mapa_tipo_nome:
            raise RuntimeError(f"Tipo primário desconhecido no CSV #{csv_id}: {tipo_primario}")
        if tipo_secundario and tipo_secundario not in mapa_tipo_nome:
            raise RuntimeError(f"Tipo secundário desconhecido no CSV #{csv_id}: {tipo_secundario}")

        habitat, habitat_situacao = tratar_habitat(especie, geracao, conciliado)
        raridade = derivar_raridade(especie, lendario_csv, conciliado)

        nome_api = forma.get("name") if forma else None
        nome_exibicao = nome_csv or f"[NOME AUSENTE - CSV #{csv_id}]"

        cursor.execute(
            """
            INSERT INTO silver.dim_pokemon (
                pokemon_csv_id, pokeapi_pokemon_id, pokedex_especie_id,
                nome_csv, nome_api, nome_exibicao, conciliado,
                estrategia_conciliacao, is_default, forma_alternativa,
                tipo_primario, tipo_secundario, geracao_num, geracao_nome, regiao,
                hp, ataque, defesa, ataque_especial, defesa_especial, velocidade,
                altura_m, peso_kg, experiencia_base, quantidade_habilidades,
                habitat, habitat_situacao, cor, forma_corporal, taxa_crescimento,
                taxa_captura, felicidade_base, lendario_csv, is_legendary,
                is_mythical, is_baby, raridade
            ) VALUES (
                %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s
            )
            RETURNING pokemon_sk
            """,
            (
                csv_id,
                inteiro(forma.get("id")) if forma else None,
                especie_id,
                nome_csv,
                nome_api,
                nome_exibicao,
                conciliado,
                estrategia,
                forma.get("is_default") if forma else None,
                bool(forma and not forma.get("is_default", False)),
                tipo_primario,
                tipo_secundario,
                geracao,
                geracao_nome,
                regiao,
                int(campo_csv(linha, "HP")),
                int(campo_csv(linha, "Attack")),
                int(campo_csv(linha, "Defense")),
                int(campo_csv(linha, "Sp. Atk")),
                int(campo_csv(linha, "Sp. Def")),
                int(campo_csv(linha, "Speed")),
                (forma.get("height") / 10.0) if forma and forma.get("height") is not None else None,
                (forma.get("weight") / 10.0) if forma and forma.get("weight") is not None else None,
                inteiro(forma.get("base_experience")) if forma else None,
                len(forma.get("abilities", [])) if forma else None,
                habitat,
                habitat_situacao,
                nome_aninhado(especie, "color") if especie else None,
                nome_aninhado(especie, "shape") if especie else None,
                nome_aninhado(especie, "growth_rate") if especie else None,
                inteiro(especie.get("capture_rate")) if especie else None,
                inteiro(especie.get("base_happiness")) if especie else None,
                lendario_csv,
                especie.get("is_legendary") if especie else None,
                especie.get("is_mythical") if especie else None,
                especie.get("is_baby") if especie else None,
                raridade,
            ),
        )
        pokemon_sk = cursor.fetchone()[0]

        cursor.execute(
            """
            INSERT INTO silver.log_conciliacao (
                pokemon_csv_id, nome_csv, nome_normalizado, pokeapi_pokemon_id,
                nome_api, pokedex_especie_id, status, estrategia, detalhe
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                csv_id,
                nome_csv,
                assinatura_nome(nome_csv),
                inteiro(forma.get("id")) if forma else None,
                nome_api,
                especie_id,
                status,
                estrategia,
                "registro preservado no modelo; nenhum combate é descartado",
            ),
        )

        if status != "CONCILIADO":
            nao_conciliados.append((csv_id, nome_csv, status))

        mapa_csv[csv_id] = {
            "pokemon_sk": pokemon_sk,
            "tipo_primario_sk": mapa_tipo_nome[tipo_primario],
            "tipo_secundario_sk": mapa_tipo_nome[
                tipo_secundario if tipo_secundario else "sem_tipo_secundario"
            ],
            "geracao_sk": mapa_geracao[geracao],
            "velocidade": int(campo_csv(linha, "Speed")),
            "nome": nome_exibicao,
        }

    return mapa_csv, nao_conciliados


def inserir_lote_fato(cursor, lote):
    if not lote:
        return
    cursor.executemany(
        """
        INSERT INTO silver.fato_participacao (
            combate_id, ordem_no_csv, pokemon_sk, oponente_sk,
            tipo_primario_sk, tipo_secundario_sk,
            oponente_tipo_primario_sk, oponente_tipo_secundario_sk,
            geracao_sk, oponente_geracao_sk,
            venceu, atacou_primeiro, velocidade, velocidade_oponente,
            diferenca_velocidade
        ) VALUES (
            %s, %s, %s, %s,
            %s, %s,
            %s, %s,
            %s, %s,
            %s, %s, %s, %s,
            %s
        )
        """,
        lote,
    )


def carregar_fato(cursor, db, mapa_csv):
    total_combates = db["combates"].count_documents({})
    if total_combates != 50000:
        raise RuntimeError(f"Esperados 50.000 combates na Bronze; encontrados {total_combates}.")

    lote = []
    processados = 0

    for doc in db["combates"].find({}, batch_size=1000):
        combate_id = int(str(doc["_id"]).split("/")[-1])
        primeiro_id = int(doc["First_pokemon"])
        segundo_id = int(doc["Second_pokemon"])
        vencedor_id = int(doc["Winner"])

        if primeiro_id not in mapa_csv or segundo_id not in mapa_csv:
            raise RuntimeError(
                f"Combate {combate_id} referencia Pokémon fora do cadastro: "
                f"{primeiro_id}, {segundo_id}."
            )

        primeiro = mapa_csv[primeiro_id]
        segundo = mapa_csv[segundo_id]

        lote.append(
            (
                combate_id,
                1,
                primeiro["pokemon_sk"],
                segundo["pokemon_sk"],
                primeiro["tipo_primario_sk"],
                primeiro["tipo_secundario_sk"],
                segundo["tipo_primario_sk"],
                segundo["tipo_secundario_sk"],
                primeiro["geracao_sk"],
                segundo["geracao_sk"],
                1 if vencedor_id == primeiro_id else 0,
                1,
                primeiro["velocidade"],
                segundo["velocidade"],
                primeiro["velocidade"] - segundo["velocidade"],
            )
        )
        lote.append(
            (
                combate_id,
                2,
                segundo["pokemon_sk"],
                primeiro["pokemon_sk"],
                segundo["tipo_primario_sk"],
                segundo["tipo_secundario_sk"],
                primeiro["tipo_primario_sk"],
                primeiro["tipo_secundario_sk"],
                segundo["geracao_sk"],
                primeiro["geracao_sk"],
                1 if vencedor_id == segundo_id else 0,
                0,
                segundo["velocidade"],
                primeiro["velocidade"],
                segundo["velocidade"] - primeiro["velocidade"],
            )
        )

        processados += 1
        if len(lote) >= 2000:
            inserir_lote_fato(cursor, lote)
            lote.clear()

    inserir_lote_fato(cursor, lote)

    if processados != 50000:
        raise RuntimeError(f"Carga incompleta da fato: {processados} combates processados.")


def imprimir_contagens(cursor, nao_conciliados, inicio):
    tabelas = [
        "dim_pokemon",
        "dim_tipo",
        "dim_geracao",
        "efetividade_tipo",
        "fato_participacao",
        "log_conciliacao",
    ]
    print("\nContagens da camada Silver:")
    for tabela in tabelas:
        cursor.execute(f"SELECT COUNT(*) FROM silver.{tabela}")
        print(f"  silver.{tabela}: {cursor.fetchone()[0]}")

    print("\nConciliação:")
    if nao_conciliados:
        for csv_id, nome, status in nao_conciliados:
            print(f"  CSV #{csv_id}: {nome!r} -> {status}")
    else:
        print("  Todos os registros foram conciliados.")

    print(f"Execução Silver concluída em {datetime.now(timezone.utc).isoformat()}")
    print(f"Início da execução: {inicio.isoformat()}")


def main():
    inicio = datetime.now(timezone.utc)
    mongo = MongoClient(MONGODB_URL)

    try:
        mongo.admin.command("ping")
        db = mongo[BANCO_BRONZE]

        with psycopg.connect(POSTGRES_URL) as conexao:
            executar_ddl(conexao)

            with conexao.cursor() as cursor:
                cursor.execute(
                    """
                    TRUNCATE TABLE
                        silver.fato_participacao,
                        silver.efetividade_tipo,
                        silver.log_conciliacao,
                        silver.dim_pokemon,
                        silver.dim_tipo,
                        silver.dim_geracao
                    RESTART IDENTITY CASCADE
                    """
                )

                mapa_geracao = carregar_geracoes(cursor)
                mapa_tipo_nome, _, docs_tipo_nome, _ = carregar_tipos(cursor, db)
                carregar_efetividade(cursor, mapa_tipo_nome, docs_tipo_nome)
                mapa_csv, nao_conciliados = carregar_pokemon(
                    cursor, db, mapa_tipo_nome, mapa_geracao
                )
                carregar_fato(cursor, db, mapa_csv)

                cursor.execute("SELECT COUNT(*) FROM silver.fato_participacao")
                linhas_fato = cursor.fetchone()[0]
                if linhas_fato != 100000:
                    raise RuntimeError(
                        f"A fato deve conter 100.000 participações; contém {linhas_fato}."
                    )

                imprimir_contagens(cursor, nao_conciliados, inicio)

        print("\nCARGA SILVER CONCLUÍDA COM SUCESSO")
    except Exception:
        print("\nERRO DURANTE A CARGA SILVER")
        raise
    finally:
        mongo.close()


if __name__ == "__main__":
    main()
