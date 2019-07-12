from django.shortcuts import render,redirect
from django.http import HttpResponse
# from django.views.decorators.http import require_POST
# from .models import *
import time
from django.conf import settings
import os
# from .forms import todoform
import nltk
import csv
# from autocorrect import spell
from .DocumentSearch import DocumentSearch
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

TEXT_STORE_LOCATION = os.path.join(settings.FILES_DIR, "scrap_data")
DATA_STORE_LOCATION = os.path.join(settings.FILES_DIR, "dataset")
WORDS_DATA_LOCATION = os.path.join(settings.FILES_DIR, "words_data")
CLICKS_LOCATION = os.path.join(settings.FILES_DIR, "clicks.txt")
PDF_INDEX_LOCATION = os.path.join(settings.FILES_DIR, "pdfindex.txt")
# file_path = os.path.join(settings.FILES_DIR, 'test.txt')


def click_prob(a):
    return float(a)/(a+1)


def homepage(request):
    data = {'title': 'home'}
    return render(request, 'searchpage/home.html', data)


def get_prior(text):
    lst = ['NN', 'NNS', 'NNP', 'NNPS', 'FW', 'JJ', 'JJR', 'JJS', 'RB', 'RBR', 'RBS', 'VB', 'VBD', 'VBG', 'VBP', 'VBN', 'VBP', 'VBZ', 'PRP', 'DT', 'IN', 'CD', 'EX', 'LS', 'MD', 'PDT', 'POS', 'PRP$', 'RP', 'SYM', 'TO', 'UH', 'WDT', 'WP', 'WP$', 'WRB']
    lst.reverse()
    tagged = nltk.pos_tag(text)
    list1 = []
    for gp_i in tagged:
        gp_j = (lst.index(gp_i[1])+1)/len(lst)
        list1.append(str(gp_j))
    return list1


def search(request):
    if not request.GET['query']:
        return redirect('')
    query = request.GET['query']

    start_time = time.time()

    # f_query = ""
    # for i in query.split():
    #     f_query += spell(i)+" "
    # query = f_query
    punctuations = ['(', ')', ';', ':', '[', ']', ',', '.', "'s", '-']
    stop_words = stopwords.words('english')
    tokens = word_tokenize(query, 'english')
    words = [word.lower() for word in tokens if not word.lower() in stop_words and not word.lower() in punctuations]
    # print("\n".join(words))

    word_weights = get_prior(words)

    if words:
        doc = DocumentSearch()
        csvfiles = doc.search("csv")
        dic = {}

        indexes = [[], []]

        with open(PDF_INDEX_LOCATION, 'r') as w:
            indexes[0] = w.readline().split(" ")
            indexes[1] = w.readline().split(" ")

        with open(CLICKS_LOCATION, 'r') as clicksfile:
            clicks = list(map(int, clicksfile.readline().split(" ")))

        with open(WORDS_DATA_LOCATION+"/total", 'r', encoding="utf8") as w:
            words_count = int(w.readline())

        for csvData in csvfiles:
            with open(csvData, encoding="utf8") as f:
                reader = csv.reader(f)
                data = [list(d) for d in reader]
                # print(data)
                score = main_search(words, data, words_count, word_weights)*click_prob(clicks[int(csvData.split("/")[-1].split(".")[0])])
                if score in dic:
                    dic[score].append(csvData)
                else:
                    dic[score] = [csvData]

        end_time = time.time()
        total_time_taken = end_time - start_time

        finalres = []
        for i in sorted(dic.keys(), reverse=True):
            if i > float(0):
                for j in dic[i]:
                    # print(j)
                    with open(j.replace("words_data", "scrap_data",).replace(".csv", ""), encoding="utf8") as final:
                        loc = final.readline()
                    loc = (loc.split('dataset/')[-1]).strip("\n")
                    print(loc)
                    if loc not in finalres:
                        finalres.append(loc)

        print(finalres)
        data = {'query': query, 'title': 'search', 'results': finalres, 'total_time_taken': total_time_taken, 'lengthofres': len(finalres),'error': not len(finalres)}
        return render(request, 'searchpage/searchresult.html', data)
    else:
        return render(request, 'searchpage/searchresult.html', {'title': 'search','error':1,'total_time_taken': '0.00', 'lengthofres': 0,'query': query})


def proxy_dist(a, b):
    return float(1)/(abs(a-b)**2)


def main_search(m_words, m_data, w_count, prior):
    m_score = float(0)
    if len(m_words) > 1:
        for m_i in range(len(m_words)//2):
            if m_words[m_i] in m_data[0] and m_words[m_i+1] in m_data[0]:
                ind1 = m_data[m_data[0].index(m_words[m_i])+1][2]
                ind2 = m_data[m_data[0].index(m_words[m_i+1])+1][2]
                ind1 = list(map(int, ind1[1:-1].split(",")))
                ind2 = list(map(int, ind2[1:-1].split(",")))
                for m_a in ind1:
                    for m_b in ind2:
                        m_score += proxy_dist(m_a, m_b)
            else:
                if m_words[m_i] in m_data[0]:
                    m_score += float(m_data[m_data[0].index(m_words[m_i])+1][1])*float(prior[m_i])/w_count
                if m_words[m_i+1] in m_data[0]:
                    m_score += float(m_data[m_data[0].index(m_words[m_i+1])+1][1])*float(prior[m_i+1])/w_count
    elif m_words[0] in m_data[0]:
        m_score += float(m_data[m_data[0].index(m_words[0])+1][1])/w_count
    return m_score


def rank(request):
    clickednum = request.GET['clickedfile']

    indexes = [[], []]
    with open(PDF_INDEX_LOCATION, 'r') as w:
        indexes[0] = w.readline().split(" ")
        indexes[1] = w.readline().split(" ")

    with open(CLICKS_LOCATION, 'r') as clicksfile:
        clicks = list(map(int, clicksfile.readline().split(" ")))

    choosen_index = int(indexes[0][indexes[1].index("/root/Projects/Proximity-Based-IR-System/dataset/"+clickednum)])
    print("Index of choosen is", choosen_index)
    clicks[choosen_index] += 1
    with open(CLICKS_LOCATION, 'w') as w:
        w.write(" ".join([str(i) for i in clicks]))

    return HttpResponse(clickednum)
