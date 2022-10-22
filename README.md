# ad_clicker

This script changes IP via Tor and clicks ads for a certain query on Google search. Tested with Firefox and Chrome.

[Related post on Medium](https://python.plainenglish.io/google-ads-clicker-with-python-selenium-and-tor-a6ff8078da2a)

## How do I get set up?

Run the shell script to install dependencies and setup Tor on Linux machine.

`./ad_clicker_setup.sh`


## How to run?

```
usage: python ad_clicker.py [-h] [-q QUERY] [-b BROWSER] [-t AD_VISIT_TIME] [--tor]

optional arguments:
  -h, --help                                   show this help message and exit
  -q QUERY, --query QUERY                      Search query
  -b BROWSER, --browser BROWSER                Browser to use
  -t AD_VISIT_TIME, --visittime AD_VISIT_TIME  Number of seconds to wait on the ad page opened
  --tor                                        Enable using Tor network

```

`python ad_clicker.py -q <search query> [-b browser] [-t ad_visit_time_in_seconds] [--tor]`


### Examples

* Search for "wireless keyboard" using Firefox and 4 seconds visit time on clicked ad pages.

    * `python ad_clicker.py -q "wireless keyboard"`

* Search for "wireless keyboard" using Chrome and 5 seconds visit time on clicked ad pages.

    * `python ad_clicker.py -q "wireless keyboard" -b chrome -t 5`

* Search for "wireless keyboard" with 7 seconds visit time and use Tor network.

    * `python ad_clicker.py -q "wireless keyboard" -t 7 --tor`
