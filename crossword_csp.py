import time
import os
import random
import argparse
from collections import defaultdict

class CrosswordCSP:
    def __init__(self, grid_file, words_file):
        """Initialize the CSP with grid and words."""
        self.grid_file = grid_file
        self.words_file = words_file
        self.grid = []
        self.words_by_length = defaultdict(list)  # Dictionary of words by length for faster lookup
        self.slots = []  # List of horizontal and vertical slots for words
        self.assignment = {}  # Maps slots to assigned words
        self.domain = {}  # Maps slots to possible words
        self.solution_log = []  # Log for recording solution steps
        self.start_time = None
        self.elapsed_time = 0
        
    def load_grid(self):
        """Load the grid from the input file."""
        with open(self.grid_file, 'r') as f:
            for line in f:
                self.grid.append(line.strip())
        
    def load_words(self):
        """Load the words from the input file, organizes them by length."""
        word_count = 0
        with open(self.words_file, 'r') as f:
            for line in f:
                word = line.strip().upper()
                if word:  # Skip empty lines
                    self.words_by_length[len(word)].append(word)
                    word_count += 1
                    # Print progress for very large files
                    if word_count % 100000 == 0:
                        print(f"Loaded {word_count} words...")
        
        self.solution_log.append(f"Loaded {word_count} words grouped by length")
        for length, words in sorted(self.words_by_length.items()):
            self.solution_log.append(f"  Length {length}: {len(words)} words")
    
    def identify_slots(self):
        """Identify horizontal and vertical slots in the grid."""
        height = len(self.grid)
        width = len(self.grid[0])
        
        # Find horizontal slots
        for i in range(height):
            j = 0
            while j < width:
                if j < len(self.grid[i]) and self.grid[i][j] == '?':
                    start = j
                    while j < width and j < len(self.grid[i]) and self.grid[i][j] == '?':
                        j += 1
                    end = j
                    if end - start > 1:  # Consider slots with at least 2 cells
                        self.slots.append(('H', i, start, end - start))
                else:
                    j += 1
        
        # Find vertical slots
        for j in range(width):
            i = 0
            while i < height:
                if i < height and j < len(self.grid[i]) and self.grid[i][j] == '?':
                    start = i
                    while i < height and j < len(self.grid[i]) and self.grid[i][j] == '?':
                        i += 1
                    end = i
                    if end - start > 1:  # Consider slots with at least 2 cells
                        self.slots.append(('V', start, j, end - start))
                else:
                    i += 1
    
    def initialize_domains(self):
        """Initialize domains for each slot."""
        for slot in self.slots:
            direction, row, col, length = slot
            # Use pre-filtered words matching the slot length
            if length in self.words_by_length:
                self.domain[slot] = list(self.words_by_length[length])
            else:
                self.domain[slot] = []
                self.solution_log.append(f"Warning: No words of length {length} in the dictionary")
    
    def forward_check(self, slot, word, assignment, domain, overlaps):
        """Apply forward checking to reduce domains of unassigned variables."""
        reduced_domains = {}
        
        for other_slot in overlaps[slot]:
            if other_slot not in assignment:
                pos1, pos2 = overlaps[slot][other_slot]
                
                # Check constraint and reduce domain
                if pos1 < len(word):
                    char_at_overlap = word[pos1]
                    new_domain = [w for w in domain[other_slot] if pos2 < len(w) and w[pos2] == char_at_overlap]
                    
                    if not new_domain:  # Domain wipeout
                        return None
                    
                    if len(new_domain) < len(domain[other_slot]):
                        reduced_domains[other_slot] = new_domain
        
        return reduced_domains
    
    def get_overlaps(self):
        """Find overlapping positions between slots."""
        overlaps = {}
        for slot1 in self.slots:
            overlaps[slot1] = {}
            dir1, row1, col1, len1 = slot1
            
            for slot2 in self.slots:
                if slot1 != slot2:
                    dir2, row2, col2, len2 = slot2
                    
                    if dir1 != dir2:  # Different directions can overlap
                        if dir1 == 'H':  # slot1 is horizontal, slot2 is vertical
                            if col1 <= col2 < col1 + len1 and row2 <= row1 < row2 + len2:
                                # Calculate relative positions in each word
                                pos1 = col2 - col1
                                pos2 = row1 - row2
                                overlaps[slot1][slot2] = (pos1, pos2)
                        else:  # slot1 is vertical, slot2 is horizontal
                            if col2 <= col1 < col2 + len2 and row1 <= row2 < row1 + len1:
                                # Calculate relative positions in each word
                                pos1 = row2 - row1
                                pos2 = col1 - col2
                                overlaps[slot1][slot2] = (pos1, pos2)
        
        return overlaps
    
    def check_consistent(self, slot, word, assignment, overlaps):
        """Check if assigning word to slot is consistent with current assignment."""
        for other_slot in overlaps[slot]:
            if other_slot in assignment:
                pos1, pos2 = overlaps[slot][other_slot]
                if pos1 < len(word) and pos2 < len(assignment[other_slot]):
                    if word[pos1] != assignment[other_slot][pos2]:
                        return False
        return True
    
    def mrv_heuristic(self, unassigned_slots, domain):
        """Minimum Remaining Values heuristic: choose slot with fewest legal values."""
        return min(unassigned_slots, key=lambda slot: len(domain[slot]))
    
    def degree_heuristic(self, unassigned_slots, overlaps):
        """Degree heuristic: choose slot with most constraints on other variables."""
        return max(unassigned_slots, key=lambda slot: sum(1 for other_slot in overlaps[slot] if other_slot in unassigned_slots))
    
    def combined_heuristic(self, unassigned_slots, domain, overlaps):
        """Combined MRV and degree heuristic."""
        # Calculate MRV score (lower is better)
        mrv_scores = {slot: len(domain[slot]) for slot in unassigned_slots}
        min_domain_size = min(mrv_scores.values())
        
        # Filter slots with minimum domain size
        min_domain_slots = [slot for slot in unassigned_slots if mrv_scores[slot] == min_domain_size]
        
        if len(min_domain_slots) == 1:
            return min_domain_slots[0]
        
        # Use degree heuristic as tie-breaker
        return self.degree_heuristic(min_domain_slots, overlaps)
    
    def lcv_heuristic(self, slot, domain, assignment, overlaps):
        """Least Constraining Value heuristic: sort domain values by how much they constrain others."""
        def count_conflicts(word):
            count = 0
            for other_slot in overlaps[slot]:
                if other_slot not in assignment:
                    pos1, pos2 = overlaps[slot][other_slot]
                    if pos1 < len(word):
                        char_at_overlap = word[pos1]
                        for other_word in domain[other_slot]:
                            if pos2 < len(other_word) and other_word[pos2] != char_at_overlap:
                                count += 1
            return count
        
        # For large domains, sample a subset to speed up sorting
        if len(domain[slot]) > 500:
            sample_size = min(200, len(domain[slot]))
            sampled_domain = random.sample(domain[slot], sample_size)
            return sorted(sampled_domain, key=count_conflicts) + [w for w in domain[slot] if w not in sampled_domain]
        else:
            return sorted(domain[slot], key=count_conflicts)
    
    def backtrack(self, assignment, domain, overlaps):
        """Backtracking search with heuristics."""
        if len(assignment) % 5 == 0 and len(assignment) > 0:
            current_time = time.time()
            elapsed = current_time - self.start_time
            self.solution_log.append(f"Current assignment size: {len(assignment)}/{len(self.slots)} in {elapsed:.2f} seconds")
        
        if len(assignment) == len(self.slots):
            return assignment
        
        unassigned_slots = [slot for slot in self.slots if slot not in assignment]
        
        # Use combined heuristic to select the next slot
        slot = self.combined_heuristic(unassigned_slots, domain, overlaps)
            
        # Use LCV heuristic to order domain values
        for word in self.lcv_heuristic(slot, domain, assignment, overlaps):
            if self.check_consistent(slot, word, assignment, overlaps):
                assignment[slot] = word
                
                # Apply forward checking to reduce domains
                reduced_domains = self.forward_check(slot, word, assignment, domain, overlaps)
                if reduced_domains is None:  # Domain wipeout - inconsistent assignment
                    del assignment[slot]
                    continue
                
                # Create new domain with reduced values
                new_domain = domain.copy()
                for s, d in reduced_domains.items():
                    new_domain[s] = d
                
                # Recursively continue
                result = self.backtrack(assignment, new_domain, overlaps)
                if result:
                    return result
                
                # If we get here, this assignment didn't work
                del assignment[slot]
                
        return None
    
    def solve(self):
        """Solve the crossword puzzle."""
        self.start_time = time.time()
        self.solution_log.append(f"Starting solution at {time.ctime()}")
        self.solution_log.append(f"Grid size: {len(self.grid)}x{len(self.grid[0])}")
        self.solution_log.append(f"Number of slots: {len(self.slots)}")
        
        # Analyze the constraints
        overlaps = self.get_overlaps()
        total_constraints = sum(len(o) for o in overlaps.values())
        self.solution_log.append(f"Total constraints: {total_constraints}")
        
        self.solution_log.append("Starting backtracking search with MRV, Degree, and LCV heuristics...")
        solution = self.backtrack({}, self.domain, overlaps)
        
        end_time = time.time()
        self.elapsed_time = end_time - self.start_time
        
        if solution:
            self.solution_log.append(f"Solution found in {self.elapsed_time:.2f} seconds!")
            self.assignment = solution
            return True
        else:
            self.solution_log.append(f"No solution found after {self.elapsed_time:.2f} seconds.")
            return False
    
    def get_filled_grid(self):
        """Return the grid filled with assigned words."""
        filled_grid = [list(row) for row in self.grid]
        
        for slot, word in self.assignment.items():
            direction, row, col, length = slot
            
            if direction == 'H':  # Horizontal
                for i in range(length):
                    if col + i < len(filled_grid[row]):
                        filled_grid[row][col + i] = word[i]
            else:  # Vertical
                for i in range(length):
                    if row + i < len(filled_grid) and col < len(filled_grid[row + i]):
                        filled_grid[row + i][col] = word[i]
        
        # Convert back to strings
        return [''.join(row) for row in filled_grid]
    
    def write_solution(self, output_file):
        """Write the solution grid to a file."""
        with open(output_file, 'w') as f:
            for row in self.get_filled_grid():
                f.write(row + '\n')
    
    def write_log(self, log_file):
        """Write the solution log to a file."""
        with open(log_file, 'w') as f:
            for line in self.solution_log:
                f.write(line + '\n')
            
            f.write(f"\nTotal time: {self.elapsed_time:.2f} seconds\n")
            
            # Add details about the assignment
            f.write("\nWord assignments:\n")
            for slot, word in self.assignment.items():
                direction, row, col, length = slot
                dir_name = "Horizontal" if direction == 'H' else "Vertical"
                f.write(f"{dir_name} at ({row},{col}), length {length}: {word}\n")
    
    def run(self):
        """Run the full solution process."""
        grid_name = os.path.basename(self.grid_file).split('.')[0]
        
        print(f"Loading grid from {self.grid_file}...")
        self.load_grid()
        
        print(f"Loading words from {self.words_file}...")
        self.load_words()
        
        print("Identifying word slots in the grid...")
        self.identify_slots()
        print(f"Found {len(self.slots)} slots")
        
        print("Initializing domains...")
        self.initialize_domains()
        
        print("Starting CSP solver...")
        solved = self.solve()
        
        if solved:
            # Create directories if they don't exist
            os.makedirs('solutions', exist_ok=True)
            os.makedirs('logs', exist_ok=True)
            
            output_file = f"solutions/{grid_name}_solution.txt"
            log_file = f"logs/{grid_name}_solution_log.txt"
            
            print("Writing solution to files...")
            self.write_solution(output_file)
            self.write_log(log_file)
            
            print(f"Solution found in {self.elapsed_time:.2f} seconds!")
            print(f"Solution written to {output_file}")
            print(f"Solution log written to {log_file}")
        else:
            print("No solution found.")


def main():
    parser = argparse.ArgumentParser(description='Solve crossword puzzles using CSP')
    parser.add_argument('grid_file', nargs='?', default="input_files/grid-11x11-20W-83L-38B.txt",
                        help='Path to the grid file (default: input_files/grid-11x11-20W-83L-38B.txt)')
    parser.add_argument('--wordlist', default='input_files/lista_palavras.txt',
                        help='Path to the wordlist file (default: input_files/lista_palavras.txt)')
    
    args = parser.parse_args()
    
    # Adjust grid path if not already in input_files directory
    if not args.grid_file.startswith('input_files/') and os.path.exists(f'input_files/{args.grid_file}'):
        args.grid_file = f'input_files/{args.grid_file}'
    
    if not os.path.exists(args.grid_file):
        print(f"Error: Grid file '{args.grid_file}' not found.")
        return 1
    
    if not os.path.exists(args.wordlist):
        print(f"Error: Wordlist file '{args.wordlist}' not found.")
        return 1
    
    solver = CrosswordCSP(args.grid_file, args.wordlist)
    solver.run()
    return 0

if __name__ == "__main__":
    main() 