""" data pipeline functions """
import os
import requests
import json
import collections
import pandas as pd

"""
FUNCTIONS TO QUERY AND SAVE DATA
"""

def query(app_date_from = None, app_date_to = None, patent_number = None, assignee_organization = None, assignee_type = None):
    
    """
    Forms query string to pass into get_data()
    
    Inputs
    :app_date_*: string type, format '"YYYY-MM-DD"'
    :patent_number / assignee_organization / assignee_type: string type, format '["key1", "key2", ...]' or '"key1"'
    
    Outputs
    :query_str: string type
    """
    
    query_str = '{"_and":['
    
    if (app_date_from):
        query_str = query_str + '{"_gte":{"app_date":' + app_date_from + '}},'

    if (app_date_to):
        query_str = query_str + '{"_lte":{"app_date":' + app_date_to + '}},'

    if (patent_number):
        query_str = query_str + '{"patent_id":' + patent_number + '},'
        
    if (assignee_organization):
        query_str = query_str + '{"assignee_organization":' + assignee_organization + '},'

    if (assignee_type):
        query_str = query_str + '{"assignee_type":' + assignee_type + '},'
    
    query_str = query_str[:-1] + ']}'
    
    return query_str


def get_data(query_str, fields_str, options, filename, filepath):
    """
    Extract and save data from the PatentsView API.
    Saves each page of data (max 10,000 results) in a dictionary collection, which is later saved to file.
    
    Inputs
    :filename: string type, data filename for the fetched data
    :filepath: string type, data folder path
    :fields:string type, format '"field1", "field2",...'
    :app_date_*: string type, format '"YYYY-MM-DD"'
    :patent_id / assignee_organization / assignee_type: string type, format '["key1", "key2", ...]' or '"key1"
    
    Outputs
    :file: string type, file path of the saved data
    """
    
    # if filepath is provided, build complete path
    if (filepath):
        file_ = os.path.join(filepath,filename)
    else:
        file_ = filename

    page = 1
    data_list = collections.defaultdict(list)
    
    # request string needs to be a function of the page, in order to automate the process
    request_str = lambda page : 'http://www.patentsview.org/api/patents/query?q=' + query_str + '&f=' + fields_str + '&o=' + options(page)
    
    print('fetching first page')
    r = requests.get(request_str(page))
    data_list[page] = r.json()

    # continue until there are less than 10,000 results in the new page, which indicates the end of the results
    while (r.json()['count'] == 10000):

        if (r.status_code == 200): 
            page += 1
            print('fetching page', page)
            if (page == 11):
                print('page limit reached, double check data')
            r = requests.get(request_str(page))
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
    :fields:string type, format '"field1", "field2",...'
    :app_date_*: string type, format '"YYYY-MM-DD"'
    :patent_id / assignee_organization / assignee_type: string type, format '["key1", "key2", ...]' or '"key1"
    
    Outputs
    :file: string type, file path of the saved data
    """
    filename = filename + '.json'
    
    # build query string
    query_str = query(app_date_from, app_date_to, patent_number, assignee_organization, assignee_type)
    
    # build output fields string
    all_fields = ('["patent_number", "assignee_latitude", "assignee_longitude",'
                  '"cited_patent_number", "inventor_latitude", "inventor_longitude",'
                  '"inventor_lastknown_latitude", "inventor_lastknown_longitude",'
                  '"patent_type", "app_date", "assignee_organization", "assignee_type"]')
    
    # add extra fields, if any
    if (fields):
        all_fields = all_fields[:-1] + ', ' + fields + ']'
    
    # set options such that the query returns the maximum number of results per page (10,000)
    # the get_data function will take care of getting the results for all the pages,
    # though the maximum number of results per query is set at (100,000) or 10 pages.
    options = lambda page : '{"page":' + str(page) + ',"per_page":10000}'
    
    # fetch the data from the PatentsView API
    file_ = get_data(query_str, all_fields, options, filename, filepath)

    return file_

"""
FUNCTIONS TO PROCESS DATA
"""

def counter_to_pandas(counter_object):
    """Function to convert the counter objects used in the data processing (json_to_pandas function) into Pandas DataFrame"""
    df = pd.DataFrame(data = list(counter_object.values()),index=counter_object.keys(), columns=['count'])
    df.sort_values(by=['count'],inplace=True,ascending=False)
    
    return df


def json_to_pandas(file_):
    """

    """
    # load json data file
    json_data = json.load(open(file_))
    
    # for certain data, we only need their distribution. To this end, we use Collections Counter objects
    assignee_type = collections.Counter()
    assignee_organization = collections.Counter()
    cited_patent_number = collections.Counter()
    
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
#                    if (assignee['assignee_type'] == None):
#                        print(patent['patent_number'])
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
              'assignee_type': assignee_type_df,
              'assignee_organization': assignee_organization_df,
              'cited_patent_number': cited_patent_number_df,
              'inventor_location': inventor_location,
              'inventor_lastknown_location': inventor_lastknown_location,
              'assignee_location': assignee_location}
    
    return output	
