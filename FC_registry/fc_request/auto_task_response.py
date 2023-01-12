from datetime import datetime, date
from apscheduler.schedulers.background import BackgroundScheduler # 指定したタイミングで指定したタスク処理を自動的に行う.
from django.db import models
from .models import Request,Wallet,Response 
from django.db.models import Q
from concurrent import futures
import json
from PIL import Image
import hashlib
from FC_registry.settings import MEDIA_ROOT
import fc_request.BSV as fk
def write_cont(id,content):
    # 実行したい処理
    # print(obj[1])
    # print(obj[2])
    # img=""
    # if obj[3]:
    #     img = Image.open(obj[3])
    #     print(img)
    # filename = 'image.png'
    json_obj = {
        "content":content,
    }
    print("aaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    print(json_obj)
    print("aaaaaaaaaaaaaaaaaaaaaaaaaaaa")

    print("定期実行11")
    tx=fk.post(str(json_obj),"mfp4bUdexky4PyMd8fLeDVYNLoGMRJhLpG")
    print("定期実行21")
    obj=Response.objects.get(id=id)
    print("//////////////////////////////////////")
    print(obj)
    print("//////////////////////////////////////")
    obj.txid_response=tx
    obj.save()
    return tx
    #print(json_obj)
    #textdata = obj[] + str(" ") + str("画像のハッシュ値:") + str(sha256)
    #         print("ブロックチェーンへの書き込み：" + textdata)
    #         walletdata = str(wallet)
    #         print("ウォレットアドレス：" + walletdata)

def search_null_txid():
    pass
    objs=Response.objects.filter(Q(txid_response__isnull=True))
    
    with futures.ThreadPoolExecutor(max_workers=2) as executor:
        #print(objs)
        future_list = []
        for obj in list(objs[0:1]):
            # image_hash=""
            # if obj.image:
            #     print(MEDIA_ROOT+str(obj.image))
            #     with open(MEDIA_ROOT+str(obj.image), 'rb') as f:
            #         binary = f.read()
            #     image_hash = hashlib.sha256(binary).hexdigest() # 画像のハッシュ化(
            future = executor.submit(write_cont,id=obj.id,content=obj.response_cont)
            future_list.append(future)
            _ = futures.as_completed(fs=future_list)

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(search_null_txid,'interval',seconds=40)  # 1分おきに実行
    scheduler.start()
    