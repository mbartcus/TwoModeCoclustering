# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 10:10:17 2018

@author: HZTT9795
"""
import utils as utl
import constants as const
import KHCUtils as khc
import KHChoosePartitionSize as part_utils
import math
import os
import datetime
from time import time


class LargeScaleDataSet():
    """
    aim: 
        set information about the data file and run our two level coclusteing algorithm
    public attributes:
        inputDataFileName - dataset file name
        outputCoclusteringFileName
        
    public methods:
        trainCoclustering(coclusteringFileName)
        
    private attributes:
        _variable1ValuesFrequency - dictionnaire des valeurs de la premiere variable, avec effectif par valeur
        _variable2ValuesFrequency - dictionnaire des valeurs de la deuxieme variable, avec effectif par valeur
        _Ic, _Jc - number of coarse clusters on variable 1 and respectively variable 2 (obtained in the partiting step)
        _variable1CoarseClusters - coarse clusters of values of variable 1 (obtained in partitioning step)
        _variable2CoarseClusters - coarse cluster of values of variable 2 (obtained in partitioning step)
        _SubDataSets - dictionary [Ic,Jc]:<SubDataSet> of SubDataSet objects (see SubDataSet class)
        _variable1MicroCluster - micro clusters on variable 1 (obtained by mitigate step)  dictionary with values as keys and clusters as objects
        _variable2MicroCluster - micro clusters on variable 2 (obtained by mitigate step)  dictionary with values as keys and clusters as objects
    private methods:
        __partitionStep(outputKHCFile='partitioning.khc')
        __fineCoclusteringStep()
        __mitigateStep
        __amalgamateStep
        __cleanWorkingData
        __cleanWorkingDirectory

    """
    def __init__(self, inputDataFileName):
        utl.globalTrace("{0}\t Init Large Scale DataSet\n".format(datetime.datetime.now()))
        utl.delete_folder(const.KHC_TemporaryDir)
        self.__cleanWorkingData()
        self.inputDataFileName = inputDataFileName
        utl.globalTrace("{0}\t End Init Large Scale DataSet\n".format(datetime.datetime.now()))
        
    def __cleanWorkingData(self):
        """
        aim: clean working data
        """
        utl.globalTrace("{0}\t Clean working data\n".format(datetime.datetime.now()))
        self.inputDataFileName = None
        self.outputCoclusteringFile=None
        self._variable1ValuesFrequency, self._variable2ValuesFrequency=None, None
        self._Ic, self._Jc = None, None
        self._variable1CoarseClusters, self._variable2CoarseClusters = None, None
        self._SubDataSets=None
        self._variable1MicroCluster = None
        self._variable2MicroCluster = None
        utl.globalTrace("{0}\t End Clean working data\n".format(datetime.datetime.now()))
    
    def __cleanWorkingDirectory(self):
        """
        aim: clean working directory
        """
        if not const.KHC_KeepWorkingDir:
            utl.globalTrace("{0}\t Clean working directory: \t {1}\n".format(datetime.datetime.now(), const.KHC_TemporaryDir))
            utl.delete_folder(const.KHC_TemporaryDir)
            utl.globalTrace("{0}\t End Clean working directory\n".format(datetime.datetime.now()))
        
    def __createWorkingDirectory(self):
        """
        aim: create working directory if it does not exist
        """
        utl.globalTrace("{0}\t Detect and create if necessary working directory: \t {1}\n".format(datetime.datetime.now(), const.KHC_TemporaryDir))
        utl.detect_path(const.KHC_TemporaryDir)
        utl.globalTrace("{0}\t End Detect working directory\n".format(datetime.datetime.now()))
    
    def trainCoclustering(self,coclusteringFileName):
        """
        aim:
            runs the optimize coclustering two level coclustering
        requires:
            the name of coclustering file as output
        ensures:
            obtain the coclustering
        """
        start_time = time()
        utl.globalTrace("{0}\t Start train optimized co-clustering\n".format(datetime.datetime.now()))
        self.__cleanWorkingDirectory()
           
        
        self.outputCoclusteringFile = coclusteringFileName
        self._variable1ValuesFrequency, self._variable2ValuesFrequency=utl.getValues(self.inputDataFileName)    

        Vx = len(self._variable1ValuesFrequency)
        Vy = len(self._variable2ValuesFrequency)
        utl.globalTrace("{0}\t File:\t{1}\t Vx:\t{2} \t Vy:\t{3}\n".format(datetime.datetime.now(), self.inputDataFileName, Vx, Vy))
        
        self.__partitionStep()
        self.__fineCoclusteringStep()
        self.__mitigateStep()
        self.__amalgamateStep()
        self.__postOptimizeStep()
        
        utl.globalTrace("{0}\t End train optimized co-clustering \t Output:  {1}\n".format(datetime.datetime.now(), self.outputCoclusteringFile))
        self.__cleanWorkingData()
        self.__cleanWorkingDirectory()
        utl.globalTrace('Total time: \t {0}\n'.format(time()-start_time))
    def __partitionStep(self, outputKHCFile='partitioning.khc'):
        
        """
        aim: partition the data set and create sub data sets
        input:
            outputKHCFile='partitioning.khc'
        require: inputDataFileName, variable1ValuesFrequency, variable2ValuesFrequency
        ensure: IC, JC, variable1CoarseClusters, variable2CoarseClusters, SubDataSets (initialises)
        """
        utl.globalTrace("{0}\t Start partitioning step: \n".format(datetime.datetime.now()))
        vx=len(self._variable1ValuesFrequency)
        vy=len(self._variable2ValuesFrequency)
        n=sum(self._variable1ValuesFrequency.values())
        self._Ic, self._Jc, time2LKHC = part_utils.ChoosePartitionSize(n, vx, vy)  
        
        utl.globalTrace("{0}\t Start KHCp \t Vx:\t{1}\t Vy:\t{2}\t N:\t{3}\t Ic:\t{4}\t Jc:\t{5} \n".format(datetime.datetime.now(), vx, vy, n, self._Ic, self._Jc))        
        self._variable1CoarseClusters, self._variable2CoarseClusters = khc.KHCp(self.inputDataFileName, self._variable1ValuesFrequency, self._variable2ValuesFrequency, self._Ic, self._Jc, const.labelKHCp, outputKHCFile)
        utl.globalTrace("{0}\t End KHCp \t Ic:\t{1}\t Jc:\t{2} \n".format(datetime.datetime.now(), len(self._variable1CoarseClusters), len(self._variable2CoarseClusters)))        
        self._SubDataSets={}
        utl.globalTrace("{0}\t Run split data sets \n".format(datetime.datetime.now()))
        self._SubDataSets = utl.splitDataFile(self.inputDataFileName, self._variable1CoarseClusters, self._variable2CoarseClusters, const.labelKHCsplit)
        utl.globalTrace("{0}\t End split data sets \n".format(datetime.datetime.now()))
        utl.globalTrace("{0}\t End partitioning step: \n".format(datetime.datetime.now()))
    def __fineCoclusteringStep(self):
        """
        aim: run KHCc for each of partitioned files
            update self.SubDataSets
        require: SubDataSets (initialized in the partitionStep)
        ensure: ubdates SubDataSets with the fine coclustering information
            
        """
        utl.globalTrace("{0}\t Run fine coclustering step: \n".format(datetime.datetime.now()))
        for subDataSet in self._SubDataSets.keys():
            self._SubDataSets[subDataSet].fineCoclustering()
            Ix = len(self._SubDataSets[subDataSet].variable1Clusters)
            Iy = len(self._SubDataSets[subDataSet].variable2Clusters)
            utl.globalTrace("{0}\t Fine coclustering \t(Ic,Jc):\t{1} \t Ix:\t{2} \t Iy:\t{3} \n".format(datetime.datetime.now(), subDataSet, Ix, Iy ))
        utl.globalTrace("{0}\t End fine coclustering step: \n".format(datetime.datetime.now()))
            
    def __mitigateStep(self):
        """
        aim: 
            obtain the finest co-clustering on the hole dataset (micro clusters)
            mitigate fine clusters on each column data sets and obtain micro clusters 
            for variable 1 and variable 2
        require: SubDataSets (with the fine coclustering information)
        ensures: _variable1MicroCluster, _variable1MicroCluster - micro clusters for variable 1 and respectively variable 2
        """
        def computeDefaultCluster(variableCluster):
            """
            input: 
                variableCluster - list of clusters with list of values
            output:
                default cluster with the smallest size of values
            requieres: a list of variable clusters
            ensures: a default cluster with the smallest number of values
            """
            clusterSize = math.inf
            for i,cluster in enumerate(variableCluster):
                if len(cluster)<clusterSize:
                    clusterSize = len(cluster)
                    defaultCluster = 'C'+str(i+1)
            return defaultCluster
            
        def mitigateOn(SubDataSets, variableCoarseClusters, dim):
            """
                aim: make the job (on two dimensions) of mitigate the clusters obtained in the fine co-custering step
                input:
                    dim: 0 or 1 (0 if 'on_x' or 1 if 'on_y')
                output:
                    variableMicroClusters - dictionary with values as keys and clusters as objects
                
                requires: 
                    the dimension (dim 0 or 1) over which we mitigate
                    the SubDataSets containing information about the fine coclustering over all subdatasets
                    variableCoarseClusters - variable clusters (list of list of values)
            """ 
            #utl.globalTrace("{0}\t Mitigate coclustering: \t dimension:\t{1} \t list_clusters:\t{2}\t coarse clusters:\t {3}\n".format(datetime.datetime.now(), dim, len(list_clusters), len(variableCoarseClusters))) 
                    
            valueMicroClusterName={}
            # parcourir une seule colone ou ligne data set
            for i,coarseCluster in enumerate(variableCoarseClusters):
                coarse_cluster_label = 'C{0}'.format(i+1)
                
                columnRowDataSetClusters = utl.getColumnRowVariableClusterValues(SubDataSets, coarse_cluster_label, dim)
                
                #parcourir une sub dataset
                for cocluster in columnRowDataSetClusters.keys(): #Ex: cocluster ('C1','C1')
                    if dim==0:
                        fineCoclusteringValuesClusters = utl.computeValueClusters(columnRowDataSetClusters[cocluster].variable1Clusters)
                        defaultCluster = computeDefaultCluster(columnRowDataSetClusters[cocluster].variable1Clusters)
                        
                    if dim==1:
                        fineCoclusteringValuesClusters = utl.computeValueClusters(columnRowDataSetClusters[cocluster].variable2Clusters)
                        defaultCluster = computeDefaultCluster(columnRowDataSetClusters[cocluster].variable2Clusters)
                        
                    
                    for value in coarseCluster:
                        
                        if value not in valueMicroClusterName:
                            valueMicroClusterName[value]=coarse_cluster_label
                           
                        if value in fineCoclusteringValuesClusters:
                            fineClusterName = fineCoclusteringValuesClusters[value]
                            valueMicroClusterName[value]+=fineClusterName
                        else:
                            valueMicroClusterName[value]+=defaultCluster
            
            variableMicroClusters = utl.computeVariableCluster(valueMicroClusterName)                
            return variableMicroClusters
            
        utl.globalTrace("{0}\t Run mitigate coclustering step \n".format(datetime.datetime.now()))  
        self._variable1MicroCluster = mitigateOn(self._SubDataSets, self._variable1CoarseClusters, 0)
        self._variable2MicroCluster = mitigateOn(self._SubDataSets, self._variable2CoarseClusters, 1)
        micro_Ix = len(self._variable1MicroCluster)
        micro_Iy = len(self._variable2MicroCluster)
        utl.globalTrace("{0}\t End mitigate coclustering step \t Micro Ix: \t {1} \t Micro Iy: \t {2}\n".format(datetime.datetime.now(), micro_Ix, micro_Iy))
        
            
        
    
    def __amalgamateStep(self):
        """
            aim: reduce the number of micro clusters obtained in the mitigate step
            
            contains two inner funcitons: 
                1) amalgamateStepColumns()
                2) amalgamateStepRows()
            
        """
        def amalgamateStepColumns():
            """
            aim: amalgamate step columns
            require:
                the SubDataSets containing information about the fine coclustering over all subdatasets
                variable1CoarseClusters - cluster of values (coarse cluster)
                variable1ValuesMicroClusters = clusters of values (micro or mini clusters)
                Ic - number of coarse clusters
            ensures:
                mini clusters on X
            """
            
            Vx = len(self._variable1MicroCluster)#number of micro clusters on variable 1
            
            utl.globalTrace("{0}\t Run Amalgamation column data sets \t Ic:\t{1}\t micro clusters Vx:\t{2} \n".format(datetime.datetime.now(), self._Ic, Vx)) 
            
            if Vx>const.Vmax and self._Ic>1:
                variable1MiniClusters = []
                dim=0
                
                columnDataSetModels={}
                #{Reduce the number of micro clusters on X based on mini clusters with VsX<Vmax}
                utl.globalTrace("{0}\t Reduce the number of micro clusters on X based on mini clusters with VsX<Vmax \n".format(datetime.datetime.now())) 
                
                for i,coarseCluster in enumerate(self._variable1CoarseClusters):
                    coarse_cluster_label = 'C{0}'.format(i+1)
                    
                    columnDataSetClusters = utl.getColumnRowVariableClusterValues(self._SubDataSets, coarse_cluster_label, dim)
                    #get number of fine clusters on variable 2 of coarse cluster: cluster
                    Vy=0 #number of fine clusters on variable 2
                    for cocluster in columnDataSetClusters.keys():
                        current_Vy = len(columnDataSetClusters[cocluster].variable2Clusters)
                        Vy+=current_Vy
                        
                    #{Reduce the number of fine clusters on Y per sub data set of the column data set}
                    if Vy>const.Vmax:
                        # simplify for all sub data set models in the column data set
                        utl.globalTrace("{0}\t Reduce the number of fine clusters on Y per sub data set of the column data set \t coarse cluster \t {1} fine clusters Vy \t {2} \n".format(datetime.datetime.now(), coarse_cluster_label, Vy)) 
                        for subDataSet in columnDataSetClusters.keys():
                            #{compute the maximum number of fine clusters per sub dataset}
                            current_Vy = len(columnDataSetClusters[subDataSet].variable2Clusters)
                            c_max = math.ceil(current_Vy/Vy * const.Vmax)
                            columnDataSetClusters[subDataSet].simplifyClustering(1, c_max)
                            utl.globalTrace("{0}\t KHCs \t (Ic, Jc): \t {0} \t current_Vy: \t {1} \t c_max \t {2} \n".format(datetime.datetime.now(), subDataSet, current_Vy, c_max)) 
                    
                    #{Reduce the number of micro clusters on X of the column data set}
                    utl.globalTrace("{0}\t Reduce the number of micro clusters on X of the column data set \t coarse cluster \t {1} \n".format(datetime.datetime.now(), coarse_cluster_label)) 
                    #-set of micro clusters on X for D_alpha.
                    micro_Vx = utl.getMicroClustersFromCoarseCluster(coarseCluster, self._variable1MicroCluster)
                    
                    #-set of reduced fine clusters on Y for D_alpha.
                    reduced_Vy=[]
                    for subDataSet in columnDataSetClusters.keys():
                        rVy = columnDataSetClusters[subDataSet].variable2Clusters
                        for fine_cluster in rVy:
                            if fine_cluster!=[]:
                                reduced_Vy.append(fine_cluster)
                    
                    
                    #run KHCc on column data set
                    #utl.globalTrace("{0}\t Recode column data set with files: \n".format(datetime.datetime.now())) 
                    
                    coarse_list_Files = []
                    for subDataSet in columnDataSetClusters.keys():
                        utl.globalTrace("\t {0} \n".format(columnDataSetClusters[subDataSet].datasetFileName))
                        coarse_list_Files.append(columnDataSetClusters[subDataSet].datasetFileName)
                    pathFiles = const.KHC_TemporaryDir + const.labelAmalgamate + '/'
                    utl.detect_path(pathFiles)
                    dataFileName = os.path.basename(os.path.abspath(self.inputDataFileName)).split('.')[0]
                    outputDataFileName = pathFiles  + dataFileName + '_Col_{0}.txt'.format(coarse_cluster_label)
                    cluster1Frequency, cluster2Frequency, outputDataFileName = utl.recodeListFileWithClusters(coarse_list_Files, micro_Vx, reduced_Vy, outputDataFileName)
                    #utl.globalTrace("\t -> write {0} \t for row data \t {1} \n".format(outputDataFileName, coarse_cluster_label))
                    
                    outputKHCFilePath= const.labelAmalgamate + dataFileName + '_Col_{0}.khc'.format(coarse_cluster_label)
                    
                    utl.globalTrace("{0}\t Start KHCc on column \t {1} \t VsX: \t {2} \t VsY: \t {3} \n".format(datetime.datetime.now(), coarse_cluster_label, len(micro_Vx), len(reduced_Vy))) 
                    
                    #compute mini clusters of micro clusters
                    variable1MiniClustersOnCol, variable2MiniClustersOnCol, _ = khc.KHCc(outputDataFileName, cluster1Frequency, cluster2Frequency, const.Imax, const.labelAmalgamate, outputKHCFilePath)
                    
                    utl.globalTrace("{0}\t End KHCc on column \t {1} \t VsX: \t {2} \t VsY: \t {3} \t -> mini clusters \t VsX: \t {4} \t VsY: \t {5} \n".format(datetime.datetime.now(), coarse_cluster_label, len(micro_Vx), len(reduced_Vy), len(variable1MiniClustersOnCol), len(variable2MiniClustersOnCol) )) 
                    
                    
                    
                    #from mini clusters of micro clusters -> TRUE Values
                    variable1MiniClustersOnCol = utl.fromClustersOfMiniClustersToTrueValueClusters(micro_Vx, variable1MiniClustersOnCol)                    
                    
                    
                    
                    
                    columnDataSetModels[coarse_cluster_label] = (pathFiles + outputKHCFilePath, variable1MiniClustersOnCol)
                    
                    for miniCluster in variable1MiniClustersOnCol:
                        variable1MiniClusters.append(miniCluster)
                        
                    if not const.KHC_KeepRecodedFiles:
                        utl.delete_file(outputDataFileName)
                #{Reduce the toatal number of mini clusters of all column data sets}
                if len(variable1MiniClusters)>const.Vmax:
                    utl.globalTrace("{0}\t Reduce the total number of mini clusters of all column data sets \n".format(datetime.datetime.now() )) 
                    
                    updatedVariable1MiniClusters = []
                    for coarseCluster in columnDataSetModels.keys():
                        modelkhc = columnDataSetModels[coarseCluster][0]
                        current_Vx = len(columnDataSetModels[coarseCluster][1])
                        
                        if current_Vx<2:
                            variable1Clusters = columnDataSetModels[coarseCluster][1]
                        else:
                            c_max = math.ceil(current_Vx/len(variable1MiniClusters) * const.Vmax)
                            outputKHCFilePath = os.path.basename(modelkhc).split('.')[0]+'s.khc'
                            variable1Clusters, variable2Clusters, filePathName = khc.KHCs(modelkhc, 0, c_max, const.labelSimplify, outputKHCFilePath)
                            
                            micro_Vx = columnDataSetModels[coarseCluster][1] # mini clusters of values
                            #from mini clusters of micro clusters -> TRUE Values
                            #index = int(coarseCluster.split('C')[1])-1
                            #micro_Vx = utl.getMicroClustersFromCoarseCluster(self._variable1CoarseClusters[index], self._variable1MicroCluster)
                            
                            variable1Clusters = utl.fromClustersOfMiniClustersToTrueValueClusters(micro_Vx, variable1Clusters)                              
                        for cluster in variable1Clusters:
                            updatedVariable1MiniClusters.append(cluster)
                    utl.globalTrace("{0}\t END Reduce the total number of mini clusters of all column data sets\n".format(datetime.datetime.now()))         
                    return updatedVariable1MiniClusters # if Vx>const.Vmax and Ic>1 and then reduced on each column data set
                else:
                    return variable1MiniClusters # if not need to reduced on each column data set
            else:
                return self._variable1MicroCluster #(if not Vx>const.Vmax and Ic>1) returns original
                    
        def amalgamateStepRows():
            """
            aim: amalgamate step rows
            require:
                the SubDataSets containing information about the fine coclustering over all subdatasets
                variable2CoarseClusters - cluster of values (coarse cluster)
                variable2MicroClusters = clusters of values (micro or mini clusters) for variable 2
                variable1ValuesMicroClusters = clusters of values (micro or mini clusters) for variable 1 obtained in the amalgamate on columns
                Jc - number of coarse clusters
            ensures:
                mini clusters on Y
            """
            Vy = len(self._variable2MicroCluster)#number of micro clusters on variable 2
            
            utl.globalTrace("{0}\t Run Amalgamation row data sets \t Jc:\t{1}\t micro clusters Vy:\t{2} \n".format(datetime.datetime.now(), self._Jc, Vy)) 
            
            #{Reduce the number of micro clusters on Y per row data set}
            if Vy>const.Vmax and self._Jc>1:
                variable2MiniClusters = []
                dim=1
                rowDataSetModels={}
                for i,coarseCluster in enumerate(self._variable2CoarseClusters):                    
                    coarse_cluster_label = 'C{0}'.format(i+1)
                    utl.globalTrace("{0}\t START Reduce the number of micro clusters on Y per row data set \t {1}\n".format(datetime.datetime.now(), coarse_cluster_label)) 
                    rowDataSetClusters = utl.getColumnRowVariableClusterValues(self._SubDataSets, coarse_cluster_label, dim)
                    #-set of micro clusters on X 
                    micro_Vx = self._variable1MicroCluster
                    #-set of micro clusters on Y for D_alpha.
                    micro_Vy = utl.getMicroClustersFromCoarseCluster(coarseCluster, self._variable2MicroCluster)
                    
                    
                    #run KHCc on row data set
                    #utl.globalTrace("{0}\t Recode row data set with files: \n".format(datetime.datetime.now())) 
                    coarse_list_Files = []
                    for subDataSet in rowDataSetClusters.keys():
                        utl.globalTrace("\t {0} \n".format(rowDataSetClusters[subDataSet].datasetFileName))
                        coarse_list_Files.append(rowDataSetClusters[subDataSet].datasetFileName)
                    
                    pathFiles = const.KHC_TemporaryDir + const.labelAmalgamate + '/'
                    utl.detect_path(pathFiles)
                    dataFileName = os.path.basename(os.path.abspath(self.inputDataFileName)).split('.')[0]
                    outputDataFileName = pathFiles  + dataFileName + '_Row_{0}.txt'.format(coarse_cluster_label)
                    cluster1Frequency, cluster2Frequency, outputDataFileName = utl.recodeListFileWithClusters(coarse_list_Files, micro_Vx, micro_Vy, outputDataFileName)
                    
                    
                    #utl.globalTrace("\t -> write {0} \t for row data \t {1} \n".format(outputDataFileName, coarse_cluster_label))
                    
                    utl.globalTrace("{0}\t Start KHCc on row \t {1} \t VsX: \t {2} \t VsY: \t {3} \n".format(datetime.datetime.now(), coarse_cluster_label, len(micro_Vx), len(micro_Vy))) 
                    outputKHCFilePath= const.labelAmalgamate + dataFileName + '_Row_{0}.khc'.format(coarse_cluster_label)
                    #compute mini clusters of micro clusters
                    variable1MiniClustersOnRow, variable2MiniClustersOnRow, _ = khc.KHCc(outputDataFileName, cluster1Frequency, cluster2Frequency, const.Imax, const.labelAmalgamate, outputKHCFilePath)
                    utl.globalTrace("{0}\t End KHCc on row \t {1} \t VsX: \t {2} \t VsY: \t {3} \t -> mini clusters \t VsX: \t {4} \t VsY: \t {5} \n".format(datetime.datetime.now(), coarse_cluster_label, len(micro_Vx), len(micro_Vy), len(variable1MiniClustersOnRow), len(variable2MiniClustersOnRow) )) 
                    
                    
                    #from mini clusters of micro clusters -> TRUE Values
                    variable2MiniClustersOnRow = utl.fromClustersOfMiniClustersToTrueValueClusters(micro_Vy, variable2MiniClustersOnRow)                    
                    
                    
                    rowDataSetModels[coarse_cluster_label] = (pathFiles + outputKHCFilePath, variable2MiniClustersOnRow)
                    for miniCluster in variable2MiniClustersOnRow:
                        variable2MiniClusters.append(miniCluster)
                        
                    if not const.KHC_KeepRecodedFiles:
                        utl.delete_file(outputDataFileName)
                    utl.globalTrace("{0}\t END Reduce the number of micro clusters on Y per row data set \t {1}\n".format(datetime.datetime.now(), coarse_cluster_label))
                
                #{Reduce the toatal number of mini clusters of all row data sets}
                if len(variable2MiniClusters)>const.Vmax:
                    utl.globalTrace("{0}\t START Reduce the total number of mini clusters of all row data sets\n".format(datetime.datetime.now())) 
                    updatedVariable2MiniClusters = []
                    for coarseCluster in rowDataSetModels.keys():
                        modelkhc = rowDataSetModels[coarseCluster][0]
                        
                        current_Vy = len(rowDataSetModels[coarseCluster][1])# mini clusters of values
                        
                        if current_Vy<2:
                            variable2Clusters = rowDataSetModels[coarseCluster][1] # mini clusters of values
                        else:
                            c_max = math.ceil(current_Vy/len(variable2MiniClusters) * const.Vmax)
                            outputKHCFilePath = os.path.basename(modelkhc).split('.')[0]+'s.khc'
                            variable1Clusters, variable2Clusters, filePathName = khc.KHCs(modelkhc, 1, c_max, const.labelSimplify, outputKHCFilePath)
                            
#                            micro_Vy=rowDataSetModels[coarseCluster][1]
#                            variable2Clusters = utl.fromClustersOfMiniClustersToTrueValueClusters(micro_Vy, variable2Clusters)
                            
                            #index = int(coarseCluster.split('C')[1])-1
                            micro_Vy = rowDataSetModels[coarseCluster][1] # mini clusters of values
                            #utl.getMicroClustersFromCoarseCluster(self._variable2CoarseClusters[index], self._variable2MicroCluster)
                            
                            variable2Clusters = utl.fromClustersOfMiniClustersToTrueValueClusters(micro_Vy, variable2Clusters)                              
                        for cluster in variable2Clusters:
                            updatedVariable2MiniClusters.append(cluster)
                            
                    utl.globalTrace("{0}\t END Reduce the total number of mini clusters of all row data sets\n".format(datetime.datetime.now())) 
                    
                    return updatedVariable2MiniClusters # if Vy>const.Vmax and Jc>1 and then reduced micro clusters on each row data set
                else:
                    return variable2MiniClusters # if not need to reduced on each row data set
            else:
                return self._variable2MicroCluster #(if not Vy>const.Vmax and Jc>1) returns original
            
            
        
        utl.globalTrace("{0}\t Run Amalgamation step \n".format(datetime.datetime.now())) 
        self._variable1MicroCluster = amalgamateStepColumns()
        self._variable2MicroCluster = amalgamateStepRows()  
        
        
        
#        utl.globalTrace("\n \n  _variable1MicroCluster \n {0} \n\n\n".format(self._variable1MicroCluster)) 
#        
#        utl.globalTrace("\n \n  _variable2MicroCluster \n {0} \n\n\n".format(self._variable2MicroCluster)) 
        
        
        
        utl.globalTrace("{0}\t End Amalgamation step \n".format(datetime.datetime.now())) 
        
    def __postOptimizeStep(self):
        """
            aim: writes a khc file with the true MODL cost
            require:
                inputDataFileName - the data file
                _variable1MicroCluster, _variable2MicroCluster - clusters of values (micro or mini clusters)
                _variable1ValuesFrequency, _variable2ValuesFrequency - true value frequencies dictionaries
            ensures:
                outputCoclusteringRapport - writes tha output coclustering file
        """
        utl.globalTrace("{0}\t Run post optimization coclustering step \n".format(datetime.datetime.now())) 
        
        pathFiles = const.KHC_TemporaryDir + const.labelPostOpt + '/'
        utl.detect_path(pathFiles)
        
        utl.globalTrace("{0}\t Run Recode mini clusters \n".format(datetime.datetime.now())) 
        dataFileName = os.path.basename(os.path.abspath(self.inputDataFileName)).split('.')[0]
        outputDataFileName = pathFiles  + dataFileName + '_micro.txt'
        cluster1Frequency, cluster2Frequency, outputDataFileName = utl.recodeListFileWithClusters([self.inputDataFileName], self._variable1MicroCluster, self._variable2MicroCluster, outputDataFileName)
        utl.globalTrace("{0}\t End Recode mini clusters \t Output file: \t {1}\n".format(datetime.datetime.now(), outputDataFileName))    
        
        utl.globalTrace("{0}\t Run KHCc on mini clusters \n".format(datetime.datetime.now())) 
        outputKHCFilePath= const.labelPostOpt + dataFileName + '_micro.khc'
        #compute clusters of micro clusters
        variable1Clusters, variable2Clusters, _ = khc.KHCc(outputDataFileName, cluster1Frequency, cluster2Frequency, const.Imax, const.labelPostOpt, outputKHCFilePath)
        if not const.KHC_KeepRecodedFiles:
            utl.delete_file(outputDataFileName)
        Ix_mini = len(variable1Clusters)
        Iy_mini = len(variable2Clusters)
        utl.globalTrace("{0}\t End KHCc on mini clusters \t Ix mini:\t {1}\t Iy mini:\t {2}\n".format(datetime.datetime.now(), Ix_mini, Iy_mini)) 
        
        
        utl.globalTrace("{0}\t Run format mini clusters to true values \n".format(datetime.datetime.now())) 
        variable1TrueValuesClusters = utl.fromClustersOfMiniClustersToTrueValueClusters(self._variable1MicroCluster, variable1Clusters)
        variable2TrueValuesClusters = utl.fromClustersOfMiniClustersToTrueValueClusters(self._variable2MicroCluster, variable2Clusters)
        Ix_mini = len(variable1TrueValuesClusters)
        Iy_mini = len(variable2TrueValuesClusters)
        utl.globalTrace("{0}\t End format mini clusters to true values \t Ix mini:\t {1}\t Iy mini:\t {2}\n".format(datetime.datetime.now(), Ix_mini, Iy_mini)) 
        
        #  
        #run KHCe
        utl.globalTrace("{0}\t Run KHCe\n".format(datetime.datetime.now())) 
        level = khc.KHCe(self.inputDataFileName, self._variable1ValuesFrequency, self._variable2ValuesFrequency, const.Imax, const.labelPostOpt, variable1TrueValuesClusters, variable2TrueValuesClusters, self.outputCoclusteringFile)
        
        pathF = os.path.dirname(os.path.abspath(self.inputDataFileName))+ '/' + const.labelPostOpt + '/'
        destination_path = pathF + const.labelPostOpt + '.khc'
        source_path = pathFiles + const.labelPostOpt + '.khc'
        utl.move_file(destination_path,source_path)
        
        utl.globalTrace("{0}\t End KHCe \t level: \t {1}\n".format(datetime.datetime.now(), level)) 
        utl.globalTrace("{0}\t End post optimization coclustering step \n".format(datetime.datetime.now())) 

          
    
       