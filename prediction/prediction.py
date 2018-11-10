# -*- coding: utf-8 -*-
"""
Created on Sat Nov 10 17:29:40 2018

@author: OpenSource
"""
import ast
import pandas as pd
import numpy as np
import re
import nltk
from nltk.corpus import stopwords #nltk library
nltk.download('stopwords') #downloadin stopword dictionary
from collections import Counter #counting occurence
import heapq #for getting top values 


data = open("file.txt","r+") 
list_data= data.readlines()

list_cat=[]
list_head=[]
list_description=[]

#getting required data
for i in range (len(list_data)):
    list_data[i]=ast.literal_eval(list_data[i])
    list_cat.append(list_data[i]['category'].lower())
    list_head.append(list_data[i]['headline'].lower())
    list_description.append(list_data[i]['short_description'].lower())

cln_list_head=[]
cln_list_description=[]

def clean_sentence(sentence):
    clean_sentence = []
    # Convert to lower case
    sentence = sentence.lower()
    # Removing URLs
    sentence = re.sub(r'((www\.[\S]+)|(https?://[\S]+))', '', sentence)
    # Replace 2+ dots with space
    sentence = re.sub(r'\.{2,}', ' ', sentence)
    # Strip space, " and ' from sentence
    sentence = sentence.strip(' "\'')
    # Replace multiple spaces with a single space
    sentence = re.sub(r'\s+', ' ', sentence)
    words = sentence.split()

    en_stops = set(stopwords.words('english')) #stop words(the ,a ,of,for..)
    for word in words:
        word = preprocess_word(word)
        if word not in en_stops:
            clean_sentence.append(word)
                
    

    return ' '.join(clean_sentence)

def preprocess_word(word):
    # Remove punctuation
    word = word.strip('\'"?!,.():;')
    # Convert more than 2 letter repetitions to 2 letter
    # tryyyy --> try
    word = re.sub(r'(.)\1+', r'\1\1', word)
    # Remove - & '
    word = re.sub(r'(-|\')', '', word)
    return word

#preprocessing
for i in range(len(list_head)):
    cln_list_head.append(clean_sentence(list_head[i]))
    cln_list_description.append(clean_sentence(list_description[i]))

#convert those extracted list to Dataframe
df = pd.DataFrame({'heading':cln_list_head,'description':cln_list_description,'category':list_cat})         

train,test = np.split(df.sample(frac=1), [int(.7*len(df))]) #deviding dataset into 2 parts train and test (70% & 30%)

uniq_cat=df.category.unique()
train=train.reset_index() #reseting index
test=test.reset_index()

model_list1=[]
x_list=train['heading'].tolist()

#training part (finding the probability of  a perticular word in a category)
for i in range (len(x_list)):
    if (len(model_list1)==0):
        x=dict(Counter(x_list[i].split()))
        model_list1.append({train['category'][i]:x})
    else:
        flag=0
        var=0
        for j in range (len(model_list1)):
            if train['category'][i] in model_list1[j]:
                flag=1
                var=j
        if (flag==1):
            x=dict(Counter(x_list[i].split())) 
            for k in x:
                if k in model_list1[var][train['category'][i]]:
                    model_list1[var][train['category'][i]][k] = model_list1[var][train['category'][i]][k] + x[k]
                else:
                    model_list1[var][train['category'][i]][k]=x[k]
                    
        else:
            x=dict(Counter(x_list[i].split()))
            model_list1.append({train['category'][i]:x})
 
model_list2=[]
y_list=train['description'].tolist()


for i in range (len(y_list)):
    if (len(model_list2)==0):
        x=dict(Counter(y_list[i].split()))
        model_list2.append({train['category'][i]:x})
    else:
        flag=0
        var=0
        for j in range (len(model_list2)):
            if train['category'][i] in model_list2[j]:
                flag=1
                var=j
        if (flag==1):
            x=dict(Counter(y_list[i].split())) 
            for k in x:
                if k in model_list2[var][train['category'][i]]:
                    model_list2[var][train['category'][i]][k] = model_list2[var][train['category'][i]][k] + x[k]
                else:
                    model_list2[var][train['category'][i]][k]=x[k]
                    
        else:
            x=dict(Counter(y_list[i].split()))
            model_list2.append({train['category'][i]:x})       
            
            
            
            
            
#testing part
def testing_head(x):
    list_x=x.split()
    
    
    list1=[] 
    
    for i in list_x:
        dict_temp={}
        for j in model_list1:
            for l in j:
                for k in j[l]:
                    if (i==k):
                        dict_temp[l]=j[l][k]
        list1.append(dict_temp)
    for k in range (len(list1)):
        if(len(list1[k])!=0):
            tot=sum(list1[k].values())
            for l in list1[k]:
                list1[k][l]=(list1[k][l]/tot)*100
            
    temp1_dict={}
    for i in range (len(list1)):
        for j in list1[i]:
            if j in temp1_dict:
               temp1_dict[j] =temp1_dict[j]+list1[i][j]
            else:
               temp1_dict[j] = list1[i][j]

    return temp1_dict

def testing_desc(y):
    list_y=y.split()
    list2=[] 
    
    for i in list_y:
        dict_temp={}
        for j in model_list2:
            for l in j:
                for k in j[l]:
                    if (i==k):
                        dict_temp[l]=j[l][k]
        list2.append(dict_temp)
        
    for k in range (len(list2)):
        if(len(list2[k])!=0):
            tot=sum(list2[k].values())
            for l in list2[k]:
                list2[k][l]=(list2[k][l]/tot)*100
            
    temp2_dict={}
    for i in range (len(list2)):
        for j in list2[i]:
            if j in temp2_dict:
               temp2_dict[j] =temp2_dict[j]+list2[i][j]
            else:
               temp2_dict[j] = list2[i][j]
    return temp2_dict

# pass arguments here:
i1=test['heading'][5] #take test heading
i2=test['description'][5] #take test description

test_head= testing_head(i1)
test_desc=testing_desc(i2)

t1=heapq.nlargest(3, range(len(list(test_head.values()))), key=list(test_head.values()).__getitem__)
t2=heapq.nlargest(3, range(len(list(test_desc.values()))), key=list(test_desc.values()).__getitem__)
print('Heading::'+i1)
print('Description::'+i2)
                   
print("According to Heading")                
for i in t1:
    print('Categorey: '+repr(list(test_head.keys())[i])+' ==> '+'Vote: '+repr(list(test_head.values())[i]))
    
print('=============')
print("According to Description")                
for i in t2:
    print('Categorey: '+repr(list(test_head.keys())[i])+' ==> '+'Vote: '+repr(list(test_head.values())[i]))
