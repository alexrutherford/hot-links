# hot-links

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

This is a Python project evaluating LLMs ability to automatically generate document hyperlinks using Guardian news articles as an exemplar.  

Links within documents such as news articles are important for the reader, they provide more relevant information, and the publisher, they encourage more engagement. However, links should be inserted carefully; too many will overwhelm and the links should be relevant to be valuable. Wikipedia even has a [style guide](https://en.wikipedia.org/wiki/Wikipedia:Manual_of_Style/Linking) for contributors to follow. You could even imagine that these links could be customised for each reader, forming a kind of content recommendation system.

![News article excerpt showing hyperlink](assets/hyperlink_example.png "An example hyperlink" )

However it is time consuming to embed these as part of the editorial process. It seems natural that an LLM could help to automate this. Formally the problem is stated as

For a given document $D$ there are a set of tuples of the form $(\textrm{text}, \textrm{link})$. There are several distinct tasks given a document $D$ in loosely increasing order of complexity

1. Given a link to another document $\mathrm{link}$ find the optimal $\mathrm{text}$ in $D$ to place the hyperlink. 
2. Given a $\mathrm{text}$ in $D$ find the optimal link to another document $\mathrm{link}$. 
3. Find the full set of substrings and corresponding links $\{(\mathrm{text},\mathrm{link})\}$



## Things to do

- ~~Scrape a few recent articles to build up a validation set~~
- ~~Persist to interim data file~~
- Check to see how many links are external (FYI)
- ~~Check to see if there are Guardian articles that are not in the dataset~~
- ~~Do a snowball sample until some reasonable place to stop~~
- Set up vector DB with date as meta-data
- Set up LLM prompt to try to guess article to link to from text snippet
- Set up evaluation

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

