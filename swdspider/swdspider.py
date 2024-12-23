from bs4 import BeautifulSoup
from os import system,chdir
import json
import urllib
from importlib import import_module, reload
import sys
from os.path import abspath

sys.stderr = sys.stdout


def main():
    print('swdspider v0.1.1 Dec 22 2024')
    src = {}
    src['items'] = '''\
# Define here the models for your items


class SpiderItem(object):
    # define the fields for your item here like:
    # name = None
    
    pass

'''
    src['pipelines'] = '''\
# Define your pipelines here


def defaultpipeline(items:list):
    return items

'''
    src['settings'] = '''\
import {proj}.pipelines as pipelines

DEFAULT_USER_AGENT = 'Spider'
PIPELINES = {'defaultgroup':[pipelines.defaultpipeline]}

'''
    spi = {}
    spi['default'] = '''\
from urllib.request import Request
from bs4 import BeautifulSoup
from {proj}.items import SpiderItem

crawl_urls = []
pipeline_groups = ['defaultgroup']


def process_request(request:Request):
    
    return request


def process_response(response, soup:BeautifulSoup):
    items = []
    
    return items

'''
    proj = input('Project folder:')
    system(f'mkdir {proj} >nul')
    chdir(proj)
    sys.path.append(abspath('../'))
    try:
        cfgfp = open(f"swdspider.cfg", 'r+')
    except Exception as e:
        cfgfp = open(f"swdspider.cfg", 'w+')
    try:
        cfg = json.load(cfgfp)
    except Exception as e:
        cfg = ''
    
    def dumpcfg():
        cfgfp.seek(0)
        json.dump(cfg, cfgfp)
    
    def crawl(t):
        for i in list(sys.modules.keys()):
            if i.startswith(proj):
                del sys.modules[i]
        settings = import_module(name='.settings',package=proj)
        sp = import_module(name=f'.spiders.{t}',package=proj)
        
        
        def getrequest(url):
            headers = {'User-Agent':settings.DEFAULT_USER_AGENT}
            return urllib.request.Request(url, headers=headers)
    
        def getresponse(request):
            try:
                response = urllib.request.urlopen(request)
            except Exception:
                response = ''
            return response
            
        items = []
        for url in sp.crawl_urls:
            request = getrequest(url)
            request = sp.process_request(request)
            response = getresponse(request)
            if response:
                items += sp.process_response(response, BeautifulSoup(response.read(), 'html.parser'))
                print(f'Crawled {url} successfully.')
            else:
                print(f'Error: {url}')
        print('Crawling finished.')
        for group in sp.pipeline_groups:
            for pipeline in settings.PIPELINES[group]:
                items = pipeline(items)
        print('Pipeline finished.')
        print('Done')
                
    if not cfg:
        cfg = {'spiders':{}}
        dumpcfg()
        system(f'mkdir spiders')
        for i in src:
            with open(f'{i}.py', 'w') as fp:
                fp.write(src[i].replace('{proj}', proj))
    spiders = cfg['spiders']
    print(f'Project "{proj}"')
    c = input('>')
    
    while c not in ('exit', 'e'):
        t = c.split()
        if not c:
            pass
        elif t[0] == 'new':
            try:
                if t[1] in spiders:
                    print(f'Error: Spider "{t[1]}" already exists.')
                else:
                    with open(f'spiders/{t[1]}.py', 'w') as fp:
                        fp.write(spi['default'].replace('{proj}', proj))
                    spiders[t[1]] = t[1]
                    print(f'Successfully created spider "{t[1]}"')
            except Exception as e:
                print(e)
                print('Error: An exception has occurred while handling new command.')
        elif t[0] == 'del':
            try:
                if t[1] not in spiders:
                    print(f'Error: Couldn\'t find spider "{t[1]}".')
                else:
                    if input('Proceed (y/n)?') == 'y':
                        del spiders[t[1]]
                        system(f'del spiders\\{t[1]}.py /q')
                        print('Successfully deleted the spider.')
                    else:
                        print('Process cancelled.')
            except Exception:
                print('Error: An exception has occurred while handling del command.')
        elif t[0] == 'crawl':
            try:
                if t[1] not in spiders:
                    print(f'Error: Couldn\'t find spider "{t[1]}".')
                else:
                    crawl(t[1])
            except Exception as e:
                print('Error: An exception has occurred while handling crawl command.')
                print(type(e), e)
        else:
            print('Bad command.')
        c = input('>')
    cfgfp.close()
    system('del swdspider.cfg /q')
    with open('swdspider.cfg', 'w') as fp:
        json.dump(cfg, fp)
if __name__ == '__main__':
    main()
