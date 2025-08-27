import openai
import io
import pandas as pd
import tqdm

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

def create_vs(name):
    vector_store = client.vector_stores.create(
        name=name
    )
    return vector_store.id
# Create the vector store

def make_file_object(name,content):
    return (name+'.txt', io.BytesIO(content.encode('utf-8')), 'text/markdown')
# Important to encode as bytes and add '.txt' to filename to trick API that this is a file

def push_file_to_cloud(name, content):
    result = client.files.create(file = make_file_object(name, content), purpose = 'assistants') 
    return result.id

def add_file_to_db(file_id, vs_id, attributes = {}):
    result = client.vector_stores.files.create(
        vector_store_id=vs_id,
        file_id=file_id,
        attributes=attributes
    )
    return result
# Then add it to the vector store with attributes

def get_all_vs():
    for f in client.vector_stores.list():
        yield f
# Get all vector stores

def delete_all_files():
    for f in tqdm.tqdm(client.files.list()):
        #print(f.id)

        res = client.files.delete(f.id)
        
        if not res.deleted:
            tqdm.tqdm.write(f"Failed to delete file {f.id}")
            
def delete_all_files():

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