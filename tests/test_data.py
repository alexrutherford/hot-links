import pytest


def test_code_is_tested():
    assert False

def openai_key_available():

    import dotenv
    dotenv.load_dotenv()
    assert dotenv.dotenv_values().get('OPENAI_API_KEY')
    
'''
- Push file to cloud, remove
- Push file to vs

'''