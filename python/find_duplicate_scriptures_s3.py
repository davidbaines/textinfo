import argparse
import boto3
import hashlib
from pathlib import Path

def list_files_in_folder(bucket_name, folder_path):
    s3 = boto3.client('s3')
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_path)
    files = [obj['Key'] for obj in response.get('Contents', [])]
    return files

def download_metadata(bucket_name, file_key):
    s3 = boto3.client('s3')
    response = s3.head_object(Bucket=bucket_name, Key=file_key)
    metadata = {
        'size': response['ContentLength'],
        'last_modified': response['LastModified']
    }
    return metadata

def calculate_file_hash(bucket_name, file_key):
    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket=bucket_name, Key=file_key)
    content = obj['Body'].read()
    file_hash = hashlib.sha256(content).hexdigest()
    return file_hash

def check_for_duplicates(bucket_name, folder_path):
    files = list_files_in_folder(bucket_name, folder_path)
    file_metadata = {}
    duplicate_files = []

    for file_key in files:
        metadata = download_metadata(bucket_name, file_key)
        file_hash = calculate_file_hash(bucket_name, file_key)

        if (metadata['size'], metadata['last_modified'], file_hash) in file_metadata.values():
            duplicate_files.append(file_key)
        else:
            file_metadata[file_key] = (metadata['size'], metadata['last_modified'], file_hash)

    return duplicate_files

def main():
    parser = argparse.ArgumentParser(
        description="Report duplicate files."
    )
    parser.add_argument("folder", type=Path, help="Directory to search")
    args = parser.parse_args()

    folder = Path(args.folder)
    # Example usage
    bucket_name = 'your-bucket-name'
    folder_path = 'your-folder-path'
    duplicates = check_for_duplicates(bucket_name, folder_path)
    print("Duplicate files:", duplicates)

if __name__ == "__main__":
    main()