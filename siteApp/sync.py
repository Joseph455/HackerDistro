import asyncio
import aiohttp
from asgiref.sync import sync_to_async
from django.conf import settings
from django.db import models
from .models import BaseModel
import time

class DbSyncTask:
    base_url = settings.HACKER_NEWS_API_URL

    @staticmethod
    async def get_latest_items(retries=0) -> list:
        items = []
        if retries < 5:
            try:
                async with aiohttp.ClientSession() as session:
                    url = DbSyncTask.base_url + "/topstories.json"
                    res = await session.get(url=url)
                    if res.status >= 200 and res.status < 300:
                        items = await res.json()
                    return  items
            except aiohttp.ClientConnectorError:
                    time.sleep(2)
                    return await DbSyncTask.get_latest_items(retries+1)

    
    @staticmethod
    async def get_item_data(item_id:int, retries=0) -> dict:
        if retries < 5:
            try:
                async with aiohttp.ClientSession() as session:
                    url =  DbSyncTask.base_url + f"/item/{item_id}.json"
                    res = await session.get(url=url)
                    item = None
                    if res.status >= 200 and res.status < 300:
                        item = await res.json()
                    return item
            except aiohttp.ClientConnectorError:
                time.sleep(2)
                return await DbSyncTask.get_item_data(item_id, retries+1)

    @staticmethod
    @sync_to_async
    def get_item_from_db(source_id:int):
        try:
            obj = BaseModel.objects.get(source_id=source_id)
        except (BaseModel.DoesNotExist, BaseModel.MultipleObjectsReturned):
            obj = None
        return obj
    
    @staticmethod
    async def add_item_to_db(item:dict) -> models.Model:
        try:
            obj, _ = (await BaseModel.create(item.get("id")))   
            return obj
        except Exception as e :
            print(e)

    @staticmethod
    async def process_item(item:dict, get_kids=True):        
        obj = await DbSyncTask.add_item_to_db(item)   
        
        if get_kids and obj:

            try:
                await obj.load_kids()
            except Exception as e:
                print(e)

        return obj

    @staticmethod
    async def main():
        items =  await DbSyncTask.get_latest_items()
        items = items[:100] if len(items) > 100 else items

        async def task(item_id):
            try:
                item = await DbSyncTask.get_item_from_db(item_id)
                if not item:
                    item_data = await DbSyncTask.get_item_data(item_id)
                    await DbSyncTask.process_item(item_data, get_kids=True)
            except Exception as e:
                print(e)

        tasks = [task(item_id) for item_id in items]

        await asyncio.gather(*tasks)

    @staticmethod
    def run():
        asyncio.run(DbSyncTask.main())
