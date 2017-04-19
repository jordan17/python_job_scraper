from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from datetime import datetime,timedelta
from pymongoExample import pyMongo
from jobContents import jobContents
import time
from urllib import request
from bs4 import BeautifulSoup
from lxml import html
import sys
import mysqlimport


def remove_tags(text):
    try:
        return html.fromstring(text).text_content()
    except:
        return text

def grab_fifa(url):
    mongo = pyMongo()
    driver = webdriver.Chrome()
    page=661
    count=1
    errorcount=0
    while page <=720:
        driver.get(url+str(page))

        elem_list = driver.find_elements_by_xpath("//tr[contains(@class,'js-player')]")
        print("page"+str(page))
        for element in elem_list:
            try:

                print("count:"+str(count))
                titles = element.find_elements_by_xpath("td[@class='player_club_name']/a/p")

                name = titles[0].get_attribute("innerHTML")
                print(name)
                #'R. Madrid｜ESP 1'
                #club = element.find_element_by_xpath("td[@class='player_club_name']/a/p[1]")
                club_league = titles[1].get_attribute("innerHTML").split('｜')
                nation_id = element.find_element_by_xpath("td[2]/a/p/img").get_attribute("src").split('_')[2].split('.')[0]
                print("club is "+club_league[0]+" league is "+club_league[1])
                lv =  element.find_element_by_xpath("td[5]/a/p").get_attribute("class").split(" ")[0]
                joburl = element.find_element_by_xpath("td/a").get_attribute("href")
                id = element.find_element_by_xpath("td/a").get_attribute("href").split("/")[5]
                rating = element.find_element_by_xpath("td[@class='rating']/a/p").get_attribute("innerHTML")
                position =  element.find_element_by_xpath("td[4]/a").get_attribute("innerHTML")
                #jobpage = request.urlopen(joburl)
                data = { "id":int(id),
                         "name":name,
                          "rating":int(rating),
                         "club": club_league[0],
                         "league": club_league[1],
                         "pos":position,
                        "pac":int(element.find_element_by_xpath("td[7]/a").get_attribute("innerHTML")),
                         "sho":int(element.find_element_by_xpath("td[8]/a").get_attribute("innerHTML")),
                         "pas":int(element.find_element_by_xpath("td[9]/a").get_attribute("innerHTML")),
                         "dri":int(element.find_element_by_xpath("td[10]/a").get_attribute("innerHTML")),
                         "def":int(element.find_element_by_xpath("td[11]/a").get_attribute("innerHTML")),
                         "phy":int(element.find_element_by_xpath("td[12]/a").get_attribute("innerHTML")),
                         "skill":element.find_element_by_xpath("td[13]/a").get_attribute("innerHTML"),
                         "weak_foot":element.find_element_by_xpath("td[14]/a").get_attribute("innerHTML"),
                         "wr":element.find_element_by_xpath("td[15]/a").get_attribute("innerHTML"),
                         "nation_id":int(nation_id),
                         "rare":lv
                         }
                mysqlimport.insertPlayer(data)
                #mysqlimport.updateNation(data)
                #mysqlimport.updateRare(data)
            except Exception as e:
                print(e)
                errorcount = errorcount +1
                pass
            count = count+1
        time.sleep(5)
        page = page+1
    driver.quit()
    print(str(errorcount))

def grab_nation(url):
    mongo = pyMongo()
    driver = webdriver.Chrome()
    id=251
    errorcount=0
    while id <=  400:
        driver.get(url+str(id))
        try:
            element = driver.find_element_by_xpath("//a[@class='js-selected_condition' and @data-name='q[nation_id_eq]']")
            print(element.text)
            data = { "nation_id":int(id),
                     "nation_name":element.text
                             }
            mysqlimport.insertNation(data)
        except Exception as e:
                print(e)
                errorcount = errorcount +1
        time.sleep(10)
        id=id+1
    driver.quit()
    print(str(errorcount))
if __name__ == "__main__":
    grab_fifa("https://fifa-gamers-pub.com/players/fifa17?per=25&q%5Bgame_version_id_eq%5D=2&q%5Bs%5D=&page=")
    #grab_nation("https://fifa-gamers-pub.com/players/fifa17?utf8=%E2%9C%93&q[s]=player_lowest_price_ps4_price+asc&q[attacking_work_rate_id_eq]=&q[defensive_work_rate_id_eq]=&q[foot_id_eq]=&q[player_traits_id_eq]=&q[player_specialities_id_eq]=&q[club_league_id_eq]=&q[club_id_eq]=&q[position_group_in]=&q[position_id_eq]=&q[card_type]=&q[has_real_face_eq]=&q[skill_moves_in_5]=false&q[skill_moves_in_4]=false&q[skill_moves_in_3]=false&q[skill_moves_in_2]=false&q[skill_moves_in_1]=false&q[weak_foot_in_5]=false&q[weak_foot_in_4]=false&q[weak_foot_in_3]=false&q[weak_foot_in_2]=false&q[weak_foot_in_1]=false&per=&custom_sort=&kit_number=&q[nation_id_eq]=")