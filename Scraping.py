import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import io
from PIL import Image
import time
import csv
import os
from threading import Thread 


'''
make sure chrome driver version matches with your chrome version
follow below steps to start scraping inaturalist
'''
# requirements beforer running code
PATH ='' # path of ur chrome driver ex: "C:\\Users\\user 2\\VIP\\chromedriver.exe"

csv_directory ="" # path where we want to save the metaData on excel sheets ex:"C:\\Users\\user 2\\Desktop\\VIP\\metaData files\\" ps: this is a folder, the code automatically generates files

photo_path = "" # path where we want to save the scraped images "C:\\Users\\user 2\\Desktop\\VIP\\Images\\" also a folder, code automatically generates sub folders

csv_file_paths = "" #'C:\\Users\\user 2\\Desktop\\VIP\\ the folder that contains the csv files with species names


#what is below may vary ie decrease files or increase depending on processing power and internet speed

# names of csv files that contain the species names
# split the names equally btw these files
file1 = '' # ex ids1.csv 
file2 = '' # ex ids1.csv
file3 = '' # ex ids1.csv

#initialize the webdrivesrs
service = Service(PATH)
wd = webdriver.Chrome(service=service)
wd2 = webdriver.Chrome(service=service)
wd3 = webdriver.Chrome(service=service)

#ready to start

#configure delays to your internet needs
#time.sleep(increase here if slow wifi)



def get_id(wd, name): #name of target plant
    '''gets the id of a plant on inaturalist using its name only'''
    url = "https://www.inaturalist.org/observations?quality_grade=research"
    wd.get(url) #open page
    wait_for_dynamic_loading(wd, "input.form-control.ui-autocomplete-input[placeholder='Species']", 5)
    search = wd.find_element(By.CSS_SELECTOR, "input.form-control.ui-autocomplete-input[placeholder='Species']") #find the search bar
    search.click() # click it
    search.send_keys(name) # type the name
    search.send_keys(Keys.RETURN) #type name of plant
    time.sleep(2) #wait for it to load
    plant = wd.find_element(By.CSS_SELECTOR, "li.ac-result a.ac-view") #find the plant
    href = plant.get_attribute("href") #scrape the link
    href = href.split('taxa/') #get the id part of the link
    plant_id = href[1] #extract the id
    
    # url format becomes https://www.inaturalist.org/observations?quality_grade=research&taxon_id={plant_id}
    return plant_id


def get_urls_from_google(wd, delay, url, data, page_count):
    '''Transforms images to a set of image_urls using a page url'''
    thumbnails = []
    while True:
        try:
            time.sleep(1)
            wd.get(url)
            print("page: ",page_count)
            time.sleep(2)
            urls_set = set()  
            scroll_to_bottom(wd, 2)
            wait_for_dynamic_loading(wd, ".photo.has-photo", delay)
            thumbnails = wd.find_elements(By.CSS_SELECTOR, ".photo.has-photo")
            thumbnail_urls = [thumbnail.get_attribute("href") for thumbnail in thumbnails if thumbnail.get_attribute("href")]
            break
        except:
            continue
    
    i=0 #number of thumbanils seen in this function call debugging only
    j=(page_count-1)*96 #number of thumbnail taken in total, to keep track of which thumbnail this is
    for thumbnail in thumbnail_urls:
        time.sleep(0.2)
        print("thumbnail:", i)
        k=0 #image counter
        try:
            wd.get(thumbnail) # click thumbnail to show bigger image
            time.sleep(0.2)
            print("entering thumbnail")
            wait_for_dynamic_loading(wd, '.image-gallery-image img', delay)# Wait for the images to appear dynamically
            image_elements = wd.find_elements(By.CSS_SELECTOR, '.image-gallery-image img')
            for image in image_elements:
                if image.get_attribute('src') and 'http' in image.get_attribute('src'): # make sure image has a http link
                    src = image.get_attribute('src')
                    if src not in urls_set:
                        urls_set.add((image.get_attribute('src'), k)) #get url andadd it to our set
                        print("Image added!")
                        k += 1
                    else:
                        print("duplicate image skipped")
            new_data = get_uploader_info(thumbnail, j)
            data.append(new_data)
            print(new_data)
            j+=1
                        
                    
        except:
            print('skipping thumbnail')
        finally:
            i+=1
    return urls_set


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
        
        
def get_uploader_info(thumbnail_url, j):
    new_data = []
    try: #because sometimes show is not needed
        # Wait for the button to become clickable
        #wait 10 seconds if not found skip
        show_button = WebDriverWait(wd, 3).until( 
            EC.element_to_be_clickable((By.XPATH, "//button[@class='btn btn-nostyle' and text()='Show']"))
        )
        # Click the "Show" button
        show_button.click()
    finally:
    
    
        date_element = wd.find_element(By.CSS_SELECTOR, 'span.date')
        date = date_element.text
        date = date.split(" ")
        print(date)
        date = date[0] + " " + date[1] + " " + date[2]
        
        username_element = wd.find_element(By.CSS_SELECTOR, 'div.title')
        # username_href = username_element.getattr('href')
        # username = username_href.split('/')[-1]
        username = username_element.text
        
        place_element = wd.find_element(By.CSS_SELECTOR, "span.place")
        place = place_element.text
        
        
        new_data = [f"thumbnail_{j}", thumbnail_url, username, date, place]
        return new_data
    
    
#---HELPER FUNCTIONS---
def is_at_bottom(wd):
    # Get the current scroll position (window.scrollY) and the total height of the page (document.body.scrollHeight)
    scroll_position = wd.execute_script("return window.scrollY;")
    page_height = wd.execute_script("return document.body.scrollHeight;")
    return scroll_position + wd.execute_script("return window.innerHeight;") >= page_height


def scroll_to_bottom(wd, delay):
    while not is_at_bottom(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # Scroll to the bottom of the page
        time.sleep(delay)  # Wait for page to load new content
        

def read_csv_plants(name):
    global csv_file_paths
    '''read names from csv file into a list '''
    # place name of csv in directory
    with open(csv_file_paths + f'{name}.csv', mode = 'r', newline='', encoding = 'utf-8') as file: #open csv file
        csv_reader = csv.reader(file) # create a reader
        species_names = [row[0] for row in csv_reader if row] # read first column in each row
    return species_names # return a list of all species in csv


def species_name_to_id(name,wd):
    '''this is for transferrring the names to ids'''
    name_id_list = []
    species = read_csv_plants(name) # list of specie names read from file
     
    for name in species:
        plant_id = get_id(wd,name) # for each plant get the id
        name_id_list.append((name,plant_id)) #tuple
    return name_id_list


def create_folder(new_path): 
    '''this just creates a new folder in specified path'''
    if not os.path.exists(new_path):
        os.makedirs(new_path)
    return new_path


def get_number_of_observations(wd):
    time.sleep(4)
    element = wd.find_element(By.CLASS_NAME, 'stat-value')
    number_text = element.text
    print(number_text)
    number = int(number_text.replace(",", ""))
    return number


def wait_for_dynamic_loading(wd, path, delay):
    WebDriverWait(wd, delay).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, path)))
    
    
#---HELPER FUNCTIONS---

def main(name,wd):
    global csv_directory
    global photo_path
    
    plant_name_ids = species_name_to_id(name,wd) #returns list of tuples (name, id)
    for name, ID in plant_name_ids: #for the tuple returned by species_name_to_id
        page_url = f"https://www.inaturalist.org/observations?quality_grade=research&taxon_id={ID}"
        wd.get(page_url)
        time.sleep(3)
        total_thumbnails = get_number_of_observations(wd)
        number_of_full_pages = total_thumbnails // 96 # 96 thumbnails per page
        thumbnails_left = total_thumbnails % 96
        
        data = [['Thumbnail', "Url", "Name of uploader", "Upload date", "Location observed"]]
        csv_file_path = os.path.join(csv_directory, f"{name}.csv")
        urls = set()
        for i in range(1,number_of_full_pages+1):
            page_url = f"https://www.inaturalist.org/observations?page={i}&quality_grade=research&taxon_id={ID}" # open page using id and page number
            urls.update(get_urls_from_google(wd, 3, page_url, data, page_count = i)) # update urls with next page
        
        if thumbnails_left:
            page_url = f"https://www.inaturalist.org/observations?page={number_of_full_pages+1}&quality_grade=research&taxon_id={ID}"
            urls.update(get_urls_from_google(wd, 3, page_url, data, page_count = number_of_full_pages+1))  
        
        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(data)
       
        for i, (url,k) in enumerate(urls):
            path = create_folder(photo_path + f"{name}/") #inserts images into a folder with the name of plant
            download_image(path,url, f"INATURALIST_{ID}___thumbnail_{i}___image_{k}.jpg") #name of the image with needed format
            
    wd.quit() # close webdriver

#start process


t = Thread(target = main,args = (file1,wd,))
t2 = Thread(target = main,args = (file2,wd2,))
t3 = Thread(target = main,args = (file3,wd3,))


t.start()
t2.start()
t3.start()
