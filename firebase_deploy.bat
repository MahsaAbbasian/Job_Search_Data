@echo off
echo %DATE% %TIME% - Firebase Deploy Started >> firebase_log.txt
cd C:\Users\Mahsa\Desktop\NewFolder\projects\python\Job_Search_Data
C:\Users\Mahsa\AppData\Roaming\npm\firebase.cmd deploy >> firebase_log.txt 2>&1
echo %DATE% %TIME% - Firebase Deploy Finished >> firebase_log.txt
exit
