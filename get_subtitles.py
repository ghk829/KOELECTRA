import numpy as np
import requests
from random import sample 
from bs4 import BeautifulSoup
import re
from urllib import request
import string
import pickle
import glob 

def flatten(A):
    rt = []
    for i in A:
        if isinstance(i,list): rt.extend(flatten(i))
        else: rt.append(i)
    return rt
def remove_tag(content):
    content=content.replace( '<br>',' ')
    content=re.sub('&nbsp;', '', content)
    content=re.sub('-', '\n', content)        
    cleanr =re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', content).strip()
    if '\n' in cleantext:
        cleantext=cleantext.split('\n')
    return cleantext


def has_only_latin_letters(name):
    char_set = string.printable
    return all((True if x in char_set else False for x in name))



def get_seq_id(pg_st=10, num_pg=5, den=50):
    subs={}
    pg_end=pg_st+num_pg
    for page in range(pg_st,pg_end):
        try: 
            if (page-pg_st)/den==0:
                print(str(round(((page-pg_st)/num_pg)*100,2)) +'% done.') 
            list_url="https://www.gomlab.com/subtitle/?preface=kr&page="+str(page)
            response = requests.get(list_url) 
            soup = BeautifulSoup(response.text, "lxml") 
            tb_id = soup.find('table', {'class':"tbl tbl_board transform"})
            for link in tb_id.find_all('a'):
                seq_start= link['href'].find('=')+1
                seq_end = link['href'].find('&')
                seq_id = link.get('href')[seq_start:seq_end]        

                sub_url='https://www.gomlab.com/subtitle/view.gom?seq='+str(seq_id)
                sub_response = requests.get(sub_url) 
                sub_soup = BeautifulSoup(sub_response.text, "lxml") 
                sub_tb=sub_soup.find('table', {'class':"tbl tbl_veiw mda"})
                if len(sub_tb.find_all('th'))==9:
                    sub_title=sub_tb.find_all('td')[5].text
                else: 
                    sub_title=sub_tb.find_all('td')[6].text

                sub_end=sub_title.rfind(' [')
                sub_name=sub_title[:sub_end].strip()

                subs[seq_id]=sub_name
        except:
            continue

    return subs

def download_subs(subs, den=100):
    for i, (seq_id, sub_name) in enumerate(subs.items()):
        if i!=0 and i%den==0:
            print(str(round(i/len(subs)*100)) +'% downloaded.') 
        download_url='https://www.gomlab.com/subtitle/download.gom?seq=' + str(seq_id)
        savename = "./data/" + sub_name
        try: 
            request.urlretrieve(download_url, savename)
        except:
            continue

def get_subs(data_path):
    try: 
        with open(data_path) as f:
            lines=f.readlines()
    except UnicodeDecodeError:
        try:
            with open(data_path, encoding='UTF-16') as f:
                lines=f.readlines()
        except:
            return False
    if lines[0]!='<SAMI>\n':
        return False
    sub_lines=[remove_tag(l) for l in lines if (not has_only_latin_letters(l)) and (not l.strip().startswith('font'))]
    sub_lines=flatten(sub_lines)
    sub_lines=[i for i in sub_lines if i]
    return data_path, sub_lines

def sub_final(den=1000):
    sub_dict={}
    files=glob.glob("./data/*.smi")
    l=len(files)
    for i, file in enumerate(files):
        if i in np.arange(0,l, den):
            print(str(round(i/l*100)) +'% done.') 
        try:
            data_name, sub_lines=get_subs(file)
            sub_dict[data_name]=sub_lines
        except:
            continue
    return sub_dict


#into one string
#' '.join(sub_lines)


if __name__ == "__main__":
	sub_g=sub_final()
	f = open("file.pkl","wb")
	pickle.dump(sub_g,f)
	f.close()

