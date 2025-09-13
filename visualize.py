import argparse
import graphviz
import os
import sys

# Alias for types used in decompression
INT_SIZE = 4
TPAIR_SIZE = INT_SIZE * 2

def load_rlz_repair_grammar(rules_filepath):
    """
    Loads a RLZ-RePair grammar from the .R file.

    The binary file is expected to be structured as follows:
    1. Alphabet Size (int): A 4-byte integer ('alpha') specifying the number
       of terminal symbols.
    2. Character Map (bytes): 'alpha' bytes mapping terminal symbol IDs to
       their character representation.
    3. Rules (bytes): A sequence of rules, where each rule is 8 bytes
       (a pair of 4-byte integers representing two symbol IDs).

    Args:
        rules_filepath (str): The path to the grammar's .rules file.

    Returns:
        dict: A dictionary representing the complete grammar.
              - Non-terminal IDs map to a tuple of two symbol IDs.
              - Terminal IDs map to their single byte representation.
    
    Raises:
        IOError: If the file is malformed, truncated, or cannot be read.
    """
    # Get the size of the rules file
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
        # Generate the grammar
        grammar = {}
        # Generate the rules for the terminal symbols
        for i in range(alpha):
            grammar[i] = char_map[i:i+1]
        # Generate the rules for the non-terminal symbols
        for i in range(num_rules):
            rule_id = alpha + i
            # Get the 8-byte slice for the current rule
            start_index = i * TPAIR_SIZE
            end_index = start_index + TPAIR_SIZE
            rule_chunk = rules_bytes[start_index:end_index]
            # Unpack the two symbols from the 8-byte chunk
            s1 = int.from_bytes(rule_chunk[0:INT_SIZE], 'little')
            s2 = int.from_bytes(rule_chunk[INT_SIZE:TPAIR_SIZE], 'little')
            grammar[rule_id] = (s1, s2)

        print("Grammar loaded successfully.\n")
        return grammar

def load_bigrepair_grammar(rules_filepath):
    """
    Loads a BigRePair grammar from the .R file.

    The binary file is expected to be structured as follows:
    1. Alphabet Size (int): A 4-byte integer ('alpha') specifying the number
       of terminal symbols.
    2. Rules (bytes): A sequence of rules, where each rule is 8 bytes
       (a pair of 4-byte integers representing two symbol IDs).

    Args:
        rules_filepath (str): The path to the grammar's .rules file.

    Returns:
        dict: A dictionary representing the complete grammar.
              - Non-terminal IDs map to a tuple of two symbol IDs.
              - Terminal IDs map to their single byte representation.
    
    Raises:
        IOError: If the file is malformed, truncated, or cannot be read.
    """
    # Get the size of the rules file
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
        # Generate the grammar
        grammar = {}
        # Generate the rules for the non-terminal symbols
        for i in range(num_rules):
            rule_id = alpha + i
            # Get the 8-byte slice for the current rule
            start_index = i * TPAIR_SIZE
            end_index = start_index + TPAIR_SIZE
            rule_chunk = rules_bytes[start_index:end_index]
            # Unpack the two symbols from the 8-byte chunk
            s1 = int.from_bytes(rule_chunk[0:INT_SIZE], 'little')
            s2 = int.from_bytes(rule_chunk[INT_SIZE:TPAIR_SIZE], 'little')
            grammar[rule_id] = (s1, s2)

        print("Grammar loaded successfully.\n")
        return grammar


def format_rlz_repair_symbol(symbol_id, grammar):
    """Formats a symbol ID for RLZ-RePair printing based on its type."""
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


def print_rlz_repair_grammar(grammar):
    """Prints a summary of the loaded RLZ-RePair grammar rules."""
    print("--- Parsed Grammar Rules ---")
    
    # Separate terminal and non-terminal symbols for clarity
    terminals = {k: v for k, v in grammar.items() if isinstance(v, bytes)}
    non_terminals = {k: v for k, v in grammar.items() if isinstance(v, tuple)}
    
    print(f"\nFound {len(terminals)} terminal symbols.")
    count = 0
    # Sort by ID to get a consistent order of printable characters
    for symbol_id, char_byte in sorted(terminals.items()):
        # Attempt to decode for cleaner printing, focusing on printable chars
        try:
            char = char_byte.decode('ascii')
            if char.isprintable():
                print(f"    {symbol_id} -> '{char}'")
                count += 1
        except UnicodeDecodeError:
            continue

    print(f"\nFound {len(non_terminals)} non-terminal rules:")
    # Sort by ID to get a consistent order and print all rules
    for rule_id, symbols in sorted(list(non_terminals.items())):
        s1, s2 = symbols
        # Use the new helper to format the rule's components
        formatted_s1 = format_rlz_repair_symbol(s1, grammar)
        formatted_s2 = format_rlz_repair_symbol(s2, grammar)
        print(f"    {rule_id} -> ({formatted_s1},{formatted_s2})")

    print(f"\nTotal symbols in grammar: {len(grammar)}")


def format_bigrepair_symbol(symbol_id, grammar):
    """
    Formats a symbol ID from a BigRepair grammar for printing.
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


def print_bigrepair_grammar(grammar):
    """Prints a summary of the loaded BigRepair grammar rules."""
    print("--- Parsed Grammar Rules ---")
    
    # Separate terminal and non-terminal symbols for clarity
    terminals = {k: v for k, v in grammar.items() if isinstance(v, bytes)}
    non_terminals = {k: v for k, v in grammar.items() if isinstance(v, tuple)}
    
    print(f"\nFound {len(non_terminals)} non-terminal rules:")
    # Sort by ID to get a consistent order and print all rules
    for rule_id, symbols in sorted(list(non_terminals.items())):
        s1, s2 = symbols
        # Use the new helper to format the rule's components
        formatted_s1 = format_bigrepair_symbol(s1, grammar)
        formatted_s2 = format_bigrepair_symbol(s2, grammar)
        print(f"    {rule_id} -> ({formatted_s1},{formatted_s2})")

    print(f"\nTotal symbols in grammar: {len(grammar)}")


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

def print_compressed_str(sequence):
    """ Prints the loaded compressed sequence to the console. """
    print("\n--- Loaded Compressed Sequence ---")
    print(sequence)
    print(f"Sequence contains {len(sequence)} symbols.")


# --- Visualization Code ---

# A counter to ensure every node has a unique ID
node_counter = 0

def build_tree_rlz_recursive(dot, symbol_id, parsed_grammar, parent_id=None):
    """
    Recursively builds the parse tree by adding nodes and edges to the graph.

    This corrected function properly:
    - Uses the `parsed_grammar` passed as an argument.
    - Uses `format_rlz_repair_symbol` to create clear node labels.
    - Differentiates between terminals and non-terminals to avoid crashing.
    """
    global node_counter
    
    # Get the human-readable label for the current symbol ID
    label = str(format_symbol(symbol_id, parsed_grammar))
    
    # Get the actual value (rule or character) from the grammar
    symbol_value = parsed_grammar.get(symbol_id)
    
    # Create a unique ID for the graphviz node
    current_node_id = f"node{node_counter}"
    node_counter += 1
    
    # Add the node to the graph, with a different shape for terminals vs. non-terminals
    if isinstance(symbol_value, tuple):
        dot.node(current_node_id, label=label, shape='box')  # Non-terminal
    else:
        dot.node(current_node_id, label=label, shape='plaintext')  # Terminal
    
    # Connect this node to its parent, if one exists
    if parent_id:
        dot.edge(parent_id, current_node_id)
    
    # If the symbol is a non-terminal (a tuple), recurse for its children
    if isinstance(symbol_value, tuple):
        s1, s2 = symbol_value
        build_tree_rlz_recursive(dot, s1, parsed_grammar, parent_id=current_node_id)
        build_tree_rlz_recursive(dot, s2, parsed_grammar, parent_id=current_node_id)
        
    return current_node_id

def build_tree_bigrepair_recursive(dot, symbol_id, parsed_grammar, parent_id=None):
    """
    Recursively builds the parse tree by adding nodes and edges to the graph.

    This corrected function properly:
    - Uses the `parsed_grammar` passed as an argument.
    - Uses `format_bigrepair_symbol` to create clear node labels.
    - Differentiates between terminals and non-terminals to avoid crashing.
    """
    global node_counter
    
    # Get the human-readable label for the current symbol ID
    label = str(format_bigrepair_symbol(symbol_id, parsed_grammar))
    
    # Get the actual value (rule or character) from the grammar
    symbol_value = parsed_grammar.get(symbol_id)
    
    # Create a unique ID for the graphviz node
    current_node_id = f"node{node_counter}"
    node_counter += 1
    
    # Add the node to the graph, with a different shape for terminals vs. non-terminals
    if isinstance(symbol_value, tuple):
        dot.node(current_node_id, label=label, shape='box')  # Non-terminal
    else:
        dot.node(current_node_id, label=label, shape='plaintext')  # Terminal
    
    # Connect this node to its parent, if one exists
    if parent_id:
        dot.edge(parent_id, current_node_id)
    
    # If the symbol is a non-terminal (a tuple), recurse for its children
    if isinstance(symbol_value, tuple):
        s1, s2 = symbol_value
        build_tree_bigrepair_recursive(dot, s1, parsed_grammar, parent_id=current_node_id)
        build_tree_bigrepair_recursive(dot, s2, parsed_grammar, parent_id=current_node_id)
        
    return current_node_id

# --- Main ---
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Print the parse tree of RePair grammars")
    parser.add_argument("-s", "--sequence", type=str, help="Path to the compressed sequence file.", required=True)
    parser.add_argument('-r', "--rules", type=str, help="Path to grammar rule file.", required=True)
    parser.add_argument("-o", "--output", type=str, help="Prefix of output file.", default="parse_tree")
    parser.add_argument("-e", "--extension", nargs='+', type=str, help="One or more image file extensions (e.g., png svg jpg).", default=["png"])
    parser.add_argument("-p", "--program", type=str, help="Compression program used (repair, rlz-repair, bigrepair, rerepair).", default="rlz-repair")
    parser.add_argument("--print_grammar", action='store_true', help="If set, print the parsed grammar rules to the console.")
    parser.add_argument("--print_sequence", action='store_true', help="If set, print the compressed sequence to the console.")
    parser.add_argument("--no_image", action='store_true', help="If set, do not produce the parse tree image.")
    args = parser.parse_args()

    print(f"Compressed sequence file location: {args.sequence}")
    print(f"Rule file location: {args.rules}")
    print(f"Output file prefix: {args.output}")
    print(f"Output file extension: {args.extension}\n")

    # Load the grammar for the specific type of software
    if (args.program == "rlz-repair"):
        parsed_grammar = load_rlz_repair_grammar(args.rules)
    elif (args.program == "bigrepair"):
        parsed_grammar = load_bigrepair_grammar(args.rules)
    elif (args.program == "rerepair"):
        parsed_grammar = load_rerepair_grammar(args.rules)
    else:
        raise ValueError("{args.program} is not a valid program type.")

    # Print the grammar rules if specified
    if (args.print_grammar):
        if (args.program == "rlz-repair"):
            print_rlz_repair_grammar(parsed_grammar)
        elif (args.program == "bigrepair"):
            print_bigrepair_grammar(parsed_grammar)
        elif (args.program == "rerepair"):
            print_rerepair_grammar(parsed_grammar)
        else:
            raise ValueError("{args.program} is not a valid program type.")

    # Load the compressed sequence
    compressed_sequence = load_compressed_str(args.sequence)

    # Print the compressed sequence if specified
    if (args.print_sequence):
        print_compressed_str(compressed_sequence)

    # Exit if image is not required
    if (args.no_image):
        sys.exit()

    # Initialize the graph object (Digraph for Directed Graph)
    dot = graphviz.Digraph(comment='RePair Parse Tree')
    dot.attr(rankdir='TB', splines='line')
    dot.attr('node', shape='box', style='rounded', fontname='helvetica')
    dot.attr('edge', arrowhead='none')

    # Create a dynamic label for the root node based on the loaded sequence
    if (args.program == "rlz-repair"):
        sequence_labels = [str(format_rlz_repair_symbol(s, parsed_grammar)) for s in compressed_sequence]
    elif (args.program == "bigrepair"):
        sequence_labels = [str(format_bigrepair_symbol(s, parsed_grammar)) for s in compressed_sequence]
    elif (args.program == "rerepair"):
        sequence_labels = [str(format_rerepair_symbol(s, parsed_grammar)) for s in compressed_sequence]
    else:
        raise ValueError("{args.program} is not a valid program type.")

    root_label = f"Compressed Sequence\n({' '.join(sequence_labels)})"

    # Create a single invisible root node to connect the sequence
    root_id = "root"
    dot.node(root_id, label=root_label, shape='none')

    # Build the tree for each symbol in the compressed sequence
    for symbol in compressed_sequence:
        # Pass the root_id as the parent for top-level symbols
        if (args.program == "rlz-repair"):
            child_root_id = build_tree_rlz_recursive(dot, symbol, parsed_grammar, parent_id=root_id)
        elif (args.program == "bigrepair"):
            child_root_id = build_tree_bigrepair_recursive(dot, symbol, parsed_grammar, parent_id=root_id)
        elif (args.program == "rerepair"):
            child_root_id = build_tree_rerepair_recursive(dot, symbol, parsed_grammar, parent_id=root_id)
        else:
            raise ValueError("{args.program} is not a valid program type.")

    # Render the graph to a file. 
    output_filename = args.output
    try:
        for ext in args.extension:
            dot.render(output_filename, format=args.ext, view=False, cleanup=True)
            print(f"\n✅ Figure saved successfully as '{output_filename}.{ext}'")
    except graphviz.backend.execute.ExecutableNotFound:
        print("\n❌ Error: Graphviz executable not found.")
        print("Please ensure Graphviz is installed and in your system's PATH.")
        print("Installation instructions: https://graphviz.org/download/")