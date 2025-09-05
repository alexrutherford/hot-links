import pytest
from data.make_data import *

###################
def test_openai_key_available():

    import dotenv
    dotenv.load_dotenv()
    assert dotenv.dotenv_values().get('OPENAI_API_KEY')
###################
def test_kaggle_credentials_available():
    import json
    
    with open('kaggle.json','r') as f:
        d = json.load(f)
        
    assert d.get('username') and d.get('key')
###################
def test_article_filter():
    url = 'https://www.theguardian.com/politics/2025/sep/03/angela-rayner-battling-for-political-survivial-after-referring-herself-to-ethics-adviser'
    assert is_article(url) and not is_article('https://www.theguardian.com/environment/climate-crisis')

    

'''
- Push file to cloud, remove
- Push file to vs

'''