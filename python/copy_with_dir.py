from pathlib import Path
#from tqdm import tqdm as tqdm
import shutil

source = Path("S:/MT/experiments/BT-English")
dest_root = Path("E:/Work/MT/experiments")

top_shared_folder_name = "MT"
bottom_shared_folder_name = "experiments"
file_patterns = ["config.yml", "effective-config*.yml", "scores-*.csv", "test*"]

for file_pattern in file_patterns:
    files = source.rglob(file_pattern)

    for file in files:
        for idx, parent in enumerate(file.parents):
    #        print(parent, "    ", idx, "    ", parent.name)
            if parent.name == bottom_shared_folder_name:
                
                # Create the folders on the destination drive.
                new_dest = dest_root
                #print(f"Starting to add to {new_dest}")
                for i in reversed(range(idx)):
                    #print(f"Adding {file.parents[i].name}")
                    new_dest = Path(new_dest , file.parents[i].name)
                    #print(f"Dest is now: {new_dest}")

                # Make the folders required if necessary
                if not new_dest.is_dir():                 
                    new_dest.mkdir(parents=True, exist_ok=True)
                    destination_file = new_dest / file.name

                    # Write an exact copy of the file from the source to the new destitation folder.
                    print(f"Writing:  {destination_file}")
                    shutil.copyfile(file, destination_file)
                else:
                    destination_file = new_dest / file.name
                    if not destination_file.is_file():

                    # Write an exact copy of the file from the source to the new destitation folder.
                    print(f"Writing:  {destination_file}")
                    shutil.copyfile(file, destination_file)

                


