#!/bin/bash

wait_time=60

if [[ $# -eq 1 ]]; then
    browser_count=$1
elif [[ $# -eq 2 ]]; then
    browser_count=$1
    wait_time=$2
fi

while true;
do
    if [[ $browser_count -gt 1 ]]; then
        echo "Running with ${browser_count} browsers..."
        python run_ad_clicker.py --auth -pf ~/proxies.txt -qf ~/queries.txt -bc ${browser_count}
    else
        python run_ad_clicker.py --auth -pf ~/proxies.txt -qf ~/queries.txt
    fi

    echo "Sleeping ${wait_time} seconds..."
    sleep $wait_time
done
