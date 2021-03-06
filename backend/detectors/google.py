import requests
import csv
import re
import time
from bs4 import BeautifulSoup
from selenium import webdriver
import json
import sys
import ast


#Get input from form:
info = ast.literal_eval(sys.argv[1])
#key inputs
if("fname" in info):
    first_name = info["fname"]
last_name=""
if("lname" in info):
    last_name = info["lname"]

original_name=first_name+" "+last_name
name=original_name.replace(" ","+")

age=0
if("age" in info):
    age = int(info["age"])

city=""
if("city" in info):
    city = info["city"]
state=""
if("state" in info):
    state = info["state"]
location=city+" "+state

other_location=""

school=""
if("school" in info):
    school = info["school"]

phone_number=""
if("pnumber" in info):
    phone_number = info["pnumber"]

email=""
if("email" in info):
    phone_number = info["email"]

other_email=""
nikename=""
other_nickname=""
other_keywords = ""
if("keywords" in info):
    other_keywords= info["keywords"]


blacklist=["https://www.spokeo.com","https://www.whitepages.com","https://www.ussearch.com","https://www.beenverified.com","http://handmadegardens.net"]

keywords=[]
output_links=set()
all_results=[]

#Prepare csv output file
# f = csv.writer(open("google-search.csv","w"))
# f.writerow(["Title","Link","Description"])

#construct url combinations
if(age!=0):
    keywords.append(name+"+"+str(age))
if(location):
    location=location.replace(" ","+")
    keywords.append(name+"+"+location)
if(other_location):
    other_location=other_location.replace(" ","+")
    keywords.append(name+"+"+other_location)
if(school):
    school=school.replace(" ","+")
    keywords.append(name+"+"+school)
if(phone_number):
    keywords.append(name+"+"+phone_number)
if(email):
    keywords.append(name+"+"+email)
if(other_email):
    keywords.append(name+"+"+other_email)
if(nikename):
    keywords.append(name+"+"+nikename)
if(other_nickname):
    keywords.append(name+"+"+other_nickname)
if(other_keywords):
    keywords.append(name+"+"+other_keywords)
if(not keywords):
    keywords.append(name)

#check if the link is already saved
def isDuplicate(link):
    if(link not in output_links):
        output_links.add(link)
        return False 
    else:
        return True

#check if link is in blacklist
def inBlacklist(link):
    for item in blacklist:
        if item in link:
            return True
    return False

#check if it's the right person
def isRightPerson(title,description):
    real_name = original_name.lower()
    if(real_name in title.lower() or real_name in description.lower()):
        return True
    else: 
        return False

def for_images(title):
    if("images for" in title.lower()):
        return True
    else:
        return False

#Core search function
def google_search(keywords):
    driver = webdriver.Chrome()
    url="https://www.google.com/search?q="+keywords
    driver.maximize_window()
    driver.get(url)
    # time.sleep(1)
    content = driver.page_source.encode('utf-8').strip()
    soup = BeautifulSoup(content, 'html.parser')

    for e in soup.findAll('br'):
        e.extract()
    for s in soup('script'):
        s.extract()
    for s in soup('style'):
        s.extract()

    results =  soup.find_all(class_="g")

    for result in results:
        duplicate=False
        is_right_person = True
        no_for_image_page = True
        is_inblacklist = False
        #Get title elements
        result_title = result.find(class_="LC20lb")

        #Get Title Text
        title=''
        if(result_title):
            title = result_title.text
            no_for_image_page = not for_images(title)
        else:
            return

        #Get Title Link

        title_link = result.find(class_="r")
        if(result.find(class_="r")):
            title_link = title_link.find("a")
            title_link = title_link.get('href')
            duplicate = isDuplicate(title_link)
            is_inblacklist = inBlacklist(title_link)

        #Get description
        description=''
        result_description = result.find(class_="st")
        if(result_description):
            description = result_description.text
        else:
            return
        is_right_person = isRightPerson(title,description)
        if not duplicate and is_right_person and no_for_image_page and not is_inblacklist:
            all_results.append([title,title_link,description])

def main():
    for i in keywords:
        google_search(i)
    result = json.dumps(all_results)
    print(result)
    sys.stdout.flush()
    # f.writerow(row)

if __name__ == "__main__":
    # execute only if run as a script
    main()