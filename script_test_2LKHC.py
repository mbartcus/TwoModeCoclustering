# -*- coding: utf-8 -*-
"""
Created on Mon Feb 19 09:33:01 2018

@author: HZTT9795
"""
import constants as const
import datasets as data
import utils as utl
import TwoLevelCoclustering as KHCopt
            
def mainOptimizeCoclustering(dataName, dataFileName, trace=True):
    """
    requires:
        a data name - name of data (used as a folder name where the data file is placed)
        dataFileName - name of the data file (without the extension)
        trace - in order to indicate if a trace file is created or not
    
    ensures:
        the optimize two level coclustering file, running all the steps:
        1) partition step
        2) fine coclustering step (with the need of mitigate to obtain micro clusters on the first variable and on the second variable)
        3) amalgamate step
        4) post optimize step
    """
    
    KHC_DicFileName = 'D:/Utilisateur/Marius/TwoModeCoclustering_clear_v3/CoclusteringDatasets/RealData.kdic'
    KHC_DicName = 'RealData'
    KHC_VariableName1 = "X"
    KHC_VariableName2 = "Y"
    KHC_FrequencyVariable = "Freq"
    const.setDictionarySettings(KHC_DicFileName, KHC_DicName, KHC_VariableName1, KHC_VariableName2, KHC_FrequencyVariable)
    
    
    
    KHC_RootTemporaryDir = "D:/Utilisateur/Marius/temp/"
    KHC_RootDataDir = "D:/Utilisateur/Marius/TwoModeCoclustering_clear_v3/CoclusteringDatasets/"
    KHC_RootDataDir = KHC_RootDataDir+dataName+'/'
    KHC_RootTemporaryDir= KHC_RootTemporaryDir+dataName+'/'
    const.setRootDirectories(KHC_RootTemporaryDir, KHC_RootDataDir)
    
    
    
    const.setKeepAllTemporaryFiles(True)
#    const.KHC_KeepWorkingDir = True
    
    
    
    
    inputDataFileName = const.KHC_DataDir + '{0}.txt'.format(dataFileName)
    outputCoclusteringRapport = '{0}.khc'.format(dataFileName)
    if trace:
        utl.fileGlobalTrace=open(const.KHC_DataDir + "GlobalTrace{0}.txt".format(dataName), "w")
    utl.globalTrace("Start optimisation\n")
    lcc = KHCopt.LargeScaleDataSet(inputDataFileName)
    lcc.trainCoclustering(outputCoclusteringRapport)
    utl.globalTrace("Stop optimisation\n")
    if trace:
        utl.fileGlobalTrace.close()
        utl.fileGlobalTrace = None  
        
    const.KHC_DataDir = None
    const.KHC_TemporaryDir = None
    
mainOptimizeCoclustering(data.dataNames[0], data.dataFileNames[0])
print('end 0')
#mainOptimizeCoclustering(data.dataNames[1], data.dataFileNames[1])
#print('end 1')
#mainOptimizeCoclustering(data.dataNames[2], data.dataFileNames[2])
#print('end 2')
#mainOptimizeCoclustering(data.dataNames[3], data.dataFileNames[3])
#print('end 3')
#mainOptimizeCoclustering(data.dataNames[4], data.dataFileNames[4])
#print('end 4')
#mainOptimizeCoclustering(data.dataNames[5], data.dataFileNames[5])
#print('end 5')
