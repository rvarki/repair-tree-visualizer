import argparse
import os
import sys
import random
import time

# Alias for types used in decompression
INT_SIZE = 4
TPAIR_SIZE = INT_SIZE * 2

def load_original_repair_grammar_with_lengths(rules_filepath):
    """
    Loads an original RePair grammar from a .R file and computes expansion lengths.

    Args:
        rules_filepath (str): The path to the grammar's .rules file.

    Returns:
        tuple[dict, dict]: A tuple containing two dictionaries:
            1. grammar: Maps symbol IDs to their rule (byte for terminals,
               tuple of two ints for non-terminals).
            2. lengths: Maps symbol IDs to their full expansion length (int).
    
    Raises:
        IOError: If the file is malformed, truncated, or cannot be read.
    """
    if not os.path.exists(rules_filepath):
        raise FileNotFoundError(f"Error: Rules file not found at {rules_filepath}")

    rules_size = os.path.getsize(rules_filepath)
    with open(rules_filepath, 'rb') as f:
        # Get the size of the original alphabet
        alpha_bytes = f.read(INT_SIZE)
        if len(alpha_bytes) < INT_SIZE:
            raise IOError(f"Error: Cannot read alphabet from rules file {rules_filepath}")
        alpha = int.from_bytes(alpha_bytes, 'little')
        
        # Read the character map
        char_map = f.read(alpha)
        if len(char_map) < alpha:
            raise IOError(f"Error: Could not read character map from rules file {rules_filepath}")
            
        # Calculate the number of rules
        num_rules = (rules_size - INT_SIZE - alpha) // TPAIR_SIZE
        
        # Read the block rules data
        rules_bytes = f.read(num_rules * TPAIR_SIZE)
        if len(rules_bytes) < num_rules * TPAIR_SIZE:
            raise IOError(f"Error: Truncated rules data in {rules_filepath}")
        
        # Initialize two dictionaries: one for rules, one for lengths
        grammar = {}
        lengths = {}

        # Terminals are the base case: their expansion length is always 1.
        for i in range(alpha):
            grammar[i] = char_map[i:i+1]
            lengths[i] = 1

        # The length of a new rule is the sum of the lengths of its children.
        # Since rules are defined in order, the lengths for s1 and s2 will
        # already be in the `lengths` dictionary.
        for i in range(num_rules):
            rule_id = alpha + i
            
            # Get the 8-byte slice for the current rule
            start_index = i * TPAIR_SIZE
            end_index = start_index + TPAIR_SIZE
            rule_chunk = rules_bytes[start_index:end_index]
            
            # Unpack the two symbols from the 8-byte chunk
            s1 = int.from_bytes(rule_chunk[0:INT_SIZE], 'little')
            s2 = int.from_bytes(rule_chunk[INT_SIZE:TPAIR_SIZE], 'little')
            
            # Store the rule in the grammar dictionary
            grammar[rule_id] = (s1, s2)
            
            # Calculate and store the expansion length
            expansion_length = lengths[s1] + lengths[s2]
            lengths[rule_id] = expansion_length

        print("Grammar and expansion lengths loaded successfully. \n")
        return grammar, lengths


def load_pfp_repair_grammar_with_lengths(rules_filepath):
    """
    Loads a PFP-created RePair grammar from .R file and computes expansion lengths.

    Args:
        rules_filepath (str): The path to the grammar's .rules file.

    Returns:
        tuple[dict, dict]: A tuple containing two dictionaries:
            1. grammar: Maps non-terminal IDs to their rule (tuple of two ints).
               Terminal rules are not explicitly stored.
            2. lengths: Maps all symbol IDs (terminal and non-terminal) to
               their full expansion length (int).
    
    Raises:
        IOError: If the file is malformed, truncated, or cannot be read.
    """
    if not os.path.exists(rules_filepath):
        raise FileNotFoundError(f"Error: Rules file not found at {rules_filepath}")

    rules_size = os.path.getsize(rules_filepath)
    with open(rules_filepath, 'rb') as f:
        # Get the size of the original alphabet
        alpha_bytes = f.read(INT_SIZE)
        if len(alpha_bytes) < INT_SIZE:
            raise IOError(f"Error: Cannot read alphabet from rules file {rules_filepath}")
        alpha = int.from_bytes(alpha_bytes, 'little')
        
        # Calculate the number of rules
        num_rules = (rules_size - INT_SIZE) // TPAIR_SIZE
        
        # Read the block rules data
        rules_bytes = f.read(num_rules * TPAIR_SIZE)
        if len(rules_bytes) < num_rules * TPAIR_SIZE:
            raise IOError(f"Error: Truncated rules data in {rules_filepath}")

        # Initialize dictionaries for grammar rules and lengths
        grammar = {}
        lengths = {}

        # Terminals (IDs 0 to alpha-1) have an expansion length of 1.
        for i in range(alpha):
            lengths[i] = 1

        # The length of a new rule is the sum of the lengths of its children.
        for i in range(num_rules):
            rule_id = alpha + i
            
            # Get the 8-byte slice for the current rule
            start_index = i * TPAIR_SIZE
            end_index = start_index + TPAIR_SIZE
            rule_chunk = rules_bytes[start_index:end_index]
            
            # Unpack the two symbols from the 8-byte chunk
            s1 = int.from_bytes(rule_chunk[0:INT_SIZE], 'little')
            s2 = int.from_bytes(rule_chunk[INT_SIZE:TPAIR_SIZE], 'little')
            
            # Store the rule in the grammar dictionary
            grammar[rule_id] = (s1, s2)
            
            # Calculate and store the expansion length by looking up the
            # lengths of the constituent symbols, which are guaranteed to exist.
            expansion_length = lengths[s1] + lengths[s2]
            lengths[rule_id] = expansion_length

        print("Grammar and expansion lengths loaded successfully. \n")
        return grammar, lengths


def load_compressed_str(sequence_filepath):
    """Loads the compressed .C sequence file"""
    sequence_size = os.path.getsize(sequence_filepath) // INT_SIZE
    compressed_sequence = []
    with open(sequence_filepath, 'rb') as f:
        for _ in range(sequence_size):
            int_bytes = f.read(INT_SIZE)
            # Error check: ensure we read the expected number of bytes
            if len(int_bytes) < INT_SIZE:
                raise IOError(f"Error: Truncated file, could not read full integer.")
            # Convert bytes to an integer and append to the list
            value = int.from_bytes(int_bytes, 'little')
            compressed_sequence.append(value)
    return compressed_sequence




def format_original_repair_symbol(symbol_id, grammar):
    """Formats a symbol ID for original repair printing based on its type."""
    symbol_value = grammar.get(symbol_id)
    if isinstance(symbol_value, bytes):
        # It's a terminal, return its character representation.
        try:
            char = symbol_value.decode('ascii')
            if char.isprintable():
                return f"'{char}'"
            else:
                return f"byte({symbol_id})" # For non-printable chars
        except UnicodeDecodeError:
            return f"byte({symbol_id})"
    elif isinstance(symbol_value, tuple):
        # It's a non-terminal, return the integer ID directly.
        return str(symbol_id)
    else:
        # Fallback for unknown symbol types.
        return f"?{symbol_id}?"

def format_pfp_repair_symbol(symbol_id, grammar):
    """
    Formats a symbol ID from a PFP repair grammar for printing.
    It assumes symbol IDs < 256 are terminals (characters) and
    symbol IDs >= 256 are non-terminals (rules).
    """
    # 1. First, check if the symbol is a terminal by its value.
    if symbol_id < 256:
        # It's a character. Convert the integer ID to its char equivalent.
        char = chr(symbol_id)
        # For clean output, check if the character is printable.
        if char.isprintable():
            return f"'{char}'"
        else:
            # If not printable (e.g., null, tab), show its byte ID instead.
            return f"byte({symbol_id})"

    # 2. If the symbol is not a terminal, it must be a non-terminal rule.
    symbol_value = grammar.get(symbol_id)
    if isinstance(symbol_value, tuple):
        # It's a rule, so just return its integer ID as a string.
        return str(symbol_id)
    else:
        # This case handles an unknown symbol with an ID >= 256.
        return f"?{symbol_id}?"



def random_access(top_level_sequence, grammar, lengths, position):
    """
    Finds the character at a given position in the original text.

    Args:
        top_level_sequence (list[int]): The sequence of symbols from the .C file.
        grammar (dict): The grammar rules mapping non-terminals to their expansions.
        lengths (dict): A dict mapping all symbol IDs to their expansion length.
        position (int): The 0-indexed position of the character to retrieve.

    Returns:
        int: The terminal ID of the character at the specified position.
    """

    current_sequence = top_level_sequence
    while True:
        for symbol_id in current_sequence:
            symbol_len = lengths[symbol_id]
            if position < symbol_len:
                if symbol_id not in grammar or not isinstance(grammar[symbol_id], tuple):
                    return symbol_id # Found the terminal character's ID! 
                current_sequence = grammar[symbol_id]
                break 
            else:
                position -= symbol_len


def calculate_grammar_depth_stats(grammar, top_level_sequence, lengths, uncompressed_size):
    """
    Calculates and prints the max and average depth of the parse tree forest.

    Args:
        grammar (dict): The grammar rules.
        top_level_sequence (list[int]): The sequence of top-level symbols.
        lengths (dict): A dict mapping symbol IDs to their expansion length.
        uncompressed_size (int): The total length of the original text.
    """
    depth_cache = {}
    leaf_depth_sum_cache = {}

    def get_max_depth(symbol_id):
        # Memoization: Return cached result if available
        if symbol_id in depth_cache:
            return depth_cache[symbol_id]
        
        # Base case: A terminal symbol has a depth of 0 in its own subtree.
        if symbol_id not in grammar or not isinstance(grammar.get(symbol_id), tuple):
            depth_cache[symbol_id] = 0
            return 0

        # Recursive step: Depth is 1 + max depth of its children's subtrees.
        s1, s2 = grammar[symbol_id]
        depth = 1 + max(get_max_depth(s1), get_max_depth(s2))
        depth_cache[symbol_id] = depth
        return depth

    def get_leaf_depth_sum(symbol_id):
        # Memoization: Return cached result if available
        if symbol_id in leaf_depth_sum_cache:
            return leaf_depth_sum_cache[symbol_id]

        # Base case: A terminal symbol is a leaf at depth 0 (relative to itself).
        if symbol_id not in grammar or not isinstance(grammar.get(symbol_id), tuple):
            leaf_depth_sum_cache[symbol_id] = 0
            return 0
        
        # Recursive step for non-terminals
        s1, s2 = grammar[symbol_id]
        
        # Get the sum of leaf depths from children subtrees
        sum1 = get_leaf_depth_sum(s1)
        sum2 = get_leaf_depth_sum(s2)
        
        # The total sum is the sum from children, plus 1 for each leaf in
        # their expansions, because they are all now one level deeper.
        # The number of leaves is given by the `lengths` dictionary.
        total_sum = sum1 + sum2 + lengths[s1] + lengths[s2]
        
        leaf_depth_sum_cache[symbol_id] = total_sum
        return total_sum

    # --- Main Calculation ---
    max_overall_depth = 0
    total_leaf_depth_sum = 0
    
    print("Calculating parse tree depth statistics...")
    
    # Iterate through the "forest" of trees in the top-level sequence
    for symbol in top_level_sequence:
        max_overall_depth = max(max_overall_depth, get_max_depth(symbol))
        total_leaf_depth_sum += get_leaf_depth_sum(symbol)
    
    # Calculate average depth
    if uncompressed_size > 0:
        average_depth = total_leaf_depth_sum / uncompressed_size
    else:
        average_depth = 0

    print("\n--- Depth Statistics ---")
    print(f"Maximum parse tree depth: {max_overall_depth}")
    print(f"Average leaf depth: {average_depth:.4f}")
    print(f"The number of leaves (uncompressed file size): {uncompressed_size}")
    print("------------------------\n")


# --- Main ---
if __name__ == "__main__":
    # sys.setrecursionlimit(20000)
    parser = argparse.ArgumentParser(description="Print the parse tree of RePair grammars")
    parser.add_argument("-s", "--sequence", type=str, help="Path to the compressed sequence file.", required=True)
    parser.add_argument('-r', "--rules", type=str, help="Path to grammar rule file.", required=True)
    parser.add_argument("-o", "--output", type=str, help="Prefix of output file.", default="ra_output")
    parser.add_argument("-i", "--iteration", type=int, help="Number of random positions to test", default=10000)
    parser.add_argument("-p", "--program", type=str, help="Compression program used (repair, rlz-repair, bigrepair, rerepair).", default="rlz-repair")
    parser.add_argument("--seed", type=int, help="Seed for random number generator", default=100)
    parser.add_argument("--depth", action="store_true", help="Calculate the depth of the parse tree.")
    parser.add_argument("--no_ra", action="store_true", help="Do not perform random access test.")
    args = parser.parse_args()

    print(f"Compressed sequence file location: {args.sequence}")
    print(f"Rule file location: {args.rules}")
    print(f"Output file prefix: {args.output}")
    
    # Load the grammar for the specific type of software
    if (args.program == "repair" or args.program == "rlz-repair"):
        parsed_grammar, lengths = load_original_repair_grammar_with_lengths(args.rules)
    elif (args.program == "bigrepair" or args.program == "rerepair"):
        parsed_grammar, lengths = load_pfp_repair_grammar_with_lengths(args.rules)
    else:
        raise ValueError("{args.program} is not a valid program type.")
    
    # Load the compressed sequence
    compressed_sequence = load_compressed_str(args.sequence)

    # Calculate length of uncompressed sequence
    uncompressed_size = 0
    for i in range(len(compressed_sequence)):
        uncompressed_size += lengths[compressed_sequence[i]]

    # Pass the seed to RNG
    random.seed(args.seed)
    
    # Calculate depth of parse tree
    if (args.depth):
        calculate_grammar_depth_stats(parsed_grammar, compressed_sequence, lengths, uncompressed_size)

    # RA test
    if (not args.no_ra):
        total_time = 0
        output_fp = args.output + ".txt"
        with open(output_fp, "w") as outfile:
            for i in range(args.iteration):
                random_pos = random.randint(0, uncompressed_size - 1) # Since inclusive ends
                start_time = time.perf_counter()
                ra_char = random_access(compressed_sequence, parsed_grammar, lengths, random_pos)
                end_time = time.perf_counter()
                elapsed_time = end_time - start_time
                total_time += elapsed_time
                
                if i % 1000 == 0: # Print progress periodically
                    print(f"Completed {i}/{args.iteration} queries...")

                if args.program in ("repair", "rlz-repair"):
                    outfile.write(f"pos: {random_pos} value: {format_original_repair_symbol(ra_char, parsed_grammar)}\n")
                else: 
                    outfile.write(f"pos: {random_pos} value: {format_pfp_repair_symbol(ra_char, parsed_grammar)}\n")

        print("\n--- Benchmark Complete ---")
        print(f"It took {total_time:.4f} seconds to perform {args.iteration} random access queries.")
        average_time = total_time / args.iteration
        print(f"It took {average_time:.6f} seconds on average per random access query.")
        print(f"Results saved to {output_fp}")