import os
from atlassian import Confluence

import nltk
from transformers import GPT2TokenizerFast
tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
import openai
import requests

import numpy as np
import pd
from bs4 import BeautifulSoup


### CONNECT TO CONFLUENCE

def get_url():
    return 'https://elementor.atlassian.net/'

def connect_to_Confluence():
    
    url = get_url()
    username = "ayalah@elementor.com"
    password = "ATATT3xFfGF0nbNeYNdBOOQ9ExTxOQArBG-K7VfV7Te4dtxJY1GKAFPBaxzT_3srrGgeeevVV7ltQjWPvUJXMdVOjTP_lnic-1DRZ9TvgtY-tq1Srz8G0RdJ9GtF-e-zqI8sWZT-e5dTn57Tx1jAjxw9c1OBSDYZAyYWcb83Z_Nw_Kb9LE6ZQPs=B072E913"
    
    confluence = Confluence(
        url=url,
        username=username,
        password=password,
        cloud=True)
    
    return confluence

### RETRIEVE CHILDREN PAGES UNDER SPECIFIC PAGE

# Connect to Confluence
confluence = connect_to_Confluence()

def get_all_pages(confluence, space='NKB'):
    keep_going = True
    start = 0
    limit = 100
    pages = []
    while keep_going:
        results = confluence.get_all_pages_from_space(space, start=start, limit=100, status=None, expand='body.storage', content_type='page')
        pages.extend(results)
        if len(results) < limit:
            keep_going = False
        else:
            start = start + limit

    return pages

# Call the function to get the list of pages
all_pages = get_all_pages(confluence)


# Iterate over the pages and print them
for page in all_pages:
    print(page)



'''
def get_child_pages(confluence, parent_id):
    parent_page = confluence.get_page_by_id(parent_id, expand='children.page')
    child_pages = parent_page['children']['page']['results'] if 'children' in parent_page else []
    return child_pages

# Retrieve child pages
parent_page_id = '585564222'

child_pages = get_child_pages(confluence, parent_page_id)
'''

#### SETUP OPENAI ENDPOINT AND KEY, RETRIEVE LIST OF MODELS

API_KEY = '8ef6f79ff84c42f0944d0961f2394cf2'
RESOURCE_ENDPOINT = 'https://ai-stg.openai.azure.com/' 

openai.api_type = "azure"
openai.api_key = API_KEY
openai.api_base = RESOURCE_ENDPOINT
openai.api_version = "2023-03-15-preview"

url = openai.api_base + "/openai/deployments?api-version=2023-03-15-preview" 

r = requests.get(url, headers={"api-key": API_KEY})

print(r.text)

