Alpha-client-server
=====================



### Flow of the AlphaClient
- `AlphaClient` is for collecting the ssh login attempts in a day. 
    - The collected ssh login attempts is placed in Document based DB in `SSHLogins` collection. Here mongodb is used.
- Flow
    - `auth.log` is used to store the SSH and other authentication related details by the OS. SSH login details success or failure is available in `auth.log`.
    - When the auth.log is modified an `event` is triggered. 
    -When the event is  triggered `client.py` runs linux commands using `subprocess` module to get the data from the auth.log instead of opening the log file.
        - Opening the file and closing the file frequently might cause errors and bugs (while OS tries to write ssh details at the same point of time). `subprocess` module makes the OS to run the commands and fault tolerant.
    - Linux commands are run using the subprocess module
        - `wc -l <path_of_auth_log_file>` It is to get the length of the file.
    - The length of the file is stored in `FilePointer` collection. Whenever new lines add we subtract the file pointer number with the length of the file. The resultant number is used to tail the log data from the auth.log
        - `tail -<diff> <path_of_auth_file>`
    - The idea is to track only sshd, we pipe the above result to `grep`
        - `grep sshd`
    - Here there is a catch the messages of sshd in auth.log can be multiple from same `sshd_id`.
        - We are using regex to fetch the id and using `set` datastructure to find the unique ones and adding that to the count of each day in `SSHLogins` collection.
        - Eg
            ```
                Mar 29 17:37:18 ip-10-77-20-248 sshd[4890]: pam_unix(sshd:session): session closed for user elastic_user_9
                Mar 29 17:20:59 ip-10-77-20-248 sshd[4758]: Accepted password for elastic_user_2 from 85.245.107.41 port 54870 ssh2
                Mar 29 17:33:17 ip-10-77-20-248 sshd[4888]: Failed password for elastic_user_6 from 85.245.107.41 port 54957 ssh2
                Mar 29 17:33:17 ip-10-77-20-248 sshd[4888]: Connection closed by 85.245.107.41 port 54957 [preauth]
                Mar 29 17:37:18 ip-10-77-20-248 sshd[4890]: Accepted password for elastic_user_9 from 24.151.103.17 port 50686 ssh2
            ```
            - We have `sshd[4890]`, `sshd[4888]`, `sshd[4890]`, `sshd[4758]` sshd logs and these are unique. So we increment the value of the SSHLogins with 4 in particular date.

    - A WSGI python file which runs the server is used to fetch the details of the ssh_logins from the MongoDB and returns as json.
    - We can wrap the mongodb and wsgi application in docker make them secured without any interruptions from other applications.
    - The `client.py` should be run independent of the rest as it has to access `auth.log` file (as OSs uses auth.log to log the sshd attempts). If it is dockerized it can't run linux commands or access the auth.log of the alphaclient. But it can update the ssh count in document based db which can be running in docker.
- Requirements 
    - DATBASE_URL
    - DATABASE_NAME
- Commands
    - `python3 client.py` and provide the path of the log file and it works.
    - `docker-compose up` to run the wsgi and mongodb (optional) or provide the requirements and run `python3 client_wsgi.py`


---

### Flow of AlphaServer
- `AlphaServer` is a visualization tool which visualizes the ssh login attempts of all servers provided in the inventory.
- We can also any framework including frontend frameworks. The reason is if there are 100 servers and fetching the ssh login attempts for all the servers at the same time requires asynchronous approach. So FastAPI.
- Technology 
    - Python FastAPI 
    - It can be used for REST APIs with asynchronous nature. 
- Flow
    - Alpha server provides 2 APIs.
        - Fetches the ssh login attempts of the particular host and particular date. (Need to pass host and date as path parameter (that makes the variables madatory)).
        - Fetches the ssh login attempts of the all the server by making asynchronous calls (aiohttp) for the URLs provided and for particular date.
- Requirements to be provided
    - URL of the alphaclient's running wsgi application for REST API call.
    - Docker (optional)
        - If provided it would be better to avail the benefits of the docker.
- Commands
    - `cd alphaserver`
    - `docker-compose up -d` or 
    - `python3 run.py`
    - Swagger docs
        - > http://127.0.0.1:8000/docs


#### Note
- The application can be modified based on the resources and requirements for scaling etc.
- The state of the nodes remains unchanged i.e. the deployment is idempotent. 
    - alphaclient -> We can run the client.py any number of time and also client_wsgi.py any number of times required.
    - alphaserver -> We are dockerizing makes the application independent and isolated. When it is deployed it will not affect the server it is running.
- In resources folder, sample screenshots are available
    - FastApi Swagger
    - REST API response of the FAST API (we are using for visualization)

#### Snapshots
- Architecture 
    - ![Arch](/resources/Architecture.png?raw=true)
- DB Pointer collection
    - ![Pointer](/resources/pointer.png?raw=true)
- DB SSH Attempts collection
    - ![SSH](/resources/ssh_attempts.png?raw=true)