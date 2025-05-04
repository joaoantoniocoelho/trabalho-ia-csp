#!/usr/bin/env python3
import os
import sys
import subprocess
import time
import argparse

def run_command(command, description):
    """Run a command and print its output."""
    print(f"\n{'='*60}")
    print(f"ETAPA: {description}")
    print(f"Executando: {' '.join(command)}")
    print(f"{'='*60}\n")
    
    start_time = time.time()
    result = subprocess.run(command, 
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE,
                           text=True)
    
    print(result.stdout)
    
    if result.stderr:
        print("Erros encontrados:")
        print(result.stderr)
    
    elapsed = time.time() - start_time
    print(f"Tempo total: {elapsed:.2f} segundos")
    return result.returncode == 0

def main():
    parser = argparse.ArgumentParser(description='Executa o fluxo completo de solução para um grid de palavras cruzadas')
    parser.add_argument('grid', help='Arquivo do grid a ser processado')
    parser.add_argument('--wordlist', default='lista_palavras.txt', 
                      help='Arquivo com a lista de palavras (default: lista_palavras.txt)')
    
    args = parser.parse_args()
    
    # Verifica se o grid existe
    if not os.path.exists(args.grid):
        print(f"Erro: Arquivo de grid '{args.grid}' não encontrado.")
        return 1
    
    # Verifica se a lista de palavras existe
    if not os.path.exists(args.wordlist):
        print(f"Erro: Arquivo de palavras '{args.wordlist}' não encontrado.")
        return 1
    
    print(f"\n{'#'*80}")
    print(f"# INICIANDO FLUXO COMPLETO PARA O GRID: {args.grid}")
    print(f"{'#'*80}\n")
    
    start_total = time.time()
    
    # Etapa 1: Resolver o grid com CSP
    solve_success = run_command(
        ['python3', 'crossword_csp.py', args.grid, '--wordlist', args.wordlist],
        "Resolvendo o grid com o solver CSP"
    )
    
    if not solve_success:
        print("Erro ao resolver o grid. Abortando.")
        return 1
    
    # Etapa 2: Visualizar a solução
    visualize_success = run_command(
        ['python3', 'visualize_solution.py', args.grid],
        "Visualizando a solução"
    )
    
    if not visualize_success:
        print("Erro ao visualizar a solução.")
        return 1
    
    # Calcular tempo total
    total_time = time.time() - start_total
    
    print(f"\n{'#'*80}")
    print(f"# FLUXO COMPLETO FINALIZADO COM SUCESSO")
    print(f"# Grid: {args.grid}")
    print(f"# Tempo total: {total_time:.2f} segundos")
    
    # Encontrar os arquivos de saída
    grid_name = os.path.basename(args.grid).split('.')[0]
    solution_file = f"{grid_name}_solution.txt"
    log_file = f"{grid_name}_solution_log.txt"
    
    print(f"# Arquivo de solução: {solution_file}")
    print(f"# Arquivo de log: {log_file}")
    print(f"{'#'*80}\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 