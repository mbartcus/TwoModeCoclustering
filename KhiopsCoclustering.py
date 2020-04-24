# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 16:04:30 2018

@author: HZTT9795
"""
import subprocess
import os
import sys
    
KhiopsHome="E:/Programme/khiops8.5"
#KhiopsHome="E:/Utilisateurs/Marc/khiops9"
#KhiopsHome="C:/Program Files/khiops"

KhiopsBatchMode=True

def startKhiopsCoclustering(scenarioFilePathName, logFilePathName):
    # Start khiops-coclustering with a scenario file and a log file
    # Erreur if os.path.join(KhiopsHome, "bin", "khiops_coclustering.cmd") exists
    KhiopsPath = os.path.join(KhiopsHome, "bin", "khiops_coclustering.cmd")
    if not os.path.exists(KhiopsPath):
        print("Error: Khiops coclustering not found (" + KhiopsPath + ")")
        sys.exit(0)
    params = []
    params.append(KhiopsPath)
    if KhiopsBatchMode:
        params.append("-b")
    params.append("-i")
    params.append(scenarioFilePathName)
    params.append("-e")
    params.append(logFilePathName)
    #params.append("-r")
    #params.append("DIRNAME:" + RezultDirCoClustering)
    subprocess.call(params)