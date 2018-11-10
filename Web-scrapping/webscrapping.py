from bs4 import BeautifulSoup
import requests #https connection client
import re #regular expression
from langdetect import detect #language detection
from translate import Translator #translation

url = 'https://www.hindustantimes.com/'
response = requests.get(url)
html = response.content


full_page = BeautifulSoup(html, 'html.parser') #getting full page
list_news_head=full_page.find_all('a') #extracting all <a> tag contents.because only <a> tag consists all news.

list_news=[] #empty list for only news(without tag and link)

for i in list_news_head:
    list_news.append(i.get_text()) #getting only news
    
#cleaning
for i in range (len(list_news)):
    list_news[i]=re.sub('\s+',' ', list_news[i]) #cleaning '\s\t\n..' and all
    
preprocessed_news=[] #preprocessed all news
for i in range (len(list_news)): #removing sentences those have less than words e.g: know more,about us,home,feedback.... 
    z=list_news[i].split()
    if (len(z)>4):
        preprocessed_news.append(list_news[i])
        
for i in range (len(preprocessed_news)):
    lang = detect(preprocessed_news[i]) #as it contains punjabi news also,here am detecting which one is in punjabi language
    if (lang == 'pa'):
        translator= Translator(from_lang=lang,to_lang="EN") #transslating punjabi to english
        preprocessed_news[i]=translator.translate(preprocessed_news[i])
        
import csv #library for reading csv

with open('news.csv', 'w') as myfile:
    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    wr.writerow(preprocessed_news) #saving in csv
#saving into a csv file. (in instruction you have mentioned to save in row.)



