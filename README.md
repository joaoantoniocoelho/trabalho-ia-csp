# Crossword Puzzle CSP Solver

Este projeto implementa um solver para preencher grids de palavras cruzadas usando a modelagem como um Problema de Satisfação de Restrições (CSP), conforme solicitado no trabalho.

## Descrição da Solução

O problema foi modelado como um CSP onde:
- **Variáveis**: Cada slot (horizontal ou vertical) no grid
- **Domínios**: Palavras disponíveis na lista de palavras que têm o comprimento correto
- **Restrições**: As palavras atribuídas a slots que se cruzam devem ter a mesma letra na posição de cruzamento

### Heurísticas Implementadas

Conforme exigido nos requisitos do trabalho, implementamos múltiplas heurísticas para melhorar o desempenho do algoritmo:

1. **Minimum Remaining Values (MRV)**: Escolhe o slot com o menor número de valores válidos restantes. Esta heurística ajuda a identificar primeiro as variáveis mais restritas, reduzindo o fator de ramificação.

2. **Degree Heuristic**: Escolhe o slot que tem o maior número de restrições com outras variáveis não atribuídas. Isso ajuda a resolver primeiro os slots que podem ter maior impacto nas escolhas futuras.

3. **Least Constraining Value (LCV)**: Ordena os valores do domínio pela quantidade de conflitos que causam com outras variáveis. Isso ajuda a escolher valores que mantêm maior flexibilidade para atribuições futuras.

4. **Heurística Combinada**: Utiliza o MRV como primeira escolha e o Degree como desempate quando vários slots têm o mesmo tamanho de domínio.

### Otimizações Implementadas

1. **Organização de palavras por comprimento**: Armazena as palavras em dicionários indexados pelo comprimento, acelerando a inicialização dos domínios.

2. **Forward Checking**: Reduz os domínios de variáveis não atribuídas após cada atribuição, detectando inconsistências precocemente.

3. **Detecção precoce de inconsistências**: Identifica e abandona rapidamente caminhos de busca inconsistentes.

4. **Amostragem para domínios grandes**: Para domínios com muitas palavras, usa amostragem para aplicar o LCV de forma mais eficiente.

## Como Executar

### Fluxo Completo Automatizado

A maneira mais simples de executar todo o processo para um grid específico é usar o script `solve_grid.py`:

```bash
python3 solve_grid.py grid-11x11-20W-83L-38B.txt
```

Este script executará automaticamente todas as etapas:
1. Solução do grid com o CSP solver
2. Visualização da solução

Opções adicionais:
```bash
python3 solve_grid.py grid-11x11-20W-83L-38B.txt --wordlist lista_palavras.txt
```

- `--wordlist`: Arquivo com a lista de palavras (padrão: lista_palavras.txt)

### Executando Manualmente Passo a Passo

#### Executando o Solver

```bash
python3 crossword_csp.py grid-11x11-20W-83L-38B.txt
```

#### Visualização da Solução

```bash
python3 visualize_solution.py grid-11x11-20W-83L-38B.txt
```

## Arquivos de Saída

Conforme requisitado no trabalho, o programa gera dois arquivos para cada grid processado:

1. **{grid_name}_solution.txt**: Contém o grid preenchido com as palavras, substituindo os pontos de interrogação pelas palavras escolhidas.

2. **{grid_name}_solution_log.txt**: Contém o log de execução com informações sobre o processo de solução, incluindo o tempo total de processamento.

## Estrutura do Código

- **crossword_csp.py**: Implementação principal do solver CSP
  - Modelagem do problema como CSP
  - Implementação das heurísticas
  - Algoritmo de backtracking com forward checking
  - Geração dos arquivos de saída conforme requisitos

- **visualize_solution.py**: Script para visualizar grids e soluções
  - Ferramenta auxiliar para exibir na tela o resultado da solução

- **solve_grid.py**: Script para executar o fluxo completo para um grid específico
  - Automatiza a execução do solver e da visualização

## Requisitos do Projeto e Como São Cumpridos

1. **Modelagem do problema como CSP**: 
   - Implementado na classe `CrosswordCSP` que define as variáveis (slots), domínios (palavras) e restrições (letras coincidentes nas interseções).

2. **Implementação de heurísticas (mínimo duas)**:
   - Implementamos quatro heurísticas: MRV, Degree, LCV e Combinada.
   - O código inclui métodos específicos para cada heurística: `mrv_heuristic()`, `degree_heuristic()`, `combined_heuristic()` e `lcv_heuristic()`.

3. **Entrada no formato do site Words Up**:
   - O programa lê os grids diretamente nos formatos fornecidos.
   - Não há modificação nos arquivos de entrada (grid e lista de palavras).

4. **Saída conforme especificações**:
   - Geração de arquivo com o grid preenchido: `{grid_name}_solution.txt`.
   - Geração de log com tempo de execução: `{grid_name}_solution_log.txt`.

5. **Cronometragem do tempo de execução**:
   - Implementada na função `solve()` usando `time.time()`.
   - O tempo é registrado no log e exibido na tela ao final do processamento. 