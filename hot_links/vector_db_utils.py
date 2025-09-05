'''
Utils for using OpenAI vector store for semantic search and RAG. Follows OpenAI documentation at
https://platform.openai.com/docs/api-reference/responses/create

'''

from typing import Tuple, Any
import openai
import io
import pandas as pd
import tqdm
import datetime
import logging

from openai import OpenAI
from dotenv import load_dotenv
from collections.abc import Iterator
from openai.types import FileObject, ResponseFormatJSONObject, VectorStore
from openai.types.vector_store_search_response import VectorStoreSearchResponse

logging.basicConfig(filename='out.log', filemode='a', level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

default_model ='gpt-4o-mini-2024-07-18'

try:
    client = OpenAI()
    logger.info("Successfully created OpenAI client.")
except:
    logger.error("Failed to create OpenAI client.")
################################################################
def get_vector_store_id(vs_name:str = 'hot_links') -> VectorStore:
    vector_store_id = None

    for vs in get_all_vs():
        # print(vs.id,vs.name)
        
        if vs.name == vs_name:
            vector_store_id = vs.id
    return vector_store_id

def get_files_in_db(vector_store_id: str) -> Iterator[int]:
    '''Return an iterator of all files in a vector DB'''
    for f in client.vector_stores.files.list(vector_store_id=vector_store_id):
        yield f

####
def create_vs(name: str) -> str:
    '''Create a vector DB'''
    vector_store = client.vector_stores.create(
        name=name
    )
    return vector_store.id
# Create the vector store

####
def make_file_object(name: str, content: str) -> Tuple[str, io.BytesIO, str]:
    '''Creates an OpenAI file object and returns it'''
    return (name+'.txt', io.BytesIO(str(content).encode('utf-8')), 'text/markdown')
# Important to encode as bytes and add '.txt' to filename to trick API that this is a file

####
def push_file_to_cloud(name: str, content: str) -> str:
    '''Creates a file object and puts in cloud storage'''
    result = client.files.create(file = make_file_object(name, content), purpose = 'assistants') 
    return result.id

####
def add_file_to_db(file_id: str, vs_id: str, attributes: dict = {}) -> Any:
    '''Puts a file object, previously uploaded, into a vector DB'''
    # TODO add filename of source as additional attribute to filter out
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
        
def delete_vs(vs):
    '''Deletes vector store in the cloud, asks for confirmation'''

    confirmation = input("Type 'DELETE' to confirm deletion of vs: ")

    if confirmation != "DELETE":
        print("Deletion cancelled.")
        return
    
    deleted_vector_store = client.vector_stores.delete(
    vector_store_id=vs)

    print(deleted_vector_store)
            
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
            
def convert_date_to_epoch(date: str):
    return pd.to_datetime(date).value//10**9

def query_db(vector_store_id: str, query_string: str, time_stamp : int = None,model : str = default_model) -> ResponseFormatJSONObject:
    '''Responds to a query performing RAG to augment context from vectore DB files'''
    # TODO add filename of source as additional attribute to filter out
    if time_stamp:
        filters = {
                "type": "lt",
                "key": "time",
                "value": time_stamp
            }
    else:
        filters = {}

    response = client.responses.create(
        model=model,
        input=query_string,
        tools=[{
            "type": "file_search",
            "vector_store_ids": [vector_store_id],
            "filters": filters
        }]
    )
    return response

def search_db(vector_store_id: str, query: str, time_stamp: int = None, name = None) ->Iterator[VectorStoreSearchResponse]:
    '''Does plain vector search returning relevant documents and scores'''
    if time_stamp:
        filters = {
                "type": "lt",
                "key": "date",
                "value": int(time_stamp)
            }
    else:
        filters = None
        
    if name and time_stamp:
        filters = {'type' : 'and', 'filters' : [{
                "type": "lt",
                "key": "date",
                "value": int(time_stamp)},
                    {
                "type": "ne",
                "key": "filename",
                "value": name}]
            }
        
    print('filters',filters)
        
    if filters:
        results = client.vector_stores.search(
        vector_store_id=vector_store_id,
        query=query,
        max_num_results = 30,
        filters=filters
    )
    else:
        
        results = client.vector_stores.search(
        vector_store_id=vector_store_id,
        query=query,
        max_num_results = 30
    )
    return results