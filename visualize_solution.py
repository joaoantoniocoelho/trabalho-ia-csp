# =============================================================================
# ARQUIVO GERADO INTEIRAMENTE POR IA
# Modelo: Claude 3.7 Sonnet (Anthropic) 
# =============================================================================

import os
import sys
import argparse

def visualize_grid(grid_file, solution_file=None):
    """
    Visualize a crossword grid or solution.
    If solution_file is provided, it compares the original grid with the solution.
    """
    # Read the original grid
    with open(grid_file, 'r') as f:
        original_grid = [line.strip() for line in f]
    
    # Read the solution if provided
    solution_grid = None
    if solution_file and os.path.exists(solution_file):
        with open(solution_file, 'r') as f:
            solution_grid = [line.strip() for line in f]
    
    grid_to_display = solution_grid if solution_grid else original_grid
    
    # Print the grid with borders
    width = len(grid_to_display[0])
    print("+" + "-" * (width * 2 + 1) + "+")
    
    for i, row in enumerate(grid_to_display):
        line = "| "
        for j, cell in enumerate(row):
            if cell == '.':
                # Black cell
                line += "█ "
            elif cell == '?':
                # Empty cell in original grid
                line += "_ "
            else:
                # Either a filled cell in solution or a pre-filled cell in original
                if solution_grid and original_grid[i][j] == '?':
                    # Highlight filled cells in solution that were empty in original
                    line += f"\033[1m{cell}\033[0m "
                else:
                    line += f"{cell} "
        line += "|"
        print(line)
    
    print("+" + "-" * (width * 2 + 1) + "+")
    
    # Print comparison stats if solution is provided
    if solution_grid:
        filled_count = 0
        for i in range(len(original_grid)):
            for j in range(min(len(original_grid[i]), len(solution_grid[i]))):
                if original_grid[i][j] == '?' and solution_grid[i][j] != '?':
                    filled_count += 1
        
        print(f"\nComparison Statistics:")
        print(f"- Filled cells: {filled_count}")
        
        # Check if any cells remained unfilled
        unfilled = 0
        for i in range(len(solution_grid)):
            for j in range(len(solution_grid[i])):
                if solution_grid[i][j] == '?':
                    unfilled += 1
        
        if unfilled > 0:
            print(f"- Unfilled cells: {unfilled}")
            print("  Note: Some cells remain unfilled in the solution.")
        else:
            print("- All cells have been filled in the solution.")

def main():
    parser = argparse.ArgumentParser(description='Visualize crossword grid and solution')
    parser.add_argument('grid', help='Path to the original grid file')
    parser.add_argument('-s', '--solution', help='Path to the solution file (optional)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.grid):
        print(f"Error: Grid file '{args.grid}' not found.")
        return 1
    
    # If no solution file provided, try to find it based on grid name
    solution_file = args.solution
    if not solution_file:
        grid_name = os.path.basename(args.grid).split('.')[0]
        potential_solution = f"{grid_name}_solution.txt"
        if os.path.exists(potential_solution):
            solution_file = potential_solution
            print(f"Found solution file: {solution_file}")
    
    if solution_file and not os.path.exists(solution_file):
        print(f"Warning: Solution file '{solution_file}' not found. Displaying original grid only.")
        solution_file = None
    
    visualize_grid(args.grid, solution_file)
    return 0

if __name__ == "__main__":
    sys.exit(main()) 