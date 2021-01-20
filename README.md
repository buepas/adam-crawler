# ADAM-CRAWL
## Requirements / Dependencies
- [pip](https://pypi.org/project/pip/)
- [python3.8](https://www.python.org/downloads/release/python-380/)
- [virtualenv](https://pypi.org/project/virtualenv/)
##  Setup
1. Clone the repository:

   `git clone git@github.com:buepas/adam-crawler.git`

2. Clone the repository:

   `cd ./adam-crawler/`

3. Install dependencies:
   Make sure [pip](https://pypi.org/project/pip/) and [python3.8](https://www.python.org/downloads/release/python-380/) are installed
   
   `pip3 install -r requirements.txt`

4. Setup virtualenv:

    `python3 -m venv venv`
    
    and enable it  
    
    `source venv/bin/activate`


5. Change permission of the script to make it executable:
   
   `chmod +x adam-crawl.py`

##  Usage
1. Options:
    ```
    Usage:
            adam-crawl.py -u -p [-b] [-m a,v,p]
    Required: 
            -u --user=<e-mail>                                       The UniBas e-mail address.
            -p --password=<passwd>                           The eduID password.
    Optional: 
            -b --base-url<adam.unibas.ch/...>        The base-url of the crawled lecture.
            -m a,v,p --mode=a,v,p                            Decides wether to crawl [a]ll, [v]ideos or [p]dfs only.
            -h --help                                Prints this information.
    ```
 2. More infos:
    
    This script generates a html page that contains all download links for lecture-specific data.
    Use the base-url of a lecture in ADAM e.g. `https://adam.unibas.ch/goto_adam_crs_910690.html` 
    for the Scientific-Computing lecture
    
## TODOs
- Exercise Support
- Automated Download
- ...