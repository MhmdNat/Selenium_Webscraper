import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import io
from PIL import Image
import time

PATH = "C:\\Users\\user 2\\Desktop\\WebScraping Stuff\\chromedriver.exe"
service = Service(PATH)
wd = webdriver.Chrome(service=service)


def get_urls_from_google(wd, delay, max_images):
    
    
    def scroll_down(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);") #execute javascript script
        time.sleep(delay)
        
        
    url = "https://www.inaturalist.org/observations?quality_grade=research"
    wd.get(url)
    
    image_urls = set() #not list to make sure we have each url once only
    i=1
    while i <max_images:
        scroll_down(wd)
        
        thumbnails = wd.find_elements(By.CSS_SELECTOR, ".photo.has-photo")  #find all thumbnails with the class name (By.CLASS_NAME, "photo    has-photo")
        
        for img in thumbnails[len(image_urls) : max_images]:
            try:
                img.click() #show bigger image
                try:
                    time.sleep(delay)
                    image_elements = wd.find_elements(By.CSS_SELECTOR, '.image-gallery-image img') 
                    for image in image_elements:
                        if image.get_attribute('src') and 'http' in image.get_attribute('src'):
                            image_urls.add(image.get_attribute('src'))
                            #print(image.get_attribute('src'))
                            print("Image added!")
                            i+=1
                finally:
                    wd.back()
                
                
            except:
                continue
                
    wd.quit()
    return image_urls
            
        
def download_image(download_path, url, file_name):
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
urls = get_urls_from_google(wd, 5, max_photos)

for i, url in enumerate(urls):
    download_image("C:\\Users\\user 2\\Desktop\\WebScraping Stuff\\Imgs/",url, f"{i}.jpg")


    
    