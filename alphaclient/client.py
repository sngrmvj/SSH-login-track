
import sys, os, re
import subprocess
from datetime import datetime
from pymongo import MongoClient
import constants
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler




# >>>> Attributes
os.environ['DATABASE_URL'] = constants.DATABASE_URL
os.environ['DATABASE_NAME'] = constants.DATABASE_NAME





# >>>> Handler class
class MyHandler(FileSystemEventHandler):

    FILENAME ="auth.log"
    cache = {}

    def on_modified(self, event):
        now = datetime.now().time()
        if now.second in MyHandler.cache:
            return 
        else:
            MyHandler.cache[now.second] = now.microsecond
        # The main idea is to avoid event triggering twice in milliseconds and we take 1 second difference
        if event.src_path.endswith(MyHandler.FILENAME):
            if event.is_directory == False:
                print(self.read_auth_file(folder=folder))

    # ----------------------------------------------------------------------------------------------

    def get_pointer(self):
        try:
            # Creating a client
            client = MongoClient(os.environ.get('DATABASE_URL'))
            dblist = client.list_database_names()
            mydb = client[os.environ.get('DATABASE_NAME')]
            myPointer = mydb[constants.FILE_POINTER_COLLECTION]
            return myPointer

        except Exception as error:
            print(f"Error in fetching the pointer - {error}")

    # ----------------------------------------------------------------------------------------------

    def update_pointer(self,new_pointer):
        try:
            # Creating a client
            file_pointer = self.get_pointer()
            all_records = [item for item in file_pointer.find()]
            file_pointer.update_one({'_id': all_records[0]['_id']},new_pointer)
        except Exception as error:
            print(f"Error in updating the pointer - {error}")   

    
    # ----------------------------------------------------------------------------------------------

    
    def update_count(self, count):
        date  = str(datetime.now().date())
        try:
            # Creating a client
            client = MongoClient(os.environ.get('DATABASE_URL'))
            dblist = client.list_database_names()
            if os.environ.get('DATABASE_NAME') in dblist:
                mydb = client[os.environ.get('DATABASE_NAME')]
                ssh_logins = mydb[constants.SSH_LOGIN_COLLECTION]
                all_ssh_records = [item for item in ssh_logins.find()]
                if date in all_ssh_records[0]:
                    all_ssh_records = all_ssh_records[0]
                    all_ssh_records[date] += count
                else:
                    all_ssh_records = all_ssh_records[0]
                    all_ssh_records[date] = count
                ssh_logins.update_one({'_id':all_ssh_records['_id']},{"$set": all_ssh_records})
        except Exception as error:
            print(f"Error in updating / adding the count per day to the collection - {error}")


    # ----------------------------------------------------------------------------------------------

    def read_auth_file(self,folder):

        try:
            file = folder + "/" +MyHandler.FILENAME

            if not file:
                return False

            file_pointer = self.get_pointer()
            file_pointer = [item for item in file_pointer.find()]
            if not file_pointer:
                file_pointer= {'pointer':0} 

            # Getting the number of lines in the file using linux commands
            len_of_file_process = subprocess.Popen(["wc", "-l", file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # Getting the difference of lines to be fetched between length of the file and pointer
            # Pointer is where the last read of the file happens generally the end of the file.
            len_of_file = len_of_file_process.stdout.readline().decode('utf-8').strip().split(" ")[0]
            if len_of_file == 0:
                return False
            diff = (int(len_of_file)-int(file_pointer[0]['pointer'])) 

            tail_auth_file_process = subprocess.Popen(['tail', "-"+ str(diff), file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            pipe_process = subprocess.run(['grep', "sshd"],stdin=tail_auth_file_process.stdout, capture_output=True, text=True)
            pipe_process = pipe_process.stdout.split("\n")
            sets = set()
            for line in pipe_process:
                if(re.findall("sshd\[(.*?)\]",line)):
                    sets.add(re.findall("sshd\[(.*?)\]",line)[0])
            ssh_login_attempt_count = len(sets)
            
            # We need the pointer for to track the number of read of lines
            new_pointer = {"$set":{'pointer':int(len_of_file)}}
            self.update_pointer(new_pointer=new_pointer)
            print("Pointer updated")

            self.update_count(count=ssh_login_attempt_count)

            # return the count of the unique sshd login ids 
            # The number of the sshd messages are more for one sshd id.
            return True
        except Exception as error:
            print(f"Error while fetching the sshd login attempts = {error}")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return False



# ----------------------------------------------------------------------------------------------


def initialise_db():

    try:
        # Creating a client
        date  = str(datetime.now().date())
        client = MongoClient(os.environ.get('DATABASE_URL'))
        mydb = client[os.environ.get('DATABASE_NAME')]
        # Automatic setup of the collection initially
        pointer = { 'pointer': 0 }
        pointer_collection = mydb[constants.FILE_POINTER_COLLECTION]
        isCollection = pointer_collection.find()
        isCollection = [x for x in isCollection]
        if not isCollection:
            pointerdoc = pointer_collection.insert_one(pointer)
            if not pointerdoc.inserted_id:
                return False
        
        count = { date: 0 }
        ssh_collection = mydb[constants.SSH_LOGIN_COLLECTION]
        isSSHCollection = ssh_collection.find()
        isSSHCollection = [x for x in isSSHCollection]
        if not isSSHCollection:
            sshdoc = ssh_collection.insert_one(count)
            if not sshdoc.inserted_id:
                return False

        return True
    except Exception as error:
        print(f"Error while initilising the db - {error}")
    




# ----------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------



if __name__ == "__main__":

    isDBInitialised = initialise_db()
    if isDBInitialised:
        folder = os.path.abspath(constants.FOLDER_PATH)    
        # below only added the file as path
        event_handler = MyHandler()
        observer = Observer()
        observer.schedule(event_handler, path=folder, recursive=False)
        observer.start()

        try:
            pass
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
    else:
        print("Not able to initialise the DB")