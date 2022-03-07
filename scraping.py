
# Import Splinter and BeautifulSoup and other dependencies

#from dataclasses import dataclass
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt

def scrape_all():
    #initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)
    
    news_title, news_paragraph = mars_news(browser)
    data = {
        'news_title' : news_title,
        'news_paragraph' : news_paragraph,
        'featured_image' : featured_image(browser),
        'facts' : mars_facts(),
        'hemispheres': hemispheres(browser), 
        'last_modified' : dt.datetime.now(),
        
    }
    #stop web driver and return data    
    browser.quit()
    return data


#putting scraping code into a function
def mars_news(browser):

    #visit the mars nasa news site
    url = 'https://redplanetscience.com'
    browser.visit(url)
    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    #convert browser html to soup object
    html = browser.html
    news_soup = soup(html, 'html.parser')
    
    #begin scraping
    try:
        slide_elem = news_soup.select_one('div.list_text')
        slide_elem.find('div', class_ = 'content_title')


    #use the parent element to find the first 'a' tag and save it as 'new'
        news_title = slide_elem.find('div', class_= 'content_title').get_text()
    


    #use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    except AttributeError:
        return None, None

    return news_title, news_p


# ### Featured Images

#declare a function for featured images scrape
def featured_image(browser):
    #visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)


    #find the full image button and click it
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()


    #parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')


    #error handling
    try:
        #find the relative image url (but this only gives the path documented in html, not the entire path of the image)
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
    
    except AttributeError:
        return None

    
    #use the base URL to create an absolute URL of the image
    #img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    img_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_url_rel}'

    return img_url

def mars_facts():
    try:
        #use read html to scrape facts table into a DF
        #df = pd.read_html('https://galaxyfacts-mars.com')[0]
        df = pd.read_html('https://data-class-mars-facts.s3.amazonaws.com/Mars_Facts/index.html')[0]
    except BaseException:
        return None

    #assigning columns and set index
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    #convert DF into HTML format, add bootstrap
    return df.to_html(classes='table table-striped' "table table-bordered")

def hemispheres(browser):
    #Use browser to visit the URL 
    url = 'https://marshemispheres.com/'
    browser.visit(url)

    #Reviewing and parsing the html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')
    
    #Hemisphere specific data
    data = img_soup.find_all('div', class_='item')
   #Create a list to hold the images and titles.
    hemisphere_image_urls = []
    #Write code to retrieve the image urls and titles for each hemisphere; 4 hemispheres to collect
    for x in data:
        hemispheres = {}
        hemisphere_titles = x.find('h3').text
        #get to full image page
        full_page_url = x.find('a', class_ = 'itemLink product-item')['href']
        #visit full image page
        browser.visit(url + full_page_url)
        #parse results
        html = browser.html
        img_soup = soup(html, 'html.parser')
        #img_soup
        #img url for full image
        img_url_rel = img_soup.find('div', class_='downloads')
        full_url = img_url_rel.find('a')['href']
        #url creation with base, for full resolution image URL string
        img_url = f'https://marshemispheres.com/{full_url}' 
        
        print(hemisphere_titles)
        print(img_url)

        #add title and url to dictionary
        hemispheres['img_url'] = img_url
        hemispheres['titles'] = hemisphere_titles
        hemisphere_image_urls.append(hemispheres)
        browser.back()
    return hemisphere_image_urls

    
    
if __name__ == "__main__":
 
 # If running as script, print scraped data
    print(scrape_all()) 


