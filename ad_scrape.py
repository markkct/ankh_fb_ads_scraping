from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import time
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
import logging
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
filename = os.path.join(dir_path, 'scraping_live.log')

#Config
# login=False
login=True
# pc_mac='mac'
pc_mac='pc'
list_url='https://record.ankh.com.hk/api/scrape/list'
storeUrl='https://record.ankh.com.hk/api/scrape/py/ads'

# Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(filename)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)


def do_logging():
    logger.info("scraping")


if __name__ == '__main__':
    do_logging()

options = Options()
options.add_argument("--disable-notifications")

# options.add_argument("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36")
# options.headless = False
options.headless = True
#specify the path to chromedriver.exe (download and save on your computer)
# chrome = webdriver.Chrome('/usr/local/bin/chromedriver', options=options)
if(pc_mac=='mac'):
    chrome = webdriver.Chrome('/usr/local/bin/chromedriver',options=options)
else:
    chrome = webdriver.Chrome('C:\mining\webdriver.exe',options=options)

#LOGIN START
#open the webpage
if(login):
    chrome.get("http://www.facebook.com")
    email = chrome.find_element('name',"email")
    password = chrome.find_element('name',"pass")
    print('Logging in')
    #enter username and password
    email.send_keys('ankh.api@gmail.com')
    password.send_keys('ANfbpw321!')
    time.sleep(3)
    password.submit()
    time.sleep(3)
#LOGIN END

r = requests.get(list_url)

fanpages = r.json()
# print(fanpages)

print()
if(r.status_code == 200):

    for fanpage in fanpages:
        chrome.get(fanpage['url'])
        print('Scraping Target: '+fanpage['page_name'])
        time.sleep(5)

        for j in range(0,1):
            chrome.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(6)

        pageContent = BeautifulSoup(chrome.page_source, 'html.parser')
        creatives = pageContent.find_all('div',{'class':'_7jvw x2izyaf x1hq5gj4 x1d52u69'})
        totalAds=pageContent.select('div.x8t9es0.x1uxerd5.xrohxju.x108nfp6.xq9mrsl.x1h4wwuj.x117nqv4.xeuugli')[0].text

        postData=[]
        for creative in creatives:
            # print(creative)
            
            page_title = creative.select('span.x8t9es0.x1fvot60.xxio538.x108nfp6.xq9mrsl.x1h4wwuj.x117nqv4.xeuugli')[0].string
            totalResult = totalAds
            ad_id = (creative.find_all('div',{"class":"x3nfvp2 x1e56ztr"})[-1]).select('span')[0].string     
            postDate = creative.select('span.x8t9es0.xw23nyj.xo1l8bm.x63nzvj.x108nfp6.xq9mrsl.x1h4wwuj.xeuugli')[1].string
            useCount = creative.select('._9b9y span strong')[0].string if creative.select('._9b9y span') else '1則廣告'
            creativeType = 'video' if creative.select('video') else 'image'

            cover = None
            if creative.select('video'): cover = creative.select('video')[0]['poster']
            if creative.select('.x1ywc1zp.x78zum5.xl56j7k.x1e56ztr.x1277o0a img'): cover = creative.select('.x1ywc1zp.x78zum5.xl56j7k.x1e56ztr.x1277o0a img')[0]['src']
            # print()

            if fanpage:
                text = None
                if creative.select('video'): cover = creative.select('video')[0]['poster']
                if creative.select('.o9tcmdvq img.img'): cover = creative.select('.o9tcmdvq img.img')[0]['src']
                creative_data = {                        
                    'id':fanpage['id'], 
                    'type':fanpage['type'],
                    'name':fanpage['name'],
                    'url':fanpage['url'],

                    'fanpage':page_title,
                    'totalResult':totalResult,
                    'ad_id':ad_id,
                    'postDate':postDate,
                    'useCount':useCount,
                    'creativeType': creativeType,
                    'cover':cover,
                    'text':None

                }
                # print(creative_data)
                postData.append(creative_data)
                
            print('Scraped '+ str(len(postData)) + ' creatives')
            print(postData)
            postURL=storeUrl
            postToServer = requests.post(postURL,json=postData)
            print(postToServer)
            print('Sent to Server')
            time.sleep(2)

chrome.quit()
logger.info("All task completed!")
print('All task completed!')
