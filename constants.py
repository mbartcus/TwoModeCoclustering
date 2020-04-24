# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 14:35:17 2018

@author: HZTT9795


"""

# 2L-KHC algorithm for co-clustering of very large data sets
# Choice of the number of corase clusters for the partitioning step

# Parameters of 2L-KHC
Imax = 500   # Max size of data matrix
Vmax = 2000  # Maximum number of super values
Nmin = 10000 # Minimum number of instances
Vmin = 200   # Minimum number of values per dimension
nuMin = 2   # Minimum number of instances per value


# Parametrage des dictionnaires de coclustering
# Par defaut, en "dur": X, Y variable categorielles et Freq variable d'effectif
KHC_DicFileName = None
KHC_DicName = None
KHC_VariableName1 = None
KHC_VariableName2 = None
KHC_FrequencyVariable = None

def setDictionarySettings(DicFileName, DicName, VariableName1, VariableName2, FrequencyVariable):
    global KHC_DicFileName
    global KHC_DicName
    global KHC_VariableName1
    global KHC_VariableName2 
    global KHC_FrequencyVariable 
    KHC_DicFileName = DicFileName
    KHC_DicName = DicName
    KHC_VariableName1 = VariableName1
    KHC_VariableName2 = VariableName2
    KHC_FrequencyVariable = FrequencyVariable

'''
Parametrage pour le lancement de Khiops_coclustering

KHC_TemporaryDir: None/Directory
KHC_KeepLogFiles: False/True
KHC_KeepScenarioFiles: False/True
KHC_KeepPartitionFiles: False/True
'''
KHC_TemporaryDir=None
KHC_DataDir=None

def setRootDirectories(KHC_RootTemporaryDir, KHC_RootDataDir):
    global KHC_TemporaryDir
    global KHC_DataDir
    KHC_TemporaryDir = KHC_RootTemporaryDir # set by default the temporary directory where all the intermediate files will be writen
    KHC_DataDir = KHC_RootDataDir # set the 



# set all the temporary files to be deleted by default
KHC_KeepLogFiles = False
KHC_KeepScenarioFiles = False
KHC_KeepPartitionFiles = False
KHC_KeepRecodedFiles = False
KHC_KeepWorkingDir = False

def setKeepAllTemporaryFiles(isKept):
    """
    requires 
        a boolean
    ensures:
        keeping or deleting all the temporary files
    """
    global KHC_KeepLogFiles
    global KHC_KeepScenarioFiles
    global KHC_KeepPartitionFiles
    global KHC_KeepRecodedFiles
    global KHC_KeepWorkingDir
    KHC_KeepLogFiles = isKept
    KHC_KeepScenarioFiles = isKept
    KHC_KeepPartitionFiles = isKept
    KHC_KeepRecodedFiles = isKept
    KHC_KeepWorkingDir = isKept

"""
Parametrage pour les noms des fichiers ou repertoires
"""
labelKHCp = 'part'
labelKHCf = 'fine'
labelKHCsplit='output'
labelPostOpt='post'
labelSimplify = 'simplify'
labelAmalgamate = 'amalgamate'