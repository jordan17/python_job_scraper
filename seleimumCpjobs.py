from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from datetime import datetime,timedelta
from pymongoExample import pyMongo
from jobContents import jobContents,jobConstants
import time
from urllib import request
from bs4 import BeautifulSoup
from lxml import html
import sys
import mysqlimport

keywords = ["experience","java"]
previousDate = jobConstants.previousDate
def remove_tags(text):
    try:
        return html.fromstring(text).text_content()
    except:
        return text

def grab_cpjobs(url):
    mongo = pyMongo()
    try:
        print(sys.argv[1])
        filename = "log/"+time.strftime("%Y%m%d-%H%M%S")+'-cpjobs.log'
        fileout = open(filename,"w")
        sys.stdout = fileout
    except:
        pass
    driver = webdriver.Chrome()
    page=1
    count=1
    errorcount=0
    previousrun = previousDate
    try:
        previousrun = datetime.strptime(sys.argv[1],"%Y/%m/%d")-timedelta(days=1)
    except IndexError:
        pass
    lastestdate = datetime.now()
    while previousrun <=  lastestdate:
        driver.get(url+str(page))
        if page == 1:
            driver.execute_script("switchMode('summary')")
        #assert "Software" in driver.title
        time.sleep(3)
        elem_list = driver.find_elements_by_xpath("//*[@id='list_container']/div[2]/ul/li")
        print("page"+str(page))
        for element in elem_list:
            try:
                time.sleep(3)
                print("count:"+str(count))
                title = element.find_element_by_xpath("h2/a")
                print(title.get_attribute("innerHTML"))
                name = element.find_element_by_xpath("p/a")
                print(name.get_attribute("innerHTML"))
                date1 = element.find_element_by_xpath("label[@class='date']")
                date2 = date1.get_attribute("innerHTML")
                date3 = datetime.strptime(date2,"%d/%m/%Y")
                if element.get_attribute("class") != "priority":
                    lastestdate = date3
                print(date3)
                joburl = title.get_attribute("href")
                jobpage = request.urlopen(joburl)
                soup = BeautifulSoup(jobpage,"lxml")
                content =  soup.body.find("div",{"class": "desc"}).contents
                content_filter = [k for k in content if (k != '\n' and k != "," and "counter.adcourier" not in k)]
                experience_filter = []
                skill_filter = set()
                for content1 in content_filter:
                    try:
                        root = html.document_fromstring(str(content1))
                    except:
                        continue
                        #e = root.xpath('//a[contains(text(),"experience"]')
                        #experience_filter.append(e)
                    for tag in root.iter():
                        try:
                            if any(keyword in tag.text for keyword in jobContents.keywords):
                                experience_filter.append(tag.text)
                            skill_filter.update({skill for skill in jobContents.skills if skill in tag.text})
                        except:
                            pass
                # for k in experience_filter:
                #     print(k)
                skill = ",".join(str(e) for e in skill_filter)
                data = { "jobTtile":remove_tags(title.get_attribute("innerHTML")),
                          "company":remove_tags(name.get_attribute("innerHTML")),
                         "datePosted": date3,
                         "jobDesc": "".join(str(e) for e in content_filter),
                         "jobCate":"all IT",
                        "experience":str(experience_filter),
                         "skills":skill,
                         "url":joburl,
                         "origin":"cpjobs"}
                mongo.insert_jobsdb(data)
                mysqlimport.insertJob(data)
            except Exception as e:
                #print(data['jobTtile']+" "+data['company']+" failed.")
                errorcount = errorcount +1
                pass
            count = count+1
        page = page+1
    driver.quit()
    #driver.close()
    print(str(errorcount))
    fileout.close()


if __name__ == "__main__":
    grab_cpjobs("http://www.cpjobs.com/hk/jobs/information-technology/")