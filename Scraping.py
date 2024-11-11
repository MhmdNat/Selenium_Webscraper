import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import io
from PIL import Image
import time

#Global variables
PATH = "C:\\Users\\user 2\\Desktop\\WebScraping Stuff\\chromedriver.exe" #path of chromdriver.exe
service = Service(PATH) 
wd = webdriver.Chrome(service=service) #creating a webdriver using chrome driver


def get_urls_from_google(wd, delay, max_images):
    '''Transforms images to a set of image_urls using a page url'''
    
    
    def scroll_down(wd):
        '''handles scrolling down to load more images'''
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);") #execute javascript script
        time.sleep(delay) # wait for images to load
        
        
    url = "https://www.inaturalist.org/observations?quality_grade=research"
    wd.get(url) # open url page
    
    image_urls = set() #not list to make sure we have each url once only
    i=1 # currently counter of images, need to change it to thubmnail counter
    stop = False
    while i <max_images and stop==False:
        scroll_down(wd)
        
        thumbnails = wd.find_elements(By.CSS_SELECTOR, ".photo.has-photo")  # returns a list of all thumbnails, at most 96 thumbnails
        
        for img in thumbnails[len(image_urls) : max_images]:
            if stop: break
            try:
                img.click() # click thumbnail to show bigger image
                try:
                    time.sleep(delay) # wait for image to load
                    image_elements = wd.find_elements(By.CSS_SELECTOR, '.image-gallery-image img') # list of all images inside the thumbnail
                    for image in image_elements:
                        if i>=max_images:
                            stop = True
                            break
                        if image.get_attribute('src') and 'http' in image.get_attribute('src'): # make sure image has a http link
                            image_urls.add(image.get_attribute('src')) #get url andadd it to our set
                            print("Image added!")
                            i+=1 
                finally:
                    wd.back() # wd returns to main page
                
                
            except:
                continue
                
    wd.quit()
    return image_urls
            
        
def download_image(download_path, url, file_name):
    '''Using an image url, download the image into a specific file'''
    try:
        image_content = requests.get(url).content #get req to get content from url
        image_file = io.BytesIO(image_content) #storing file in memory in binary
        image = Image.open(image_file) # converts to pil image easier to save
        file_path = download_path + file_name # the path of image
        with open(file_path, "wb") as f: # open new file at file path "wb" write bytes, f name of file
            image.save(f, "JPEG") 
        print("success")
        
    except Exception as e:
        print("failed -", e)    


#Main
max_photos = 4
urls = get_urls_from_google(wd, 1, max_photos)

for i, url in enumerate(urls):
    download_image("C:\\Users\\user 2\\Desktop\\WebScraping Stuff\\Imgs/",url, f"{i}.jpg")
