# pip install langchain --upgrade
# Version: 0.0.164

# !pip install pypdf
# PDF Loaders. If unstructured gives you a hard time, try PyPDFLoader

from langchain.document_loaders import UnstructuredPDFLoader, OnlinePDFLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain.vectorstores import Chroma, Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
import pinecone
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
import openai
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
from slack_bolt import App

from dotenv import load_dotenv
load_dotenv('env_prod.env')

'''
loader = PyPDFLoader("/Users/ayalah/Documents/SAMA_2/NKB-140623-160136.pdf")
data = loader.load()

# Note: If you're using PyPDFLoader then it will split by page for you already
print (f'You have {len(data)} document(s) in your data')
print (f'There are {len(data[30].page_content)} characters in your document')

# Note: If you're using PyPDFLoader then we'll be splitting for the 2nd time.
# This is optional, test out on your own data.

text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=0)
texts = text_splitter.split_documents(data)
print (f'Now you have {len(texts)} documents')
'''
# Check to see if there is an environment variable with you API keys, if not, use what you put below

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'YourAPIKey')
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY', 'YourAPIKey')
PINECONE_API_ENV = os.getenv('PINECONE_API_ENV', 'asia-southeast1-gcp-free') # You may need to switch with your env
SLACK_BOT_TOKEN= os.getenv('SLACK_BOT_TOKEN')
SLACK_APP_TOKEN=os.getenv('SLACK_APP_TOKEN')

app = App(token=SLACK_BOT_TOKEN) 
client = WebClient(SLACK_BOT_TOKEN)

embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

# initialize pinecone
pinecone.init(
    api_key=PINECONE_API_KEY,  # find at app.pinecone.io
    environment=PINECONE_API_ENV  # next to api key in console
)
index_name = "elementorcx-chatbot" # put in the name of your pinecone index here

'''docsearch = Pinecone.from_texts([t.page_content for t in texts], embeddings, index_name=index_name)'''
docsearch = Pinecone.from_existing_index(index_name=index_name, embedding=embeddings)

spliter=1
@app.event("message")
def handle_direct_message(body, logger):
    # Log message 
    print(str(body["event"]["text"]).split(">")[0])

    # Create prompt for ChatGPT
    query = str(body["event"]["text"]).split(">")[0]
    
    # Let thre user know that we are busy with the request 
    response = client.chat_postMessage(channel=body["event"]["channel"], 
                                       thread_ts=body["event"]["event_ts"],
                                       text=f"Hello from your bot! :robot_face: \nThanks for your request, I'm on it!")
    handle_chat_response(query,body)

@app.event("app_mention")   
def handle_message_events(body, logger):
    # Log message 
    print(str(body["event"]["text"]).split(">")[1])

    # Create prompt for ChatGPT
    query = str(body["event"]["text"]).split(">")[1]
    
    # Let thre user know that we are busy with the request 
    response = client.chat_postMessage(channel=body["event"]["channel"], 
                                       thread_ts=body["event"]["event_ts"],
                                       text=f"Hello from your bot! :robot_face: \nThanks for your request, I'm on it!")
    handle_chat_response(query,body)

def handle_chat_response(query,body):
#query = "Everytime when I am trying to add navigation menu to the header , it appers twice in the preview or the final webpage"
    docs = docsearch.similarity_search(query)

    # Here's an example of the first document that was returned
    print(docs[0].page_content[:450])


    llm = OpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)
    chain = load_qa_chain(llm, chain_type="stuff")

    result = chain.run(input_documents=docs, question=query)

    base_query=str(query)+". Get only the one relevant Categorization for this issue in a 'Level 1 > Level 2 > Level 3' format. One line only."
    docs = docsearch.similarity_search(base_query)
    
    categories=chain.run(input_documents=docs,question=base_query)
    print("\n-------------------\n")
    print(result)



    openai.api_key = OPENAI_API_KEY

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt="summarize this for an answer for a customer:" + str(result),
        max_tokens=250,  # Adjust the number of tokens to control the summary length
        temperature=0.3,  # Adjust the temperature to control the randomness of the output
        n=1,  # Generate a single response
        stop=None  # You can specify a stop condition to end the summary at a specific point
    )

    summary = response.choices[0].text.strip()

    client.chat_postMessage(channel=body["event"]["channel"], 
                                       thread_ts=body["event"]["event_ts"],
                                       text=f"*Here is the summary of the issue:* \n {summary}")

    client.chat_postMessage(channel=body["event"]["channel"], 
                                       thread_ts=body["event"]["event_ts"],
                                       text=f"*Here is how to respond to the user:* \n {result}")


    client.chat_postMessage(channel=body["event"]["channel"], 
                                       thread_ts=body["event"]["event_ts"],
                                       text=f"*The relevant Category is:* \n {categories}")    
                                     

    print("Summary:")
    print(summary)


if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()