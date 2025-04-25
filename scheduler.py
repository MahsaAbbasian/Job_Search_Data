import schedule
import time
import os
from datetime import datetime
import sys
import subprocess

def log_message(message):
    now_str = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    with open("scheduler_log.txt", "a") as log_file:
        log_file.write(f"{now_str}-{message} \n")

def run_vakanser():
    log_message("Running vakanser.py...")
    log_message("Running vakanser.py...")
    result = os.system("C:\\Users\\Mahsa\\AppData\\Local\\Programs\\Python\\Python313\\python.exe C:\\Users\\Mahsa\\Desktop\\NewFolder\\projects\\python\\Job_Search_Data\\vakanser.py")

    log_message(f"vakanser.py finished with status {result}")

def run_arbetsformedlingen():
    log_message("Running arbetsformedlingen.py...")
    result = os.system("C:\\Users\\Mahsa\\AppData\\Local\\Programs\\Python\\Python313\\python.exe C:\\Users\\Mahsa\\Desktop\\NewFolder\\projects\\python\\Job_Search_Data\\arbetsformedlingen.py")
    log_message(f"arbetsformedlingen.py finished with status {result}")

def deploy():
    log_message("Running Firebase deploy...")
    
    firebase_path = "C:\\Users\\Mahsa\\AppData\\Roaming\\npm\\firebase.cmd"
    project_path = "C:\\Users\\Mahsa\\Desktop\\NewFolder\\projects\\python\\Job_Search_Data"

    result = subprocess.run(
        [firebase_path, "deploy", "--debug"],
        cwd=project_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=True
    )

    log_message(f"Firebase deploy finished with status {result.returncode}")
    log_message(f"DEBUG STDOUT: {result.stdout}")
    log_message(f"DEBUG STDERR: {result.stderr}")

schedule.every().day.at("13:05").do(run_vakanser)
schedule.every().day.at("13:10").do(run_arbetsformedlingen)
schedule.every().day.at("13:15").do(deploy)

log_message("Scheduler started...")
log_message(f"Python Executable: {sys.executable}")
log_message(f"Current Working Directory: {os.getcwd()}")

while True:
    schedule.run_pending()
    time.sleep(60)
