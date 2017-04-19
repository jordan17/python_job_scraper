from selenium import webdriver
from datetime import datetime,timedelta
from pymongoExample import pyMongo
import requests
from bs4 import BeautifulSoup
from lxml import html
import sys
import time
import mysqlimport
from jobContents import jobContents,jobConstants
def remove_tags(text):
    try:
        return html.fromstring(text).text_content()
    except:
        return text

# keywords = ["experience"]
# sample = ["experience 123","Java 41231","experience Java 133"]
# results = [s for s in sample if any(keyword in s for keyword in keywords)]
# print(results)
previousDate = jobConstants.previousDate
previousrun =previousDate
try:
    previousrun = datetime.strptime(sys.argv[1],"%Y/%m/%d")-timedelta(days=1)
    filename =  "log/"+time.strftime("%Y%m%d-%H%M%S")+'-jobsdb-softwaredeve.log'
    fileout = open(filename,"w")
    sys.stdout = fileout
except IndexError:
    pass

def grab_programmer(url):
    mongo = pyMongo()
    #profile = webdriver.FirefoxProfile()
    #profile.set_preference("javascript.enabled", False)
    #driver = webdriver.Firefox(profile)
    driver = webdriver.Chrome()
    filename =  "log/"+time.strftime("%Y%m%d-%H%M%S")+'-jobsdb-programmer.log'
    #fileout = open(filename,"w")
    # sys.stdout = fileout
    page=0
    count=1
    errorcount=0
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    lastestdate = datetime.now()
    while previousrun <=  lastestdate:
        #http://hk.jobsdb.com/HK/EN/Search/FindJobs?KeyOpt=COMPLEX&JSRV=1&RLRSF=1&JobCat=142,139,146,150&Career=4,3&JSSRC=HPAS&keepExtended=1 original
        #http://hk.jobsdb.com/HK/EN/Search/FindJobs?KeyOpt=COMPLEX&JSRV=1&RLRSF=1&JobCat=132,142,147,139,148&Career=4,3,2&JSSRC=JSRAS&keepExtended=1 sofrware development
        #http://hk.jobsdb.com/HK/EN/Search/FindJobs?KeyOpt=COMPLEX&JSRV=1&RLRSF=1&JobCat=132,139,141,142,146&Career=3,4&SearchFields=Positions&SalaryType=1&JSSRC=JSRAS&keepExtended=1&WFFBC=HK workalert software developement
        #http://hk.jobsdb.com/HK/EN/Search/FindJobs?KeyOpt=COMPLEX&JSRV=1&RLRSF=1&JobCat=131&SearchFields=Positions&Key=programmer%2Cjava%2Cdeveloper&Career=3,4&JSSRC=JSRAS&keepExtended=1&WFFBC=HK workalert programmer,java,developer
        #http://hk.jobsdb.com/HK/EN/Search/FindJobs?KeyOpt=COMPLEX&JSRV=1&RLRSF=1&JobCat=131&Career=3,4&JSSRC=JSRAS&keepExtended=1&WFFBC=HK workalert all IT
        #programmer
        driver.get(url+str(page))
        #software development
        #driver.get("http://hk.jobsdb.com/HK/EN/Search/FindJobs?KeyOpt=COMPLEX&JSRV=1&RLRSF=1&JobCat=132,139,141,142,146&SearchFields=Positions&Career=3,4&SalaryType=1&JSSRC=JSRAS&keepExtended=1&WFFBC=HK&page="+str(page))
        #assert "Software" in driver.title
        source =  driver.page_source
        soup1 = BeautifulSoup(source,"lxml")
        elems = soup1.body.findAll("div",attrs={"class":"result-sherlock-cell"})
        #elems = driver.find_elements_by_class_name("result-sherlock-cell")
        print("page"+str(page))
        for element in elems:
            try:
                #if "promo-ja" in element.get_attribute("class"):
                if "promo-ja" in element.attrs['class']:
                    continue
                time.sleep(3)
                #print("count:"+str(count))
                #title = element.find_element_by_id("cp"+str(count))
                title = element.find("a",attrs={"id":"cp"+str(count)})
                #print(title.get_attribute("innerHTML"))
                #print(title.text)
                #name = element.find_element_by_tag_name("meta")
                name = element.find("meta")
                #print(name.get_attribute("content"))
                #print(name.attrs["content"])
                #date1 = element.find_element_by_class_name("job-quickinfo")
                date1 = element.find("div",attrs={"class":"job-quickinfo"})
                #date2=date1.find_element_by_tag_name("meta")
                date2 = date1.find("meta")
                #date3 = datetime.strptime(date2.get_attribute("content"),"%d-%b-%y")
                date3 = datetime.strptime(date2.attrs["content"],"%d-%b-%y")
                #print(date3)
                lastestdate = date3
                #link = title.get_attribute("href")
                link=title.attrs["href"]
                #jobpage = request.urlopen(link)
                jobpage = requests.get(link,headers)
                soup = BeautifulSoup(jobpage.text,"lxml")
                content = soup.body.find("div",attrs={"class":"jobad-primary-details"}).contents
                content_filter = [k for k in content if (k != "\n" and k != "," and "counter.adcourier" not in k)]
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
                #     print(str(k))
                # data = { "jobTtile":remove_tags(title.get_attribute("innerHTML")),
                #           "company":remove_tags(name.get_attribute("content")),
                #          "datePosted": date3,
                #          "jobDesc": str(content_filter),
                #          "jobCate":"programmer",
                #         "experience":str(experience_filter),
                #          "url":link,
                #          "origin":"jobsdb"}

                skill = ",".join(str(e) for e in skill_filter)
                data = { "jobTtile":remove_tags(title.text),
                          "company":remove_tags(name.attrs["content"]),
                         "datePosted": date3,
                         "jobDesc": "".join(str(e) for e in content_filter),
                         "jobCate":"programmer",
                        "experience":str(experience_filter),
                         "skills":skill,
                         "url":link,
                         "origin":"jobsdb"}
                mongo.insert_jobsdb(data)
                mysqlimport.insertJob(data)
            except Exception as e:
                print(e)
                print("failed.")
                errorcount += 1;
                pass
            count = count+1
        page = page+1
    #fileout.close()
    print("error count:"+str(errorcount))
    driver.quit()
    #driver.close()

if __name__ == "__main__":
    #http://hk.jobsdb.com/HK/EN/Search/FindJobs?KeyOpt=COMPLEX&JSRV=1&RLRSF=1&JobCat=150,137&keepExtended=1&JSSRC=JSRSB&WFFBC=HK &page=
    #http://hk.jobsdb.com/HK/EN/Search/FindJobs?KeyOpt=COMPLEX&JSRV=1&RLRSF=1&JobCat=131&SearchFields=Positions&Key=programmer%2Cjava%2Cdeveloper&Career=3,4&JSSRC=JSRAS&keepExtended=1&WFFBC=HK &page=
    #http://hk.jobsdb.com/HK/EN/Search/FindJobs?KeyOpt=COMPLEX&JSRV=1&RLRSF=1&JobCat=132,139,141,142,146&SearchFields=Positions&Career=3,4&SalaryType=1&JSSRC=JSRAS&keepExtended=1&WFFBC=HK&page=
    grab_programmer("http://hk.jobsdb.com/HK/EN/Search/FindJobs?KeyOpt=COMPLEX&JSRV=1&RLRSF=1&JobCat=150,137&keepExtended=1&JSSRC=JSRSB&WFFBC=HK &page=")
    #print("first function ended")
    grab_programmer("http://hk.jobsdb.com/HK/EN/Search/FindJobs?KeyOpt=COMPLEX&JSRV=1&RLRSF=1&JobCat=131&SearchFields=Positions&Key=programmer%2Cjava%2Cdeveloper&Career=3,4&JSSRC=JSRAS&keepExtended=1&WFFBC=HK&page=")
    #print("second function ended")
    grab_programmer("http://hk.jobsdb.com/HK/EN/Search/FindJobs?KeyOpt=COMPLEX&JSRV=1&RLRSF=1&JobCat=132,139,141,142,146&SearchFields=Positions&Career=3,4&SalaryType=1&JSSRC=JSRAS&keepExtended=1&WFFBC=HK&page=")
    print("third function ended")
    #grab_software_development()
    fileout.close()