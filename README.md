# EP01: ETL e Arquitetura Medalhão

**Integrantes do Grupo:**
- Isaias Maia de Oliveira
- Daniel Santos Baptista

## 1. Ambiente e Configuração Inicial

Este projeto foi desenvolvido para suportar execução em ambientes baseados em contêineres, como o GitHub Codespaces, utilizando o Docker para a infraestrutura de banco de dados.

### 1.1 Instalação de Dependências

Certifique-se de instalar as bibliotecas Python necessárias listadas no repositório:

```bash
pip install -r requirements.txt
```

### 1.2 Inicialização do MongoDB (Camada Bronze)

A camada bronze requer o MongoDB para armazenar os dados brutos. Inicie uma instância do banco via Docker rodando em segundo plano:

```bash
docker run -d -p 27017:27017 --name mongodb mongo
```

Em seguida, configure a variável de ambiente apontando para o banco recém-criado:

```bash
export MONGODB_URL="mongodb://localhost:27017"
```

## 2. Execução do Pipeline
A ordem de execução dos scripts deve ser estritamente respeitada para garantir o fluxo da arquitetura medalhão.

### 2.1 Extração para a Camada Bronze
O script de extração consome a PokéAPI e os arquivos CSV de batalhas, gravando-os no banco pokedex_bronze.

```bash
python extrair.py
```

O script utiliza um cache local (dados_brutos/) para gravar as respostas JSON e evitar sobrecarga na rede. A segunda execução consecutiva deste script fará zero requisições HTTP à API. 

## 3. Decisões de Arquitetura

### 3.1 Uso de Banco de Documentos na Camada Bronze

A escolha do MongoDB para a camada bronze justifica-se pela natureza da PokéAPI, que entrega entidades em formato JSON fortemente aninhado. Atributos como stats[], types[] e abilities[] contêm listas de subdocumentos que perderiam sua estrutura original caso fossem mapeados imediatamente para tabelas relacionais. O banco de documentos permite armazenar o dado bruto, idêntico ao que a fonte entregou, satisfazendo a restrição de não transformação exigida nesta etapa. 

### 3.2 Garantia de Idempotência

A idempotência no script extrair.py é assegurada pela derivação da chave natural da origem para o campo _id dos documentos (por exemplo, pokemon/25 ou combate/1). A inserção no MongoDB é feita através da operação update_one com a flag upsert=True. Consequentemente, repetições do script sobrescrevem o estado anterior sem gerar duplicação de documentos na base de dados.  