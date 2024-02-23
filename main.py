import sys
import os
import argparse
import scap_documentation
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv
from langchain.vectorstores.pgvector import PGVector
from langchain.docstore.document import Document

parser = argparse.ArgumentParser()
parser.add_argument('-s', "--search", nargs='?', const=False)
parser.add_argument('-p', "--prompt")
parser.add_argument('-k', "--number", nargs='?', const=2)
args = parser.parse_args()


CONNECTION_STRING = "postgresql+psycopg2://postgres:test@localhost:5432/vector_db"
COLLECTION_NAME = 'testcollection'

def add_test_data_to_db(doc_texts):
    load_dotenv()
    embeddings = OpenAIEmbeddings()
    
    CONNECTION_STRING = "postgresql+psycopg2://postgres:test@localhost:5432/vector_db"
    COLLECTION_NAME = 'testcollection'

    db = PGVector.from_documents(embedding=embeddings, documents=doc_texts, collection_name=COLLECTION_NAME, connection_string=CONNECTION_STRING)

def add_data():
    load_dotenv()
    embeddings = OpenAIEmbeddings()
    docs = []
    CONNECTION_STRING = "postgresql+psycopg2://postgres:test@localhost:5432/vector_db"
    COLLECTION_NAME = 'testcollection'
    db = PGVector(embedding_function=embeddings, collection_name=COLLECTION_NAME, connection_string=CONNECTION_STRING)
    path = "./../wc_support_awnswers/generated_responses/"
    for file in os.listdir(path):
        with open(path + file, 'r') as text_file: 
            text = text_file.read()
            docs.append(Document(page_content=text))
    db.add_documents(docs)

def test_search(query, nk, bPrint):
    # query = "how des the curve filter work?"
    load_dotenv()
    embeddings = OpenAIEmbeddings()
    db = PGVector(embedding_function=embeddings, collection_name=COLLECTION_NAME, connection_string=CONNECTION_STRING)
    similar = db.similarity_search_with_score(query, k=nk)
    if bPrint:
        for sim in similar:
            print(sim)
            print("\n")
        # print(similar)
    return similar

def test_prompting(query, similar):
    llm = ChatOpenAI(temperature=0, model="gpt-4-0613")
    template = """Question: {question}\
\
Answer: Let's think step by step."""\

    prompt = PromptTemplate(template=template, input_variables=["question"])
    llm_chain = LLMChain(prompt=prompt, llm=llm)
    question = "you are a tech artist, working with the software World Creator. how would you solve the following problem: " + query
    question += query
    considerations = llm_chain.run(question)
    question = "You are a Support agent for the software World Creator. solve the following problem with the help of world creator" + query + "you could consider some of the following poitns as a starting point: " + considerations + ". consider only points that are solvable with the attached information. attached is some specialized information about the software. remember that not all of the additional information is nessesary to corectly awnswer the question."
    similar.extend(test_search(query + considerations, 5, False))
    for tmp in similar:
        question += tmp[0].page_content
    question += query
    #llm_chain = LLMChain(prompt=prompt, llm=llm)    
    answere = llm_chain.run(question)
    print(answere)

if __name__ == "__main__":
    nk = 2
    if args.number is not None:
        nk = args.number
    if args.search is None:
        print("Hey, How can I help you?")
        while True: 
            data = input()
            if data: 
                print("\n")
                similar = test_search(data, nk, False)
                test_prompting(data, similar)
                data = None
                print("\nIs there another thing I can help with?")
        #similar = test_search(args.prompt, nk, False)
        #test_prompting(args.prompt, similar)
    else:
        test_search(args.prompt, nk, True)
    
    #add_data()

    #doc_texts = []
    #texts_list = scap_documentation.extract_documentation()
    #i = 0
    #for text in texts_list:
    #    print(i)
    #    i += 1
    #    doc_texts.append(Document(page_content=text))
    # add_test_data_to_db(doc_texts)

