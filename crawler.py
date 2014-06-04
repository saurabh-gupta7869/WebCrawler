import urllib2
import socket
socket.setdefaulttimeout(10)

print "***Web-Crawler***"

print "Enter the seed url to start crawling like http://edition.cnn.com/ :"
x= raw_input()
if x!="":
    try:
        f = urllib2.urlopen(url)
        U=x
    except:
        print "Invalid Url"
        U="http://edition.cnn.com/"
        
else:
    U="http://edition.cnn.com/"

# Limit for maximum no pages to crawl
print "Enter the maximum no pages to crawl :"
x= raw_input()
try:
    x=int(x)
    if int(x)>=1:
        M=x
    else:
        M=40
except:
    M=40


print "Enter the Maximum depth to crawl :"
x= raw_input()
try:
    x=int(x)
    if int(x)>=1:
        D=x
    else:
        D=40
except:
    D=40

K=3 # Reciprocal Factor

print "url =" + U
print "Maxpages =" + str(M)
print "Max_Depth =" + str(D)
print "Creating Index..."
      

def get_page(url):
    
    try:
        # for urls like "/about"
        if url[0]=='/':
            url = U + url
        else:
            if url.find(U)==-1:
                return ""
        
        f = urllib2.urlopen(url)
        content = f.read()
        f.close()
        #cache[url]=content
        #print content
        return content
    except Exception, e:
        print "In get_page():" 
        print e
        return ""

# return s after removing all tags
def remove_tags(s):
    start = s.find('<')

    try:
        while start!=-1:
            end = s.find('>',start)
            s = s[:start] + " " + s[end+1:]
            start = s.find('<')
    except Exception, e:
        print "In remove_tags():"
        print e      

    return s
            
def split_string(source,splitlist):
        return ''.join([ w if w not in splitlist else ' ' for w in source]).split()

def get_next_target(page):

    try:
        start_link = page.find('<a href=')
        if start_link == -1: 
            return None, 0
        start_quote = page.find('"', start_link)
        end_quote = page.find('"', start_quote + 1)
        url = page[start_quote + 1:end_quote]
        return url, end_quote

    except Exception, e:
        print "In get_next_target():"
        print e
        return None, 0
    
    
def get_all_links(page):
    links = []
    while True:
        url, endpos = get_next_target(page)
        if url:
            links.append(url)
            page = page[endpos:]
        else:
            break
    return links


def union(a, b):
    for e in b:
        if e not in a:
            a.append(e)


def add_to_index(index, keyword, url):
    if keyword in index:
        if url not in index[keyword]:
            index[keyword].append(url)
    else:
        index[keyword] = [url]


def add_page_to_index(index, url, content):
    try:
        content = remove_tags(content)
        words = split_string(content, """ ,"!-.()<>[]{};:?!-=`&""")
        #words = content.split()
        for word in words:
            add_to_index(index, word, url)
    except Exception, e:
        print "In add_page_to_index():" 
        print e

def is_reciprocal(graph,src,dest,k):
    if k==0:
        if src==dest:
            return True
        return False

    
    if dest not in graph:
        return False
    
    if k==1:       
        for e in graph[dest]:
            if e==src:
                return True
        return False    

    for e in graph[dest]:
        if is_reciprocal(graph,src,e,k-1):
            return True
    return False

    
def compute_ranks(graph,k):
    d = 0.8 # damping factor
    numloops = 10
    ranks = {}
    
    npages = len(graph)
    for page in graph:
        ranks[page] = 1.0 / npages
    for i in range(0, numloops):
        newranks = {}
        for page in graph:
            newrank = (1 - d) / npages
            for node in graph:
                if page in graph[node]:
                    if not is_reciprocal(graph,node,page,k):
                        newrank = newrank + d * (ranks[node]/len(graph[node]))
            newranks[page] = newrank
        ranks = newranks
    return ranks



# creates index and graph
def crawl_web(seed,max_depth,max_pages): # returns index, graph of inlinks
    tocrawl = [seed]
    crawled = []
    next_depth=[]
    graph = {}  # <url>, [list of pages it links to]
    index = {}  # <keyword>, [list of urls]
    depth=0
    while tocrawl and max_pages and depth<=max_depth: 

        page = tocrawl.pop()

        if page not in crawled:
            content = get_page(page)
            if content:
                add_page_to_index(index, page, content)
                outlinks = get_all_links(content)
                graph[page] = outlinks
                union(next_depth, outlinks) # add all next level links to next_depth list 
                max_pages-=1
                
            crawled.append(page)
            
    
        if not tocrawl:
            tocrawl=next_depth
            next_depth=[]
            depth+=1

        print "Pages crawled = " + str(M-max_pages) + ", Depth = " + str(depth)

    #print "depth crawled = " + str(depth)
    #print "No of pages crawled = " + str(M - max_pages)
    return index, graph


def lookup(index, keyword):
    if keyword in index:
        return index[keyword]
    else:
        return None


def sorted_urls(index, ranks, keyword):
 
    urls= lookup(index,keyword)
    if urls==None:
        return None
    
    temp=[]

    for url in urls:
        temp.append(ranks[url])

    return [(x,y) for (y,x) in sorted(zip(temp,urls),reverse=True)]
    
    '''
    print max rank url
    rank=0
    # return url with max rank
    for url in urls:
        if ranks[url]>rank:
            res=url
            rank=ranks[url]
            
    return res
    '''

index, graph = crawl_web(U,D,M)
ranks = compute_ranks(graph,K)

#print index
#print graph
#print ranks

print "Index created."
print "Enter the Keyword to search (q to quit)"+ "\n"
while True:
    keyW = raw_input()
    if keyW =="q" or keyW== "Q":
        break
    results = sorted_urls(index, ranks, keyW)
    if results:
        for r in results:
            print str(r[0]) + ", rank= " + str(r[1])
    else:
        print "No Results Found!"


