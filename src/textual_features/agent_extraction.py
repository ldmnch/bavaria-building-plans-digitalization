import os
import logging
import sys
import os.path

from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    PromptTemplate,
    StorageContext,
    load_index_from_storage,
    Settings
)

from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.core import PromptTemplate

logging.basicConfig(stream=sys.stdout, level=logging.INFO) # logging.DEBUG for more verbose output
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

def load_models(AZURE_OPENAI_ENDPOINT : str, 
                AZURE_OPENAI_API_KEY : str): 
    
    os.environ["AZURE_OPENAI_API_KEY"] = AZURE_OPENAI_API_KEY
    os.environ["AZURE_OPENAI_ENDPOINT"] = AZURE_OPENAI_ENDPOINT

    embed_model = AzureOpenAIEmbedding(
        model="text-embedding-ada-002",
        deployment_name="text-embedding-ada-002",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2023-07-01-preview"
    )


    llm = AzureOpenAI(
        engine="gpt-35-turbo-1106", model="gpt-35-turbo-16k", temperature=0.0,
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2023-07-01-preview"
    )

    Settings.llm = llm
    Settings.embed_model = embed_model

def load_data(input_folder_path : str):

    documents = SimpleDirectoryReader(input_folder_path).load_data()

    index = VectorStoreIndex.from_documents(documents)
    
    return(index)