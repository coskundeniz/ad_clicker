# ad_clicker

This command-line tool clicks ads for a certain query on Google search using [undetected_chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver) package.

Old version of the tool can be found in the `old_version` branch.

Supports Python 3.9+

[Related post on Medium](https://python.plainenglish.io/google-ads-clicker-with-python-selenium-and-tor-a6ff8078da2a)

## How to setup

Run the following commands to install required packages.

* `python -m venv env`
* `source env/bin/activate`
* `pip install -r requirements.txt`


## How to run

```
usage: python ad_clicker.py [-h] [-q QUERY] [-t AD_VISIT_TIME] [--headless] [-p PROXY] [-pf PROXY_FILE]

optional arguments:
  -h, --help                                   show this help message and exit
  -q QUERY, --query QUERY                      Search query
  -t AD_VISIT_TIME, --visittime AD_VISIT_TIME  Number of seconds to wait on the ad page opened
  --headless                                   Use headless browser
  -p PROXY, --proxy PROXY                      Use the given proxy in ip:port format
  -pf PROXY_FILE, --proxy_file PROXY_FILE      Select a proxy from the given file
  --auth                                       Use proxy with username and password. If this is passed,
                                               proxy parameter should be in "username:password@host:port" format
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

---

## Support

If you benefit from this tool, please consider donating using the sponsor links.

If you want more customized solutions, please contact via email.