# Relatório — EP01: ETL e Arquitetura Medalhão

**Integrantes:** Isaias Maia de Oliveira e Daniel Santos Baptista.

Este relatório registra as **saídas reais** obtidas após a execução completa do pipeline (`extrair.py` → `carregar.py` → `publicar.py` → `sql/consultas.sql`) no PostgreSQL. As taxas de vitória são apresentadas como proporções entre 0 e 1, exatamente como retornadas pelas consultas.

## 1. Quantidade de Pokémon por tipo primário e geração

### Pergunta

Como os Pokémon do cadastro se distribuem entre os 18 tipos primários e as gerações I a VI?

### Resultado da execução

| tipo | geracao_1 | geracao_2 | geracao_3 | geracao_4 | geracao_5 | geracao_6 | total |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bug | 14 | 12 | 12 | 10 | 18 | 3 | 69 |
| dark | 0 | 6 | 6 | 3 | 13 | 3 | 31 |
| dragon | 3 | 0 | 12 | 4 | 9 | 4 | 32 |
| electric | 9 | 7 | 5 | 12 | 8 | 3 | 44 |
| fairy | 2 | 5 | 0 | 1 | 0 | 9 | 17 |
| fighting | 7 | 2 | 5 | 3 | 7 | 3 | 27 |
| fire | 14 | 8 | 8 | 5 | 9 | 8 | 52 |
| flying | 0 | 0 | 0 | 0 | 2 | 2 | 4 |
| ghost | 4 | 1 | 5 | 7 | 5 | 10 | 32 |
| grass | 13 | 9 | 13 | 15 | 15 | 5 | 70 |
| ground | 8 | 3 | 7 | 4 | 10 | 0 | 32 |
| ice | 2 | 4 | 7 | 3 | 6 | 2 | 24 |
| normal | 24 | 15 | 18 | 18 | 19 | 4 | 98 |
| poison | 14 | 1 | 3 | 6 | 2 | 2 | 28 |
| psychic | 11 | 7 | 12 | 8 | 14 | 5 | 57 |
| rock | 10 | 5 | 8 | 6 | 6 | 9 | 44 |
| steel | 0 | 3 | 12 | 3 | 4 | 5 | 27 |
| water | 31 | 18 | 27 | 13 | 18 | 5 | 112 |

A soma da matriz é de **800 Pokémon**. Por geração, foram obtidos **166** registros na geração I, **106** na II, **160** na III, **121** na IV, **165** na V e **82** na VI.

### Interpretação

A matriz confirma que os 800 registros conciliados/preservados chegaram à Silver sem perda. `water` é o tipo primário mais frequente, com **112** Pokémon, seguido de `normal` (**98**), `grass` (**70**) e `bug` (**69**). `flying` aparece como tipo primário em apenas **4** registros, embora seja comum como tipo secundário. As células iguais a zero representam combinações de tipo primário e geração que não aparecem no cadastro analisado, e não falhas de carga.

---

## 2. Médias dos atributos de status por tipo primário

### Pergunta

Quais são as médias de HP, ataque, defesa, ataque especial, defesa especial e velocidade por tipo? Qual tipo possui maior velocidade média, qual apresenta maior resistência média e existe um tipo que lidere todos os atributos simultaneamente?

### Resultado da execução — médias por tipo

| tipo | hp_medio | ataque_medio | defesa_media | ataque_especial_medio | defesa_especial_media | velocidade_media | resistencia_media |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bug | 56.88 | 70.97 | 70.72 | 53.87 | 64.80 | 61.68 | 64.14 |
| dark | 66.81 | 88.39 | 70.23 | 74.65 | 69.52 | 76.16 | 68.85 |
| dragon | 83.31 | 112.13 | 86.38 | 96.84 | 88.84 | 83.03 | 86.18 |
| electric | 59.80 | 69.09 | 66.30 | 90.02 | 73.70 | 84.50 | 66.60 |
| fairy | 74.12 | 61.53 | 65.71 | 78.53 | 84.71 | 48.59 | 74.84 |
| fighting | 69.85 | 96.78 | 65.93 | 53.11 | 64.70 | 66.07 | 66.83 |
| fire | 69.90 | 84.77 | 67.77 | 88.98 | 72.21 | 74.44 | 69.96 |
| flying | 70.75 | 78.75 | 66.25 | 94.25 | 72.50 | 102.50 | 69.83 |
| ghost | 64.44 | 73.78 | 81.19 | 79.34 | 76.47 | 64.34 | 74.03 |
| grass | 67.27 | 73.21 | 70.80 | 77.50 | 70.43 | 61.93 | 69.50 |
| ground | 73.78 | 95.75 | 84.84 | 56.47 | 62.75 | 63.91 | 73.79 |
| ice | 72.00 | 72.75 | 71.42 | 77.54 | 76.29 | 63.46 | 73.24 |
| normal | 77.28 | 73.47 | 59.85 | 55.82 | 63.72 | 71.55 | 66.95 |
| poison | 67.25 | 74.68 | 68.82 | 60.43 | 64.39 | 63.57 | 66.82 |
| psychic | 70.63 | 71.46 | 67.68 | 98.40 | 86.28 | 81.49 | 74.87 |
| rock | 65.36 | 92.86 | 100.80 | 63.34 | 75.48 | 55.91 | 80.55 |
| steel | 65.22 | 92.70 | 126.37 | 67.52 | 80.63 | 55.26 | 90.74 |
| water | 72.06 | 74.15 | 72.95 | 74.81 | 70.52 | 65.96 | 71.84 |

### Maior velocidade média

| tipo | velocidade_media |
| --- | --- |
| flying | 102.50 |

### Maior resistência média

| tipo | resistencia_media |
| --- | --- |
| steel | 90.74 |

### Liderança simultânea dos seis atributos

A consulta 2D retornou **0 linhas**.

### Interpretação

A resistência foi definida como a média simples de HP, Defesa e Defesa Especial. O tipo `flying` apresentou a maior velocidade média (**102,50**), mas esse resultado deve ser lido junto da análise 1: há somente **4 Pokémon** cujo tipo primário é `flying`, portanto a média é baseada em um grupo pequeno. O tipo `steel` apresentou a maior resistência média (**90,74**), coerente com sua defesa média elevada (**126,37**). Nenhum tipo liderou simultaneamente HP, ataque, defesa, ataque especial, defesa especial e velocidade; logo, os dados não indicam um único tipo dominante em todos os atributos médios.

---

## 3. Taxa de vitórias por Pokémon

### Pergunta

Quais Pokémon apresentam as dez maiores e as dez menores taxas de vitória entre aqueles com pelo menos 50 combates?

### Dez maiores taxas

| pokemon_csv_id | pokemon_nome | total_combates | vitorias | taxa_vitorias |
| --- | --- | --- | --- | --- |
| 155 | Mega Aerodactyl | 129 | 127 | 0.984496 |
| 513 | Weavile | 119 | 116 | 0.974790 |
| 704 | Tornadus Therian Forme | 125 | 121 | 0.968000 |
| 20 | Mega Beedrill | 119 | 115 | 0.966387 |
| 154 | Aerodactyl | 141 | 136 | 0.964539 |
| 477 | Mega Lopunny | 129 | 124 | 0.961240 |
| 727 | Greninja | 127 | 122 | 0.960630 |
| 717 | Meloetta Pirouette Forme | 123 | 118 | 0.959350 |
| 165 | Mega Mewtwo Y | 125 | 119 | 0.952000 |
| 350 | Mega Sharpedo | 120 | 114 | 0.950000 |

### Dez menores taxas

| pokemon_csv_id | pokemon_nome | total_combates | vitorias | taxa_vitorias |
| --- | --- | --- | --- | --- |
| 231 | Shuckle | 135 | 0 | 0.000000 |
| 290 | Silcoon | 138 | 3 | 0.021739 |
| 190 | Togepi | 122 | 3 | 0.024590 |
| 639 | Solosis | 129 | 4 | 0.031008 |
| 237 | Slugma | 123 | 4 | 0.032520 |
| 577 | Munna | 128 | 5 | 0.039063 |
| 189 | Igglybuff | 115 | 5 | 0.043478 |
| 395 | Wynaut | 130 | 6 | 0.046154 |
| 210 | Wooper | 125 | 6 | 0.048000 |
| 292 | Cascoon | 133 | 7 | 0.052632 |

### Interpretação

O corte mínimo de 50 combates evita que taxas extremas sejam produzidas por pouquíssimas observações. O maior winrate foi o de **Mega Aerodactyl**, com **127 vitórias em 129 combates (0,984496)**. Em seguida aparecem **Weavile (0,974790)** e **Tornadus Therian Forme (0,968000)**. Na outra extremidade, **Shuckle** disputou **135** combates e não venceu nenhum, resultando em taxa **0,000000**. Os demais Pokémon da parte inferior também apresentam amostras superiores a 100 combates, o que reforça que os valores extremos observados não decorrem apenas de denominadores pequenos.

---

## 4. Taxa de vitórias por tipo primário

### Pergunta

Como a taxa de vitórias varia entre os tipos primários? Há algum tipo que se destaque nos dados simulados?

### Resultado da execução

| tipo | total_combates | vitorias | taxa_vitorias |
| --- | --- | --- | --- |
| flying | 478 | 362 | 0.757322 |
| dark | 3845 | 2447 | 0.636411 |
| dragon | 3932 | 2490 | 0.633266 |
| electric | 5346 | 3370 | 0.630378 |
| fire | 6552 | 3802 | 0.580281 |
| psychic | 7320 | 3998 | 0.546175 |
| normal | 12098 | 6518 | 0.538767 |
| ground | 3889 | 2088 | 0.536899 |
| ghost | 3908 | 1877 | 0.480297 |
| water | 14041 | 6569 | 0.467844 |
| fighting | 3306 | 1543 | 0.466727 |
| ice | 3079 | 1357 | 0.440728 |
| grass | 8426 | 3707 | 0.439948 |
| bug | 8760 | 3772 | 0.430594 |
| poison | 3654 | 1571 | 0.429940 |
| steel | 3546 | 1523 | 0.429498 |
| rock | 5669 | 2299 | 0.405539 |
| fairy | 2151 | 707 | 0.328684 |

### Interpretação

`flying` apresentou a maior taxa observada (**0,757322**), porém em apenas **478** participações, número muito menor que o de tipos como `water` (**14.041**) e `normal` (**12.098**). Entre tipos com milhares de participações, `dark` (**0,636411**), `dragon` (**0,633266**) e `electric` (**0,630378**) aparecem no topo. `fairy` apresentou a menor taxa (**0,328684**). Esses valores descrevem o comportamento do conjunto de batalhas simuladas; não isolam um efeito causal do tipo, pois cada grupo contém Pokémon com distribuições diferentes de velocidade, ataque, defesa e demais atributos.

---

## 5. Diferença de velocidade e vitória

### Pergunta

Como a probabilidade de vitória muda quando o Pokémon é mais lento, tem velocidade semelhante ou é mais rápido que o oponente?

### Resultado da execução

| ordem_faixa | faixa_velocidade | total_confrontos | vitorias | taxa_vitorias |
| --- | --- | --- | --- | --- |
| 1 | <= -50 | 12407 | 1166 | 0.093979 |
| 2 | -49 a -20 | 20489 | 1315 | 0.064181 |
| 3 | -19 a -1 | 15776 | 492 | 0.031187 |
| 4 | 0 | 2656 | 1328 | 0.500000 |
| 5 | 1 a 19 | 15776 | 15284 | 0.968813 |
| 6 | 20 a 49 | 20489 | 19174 | 0.935819 |
| 7 | >= 50 | 12407 | 11241 | 0.906021 |

### Interpretação

O sinal da diferença de velocidade está fortemente associado ao resultado. Quando as velocidades são iguais, a taxa é exatamente **0,500000**. Participantes mais rápidos apresentaram taxas muito elevadas: **0,968813** para diferenças de 1 a 19, **0,935819** entre 20 e 49 e **0,906021** para diferenças de pelo menos 50. Participantes mais lentos apresentaram taxas abaixo de 10% em todas as faixas negativas.

O efeito não é monotônico com a magnitude: entre os mais rápidos, a maior taxa ocorre na faixa de 1 a 19, e entre os mais lentos a menor taxa ocorre entre -19 e -1. Assim, os dados sustentam uma associação muito forte entre **ser o participante mais rápido** e vencer, mas não sustentam a afirmação simples de que uma diferença cada vez maior aumenta continuamente a probabilidade de vitória. Outros atributos dos Pokémon também participam do resultado.

---

## 6. Vantagem de tipo e vitória

### Pergunta

A taxa de vitórias acompanha o multiplicador de efetividade de tipos?

### Resultado da execução

| multiplicador | total_confrontos | vitorias | taxa_vitorias |
| --- | --- | --- | --- |
| 0.00 | 3234 | 1338 | 0.413729 |
| 0.25 | 2309 | 960 | 0.415764 |
| 0.50 | 20519 | 9702 | 0.472830 |
| 1.00 | 57408 | 29123 | 0.507299 |
| 2.00 | 15242 | 8128 | 0.533263 |
| 4.00 | 1288 | 749 | 0.581522 |

### Interpretação

A taxa de vitória cresce de forma consistente com o multiplicador: **0,413729** para multiplicador 0; **0,415764** para 0,25; **0,472830** para 0,5; **0,507299** para 1; **0,533263** para 2; e **0,581522** para 4. Portanto, o padrão agregado é compatível com a mecânica de efetividade: multiplicadores favoráveis estão associados a taxas maiores.

O efeito, contudo, é moderado quando comparado ao observado na análise de velocidade. Mesmo multiplicador 4 resulta em taxa de aproximadamente 58%, enquanto a vantagem de velocidade produz taxas superiores a 90% nas três faixas positivas. Isso indica que o simulador não é determinado exclusivamente pela tabela de tipos.

---

## 7. Matriz de confronto entre tipos

### Pergunta

Qual é a taxa de vitória do tipo A contra o tipo B nas 324 combinações de tipos primários, e onde a direção observada contradiz a efetividade esperada?

### Resultado da execução — matriz completa 18 × 18

A consulta produziu exatamente **324 posições**, uma para cada par ordenado entre os 18 tipos primários.

<details>
<summary>Exibir as 324 linhas da matriz de confronto</summary>

| tipo_atacante | tipo_defensor | total_confrontos | vitorias | taxa_vitorias | multiplicador_efetividade | expectativa | diverge_da_efetividade |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bug | bug | 772 | 386 | 0.500000 | 1.00 | neutro | f |
| bug | dark | 309 | 112 | 0.362460 | 2.00 | vantagem esperada | t |
| bug | dragon | 342 | 97 | 0.283626 | 1.00 | neutro | f |
| bug | electric | 473 | 126 | 0.266385 | 1.00 | neutro | f |
| bug | fairy | 190 | 116 | 0.610526 | 0.50 | desvantagem esperada | t |
| bug | fighting | 271 | 116 | 0.428044 | 0.50 | desvantagem esperada | f |
| bug | fire | 599 | 198 | 0.330551 | 0.50 | desvantagem esperada | f |
| bug | flying | 38 | 8 | 0.210526 | 0.50 | desvantagem esperada | f |
| bug | ghost | 356 | 162 | 0.455056 | 0.50 | desvantagem esperada | f |
| bug | grass | 764 | 396 | 0.518325 | 2.00 | vantagem esperada | f |
| bug | ground | 335 | 160 | 0.477612 | 1.00 | neutro | f |
| bug | ice | 295 | 144 | 0.488136 | 1.00 | neutro | f |
| bug | normal | 1066 | 412 | 0.386492 | 1.00 | neutro | f |
| bug | poison | 324 | 151 | 0.466049 | 0.50 | desvantagem esperada | f |
| bug | psychic | 646 | 274 | 0.424149 | 2.00 | vantagem esperada | t |
| bug | rock | 487 | 223 | 0.457906 | 1.00 | neutro | f |
| bug | steel | 289 | 136 | 0.470588 | 0.50 | desvantagem esperada | f |
| bug | water | 1204 | 555 | 0.460963 | 1.00 | neutro | f |
| dark | bug | 309 | 197 | 0.637540 | 1.00 | neutro | f |
| dark | dark | 148 | 74 | 0.500000 | 0.50 | desvantagem esperada | t |
| dark | dragon | 149 | 77 | 0.516779 | 1.00 | neutro | f |
| dark | electric | 210 | 94 | 0.447619 | 1.00 | neutro | f |
| dark | fairy | 83 | 66 | 0.795181 | 0.50 | desvantagem esperada | t |
| dark | fighting | 103 | 52 | 0.504854 | 0.50 | desvantagem esperada | t |
| dark | fire | 249 | 127 | 0.510040 | 1.00 | neutro | f |
| dark | flying | 23 | 6 | 0.260870 | 1.00 | neutro | f |
| dark | ghost | 142 | 95 | 0.669014 | 2.00 | vantagem esperada | f |
| dark | grass | 332 | 240 | 0.722892 | 1.00 | neutro | f |
| dark | ground | 148 | 90 | 0.608108 | 1.00 | neutro | f |
| dark | ice | 119 | 81 | 0.680672 | 1.00 | neutro | f |
| dark | normal | 495 | 271 | 0.547475 | 1.00 | neutro | f |
| dark | poison | 125 | 83 | 0.664000 | 1.00 | neutro | f |
| dark | psychic | 291 | 275 | 0.945017 | 2.00 | vantagem esperada | f |
| dark | rock | 246 | 181 | 0.735772 | 1.00 | neutro | f |
| dark | steel | 153 | 103 | 0.673203 | 1.00 | neutro | f |
| dark | water | 520 | 335 | 0.644231 | 1.00 | neutro | f |
| dragon | bug | 342 | 245 | 0.716374 | 1.00 | neutro | f |
| dragon | dark | 149 | 72 | 0.483221 | 1.00 | neutro | f |
| dragon | dragon | 150 | 75 | 0.500000 | 2.00 | vantagem esperada | t |
| dragon | electric | 178 | 97 | 0.544944 | 1.00 | neutro | f |
| dragon | fairy | 84 | 9 | 0.107143 | 0.00 | desvantagem esperada | f |
| dragon | fighting | 123 | 83 | 0.674797 | 1.00 | neutro | f |
| dragon | fire | 252 | 143 | 0.567460 | 1.00 | neutro | f |
| dragon | flying | 22 | 4 | 0.181818 | 1.00 | neutro | f |
| dragon | ghost | 153 | 105 | 0.686275 | 1.00 | neutro | f |
| dragon | grass | 313 | 216 | 0.690096 | 1.00 | neutro | f |
| dragon | ground | 137 | 95 | 0.693431 | 1.00 | neutro | f |
| dragon | ice | 116 | 80 | 0.689655 | 1.00 | neutro | f |
| dragon | normal | 479 | 275 | 0.574113 | 1.00 | neutro | f |
| dragon | poison | 173 | 119 | 0.687861 | 1.00 | neutro | f |
| dragon | psychic | 276 | 148 | 0.536232 | 1.00 | neutro | f |
| dragon | rock | 260 | 194 | 0.746154 | 1.00 | neutro | f |
| dragon | steel | 141 | 112 | 0.794326 | 0.50 | desvantagem esperada | t |
| dragon | water | 584 | 418 | 0.715753 | 1.00 | neutro | f |
| electric | bug | 473 | 347 | 0.733615 | 1.00 | neutro | f |
| electric | dark | 210 | 116 | 0.552381 | 1.00 | neutro | f |
| electric | dragon | 178 | 81 | 0.455056 | 0.50 | desvantagem esperada | f |
| electric | electric | 268 | 134 | 0.500000 | 0.50 | desvantagem esperada | t |
| electric | fairy | 132 | 108 | 0.818182 | 1.00 | neutro | f |
| electric | fighting | 179 | 123 | 0.687151 | 1.00 | neutro | f |
| electric | fire | 327 | 196 | 0.599388 | 1.00 | neutro | f |
| electric | flying | 16 | 5 | 0.312500 | 2.00 | vantagem esperada | t |
| electric | ghost | 214 | 163 | 0.761682 | 1.00 | neutro | f |
| electric | grass | 459 | 306 | 0.666667 | 0.50 | desvantagem esperada | t |
| electric | ground | 218 | 21 | 0.096330 | 0.00 | desvantagem esperada | f |
| electric | ice | 163 | 116 | 0.711656 | 1.00 | neutro | f |
| electric | normal | 676 | 418 | 0.618343 | 1.00 | neutro | f |
| electric | poison | 201 | 145 | 0.721393 | 1.00 | neutro | f |
| electric | psychic | 422 | 239 | 0.566351 | 1.00 | neutro | f |
| electric | rock | 286 | 204 | 0.713287 | 1.00 | neutro | f |
| electric | steel | 211 | 150 | 0.710900 | 1.00 | neutro | f |
| electric | water | 713 | 498 | 0.698457 | 2.00 | vantagem esperada | f |
| fairy | bug | 190 | 74 | 0.389474 | 1.00 | neutro | f |
| fairy | dark | 83 | 17 | 0.204819 | 2.00 | vantagem esperada | t |
| fairy | dragon | 84 | 75 | 0.892857 | 2.00 | vantagem esperada | f |
| fairy | electric | 132 | 24 | 0.181818 | 1.00 | neutro | f |
| fairy | fairy | 50 | 25 | 0.500000 | 1.00 | neutro | f |
| fairy | fighting | 62 | 21 | 0.338710 | 2.00 | vantagem esperada | t |
| fairy | fire | 142 | 31 | 0.218310 | 0.50 | desvantagem esperada | f |
| fairy | flying | 11 | 3 | 0.272727 | 1.00 | neutro | f |
| fairy | ghost | 62 | 28 | 0.451613 | 1.00 | neutro | f |
| fairy | grass | 203 | 59 | 0.290640 | 1.00 | neutro | f |
| fairy | ground | 82 | 24 | 0.292683 | 1.00 | neutro | f |
| fairy | ice | 60 | 24 | 0.400000 | 1.00 | neutro | f |
| fairy | normal | 247 | 60 | 0.242915 | 1.00 | neutro | f |
| fairy | poison | 77 | 23 | 0.298701 | 0.50 | desvantagem esperada | f |
| fairy | psychic | 138 | 37 | 0.268116 | 1.00 | neutro | f |
| fairy | rock | 140 | 57 | 0.407143 | 1.00 | neutro | f |
| fairy | steel | 67 | 25 | 0.373134 | 0.50 | desvantagem esperada | f |
| fairy | water | 321 | 100 | 0.311526 | 1.00 | neutro | f |
| fighting | bug | 271 | 155 | 0.571956 | 0.50 | desvantagem esperada | t |
| fighting | dark | 103 | 51 | 0.495146 | 2.00 | vantagem esperada | t |
| fighting | dragon | 123 | 40 | 0.325203 | 1.00 | neutro | f |
| fighting | electric | 179 | 56 | 0.312849 | 1.00 | neutro | f |
| fighting | fairy | 62 | 41 | 0.661290 | 0.50 | desvantagem esperada | t |
| fighting | fighting | 130 | 65 | 0.500000 | 1.00 | neutro | f |
| fighting | fire | 216 | 76 | 0.351852 | 1.00 | neutro | f |
| fighting | flying | 10 | 0 | 0.000000 | 0.50 | desvantagem esperada | f |
| fighting | ghost | 131 | 18 | 0.137405 | 0.00 | desvantagem esperada | f |
| fighting | grass | 270 | 152 | 0.562963 | 1.00 | neutro | f |
| fighting | ground | 124 | 61 | 0.491935 | 1.00 | neutro | f |
| fighting | ice | 93 | 55 | 0.591398 | 2.00 | vantagem esperada | f |
| fighting | normal | 443 | 195 | 0.440181 | 2.00 | vantagem esperada | t |
| fighting | poison | 133 | 75 | 0.563910 | 0.50 | desvantagem esperada | t |
| fighting | psychic | 236 | 87 | 0.368644 | 0.50 | desvantagem esperada | f |
| fighting | rock | 194 | 132 | 0.680412 | 2.00 | vantagem esperada | f |
| fighting | steel | 116 | 70 | 0.603448 | 2.00 | vantagem esperada | f |
| fighting | water | 472 | 214 | 0.453390 | 1.00 | neutro | f |
| fire | bug | 599 | 401 | 0.669449 | 2.00 | vantagem esperada | f |
| fire | dark | 249 | 122 | 0.489960 | 1.00 | neutro | f |
| fire | dragon | 252 | 109 | 0.432540 | 0.50 | desvantagem esperada | f |
| fire | electric | 327 | 131 | 0.400612 | 1.00 | neutro | f |
| fire | fairy | 142 | 111 | 0.781690 | 1.00 | neutro | f |
| fire | fighting | 216 | 140 | 0.648148 | 1.00 | neutro | f |
| fire | fire | 430 | 215 | 0.500000 | 0.50 | desvantagem esperada | t |
| fire | flying | 29 | 8 | 0.275862 | 1.00 | neutro | f |
| fire | ghost | 244 | 157 | 0.643443 | 1.00 | neutro | f |
| fire | grass | 547 | 385 | 0.703839 | 2.00 | vantagem esperada | f |
| fire | ground | 266 | 138 | 0.518797 | 1.00 | neutro | f |
| fire | ice | 196 | 134 | 0.683673 | 2.00 | vantagem esperada | f |
| fire | normal | 861 | 466 | 0.541231 | 1.00 | neutro | f |
| fire | poison | 225 | 151 | 0.671111 | 1.00 | neutro | f |
| fire | psychic | 448 | 215 | 0.479911 | 1.00 | neutro | f |
| fire | rock | 358 | 216 | 0.603352 | 0.50 | desvantagem esperada | t |
| fire | steel | 232 | 159 | 0.685345 | 2.00 | vantagem esperada | f |
| fire | water | 931 | 544 | 0.584318 | 0.50 | desvantagem esperada | t |
| flying | bug | 38 | 30 | 0.789474 | 2.00 | vantagem esperada | f |
| flying | dark | 23 | 17 | 0.739130 | 1.00 | neutro | f |
| flying | dragon | 22 | 18 | 0.818182 | 1.00 | neutro | f |
| flying | electric | 16 | 11 | 0.687500 | 0.50 | desvantagem esperada | t |
| flying | fairy | 11 | 8 | 0.727273 | 1.00 | neutro | f |
| flying | fighting | 10 | 10 | 1.000000 | 2.00 | vantagem esperada | f |
| flying | fire | 29 | 21 | 0.724138 | 1.00 | neutro | f |
| flying | flying | 2 | 1 | 0.500000 | 1.00 | neutro | f |
| flying | ghost | 23 | 19 | 0.826087 | 1.00 | neutro | f |
| flying | grass | 36 | 27 | 0.750000 | 2.00 | vantagem esperada | f |
| flying | ground | 19 | 17 | 0.894737 | 1.00 | neutro | f |
| flying | ice | 20 | 16 | 0.800000 | 1.00 | neutro | f |
| flying | normal | 61 | 44 | 0.721311 | 1.00 | neutro | f |
| flying | poison | 20 | 16 | 0.800000 | 1.00 | neutro | f |
| flying | psychic | 35 | 21 | 0.600000 | 1.00 | neutro | f |
| flying | rock | 24 | 16 | 0.666667 | 0.50 | desvantagem esperada | t |
| flying | steel | 21 | 18 | 0.857143 | 0.50 | desvantagem esperada | t |
| flying | water | 68 | 52 | 0.764706 | 1.00 | neutro | f |
| ghost | bug | 356 | 194 | 0.544944 | 1.00 | neutro | f |
| ghost | dark | 142 | 47 | 0.330986 | 0.50 | desvantagem esperada | f |
| ghost | dragon | 153 | 48 | 0.313725 | 1.00 | neutro | f |
| ghost | electric | 214 | 51 | 0.238318 | 1.00 | neutro | f |
| ghost | fairy | 62 | 34 | 0.548387 | 1.00 | neutro | f |
| ghost | fighting | 131 | 113 | 0.862595 | 1.00 | neutro | f |
| ghost | fire | 244 | 87 | 0.356557 | 1.00 | neutro | f |
| ghost | flying | 23 | 4 | 0.173913 | 1.00 | neutro | f |
| ghost | ghost | 166 | 83 | 0.500000 | 2.00 | vantagem esperada | t |
| ghost | grass | 351 | 173 | 0.492877 | 1.00 | neutro | f |
| ghost | ground | 159 | 74 | 0.465409 | 1.00 | neutro | f |
| ghost | ice | 123 | 62 | 0.504065 | 1.00 | neutro | f |
| ghost | normal | 484 | 245 | 0.506198 | 0.00 | desvantagem esperada | t |
| ghost | poison | 145 | 83 | 0.572414 | 1.00 | neutro | f |
| ghost | psychic | 289 | 130 | 0.449827 | 2.00 | vantagem esperada | t |
| ghost | rock | 208 | 128 | 0.615385 | 1.00 | neutro | f |
| ghost | steel | 158 | 87 | 0.550633 | 1.00 | neutro | f |
| ghost | water | 500 | 234 | 0.468000 | 1.00 | neutro | f |
| grass | bug | 764 | 368 | 0.481675 | 0.50 | desvantagem esperada | f |
| grass | dark | 332 | 92 | 0.277108 | 1.00 | neutro | f |
| grass | dragon | 313 | 97 | 0.309904 | 0.50 | desvantagem esperada | f |
| grass | electric | 459 | 153 | 0.333333 | 1.00 | neutro | f |
| grass | fairy | 203 | 144 | 0.709360 | 1.00 | neutro | f |
| grass | fighting | 270 | 118 | 0.437037 | 1.00 | neutro | f |
| grass | fire | 547 | 162 | 0.296161 | 0.50 | desvantagem esperada | f |
| grass | flying | 36 | 9 | 0.250000 | 0.50 | desvantagem esperada | f |
| grass | ghost | 351 | 178 | 0.507123 | 1.00 | neutro | f |
| grass | grass | 708 | 354 | 0.500000 | 0.50 | desvantagem esperada | t |
| grass | ground | 318 | 156 | 0.490566 | 2.00 | vantagem esperada | t |
| grass | ice | 244 | 102 | 0.418033 | 1.00 | neutro | f |
| grass | normal | 984 | 393 | 0.399390 | 1.00 | neutro | f |
| grass | poison | 301 | 131 | 0.435216 | 0.50 | desvantagem esperada | f |
| grass | psychic | 632 | 236 | 0.373418 | 1.00 | neutro | f |
| grass | rock | 482 | 274 | 0.568465 | 2.00 | vantagem esperada | f |
| grass | steel | 274 | 138 | 0.503650 | 0.50 | desvantagem esperada | t |
| grass | water | 1208 | 602 | 0.498344 | 2.00 | vantagem esperada | t |
| ground | bug | 335 | 175 | 0.522388 | 0.50 | desvantagem esperada | t |
| ground | dark | 148 | 58 | 0.391892 | 1.00 | neutro | f |
| ground | dragon | 137 | 42 | 0.306569 | 1.00 | neutro | f |
| ground | electric | 218 | 197 | 0.903670 | 2.00 | vantagem esperada | f |
| ground | fairy | 82 | 58 | 0.707317 | 1.00 | neutro | f |
| ground | fighting | 124 | 63 | 0.508065 | 1.00 | neutro | f |
| ground | fire | 266 | 128 | 0.481203 | 2.00 | vantagem esperada | t |
| ground | flying | 19 | 2 | 0.105263 | 0.00 | desvantagem esperada | f |
| ground | ghost | 159 | 85 | 0.534591 | 1.00 | neutro | f |
| ground | grass | 318 | 162 | 0.509434 | 0.50 | desvantagem esperada | t |
| ground | ground | 144 | 72 | 0.500000 | 1.00 | neutro | f |
| ground | ice | 122 | 59 | 0.483607 | 1.00 | neutro | f |
| ground | normal | 472 | 231 | 0.489407 | 1.00 | neutro | f |
| ground | poison | 149 | 92 | 0.617450 | 2.00 | vantagem esperada | f |
| ground | psychic | 274 | 138 | 0.503650 | 1.00 | neutro | f |
| ground | rock | 229 | 147 | 0.641921 | 2.00 | vantagem esperada | f |
| ground | steel | 122 | 76 | 0.622951 | 2.00 | vantagem esperada | f |
| ground | water | 571 | 303 | 0.530648 | 1.00 | neutro | f |
| ice | bug | 295 | 151 | 0.511864 | 1.00 | neutro | f |
| ice | dark | 119 | 38 | 0.319328 | 1.00 | neutro | f |
| ice | dragon | 116 | 36 | 0.310345 | 2.00 | vantagem esperada | t |
| ice | electric | 163 | 47 | 0.288344 | 1.00 | neutro | f |
| ice | fairy | 60 | 36 | 0.600000 | 1.00 | neutro | f |
| ice | fighting | 93 | 38 | 0.408602 | 1.00 | neutro | f |
| ice | fire | 196 | 62 | 0.316327 | 0.50 | desvantagem esperada | f |
| ice | flying | 20 | 4 | 0.200000 | 2.00 | vantagem esperada | t |
| ice | ghost | 123 | 61 | 0.495935 | 1.00 | neutro | f |
| ice | grass | 244 | 142 | 0.581967 | 2.00 | vantagem esperada | f |
| ice | ground | 122 | 63 | 0.516393 | 2.00 | vantagem esperada | f |
| ice | ice | 94 | 47 | 0.500000 | 0.50 | desvantagem esperada | t |
| ice | normal | 365 | 144 | 0.394521 | 1.00 | neutro | f |
| ice | poison | 99 | 49 | 0.494949 | 1.00 | neutro | f |
| ice | psychic | 224 | 84 | 0.375000 | 1.00 | neutro | f |
| ice | rock | 182 | 89 | 0.489011 | 1.00 | neutro | f |
| ice | steel | 119 | 56 | 0.470588 | 0.50 | desvantagem esperada | f |
| ice | water | 445 | 210 | 0.471910 | 0.50 | desvantagem esperada | f |
| normal | bug | 1066 | 654 | 0.613508 | 1.00 | neutro | f |
| normal | dark | 495 | 224 | 0.452525 | 1.00 | neutro | f |
| normal | dragon | 479 | 204 | 0.425887 | 1.00 | neutro | f |
| normal | electric | 676 | 258 | 0.381657 | 1.00 | neutro | f |
| normal | fairy | 247 | 187 | 0.757085 | 1.00 | neutro | f |
| normal | fighting | 443 | 248 | 0.559819 | 1.00 | neutro | f |
| normal | fire | 861 | 395 | 0.458769 | 1.00 | neutro | f |
| normal | flying | 61 | 17 | 0.278689 | 1.00 | neutro | f |
| normal | ghost | 484 | 239 | 0.493802 | 0.00 | desvantagem esperada | f |
| normal | grass | 984 | 591 | 0.600610 | 1.00 | neutro | f |
| normal | ground | 472 | 241 | 0.510593 | 1.00 | neutro | f |
| normal | ice | 365 | 221 | 0.605479 | 1.00 | neutro | f |
| normal | normal | 1416 | 708 | 0.500000 | 1.00 | neutro | f |
| normal | poison | 432 | 276 | 0.638889 | 1.00 | neutro | f |
| normal | psychic | 811 | 367 | 0.452528 | 1.00 | neutro | f |
| normal | rock | 682 | 413 | 0.605572 | 0.50 | desvantagem esperada | t |
| normal | steel | 422 | 244 | 0.578199 | 0.50 | desvantagem esperada | t |
| normal | water | 1702 | 1031 | 0.605758 | 1.00 | neutro | f |
| poison | bug | 324 | 173 | 0.533951 | 1.00 | neutro | f |
| poison | dark | 125 | 42 | 0.336000 | 1.00 | neutro | f |
| poison | dragon | 173 | 54 | 0.312139 | 1.00 | neutro | f |
| poison | electric | 201 | 56 | 0.278607 | 1.00 | neutro | f |
| poison | fairy | 77 | 54 | 0.701299 | 2.00 | vantagem esperada | f |
| poison | fighting | 133 | 58 | 0.436090 | 1.00 | neutro | f |
| poison | fire | 225 | 74 | 0.328889 | 1.00 | neutro | f |
| poison | flying | 20 | 4 | 0.200000 | 1.00 | neutro | f |
| poison | ghost | 145 | 62 | 0.427586 | 0.50 | desvantagem esperada | f |
| poison | grass | 301 | 170 | 0.564784 | 2.00 | vantagem esperada | f |
| poison | ground | 149 | 57 | 0.382550 | 0.50 | desvantagem esperada | f |
| poison | ice | 99 | 50 | 0.505051 | 1.00 | neutro | f |
| poison | normal | 432 | 156 | 0.361111 | 1.00 | neutro | f |
| poison | poison | 148 | 74 | 0.500000 | 0.50 | desvantagem esperada | t |
| poison | psychic | 270 | 105 | 0.388889 | 1.00 | neutro | f |
| poison | rock | 194 | 118 | 0.608247 | 0.50 | desvantagem esperada | t |
| poison | steel | 120 | 29 | 0.241667 | 0.00 | desvantagem esperada | f |
| poison | water | 518 | 235 | 0.453668 | 1.00 | neutro | f |
| psychic | bug | 646 | 372 | 0.575851 | 1.00 | neutro | f |
| psychic | dark | 291 | 16 | 0.054983 | 0.00 | desvantagem esperada | f |
| psychic | dragon | 276 | 128 | 0.463768 | 1.00 | neutro | f |
| psychic | electric | 422 | 183 | 0.433649 | 1.00 | neutro | f |
| psychic | fairy | 138 | 101 | 0.731884 | 1.00 | neutro | f |
| psychic | fighting | 236 | 149 | 0.631356 | 2.00 | vantagem esperada | f |
| psychic | fire | 448 | 233 | 0.520089 | 1.00 | neutro | f |
| psychic | flying | 35 | 14 | 0.400000 | 1.00 | neutro | f |
| psychic | ghost | 289 | 159 | 0.550173 | 1.00 | neutro | f |
| psychic | grass | 632 | 396 | 0.626582 | 1.00 | neutro | f |
| psychic | ground | 274 | 136 | 0.496350 | 1.00 | neutro | f |
| psychic | ice | 224 | 140 | 0.625000 | 1.00 | neutro | f |
| psychic | normal | 811 | 444 | 0.547472 | 1.00 | neutro | f |
| psychic | poison | 270 | 165 | 0.611111 | 2.00 | vantagem esperada | f |
| psychic | psychic | 518 | 259 | 0.500000 | 0.50 | desvantagem esperada | t |
| psychic | rock | 445 | 280 | 0.629213 | 1.00 | neutro | f |
| psychic | steel | 279 | 154 | 0.551971 | 0.50 | desvantagem esperada | t |
| psychic | water | 1086 | 669 | 0.616022 | 1.00 | neutro | f |
| rock | bug | 487 | 264 | 0.542094 | 2.00 | vantagem esperada | f |
| rock | dark | 246 | 65 | 0.264228 | 1.00 | neutro | f |
| rock | dragon | 260 | 66 | 0.253846 | 1.00 | neutro | f |
| rock | electric | 286 | 82 | 0.286713 | 1.00 | neutro | f |
| rock | fairy | 140 | 83 | 0.592857 | 1.00 | neutro | f |
| rock | fighting | 194 | 62 | 0.319588 | 0.50 | desvantagem esperada | f |
| rock | fire | 358 | 142 | 0.396648 | 2.00 | vantagem esperada | t |
| rock | flying | 24 | 8 | 0.333333 | 2.00 | vantagem esperada | t |
| rock | ghost | 208 | 80 | 0.384615 | 1.00 | neutro | f |
| rock | grass | 482 | 208 | 0.431535 | 1.00 | neutro | f |
| rock | ground | 229 | 82 | 0.358079 | 0.50 | desvantagem esperada | f |
| rock | ice | 182 | 93 | 0.510989 | 2.00 | vantagem esperada | f |
| rock | normal | 682 | 269 | 0.394428 | 1.00 | neutro | f |
| rock | poison | 194 | 76 | 0.391753 | 1.00 | neutro | f |
| rock | psychic | 445 | 165 | 0.370787 | 1.00 | neutro | f |
| rock | rock | 314 | 157 | 0.500000 | 1.00 | neutro | f |
| rock | steel | 179 | 86 | 0.480447 | 0.50 | desvantagem esperada | f |
| rock | water | 759 | 311 | 0.409750 | 1.00 | neutro | f |
| steel | bug | 289 | 153 | 0.529412 | 1.00 | neutro | f |
| steel | dark | 153 | 50 | 0.326797 | 1.00 | neutro | f |
| steel | dragon | 141 | 29 | 0.205674 | 1.00 | neutro | f |
| steel | electric | 211 | 61 | 0.289100 | 0.50 | desvantagem esperada | f |
| steel | fairy | 67 | 42 | 0.626866 | 2.00 | vantagem esperada | f |
| steel | fighting | 116 | 46 | 0.396552 | 1.00 | neutro | f |
| steel | fire | 232 | 73 | 0.314655 | 0.50 | desvantagem esperada | f |
| steel | flying | 21 | 3 | 0.142857 | 1.00 | neutro | f |
| steel | ghost | 158 | 71 | 0.449367 | 1.00 | neutro | f |
| steel | grass | 274 | 136 | 0.496350 | 1.00 | neutro | f |
| steel | ground | 122 | 46 | 0.377049 | 1.00 | neutro | f |
| steel | ice | 119 | 63 | 0.529412 | 2.00 | vantagem esperada | f |
| steel | normal | 422 | 178 | 0.421801 | 1.00 | neutro | f |
| steel | poison | 120 | 91 | 0.758333 | 1.00 | neutro | f |
| steel | psychic | 279 | 125 | 0.448029 | 1.00 | neutro | f |
| steel | rock | 179 | 93 | 0.519553 | 2.00 | vantagem esperada | f |
| steel | steel | 146 | 73 | 0.500000 | 0.50 | desvantagem esperada | t |
| steel | water | 497 | 190 | 0.382294 | 0.50 | desvantagem esperada | f |
| water | bug | 1204 | 649 | 0.539037 | 1.00 | neutro | f |
| water | dark | 520 | 185 | 0.355769 | 1.00 | neutro | f |
| water | dragon | 584 | 166 | 0.284247 | 0.50 | desvantagem esperada | f |
| water | electric | 713 | 215 | 0.301543 | 1.00 | neutro | f |
| water | fairy | 321 | 221 | 0.688474 | 1.00 | neutro | f |
| water | fighting | 472 | 258 | 0.546610 | 1.00 | neutro | f |
| water | fire | 931 | 387 | 0.415682 | 2.00 | vantagem esperada | t |
| water | flying | 68 | 16 | 0.235294 | 1.00 | neutro | f |
| water | ghost | 500 | 266 | 0.532000 | 1.00 | neutro | f |
| water | grass | 1208 | 606 | 0.501656 | 0.50 | desvantagem esperada | t |
| water | ground | 571 | 268 | 0.469352 | 2.00 | vantagem esperada | t |
| water | ice | 445 | 235 | 0.528090 | 1.00 | neutro | f |
| water | normal | 1702 | 671 | 0.394242 | 1.00 | neutro | f |
| water | poison | 518 | 283 | 0.546332 | 1.00 | neutro | f |
| water | psychic | 1086 | 417 | 0.383978 | 1.00 | neutro | f |
| water | rock | 759 | 448 | 0.590250 | 2.00 | vantagem esperada | f |
| water | steel | 497 | 307 | 0.617706 | 1.00 | neutro | f |
| water | water | 1942 | 971 | 0.500000 | 0.50 | desvantagem esperada | t |

</details>

### Posições que divergem da direção esperada

Foram identificadas **50 posições divergentes entre as 324 combinações** (aproximadamente **15,4%**):

| tipo_atacante | tipo_defensor | total_confrontos | taxa_vitorias | multiplicador_efetividade | expectativa |
| --- | --- | --- | --- | --- | --- |
| bug | dark | 309 | 0.362460 | 2.00 | vantagem esperada |
| bug | fairy | 190 | 0.610526 | 0.50 | desvantagem esperada |
| bug | psychic | 646 | 0.424149 | 2.00 | vantagem esperada |
| dark | dark | 148 | 0.500000 | 0.50 | desvantagem esperada |
| dark | fairy | 83 | 0.795181 | 0.50 | desvantagem esperada |
| dark | fighting | 103 | 0.504854 | 0.50 | desvantagem esperada |
| dragon | dragon | 150 | 0.500000 | 2.00 | vantagem esperada |
| dragon | steel | 141 | 0.794326 | 0.50 | desvantagem esperada |
| electric | electric | 268 | 0.500000 | 0.50 | desvantagem esperada |
| electric | flying | 16 | 0.312500 | 2.00 | vantagem esperada |
| electric | grass | 459 | 0.666667 | 0.50 | desvantagem esperada |
| fairy | dark | 83 | 0.204819 | 2.00 | vantagem esperada |
| fairy | fighting | 62 | 0.338710 | 2.00 | vantagem esperada |
| fighting | bug | 271 | 0.571956 | 0.50 | desvantagem esperada |
| fighting | dark | 103 | 0.495146 | 2.00 | vantagem esperada |
| fighting | fairy | 62 | 0.661290 | 0.50 | desvantagem esperada |
| fighting | normal | 443 | 0.440181 | 2.00 | vantagem esperada |
| fighting | poison | 133 | 0.563910 | 0.50 | desvantagem esperada |
| fire | fire | 430 | 0.500000 | 0.50 | desvantagem esperada |
| fire | rock | 358 | 0.603352 | 0.50 | desvantagem esperada |
| fire | water | 931 | 0.584318 | 0.50 | desvantagem esperada |
| flying | electric | 16 | 0.687500 | 0.50 | desvantagem esperada |
| flying | rock | 24 | 0.666667 | 0.50 | desvantagem esperada |
| flying | steel | 21 | 0.857143 | 0.50 | desvantagem esperada |
| ghost | ghost | 166 | 0.500000 | 2.00 | vantagem esperada |
| ghost | normal | 484 | 0.506198 | 0.00 | desvantagem esperada |
| ghost | psychic | 289 | 0.449827 | 2.00 | vantagem esperada |
| grass | grass | 708 | 0.500000 | 0.50 | desvantagem esperada |
| grass | ground | 318 | 0.490566 | 2.00 | vantagem esperada |
| grass | steel | 274 | 0.503650 | 0.50 | desvantagem esperada |
| grass | water | 1208 | 0.498344 | 2.00 | vantagem esperada |
| ground | bug | 335 | 0.522388 | 0.50 | desvantagem esperada |
| ground | fire | 266 | 0.481203 | 2.00 | vantagem esperada |
| ground | grass | 318 | 0.509434 | 0.50 | desvantagem esperada |
| ice | dragon | 116 | 0.310345 | 2.00 | vantagem esperada |
| ice | flying | 20 | 0.200000 | 2.00 | vantagem esperada |
| ice | ice | 94 | 0.500000 | 0.50 | desvantagem esperada |
| normal | rock | 682 | 0.605572 | 0.50 | desvantagem esperada |
| normal | steel | 422 | 0.578199 | 0.50 | desvantagem esperada |
| poison | poison | 148 | 0.500000 | 0.50 | desvantagem esperada |
| poison | rock | 194 | 0.608247 | 0.50 | desvantagem esperada |
| psychic | psychic | 518 | 0.500000 | 0.50 | desvantagem esperada |
| psychic | steel | 279 | 0.551971 | 0.50 | desvantagem esperada |
| rock | fire | 358 | 0.396648 | 2.00 | vantagem esperada |
| rock | flying | 24 | 0.333333 | 2.00 | vantagem esperada |
| steel | steel | 146 | 0.500000 | 0.50 | desvantagem esperada |
| water | fire | 931 | 0.415682 | 2.00 | vantagem esperada |
| water | grass | 1208 | 0.501656 | 0.50 | desvantagem esperada |
| water | ground | 571 | 0.469352 | 2.00 | vantagem esperada |
| water | water | 1942 | 0.500000 | 0.50 | desvantagem esperada |

### Interpretação

A matriz é orientada pelo participante e pelo oponente; cada combate alimenta as duas orientações do par. Em pares do mesmo tipo, a taxa tende naturalmente a 0,5, mesmo quando a tabela de efetividade marca resistência ou vantagem, o que gera algumas divergências pelo critério adotado.

As 50 divergências mostram que a efetividade do tipo primário não explica isoladamente os resultados. Algumas envolvem amostras pequenas, como `electric` × `flying` com 16 confrontos, mas outras ocorrem em grupos grandes. Exemplos importantes são `fire` × `water` (**931 confrontos**, taxa **0,584318** apesar de multiplicador 0,5), `water` × `fire` (**931**, taxa **0,415682** apesar de multiplicador 2), `grass` × `water` (**1.208**, taxa **0,498344** apesar de multiplicador 2) e `water` × `grass` (**1.208**, taxa **0,501656** apesar de multiplicador 0,5). Isso reforça que atributos individuais, composição de segundo tipo e regras do simulador interferem no resultado além da relação primária de tipos.

---

## 8. Análise proposta — vantagem de atacar primeiro

### Pergunta de negócio

**Atacar primeiro está associado a uma taxa de vitórias maior nas batalhas simuladas?**

A análise usa uma capacidade não exigida nas sete anteriores: a posição original `First_pokemon`/`Second_pokemon` do `combats.csv`, materializada como `atacou_primeiro` na fato.

### Resultado da execução

| ordem_ataque | total_confrontos | vitorias | taxa_vitorias |
| --- | --- | --- | --- |
| ATACOU_PRIMEIRO | 50000 | 23601 | 0.472020 |
| ATACOU_SEGUNDO | 50000 | 26399 | 0.527980 |

### Interpretação

Os dois grupos possuem exatamente **50.000 participações**, como esperado. Quem atacou primeiro venceu **23.601** vezes, com taxa **0,472020**; quem atacou em segundo venceu **26.399** vezes, com taxa **0,527980**. A diferença é de **5,596 pontos percentuais** a favor do segundo participante.

Portanto, neste conjunto de batalhas simuladas, **atacar primeiro não está associado a uma taxa de vitória maior**; a associação observada aponta na direção oposta. Esse resultado não deve ser interpretado como causal por si só, pois a ordem pode estar relacionada a outras características dos Pokémon, e o desfecho é produzido pelo programa de simulação.

---

## Conclusão

A execução completa do pipeline preservou os **800 Pokémon** do cadastro e os **50.000 combates**, produzindo as camadas Silver e Gold necessárias às oito análises.

Os resultados mostram três padrões principais. Primeiro, **velocidade é a associação mais forte observada**: participantes mais rápidos venceram mais de 90% dos confrontos nas três faixas positivas, enquanto empates de velocidade resultaram em 50%. Segundo, a **efetividade de tipos também aparece nos dados**, com winrate crescendo gradualmente de multiplicadores desfavoráveis para favoráveis, embora 50 das 324 posições da matriz contradigam a direção esperada quando se considera apenas o tipo primário. Terceiro, a análise proposta mostrou que o participante registrado como primeiro atacante venceu **47,202%** das vezes, abaixo dos **52,798%** do segundo.

Esses resultados devem ser interpretados como propriedades do conjunto de batalhas **simuladas**, e não como evidência experimental sobre batalhas reais. A presença de divergências entre efetividade teórica e taxa observada é compatível com um sistema em que múltiplos atributos — especialmente velocidade, mas também ataque, defesa, combinações de tipos e regras internas do simulador — influenciam conjuntamente o resultado. O modelo dimensional permite observar esses padrões sem retornar às fontes brutas e mantém as métricas necessárias materializadas para novas perguntas analíticas.
