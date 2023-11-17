import sys
import argparse
import scap_documentation
from langchain.llms import OpenAI
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

texts = [ \
        Document(page_content="All filters have several common features as listed below:\
UI in the Treeview\
In the UI you can change the name of a filter by double-clicking its name (here Erosion - Wide Flows). Additionally, you can change the type of a filter to any other of World Creators filters by pressing the arrows to the right of the name.\
Distributions\
Every filter allows you to add distributions to them. For further information on the distribution system, please refer to this article.\
Parameters\
All filters provide the following options in common:\
Level Step Strengths\
Controls the strength of the filter on each level step.\
Presets\
Select any preset available for this filter in the preset library.\
Sediment Modification - Experimental\
Allows the filter to function on the sediment layer.\
Rock Modification - Experimental\
Allows the filter to function on standard terrain (everything that is not sediment).\
General Strength\
Controls the overall strength of the filter.\
Combine Operation\
Allows control of the parts of the result which will blend into\
the terrain.\
- All blends both lower and higher sections into the terrain.\
- Min blends modified sections lower than the pre-filtered terrain.\
- Max blends modified sections higher than the pre-filtered terrain.\
Invert\
Inverts the effect of the filter on the terrain"),\
        Document(page_content="The Add/Set filter allows you to adjust the terrain by either setting it to a fixed height or adding or subtracting from the height of the terrain.\
Parameters\
Add\
Switches between Set and Add mode.\
Height Offset\
Either the height to which the terrain will be set or the amount of height added to the terrain."),\
        Document(page_content="The Zero Edge filter sets the height of the edges of the terrain on the applied step to zero. By default, it is only applied on a lower level so you might have to take a look at the level step strengths to get your desired output.\
Note that this filter operates based on a pixel distance, therefore lower levels will result in longer travel distances on the terrain, whereas higher levels will produce shorter smoothing distances.\
Parameters\
Smoothness\
The range of the zero edge effect"),\
        Document(page_content="The Border Blend filter smoothly interpolates the terrain to a given border height over a custom blend distance.\
Parameters\
Height Offset\
The height of the border.\
Blend Range\
Controls how much the blend will use from the Blend Distance.\
Blend Distance\
The maximum distance of the blend on the terrain."),\
        Document(page_content="The Flatten filter allows you to flatten the terrain on a specified level completely.\
Parameters\
Flatten Anchor\
Shifts the height of the terrain.\
Flatten Strength\
The strength of the flatten effect."),\
        Document(page_content="The Voronoi filter applies a Voronoi effect to your landscape.\
Parameters\
Seed\
The seed of the Voronoi noise.\
Cell Size\
Scale the Voronoi to increase or decrease their size.\
Cell Height\
The height scale of the edges of the Voronoi cells.\
Distance Scale\
The maximum distance of a cell. Lower values will lead to more circular cells.\
Mode\
Specifies which part of the Voronoi cells are blended into the terrain.\
Falloff\
Defines the calculation method for the distance between the center and borders of a cell.\
Height from Center\
Uses the height from the center in the distance calculation."),\
        Document(page_content="The Curve filter enables custom modification of the terrain's altitude using a spline base curve. It works by mapping the height of the terrain to a curve which can then be modified.\
Parameters:\
Curve: Build a curve to be applied to the terrain. Use 2x LMB to add a new control point and RMB on a point to delete it.\
Source Range: Set the minimum and maximum height values taken from the terrain. The minimum value corresponds to the 0 point on the graph, and the maximum value corresponds to the 1 point on the graph.\
Typically, you will want the minimum and maximum values of your terrain (displayed below the height meter on the left) to fall within your source range.\
Destination Range: Sets the outcoming height of the 0 and 1 points of the graph."),\
        Document(page_content="The Cutoff filter produces a planar cut at the specified range values. For a smoother outcome, apply it on multiple levels, but if you prefer a sharper intersection, restrict its usage to the higher levels.\
Parameters\
Range\
The lower and upper cutoff values."),\
        Document(page_content="The Blocks filter converts the terrain into a collection of square blocks. It provides choices for block dimensions and, based on the level you select, various degrees of blending between them.\
Parameters\
BlockSize\
Determines the scale of the block effect. Remember that the level at which it is applied also affects its size."),\
        Document(page_content="The Smooth Ridge filter enables you to smoothen the sharp ridges of your terrain. Depending on the level it operates on, it can either smooth out small ridges or even larger hills or mountains on lower levels.\
Parameters\
Length\
Adjust the smoothing effect radius for every ridge.")\
        ]

CONNECTION_STRING = "postgresql+psycopg2://postgres:test@localhost:5432/vector_db"
COLLECTION_NAME = 'testcollection'

def add_test_data_to_db(doc_texts):
    load_dotenv()
    embeddings = OpenAIEmbeddings()
    
    CONNECTION_STRING = "postgresql+psycopg2://postgres:test@localhost:5432/vector_db"
    COLLECTION_NAME = 'testcollection'

    db = PGVector.from_documents(embedding=embeddings, documents=doc_texts, collection_name=COLLECTION_NAME, connection_string=CONNECTION_STRING)

def test_search(query, nk, bPrint):
    # query = "how des the curve filter work?"
    load_dotenv()
    embeddings = OpenAIEmbeddings()
    db = PGVector(embedding_function=embeddings, collection_name=COLLECTION_NAME, connection_string=CONNECTION_STRING)
    similar = db.similarity_search_with_score(query, k=nk)
    if bPrint:
        print(similar)
    return similar

def test_prompting(query, similar):
    llm = OpenAI()
    template = """Question: {question}\
\
Answer: Let's think step by step."""\

    prompt = PromptTemplate(template=template, input_variables=["question"])
    question = "you are a support agend for the software World creator. "
    for tmp in similar:
        question += tmp[0].page_content
    question += query
    llm_chain = LLMChain(prompt=prompt, llm=llm)
    answere = llm_chain.run(question)
    print(answere)

if __name__ == "__main__":
    nk = 2
    if args.number is not None:
        nk = args.number
    if args.search is None:
        similar = test_search(args.prompt, nk, False)
        test_prompting(args.prompt, similar)
    else:
        test_search(args.prompt, nk, True)
    #doc_texts = []
    #texts_list = scap_documentation.extract_documentation()
    #for text in texts_list:
    #    doc_texts.append(Document(page_content=text))
    #add_test_data_to_db(doc_texts)

