# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 16:49:48 2017

@author: HZTT9795
"""
import pandas as pd
import os
import CoclusteringModel as model
import math
import numpy as np
from random import shuffle
import io
from pathlib import Path
import SubDataSet as sds
import constants as const
from shutil import rmtree
from shutil import move


fileGlobalTrace=None

def globalTrace(message):
    """
    aim: prints a message in a file
    input: 
        message
    """
    if not fileGlobalTrace is None:
        fileGlobalTrace.write(message)
        fileGlobalTrace.flush()

  
def dataFileNameReader(inputDataFileName):
    """
    aim: reads a file
    input:
        inputDataFileName: file full path
    output:
        lines - table of sctring containing the data
        indexX, indexY, indexFreq - indexes of variable 1, 2 and Frequency
    """
    fInput = open(inputDataFileName, "r")
    lines=fInput.readlines()
    fInput.close()
    headerLine = lines[0][:-1]
    fieldNames = headerLine.split('\t')
    indexX = -1
    indexY = -1
    indexFreq = -1
    for index, field in enumerate(fieldNames):
        if field == "X":
             indexX = index
        if field == "Y":
            indexY = index
        if field == "Freq":
            indexFreq = index
    # Arret si fichier errone
    if indexX == -1 or indexY == -1:
        print("error in data file " + inputDataFileName + " (" + headerLine + ")")
        return
    return lines, indexX, indexY, indexFreq
    
def getXYFreq(inputDataFileName):
    """
    aim: reads a files and returns a dictionary (variable1, variable2):frequency
    input:
        inputDataFileName: file full path
    output:
        xyValues: dictionary containing the pair of values as keys and the frequency as objects
    """
    xyValues = {}
    lines, indexX, indexY, indexFreq = dataFileNameReader(inputDataFileName)
    # Parsing du fichier hors ligne d'entete
    for line in lines[1:] :
        sline=line[:-1].split('\t')
        # L'effectif vaut 1 par defaut
        frequency = 1
        if indexFreq != -1 and len(sline) > indexFreq:
            frequency = int(sline[indexFreq])
        # Mise a jour des effectif par valeur et par co-occurrence
        xVal = sline[indexX]
        yVal = sline[indexY]
        if (xVal,yVal) not in xyValues:
            xyValues[xVal, yVal] = frequency
        else:
            xyValues[xVal, yVal] += frequency
    
    return xyValues
    
def getValues(inputDataFileName):
    """
    aim: gets the value frequencies from a input file
    input:
        inputDataFileName: file full path
    output:
        xValFreq, yValFreq: dictionaries with values as keys and frequency as objects of variable 1 and 2
    """
    xValFreq = {}
    yValFreq = {}
    lines, indexX, indexY, indexFreq = dataFileNameReader(inputDataFileName)
    # Parsing du fichier hors ligne d'entete
    for line in lines[1:] :
        sline=line[:-1].split('\t')
        # L'effectif vaut 1 par defaut
        frequency = 1
        if indexFreq != -1 and len(sline) > indexFreq:
            frequency = int(sline[indexFreq])
        # Mise a jour des effectif par valeur et par co-occurrence
        xVal = sline[indexX]
        yVal = sline[indexY]
        if xVal in xValFreq:
            xValFreq[xVal] += frequency
        else:
            xValFreq[xVal] = frequency
        if yVal in yValFreq:
            yValFreq[yVal] += frequency
        else:
            yValFreq[yVal] = frequency
    return xValFreq, yValFreq




def getListCoarseClusters(SubDataSets, dim):
    """
    aim: return list of coarse clusters
    input:
        SubDataSets
        dim=0 or 1 - if 0 then works on variable 1 if 1 works on variable 2
    """
    
    list_clusters = []
    for cocluster in SubDataSets.keys():
        if cocluster[dim] not in list_clusters:
            list_clusters.append(cocluster[dim])
    return list_clusters

def getMicroClustersFromCoarseCluster(coarseCluster, variableValuesMicroClusters):
    """
    requires:
        coarseCluster - a list of values (coarse cluster)
        variableValuesMicroClusters - a list of clusters of values (micro clusters)
    ensures:
        a list of clusters of values in (micro clusters) of the given coarseCluster
    """
    dict_micro={}
    value2ClustDict = computeValueClusters(variableValuesMicroClusters)
    for value in coarseCluster:
        dict_micro[value] = value2ClustDict[value]
    microValueClusters = computeVariableCluster(dict_micro)
    return microValueClusters

def fromClustersOfMiniClustersToTrueValueClusters(variableValuesClusters, variableClusters):
    """
    require:
        variableValuesClusters - a list of clusters of values Ex: [['a','b'],['c','d'],['e','f']]
        variableClusters - a list of clusters of clusters Ex: [['C1','C2'],['C3']]
    
    ensures:
        a list of clusters with values in the place of variableClusters Ex:[['a','b','c','d'],['e','f']]
    
    """
    variableTrueValuesClusters=[]
    valClustDict = computeValueClusters(variableValuesClusters)
    for cluster in variableClusters:
        new_cluster = []
        for mini_cluster in cluster:
            trueValues = getListKeysByValue(valClustDict, mini_cluster)
            for value in trueValues:
                new_cluster.append(value)
        variableTrueValuesClusters.append(new_cluster)
    return variableTrueValuesClusters
         

def recodeListFileWithClusters(listInputDataFileName, variable1Clusters, variable2Clusters, outputDataFileName):
    """
    aim: recodes a list of data files with values into a data file with the corresponding clusters
    input:
        listInputDataFileName - input dataset file name
        variable1Clusters - variable clusters for variable 1
        variable2Clusters - variable clusters for variable 2
    output:
        cluster1Frequency - dictionary cluster as key and frequency as object for variable 1
        cluster2Frequency - dictionary cluster as key and frequency as object for variable 2
        outputDataFileName - recoded output file
    """
    cluster1cluster2={}
    cluster1Frequency = {}
    cluster2Frequency = {}
    
    for inputDataFileName in listInputDataFileName:
        xyValues = getXYFreq(inputDataFileName)
        
        xValClust = computeValueClusters(variable1Clusters)
        yValClust = computeValueClusters(variable2Clusters)
        
        for value1, value2 in xyValues.keys():
            cluster1=xValClust[value1]
            cluster2=yValClust[value2]
            
            frequency = xyValues[value1, value2]
            
            if (cluster1, cluster2) not in cluster1cluster2:
                cluster1cluster2[xValClust[value1], yValClust[value2]]=frequency
            else:
                cluster1cluster2[xValClust[value1], yValClust[value2]]+=frequency
                
            if cluster1 in cluster1Frequency:
                cluster1Frequency[cluster1]+=frequency
            else:
                cluster1Frequency[cluster1]=frequency
                
            if cluster2 in cluster2Frequency:
                cluster2Frequency[cluster2]+=frequency
            else:
                cluster2Frequency[cluster2]=frequency
        
        
        
    f=open(outputDataFileName, 'w')
    f.write('X\tY\tFreq\n')
    for cluster1, cluster2 in cluster1cluster2.keys():
        f.write('{0}\t{1}\t{2}\n'.format(cluster1, cluster2, cluster1cluster2[cluster1, cluster2]))
    f.close()
    
    return cluster1Frequency, cluster2Frequency, outputDataFileName
   

  
def computeValueClusters(variableClusters):
    """
    input: 
        variableClusters - table of clusters, and each cluster is a table of values
    output: 
        valueClusters - dictionary with values as  keys and cluster names (C1,C2,...) as objects
    """
    valueClusters={}
    for i,cluster in enumerate(variableClusters):
        clusterName='C'+str(i+1)
        for value in cluster:
            valueClusters[value]=clusterName
    return valueClusters

def computeVariableCluster(valueClusters):
    """    
    Input:
        valueClusters - dictionary with values as key and clusters as objects
    Output:
        variable1Clusters: tableau des clusters de valeurs de la premiere variable, chaque cluster etant un tableau de valeurs
    """
    
    variableClusters=[]
    listClusters=[]
    
    for value in valueClusters.keys():
        cluster = valueClusters[value]
        if cluster not in listClusters:
            variableClusters.append([value])
            listClusters.append(cluster)
        else:
            variableClusters[listClusters.index(cluster)].append(value)
        
    return variableClusters
            
def getPartitions(variableValues, c_max):
    """
    input: 
        variableValues - a dictionary of values:frequency
    output: 
        valueClusters - table of clusters, and each cluster is a table of values
    """
    n = sum(variableValues.values())
    variableValues=list(variableValues.keys())
    shuffle(variableValues)
    current_I_max = min(c_max,math.sqrt(n))
    current_vals = len(variableValues)
    valueClusters=[]
    i=0
    while current_I_max>0:
        nr_ins = round(current_vals/current_I_max) #values to use
        current_vals-=nr_ins
        current_I_max-=1
        valueClusters.append(variableValues[i:i+nr_ins])
        i+=nr_ins            
    
    return valueClusters

def getPartitionsFromModel(modelKhcFile, c_max, dim):
    """
    aim: from a model file obtain a a random partition
    requires:
        modelKhcFile - the model file .khc 
        variableValues - a dictionary of values:frequency
        c_max - the number of parts
        dim - if dim = 0 then works on variable 1 if dim =1 then works on variable 2
    ensures:
        valueClusters - table of clusters, and each cluster is a table of values
    """
    # parse le fichiers model
    m = model.CoclusteringModel(modelKhcFile)
    if dim==0:
        variableValues = m.XValFreq
        clustIndeces = m.XClustIndeces
        clustVals = m.XClustVals
    if dim==1:
        variableValues = m.YValFreq
        clustIndeces = m.YClustIndeces
        clustVals = m.YClustVals
    
    n = sum(variableValues.values())  
    
    variableValueClusters = []
    for cluster in range(len(clustIndeces)):
        vals =  clustVals[clustIndeces[cluster]]
        shuffle(vals)
        variableValueClusters.append(vals)
        
       
    variableValues=[]
    for k_vals in variableValueClusters:
        for val in k_vals:
            variableValues.append(val)
    
       
    current_I_max = min(c_max,math.sqrt(n))
    current_vals = len(variableValues)
    valueClusters=[]
    i=0
    while current_I_max>0:
        nr_ins = round(current_vals/current_I_max) #values to use
        current_vals-=nr_ins
        current_I_max-=1
        valueClusters.append(variableValues[i:i+nr_ins])
        i+=nr_ins     
        

    return valueClusters
    
#def testGetPartitionsFromModel():
#    modelKhcFile='D:/Utilisateur/Marius/TwoModeCoclustering_clear_v2/test/SmallTest.khc'
#    
#    valueClusters1 = getPartitionsFromModel(modelKhcFile, 10, 0)
#    valueClusters2 = getPartitionsFromModel(modelKhcFile, 10, 1)
    
     
def getColumnRowVariableClusterValues(SubDataSets, clusterVariable, dim):
    """
    input: 
        SubDataSets - dictionary of SubDataSet objects (see SubDataSet class)
        clusterVariable - name of cluster variable on row or column    Ex: 'C1'
        dim -  0 or 1 (0 if on_x and 1 if on_y)
    return:
        columnRowVariableClusterValues - list containing SubDataSet objects just one column/row
        
        Ex: for column 'C1'
        {('C1', 'C1'): <SubDataSet Object>,
        ('C1', 'C2'): <SubDataSet Object>,
        ('C1', 'C3'): <SubDataSet Object>
        ('C1', 'C4'): <SubDataSet Object>
        ('C1', 'C5'): <SubDataSet Object>
        ....
        }
    """        
    columnRowVariableClusterValues={}
    for k in SubDataSets.keys():
        if(k[dim]==clusterVariable):
            columnRowVariableClusterValues[k]=SubDataSets[k]
    return columnRowVariableClusterValues 

def writeKHCPartitionFile(xValClust, yValClust, xValFreq, yValFreq, outputModelFile):
    """
    input: 
        xValClust - dictionary value:cluster on variable 1
        yValClust - dictionary value:cluster on variable 2
        xValFreq - dictionary value:frequency on variable 1
        yValFreq - dictionary value:frequency on variable 2
    output:
        outputModelFile - writes the partition file .khc
        
    """
    ftemp=open(outputModelFile, 'w')
    
    ftemp.write('#Khiops 8.4.7.3i\n')
    ftemp.write('Dimensions\t2\n')
    ftemp.write('Name\tType\tParts\tInitial parts\tValues\tInterest\tDescription\n')
    ftemp.write(('X\tCategorical\t{0}\t{0}\t{1}\t1\t\n').format(len(np.unique(list(xValClust.values()))), len(np.unique(list(xValClust.keys())))))
    ftemp.write(('Y\tCategorical\t{0}\t{0}\t{1}\t1\t\n\n').format(len(np.unique(list(yValClust.values()))), len(np.unique(list(yValClust.keys())))))

    ftemp.write('Composition\tX\n')
    ftemp.close()
    
    cols=['Cluster','Value', 'Frequency', 'Typicality'] 
    
    arr=[]
    for k in xValClust.keys():
        arr.append([xValClust[k], k, xValFreq[k], 1])
    CX=pd.DataFrame(arr, columns=cols)
    
    CX.sort_values(by='Cluster').to_csv(outputModelFile, sep='\t', index=False, mode='a')
    
    ftemp=open(outputModelFile, 'a')
    ftemp.write('\nComposition\tY\n') # Write Composition Y\n
    ftemp.close()
    
    arr=[]
    for k in yValClust.keys():
        arr.append([yValClust[k], k, yValFreq[k], 1])
    CY=pd.DataFrame(arr, columns=cols)
    
    CY.sort_values(by='Cluster').to_csv(outputModelFile, sep='\t', index=False, mode='a')

def getIsError(logFilePathName):
    """
    requires: a log file path file
    ensures:
        true if there is an error in the log file coclustering
        false if the coclustering finishes without errors
    """
    isError=False
    logs = open(logFilePathName,'r')
    lines = logs.readlines()  
    logs.close()
    
    for line in lines:
        if 'error' in str.lower(line):
            isError=True
    
    return isError

def getIsIformative(outputKHCFilePath, logFilePathName):
    """
    input: outputKHCFilePath
    return: True/False depending if the model is informative
    """
    isInformative=False
    logs = open(logFilePathName,'r')
    lines = logs.readlines()  
    logs.close()
    if 'No informative coclustering found in data\n' not in lines:
        isInformative=True
        
    outputKHCFilePath_path = Path(outputKHCFilePath)
    if outputKHCFilePath_path.is_file():
        file_khc=open(outputKHCFilePath,'r')
        lines = file_khc.readlines()
        file_khc.close()
        dimension=int(lines[1].split('\t')[1].split('\n')[0])
        isInformative=not(dimension==1 or dimension==0)
    return isInformative
    

def splitDataFile(inputDataFileName, inputVariable1Clusters, inputVariable2Clusters, label='split'):
    """
    input: 
        inputDataFileName - data file 
        inputVariable1Clusters - tableau des clusters de valeurs de la premiere variable, chaque cluster etant un tableau de valeurs
        inputVariable2Clusters - tableau des clusters de valeurs de la deuxieme variable, chaque cluster etant un tableau de valeurs
        
        label='split' - prefix to use in file names
    
    aim:
        writes partitioned files
    
    returns:
        listSubDataSetsPartitionedFiles: list of SubDataSet objects (see SubDataSet class)
    """
    datalines, indexX, indexY, indexFreq = dataFileNameReader(inputDataFileName)
    
    variable1ValueCluster=computeValueClusters(inputVariable1Clusters)  
    variable2ValueCluster=computeValueClusters(inputVariable2Clusters) 
    
    Ic_Clusters = np.unique(list(variable1ValueCluster.values()))
    Jc_Clusters = np.unique(list(variable2ValueCluster.values()))
    
    all_coarse_files_data={}
    for cx in Ic_Clusters:
        for cy in Jc_Clusters:
            all_coarse_files_data[cx,cy]=io.StringIO()
    
    for line in datalines[1:] :
        sline=line[:-1].split('\t')
        xValue = sline[indexX]
        yValue = sline[indexY]
        all_coarse_files_data[variable1ValueCluster[xValue],variable2ValueCluster[yValue]].write(line)
    
    pathFiles = const.KHC_TemporaryDir+'/'+label+'/'
    detect_path(pathFiles)   
    
    dictSubDataSetsPartitionedFiles = {}
    #writing data
    for cx in Ic_Clusters:
        for cy in Jc_Clusters:
            file_name = pathFiles + label + '_' + str(cx) + '_' + str(cy)+'.txt'
            f = open(file_name,'w')
            if (indexFreq==0) & (indexX==1) & (indexY==2):
                f.write('Freq\tX\tY\n')
            if (indexFreq==2) & (indexX==0) & (indexY==1):
                f.write('X\tY\tFreq\n')
            ioBuffer = all_coarse_files_data[cx,cy]
            f.write(ioBuffer.getvalue())
            ioBuffer.close()
            f.close()
            
            sub_data_set = sds.SubDataSet(cx, cy, file_name)
            dictSubDataSetsPartitionedFiles[cx, cy] = sub_data_set
            
    return dictSubDataSetsPartitionedFiles

        
def detect_path(pathname):
    """
    requires: 
        a path name
    ensures:
        creqtes the path if it does not exist
    """
    if not os.path.exists(pathname):
        os.makedirs(pathname, exist_ok=True)

def getLevelFromKhcRapport(path_rapport):
    """
    requires:
        a coclustering repport
    ensures:
        returns the coclustering level
    """
    f=open(path_rapport,'r')
    for l in f:
        if 'Level\t' in l:
            s=l
            break
    #print(s)
    level = s.split('\t')[1].split('\n')[0]
    f.close()
    return level


def getModelCriterion(modelFileName):
    """
    requires:
        a coclustering model
    ensures:
        the prior, loglikelihood and the MODL criterion for the required model
    """
    m = model.CoclusteringModel(modelFileName)
    prior=m.computePrior()
    ll=m.computeLikelihood()
    criterion = ll+prior
    return prior,ll,criterion
    
def move_file(destination_path,source_path):
    if os.path.isfile(destination_path):
        move(destination_path, source_path)

def delete_folder(pth) :
    """
    requires: 
        the path
    ensures:
        delete the folder and all subfolders
    """
    if  os.path.exists(pth):
        rmtree(pth)
 
def delete_file(path):
    """
    requires:
        param <path> that is the file
    ensures:
        deletes the given file
    """

    if os.path.isfile(path):
        os.remove(path)  # remove the file
#    elif os.path.isdir(path):
#        shutil.rmtree(path)  # remove dir and all contains
    else:
        raise ValueError("file {} is not a file.".format(path))


def getListKeysByValue(dictionary, searched_value):
    """
    aim: searches by value(object) in a dictionary
    requires:
        a dictionary 
        a value that will be searched
    ensures
        a list of keys with the searched value
    """
    return [k for k, v in dictionary.items() if v == searched_value]   
    
def getDictWithEqualValues(dictionary, val_detect):
    """
    requires:
        a dictionary
        value to searche
    ensures:
        a dictionary with the searced value
    """
    return {k:v for k, v in dictionary.items() if v == val_detect}


def getDictValuesStartsWith(dictionary,val_detect):
    """
    requires:
        a dictionary
        val_detect - value to start with
    ensures:
        a dictionary with the value that starts with val_detect
    """
    return {k:v for k, v in dictionary.items() if v.startswith(val_detect)}