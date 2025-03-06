import os, uuid
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

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

    # Create a unique name for the container
    container_name = str(uuid.uuid4())

    # Create the container
    container_client = blob_service_client.create_container(container_name)

    return blob_service_client

def create_azure_container(blob_service_client, container_name):

    container_client = blob_service_client.create_container(container_name)

    return container_client

def azure_upload_blob(container_client, file_path):

    # Create a blob client using the local file name as the name for the blob
    blob_client = container_client.get_blob_client(os.path.basename(file_path))

    print("\nUploading to Azure Storage as blob:\n\t" + os.path.basename(file_path))

    # Upload the created file
    with open(file_path, "rb") as data:
        blob_client.upload_blob(data)

