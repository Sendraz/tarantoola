import requests
import json
import optparse
import sys
import re
from html.parser import HTMLParser


defaultUserAgent = "Mozilla/5.0 (X11; Linux i686; rv:109.0) Gecko/20100101 Firefox/120.0"

#used for parsing html and scanning for urls leading to next pages 
class Scanner(HTMLParser):
    def __init__(self, host):
        self.host = host
        self.urls = []
        return super().__init__()
    def handle_starttag(self, tag, attrs):
        for a in range(len(attrs)):
            #search for urls in tag attributes
            if "href" in attrs[a] or "src" in attrs[a] or "action" in attrs[a]:
                if attrs[a][1]:
                    if "http" in attrs[a][1] or attrs[a][1][0] == '/' or ".php" in attrs[a][1] or ".html" in attrs[a][1]:
                        self.urls.append(attrs[a][1])
    def handle_data(self, data):
        #search for urls in tag body
        url = re.search("^https?://", data)
        if url:
            self.urls.append(url.string)
    def getURLs(self):
        for u in range(len(self.urls)):
            try:
                if self.urls[u][0] == '/' and self.urls[u][1] != '/': #if url is relative, convert it to absolute
                    self.urls[u] = self.host[0:self.host.find('/', 8)] + self.urls[u]
                elif self.urls[u][0] != '/' and "http" not in self.urls[u]:
                    self.urls[u] = self.host[0:self.host.find('/', 8)] + "/" + self.urls[u]
            except IndexError:
                pass
        return self.urls
#main crawler class
class Crawler:
    def __init__(self, target_host, headers, cookies):
        self.target_host = target_host
        self.session = requests.Session()
        self.session.max_redirects = 10000

        self.cookies = {}  
        if cookies:
            self.cookies = cookies
        self.headers = headers
        self.found = []

    def parseHTML(self, data):
        #search for urls and forms in html code
        scan = Scanner(self.target_host)
        scan.feed(data)
        scan.close()
        return scan.getURLs()

    def fetchUrl(self, target):
        self.found.append(target)
        resp = None
        try:
            resp = self.session.get(target, headers=self.headers, cookies=self.cookies, timeout=5)
        except requests.exceptions.InvalidSchema:
            print("found url is not valid! " + target)
        urls = []
        if(resp):
            print(target + " = " + str(resp.status_code))
            if(resp.ok):
                urls = self.parseHTML(resp.text)
                for u in urls:
                    if u not in self.found:
                        if self.sub_domains == True and re.search("^.*" + self.target_host[self.target_host.find("."):], u): #if is on the same domain + subdomains
                            self.fetchUrl(u)
                        elif self.target_host in u: #if is on the same domain
                           self.fetchUrl(u)
        
    def start(self, sub_domains):
        self.sub_domains = sub_domains
        print("crawling in my skin...")
        self.fetchUrl(self.target_host)

def prepareOpts(opts):
    cookies = {}
    headers = {}
    if opts.cookies:
        with open(opts.cookies, "r") as cookiefile:
            cookies = json.load(cookiefile)
    if opts.user_agent:
        headers = {"User-Agent":opts.user_agent}
    else:
        headers = {"User-Agent":defaultUserAgent}    
    if opts.header:
        hdrJson = "{\"" + opts.header[0:opts.header.find(":")] + "\":\"" + opts.header[opts.header.find(":") + 1:] + "\"}" #add parenthesis required for valid json decoding
        headers.update(json.loads(hdrJson))
    return (headers, cookies)

if __name__ == "__main__":
    print("Tarantoola")
    parser = optparse.OptionParser(usage="Usage: tarantoola.py [url] [options]")
    parser.add_option("-c", "--cookies", dest="cookies", metavar="[JSON WITH COOKIES]", help="add cookies to requests from json file")
    parser.add_option("-e", "--header", dest="header", help="add custom header to requests")
    parser.add_option("-u", "--user-agent", dest="user_agent", help="set user agent, default=" + defaultUserAgent)
    parser.add_option("-s", "--subdomain-scan", action="store_true", dest="sub", help="scans and outputs subdomains found on websites")
    (opts, args) = parser.parse_args()
    headers, cookies = prepareOpts(opts)
    
    if(len(args) < 1):
        print("please provide target url!")
        sys.exit(-1)
    crawler = Crawler(args[0], headers, cookies)
    crawler.start(opts.sub)
    


    
