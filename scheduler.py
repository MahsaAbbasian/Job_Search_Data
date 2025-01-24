import schedule
import time
import os

def log_message(message):
    with open("scheduler_log.txt", "a") as log_file:
        log_file.write(message + "\n")

def run_vakanser():
    log_message("Running vakanser.py...")
    result = os.system("python C:\\Users\\Mahsa\\Desktop\\NewFolder\\projects\\python\\Job_Search_Data\\vakanser.py")
    log_message(f"vakanser.py finished with status {result}")

def run_arbetsformedlingen():
    log_message("Running arbetsformedlingen.py...")
    result = os.system("python C:\\Users\\Mahsa\\Desktop\\NewFolder\\projects\\python\\Job_Search_Data\\arbetsformedlingen.py")
    log_message(f"arbetsformedlingen.py finished with status {result}")

def deploy():
    log_message("Running Firebase deploy...")
    result = os.system("firebase deploy")
    log_message(f"Firebase deploy finished with status {result}")

schedule.every().day.at("17:20").do(run_vakanser)
schedule.every().day.at("17:23").do(run_arbetsformedlingen)
schedule.every().day.at("17:25").do(deploy)

log_message("Scheduler started...")
while True:
    schedule.run_pending()
    time.sleep(1)
