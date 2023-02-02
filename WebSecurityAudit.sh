#!/usr/bin/env zsh
#
# Saecurity Audit
# Discover sub-domains running an http server on the hosts
# Process these domains through WafW00f engine & output in a CSV
#
# Main Source:
# Key File:
#
clear
echo "Web Security Risk Assessment (WSRA) Started for " $1 " Sub-domains"
echo ""
echo "This could take a few minutes depending on the number of Sub-domains"
echo $1 | subfinder -silent | httpx -silent > httphostslist.txt
#wc -l httphostslist.txt
wc -l httphostslist.txt
wafw00f -i httphostslist.txt -o $1-waf-provider-list.csv
rm httphostslist.txt
column -s, -t < $1-waf-provider-list.csv
