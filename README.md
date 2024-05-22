E-Periodica DOI checker
=========================

Project Description
--------------------------

The prototype aims to find full-text links for articles published in journals that are digitized in E-Periodica (https://www.e-periodica.ch/). These articles are already indexed in a repository, but their metadata entries lack a link to a freely available full-text or a full-text attachment. 
The search via the API is based on data from the library system ALMA (comparison between the repository data and the journals indexed in E-Periodica based on the ISSN) and the repository (name of the author, title of the article, year of publication, title of the journal in which the article is published).

The result is a list of bibliographic metadata that facilitates the inclusion of full-text links as DOIs to a freely accessible PDF of an article in repositories. ZHAW counts these linked articles as "green elsewhere" in the Swiss Open Access monitor (repository monitor, https://oamonitor.ch/charts-data/repository-monitor/)



How to Install and Run the Projects
--------------------------

_Before running the scripts, follow these steps:_

- Check the configuration (config.ini) and adjust the file according to your needs.

These variables should be changed in any case:

[Repository]

- file_repository
- repository_issn 
- title 
- delimiter_title
- author 
- delimiter_author 
- issue
- volume
- date
- repository_journal
- page_start
- page_end
- record_uri


[Alma]

- file_alma
- alma_issn

[API]

- Add your API key for the ETH Discovery API

Further preparation
- Prepare an export of repository data (metadata for articles) and Alma data (metadata for journals indexed in E-Periodica) as a basis for the API query.
- The download of the journal list of the E-Periodica collection in Alma was done manually (export all electronic portfolios in the network zone matching the search for the term "e-periodica" and export them as Excel file).
- The script works with relative file paths and the given folder structure to save the results as CSV and Excel. This can be changed if necessary.
- The ISSNs of the journals in the Alma collection E-Periodica should be stored in an Excel file. The column where the ISSNs are stored should contain only one ISSN per cell.
- API keys are free of charge, please register yourself at https://developer.library.ethz.ch/accounts/create to receive your key.


_Prerequisites_

- Python 3.11.7

**additional packages**

- requests (version 2.31.0)
- pandas (version 2.2.2)
- tqdm (version 4.66.2)

**Limitations**

The ETH Library is a provider of digitized journals in E_Periodica. It owns no copyrights of the journals and is not responsible for their content. The rights generally lie with the publishers. Inserting links on E-Periodica pages is possible at any time and indeed desired.
To minimize false positives, the script combines four different search parameters (author name, main title of article, part of journal title, year of publication). This narrow search approach may result in existing texts not being found in E-Periodica, as individual search parameters for the API query (spelling of the journal title, spelling of the authors' names, year, etc.) differ slightly between E-Periodica and the repository. To broaden the search, it is possible to search with fewer parameters (e.g. without year or journal title), at least for articles published in a journal that is definitely indexed in E-Periodica (parameter ISSN match between repository data and Alma data of the E-Periodica collection is true). 


**Sources**

- ETH documentation of their Discovery API: https://eth-library.github.io/apiplatform-swagger/discovery/v1/
- E-Periodica platform: https://www.e-periodica.ch/


**Contributing**

Feel free to contribute by opening pull requests or reporting issues.
