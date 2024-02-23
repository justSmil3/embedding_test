from llama_index import SimpleDirectoryReader, StorageContext
from llama_index.indices.vector_store import VectorStoreIndex
from llama_index.vector_stores import PGVectorStore
from sqlalchemy import make_url
import psycopg2
from dotenv import load_dotenv
import openai
import textwrap
import scap_documentation
from llama_index import download_loader
from llama_index.tools import QueryEngineTool, ToolMetadata
from llama_index.agent import OpenAIAgent
import sys

load_dotenv()
connection_string = "postgresql://postgres:12345678@database-1.chqako4u4sgl.eu-central-1.rds.amazonaws.com:5432"
db_name = "vector_db"
conn = psycopg2.connect(connection_string)
conn.autocommit = True

#texts_list = scap_documentation.extract_documentation()
#StringIterableReader = download_loader("StringIterableReader")
#loader = StringIterableReader()
#documents = loader.load_data(texts=texts_list)

url = make_url(connection_string)
vec_store = PGVectorStore.from_params(database = db_name,
                                      host=url.host,
                                      password=url.password,
                                      port=url.port,
                                      user=url.username,
                                      table_name="llama_pg_embedding",
                                      embed_dim=1536)
#storage_context = StorageContext.from_defaults(vector_store=vec_store)
#index = VectorStoreIndex.from_documents(documents, storage_context=storage_context, show_progress = True)

index = VectorStoreIndex.from_vector_store(vector_store=vec_store)
qengine = index.as_query_engine()
tools = [QueryEngineTool(
    query_engine=qengine,
    metadata = ToolMetadata(
        name="query_engine",
        description="usefull for when you want to answer queries that require analysing documents for worldcreator"
        )
    )]

#agent = OpenAIAgent.from_tools(tools, verbose = True)
agent = index.as_chat_engine()


role = "you are a support agent for the software world creator. awnswere just with what is possible in the given knowledge base"
agent.chat(role)
#response = agent.chat("hi, I am an idiot")
#print(str(response))
#response = agent.chat("how does the canyon filter work")
#print(str(response))
#response = agent.chat("can you give me an example?")
#print(str(response))
#response = agent.stream_chat("can you give me an example to create a terrian that resembles the alps?")
#for token in response.response_gen:
#    print(token, end="")
print("ready")
while True: 
    data = input()
    if data:
        print("\n")
        response = agent.stream_chat(role + " " + str(data))
        for token in response.response_gen:
            print(token, end="")
        data = None
        print("\n")
#response = qengine.query("how do I build a chatbot using llamaindex")
#print(textwrap.fill(str(response), 100))
