# EP01: ETL e Arquitetura Medalhão

**Integrantes do grupo:**
- Isaias Maia de Oliveira
- Daniel Santos Baptista

Este repositório implementa o pipeline completo da EP01 de Ciência de Dados: fontes públicas → **Bronze/MongoDB** → **Silver/PostgreSQL** → **Gold/PostgreSQL** → análises SQL.

## 1. Arquitetura

```text
PokéAPI + pokemon.csv + combats.csv
              |
              v
      Bronze / MongoDB
      pokedex_bronze
              |
          extrair.py
              |
              v
     Silver / PostgreSQL
   schema silver (estrela)
              |
          carregar.py
              |
              v
      Gold / PostgreSQL
 schema gold (agregados)
              |
          publicar.py
              |
              v
       sql/consultas.sql
```

Os scripts respeitam fronteiras adjacentes: `extrair.py` acessa as fontes e escreve apenas na Bronze; `carregar.py` lê apenas a Bronze e escreve na Silver; `publicar.py` lê apenas a Silver e materializa a Gold.

## 2. Como executar

### 2.1 Dependências Python

Requer Python 3.11+.

```bash
python -m pip install -r requirements.txt
```

O projeto não utiliza `pandas`, `polars`, `numpy`, `pyarrow` nem biblioteca equivalente de manipulação tabular em memória. As dependências externas são somente cliente HTTP e drivers dos bancos.

### 2.2 MongoDB

Exemplo com Docker:

```bash
docker run -d --name ep01-mongodb -p 27017:27017 mongo:7
```

Linux/macOS:

```bash
export MONGODB_URL="mongodb://localhost:27017"
```

PowerShell:

```powershell
$env:MONGODB_URL="mongodb://localhost:27017"
```

Se `MONGODB_URL` não for informada, o código usa `mongodb://localhost:27017`.

### 2.3 PostgreSQL

Exemplo com Docker:

```bash
docker run -d --name ep01-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=pokedex \
  -p 5432:5432 postgres:16
```

Linux/macOS:

```bash
export POSTGRES_URL="postgresql://postgres:postgres@localhost:5432/pokedex"
```

PowerShell:

```powershell
$env:POSTGRES_URL="postgresql://postgres:postgres@localhost:5432/pokedex"
```

Se `POSTGRES_URL` não for informada, essa mesma URL local é utilizada como padrão.

### 2.4 Ordem do pipeline

```bash
python extrair.py
python carregar.py
python publicar.py
```

Depois, execute as análises:

```bash
psql "$POSTGRES_URL" -f sql/consultas.sql
```

No PowerShell, pode-se usar o valor literal da conexão no lugar de `$POSTGRES_URL`. As consultas também podem ser abertas no pgAdmin ou em outro cliente PostgreSQL.

## 3. Bronze: por que MongoDB

A PokéAPI devolve JSON aninhado e heterogêneo. Campos como `types[]`, `stats[]`, `abilities[]`, `varieties[]` e `damage_relations` contêm listas e subdocumentos que perderiam sua forma original se fossem achatados imediatamente em tabelas relacionais. O MongoDB permite persistir cada resposta exatamente na estrutura entregue pela fonte e, portanto, é adequado à responsabilidade da Bronze: preservar o dado bruto e reprocessável.

O banco `pokedex_bronze` possui cinco coleções:

| Coleção | Origem |
|---|---|
| `pokemon` | `/pokemon/{id}` para as formas padrão e todas as variedades das espécies 1..721 |
| `especies` | `/pokemon-species/{id}` para 1..721 |
| `tipos` | `/type/{id}` |
| `pokemon_csv` | uma linha de `pokemon.csv` por documento |
| `combates` | uma linha de `combats.csv` por documento |

A extração dos tipos consulta a listagem com `limit=100`, evitando a paginação padrão da API e garantindo que os 21 tipos retornados pela fonte sejam preservados na Bronze. Na Silver são usados somente os IDs 1..18, porque `stellar`, `unknown` e `shadow` não pertencem ao universo de tipos do conjunto de batalhas da EP.

### Cache, linhagem e idempotência da Bronze

Antes de qualquer escrita no MongoDB, as respostas da API e os dois CSVs são gravados em `dados_brutos/`. A API só é acessada quando o arquivo bruto correspondente não existe. Por isso, a segunda execução consecutiva realiza zero requisições às fontes.

Cada documento recebe `_id` derivado da chave natural, `_fonte`, `_url` e `_ingerido_em`. A escrita usa `update_one(..., upsert=True)`. `_ingerido_em` é definido com `$setOnInsert`, logo não é regravado em uma nova execução sobre o mesmo cache.

`dados_brutos/` é cache reconstituível e permanece no `.gitignore`.

## 4. Silver: modelo dimensional

**Grão da tabela fato:** uma linha de `silver.fato_participacao` representa **a participação de um Pokémon em um combate**. Assim, 50.000 combates produzem exatamente 100.000 participações.

Esse grão foi escolhido antes da modelagem porque transforma taxa de vitórias em `AVG(venceu)`, evita procurar o Pokémon em duas colunas para análises por participante e faz cada confronto alimentar naturalmente as duas orientações da matriz de tipos.

### 4.1 Esquema estrela

```text
                            +--------------------+
                            | silver.dim_pokemon |
                            | Pokémon / oponente |
                            +---------+----------+
                                      |
        +------------------+          |          +--------------------+
        | silver.dim_tipo  |----------+----------| silver.dim_geracao |
        | quatro papéis    |     fato_particip.  | dois papéis        |
        +------------------+          |          +--------------------+
                                      |
                            +---------v----------+
                            | fato_participacao  |
                            +--------------------+

silver.efetividade_tipo = relação 18 x 18 entre dois papéis de dim_tipo
silver.log_conciliacao  = artefato de auditoria, fora do esquema estrela
```

As dimensões não apontam umas para as outras. `dim_pokemon`, `dim_tipo` e `dim_geracao` são ligadas diretamente à fato em papéis diferentes. Todas possuem chaves substitutas geradas pelo PostgreSQL; os identificadores das fontes permanecem apenas como atributos auditáveis.

### 4.2 Conciliação das chaves

O campo `#` do `pokemon.csv` não é número da Pokédex. A conciliação é feita por nome em `carregar.py`:

1. normalização Unicode e remoção de acentos;
2. tratamento dos símbolos `♀` e `♂`;
3. separação de CamelCase, necessária para casos como `DeoxysAttack Forme`;
4. remoção apenas de marcadores genéricos de apresentação (`Forme`, `Form`, `Mode`, `Cloak`, `Size`);
5. comparação por forma compacta e por assinatura de tokens independente da ordem, resolvendo casos como `Mega Charizard X` ↔ `charizard-mega-x` e `Heat Rotom` ↔ `rotom-heat`;
6. validação adicional por geração e tipos;
7. exceções semânticas documentadas no código para nomes que não podem ser obtidos apenas por normalização, como `Basculin`, `Zygarde Half Forme` e `Hoopa Confined`.

O resultado de **cada uma das 800 linhas** é gravado em `silver.log_conciliacao`, que é a alternativa permitida pelo R4 ao arquivo `conciliacao.csv`. Nenhuma linha é descartada silenciosamente.

A linha CSV `#63`, cujo nome está ausente na fonte, **não é inferida por posição**. Ela é mantida como membro especial de `dim_pokemon`, com nome legível `[NOME AUSENTE - CSV #63]`, preservando tipo, geração e atributos existentes no CSV. Os combates que a referenciam permanecem na fato.

### 4.3 Herança das formas alternativas

Uma forma alternativa existe em `/pokemon/`, mas os atributos de espécie residem em `/pokemon-species/`. Após a conciliação, `carregar.py` usa o campo `species.url` do documento da forma para localizar a espécie na própria Bronze e herdar geração da espécie, habitat, cor, forma corporal, taxa de crescimento, taxa de captura, felicidade e indicadores de raridade. Nenhuma chamada à PokéAPI é realizada pela Silver.

### 4.4 Ausências com significados diferentes

As ausências não são tratadas da mesma maneira:

- **nome ausente do CSV #63:** `DADO AUSENTE`, representado por membro especial de `dim_pokemon`;
- **habitat nulo em gerações posteriores:** `NAO_APLICAVEL`, registrado em `habitat_situacao`;
- **habitat nulo quando o conceito deveria ser aplicável:** `DADO_AUSENTE`;
- **ausência de segundo tipo:** a fato usa o membro especial `sem_tipo_secundario` em `dim_tipo`, evitando FK nula. Para efetividade, esse segundo fator vale 1.

## 5. As seis decisões de modelagem

### Decisão 1 — Grão da fato

Foi adotada **uma linha por participação em combate**, totalizando 100.000 linhas. O custo é duplicar o número físico de linhas em relação a uma fato de 50.000 combates. O benefício é que winrate passa a ser uma média direta de `venceu`, o oponente assume papel explícito e cada batalha fornece uma observação para cada lado.

### Decisão 2 — Diferença de velocidade

`diferenca_velocidade = velocidade - velocidade_oponente` é materializada na fato. Isso ocupa uma coluna adicional, mas evita recalcular a comparação em todas as análises e deixa a métrica numérica pronta para `SUM`, `AVG` e `COUNT`.

As faixas usadas na Gold são: `<= -50`, `-49 a -20`, `-19 a -1`, `0`, `1 a 19`, `20 a 49` e `>= 50`. São faixas simétricas em torno de zero, distinguem empate e separam diferenças pequenas, médias e grandes sem criar dezenas de grupos pouco interpretáveis.

### Decisão 3 — Efetividade de tipos

A matriz completa 18 x 18 é materializada em `silver.efetividade_tipo`, com 324 pares e multiplicadores 0, 0,5, 1 ou 2. A análise 6 adota o **multiplicador efetivo contra os dois tipos do defensor**: multiplica-se a efetividade do tipo primário atacante contra o tipo primário e, quando houver, contra o secundário. Assim, os valores possíveis são 0, 0,25, 0,5, 1, 2 e 4.

O custo é realizar duas junções com `efetividade_tipo` durante a publicação. O benefício é manter a mecânica consultável em SQL e não escondida em um dicionário Python.

### Decisão 4 — Representação do oponente

`dim_pokemon` é uma **dimensão papel**: a fato possui `pokemon_sk` e `oponente_sk`, ambos referenciando a mesma dimensão. O mesmo princípio é aplicado aos papéis de tipo e geração. Isso evita duplicar dimensões fisicamente e preserva o esquema estrela.

### Decisão 5 — Atributos de status

Os seis atributos de status ficam em `dim_pokemon`, pois descrevem o cadastro. A velocidade é também materializada na fato (`velocidade`, `velocidade_oponente` e `diferenca_velocidade`) porque a análise 5 compara os dois lados. A duplicação controlada custa espaço, mas simplifica o uso analítico e evita joins desnecessários para uma métrica central da fato.

Para análises de status, o CSV é a fonte de verdade, pois esses valores pertencem exatamente ao conjunto usado pelo simulador de batalhas; a PokéAPI fornece metadados descritivos complementares.

### Decisão 6 — Categoria de raridade

A categoria é derivada uma vez na carga Silver: `MITICO` > `LENDARIO` > `BEBE` > `COMUM`. Nas formas alternativas, os indicadores são herdados da espécie. Quando a linha não pode ser conciliada com a API, o indicador `Legendary` do CSV é preservado como fallback. A vantagem é disponibilizar a classificação a qualquer pergunta futura sem repetir `CASE` em cada consulta.

## 6. Integridade e suficiência da Silver

- todas as dimensões possuem `PRIMARY KEY` substituta;
- todas as FKs da fato são `NOT NULL` e declaradas no PostgreSQL;
- a falta de segundo tipo é representada por membro especial, não por FK nula;
- `pokemon_csv_id` e `pokeapi_pokemon_id` permanecem como chaves naturais auditáveis;
- a matriz de efetividade está no banco, não apenas no Python;
- entram 50.000 combates e permanecem 50.000 combates, representados por 100.000 participações;
- as análises 1 e 2 usam a dimensão de cadastro, evitando ponderação indevida pelo número de batalhas;
- as análises de batalhas usam métricas numéricas da fato e podem ser agregadas integralmente dentro do PostgreSQL.

`carregar.py` pode ser executado sem acesso à rede: ele lê somente MongoDB, `sql/silver.sql` e PostgreSQL.

## 7. Gold

`publicar.py` executa `sql/gold.sql` e reconstrói as tabelas abaixo por `INSERT INTO ... SELECT ... FROM silver...`, sem transportar a fato para a memória do Python:

| Tabela | Grão | Análise |
|---|---|---|
| `gold.ranking_pokemon` | um Pokémon | 3 |
| `gold.taxa_vitorias_por_tipo` | um tipo primário | 4 |
| `gold.taxa_vitorias_por_faixa_velocidade` | uma faixa de diferença | 5 |
| `gold.taxa_vitorias_por_multiplicador` | um multiplicador efetivo | 6 |
| `gold.matriz_confronto` | par tipo A x tipo B | 7 |
| `gold.vantagem_primeiro_ataque` | posição na ordem de ataque | 8 |

A matriz de confronto contém todas as 324 combinações, inclusive pares sem observação. Cada batalha alimenta duas orientações porque a fato possui uma participação por lado; a coluna `First_pokemon` não define a orientação da análise 7.

Na análise 3 o corte recomendado no arquivo de consultas é **50 combates**. A Gold não aplica esse corte durante a carga: `total_combates` permanece materializado ao lado do winrate, então o limiar pode ser alterado somente com `WHERE`.

## 8. Análise proposta pelo grupo

**Pergunta:** *Atacar primeiro está associado a uma taxa de vitórias maior nas batalhas simuladas?*

A pergunta é relevante porque o `combats.csv` registra explicitamente quem aparece como `First_pokemon`, informação não explorada pelas sete análises obrigatórias. Ela exige uma capacidade adicional do modelo: a métrica `atacou_primeiro` na fato. A tabela `gold.vantagem_primeiro_ataque` possui uma linha para `ATACOU_PRIMEIRO` e uma para `ATACOU_SEGUNDO`, com quantidade de confrontos, vitórias e taxa de vitórias.

Essa análise não é uma troca de coluna das análises obrigatórias: investiga uma propriedade temporal/posicional do confronto, ausente das demais.

## 9. Idempotência por camada

- **Bronze:** cache em disco + `_id` natural + `upsert`; `_ingerido_em` somente no primeiro insert.
- **Silver:** o DDL é versionado e executado por `carregar.py`; as tabelas são truncadas e reconstruídas integralmente a partir da Bronze dentro de uma transação. Reexecutar produz o mesmo conjunto analítico, sem duplicação.
- **Gold:** `publicar.py` trunca e repopula os agregados exclusivamente a partir da Silver. Não há `GROUP BY` nem join nas consultas finais da Gold.

Ao final de cada script são impressas as contagens e o instante da execução. Isso permite verificar rapidamente os valores de referência: 721 espécies na Bronze, 800 registros do CSV, 50.000 combates, 800 linhas em `dim_pokemon`, 18 tipos reais + 1 membro especial, 6 gerações, 324 pares de efetividade, 100.000 participações e 324 posições na matriz Gold.

## 10. Arquivos

```text
.
├── README.md
├── RELATORIO.md
├── requirements.txt
├── extrair.py
├── carregar.py
├── publicar.py
├── sql/
│   ├── silver.sql
│   ├── gold.sql
│   └── consultas.sql
└── dados_brutos/        # cache local; não versionado
```

O requisito R4 é atendido por `silver.log_conciliacao`, portanto `conciliacao.csv` é dispensado pelo próprio enunciado.

## 11. Observação sobre o relatório

`RELATORIO.md` está estruturado para as oito análises. As saídas numéricas devem corresponder à execução real do pipeline no ambiente de entrega; não devem ser inventadas nem copiadas de outra execução. Depois de executar `sql/consultas.sql`, registre os resultados e interprete-os no relatório antes da submissão final do repositório.
