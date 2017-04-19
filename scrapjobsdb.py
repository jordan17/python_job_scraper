import requests
from lxml import html

session_requests = requests.session()
login_url ="https://hk.jobsdb.com/hk/en/login/jobseekerlogin"
result = session_requests.get(login_url)
tree = html.fromstring(result.text)

payload = { "c_JbSrP1LnItDap_El0":	"li_17hk@yahoo.com.hk",
			"c_JbSrP1LnItDap_Pd0":	 "Jordan17" }
result = session_requests.post(
    login_url,
    data = payload,
    headers = dict(referer=login_url)
)

root_url = 'http://pyvideo.org'
index_url = root_url + '/category/50/pycon-us-2014'

def get_video_page_urls():
    response = requests.get(index_url)
    soup = bs4.BeautifulSoup(response.text,"lxml")
    return [a.attrs.get('href') for a in soup.select('div a[href^=/video]')]

print(get_video_page_urls())