# LeakLookerLib - Powered by Binaryedge.io
Find open databases/services

New version supports:
- Elasticsearch
- CouchDB
- MongoDB
- Gitlab
- Rsync
- Jenkins
- Sonarqube
- Kibana
- CassandraDB
- RethinkDB
- Directory listing

Not yet supported:
- ustom query.

Queries:
- https://docs.binaryedge.io/api-v2/

Source:
 - https://github.com/woj-ciech/LeakLooker


## Requirements:
Python 3 &
Binaryedge API

***Paste your BinaryEdge API key in the config.json***

```
pip install -r requirements.txt
```
## Usage
```
import leaklooker

# -> select whatever db you want as True
# -> select how many pages you want
leaklooker.run(elastic=True,couchdb=False,mongodb=False,gitlab=False,rsync=False,
        jenkins=False, sonarqube=False, cassandra=False,
        rethink=False,listing=False,kibana=False,first=0,last=0)
```

## Future
- add config file option to method
- add shodan support
- add more db and query options
- add extra filter
- add binaryedge API usage limit warning


## Additional
Tool has been made for educational purposes only. I'm not responsible for any damage caused. Don't be evil.
