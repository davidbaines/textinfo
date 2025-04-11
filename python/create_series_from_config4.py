import argparse
from pathlib import Path
import yaml
import re
import shutil
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

def get_input_dir_relative_path(input_dir, base="MT/experiments"):
    """Get the input directory path relative to the base directory."""
    if isinstance(input_dir, str):
        input_dir_str = input_dir
    else:
        input_dir_str = str(input_dir)
        
    # Clean path by standardizing separators
    input_dir_str = input_dir_str.replace('\\', '/')
    base = base.replace('\\', '/')
    
    # Check if the base path is in the input directory path
    base_index = input_dir_str.lower().find(base.lower())
    if base_index != -1:
        return input_dir_str[base_index + len(base) + 1:]  # +1 for the slash
    
    # If not found, just return the last parts of the path
    parts = input_dir_str.split('/')
    if len(parts) >= 3:
        return '/'.join(parts[-3:])  # Return last 3 parts like Country/Language/Folder
    return input_dir_str

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

def generate_configs(config_file_path, overwrite=False):
    """Generate multiple configs by removing one source at a time from the first corpus pair."""
    # Read the original config file
    config_path = Path(config_file_path)
    input_dir = config_path.parent
    parent_dir = input_dir.parent  # Go up one level from the config file
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Check for translate_config.yml
    translate_config_path = input_dir / "translate_config.yml"
    has_translate_config = translate_config_path.exists()
    
    # Validate language codes
    missing_codes = validate_language_codes(config)
    if missing_codes:
        print(f"WARNING: The following language codes are used but not defined in lang_codes section: {', '.join(missing_codes)}")
    
    # Track created folders for the notes
    created_folders = [get_relative_path(input_dir)]
    
    # We only modify the first corpus pair
    if not config['data']['corpus_pairs']:
        print("No corpus pairs found in the config file.")
        return created_folders, has_translate_config
        
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
        
        # Create folder if it doesn't exist or if overwriting
        if not new_folder.exists() or overwrite:
            new_folder.mkdir(exist_ok=True)
            
            # Create a new config with current sources
            new_config = deepcopy(config)
            new_config['data']['corpus_pairs'][0]['src'] = sources.copy()
            
            # Write the new config
            with open(new_folder / 'config.yml', 'w') as f:
                yaml.dump(new_config, f, default_flow_style=False, sort_keys=False)
            
            # Copy translate_config.yml if it exists
            if has_translate_config:
                shutil.copy2(translate_config_path, new_folder / "translate_config.yml")
        
        # Add to created folders list
        created_folders.append(get_relative_path(new_folder))
    
    return created_folders, has_translate_config

def update_notes_file(parent_dir, created_folders, has_translate_config):
    """Update the Notes.txt file with preprocessing and experiment commands."""
    # Update Notes.txt
    notes_path = parent_dir / "Notes.txt"
    
    # Generate preprocess commands
    preprocess_commands = []
    experiment_commands = []
    
    for folder in created_folders:
        # Convert path format to use backslashes for Windows compatibility
        folder_path = folder.replace('/', '\\')
        
        # Add preprocess command
        preprocess_commands.append(f"poetry run python -m silnlp.nmt.preprocess --stats {folder_path}")
        
        # Add experiment command (with --translate only if translate_config.yml exists)
        translate_option = " --translate" if has_translate_config else ""
        experiment_commands.append(f"poetry run python -m silnlp.nmt.experiment --save-checkpoints --clearml-queue jobs_backlog{translate_option} {folder_path}")
    
    # Write to Notes.txt
    with open(notes_path, 'w') as notes_file:
        # Write preprocess commands
        notes_file.write("\n".join(preprocess_commands) + "\n")
        # Add a blank line between blocks
        notes_file.write("\n")
        # Write experiment commands
        notes_file.write("\n".join(experiment_commands) + "\n")

def main():
    parser = argparse.ArgumentParser(description='Generate ML configuration files with reduced sources.')
    parser.add_argument('config_path', help='Path to a config.yml file or directory containing a config.yml file')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing configuration files')
    
    args = parser.parse_args()
    
    try:
        config_file = find_config_file(args.config_path)
        print(f"Using config file: {config_file}")
        
        # Get parent directory for Notes.txt
        parent_dir = config_file.parent.parent
        
        created_folders, has_translate_config = generate_configs(config_file, args.overwrite)
        
        # Only update Notes.txt if not in overwrite mode
        if not args.overwrite:
            update_notes_file(parent_dir, created_folders, has_translate_config)
        
        print("Configuration files generated successfully.")
        print(f"Created/Updated folders: {len(created_folders)}")
        for folder in created_folders:
            print(f"  - {folder}")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())