# EP01 - CAMADA BRONZE: EXTRAÇÃO DE DADOS

import csv
import json
import os
import time
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path

import requests
from pymongo import MongoClient


# CONFIGURAÇÕES GERAIS
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
BANCO = "pokedex_bronze"

POKEAPI_BASE = "https://pokeapi.co/api/v2"
URL_POKEMON_CSV = "https://raw.githubusercontent.com/cdiener/pokemon_app/master/pokemon.csv"
URL_COMBATES_CSV = "https://raw.githubusercontent.com/cdiener/pokemon_app/master/combats.csv"

PASTA_CACHE = Path("dados_brutos")
INTERVALO_API = 0.1


# CONEXÃO COM MONGODB
cliente = MongoClient(MONGODB_URL)
db = cliente[BANCO]

colecao_pokemon = db["pokemon"]
colecao_especies = db["especies"]
colecao_tipos = db["tipos"]
colecao_pokemon_csv = db["pokemon_csv"]
colecao_combates = db["combates"]


def data_ingestao():
    """Retorna o instante UTC usado somente na primeira inserção do documento."""
    return datetime.now(timezone.utc)


def salvar_json_cache(caminho, dados):
    """Salva a resposta bruta da API antes da escrita no MongoDB."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)


def ler_json_cache(caminho):
    with open(caminho, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def buscar_json_com_cache(url, caminho_cache):
    """Consulta a rede somente quando o arquivo bruto ainda não existe."""
    if caminho_cache.exists():
        print(f"[CACHE] {caminho_cache}")
        return ler_json_cache(caminho_cache)

    print(f"[API] {url}")
    resposta = requests.get(url, timeout=30)
    resposta.raise_for_status()
    dados = resposta.json()
    salvar_json_cache(caminho_cache, dados)
    time.sleep(INTERVALO_API)
    return dados


def inserir_documento(colecao, documento):
    """
    Upsert idempotente por substituição completa do documento.

    A substituição é intencional: cabeçalhos brutos do pokemon.csv como
    "Sp. Atk" e "Sp. Def" contêm ponto. Em operadores como $set, o ponto é
    interpretado pelo MongoDB como caminho de subdocumento e alteraria a
    estrutura da fonte. replace_one preserva o documento bruto como recebido.

    O instante de ingestão original é mantido em reexecuções.
    """
    documento_id = documento["_id"]
    existente = colecao.find_one(
        {"_id": documento_id},
        {"_ingerido_em": 1},
    )

    if existente and "_ingerido_em" in existente:
        documento["_ingerido_em"] = existente["_ingerido_em"]

    colecao.replace_one(
        {"_id": documento_id},
        documento,
        upsert=True,
    )


def extrair_especies():
    print("\n========================================")
    print("EXTRAINDO ESPÉCIES")
    print("========================================")

    total = 0
    for especie_id in range(1, 722):
        url = f"{POKEAPI_BASE}/pokemon-species/{especie_id}"
        caminho_cache = PASTA_CACHE / "especies" / f"{especie_id}.json"
        dados = buscar_json_com_cache(url, caminho_cache)

        documento = dados.copy()
        documento["_id"] = f"especie/{especie_id}"
        documento["_fonte"] = "pokeapi"
        documento["_url"] = url
        documento["_ingerido_em"] = data_ingestao()

        inserir_documento(colecao_especies, documento)
        total += 1

    print(f"Total de espécies carregadas: {total}")


def extrair_pokemon():
    """
    Extrai as formas padrão 1..721 e TODAS as variedades relacionadas em
    pokemon-species/{id}. Isso inclui Mega, Primal e demais formas alternativas.
    """
    print("\n========================================")
    print("EXTRAINDO POKÉMON (TODAS AS FORMAS)")
    print("========================================")

    formas = {}

    # As formas padrão garantem o escopo básico das 721 espécies.
    for pokemon_id in range(1, 722):
        formas[pokemon_id] = {
            "name": None,
            "url": f"{POKEAPI_BASE}/pokemon/{pokemon_id}",
        }

    # As variedades são descobertas exclusivamente a partir do cache de espécies.
    for especie_id in range(1, 722):
        caminho_especie = PASTA_CACHE / "especies" / f"{especie_id}.json"
        if not caminho_especie.exists():
            raise FileNotFoundError(
                f"Cache da espécie {especie_id} ausente. Execute extrair_especies() primeiro."
            )

        especie = ler_json_cache(caminho_especie)
        for variedade in especie.get("varieties", []):
            pokemon = variedade.get("pokemon", {})
            url = pokemon.get("url")
            nome = pokemon.get("name")
            if not url:
                continue
            pokemon_id = int(url.rstrip("/").split("/")[-1])
            formas[pokemon_id] = {"name": nome, "url": url}

    total = 0
    alternativas = 0
    for pokemon_id in sorted(formas):
        dados_forma = formas[pokemon_id]
        url = dados_forma["url"]
        caminho_cache = PASTA_CACHE / "pokemon" / f"{pokemon_id}.json"
        dados = buscar_json_com_cache(url, caminho_cache)

        documento = dados.copy()
        documento["_id"] = f"pokemon/{pokemon_id}"
        documento["_fonte"] = "pokeapi"
        documento["_url"] = url
        documento["_ingerido_em"] = data_ingestao()

        inserir_documento(colecao_pokemon, documento)
        total += 1
        if pokemon_id > 721 or not dados.get("is_default", True):
            alternativas += 1

    print(f"Total de formas carregadas: {total}")
    print(f"Formas alternativas identificadas: {alternativas}")


def extrair_tipos():
    print("\n========================================")
    print("EXTRAINDO TIPOS")
    print("========================================")

    url_lista = f"{POKEAPI_BASE}/type?limit=100"
    caminho_lista = PASTA_CACHE / "tipos" / "lista_completa.json"
    dados_lista = buscar_json_com_cache(url_lista, caminho_lista)

    total = 0
    for tipo in dados_lista["results"]:
        url = tipo["url"]
        tipo_id = int(url.rstrip("/").split("/")[-1])
        caminho_tipo = PASTA_CACHE / "tipos" / f"{tipo_id}.json"
        dados = buscar_json_com_cache(url, caminho_tipo)

        documento = dados.copy()
        documento["_id"] = f"tipo/{tipo_id}"
        documento["_fonte"] = "pokeapi"
        documento["_url"] = url
        documento["_ingerido_em"] = data_ingestao()
        inserir_documento(colecao_tipos, documento)
        total += 1

    print(f"Total de tipos carregados: {total}")


def obter_csv_com_cache(url, caminho_cache):
    if caminho_cache.exists():
        print(f"[CACHE] {caminho_cache}")
        return caminho_cache.read_text(encoding="utf-8")

    print(f"[CSV] {url}")
    resposta = requests.get(url, timeout=30)
    resposta.raise_for_status()
    caminho_cache.parent.mkdir(parents=True, exist_ok=True)
    caminho_cache.write_text(resposta.text, encoding="utf-8")
    return resposta.text


def extrair_pokemon_csv():
    print("\n========================================")
    print("EXTRAINDO POKEMON.CSV")
    print("========================================")

    caminho_cache = PASTA_CACHE / "pokemon_csv" / "pokemon.csv"
    conteudo = obter_csv_com_cache(URL_POKEMON_CSV, caminho_cache)

    total = 0
    for linha in csv.DictReader(StringIO(conteudo)):
        numero_csv = linha["#"]
        documento = linha.copy()
        documento["_id"] = f"pokemon_csv/{numero_csv}"
        documento["_fonte"] = "pokemon.csv"
        documento["_url"] = URL_POKEMON_CSV
        documento["_ingerido_em"] = data_ingestao()
        inserir_documento(colecao_pokemon_csv, documento)
        total += 1

    print(f"Total de cadastros CSV carregados: {total}")


def extrair_combates():
    print("\n========================================")
    print("EXTRAINDO COMBATS.CSV")
    print("========================================")

    caminho_cache = PASTA_CACHE / "combates" / "combats.csv"
    conteudo = obter_csv_com_cache(URL_COMBATES_CSV, caminho_cache)

    total = 0
    for numero_linha, linha in enumerate(csv.DictReader(StringIO(conteudo)), start=1):
        documento = linha.copy()
        documento["_id"] = f"combate/{numero_linha}"
        documento["_fonte"] = "combats.csv"
        documento["_url"] = URL_COMBATES_CSV
        documento["_ingerido_em"] = data_ingestao()
        inserir_documento(colecao_combates, documento)
        total += 1

    print(f"Total de combates carregados: {total}")


def main():
    print("\n============================================")
    print("      EP01 - EXTRAÇÃO PARA A CAMADA BRONZE")
    print("============================================")
    print(f"Banco alvo: {BANCO}")

    try:
        cliente.admin.command("ping")
        print("MongoDB conectado com sucesso.")

        extrair_especies()
        extrair_pokemon()
        extrair_tipos()
        extrair_pokemon_csv()
        extrair_combates()

        print("\nContagens na camada bronze:")
        for nome in ("pokemon", "especies", "tipos", "pokemon_csv", "combates"):
            print(f"  {nome}: {db[nome].count_documents({})}")

        print("\nEXTRAÇÃO CONCLUÍDA COM SUCESSO")
    except Exception as erro:
        print("\nERRO DURANTE A EXTRAÇÃO:")
        print(erro)
        raise
    finally:
        cliente.close()


if __name__ == "__main__":
    main()
