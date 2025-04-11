from pathlib import Path
import yaml
import shutil
import re

def extract_isocode(source_string):
    """Extract the ISO code (first part before dash) from a source string."""
    match = re.match(r'^([^-]+)', source_string)
    if match:
        return match.group(1)
    return source_string

def get_folder_name(sources, target):
    """Generate folder name from sources and target."""
    # Extract isocodes from sources and target
    isocodes = [extract_isocode(src) for src in sources]
    target_code = extract_isocode(target)
    
    # Add target code to the list
    isocodes.append(target_code)
    
    # Remove duplicates while preserving order
    unique_codes = []
    for code in isocodes:
        if code not in unique_codes:
            unique_codes.append(code)
    
    # Join with underscores and add "_1" suffix
    return "_".join(unique_codes) + "_1"

def generate_configs(config_file_path):
    """Generate multiple configs by removing one source at a time."""
    # Read the original config file
    config_path = Path(config_file_path)
    parent_dir = config_path.parent.parent  # Go up one level from the config file
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Extract corpus pairs and sources
    corpus_pairs = config['data']['corpus_pairs']
    
    # For each corpus pair (assuming there might be multiple)
    for i, pair in enumerate(corpus_pairs):
        sources = pair['src'].copy()  # Create a copy to avoid modifying the original
        target = pair['trg']
        
        # Continue generating configs until only one source remains
        while len(sources) > 0:
            # Create folder name based on current sources and target
            folder_name = get_folder_name(sources, target)
            new_folder = parent_dir / folder_name
            new_folder.mkdir(exist_ok=True)
            
            # Create a new config with current sources
            new_config = config.copy()
            new_config['data']['corpus_pairs'][i]['src'] = sources.copy()
            
            # Write the new config
            with open(new_folder / 'config.yml', 'w') as f:
                yaml.dump(new_config, f, default_flow_style=False, sort_keys=False)
            
            # Remove one source for the next iteration
            if sources:
                sources.pop()  # Remove the last source

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    else:
        config_file = input("Enter the path to your config.yml file: ")
    
    generate_configs(config_file)
    print("Configuration files generated successfully.")