# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 10:35:40 2018

@author: HZTT9795
"""
import KHCUtils as khc
import constants as const
import utils as utl
import os

class SubDataSet():
    """
    class SubDataSet
    aim: geather information for sub-dataset
    attributes:
        indexVariable1 - index of sub dataset on variable 1 (obtained in the partitioning step)
        indexVariable2 - index of sub dataset on variable 2 (obtained in the partitioning step)
        datasetFileName - sub data set file full path name (obtained in the partiioning step)
        fineCoclusteringKHCFileName - sub data set khc model file full path name (obtained by the fine coclustering and modified if simplify coclustering)
        variable1Clusters - list of variable clusters (with values) for variable 1 (obtained by the fine coclustering and modified if simplify coclustering)
        variable2Clusters - list of variable clusters (with values) for variable 2 (obtained by the fine coclustering and modified if simplify coclustering)
    methods:
        fineCoclustering()
        simplifyClustering(dimensionName, c_max)
    """
    def __init__(self, indexVariable1, indexVariable2, datasetFileName):
        self.indexVariable1=indexVariable1
        self.indexVariable2=indexVariable2
        self.datasetFileName=datasetFileName
        self.fineCoclusteringKHCFileName = ''
        self.variable1Clusters=[]
        self.variable2Clusters=[]
        
    def fineCoclustering(self):
        """
        aim: 
            run KHCc on datasetFileName
            set variable1Clusters, variable1Clusters
            set fineCoclusteringKHCFileName
        """
        c_max = const.Imax
        variable1Values, variable2Values=utl.getValues(self.datasetFileName)
        #MB pathFiles = os.path.dirname(os.path.abspath(self.datasetFileName))
#        pathFiles = const.KHC_TemporaryDir + const.labelKHCf + '/' #MB
        partitionFileName = os.path.splitext(os.path.basename(self.datasetFileName))[0]
        outputKHCFilePath=partitionFileName+'.khc'
        self.variable1Clusters, self.variable2Clusters, outputKHCFilePath = khc.KHCc(self.datasetFileName, variable1Values, variable2Values, c_max, const.labelKHCf, outputKHCFilePath)
        self.fineCoclusteringKHCFileName = outputKHCFilePath
        
    def simplifyClustering(self, dimensionName, c_max):
        """
        aim:
            simplify coclustering on sub dataset
            update fineCoclusteringKHCFileName
            update variable1Clusters, variable2Clusters
        input:
            dimensionName - 0 or 1
            c_max - the number of clusters to simplify
        """
        if (len(self.variable1Clusters)>1 and  len(self.variable2Clusters)>1):
#            pathFiles = os.path.dirname(os.path.abspath(self.fineCoclusteringKHCFileName))+'/'
            outputKHCFilePath = os.path.basename(self.fineCoclusteringKHCFileName).split('.')[0]+'s.khc'
            self.variable1Clusters, self.variable2Clusters, filePathName = khc.KHCs(self.fineCoclusteringKHCFileName, dimensionName, c_max, const.labelSimplify, outputKHCFilePath)
#            self.fineCoclusteringKHCFileName = pathFiles+filePathName
            self.fineCoclusteringKHCFileName = filePathName 

