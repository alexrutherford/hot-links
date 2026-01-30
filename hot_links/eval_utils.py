from vector_db_utils import search_db
import logging
from typing import List, Tuple
from pandas import Series

logging.basicConfig(filename='out.log', filemode='a', level=logging.DEBUG)
logger = logging.getLogger(__name__)

########################################
def get_matches_snippet(vector_store_id:str, test_article:Series, v = False,time_stamp: int = None,window_days: int = None) -> Tuple[List[int],List[float]]:
    '''
    Get matched snippet positions and scores for a test article.
    Args:
        vector_store_id (str): The ID of the vector store to search.
        test_article (Series): The test article containing 'links' and 'bodyContent'.
        v (bool): Verbosity flag.
        time_stamp (int, optional): Timestamp for filtering results.
        window_days (int, optional): Time window in days for filtering results.
    '''
    test_article_links = [d['href']+'.txt' for d in test_article['links']]
    test_article_snippets = [d['link'] for d in test_article['links']]
    
    matched_chunk_positions = []
    matched_chunk_scores = []

    logger.debug('Evaluating article: {:s}'.format(test_article['webUrl']))
    logger.debug('Number of links to find: {:d}'.format(len(test_article_links)))

    for n_test in range(len(test_article_links)):
        if v:print(n_test,test_article_snippets[n_test])
        
        matched_chunk_positions.append(-999)
        matched_chunk_scores.append(-1.0)
        # Placeholder in case not found

        query = 'I want to add a link at this point\n\
        {:s}\n \
        in the article below. Which document would be best?\n\
        {:s}'.format(test_article_snippets[n_test],test_article['bodyContent'][:4096])

        '''
        results = client.vector_stores.search(
        vector_store_id=vector_store_id,
        query=query[:4096],
        max_num_results = 20
        )
        '''
        # TODO replace
        results = search_db(vector_store_id, query[:4096], max_num_results=20, time_stamp=time_stamp, window_days=window_days)

        results =[r for r in results if not r.filename == test_article.webUrl+'.txt']
        # Drop original article from results

        for n,r in enumerate(results):

            if r.filename == test_article_links[n_test]:
                matched_chunk_positions[-1] = n
                matched_chunk_scores[-1] = r.score
                
                if v:
                    print('-----')
                    print('Matched at',n)
                    print('Score: {:.2f}'.format(r.score))
                    print(r.filename)
                    print(test_article_snippets[n_test])
                    print('-----')
                break
                # A different chunk of same file maight be matched, no need to store
    return matched_chunk_positions, matched_chunk_scores
                
                

        
########################################
def get_matched_links(vector_store_id:str, query:str, test_article:Series, v:bool = False, time_stamp: int = None, window_days: int = None) -> Tuple[List[str],List[int],List[float], int]:

    """Get matched links from the vector store based on the test article.
    Args:
        vector_store_id (str): The ID of the vector store to search.
        query (str): The query string to search for.
        test_article (Series): The test article containing 'links' and 'bodyContent'.
        v (bool): Verbosity flag.
        time_stamp (int, optional): Timestamp for filtering results.
        window_days (int, optional): Time window in days for filtering results.
    """
    name = test_article['webUrl']+'txt'
    name = None
    results = search_db(vector_store_id, query, max_num_results=20, time_stamp=time_stamp, name=name, window_days=window_days) 

    test_article_links = [d['href']+'.txt' for d in test_article['links']]
    test_article_snippets = [d['link'] for d in test_article['links']]
    
    results = results.data

    matched_chunk_filenames = []
    matched_chunk_positions = []
    matched_chunk_scores = []

    for n,r in enumerate(results):
        #print(r.filename,r.score)
        
        if r.filename in test_article_links:
            if v:print('Match')
            if v:print(r.filename,r.score)
            if not r.filename in matched_chunk_filenames:
                # Don't duplicate matched chunks
                matched_chunk_filenames.append(r.filename)
                matched_chunk_positions.append(n)
                matched_chunk_scores.append(r.score)
    matched_chunk_filenames = list(set(matched_chunk_filenames))
    if v:print('-------')
    if v:print('Out of {:d} article links, {:d} were returned within the {:d} results (after excluding seed article)'.format(len(test_article_links),len(matched_chunk_filenames),len(results)))

    return matched_chunk_filenames,matched_chunk_positions, matched_chunk_scores, len(test_article_links)