import argparse
from pathlib import Path
import yaml
import re
import shutil
from copy import deepcopy
from collections import Counter

def extract_isocode(source_string):
    """Extract the ISO code (first part before dash) from a source string."""
    match = re.match(r'^([^-]+)', source_string)
    if match:
        return match.group(1)
    return source_string

def get_folder_name(sources, target):
    """Generate folder name from sources and target of first corpus pair."""
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
    base_name = "_".join(unique_codes)
    
    # Check if we need a suffix higher than 1
    all_isocodes = [extract_isocode(src) for src in sources]
    all_isocodes.append(target_code)
    
    # Count occurrences of each ISO code
    code_counts = Counter(all_isocodes)
    
    # Use _1 as default, but increment if we have duplicated language codes
    has_duplicates = any(count > 1 for count in code_counts.values())
    
    if has_duplicates:
        return f"{base_name}_1"
    else:
        return f"{base_name}_1"

def find_config_file(path_arg):
    """Find the config.yml file based on the input path."""
    # Default base path
    base_path = Path("M:/MT/experiments")
    
    # Check if argument is a direct path to a file
    path = Path(path_arg)
    if path.is_file() and path.name == "config.yml":
        return path, "Found config.yml at specified path"
    
    # Check if argument is a directory containing config.yml
    if path.is_dir() and (path / "config.yml").exists():
        return path / "config.yml", f"Found config.yml in directory: {path}"
    
    # Try prepending the base path and check again
    full_path = base_path / path_arg
    if full_path.is_dir() and (full_path / "config.yml").exists():
        return full_path / "config.yml", f"Found config.yml in MT/experiments/{path_arg}"
    
    # Try as relative path within base directory
    if (base_path / path_arg / "config.yml").exists():
        return base_path / path_arg / "config.yml", f"Found config.yml in MT/experiments/{path_arg}"
    
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

def calculate_folder_names(config, parent_dir):
    """Calculate all folder names that will be needed."""
    first_pair = config['data']['corpus_pairs'][0]
    sources = first_pair['src'].copy()
    target = first_pair['trg']
    
    folder_names = []
    
    # For each number of sources (removing one at a time)
    while len(sources) > 1:  # Stop when we reach the last source
        sources.pop()
        
        # Get the base name without suffix
        base_name = "_".join([extract_isocode(src) for src in sources] + [extract_isocode(target)])
        
        # Check if we need a suffix higher than 1 by analyzing the original full list
        # Get all unique isocodes in the original list
        all_isocodes = [extract_isocode(src) for src in sources]
        all_isocodes.append(extract_isocode(target))
        
        # Count occurrences of each isocodes in the original full config
        isocode_counts = Counter(all_isocodes)
        
        # Determine suffix based on duplicate counts
        has_duplicates = any(count > 1 for count in isocode_counts.values())
        
        # Start with suffix 1
        suffix = 1
        
        # Try folders with incremented suffix if duplicates exist
        while True:
            folder_name = f"{base_name}_{suffix}"
            folder_path = parent_dir / folder_name
            
            # If no duplicates or folder doesn't exist, we can use this name
            if not has_duplicates or not folder_path.exists():
                break
                
            # If there are duplicates and folder exists, try next suffix
            suffix += 1
        
        folder_names.append((folder_name, parent_dir / folder_name, sources.copy()))
    
    return folder_names

def generate_configs(config_file_path, overwrite=False):
    """Generate multiple configs by removing one source at a time from the first corpus pair."""
    # Read the original config file
    config_path = Path(config_file_path)
    input_dir = config_path.parent
    parent_dir = input_dir.parent  # Go up one level from the config file
    
    print(f"Reading configuration from: {config_path}")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Check for translate_config.yml
    translate_config_path = input_dir / "translate_config.yml"
    has_translate_config = translate_config_path.exists()
    
    if has_translate_config:
        print(f"Found translate_config.yml in {input_dir}")
    else:
        print(f"No translate_config.yml found in {input_dir}")
    
    # Validate language codes
    missing_codes = validate_language_codes(config)
    if missing_codes:
        print(f"WARNING: The following language codes are used but not defined in lang_codes section: {', '.join(missing_codes)}")
    
    # Track created folders and their status for reporting
    folder_status = []
    created_folders = [get_relative_path(input_dir)]
    
    # We only modify the first corpus pair
    if not config['data']['corpus_pairs']:
        print("No corpus pairs found in the config file.")
        return created_folders, has_translate_config, folder_status
    
    # Calculate all folder names we'll need
    folder_configs = calculate_folder_names(config, parent_dir)
    
    print(f"Found {len(config['data']['corpus_pairs'][0]['src'])} sources in the first corpus pair")
    
    # Process each folder
    for folder_name, folder_path, sources in folder_configs:
        folder_existed = folder_path.exists()
        config_existed = (folder_path / 'config.yml').exists()
        translate_config_existed = (folder_path / 'translate_config.yml').exists()
        
        # If folder exists but we're not overwriting, skip file operations
        if folder_existed and not overwrite:
            folder_action = "Found existing folder (use --overwrite to update files)"
            config_action = "Left existing config.yml unchanged"
            translate_action = "Left existing translate_config.yml unchanged"
        else:
            # Create folder if it doesn't exist
            if not folder_existed:
                folder_path.mkdir(exist_ok=True)
                folder_action = "Created new folder"
            else:
                folder_action = "Found existing folder"
                
            # Create a new config with current sources
            new_config = deepcopy(config)
            new_config['data']['corpus_pairs'][0]['src'] = sources
            
            # Write the new config
            with open(folder_path / 'config.yml', 'w') as f:
                yaml.dump(new_config, f, default_flow_style=False, sort_keys=False)
            config_action = "Created new config.yml" if not config_existed else "Overwrote existing config.yml"
            
            # Copy translate_config.yml if it exists
            if has_translate_config:
                shutil.copy2(translate_config_path, folder_path / "translate_config.yml")
                translate_action = "Created new translate_config.yml" if not translate_config_existed else "Overwrote existing translate_config.yml"
            else:
                translate_action = "No translate_config.yml to copy"
        
        # Add to created folders list and status tracking
        rel_path = get_relative_path(folder_path)
        created_folders.append(rel_path)
        folder_status.append({
            'path': rel_path,
            'folder_action': folder_action,
            'config_action': config_action,
            'translate_action': translate_action,
            'sources_remaining': len(sources)
        })
    
    return created_folders, has_translate_config, folder_status

def update_notes_file(parent_dir, created_folders, has_translate_config):
    """Update the Notes.txt file with preprocessing and experiment commands."""
    # Update Notes.txt
    notes_path = parent_dir / "Notes.txt"
    notes_existed = notes_path.exists()
    
    # Generate preprocess commands
    preprocess_commands = []
    experiment_commands = []
    
    for folder in created_folders:
        # Convert path format to use backslashes for Windows compatibility
        folder_path = folder.replace('/', '\\')
        
        # Strip any "Drive:/MT/experiments/" prefix if present
        if "MT\\experiments\\" in folder_path:
            folder_path = folder_path.split("MT\\experiments\\")[1]
        
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
    
    action = "Updated existing Notes.txt" if notes_existed else "Created new Notes.txt"
    return action

def main():
    parser = argparse.ArgumentParser(description='Generate ML configuration files with reduced sources.')
    parser.add_argument('config_path', help='Path to a config.yml file or directory containing a config.yml file')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing configuration files')
    
    args = parser.parse_args()
    
    try:
        config_file, location_msg = find_config_file(args.config_path)
        print(location_msg)
        
        # Get parent directory for Notes.txt
        parent_dir = config_file.parent.parent
        
        created_folders, has_translate_config, folder_status = generate_configs(config_file, args.overwrite)
        
        # Summary of actions
        print("\n=== Folder Generation Summary ===")
        for status in folder_status:
            print(f"\nFolder: {status['path']} ({status['sources_remaining']} sources)")
            print(f"  {status['folder_action']}")
            print(f"  {status['config_action']}")
            print(f"  {status['translate_action']}")
        
        # Only update Notes.txt if not in overwrite mode
        if not args.overwrite:
            notes_action = update_notes_file(parent_dir, created_folders, has_translate_config)
            print(f"\n{notes_action} with {len(created_folders)} commands for preprocessing and experiments")
        else:
            print("\nSkipped Notes.txt update (--overwrite mode)")
        
        print(f"\nProcessed {len(folder_status)} configurations from {len(created_folders[0].split('/')[0])} sources")
        print("Configuration generation completed successfully.")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())