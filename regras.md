> O objetivo é modelar um problema como um CSP e aplicar técnicas estudadas para resolver.

# O problema

Modelar o problema de preencher um grid de palavras cruzadas com um conjunto pré estabelecido de palavras como um Problema de Satisfação de Restrições.
Após isso, você pode empregar as técnicas estudadas para resolver o problema proposto.

Deve empregar heurísticas para melhorar o desempenho do algoritmo de CSP.
É obrigatório escrever no mínimo duas heurísticas. São exemplos de uso:
1. Definir em que ordem os espaços do grid serão preenchidos,
2. Em que ordem as palavras serão escolhidas
3. Entre outros

Não é necessário implementar interface gráfica.

## Formatos de Entrada e Saída
### Entrada

Arquivo texto com o formato forneceido pelo site Words Up (https://wordsup.co.uk)
Além dos grid será fornecida uma lista de palavras (lista_palavras.txt)

Restrição: proibida alterações nos arquivos de entrada da aplicação (grid e palavras)

### Saída:

1. Arquivo de texto contendo o grid fornecido como entrada preenchido com as palavras presentes no arquivo (substituindo pontos de interrogação pelas palavras escolhidas).
2. Deve salvar um log em arquivo que permita observar a execução do algoritmo (o programa deve cronometrar o tempo gasto para preencher todo o grid e exibir a informação no log e em tela ao final do processamento)

### Observações

Pode usar bibliotecas que implementem algoritmos de CSP, mas preciso de um estudo da documentação e implementação destas para saber descrever os algoritmos usados