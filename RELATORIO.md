# Relatório — EP01: ETL e Arquitetura Medalhão

**Integrantes:** Isaias Maia de Oliveira e Daniel Santos Baptista.

> Este relatório deve registrar **a saída real** das consultas após a execução do pipeline. Os campos abaixo foram estruturados para evitar a fabricação de resultados. Execute `extrair.py`, `carregar.py`, `publicar.py` e `sql/consultas.sql`; em seguida substitua cada bloco `RESULTADO DA EXECUÇÃO` pela saída obtida no PostgreSQL antes da entrega final.

## 1. Quantidade de Pokémon por tipo primário e geração

### Pergunta

Como os Pokémon do cadastro se distribuem entre os 18 tipos primários e as gerações I a VI?

### Resultado da execução

`RESULTADO DA EXECUÇÃO — consulta 1 de sql/consultas.sql`

### Interpretação

Verificar se a matriz apresenta distribuição coerente entre tipos e gerações e se a soma total corresponde aos 800 registros conciliados/preservados. Divergências de total indicam problema de conciliação ou carga; células vazias/zero podem representar inexistência real daquela combinação.

---

## 2. Médias dos atributos de status por tipo primário

### Pergunta

Quais são as médias de HP, ataque, defesa, ataque especial, defesa especial e velocidade por tipo? Qual tipo possui maior velocidade média, qual apresenta maior resistência média e existe um tipo que lidere todos os atributos simultaneamente?

### Resultado da execução

`RESULTADO DA EXECUÇÃO — consultas 2A, 2B, 2C e 2D`

### Interpretação

A resistência foi definida no projeto como a média de HP, Defesa e Defesa Especial. Comparar as médias por tipo e registrar explicitamente o líder de velocidade, o líder de resistência e se a consulta 2D retorna algum tipo. Caso 2D não retorne linha, a conclusão é que nenhum tipo domina simultaneamente os seis atributos médios.

---

## 3. Taxa de vitórias por Pokémon

### Pergunta

Quais Pokémon apresentam as dez maiores e as dez menores taxas de vitória entre aqueles com pelo menos 50 combates?

### Resultado da execução

`RESULTADO DA EXECUÇÃO — duas consultas da análise 3`

### Interpretação

O corte de 50 combates reduz a influência de amostras muito pequenas. Interpretar winrate sempre junto de `total_combates`; dois Pokémon com taxas semelhantes podem ter níveis de evidência diferentes se o número de batalhas for muito distinto.

---

## 4. Taxa de vitórias por tipo primário

### Pergunta

Como a taxa de vitórias varia entre os tipos primários? Há algum tipo que se destaque nos dados simulados?

### Resultado da execução

`RESULTADO DA EXECUÇÃO — análise 4`

### Interpretação

Comparar as taxas em conjunto com o total de confrontos. Um tipo com taxa superior não deve ser interpretado automaticamente como vantagem causal do tipo: os resultados também refletem distribuição de Pokémon, atributos e o programa de simulação que gerou as batalhas.

---

## 5. Diferença de velocidade e vitória

### Pergunta

Como a probabilidade de vitória muda quando o Pokémon é mais lento, tem velocidade semelhante ou é mais rápido que o oponente?

### Resultado da execução

`RESULTADO DA EXECUÇÃO — análise 5`

### Interpretação

As faixas são simétricas em torno de zero. Verificar se a taxa de vitória cresce à medida que `velocidade - velocidade_oponente` se torna positiva e maior. A faixa `0` permite observar confrontos entre Pokémon de mesma velocidade sem misturá-los com diferenças pequenas.

---

## 6. Vantagem de tipo e vitória

### Pergunta

A taxa de vitórias acompanha o multiplicador de efetividade de tipos?

### Resultado da execução

`RESULTADO DA EXECUÇÃO — análise 6`

### Interpretação

O multiplicador considera o tipo primário do participante contra os dois tipos do defensor, podendo assumir 0, 0,25, 0,5, 1, 2 ou 4. Verificar se multiplicadores acima de 1 apresentam, em geral, winrate maior que os neutros e desfavoráveis. Se o efeito não aparecer, isso continua sendo resultado válido: as batalhas são simuladas e o gerador pode não reproduzir integralmente a mecânica de tipos.

---

## 7. Matriz de confronto entre tipos

### Pergunta

Qual é a taxa de vitória do tipo A contra o tipo B nas 324 combinações de tipos primários, e onde a direção observada contradiz a efetividade esperada?

### Resultado da execução

`RESULTADO DA EXECUÇÃO — análises 7A e 7B`

### Interpretação

A matriz é orientada pelo participante e pelo oponente, não por `First_pokemon`: cada combate contribui como vitória para a célula do vencedor contra o perdedor e como derrota para a célula inversa. A coluna `diverge_da_efetividade` marca casos em que uma vantagem (`multiplicador > 1`) não alcança winrate acima de 50%, ou uma desvantagem (`multiplicador < 1`) não fica abaixo de 50%. Pares sem confrontos têm taxa e divergência nulas.

---

## 8. Análise proposta — vantagem de atacar primeiro

### Pergunta de negócio

**Atacar primeiro está associado a uma taxa de vitórias maior nas batalhas simuladas?**

A análise usa uma capacidade não exigida nas sete anteriores: a posição original `First_pokemon`/`Second_pokemon` do `combats.csv`, materializada como `atacou_primeiro` na fato.

### Resultado da execução

`RESULTADO DA EXECUÇÃO — análise 8`

### Interpretação

Comparar as duas linhas `ATACOU_PRIMEIRO` e `ATACOU_SEGUNDO`. Como cada batalha contém exatamente um participante em cada posição, os denominadores devem ser iguais (50.000 em cada grupo). Uma diferença de winrate descreve associação entre ordem e resultado no simulador; isoladamente, não prova causalidade, pois velocidade e atributos dos Pokémon também influenciam os confrontos.

---

## Conclusão

Após inserir as saídas reais, sintetizar aqui os principais padrões encontrados nas oito análises, destacando o que os dados simulados suportam e as limitações de interpretação. Em particular, diferenciar associações observadas de explicações causais e lembrar que os 50.000 resultados foram produzidos por um programa de simulação, não por batalhas reais observadas.
