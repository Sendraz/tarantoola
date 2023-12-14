# tarantoola
Simple crappy web crawler written in python using requests.

Usage: tarantoola.py [url] [options]

Options:
  -h, --help            show this help message and exit
  -c [JSON WITH COOKIES], --cookies=[JSON WITH COOKIES]
                        add cookies to requests from json file
  -e HEADER, --header=HEADER
                        add custom header to requests
  -u USER_AGENT, --user-agent=USER_AGENT
                        set user agent, default=Mozilla/5.0 (X11; Linux i686;
                        rv:109.0) Gecko/20100101 Firefox/120.0
  -s, --subdomain-scan  scans and outputs subdomains found on websites
