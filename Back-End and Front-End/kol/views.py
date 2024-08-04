import json
import os
import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime
from django.shortcuts import HttpResponse, render
from kol.models import KolInfo, KolPubList
from django.conf import settings
import unicodedata

file_map = {
    1: ('Immunology', 'data_chronic_urticaria.json', 'res_chronic_urticaria.json'),
    2: ('Immunology', 'data_lupus_erythematosus.json', 'res_lupus_erythematosus.json'),
    3: ('Immunology', 'data_rheumatoid_arthritis.json', 'res_rheumatoid_arthritis.json'),
    4: ('Oncology', 'data_dlbcl.json', 'res_dlbcl.json'),
    5: ('Oncology', 'data_pancreatic_adenocarcinoma.json', 'res_pancreatic_adenocarcinoma.json'),
    6: ('Oncology', 'data_uterine_cervical_cancer.json', 'res_uterine_cervical_cancer.json')
}

""" url: /search/?
    The main page for searching
"""
def search_view(request):
    query = dict()
    query_field_immunology = request.GET.get('immunology-area', '')
    query_field_oncology = request.GET.get('oncology-area', '')
    query_yoe = request.GET.get('yoe')
    query_pub_count = request.GET.get('pub_count')
    query_coauthorship_count = request.GET.get('coauthorship_count')

    # Sub-areas
    if query_field_immunology:
        if query_field_immunology == 'All':
            query['field__in'] = ['chronic_urticaria', 'rheumatoid_arthritis', 'lupus_erythematosus']
        else:
            query['field__contains'] = query_field_immunology.lower().split(' ')[0]

    if query_field_oncology:
        if query_field_oncology == 'All':
            query['field__in'] = ['dlbcl', 'pancreatic_adenocarcinoma', 'uterine_cervical_cancer']
        else:
            query['field__contains'] = query_field_oncology.lower().split(' ')[0]

    # Years of experience
    if query_yoe:
        param = query_yoe.split(' ')[0]
        match param:
            case '1':   
                query['yoe__range'] = [0, 1]
            case '5':   
                query['yoe__range'] = [1, 5]
            case '10':  
                query['yoe__range'] = [5, 10]
            case 'More':
                query['yoe__gt'] = 10

    # Number of publication
    if query_pub_count:
        param = query_pub_count.split(' ')[0]
        match param:
            case 'Less':   
                query['pub_count__range'] = [0, 2]
            case '2':   
                query['pub_count__range'] = [2, 5]
            case '5':  
                query['pub_count__range'] = [5, 10]
            case 'More':
                query['pub_count__gt'] = 10

    # Number of co-authorship
    if query_coauthorship_count:
        param = query_coauthorship_count.split(' ')[0]
        match param:
            case 'Less':   
                query['coauthorship_count__range'] = [0, 20]
            case '20':   
                query['coauthorship_count__range'] = [20, 40]
            case '40':  
                query['coauthorship_count__range'] = [40, 60]
            case 'More':
                query['coauthorship_count__gt'] = 60

    if not query:
        return render(request, 'search.html')

    # Do the SELECT query
    kol_list = KolInfo.objects.filter(**query).order_by('score')
    ret_list = []
    # y1 = []
    # y2 = []
    # y3 = []
    for kol in kol_list:
        # y1.append(kol.pub_count)
        # y2.append(kol.coauthorship_count)
        # y3.append(kol.yoe)
        info = {
            'name': kol.name,
            'affiliation': kol.affiliation.split(';')[0],
            'score': round(2000 / kol.score, 4),
        }

        ret_list.append(info)
    
    # x = [i for i in range(1, 51)]
    # plt.plot(x,y1, label='pub count')
    # plt.plot(x,y2, label='coauthorship')
    # plt.plot(x,y3, label='YoE')
    # plt.legend()
    # plt.savefig("mygraph.png")

    return render(request, 'search.html', {'results': ret_list})

    # results = KolInfo.objects.filter(**query)
    # return render(request, 'search.html', {'results': results})


""" url: /info/?name=kol_name
    Show the detailed information of a specific KOL
"""
def get_info(request):
    kol_name = request.GET['name']
    print(kol_name)

    # Select KOL info by name
    kol_info = KolInfo.objects.filter(name=kol_name).first()
    # Select KOL publication list
    kol_pubs = KolPubList.objects.filter(name=kol_name)

    pub_list = []
    for pub in kol_pubs:
        pub_list.append(pub.article_title)

    s = 2000 / kol_info.score
    info = {
        'name': kol_info.name,
        'field': kol_info.field,
        'affiliation': kol_info.affiliation,
        'coauthorship_count': kol_info.coauthorship_count,
        'yoe': kol_info.yoe,
        'score': round(2000 / kol_info.score, 4),
        'pub_count': kol_info.pub_count,
        'pub_list': pub_list
    }

    # ret = json.dumps(info)
    return render(request, 'info.html', {'person': info})


""" url: /add/
    Add data to the database
"""
def add_all_data(request):
    for file_id in file_map.keys():
        add_data(request, file_id)
    return HttpResponse('All data inserted successfully!')

def add_data(request, file_id):
    if file_id is None:
        return HttpResponse('Please provide a valid file ID.')

    if file_id not in file_map:
        return HttpResponse('Invalid file ID')

    directory, data_file, res_file = file_map[file_id]

    DATA_FILE_PATH = os.path.join(settings.BASE_DIR, 'kol', 'data', directory, data_file)
    with open(DATA_FILE_PATH, 'r', encoding='utf-8') as fp:
        row_datas = json.load(fp)

    TOP_KOL_FILE_PATH = os.path.join(settings.BASE_DIR, 'kol', 'data', directory, res_file)  
    with open(TOP_KOL_FILE_PATH, 'r', encoding='utf-8') as fp:
        top_kols = json.load(fp)

    nodes = dict()
    index = 0
    for data in row_datas:
        authors = data['AuthorList']
        for author in authors:
            if author not in nodes:
                nodes[author] = index
                index += 1

    print('Total number of authors (nodes): ' + str(len(nodes)))

    edges = []
    for data in row_datas:
        authors = data['AuthorList']
        for i in range(0, len(authors)):
            for j in range(i + 1, len(authors)):
                first_author = nodes[authors[i]]
                second_author = nodes[authors[j]]
                edge = {
                    'source': first_author,
                    'target': second_author
                }
                edges.append(edge)

    print('Total number of edges: ' + str(len(edges)))

    kol_graph = nx.Graph()

    for kol_name, id in nodes.items():
        kol_graph.add_node(id, name=kol_name)

    for edge in edges:
        source = edge['source']
        target = edge['target']
        kol_graph.add_edge(source, target)

    for kol in top_kols:
        name = kol['kol_name']
        index = nodes[name]
        field = DATA_FILE_PATH.split('.')[-2].split('/')[-1][5:]
        affiliation = ''
        latest_time = datetime(1900, 1, 1)
        for data in row_datas:
            if name not in data['AuthorList']:
                continue

            if 'Years' in data and data['Years']:
                year = int(data['Years'][0]['Year'])
                month = int(data['Years'][0]['Month'])
                day = int(data['Years'][0]['Day'])
                pub_date = datetime(year, month, day)
            else:
                pub_date = datetime.now() 

            if pub_date.__gt__(latest_time):
                for i in range(len(data['AuthorList'])):
                    if name == data['AuthorList'][i]:
                        affiliation = data['AffiliationList'][i]
            
            latest_time = pub_date

        affiliation = affiliation.replace("'", "''")
        affiliation = affiliation.replace('"', '""')

        coauthorship_count = 0
        for e in kol_graph.edges:
            if index == e[0] or index == e[1]:
                coauthorship_count += 1

        yoe = kol['kol_yoe'] // 1 + 1
        score = kol['kol_score']

        pub_count = 0
        for data in row_datas:
            if name in data['AuthorList']:
                pub_count += 1
                title = data['ArticleTitle']

                title = unicodedata.normalize('NFC', title)
                title = title.encode('utf-8', 'ignore').decode('utf-8')
                title = title.replace("\\'", "\\'\\'")
                title = title.replace("'", "''")
                title = title.replace('"', '""')

                try:
                    KolPubList.objects.create(name=name, article_title=title)
                except Exception as e:
                    print(f"Error inserting title: {title}, error: {e}")               

        KolInfo.objects.create(name=name, 
                               field=field, 
                               affiliation=affiliation, 
                               score=score, 
                               pub_count=pub_count, 
                               coauthorship_count=coauthorship_count, 
                               yoe=yoe)

    return HttpResponse('Data Insert Success!')
