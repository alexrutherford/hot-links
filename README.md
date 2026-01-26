# hot-links

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

This is a Python project evaluating LLMs ability to automatically generate document hyperlinks using Guardian news articles as an exemplar.  

## Problem Statement

Links within documents such as news articles are important for the reader, they provide more relevant information, and the publisher, they encourage more engagement. However, links should be inserted carefully; too many will overwhelm and the links should be relevant to be valuable. Wikipedia even has a [style guide](https://en.wikipedia.org/wiki/Wikipedia:Manual_of_Style/Linking) for contributors to follow. You could even imagine that these links could be customised for each reader, forming a kind of content recommendation system.

![News article excerpt showing hyperlink](assets/hyperlink_example.png "An example hyperlink" )

## Formulation

However it is time consuming to embed these as part of the editorial process. It seems natural that an LLM could help to automate this. Formally the problem is stated as

For a given document $D$ there are a set of tuples of the form $(\textrm{text}, \textrm{link})$. There are several distinct tasks given a document $D$ in loosely increasing order of complexity

1. Given a link to another document $\mathrm{link}$ find the optimal $\mathrm{text}$ in $D$ to place the hyperlink. 
2. Given a $\mathrm{text}$ in $D$ find the optimal link to another document $\mathrm{link}$. 
3. Find the full set of substrings and corresponding links $\{(\mathrm{text},\mathrm{link})\}$

This can be done through a combination of semantic search in a vector DB and LLM inference using file retrieval as a tool. This can be evaluated by masking either the substring or the link or both in a known article and determining if the substring or link can be inferred. 

There are some cavets such as only searching for articles that were published the same day or before the focal article. Also external links are ignored for now. It is also necessary to do a snowball sample in the absence of a full database of articles to retreive from.

## High level steps

Ideally, one would have access to a comprehensive database of articles to select appropriate links from. However I do not have that. So a corpus of articles must be developed. This need not be comprehensive i.e. all Guardian articles ever, but should (i) include the true article and (ii) should be of reasonable size to demonstrate the efficacy of the retrieval method.

Firstly a set of seed articles is defined, using a dataset from Kaggle (the Official Guardian API doesn't seem stable enough to retrieve). The seed articles are placed in a vector store and links are substrings are extracted and stored in a flat file. The out-links from all seed articles are de-duplicated and the HTML content derived via (responsible) scraping. The body text and second generation out-links are extracted from this HTML. The body text is placed in the vector store and the links are also stored in a flat file. This process could contiue indefinitely, navigating the document link network. However it is expensive and not necessary for demonstrating the concept.

Secondly....

## Initial Results

This is for retrieving links given a document and text snippets (formulation 2 above). Based on 50 random seed articles being tested, see [04_evals.ipynb](notebooks/04_evals.ipynb). Comparing different strategies.

### Naive Vector Search using entire seed document as search query

_Return ranked matches to \<document.contents\>_

23 articles have no link matches (46.00%).  
49 links found out of 99 (49.49%).  
Median rank is 5.0.  

### Naive Vector Search using entire seed document as search query + 14 time window

_Return ranked matches to \<document.contents\> within 14 days before \<document.date\>_

26 articles have no link matches (52.00%).  
48 links found out of 99 (48.48%).  
Median rank is 4.0.  

### Searching for each link snippet individually

_I want to add a link at this point
\<link.snippet\> \
in the article below. Which document would be best?
\<document.contents\>_

Out of 50 articles and 118 total links (2.36 av.).  
45 links not found (38.14%).  
Median rank is 2.0 (mean rank is 3.07).  
Mean score for zero ranked matches is 0.60.  

### Searching for each link snippet individually + 14 time window

_I want to add a link at this point
\<link.snippet\> \
in the article below. Which document would be best out of those within 14 days before \<document.date\>?
\<document.contents\>_

Out of 50 articles and 89 total links (1.78 av.).   
43 links not found (48.31%).  
Median rank is 1.0 (mean rank is 2.07).  
21 matches were at rank 0 (23.6% of all links).  
Mean score for zero ranked matches is 0.60.  

## Model Comparison

![Mean overlap of generated text](reports/figures/overlap_by_model.png "Compare models" )
![Mean separation of generated text from real snippet](reports/figures/separation_by_model.png "Compare models" )

## Things to do

- ~~Scrape a few recent articles to build up a validation set~~
- ~~Persist to interim data file~~
- Check to see how many links are external (FYI)
- ~~Check to see if there are Guardian articles that are not in the dataset~~
- ~~Do a snowball sample until some reasonable place to stop~~
- ~~Set up vector DB with date as meta-data~~
- Look for alternative vector stores (OpenAI has 12k doc limit and 4096 char query limit)
- Investigate chunking strategies for db
- ~~Set up LLM prompt to try to guess article to link to from text snippet~~
- ~~Set up evaluation~~
- How to set up batches (seems [not available](https://platform.openai.com/docs/api-reference/batch/create) to `vector_store.search` endpoint)
- Experiment with models, prompts, sampling
- Compare to supervised fine-tuning
- Implement prompt cahcing: move static content i.e. document contents to beginning of prompt

## Project Organization

```
├── LICENSE            <- Open-source license if one is chosen
├── Makefile           <- Makefile with convenience commands like `make data` or `make train`
├── README.md          <- The top-level README for developers using this project.
├── data
│   ├── external       <- Data from third party sources.
│   ├── interim        <- Intermediate data that has been transformed.
│   ├── processed      <- The final, canonical data sets for modeling.
│   └── raw            <- The original, immutable data dump.
│
├── docs               <- A default mkdocs project; see www.mkdocs.org for details
│
├── models             <- Trained and serialized models, model predictions, or model summaries
│
├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `1.0-jqp-initial-data-exploration`.
│
├── pyproject.toml     <- Project configuration file with package metadata for 
│                         hot_links and configuration for tools like black
│
├── references         <- Data dictionaries, manuals, and all other explanatory materials.
│
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting
│
├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `pip freeze > requirements.txt`
│
├── setup.cfg          <- Configuration file for flake8
│
└── hot_links   <- Source code for use in this project.
    │
    ├── __init__.py             <- Makes hot_links a Python module
    │
    ├── config.py               <- Store useful variables and configuration
    │
    ├── dataset.py              <- Scripts to download or generate data
    │
    ├── features.py             <- Code to create features for modeling
    │
    ├── modeling                
    │   ├── __init__.py 
    │   ├── predict.py          <- Code to run model inference with trained models          
    │   └── train.py            <- Code to train models
    │
    └── plots.py                <- Code to create visualizations
```

--------

## Kaggle Authentication

Requires Kaggle [key](https://www.kaggle.com/docs/api#authentication) to be exported to environment to access data.

## OpenAI Authentication

Requires an [OpenAI API key](https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety) to be exported to environment

## Setup

1. Create empty directory (hot-links) in this case
2. Run ccds in directory
3. Create empty Git repo
4. Push entire directory into repo
5. Creat empty Codepsace from repo
6. Create venv in VS Code from requirements.txt



[def]: 04_evals