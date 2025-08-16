import argparse
from pathlib import Path
import yaml
import re
from copy import deepcopy

def extract_isocode(source_string):
    """Extract the ISO code (first part before dash) from a source string."""
    match = re.match(r'^([^-]+)', source_string)
    if match:
        return match.group(1)
    return source_string

def get_unique_folder_name(base_dir, base_name):
    """Generate unique folder name with incremented suffix."""
    suffix = 1
    while True:
        folder_name = f"{base_name}_{suffix}"
        folder_path = base_dir / folder_name
        if not folder_path.exists():
            return folder_name
        suffix += 1

def get_base_folder_name(sources, target):
    """Generate base folder name from sources and target of first corpus pair."""
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
    
    # Join with underscores
    return "_".join(unique_codes)

def find_config_file(path_arg):
    """Find the config.yml file based on the input path."""
    # Default base path
    base_path = Path("M:/MT/experiments")
    
    # Check if argument is a direct path to a file
    path = Path(path_arg)
    if path.is_file() and path.name == "config.yml":
        return path
    
    # Check if argument is a directory containing config.yml
    if path.is_dir() and (path / "config.yml").exists():
        return path / "config.yml"
    
    # Try prepending the base path and check again
    full_path = base_path / path_arg
    if full_path.is_dir() and (full_path / "config.yml").exists():
        return full_path / "config.yml"
    
    # Try as relative path within base directory
    if (base_path / path_arg / "config.yml").exists():
        return base_path / path_arg / "config.yml"
    
    raise FileNotFoundError(f"Could not find config.yml using path: {path_arg}")

def get_relative_path(path, base="MT/experiments"):
    """Get path relative to a base directory."""
    path_str = str(path)
    base_index = path_str.find(base)
    if base_index != -1:
        return path_str[base_index + len(base) + 1:]  # +1 for the slash
    return path_str

def validate_language_codes(config):
    """Validate that all source and target language codes are defined in lang_codes section."""
    lang_codes = config['data'].get('lang_codes', {})
    missing_codes = set()
    
    for pair in config['data']['corpus_pairs']:
        # Check source language codes
        for src in pair['src']:
            code = extract_isocode(src)
            if code not in lang_codes:
                missing_codes.add(code)
        
        # Check target language code
        trg_code = extract_isocode(pair['trg'])
        if trg_code not in lang_codes:
            missing_codes.add(trg_code)
    
    return list(missing_codes)

def generate_configs(config_file_path):
    """Generate multiple configs by removing one source at a time from the first corpus pair."""
    # Read the original config file
    config_path = Path(config_file_path)
    parent_dir = config_path.parent.parent  # Go up one level from the config file
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Validate language codes
    missing_codes = validate_language_codes(config)
    if missing_codes:
        print(f"WARNING: The following language codes are used but not defined in lang_codes section: {', '.join(missing_codes)}")
    
    # Track created folders for the notes
    created_folders = [get_relative_path(config_path.parent)]
    
    # We only modify the first corpus pair
    if not config['data']['corpus_pairs']:
        print("No corpus pairs found in the config file.")
        return created_folders
        
    first_pair = config['data']['corpus_pairs'][0]
    sources = first_pair['src'].copy()  # Create a copy to avoid modifying the original
    target = first_pair['trg']
    
    # Continue generating configs until only one source remains
    while len(sources) > 1:  # Now we stop when we reach the last source
        # Remove one source for this iteration
        sources.pop()
        
        # Create folder name based on current sources and target
        base_name = get_base_folder_name(sources, target)
        folder_name = get_unique_folder_name(parent_dir, base_name)
        new_folder = parent_dir / folder_name
        new_folder.mkdir(exist_ok=True)
        
        # Create a new config with current sources
        new_config = deepcopy(config)
        new_config['data']['corpus_pairs'][0]['src'] = sources.copy()
        
        # Write the new config
        with open(new_folder / 'config.yml', 'w') as f:
            yaml.dump(new_config, f, default_flow_style=False, sort_keys=False)
        
        # Add to created folders list
        created_folders.append(get_relative_path(new_folder))
    
    # Update Notes.txt
    notes_path = parent_dir / "Notes.txt"
    with open(notes_path, 'a') as notes_file:
        notes_file.write("\n".join(created_folders) + "\n")
    
    return created_folders

def main():
    parser = argparse.ArgumentParser(description='Generate ML configuration files with reduced sources.')
    parser.add_argument('config_path', help='Path to a config.yml file or directory containing a config.yml file')
    
    args = parser.parse_args()
    
    try:
        config_file = find_config_file(args.config_path)
        print(f"Using config file: {config_file}")
        
        created_folders = generate_configs(config_file)
        print("Configuration files generated successfully.")
        print(f"Created folders: {len(created_folders)}")
        for folder in created_folders:
            print(f"  - {folder}")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())