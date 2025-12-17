from postgres_helper import save_relevant_chunks
from sentence_transformers import SentenceTransformer
import time
import json

local_debug = True

# Define the path to your JSON file (can be absolute or relative)
file_path = '../chunks.json' 

try:
    # Open the file in read mode ('r')
    with open(file_path, 'r') as file:
        # Use json.load() to parse the file contents into a Python dictionary/list
        data = json.load(file)
        
    # You can now work with the data (e.g., print it, access elements)
    print(data)
    print(type(data))

except FileNotFoundError:
    print(f"Error: The file '{file_path}' was not found.")
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from the file '{file_path}'. Check for invalid JSON content.")


# def get_embeddings(recursive_chunks : list) -> list:    
#     embedding_model = SentenceTransformer(model_name_or_path='all-mpnet-base-v2')
#     embeddings = embedding_model.encode(recursive_chunks)
#     embeddings_list = embeddings.tolist()
#     return embeddings_list

# start_time = time.time()
# data_str = "inserted_rows"
# inserted_rows = save_relevant_chunks(recursive_chunks, embeddings_list)
# end_time = time.time()
# elapsed_time = end_time - start_time
# if local_debug :
#     print(f"{data_str} ", inserted_rows)
#     print(f"Elapsed time for {data_str}: {elapsed_time:.4f} seconds which is equal to  {elapsed_time/60:.4f} minutes")

# start_time = time.time()
# data_str = "embeddings_list"
# embeddings_list = get_embeddings(recursive_chunks)
# end_time = time.time()
# elapsed_time = end_time - start_time
# if local_debug :
#     print(f"{data_str} len", len(embeddings_list))
#     print(f"Elapsed time for {data_str}: {elapsed_time:.4f} seconds which is equal to  {elapsed_time/60:.4f} minutes")