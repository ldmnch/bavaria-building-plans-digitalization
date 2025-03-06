import os, uuid
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import ResourceExistsError

# Retrieve the connection string for use with the application. The storage
# connection string is stored in an environment variable on the machine
# running the application called AZURE_STORAGE_CONNECTION_STRING. If the environment variable is
# created after the application is launched in a console or with Visual Studio,
# the shell or application needs to be closed and reloaded to take the
# environment variable into account.

def azure_container_setup():
    connect_str = os.environ['AZURE_STORAGE_CONNECTION_STRING']

    # Create the BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    return blob_service_client

def create_azure_container(blob_service_client, container_name):

    container_name = 'pdfs-'+container_name[-7::] #TODO improve this
    container_name = container_name.replace('_', '-')
    try: 

        container_client = blob_service_client.create_container(container_name)
    
    except ResourceExistsError: 

        container_client = blob_service_client.get_container_client(container= container_name) 


    return container_client

def azure_upload_blob(container_client, folder_path):

    # Create a blob client using the local file name as the name for the blob
    blob_client = container_client.get_blob_client(os.path.basename(folder_path))

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        if os.path.isfile(file_path):  # Make sure it's a file
            blob_client = container_client.get_blob_client(filename)

            print(f"\nUploading {filename} to Azure Storage...")

            with open(file_path, "rb") as data:
                blob_client.upload_blob(data)

    print(f"\nAll files in {folder_path} uploaded successfully.")
