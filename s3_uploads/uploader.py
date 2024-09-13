import os
import boto3
from botocore.exceptions import NoCredentialsError

def upload_images_to_s3(folder_path, bucket_name, s3_folder=""):
    # Initialize the S3 client
    s3 = boto3.client('s3')
    
    # Iterate through all files in the specified folder
    for filename in os.listdir(folder_path):
        # Only process files that are images (you can add more extensions if needed)
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')):
            file_path = os.path.join(folder_path, filename)
            
            # If you want the images to be organized in a folder in S3, you can specify s3_folder
            s3_key = f"{s3_folder}/{filename}" if s3_folder else filename
            
            try:
                # Upload the file to S3
                s3.upload_file(file_path, bucket_name, s3_key)
                print(f"Uploaded {filename} to {bucket_name}/{s3_key}")
            except FileNotFoundError:
                print(f"The file {file_path} was not found.")
            except NoCredentialsError:
                print("Credentials not available.")

# Example usage
folder_path = '/path/to/your/images'
bucket_name = 'your-s3-bucket-name'
s3_folder = 'optional/s3/folder'  # Leave blank if you don't want a specific S3 folder

upload_images_to_s3(folder_path, bucket_name, s3_folder)

