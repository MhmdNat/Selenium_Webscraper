import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
import io
from PIL import Image
import time
import csv
import os


PATH = "C:\\Users\\user 2\\Desktop\\WebScraping Stuff\\chromedriver.exe"
service = Service(PATH)
wd = webdriver.Chrome(service=service)


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
                

    return image_urls # return set of image urls
            
        
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
        
        
def get_id(wd, name): #name of target plant
    '''gets the id of a plant on inaturalist using its name only'''
    url = "https://www.inaturalist.org/observations?quality_grade=research"
    wd.get(url) #open page
    
    
    search = wd.find_element(By.CSS_SELECTOR, "input.form-control.ui-autocomplete-input[placeholder='Species']") #find the search bar
    search.click() # click it
    search.send_keys(name) # type the name
    search.send_keys(Keys.RETURN) #type name of plant
    
    time.sleep(5) #wait for it to dynamically load
    plant = wd.find_element(By.CSS_SELECTOR, "li.ac-result a.ac-view") #find the plant
    
    href = plant.get_attribute("href") #scrape the link
    href = href.split('taxa/')
    plant_id = href[1] #extract the id
    
    '''url format becomes https://www.inaturalist.org/observations?quality_grade=research&taxon_id={plant_id}'''
    return plant_id


def read_csv_plants():
    '''read names from csv file into a list '''
    with open('C:\\Users\\user 2\\Desktop\\WebScraping Stuff\\Species name.csv', mode = 'r', newline='', encoding = 'utf-8') as file: #open csv file
        csv_reader = csv.reader(file) # create a reader
        species_names = [row[0] for row in csv_reader] # read first column in each row
    return species_names # return a list of all species in csv


def species_name_to_id():
    '''this is for transferrring the names to ids'''
    name_id_list = []
    species = read_csv_plants() # list of specie names read from file
    
    for name in species:
        plant_id = get_id(wd,name) # for each plant get the id
        name_id_list.append((name,plant_id)) #tuple
    return name_id_list


def new_path(new_path): 
    '''this just creates a new folder in specified path'''
    if not os.path.exists(new_path):
        os.makedirs(new_path)
    return new_path

        
def main():
    plant_name_ids = species_name_to_id() #returns tuple (name, id)
    
    for name, ID in plant_name_ids: #for the tuple returned by species_name_to_id
    
        page_url = f"https://www.inaturalist.org/observations?quality_grade=research&taxon_id={ID}" # open page using id
        urls = get_urls_from_google(wd, 4, 3, page_url) # get image urls
        
        for i, url in enumerate(urls):
            path = new_path(f"C:\\Users\\user 2\\Desktop\\WebScraping Stuff\\Imgs\\{name}/") #inserts images into a folder with the name of plant
            
            download_image(path,url, f"INATURALIST_{ID}_{i}.jpg") #name of the image with needed format
            
    wd.quit() # close webdriver

#start process
main()
