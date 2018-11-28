""" data pipeline functions """
import os
import requests
import json
import collections
import pandas as pd

"""
FUNCTIONS TO QUERY AND SAVE DATA
"""

def query(app_date_from, app_date_to, patent_number, assignee_organization, assignee_type):
    
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
        
    if (assignee_organization):
        ands.append({'assignee_organization':assignee_organization})

    if (assignee_type):
        ands.append({'assignee_type':assignee_type})
    
    query_str = {'_and':ands}
    
    if (patent_number):
        query_str = {'patent_number':patent_number}
    
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


def patentsviewAPI(filename, filepath = None, fields = None, app_date_from = None, app_date_to = None, patent_number = None, 
                   assignee_organization = None, assignee_type = None):
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
    query_str = query(app_date_from, app_date_to, patent_number, assignee_organization, assignee_type)
    
    # build output fields string
    all_fields = ['patent_number', 'assignee_latitude', 'assignee_longitude','cited_patent_number',
                  'inventor_latitude', 'inventor_longitude', 'inventor_lastknown_latitude', 
                  'inventor_lastknown_longitude','patent_type', 'app_date', 'assignee_organization', 'assignee_type']
    
    # add extra fields, if any
    if (fields):
        all_fields.append(fields)
    
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

def counter_to_pandas(counter_object):
    """Function to convert the counter objects used in the data processing (json_to_pandas function) into Pandas DataFrame"""
    df = pd.DataFrame(data = list(counter_object.values()),index=counter_object.keys(), columns=['count'])
    df.sort_values(by=['count'],inplace=True,ascending=False)
    
    return df


def json_to_pandas(file_):
    """
    Converts saved json data from file to a predefined format. (see data_preprocessing.ipynb)

    Input
    :file_: path to file containing the json data

    Output
    :output: set of Pandas DataFrames containing the data in a predefined format.
    """
    # load json data file
    json_data = json.load(open(file_))
    
    # for certain data, we only need their distribution. To this end, we use Collections Counter objects
    assignee_type = collections.Counter()
    assignee_organization = collections.Counter()
    cited_patent_number = collections.Counter()
    patent_type = collections.Counter()
    
    # for the rest of the data, we want to collect all of it and transfer it into Pandas Dataframes
    patent_number = []
    app_date = []
    inventor_latitude = []
    inventor_longitude = []
    inventor_lastknown_latitude = []
    inventor_lastknown_longitude = []
    assignee_latitude = []
    assignee_longitude = []
    assignee_patent_number = []
    inventor_patent_number = []
    
    # parse json data and fill above objects 
    for page in json_data:
        if (json_data[page]['patents'] != None):
            for patent in json_data[page]['patents']:
                patent_number.append(patent['patent_number'])
                patent_type[patent['patent_type']] += 1

                for inventor in patent['inventors']:
                    inventor_latitude.append(inventor['inventor_latitude'])
                    inventor_longitude.append(inventor['inventor_longitude'])
                    inventor_lastknown_latitude.append(inventor['inventor_lastknown_latitude'])
                    inventor_lastknown_longitude.append(inventor['inventor_lastknown_longitude'])
                    inventor_patent_number.append(patent['patent_number'])

                for assignee in patent['assignees']:
                    assignee_latitude.append(assignee['assignee_latitude'])
                    assignee_longitude.append(assignee['assignee_longitude'])
                    assignee_type[assignee['assignee_type']] += 1
                    assignee_organization[assignee['assignee_organization']] += 1
                    assignee_patent_number.append(patent['patent_number'])

                for application in patent['applications']:
                    app_date.append(application['app_date'])

                for cit_patent in patent['cited_patents']:
                    cited_patent_number[cit_patent['cited_patent_number']] += 1
        else:
            print('error: empty page')

    # output formats
    app_date = pd.DataFrame(data = {'app_date' : app_date}, index = patent_number)
    patent_type_df = counter_to_pandas(patent_type)
    assignee_type_df = counter_to_pandas(assignee_type)
    assignee_organization_df = counter_to_pandas(assignee_organization)
    cited_patent_number_df = counter_to_pandas(cited_patent_number)
    
    inventor_location = pd.DataFrame(data = {'lat' : inventor_latitude,
                                             'lon' : inventor_longitude}, index = inventor_patent_number)
    inventor_lastknown_location = pd.DataFrame(data = {'lat' : inventor_lastknown_latitude,
                                                       'lon' : inventor_lastknown_longitude}, index = inventor_patent_number)
    assignee_location = pd.DataFrame(data = {'lat' : assignee_latitude,
                                             'lon' : assignee_longitude}, index = assignee_patent_number)
    
    output = {'date':app_date,
              'patent_type':patent_type_df,
              'assignee_type': assignee_type_df,
              'assignee_organization': assignee_organization_df,
              'cited_patent_number': cited_patent_number_df,
              'inventor_location': inventor_location,
              'inventor_lastknown_location': inventor_lastknown_location,
              'assignee_location': assignee_location}
    
    return output


def data_clean(file_):
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
    # load json data file
    json_data = json.load(open(file_))
    
    # data objects
    assignee_key_id = []
    assignee_type = []
    assignee_org = []
    assignee_location = []
    
    inventor_key_id = []
    inventor_location = []
    inventor_last_location = []
    
    patent_data = {}
    
    cited_patent_number = collections.Counter()
    
    # parse json data and fill above collections 
    for page in json_data:
        # when query limit is reached, the results are empty pages
        if (json_data[page]['patents'] != None):
            for patent in json_data[page]['patents']:
                
                patent_assignees = []
                patent_inventors = []
                patent_number = patent['patent_number']
                patent_type = patent['patent_type']
                app_date = patent['applications'][0]['app_date']

                if (patent_type != 'reissue'):
                
                    for inventor in patent['inventors']:
                        lat = inventor['inventor_latitude']
                        lon = inventor['inventor_longitude']
                        l_lat = inventor['inventor_lastknown_latitude']
                        l_lon = inventor['inventor_lastknown_longitude']

                        if (lat != '0.1') and (lat != None) and (l_lat != '0.1') and (l_lat != None):
                            inventor_key_id.append(inventor['inventor_key_id'])
                            inventor_location.append((float(lat), float(lon)))
                            inventor_last_location.append((float(l_lat), float(l_lon)))

                            patent_inventors.append(inventor['inventor_key_id'])

                    for assignee in patent['assignees']:
                        type_ = assignee['assignee_type']
                        org = assignee['assignee_organization']
                        lat = assignee['assignee_latitude']
                        lon = assignee['assignee_longitude']

                        if (lat != '0.1') and (lat != None) and (type_ != None):
                            assignee_key_id.append(assignee['assignee_key_id'])
                            assignee_type.append(type_)
                            assignee_org.append(org)
                            assignee_location.append((float(lat), float(lon)))

                            patent_assignees.append(assignee['assignee_key_id'])

                    for cit_patent in patent['cited_patents']:
                        cit_pat_num = cit_patent['cited_patent_number']

                        if (cit_pat_num != None):
                            cited_patent_number[cit_patent['cited_patent_number']] += 1

                    if (len(patent_inventors) != 0):
                        patent_data[patent_number] = {'type' : patent_type,
                                                      'date' : app_date,
                                                      'inventors' : patent_inventors,
                                                      'assignees' : patent_assignees}
        else:
            print('error: empty page')


    # output formats
    assignee_data = pd.DataFrame(data = {'type' : assignee_type,
                                         'organization' : assignee_org,
                                         'location' : assignee_location}, index = assignee_key_id)
    inventor_data = pd.DataFrame(data = {'location' : inventor_location,
                                         'last_location' : inventor_last_location}, index = inventor_key_id)
    
    assignee_data.drop_duplicates(inplace=True)
    inventor_data.drop_duplicates(inplace=True)
    
    patent_data = pd.DataFrame(patent_data)
    citation_data = counter_to_pandas(cited_patent_number)
    
    output = {'assignees' : assignee_data,
              'inventors' : inventor_data,
              'patents' : patent_data.T,
              'citations' : citation_data}
    
    return output