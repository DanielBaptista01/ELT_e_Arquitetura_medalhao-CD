# EP01 - CAMADA BRONZE: EXTRAÇÃO DE DADOS 

import os
import csv
import json
import time
import requests
from io import StringIO
from pathlib import Path
from datetime import datetime, timezone
from pymongo import MongoClient

# CONFIGURAÇÕES GERAIS

# Obtém a string de conexão do MongoDB pelas variáveis de ambiente.
MONGODB_URL = os.getenv("MONGODB_URL")

# Interrompe o programa caso a URL não tenha sido configurada.
if not MONGODB_URL:
    raise ValueError("A variável de ambiente MONGODB_URL não foi configurada.")

# Nome do banco de dados exigido pela arquitetura.
BANCO = "pokedex_bronze"

# URLs base das fontes de dados.
POKEAPI_BASE = "https://pokeapi.co/api/v2"
URL_POKEMON_CSV = "https://raw.githubusercontent.com/cdiener/pokemon_app/master/pokemon.csv"
URL_COMBATES_CSV = "https://raw.githubusercontent.com/cdiener/pokemon_app/master/combats.csv"

# Diretório onde os arquivos originais serão armazenados para evitar requisições repetidas.
PASTA_CACHE = Path("dados_brutos")

# Intervalo em segundos entre as requisições para poupar a API pública.
INTERVALO_API = 0.1

# CONEXÃO COM MONGODB

# Inicia o cliente do banco de dados.
cliente = MongoClient(MONGODB_URL)

# Seleciona o banco de dados da camada bronze.
db = cliente[BANCO]

# Define as cinco coleções obrigatórias para armazenar os documentos brutos.
colecao_pokemon = db["pokemon"]
colecao_especies = db["especies"]
colecao_tipos = db["tipos"]
colecao_pokemon_csv = db["pokemon_csv"]
colecao_combates = db["combates"]

# FUNÇÕES AUXILIARE

def data_ingestao():
    """Retorna a data e hora atual no fuso UTC para registrar a linhagem."""
    return datetime.now(timezone.utc)


def salvar_json_cache(caminho, dados):
    """Cria os diretórios necessários e salva o JSON no cache local."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)


def ler_json_cache(caminho):
    """Abre e converte um arquivo JSON do cache para um dicionário Python."""
    with open(caminho, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def buscar_json_com_cache(url, caminho_cache):
    """
    Controla o acesso à rede:
    - Se o arquivo existir no cache, lê do disco.
    - Se não existir, faz a requisição HTTP, salva no cache e aguarda o intervalo.
    """
    if caminho_cache.exists():
        print(f"[CACHE] {caminho_cache}")
        return ler_json_cache(caminho_cache)

    print(f"[API] {url}")
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    
    dados = response.json()
    salvar_json_cache(caminho_cache, dados)
    
    # Pausa para não sobrecarregar a PokéAPI.
    time.sleep(INTERVALO_API)
    return dados


def inserir_documento(colecao, documento):
    """
    Insere ou atualiza o documento no MongoDB (upsert).
    O uso do _id derivado da chave natural garante a idempotência da carga.
    """
    colecao.update_one(
        {"_id": documento["_id"]},
        {"$set": documento},
        upsert=True
    )

# EXTRAÇÃO 1 - ESPÉCIES

def extrair_especies():
    print("\n========================================")
    print("EXTRAINDO ESPÉCIES")
    print("========================================")

    total = 0

    # Percorre o escopo obrigatório: gerações I a VI (IDs 1 a 721).
    for especie_id in range(1, 722):
        url = f"{POKEAPI_BASE}/pokemon-species/{especie_id}"
        caminho_cache = PASTA_CACHE / "especies" / f"{especie_id}.json"

        # Obtém os dados via cache ou requisição.
        dados = buscar_json_com_cache(url, caminho_cache)
        documento = dados.copy()

        # Adiciona os campos de linhagem exigidos e define a chave natural.
        documento["_id"] = f"especie/{especie_id}"
        documento["_fonte"] = "pokeapi"
        documento["_url"] = url
        documento["_ingerido_em"] = data_ingestao()

        inserir_documento(colecao_especies, documento)
        total += 1

    print(f"\nTotal de espécies carregadas: {total}")

# EXTRAÇÃO 2 - POKÉMON (FORMAS PADRÃO E MEGAS)

def extrair_pokemon():
    print("\n========================================")
    print("EXTRAINDO POKÉMON (FORMAS)")
    print("========================================")

    total = 0
    ids_extraidos = set()

    # 1. Extração das formas padrão correspondentes às espécies de 1 a 721.
    for pokemon_id in range(1, 722):
        url = f"{POKEAPI_BASE}/pokemon/{pokemon_id}"
        caminho_cache = PASTA_CACHE / "pokemon" / f"{pokemon_id}.json"

        dados = buscar_json_com_cache(url, caminho_cache)
        documento = dados.copy()

        documento["_id"] = f"pokemon/{pokemon_id}"
        documento["_fonte"] = "pokeapi"
        documento["_url"] = url
        documento["_ingerido_em"] = data_ingestao()

        inserir_documento(colecao_pokemon, documento)
        ids_extraidos.add(pokemon_id)
        total += 1

    # 2. Varredura no cache das espécies para descobrir os IDs das formas Mega.
    print("\nProcurando formas Mega nas espécies armazenadas...")
    megas = set()

    for especie_id in range(1, 722):
        caminho_cache = PASTA_CACHE / "especies" / f"{especie_id}.json"
        
        if not caminho_cache.exists():
            continue

        dados_especie = ler_json_cache(caminho_cache)

        # Acessa a lista de variedades para isolar as formas Mega.
        for variedade in dados_especie.get("varieties", []):
            nome = variedade["pokemon"]["name"]
            if "mega" in nome:
                url = variedade["pokemon"]["url"]
                pokemon_id = int(url.rstrip("/").split("/")[-1])
                megas.add((pokemon_id, nome, url))

    # 3. Extração isolada das formas Mega encontradas.
    for pokemon_id, nome, url in sorted(megas):
        if pokemon_id in ids_extraidos:
            continue

        caminho_cache = PASTA_CACHE / "pokemon" / f"{pokemon_id}.json"
        dados = buscar_json_com_cache(url, caminho_cache)
        
        documento = dados.copy()
        documento["_id"] = f"pokemon/{pokemon_id}"
        documento["_fonte"] = "pokeapi"
        documento["_url"] = url
        documento["_ingerido_em"] = data_ingestao()

        inserir_documento(colecao_pokemon, documento)
        total += 1
        print(f"Mega extraído: {nome}")

    print(f"\nTotal de Pokémon carregados (Padrão + Mega): {total}")

# EXTRAÇÃO 3 - TIPOS

def extrair_tipos():
    print("\n========================================")
    print("EXTRAINDO TIPOS")
    print("========================================")

    total = 0
    url_lista = f"{POKEAPI_BASE}/type"
    caminho_cache = PASTA_CACHE / "tipos" / "lista.json"

    # Busca a lista completa de tipos mapeados pela API (21 tipos).
    dados_lista = buscar_json_com_cache(url_lista, caminho_cache)

    for tipo in dados_lista["results"]:
        nome = tipo["name"]
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
        print(f"Tipo carregado: {nome}")

    print(f"\nTotal de tipos carregados: {total}")

# EXTRAÇÃO 4 - POKEMON.CSV

def extrair_pokemon_csv():
    print("\n========================================")
    print("EXTRAINDO POKEMON.CSV")
    print("========================================")

    caminho_cache = PASTA_CACHE / "pokemon_csv" / "pokemon.csv"

    # Valida e efetua o cache do arquivo em texto puro (plano).
    if caminho_cache.exists():
        print(f"[CACHE] {caminho_cache}")
        with open(caminho_cache, "r", encoding="utf-8") as arquivo:
            conteudo = arquivo.read()
    else:
        print(f"[CSV] {URL_POKEMON_CSV}")
        response = requests.get(URL_POKEMON_CSV, timeout=30)
        response.raise_for_status()
        conteudo = response.text
        
        caminho_cache.parent.mkdir(parents=True, exist_ok=True)
        with open(caminho_cache, "w", encoding="utf-8") as arquivo:
            arquivo.write(conteudo)

    # Converte o CSV para dicionários Python, mantendo os valores originais.
    leitor = csv.DictReader(StringIO(conteudo))
    total = 0

    for linha in leitor:
        numero_csv = linha["#"]
        documento = linha.copy()

        documento["_id"] = f"pokemon_csv/{numero_csv}"
        documento["_fonte"] = "pokemon.csv"
        documento["_url"] = URL_POKEMON_CSV
        documento["_ingerido_em"] = data_ingestao()

        inserir_documento(colecao_pokemon_csv, documento)
        total += 1

    print(f"\nTotal de cadastros CSV carregados: {total}")

# EXTRAÇÃO 5 - COMBATS.CSV

def extrair_combates():
    print("\n========================================")
    print("EXTRAINDO COMBATS.CSV")
    print("========================================")

    caminho_cache = PASTA_CACHE / "combates" / "combats.csv"

    # Realiza o cache da listagem de batalhas.
    if caminho_cache.exists():
        print(f"[CACHE] {caminho_cache}")
        with open(caminho_cache, "r", encoding="utf-8") as arquivo:
            conteudo = arquivo.read()
    else:
        print(f"[CSV] {URL_COMBATES_CSV}")
        response = requests.get(URL_COMBATES_CSV, timeout=30)
        response.raise_for_status()
        conteudo = response.text
        
        caminho_cache.parent.mkdir(parents=True, exist_ok=True)
        with open(caminho_cache, "w", encoding="utf-8") as arquivo:
            arquivo.write(conteudo)

    # Lê as linhas, criando um identificador autoincremental seguro
    # já que combats.csv não possui chave natural própria.
    leitor = csv.DictReader(StringIO(conteudo))
    total = 0

    for numero_linha, linha in enumerate(leitor, start=1):
        documento = linha.copy()

        documento["_id"] = f"combate/{numero_linha}"
        documento["_fonte"] = "combats.csv"
        documento["_url"] = URL_COMBATES_CSV
        documento["_ingerido_em"] = data_ingestao()

        inserir_documento(colecao_combates, documento)
        total += 1

    print(f"\nTotal de combates carregados: {total}")

# ORQUESTRAÇÃO PRINCIPAL

def main():
    print("\n============================================")
    print("      EP01 - EXTRAÇÃO PARA A CAMADA BRONZE")
    print("============================================")
    print(f"Banco Alvo: {BANCO}")

    try:
        # Valida a conexão com o MongoDB antes de iniciar o processo.
        cliente.admin.command("ping")
        print("MongoDB conectado com sucesso!")

        # A execução obedece à ordem hierárquica das dependências.
        extrair_especies()
        extrair_pokemon()
        extrair_tipos()
        extrair_pokemon_csv()
        extrair_combates()

        print("\n============================================")
        print("EXTRAÇÃO CONCLUÍDA COM SUCESSO")
        print("============================================")

    except Exception as erro:
        print("\nERRO DURANTE A EXTRAÇÃO:")
        print(erro)
        raise

    finally:
        # Garante o fechamento da conexão com o banco.
        cliente.close()

if __name__ == "__main__":
    main()