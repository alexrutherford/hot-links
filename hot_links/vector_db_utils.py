import openai
import io
import pandas as pd
import tqdm
import logging

from openai import OpenAI
from dotenv import load_dotenv
from collections.abc import Iterator

logging.basicConfig(filename='out.log', filemode='a', level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

try:
    client = OpenAI()
    logger.info("Successfully created OpenAI client.")
except:
    logger.error("Failed to create OpenAI client.")
################################################################

def get_files_in_db(vector_store_id: str) -> Iterator[int]:
    '''Return an iterator of all files in a vector DB'''
    for f in client.vector_stores.files.list(vector_store_id=vector_store_id):
        yield f

####
def create_vs(name: str):
    '''Create a vector DB'''
    vector_store = client.vector_stores.create(
        name=name
    )
    return vector_store.id
# Create the vector store

####
def make_file_object(name,content):
    '''Creates an OpenAI file object and returns it'''
    return (name+'.txt', io.BytesIO(str(content).encode('utf-8')), 'text/markdown')
# Important to encode as bytes and add '.txt' to filename to trick API that this is a file

####
def push_file_to_cloud(name, content):
    '''Creates a file object and puts in cloud storage'''
    result = client.files.create(file = make_file_object(name, content), purpose = 'assistants') 
    return result.id

####
def add_file_to_db(file_id, vs_id, attributes = {}):
    '''Puts a file object, previously uploaded, into a vector DB'''
    result = client.vector_stores.files.create(
        vector_store_id=vs_id,
        file_id=file_id,
        attributes=attributes
    )
    return result
# Then add it to the vector store with attributes

####
def get_all_vs():
    '''Returns an iterator over all vector stores'''
    for f in client.vector_stores.list():
        yield f
# Get all vector stores

def get_all_files():
    '''Returns an iterator over all files'''
    for f in client.files.list():
        yield f
        

            
def delete_all_files():
    '''Deletes all files in the cloud, asks for confirmation'''
    confirmation = input("Type 'DELETE' to confirm deletion of all files: ")

    if confirmation != "DELETE":
        print("Deletion cancelled.")
        return

    for f in tqdm.tqdm(client.files.list()):
        #print(f.id)

        res = client.files.delete(f.id)
        
        if not res.deleted:
            tqdm.tqdm.write(f"Failed to delete file {f.id}")
            
def convert_date_to_epoch(date):
    return pd.to_datetime(date).value//10**9

def query_db(vector_store_id, query_string, time_stamp):
    response = client.responses.create(
        model="gpt-4.1",
        input=query_string,
        tools=[{
            "type": "file_search",
            "vector_store_ids": [vector_store_id],
            "filters": {
                "type": "lt",
                "key": "time",
                "value": time_stamp
            }
        }]
    )
    return response

def search_db(vector_store_id, query):
    results = client.vector_stores.search(
        vector_store_id=vector_store_id,
        query=query,
    )
    return results