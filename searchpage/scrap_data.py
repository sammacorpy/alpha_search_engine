import PyPDF2
import numpy as np
import csv

from .DocumentSearch import DocumentSearch
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from django.conf import settings
import os

TEXT_STORE_LOCATION = os.path.join(settings.FILES_DIR, "scrap_data")
DATA_STORE_LOCATION = os.path.join(settings.FILES_DIR, "dataset")
WORDS_DATA_LOCATION = os.path.join(settings.FILES_DIR, "words_data")

punctuations = ['(', ')', ';', ':', '[', ']', ',', '.', "'s", "-", "*"]
stop_words = stopwords.words('english')

doc = DocumentSearch()
allFiles = doc.search("pdf")
done = 0
total_words = 0

for i in allFiles:
    pdf = open(i, 'rb')
    reader = PyPDF2.PdfFileReader(pdf)
    text = ""
    n = reader.numPages
    for j in range(n):
        obj = reader.getPage(j)
        text += obj.extractText()
    tokens = word_tokenize(text, 'english')

    words = [word.lower() for word in tokens if not word.lower() in stop_words and not word.lower() in punctuations]

    unique_elements, count_elements = np.unique(words, return_counts=True)

    np.asarray((unique_elements, count_elements))

    index_elements = []
    writeData = [[a for a in unique_elements]]

    for j in unique_elements:
        # index_elements.append([indexes for indexes, value in enumerate(words) if value == j])
        writeData.append([j, count_elements[list(unique_elements).index(j)], [z for z, val in enumerate(words) if val == j]])
        total_words += count_elements[list(unique_elements).index(j)]

    with open(WORDS_DATA_LOCATION+"/"+str(allFiles.index(i))+".csv", 'w') as words_data_file:
        writer = csv.writer(words_data_file)
        writer.writerows(writeData)

    scraped = open(TEXT_STORE_LOCATION+"/"+str(allFiles.index(i)), 'w')
    scraped.write(i+"\n"+("\n".join(words)))
    scraped.close()
    done += 1
    print("Progress ", done, "/", len(allFiles))

with open(WORDS_DATA_LOCATION+"/total", 'w') as w:
    w.write(str(total_words))
