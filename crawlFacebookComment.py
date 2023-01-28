import time
import re
import sys
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import ActionChains
#from webdriver_manager.chrome import ChromeDriverManager
#from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.keys import Keys
from feedgen.feed import FeedGenerator

def print_enc(s):
    '''Print function compatible with both python2 and python3 accepting strings
    and byte arrays.
    '''
    if sys.version_info[0] >= 3:
        print(s.decode('utf-8') if isinstance(s, bytes) else s)
    else:
        print(s)

def get_id(s):
    list_url_parts = re.split('\?|:|/', s)
    if (len(list_url_parts)) >= 7:
        return list_url_parts[6]
    else:
        return ""

options = webdriver.edge.options.Options()
#options.add_argument('--headless') # headless mode

browser = webdriver.Edge(options=options)
browser.get(r'https://www.facebook.com/sweethouse104/')

js = "document.getElementById('u_0_c').remove();"

# 現在好像都不用
''' # 沒登入的「稍後再說」
ele = WebDriverWait(driver, 10).until(
    ec.visibility_of_element_located((By.ID, 'expanding_cta_close_button'))
)
ele.click()

# 打開留言
ele = driver.find_element_by_css_selector('._3hg-._42ft')
ele.click()'''

while True:
    try:
        # 不要有正在跑的小圈圈
        WebDriverWait(browser, 8).until_not(ec.presence_of_element_located(
            (By.CSS_SELECTOR, '.mls.img._55ym._55yn._55yo')))
        # 找「顯示先前留言」
        # 原為 UFIPagerLink
        ele = WebDriverWait(browser, 5).until(ec.visibility_of_element_located((By.CSS_SELECTOR, '._4sxc._42ft')))  
        ele.click()
    except ElementClickInterceptedException:
        print('remove')
        # 移除下面的橫幕
        browser.execute_script(js)
    except TimeoutException:
        print('ok 1')
        break

# 按「查看更多」
for ele in browser.find_elements(By.CSS_SELECTOR, '._5v47.fss'):
    try:
        ele.click()
    # 有時候會在這邊被觸發
    except ElementClickInterceptedException:
        print('remove')
        browser.execute_script(js)

print('ok 2\n')

# page down
##for _ in range(1): # repeat
##    browser.find_element(By.XPATH, '//body').send_keys(Keys.PAGE_DOWN)
##    browser.find_element(By.XPATH, '//body').send_keys(Keys.PAGE_UP)
##    time.sleep(2)

# scroll
browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(2)

page_title = browser.title

list_page_title = []
list_page_url = []
list_id = []
list_date = []

for ele in browser.find_elements(By.CSS_SELECTOR, '.x11i5rnm.xat24cr.x1mh8g0r.x1vvkbs.xdj266r.x126k92a'):
    list_page_title.append(ele.text)

url_xpath = '//a[@class="x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g xt0b8zv xo1l8bm"]'
for ele in browser.find_elements(By.XPATH, url_xpath):
    url = ele.get_dom_attribute('href')
    post_date = ele.find_element(By.TAG_NAME, 'span').text
    list_page_url.append(url)
    list_id.append(get_id(url))
    list_date.append(post_date)


# 等一下再關
time.sleep(5)
browser.quit()

# feed generation
fg = FeedGenerator()
fg.id('https://www.facebook.com/sweethouse104/')
fg.title(page_title)
fg.link( href='https://www.facebook.com/sweethouse104/', rel='alternate' )
fg.link( href='https://www.facebook.com/sweethouse104/', rel='self' )
fg.language('en')

# old post add first
for i in reversed(range(len(list_page_title))):
    fe = fg.add_entry()
    fe.id(str(i) if list_id[i] == '' else list_id[i])
    fe.title(list_page_title[i])
    fe.link(href=list_page_url[i])

print_enc(fg.atom_str(pretty=True))

fg.atom_file('atom.xml') # Write the ATOM feed to a file
