Alpha-client-server
=====================



### Flow of the AlphaClient
- `client.py`, Here instead of crontab which runs every few minutes and checking the file, we are using event based updation.
- An event gets triggered when there is a modification for the `auth.log` file.
- When the event triggers
    - We get the length of the file using linux command `wc -l <name_of_auth_file>`
    - Then we fetch the pointer. The pointer is the last read line of `auth.log` which is stored in collection of MongoDB.
    - The difference between the current length of the auth.log and the pointer is the number of lines to be read.
    - Here we use linux command `tail` as we don't care about the top of the file.
        - Linux Command `tail -<diff> <name_of_auth_file>`. We pipe the result to `grep`
    - `grep` is used to check for the `sshd` messages in the file alone.
        - Linux command `grep sshd`
    - Here there is a catch the messages of sshd in auth.log can be multiple from same `sshd_id`.
        - We are using regex to fetch the id and using det datastructure to find the unique ones.
    - **Each unique ones is counted as sshd login attempt** and updated in the DB of that particular day.
- A WSGI python file which runs the server is used to fetch the details of the ssh_logins from the MongoDB and returns as json.
- We wrap the mongodb and wsgi application if possible in docker make them secured without any interruptions.
- The `client.py` should be run independent of the rest as it has to access `auth.log` file (as OSs uses auth.log to log the sshd attempts)
- Please provide
    - DATBASE_URL
    - DATABASE_NAME
- Commands
    - `python3 client.py` and provide the path of the log file and it works.
    - `docker-compose up` to run the wsgi and pymongo


---

### Flow of AlphaServer
- This is a wsgi application, developed in python flask
- The main requirement is to pass server details to hit the WSGI application running in the AlphaClient
- Here a http request with the URL of the required host is used to fetch the ssh details of that particular host and visualized.