"""
    This file is part of the  E-Periodica DOI checker package.
    (c) ZHAW HSB <apps.hsb@zhaw.ch>

    For the full copyright and license information, please view the LICENSE
    file that was distributed with this source code.
"""
# Import standard python library package
import configparser
import urllib.parse 

# Import additional packages
import pandas as pd
import requests
from tqdm import tqdm


# Read config.ini and get values
config = configparser.ConfigParser()
config.read("config.ini", "UTF-8")
filepath_repository = config.get("Repository", "path")
file_repository = config.get("Repository", "file_repository")
repository_issn = config.get("Repository", "repository_issn")
title = config.get("Repository", "title")
delimiter_title = config.get("Repository", "delimiter_title")
file_csv = config.get("Repository", "file_csv")
file_xlsx = config.get("Repository", "file_xlsx")
author = config.get("Repository", "author")
delimiter_author = config.get("Repository", "delimiter_author")
issue = config.get("Repository", "issue")
volume = config.get("Repository", "volume")
date = config.get("Repository", "date")
repository_journal = config.get("Repository", "repository_journal")
page_start = config.get("Repository", "page_start")
page_end = config.get("Repository", "page_end")
record_uri = config.get("Repository", "record_uri")
filepath_alma = config.get("Alma", "path")
file_alma = config.get("Alma", "file_alma")
alma_issn = config.get("Alma", "alma_issn")

apikey = config.get("API", "apikey")

# Open csv file with bibliographic metadata of articles
df_repository = pd.read_csv(f"{filepath_repository}{file_repository}", 
                            usecols=[
                                title, 
                                author, 
                                issue, 
                                volume, 
                                page_start, 
                                page_end, 
                                date, 
                                repository_journal, 
                                repository_issn, 
                                record_uri
                                ])

# Open excel with bibliographic metadata of journals in E-Periodica
df_alma = pd.read_excel(f"{filepath_alma}{file_alma}", 
                        usecols = [alma_issn])

filtered_df_alma = df_alma[df_alma[alma_issn].notnull()]

# compare if ISSN of found article matches online ISSN in CSAL lists and add result in new column
unique_issn = filtered_df_alma[alma_issn].unique()
df_repository["issn_match"] = df_repository[repository_issn].str.contains("|".join(unique_issn))

# Add a column with a link for the manual search of the respective article in the E-Periodica database
df_repository["manual_search"] = ("https://www.e-periodica.ch/digbib/dossearch?ssearchtext="
    # Last name of first author
    + df_repository[author].str.split(delimiter_author).str[0]
    + "+\""         
    # Main title of article
    + df_repository[title].str.split(delimiter_title).str[0]
    + "\"+" 
    # publication year
    + df_repository[date].astype(str) 
    + "+&facet="
    )

# Create a column with the search query for ETH Discovery API with title of article, last name of first author, journal name, and year.
df_repository["api_request_with_year"] = (
    "https://api.library.ethz.ch/discovery/v1/resources?q=title,contains,\""
    # Main title of article
    + df_repository[title].str.split(delimiter_title).str[0].apply(urllib.parse.quote) 
    + "\",AND;creator,contains,"
     # Last name of first author
    + df_repository[author].str.split(delimiter_author).str[0]
    # Main title of article
    + ",AND;any,contains,"
    + df_repository[repository_journal].str.split(delimiter_title).str[0].apply(urllib.parse.quote)
    + ",AND;any,contains,"
    # publication year
    + df_repository[date].astype(str) 
    + "&sort=rank&limit=1&qInclude=facet_data_source,exact,ETH_Eperiodica&apikey="
    + apikey
    )

# Create a column with the search query for Discovery API with title of article, last name of first author and journal name.
df_repository["api_request_without_year"] = (
    "https://api.library.ethz.ch/discovery/v1/resources?q=title,contains,\""
    # Main title of article
    + df_repository[title].str.split(delimiter_title).str[0].apply(urllib.parse.quote) 
    + "\",AND;creator,contains,"
    # Last name of first author
    + df_repository[author].str.split(delimiter_author).str[0]
    + ",AND;any,contains,"
    # Main title of journal
    + df_repository[repository_journal].str.split(delimiter_title).str[0].apply(urllib.parse.quote)
    + "&sort=rank&limit=1&qInclude=facet_data_source,exact,ETH_Eperiodica&apikey="
    + apikey
    )

def return_json(URL):
    """Check if request for ETH Discovery API with URL is working and return resultpage as json"""
    request = requests.get(URL, timeout=15)
    try: 
        request.raise_for_status()
        
    except requests.exceptions.HTTPError as error:
        return f"HTTP Error for {URL}"
    except requests.exceptions.ReadTimeout as error: 
        return f"Time out for {URL}"
    except requests.exceptions.ConnectionError as error: 
        return f"Connection error for {URL}"
    except requests.exceptions.RequestException as error: 
        return f"Exception request for {URL}"
    
    page_with_result = request.json()
    return page_with_result

def get_DOI(docs):
    """For each API result in json (docs) return json element "identifier" and extract DOI"""
    for doc in docs:
        try:
            doi_metadata = doc.get("pnx", {}).get("display", {}).get("identifier")
            doi = doi_metadata[0].replace("$$Cdcidentifier$$V<b>DOI:</b> ", "")
            doi_EPeriodica = doi
            doi_EPeriodica_link = f"https://doi.org/{doi}"
        except Exception:
            doi_EPeriodica = f"error occured for DOI of request"
            doi_EPeriodica_link = "no link"
            return doi_EPeriodica, doi_EPeriodica_link
        return doi_EPeriodica, doi_EPeriodica_link
         


# set request for ETH discovery API
for row in tqdm(range(len(df_repository))):

    URL = df_repository.at[row,"api_request_with_year"]
     
    # loop through result (JSON) and write selected doi element in dataframe
    docs = return_json(URL)["docs"]
    if docs:
        df_repository.at[row, "doi_EPeriodica"] = get_DOI(docs)[0]
        df_repository.at[row, "doi_EPeriodica_link"] = get_DOI(docs)[1]
 
    elif df_repository.at[row, "issn_match"] == True:
        URL = df_repository.at[row,"api_request_without_year"]

        # loop through result and write selected doi element in dataframe
        docs = return_json(URL)["docs"]
        if docs:
            df_repository.at[row, "doi_EPeriodica"] = get_DOI(docs)[0]
            df_repository.at[row, "doi_EPeriodica_link"] = get_DOI(docs)[1]
        else:
            df_repository.at[row, "doi_EPeriodica"] = "No DOI found, but article is likely to be indexed."   
            df_repository.at[row, "doi_EPeriodica_link"] = "no link"
        
    else:
        df_repository.at[row, "doi_EPeriodica"] = "No DOI found"
        df_repository.at[row, "doi_EPeriodica_link"] = "no link"

# Save the output as CSV
df_repository.to_csv(f"{filepath_repository}{file_csv}", index=False, encoding="utf-8")
print(f"{file_csv} saved in path: {filepath_repository}")

# Save the output as Excel
df_repository.to_excel(f"{filepath_repository}{file_xlsx}", index=False)
print(f"{file_xlsx} saved in path: {filepath_repository}")