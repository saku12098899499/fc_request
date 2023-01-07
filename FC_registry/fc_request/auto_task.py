from datetime import datetime, date
from apscheduler.schedulers.background import BackgroundScheduler # 指定したタイミングで指定したタスク処理を自動的に行う.

def test():
    # 実行したい処理
    print("定期実行")


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(test,'interval',minutes=1)  # 1分おきに実行
    scheduler.start()
    