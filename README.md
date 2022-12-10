# ad_clicker

This command-line tool clicks ads for a certain query on Google search using [undetected_chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver) package.

Old version of the tool can be found in the `old_version` branch.

Supports Python 3.9+

[Related post on Medium](https://python.plainenglish.io/google-ads-clicker-with-python-selenium-and-tor-a6ff8078da2a)

## How to setup

Run the following commands in project directory to install required packages.

* `python -m venv env`
* `source env/bin/activate` or `.\env\Scripts\activate` (for Windows)
* `python -m pip install -r requirements.txt`


## How to run

```
usage: python ad_clicker.py [-h] [-q QUERY] [-t AD_VISIT_TIME] [--headless] [-p PROXY] [-pf PROXY_FILE] [--auth]

optional arguments:
  -h, --help                                                       show this help message and exit
  -q QUERY, --query QUERY                                          Search query
  -t AD_VISIT_TIME, --visittime AD_VISIT_TIME                      Number of seconds to wait on the ad page opened
  --headless                                                       Use headless browser
  -p PROXY, --proxy PROXY                                          Use the given proxy in ip:port format
  -pf PROXY_FILE, --proxy_file PROXY_FILE                          Select a proxy from the given file
  --auth                                                           Use proxy with username and password. If this is passed,
                                                                   proxy parameter should be in "username:password@host:port" format
  -qf QUERY_FILE, --query_file QUERY_FILE                          Read queries to search from the given file (valid for multiprocess run)
  -bc BROWSER_COUNT, --browser_count BROWSER_COUNT                 Maximum number of browsers to run concurrently (valid for multiprocess run)
  -ms MULTIPROCESS_STYLE, --multiprocess_style MULTIPROCESS_STYLE  Style of the multiprocess run. (valid for multiprocess run)
                                                                   1: single browser instance for each query (default)
                                                                   2: multiple browser instances for each query

```

`python ad_clicker.py -q <search query> [-t ad_visit_time_in_seconds] [--headless] [-p PROXY] [-pf PROXY_FILE] [--auth]`


### Examples

* Search for "wireless keyboard" with the default 4 seconds visit time on clicked ad pages.

    * `python ad_clicker.py -q "wireless keyboard"`

* Search for "wireless keyboard" with 5 seconds visit time on clicked ad pages.

    * `python ad_clicker.py -q "wireless keyboard" -t 5`

* Search for "wireless keyboard" using headless browser.

    * `python ad_clicker.py -q "wireless keyboard" --headless`

* Search for "wireless keyboard" using the given proxy without authentication.

    * `python ad_clicker.py -q "wireless keyboard" -p host:port`

* Search for "wireless keyboard" using the given proxy with authentication.

    * `python ad_clicker.py -q "wireless keyboard" --auth -p username:password@host:port`

* Search for "wireless keyboard" using a proxy from the given file.

    * `python ad_clicker.py -q "wireless keyboard" -pf ~/proxies.txt`

* Search for "wireless speaker" and click links that include the given filter words in url or title.

    * `python ad_clicker.py -q "wireless speaker@amazon#ebay  # mediamarkt"`

    * Spaces around "@" and "#" are ignored, so both "wireless speaker@amazon#ebay" and
    "wireless speaker @ amazon  # ebay" take "wireless speaker" as search query and "amazon" and "ebay"
    as filter words.

* Run multiple browsers by taking queries and proxies with authentication from the given files.

    * `python run_ad_clicker.py -qf ~/queries.txt --auth -pf ~/proxies.txt`

* Run multiple browsers by taking queries and proxies without authentication from the given files with 10 browsers.

    * `python run_ad_clicker.py -qf ~/queries.txt -pf ~/proxies.txt -bc 10`

    * If -bc(--browser_count) option is not given, the number of cpu cores is used.

* Run multiple browsers by taking queries and proxies from the given files using alternative multiprocess style.

    * `python run_ad_clicker.py -qf ~/queries.txt -pf ~/proxies.txt -ms 2`

    * **1**: each browser instance gets a different query from file (default) (e.g. 5 browsers search the first 5 queries from the file.
        After they are completed, second group of 5 browsers search the next 5 queries from the file and so on)
    * **2**: multiple browser instances get the same query (e.g. 5 browsers search the first query from file. After
        they are completed, second group of 5 browsers search the second query and so on)

    * If the number of queries or proxies are less than the number of browsers to run, they are cycled.

![Multiprocess Run](assets/ad_clicker_multiprocess.gif)

* Run shell script to run the tool in loop.

    * `./run_in_loop.sh`

    * Loop script requires *proxies.txt* and *queries.txt* files under home folder.
    * Proxies should be in *username:password@host:port* format.
    * Default wait time between runs is 60 seconds.

* Run shell script to run the tool in loop with given number of browser instances.

    * `./run_in_loop.sh 4`

* Run shell script to run the tool in loop with given number of browser instances and 2 minutes wait between runs.

    * `./run_in_loop.sh 4 120`

    * Wait time parameter should be in seconds.

---

## Support

If you benefit from this tool, please consider donating using the sponsor links.

If you want more customized solutions, please contact via email.
