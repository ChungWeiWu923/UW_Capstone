import json
from Bio import Entrez


# data_chronic_urticaria
# data_rheumatoid_arthritis
# data_lupus_erythematosus

DATA_FILE_PATH = './data/pmid_lupus_erythematosus.txt'

SAVE_FILE_NAME = './data/Immunology/data_lupus_erythematosus.json'

# if the number of authors for a certain paper is greater than N, 
# then just get fisrt N authors
GET_FISRT_N_AUTHOR = 8


""" 0 read data
"""
pmid_list = []
paper_datas = []

with open(DATA_FILE_PATH, encoding='utf-8') as f:
    for line in f:
        pmid_list.append(line.strip())


""" 1 set search parameters
"""
Entrez.email = 'your_email'


""" 2 search the data base
"""
step = len(pmid_list) // 10000
if len(pmid_list) % 10000 != 0:
    step += 1

for i in range(step):
    if i == step - 1:
        temp_pmid_list = pmid_list[10000*i:]
    else:
        temp_pmid_list = pmid_list[10000*i:10000*(i+1)-1]

    handle = Entrez.efetch(db='pubmed', id=temp_pmid_list, rettype='xml')
    records = Entrez.read(handle)
  

    """ 3 build saving data
    """
    for record in records['PubmedArticle']:
        # with open(SAVE_FILE_NAME, 'w', encoding='utf-8') as jsonfile:
        #     json.dump(record, jsonfile, ensure_ascii=False, indent=4)
        #     exit()

        # get PMID
        title = record['MedlineCitation']['Article']['ArticleTitle']
        pmid = record['MedlineCitation']['PMID']
        years = record['MedlineCitation']['Article']['ArticleDate']

        # get author list
        if 'MedlineCitation' in record and \
            'Article' in record['MedlineCitation'] and \
            'AuthorList' in record['MedlineCitation']['Article']:
            author_list = []
            affiliation_list = []
            authors = record['MedlineCitation']['Article']['AuthorList']

            count = 0
            for author in authors:
                if count >= GET_FISRT_N_AUTHOR:
                    break
                
                if 'LastName' in author and 'ForeName' in author:
                    # get author name
                    author_name = ' '.join([author['ForeName'], author['LastName']])
                    author_list.append(author_name)

                    # get author affiliation
                    if 'AffiliationInfo' in author and len(author['AffiliationInfo']) != 0:
                        for affiliation in author['AffiliationInfo']:
                            if 'Affiliation' in affiliation and len(affiliation['Affiliation']) != 0:
                                affiliation_list.append(affiliation['Affiliation'])
                            else:
                                affiliation_list.append('null')
                            break
                    else:
                        affiliation_list.append('null')

                    count += 1

            if len(author_list) < 2:
                continue

        # build saving data
        paper_data = {
            'ArticleTitle': title,
            'AuthorList': author_list,
            'AffiliationList': affiliation_list,
            'Years': years
        }
        paper_datas.append(paper_data)


""" 4 save data
""" 
with open(SAVE_FILE_NAME, 'w', encoding='utf-8') as jsonfile:
    json.dump(paper_datas, jsonfile, ensure_ascii=False, indent=4)   
