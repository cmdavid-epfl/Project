""" data pipeline functions """
import os
import requests
import json
import collections
import time
import pandas as pd

"""
FUNCTIONS TO QUERY AND SAVE DATA
"""

def query(app_date_from, app_date_to, patent_number):
    
    """
    Forms query filters string to pass into get_data()
    querying for specific patent numbers is incompatible with any other filters.
    
    Inputs
    :app_date_*: string type, format 'YYYY-MM-DD'
    :patent_number / assignee_organization / assignee_type: string type, format ['key1', 'key2', ...] or 'key1'
    
    Outputs
    :query_str: string type, complete query string to pass into get_data()
    """    
    ands = []
    
    if (app_date_from):
        ands.append({'_gte':{'app_date':app_date_from}})

    if (app_date_to):
        ands.append({'_lte':{'app_date':app_date_to}})
    
    query_str = {'_and':ands}
    
    if (patent_number):
        query_str = {'patent_number':patent_number}
        
        if (app_date_from) or (app_date_to):
            print('patent_number queried. other inputs ignored')
    
    return query_str


def get_data(query_str, fields_str, options, filename, filepath):
    """
    Extract and save data from the PatentsView API.
    Saves each page of data (max 10,000 results) in a dictionary collection, which is then saved to file.
    
    Inputs
    :query_str: string type, should be output from query() function
    :fields_str: string type, format ['field1', 'field2', ...]
    :filename: string type, data filename for the fetched data
    :filepath: string type, data folder path
    
    Outputs
    :file_: string type, complete file path of the saved data
    """
    
    # if filepath is provided, build complete path
    if (filepath):
        file_ = os.path.join(filepath,filename)
    else:
        file_ = filename

    page = 1
    data_list = collections.defaultdict(list)
    
    print(len(json.dumps(query_str)))

    # API documentation states that a query longer than 2000 characters can use post method
    if (len(json.dumps(query_str)) > 1800):
        
        payload = lambda page : {'q': query_str,
                                 'f': fields_str,
                                 'o': options(page)}   

        fetch = lambda page : requests.post('http://www.patentsview.org/api/patents/query', data = json.dumps(payload(page)))
        
    else:
        query_str = json.dumps(query_str)
        fields_str = json.dumps(fields_str)        
        request_str = lambda page : 'http://www.patentsview.org/api/patents/query?q=' + query_str + '&f=' + fields_str + '&o=' + json.dumps(options(page))
        
        fetch = lambda page : requests.get(request_str(page))
    
    print('fetching first page')
    r = fetch(page)
    data_list[page] = r.json()

    # continue until there are less than 10,000 results in the new page, which indicates the end of the results
    while (r.json()['count'] == 10000):

        if (r.status_code == 200): 
            page += 1
            print('fetching page', page)
            # the documentation states that there is no hard limit on the queries, but through our experimentation,
            # the number of results often seems to be capped at 100,000.
            if (page == 11):
                print('page limit reached, double check data')
                
            time.sleep(600)
            
            r = fetch(page)
            data_list[page] = r.json()
        else:
            print('Error exit code :',r.status_code)
            print(r.headers())
    
    if (r.status_code != 200):
        print('Error exit code :',r.status_code)
        print(r.headers())
    else:
        # save data
        print('saving data')
        with open(file_, 'w') as f:
            json.dump(data_list, f)
    
    return file_


def patentsviewAPI(filename, filepath = None, app_date_from = None, app_date_to = None, patent_number = None):
    """
    Build the query string parts (filters, output fields, output options) in the PatentsView API format
    
    Inputs
    :filename: string type, data filename (without extension) for the fetched data
    :filepath: string type, data folder path
    :fields:string type, format ['field1', 'field2', ...]
    :app_date_*: string type, format 'YYYY-MM-DD'
    :patent_number / assignee_organization / assignee_type: string type, format ['key1', 'key2', ...] or 'key1'
    
    Outputs
    :file_: string type, file path of the saved data
    """
    if (filename[-5:] != '.json'):
        filename = filename + '.json'
    
    # build query string
    query_str = query(app_date_from, app_date_to, patent_number)
    
    if (app_date_from) and (app_date_to):
        all_fields = ['assignee_latitude', 'assignee_longitude','cited_patent_number',
                      'inventor_latitude', 'inventor_longitude', 'patent_type',
                      'assignee_organization', 'assignee_type']
        
    else:
        all_fields = ['cited_patent_number','inventor_latitude','inventor_longitude', 'patent_type']
    
    # set options such that the query returns the maximum number of results per page (10,000)
    # the get_data function will take care of getting the results for all the pages,
    # though the maximum number of results per query seems to be set at (100,000) or 10 pages.
    options = lambda page : {'page': page, 'per_page': 10000}
    
    # fetch the data from the PatentsView API
    file_ = get_data(query_str, all_fields, options, filename, filepath)

    return file_


"""
FUNCTIONS TO PRE-PROCESS DATA
"""
def load_layers(file_):
    
    data = json.load(open(file_))
    
    for layer in data:
        data[layer]['inventors'] = pd.read_json(data[layer]['inventors'])
    
    return data
    

def get_layers_data(filename, filepath, patent_number, layers):
    
    if (filename[-5:] == '.json'):
        filename = filename[:-5]
    
    filenames = [filename + '_layer' + str(q) + '.json' for q in range(layers)]
    output_data = {}
    
    for i,file_ in enumerate(filenames):
        print(filepath,file_)
        if os.path.isfile(os.path.join(filepath,file_)):
            datafile = os.path.join(filepath,file_)
            print('already on file')
        else:
            datafile = get_cited_patents_data(file_, filepath, patent_number)
        
        cited_patents, inventors = load_layer_data(datafile)
        
        output_data[i] = {'cited_patents' : cited_patents,
                          'inventors' : inventors.to_json()}
        
        patent_number = cited_patents.copy()
        
    # save data
    print('saving data')
    file_ = os.path.join(filepath,filename + '.json')
    with open(file_, 'w') as f:
        json.dump(output_data, f)
        
    return file_


def get_cited_patents_data(filename, filepath, patent_numbers):
    
    data = {}
    i = 0
    while ((i+1)*100 < len(patent_numbers)):
        datafile = patentsviewAPI('temp.json', filepath, patent_number = patent_numbers[i*100:(i+1)*100])
        data[i] = json.load(open(datafile))
        i += 1

    datafile = patentsviewAPI('temp.json', filepath, patent_number = patent_numbers[i*100:])
    data[i] = json.load(open(datafile))
    
    file_ = os.path.join(filepath,filename)
    
    with open(file_, 'w') as f:
        json.dump(data, f)
    
    return file_


def load_layer_data(file_):

    cited_patent_list = []
    inventor_key_id = []
    inventor_latitude = []
    inventor_longitude = []
    
    json_data = json.load(open(file_))
    
    for fold in json_data:

        for page in json_data[fold]:
                
            for patent in json_data[fold][page]['patents']:
                
                if (patent['patent_type'] != 'reissue'):
                    
                    for inventor in patent['inventors']:
                        lat = inventor['inventor_latitude']
                        lon = inventor['inventor_longitude']
                        if (lat != '0.1') and (lat != None) and (inventor['inventor_key_id'] not in inventor_key_id) :
                            inventor_key_id.append(inventor['inventor_key_id'])
                            inventor_latitude.append(float(lat))
                            inventor_longitude.append(float(lon))

                    for cit_patent in patent['cited_patents']:
                        cit_pat_num = cit_patent['cited_patent_number']
                        if (cit_pat_num != None):
                            cited_patent_list.append(cit_pat_num)
                                    
    inventor_info = pd.DataFrame(data = {'latitude' : inventor_latitude,
                                         'longitude' : inventor_longitude}, index = inventor_key_id)
 
    return cited_patent_list, inventor_info


def load_preprocessed_data(files):
    """
    Converts saved json data from file to the cleaned format used for the data analysis. (see data_preprocessing.ipynb)

    Input
    :file_: path to files containing the json data, format ['file1','file2',...]

    Output
    :data: set containing the following elements:
     - inventors: Pandas DataFrame containing the data related to inventors.
     - assignees: Pandas DataFrame containing the data related to assignees.
     - patents: Collection containing the data related to patents.
     - citations: Pandas DataFrame containing the citations data for each patent in the dataset
    """

    assignee_key_id = []
    assignee_type = []
    assignee_org = []
    assignee_latitude = []
    assignee_longitude = []
        
    inventor_key_id = []
    inventor_latitude = []
    inventor_longitude = []
    inventor_assignee_key = []
        
    total_cited_patents_count = 0
    patent_type_count = collections.Counter()

    # parse json data and fill above objects
    for file_ in files: 
        # load json data file
        json_data = json.load(open(file_))

        for page in json_data:
            # when query limit is reached, the results are empty pages
            if (json_data[page]['patents'] != None):
                
                for patent in json_data[page]['patents']:
                    patent_type = patent['patent_type']

                    if (patent_type != 'reissue'):
                        patent_type_count[patent_type] += 1
                        
                        for assignee in patent['assignees']:
                            type_ = assignee['assignee_type']
                            org = assignee['assignee_organization']
                            lat = assignee['assignee_latitude']
                            lon = assignee['assignee_longitude']
                            assignee_key = assignee['assignee_key_id']
                            if (lat != '0.1') and (lat != None) and (type_ != None):
                                assignee_key_id.append(assignee_key)
                                assignee_type.append(type_)
                                assignee_org.append(org)
                                assignee_latitude.append(float(lat))
                                assignee_longitude.append(float(lon))
                        
                        for inventor in patent['inventors']:
                            lat = inventor['inventor_latitude']
                            lon = inventor['inventor_longitude']
                            if (lat != '0.1') and (lat != None):
                                inventor_key_id.append(inventor['inventor_key_id'])
                                inventor_latitude.append(float(lat))
                                inventor_longitude.append(float(lon))
                                inventor_assignee_key.append(assignee_key)
                                
                        for cit_patent in patent['cited_patents']:
                            if (cit_patent['cited_patent_number'] != None):
                                total_cited_patents_count += 1
                        
            else:
                print('error: empty page')


    # output formats
    assignee_info = pd.DataFrame(data = {'type' : assignee_type,
                                         'organization' : assignee_org,
                                         'latitude' : assignee_latitude,
                                         'longitude' : assignee_longitude}, index = assignee_key_id)
    inventor_info = pd.DataFrame(data = {'latitude' : inventor_latitude,
                                         'longitude' : inventor_longitude,
                                         'assignee' : inventor_assignee_key}, index = inventor_key_id)
    
    proportion_assignee_type_df = assignee_info.groupby(by='type').size().reset_index()
    proportion_assignee_type_df.set_index('type',inplace=True)
    
    assignee_info.drop_duplicates(inplace=True)
    
    patent_type_count_df = pd.DataFrame.from_dict(patent_type_count, orient='index').reset_index()
    patent_type_count_df.set_index('index', inplace = True)

    # assignee_type_count = assignees.groupby(key='type').size().reset_index()
    
    output = {'proportion_by_patent_type' : patent_type_count_df / sum(patent_type_count_df.values),
              'proportion_by_assignee_type' : proportion_assignee_type_df / sum(proportion_assignee_type_df.values),
              'num_patents' : sum(patent_type_count_df.values)[0],
              'num_citations' : total_cited_patents_count,
              'num_inventors' : len(inventor_info.index.unique()),
              'inventors' : inventor_info,
              'assignees' : assignee_info}
    
    return output

def get_full_year_data(year, filepath):
    
    filenames = [year + q for q in ['q1','q2','q3','q4']]
    date_from = [year + '-' + date for date in ['01-01','04-01','07-01','10-01']]
    date_to = [year + '-' + date for date in ['03-31','06-30','09-30','12-31']]

    output_datafiles = []
    
    for i,filename in enumerate(filenames):
        print(filepath,filename)
        if os.path.isfile(os.path.join(filepath,filename + '.json')):
            datafile = os.path.join(filepath,filename + '.json')
            print('already on file')
        else:
            datafile = patentsviewAPI(filename, filepath = filepath, app_date_from = date_from[i], app_date_to = date_to[i])
        output_datafiles.append(datafile)
        
    return output_datafiles