from fastapi import FastAPI
import aiohttp
import constants


app = FastAPI()

@app.get("/sshcount/{host}/{date}")
async def get_ssh_count(host,date):
    # Please pass the date as string in YYYY-MM-DD

    async with aiohttp.ClientSession() as session:
        async with session.get(constants.URL[host]+"?date="+date) as response:
            ssh_attempt_count = await response.text()
    return {"ssh_login_attempt": int(ssh_attempt_count), "date":date, "host": host}



@app.get("/sshcount/all/{date}")
async def get_ssh_count(date):
    # Please pass the date as string in YYYY-MM-DD

    all_hosts_ssh_attempts = {}
    for host in constants.URL:
        async with aiohttp.ClientSession() as session:
            async with session.get(constants.URL[host]+"?date="+date) as response:
                ssh_attempt_count = await response.text()
                all_hosts_ssh_attempts[host] = ssh_attempt_count

    return {"date":date,"all_ssh_login_attempts": all_hosts_ssh_attempts}

