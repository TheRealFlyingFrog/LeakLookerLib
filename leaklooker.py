from hurry.filesize import size
from colorama import Fore, init
import json
import sys
import argparse
from bs4 import BeautifulSoup
import requests
from pathlib import Path

# --> fix colorama windows bug 
init(convert=True)

# --> read from conf
conf_name = Path(r"config.json")
with open(str(conf_name), 'r') as config_file:
    conf = json.load(config_file)
BINARYEDGE_KEY = conf['apikeys']['binaryedge']['key']
# <--


BINARYEDGE_API_KEY = BINARYEDGE_KEY


def binaryedge_query(query,page):
    headers = {'X-Key': BINARYEDGE_API_KEY}
    end = 'https://api.binaryedge.io/v2/query/search?query='+query+'&page='+str(page)
    req = requests.get(end,headers=headers)
    req_json = json.loads(req.content)
  
    try:
        print("Total results: " + Fore.GREEN + str(req_json['total']) + Fore.RESET)
    except:
        print("Error with your query")
        sys.exit()
        
    return req_json['events']

def check_jenkins(results):
    if results:
        for service in results:
            print('http://'+service['target']['ip'] +":"+str(service['target']['port']))
            executors = set()
            jobs = set()

            try:
                html_code = service['result']['data']['response']['body']
                soup = BeautifulSoup(html_code, features="html.parser")
                for project in soup.find_all("a", {"class": "model-link inside"}):
                    if project['href'].startswith("/computer"):
                        splitted = project['href'].split("/")
                        executors.add(splitted[2])

                    elif project['href'].startswith("job"):
                        splitted = project['href'].split("/")
                        jobs.add(splitted[1])

                print(Fore.BLUE + "Executors" + Fore.RESET)
                for executor in executors:
                    print(Fore.CYAN + executor + Fore.RESET)

                print(Fore.BLUE + "Jobs" + Fore.RESET)
                for job in jobs:
                    print(Fore.CYAN + job + Fore.RESET)
            except:
                print(Fore.RED + "No information"+ Fore.RESET)
            print("-----------------------------")

def check_sonarqube(results):
    if results:
        for service in results:
            found = False
            print('http://'+service['target']['ip'] +":"+str(service['target']['port']))
            try:
                html_code = service['result']['data']['response']['body']
                if "Welcome to SonarQube Dashboard" in html_code:
                    soup = BeautifulSoup(html_code, features="html.parser")
                    for project in soup.find_all("a", href=True):
                        if "/dashboard/index" in project.attrs['href']:
                            print(Fore.GREEN + project.contents[0] + Fore.RESET)
                            found = True

                    if not found:
                        print("Open with no projects")

                elif service['result']['data']['response']['redirects']:
                    print(Fore.RED + "Authentication" + Fore.RESET)
                print("---------------------")
            except:
                print(Fore.RED + "Can't retrieve details" + Fore.RESET)
                print("Server status: " + service['result']['data']['state']['state'])
                print("---------------------")

def check_rsync(results):
    if results:
        for service in results:
            print('rsync://'+service['target']['ip'])
            print("Server status: " + service['result']['data']['state']['state'])
            try:
                print(Fore.GREEN + service['result']['data']['service']['banner'] + Fore.RESET,)
            except:
                print(Fore.RED + 'No information' + Fore.RESET)
            print("------------------------------")

def check_gitlab(results):
    if results:
        for service in results:
            print('https://' + service['target']['ip'] + ":" + str(service['target']['port']))
            html_code = service['result']['data']['response']['body']
            if "register" in html_code:
                soup = BeautifulSoup(html_code, features="html.parser")
                for project in soup.find_all("meta", {'property':"twitter:description"}):
                    print(Fore.GREEN + project.attrs['content'] + Fore.RESET)
                print(Fore.GREEN + "Registration is open" + Fore.RESET)
            else:
                print(Fore.RED + "Registration is closed. " + Fore.RESET + "Check public repositories. https://" + service['target']['ip'] + ":" + str(service['target']['port']) + "/explore")

            print("-----------------------")

def check_kibana(results):
    if results:
        for service in results:
            print('http://' + service['target']['ip'] + ":" + str(service['target']['port'])+"/app/kibana#/discover?_g=()")
            print("Server status: " + service['result']['data']['state']['state'])
            print("-----------------------")

def check_couchdb(results):
    if results:
        for service in results:
            print('https://' + service['target']['ip'] + ":" + str(service['target']['port']) +"/_utils")
            try:
                couch_json = json.loads(service['result']['data']['response']['body'])
                print("Status code: " + str(service['result']['data']['response']['statusCode']))
                print("Vendor: " + Fore.CYAN + couch_json['vendor']['name'] + Fore.RESET)
                print('Features:')
                for i in couch_json['features']:
                    print(Fore.GREEN + i + Fore.RESET)
            except Exception as e:
                if 'state' in service['result']['data']:
                    print("Server status: " + service['result']['data']['state']['state'])
                else:
                    print(Fore.RED + "Cannot retrieve information" + Fore.RESET)

            print("-----------------------------")

def check_mongodb(results):
    if results:
        for service in results:
            print('IP: ' + service['target']['ip'] + ":" + str(service['target']['port']))
            if not service['result']['error']:
                try:
                    if service['result']['data']['listDatabases']['totalSize'] > 217000000:
                        print("Size: " + Fore.LIGHTBLUE_EX + size(
                            service['result']['data']['listDatabases']['totalSize']) + Fore.RESET)

                        for database in service['result']['data']['listDatabases']['databases']:
                            if database['empty'] != 'true':
                                print("Database name: " + Fore.BLUE + database['name'] + Fore.RESET)
                                print("Size: " + Fore.BLUE + size(database['sizeOnDisk']) + Fore.RESET)
                                print('Collections: ')
                                for collection in database['collections']:
                                    print(Fore.LIGHTBLUE_EX + collection['name'] + Fore.RESET)
                        print("-----------------------------")
                    else:
                        print("Total size is only " + Fore.RED + str(service['result']['data']['listDatabases']['totalSize']) +Fore.RESET + " which is below default - 217000000")
                        print("-----------------------------")
                except:
                    pass
            else:
                print("Error: " + Fore.RED + service['result']['error'][0]['errmsg'] + Fore.RESET)
                print("-----------------------------")

def check_elastic(results):
    if results:
        for service in results:
            print('http://' + service['target']['ip'] + ":" + str(service['target']['port']) + "/_cat/indices")
            print("Cluster name: "+ Fore.LIGHTMAGENTA_EX + service['result']['data']['cluster_name'] + Fore.RESET)
            print("Indices:")
            try:
                for indice in service['result']['data']['indices']:
                    print("Name: " + Fore.GREEN + indice['index_name'] + Fore.RESET)
                    print("No. of documents: " +Fore.BLUE + str(indice['docs']) + Fore.RESET)
                    print("Size: " + Fore.LIGHTCYAN_EX + str(size(indice['size_in_bytes'])) + Fore.RESET)
            except:
                print("No indices")
            print("-----------------------------")

def check_listing(results):
    if results:
        for service in results:
            dir = False
            print('https://' + service['target']['ip'] + ":" + str(service['target']['port']))

            try:
                print("Product: " + Fore.MAGENTA + service['result']['data']['service']['product'] + Fore.RESET)

                if 'hostname' in service['result']['data']['service']:
                    print("Hostname: " + Fore.YELLOW + service['result']['data']['service']['hostname'] + Fore.RESET)
                html_code = service['result']['data']['service']['banner']
            except KeyError:
                if 'response' in service['result']['data']:
                    print("Status code: " + str(service['result']['data']['response']['statusCode']))
                    html_code = service['result']['data']['response']['body']
                else:
                    html_code = ""


            soup = BeautifulSoup(html_code, features="html.parser")
            for project in soup.find_all("a", href=True):
                try:
                    if project.contents[0] == "Name" or project.contents[0] == "Last modified" or project.contents[0] == "Size" or project.contents[0] == "Description" or project.contents[0] == "../":
                        dir = True
                        pass

                    if dir == True:
                        if project.contents[0] == "Name" or project.contents[0] == "Last modified" or project.contents[
                            0] == "Size" or project.contents[0] == "Description" or project.contents[0] == "../":
                                pass
                        else:
                            print(Fore.GREEN + str(project.contents[0]) + Fore.RESET)

                except:
                    pass

            print("-----------------------------")

def check_cassandra(results):
    if results:
        for service in results:
            print('IP: ' + service['target']['ip'] + ":" + str(service['target']['port']))

            try:
                print("Cluster name: " + Fore.MAGENTA + service['result']['data']['info'][0]['cluster_name'] + Fore.RESET)
                print("Datacenter: " + Fore.YELLOW + service['result']['data']['info'][0]['data_center'] + Fore.RESET)

                for keyspace in service['result']['data']['keyspaces']:
                    if keyspace == 'system' or keyspace =="system_traces" or keyspace == "system_schema" or keyspace=='system_auth' or keyspace=='system_distributed':
                        pass
                    else:
                        print("Keyspace: " + Fore.BLUE + keyspace + Fore.RESET)
                        print("Tables: ")
                        for table in service['result']['data']['keyspaces'][keyspace]['tables']:
                            print(Fore.GREEN + table + Fore.RESET)

                print("-----------------------------")

            except Exception as e:
                print("-----------------------------")
                pass

def check_rethinkdb(results):
    if results:
        for service in results:
            print('ReQL: ' + service['target']['ip'] + ":" + str(service['result']['data']['status'][0]['network']['reql_port']))
            print('HTTP Admin: ' + "http://"+service['target']['ip'] + ":" + str(service['result']['data']['status'][0]['network']['http_admin_port']))

            if 'hostname' in service['result']['data']['status'][0]['network']:
                print("Hostname: " + Fore.BLUE + service['result']['data']['status'][0]['network']['hostname'] + Fore.RESET)

            print("Version: " + Fore.YELLOW + service['result']['data']['status'][0]['process']['version'] + Fore.RESET)
            print("Name: " + Fore.MAGENTA +  service['result']['data']['status'][0]['name'] + Fore.RESET)

            for database in service['result']['data']['databases']:

                print("Database: " + Fore.LIGHTCYAN_EX +  database + Fore.RESET)
                print("Tables: ")
                for table in service['result']['data']['databases'][database]['tables']:
                    print(Fore.GREEN + table + Fore.RESET)

            print("-----------------------------")
        
def clean_query(query):
    arr_query = []
    second_part = ""

    if ":" in query:
        arr_query = query.split(":")
        second_part = '"' + arr_query[1] + '"'

        query = "%20AND%20" + arr_query[0] +":"+ second_part
        
    else:
        query = ""
        
    return query

            
            
def run(elastic=False,couchdb=False,mongodb=False,gitlab=False,rsync=False,
        jenkins=False, sonarqube=False, cassandra=False,
        rethink=False,listing=False,kibana=False,first=0,last=0):
    """
    optional:
        elastic=False
        couchdb=False
        mongodb=False
        gitlab=False
        rsync=False,
        jenkins=False, 
        sonarqube=False, 
        binaryedge_query=False, 
        cassandra=False,
        rethink=False,
        listing=False,
        kibana=False,
    
    mandatory:
        first=0
        last=0
    """

    if first and last is None:
        print(Fore.RED +  "Choose pages to search"+ Fore.RESET)
        sys.exit()
    elif last and first is None:
        print(Fore.RED +  "Choose pages to search"+ Fore.RESET)
        sys.exit()
    elif first is None and last is None:
        print(Fore.RED +  "Choose pages to search"+ Fore.RESET)
        sys.exit()
    elif first > last:
        print(Fore.RED +  "Correct pages "+ Fore.RESET)
        sys.exit()
    else:
        last = last + 1
        
        
    # --> can be put in json config later
    elastic_query = "type:%22elasticsearch%22"
    mongodb_query = "type:%22mongodb%22"
    couchdb_query = "product:%22couchdb%22"
    rsync_query = "rsync port:%22873%22"
    sonarqube_query = "%22Title: SonarQube%22"
    jenkins_query = "%22Dashboard [Jenkins]%22"
    gitlab_query = "%22Sign in GitLab%22"
    kibana_query = "product:%22kibana%22"
    listing_query = '%22Index of /%22'
    cassandra_query = "type:%22cassandra%22"
    rethink_query = "type:%22rethinkdb%22"
    
    if rsync:
        query = clean_query(rsync_query)
        for page in range(first,last):
            print(Fore.RED + '----------------------------------Rsync - Page ' + str(
                page) + '--------------------------------' + Fore.RESET)
            #rsync_results = binaryedge_query(rsync_query + " " + query,page)
            rsync_results = binaryedge_query(rsync_query,page)
            check_rsync(rsync_results)

    if gitlab:
        query = clean_query(gitlab_query)
        for page in range(first,last):
            print(Fore.RED + '----------------------------------GitLab - Page ' + str(
                page) + '--------------------------------' + Fore.RESET)
            #gitlab_results = binaryedge_query(gitlab_query+ " " + query,page)
            gitlab_results = binaryedge_query(gitlab_query,page)
            check_gitlab(gitlab_results)

    if sonarqube:
        query = clean_query(sonarqube_query)
        for page in range(first, last):
            print(Fore.RED + '----------------------------------SonarQube - Page ' + str(
                page) + '--------------------------------' + Fore.RESET)
            #sonarqube_results = binaryedge_query(sonarqube_query+ " " + query, page)
            sonarqube_results = binaryedge_query(sonarqube_query, page)
            check_sonarqube(sonarqube_results)

    if jenkins:
        query = clean_query(jenkins_query)
        for page in range(first, last):
            print(Fore.RED + '----------------------------------Jenkins - Page ' + str(
                page) + '--------------------------------' + Fore.RESET)
            #jenkins_results = binaryedge_query(jenkins_query+ " " + query, page)
            jenkins_results = binaryedge_query(jenkins_query, page)
            check_jenkins(jenkins_results)

    if elastic:
        query = clean_query(elastic_query)
        for page in range(first, last):
            print(Fore.RED + '----------------------------------Elastic - Page ' + str(
                page) + '--------------------------------' + Fore.RESET)
            #elastic_results = binaryedge_query(elastic_query+ " " + query, page)
            elastic_results = binaryedge_query(elastic_query, page)            
            check_elastic(elastic_results)

    if couchdb:
        query = clean_query(couchdb_query)
        for page in range(first, last):
            print(Fore.RED + '----------------------------------CouchDB - Page ' + str(
                page) + '--------------------------------' + Fore.RESET)
            #couchdb_results = binaryedge_query(couchdb_query+ " " + query, page)
            couchdb_results = binaryedge_query(couchdb_query, page)
            check_couchdb(couchdb_results)

    if mongodb:
        query = clean_query(mongodb_query)
        for page in range(first, last):
            print(Fore.RED + '----------------------------------MongoDB - Page ' + str(
                page) + '--------------------------------' + Fore.RESET)
            #mongodb_results = binaryedge_query(mongodb_query+ " " + query, page) 
            mongodb_results = binaryedge_query(mongodb_query, page)
            check_mongodb(mongodb_results)

    if kibana:
        query = clean_query(kibana_query)
        for page in range(first, last):
            print(Fore.RED + '----------------------------------Kibana - Page ' + str(
                page) + '--------------------------------' + Fore.RESET)
            #kibana_results = binaryedge_query(kibana_query+ " " + query, page)
            kibana_results = binaryedge_query(kibana_query, page)            
            check_kibana(kibana_results)

    if listing:
        query = clean_query(listing_query)
        for page in range(first,last):
            print(Fore.RED + '----------------------------------Listing directory - Page ' + str(
                page) + '--------------------------------' + Fore.RESET)
            #listing_results = binaryedge_query(listing_query + " " + query,page)
            listing_results = binaryedge_query(listing_query,page)            
            check_listing(listing_results)

    if cassandra:
        query = clean_query(cassandra_query)
        for page in range(first,last):
            print(Fore.RED + '----------------------------------Cassandra - Page ' + str(
                page) + '--------------------------------' + Fore.RESET)
            #cassandra_results = binaryedge_query(cassandra_query + " " + query,page)
            cassandra_results = binaryedge_query(cassandra_query,page)            
            check_cassandra(cassandra_results)

    if rethink:
        query = clean_query(rethink_query)
        for page in range(first,last):
            print(Fore.RED + '----------------------------------Rethink DB - Page ' + str(
                page) + '--------------------------------' + Fore.RESET)
            #rethink_results = binaryedge_query(rethink_query + " " + query,page)
            rethink_results = binaryedge_query(rethink_query,page)            
            check_rethinkdb(rethink_results)
