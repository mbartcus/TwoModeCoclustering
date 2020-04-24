# -*- coding: utf-8 -*-
"""
Created on Fri Oct 27 12:31:42 2017

@author: HZTT9795
"""

import datetime
import tempfile
import os
import utils as utl
import KhiopsCoclustering as khc
import CoclusteringModel as model
import constants as const


def KHCs(inputKHCFilePath, dimensionName, c_max, label, outputKHCFilePath):
    """
    aim: create a simplification scenario and starts khiops_coclustering
    write khiops template file
    
    input:
        1)inputKHCFilePath
        2)dimensionName - 0/1 depending on what variable to reduce the number of clusters variable 1 or 0
        3)c_max - number of cluster to simplify
        4)label
    outputs:
        outputKHCFilePath
    """
    if const.KHC_TemporaryDir is None:
        temporaryDir = tempfile.gettempdir()
    else:
        temporaryDir = const.KHC_TemporaryDir

    # Test d'existence
    scenarioFilePathName = os.path.join(temporaryDir, label+"._khc")
    logFilePathName = os.path.join(temporaryDir, label+".log")
    
    # Create scenario
    khFile = open(scenarioFilePathName,'w')
    khFile.write('//'+str(datetime.datetime.now())+'\n')
    
    khFile.write('// -> Khiops Coclustering\n')
    khFile.write('LearningTools.PostProcessCoclustering    // Simplify coclustering...\n')
    khFile.write('// -> Coclustering simplification\n')
    khFile.write('SelectInputCoclustering        // Select input coclustering...\n')  
    khFile.write('// -> Open\n')
    khFile.write('InputCoclusteringFileName {0}       // Input coclustering file\n'.format(inputKHCFilePath))
    khFile.write('OK                             // Open\n')
    khFile.write('// <- Open \n')
    
    if dimensionName==0:
        khFile.write('PostProcessingSpec.PostProcessedAttributes.List.Key {0}        // List item selection\n'.format(const.KHC_VariableName1))
    if dimensionName==1:
        khFile.write('PostProcessingSpec.PostProcessedAttributes.List.Key {0}        // List item selection\n'.format(const.KHC_VariableName2))
    
    khFile.write('PostProcessingSpec.PostProcessedAttributes.MaxPartNumber {0}  // Max part number\n'.format(c_max))
    khFile.write('AnalysisResults.PostProcessedCoclusteringFileName {0}  // Simplified coclustering report\n'.format(outputKHCFilePath))
        
    khFile.write('PostProcessCoclustering        // Simplify coclustering\n')
    
    khFile.write('Exit \t// Close\n')
    khFile.write('Exit \t// Close\n')
    khFile.write('// <- Khiops Coclustering\n')
    
    khFile.write('// -> Khiops Coclustering\n')
    khFile.write('OK\n')
    khFile.write('// <- Khiops Coclustering\n')
    khFile.close()
    
    # Lancement de Khiops-coclustering
    khc.startKhiopsCoclustering(scenarioFilePathName, logFilePathName)
    
    # Nettoyage si necessaire
    if not const.KHC_KeepLogFiles:
        utl.delete_file(logFilePathName)
    if not const.KHC_KeepScenarioFiles:
        utl.delete_file(scenarioFilePathName)
    
    pathFiles = os.path.dirname(os.path.abspath(inputKHCFilePath))+'/'
    m = model.CoclusteringModel(pathFiles + outputKHCFilePath)
            
    variable1Clusters, variable2Clusters=[],[]
    for k in m.XClustVals.keys():
        variable1Clusters.append(m.XClustVals[k])
    for k in m.YClustVals.keys():
        variable2Clusters.append(m.YClustVals[k])
        
    return variable1Clusters, variable2Clusters, outputKHCFilePath
    
def KHCp(inputDataFileName, variable1ValuesFrequency, variable2ValuesFrequency, c_max_1, c_max_2, label, outputKHCFilePath=None):
    #(fft)
    variable1Clusters=None
    variable2Clusters=None
    isPreoptimize='false'
    isOptimize='false'
    isPostOptimize='true'
    
    variable1Clusters, variable2Clusters, _=KHCUtil(inputDataFileName, variable1ValuesFrequency, variable2ValuesFrequency, c_max_1, c_max_2, label, variable1Clusters, variable2Clusters, isPreoptimize, isOptimize, isPostOptimize, outputKHCFilePath)
    
    return variable1Clusters, variable2Clusters
    

def KHCc(inputDataFileName, variable1ValuesFrequency, variable2ValuesFrequency, c_max, label, outputKHCFilePath=None):
    #(ttt)
    variable1Clusters=None
    variable2Clusters=None
    isPreoptimize='true'
    isOptimize='true'
    isPostOptimize='true'
    variable1Clusters, variable2Clusters, outputKHCFilePath=KHCUtil(inputDataFileName, variable1ValuesFrequency, variable2ValuesFrequency, c_max, c_max, label, variable1Clusters, variable2Clusters, isPreoptimize, isOptimize, isPostOptimize,outputKHCFilePath) 
    return variable1Clusters, variable2Clusters, outputKHCFilePath



def KHCe(inputDataFileName, variable1ValuesFrequency, variable2ValuesFrequency, c_max, label, variable1Clusters, variable2Clusters, outputKHCFilePath=None):
    """
    variable1Clusters, variable2Clusters,
    """
    #(fff) 
    #(Evaluate coclustering cost)
    isPreoptimize='false'
    isOptimize='false'
    isPostOptimize='false'
    variable1Clusters, variable2Clusters, outputKHCFilePath=KHCUtil(inputDataFileName, variable1ValuesFrequency, variable2ValuesFrequency, c_max,c_max, label, variable1Clusters, variable2Clusters, isPreoptimize, isOptimize, isPostOptimize,outputKHCFilePath, const.KHC_DataDir)
    
    #pathFiles = os.path.dirname(os.path.abspath(inputDataFileName))+ '/' + label + '/'
    level=utl.getLevelFromKhcRapport(outputKHCFilePath)
    return level


def KHCUtil(inputDataFileName, variable1ValuesFrequency, variable2ValuesFrequency, c_max_1, c_max_2, label, variable1Clusters=None, variable2Clusters=None, isPreoptimize='false', isOptimize='false', isPostOptimize='false', outputKHCFileName=None, fileSaveDirectory=None):
    """ 
    Input:
    #   inputDataFileName: contains triplets (X, Y, Freq), where X and Y are super-values or values
    #   variable1ValuesFrequency: dictionnaire des valeurs de la premiere variable, avec effectif par valeur
    #   variable2ValuesFrequency: dictionnaire des valeurs de la deuxieme variable, avec effectif par valeur
    #   c_max_1: maximum number of clusters on variable 1
    #   c_max_2: maximum number of clusters on variable 2
    #   variable1Clusters=None, variable2Clusters=None - variable clusters if known use them instead of making random partition
    #   label: label that identify the context
    #   outputKHCFilePath: output coclustering model file name
    # Output:
    #   variable1Clusters: tableau des clusters de valeurs de la premiere variable, chaque cluster etant un tableau de valeurs
    #   variable2Clusters: tableau des clusters de valeurs de la deuxieme variable, chaque cluster etant un tableau de valeurs
    # Par exemple:
    #  variable1Clusters = [["v1", "v5"], ["v2", "v3", "v4"]]
    #
    """
    if fileSaveDirectory==None:
        fileSaveDirectory=const.KHC_TemporaryDir
    
    utl.detect_path(fileSaveDirectory)
    
    if len(variable1ValuesFrequency)==0 and len(variable1ValuesFrequency)==0 and variable1Clusters is None and variable2Clusters is None:
        variable1Clusters=[[]]
        variable2Clusters=[[]]
        khcFile=''
    if len(variable1ValuesFrequency)!=0 and len(variable1ValuesFrequency)!=0:
        if outputKHCFileName==None:
            outputKHCFileName = label + str(c_max_1) + str(c_max_2) + '.khc'
        # 1. from variable1Values, variable2Values obtain partitions using c_max
        # create model inputPartitionFileName
        if (variable1Clusters is None and variable2Clusters is None):
            variable1Clusters = utl.getPartitions(variable1ValuesFrequency, c_max_1)
            variable2Clusters = utl.getPartitions(variable2ValuesFrequency, c_max_2)
        
        variable1ValueClust = utl.computeValueClusters(variable1Clusters)
        variable2ValueClust = utl.computeValueClusters(variable2Clusters)
        
        #2. create .khc model based on partitions obtained in previous step
        pathFiles = fileSaveDirectory+'/'+label+'/'
        utl.detect_path(pathFiles)
        inputPartitionFileName = pathFiles + label + '.khc'
        utl.writeKHCPartitionFile(variable1ValueClust,variable2ValueClust,variable1ValuesFrequency, variable2ValuesFrequency, inputPartitionFileName)
        
        #3. run KHCUtil that creates scenario and runs khiops -> returns variable1Values, variable2Values
        if const.KHC_TemporaryDir is None:
            temporaryDir = tempfile.gettempdir()
        else:
            temporaryDir = const.KHC_TemporaryDir   
            
        # Test d'existence
        scenarioFilePathName = os.path.join(temporaryDir, label+"._khc")
        logFilePathName = os.path.join(temporaryDir, label+".log")
        
        khFile = open(scenarioFilePathName,'w')
        khFile.write('//'+str(datetime.datetime.now())+'\n')
        
        khFile.write('// -> Khiops Coclustering\n')
        khFile.write('ClassManagement.OpenFile \t// Open...\n')
        
        khFile.write('// -> Open\n')
        khFile.write(('ClassFileName {0} // Dictionary file\n').format(const.KHC_DicFileName))
        khFile.write('OK\t // Open\n')
        khFile.write('// <- Open\n')
        
        khFile.write(('Database.DatabaseFiles.List.Key {0} \t // List item selection\n').format(const.KHC_DicName))
        khFile.write(('Database.DatabaseFiles.DataTableName {0} \t // Data table file\n').format(inputDataFileName))
        
        khFile.write('AnalysisSpec.CoclusteringParameters.Attributes.InsertItemAfter \t // Insert variable \n')
        khFile.write('AnalysisSpec.CoclusteringParameters.Attributes.List.Index {0}  // List item selection\n'.format(0))
        khFile.write(('AnalysisSpec.CoclusteringParameters.Attributes.Name {0} \t // Name \n').format(const.KHC_VariableName1))
        
        khFile.write('AnalysisSpec.CoclusteringParameters.Attributes.InsertItemAfter \t // Insert variable \n')
        khFile.write('AnalysisSpec.CoclusteringParameters.Attributes.List.Index {0}  // List item selection\n'.format(1))
        khFile.write(('AnalysisSpec.CoclusteringParameters.Attributes.Name {0} \t // Name \n').format(const.KHC_VariableName2))
            
        khFile.write(('AnalysisSpec.CoclusteringParameters.FrequencyAttribute {0} \t  // Frequency variable\n').format(const.KHC_FrequencyVariable))
        
        khFile.write('LearningTools.PostOptimizeCoclustering    // Post-optimize coclustering...\n\n')        
        khFile.write('// -> Coclustering post-optimization\n')
        khFile.write('SelectInputCoclustering        // Select input coclustering...\n\n')
        
        khFile.write('// -> Open\n')
        khFile.write(('InputCoclusteringFileName {0} \t // Input coclustering file\n').format(inputPartitionFileName))
        khFile.write('OK\n')
        khFile.write('// <- Open\n\n')
        
        khFile.write(('PostOptimizationSpec.PreOptimize {0}   // Pre-optimize (fast value move)\n').format(isPreoptimize))
        khFile.write(('PostOptimizationSpec.Optimize {0}      // Optimize (merge clusters)\n').format(isOptimize))
        khFile.write(('PostOptimizationSpec.PostOptimize {0}  // Post-optimize (deep value move)\n').format(isPostOptimize))
        khFile.write(('AnalysisResults.PostProcessedCoclusteringFileName {0}   // Post-optimized coclustering report\n').format(outputKHCFileName))
        
        #AnalysisResults.ResultFilesDirectory C:\Users\HZTT9795\Desktop\test    // Result files directory
        khFile.write(('AnalysisResults.ResultFilesDirectory {0} \t // Result files directory\n\n').format(pathFiles))  
        
        khFile.write('PostOptimize        // Post-optimize coclustering\n\n')
        khFile.write('Exit                           // Close\n')
        khFile.write('// <- Coclustering post-optimization\n')
        khFile.write('Exit // Close\n')
        khFile.write('// <- Khiops Coclustering\n\n')
        khFile.write('// -> Khiops Coclustering\n')
        khFile.write('OK                             // Close\n')
        khFile.write('// <- Khiops Coclustering\n')
        
        khFile.close()
        
        khc.startKhiopsCoclustering(scenarioFilePathName, logFilePathName)
        
        isError=utl.getIsError(logFilePathName)
        if isError:
            print('Error in log file: '+logFilePathName)
                
        khcFile = pathFiles+outputKHCFileName
        isInformative=utl.getIsIformative(khcFile, logFilePathName)
        
        #utl.globalTrace("{0}\t KHC Util \t logFile \t {1} \t isInformative: \t {2}\n".format(datetime.datetime.now(), logFilePathName, isInformative))   
        if isInformative:
            #initialize clusters a partire de fichiere outputKHCFilePath
            m = model.CoclusteringModel(khcFile)
            
            variable1Clusters, variable2Clusters=[],[]
            for k in m.XClustVals.keys():
                variable1Clusters.append(m.XClustVals[k])
            for k in m.YClustVals.keys():
                variable2Clusters.append(m.YClustVals[k])
        else:
            #initialize cluster with all values
            variable1Clusters=[list(variable1ValuesFrequency.keys())]
            variable2Clusters=[list(variable2ValuesFrequency.keys())]
        
        
        # Nettoyage si necessaire
        if not const.KHC_KeepLogFiles:
            utl.delete_file(logFilePathName)
        if not const.KHC_KeepScenarioFiles:
            utl.delete_file(scenarioFilePathName)
        if not const.KHC_KeepPartitionFiles:
            utl.delete_file(inputPartitionFileName)
        
        
    return variable1Clusters, variable2Clusters, khcFile
    