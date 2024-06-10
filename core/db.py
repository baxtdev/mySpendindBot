from datetime import datetime
import json
import aiofiles
from uuid import uuid4

from core.config import DATABASE_URL

async def create_task(data:dict):

    with open (DATABASE_URL,'r+') as file:
        data_ = json.load(file)
        data_[str(uuid4())]=data
        file.seek(0)
        json.dump(data_,file,indent=4)


async def get_tasks(user_id:int):
    print(DATABASE_URL)

    with open (DATABASE_URL,'r+') as file:
        data_:dict = json.load(file)
        result = []
        for key,value in data_.items():
            if value["user_id"]==user_id:
                value['id']=key
                result.append(value)

    return result


async def get_summ(user_id:int):
    with open (DATABASE_URL,'r+') as file:
        data_:dict = json.load(file)
        result = 0
        for key,value in data_.items():
            if value["user_id"]==user_id:
                result+=int(value["amount"])

    return result


async def day_summary(user_id):
    async with aiofiles.open(DATABASE_URL, 'r') as file:
        data_ = json.loads(await file.read())
        result = 0
        today = datetime.today().date()
        
        for key, value in data_.items():
            if value["user_id"] == user_id and datetime.fromisoformat(value["date"]).date() == today:
                result += int(value["amount"])

    return result


async def delete_task(task_id:int):
    with open ('/Users/macpro2019/projects/to_do-bot/data.json','r') as file:
        data_:dict = json.load(file)
        data=data_.pop(task_id)
        with open ('/Users/macpro2019/projects/to_do-bot/data.json','w') as file:
            json.dump(data_,file,indent=4)       
    
