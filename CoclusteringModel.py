# -*- coding: utf-8 -*-
"""
Created on Tue May 30 17:19:49 2017

@author: HZTT9795
"""
import khiopsStats as KS
import math
import numpy as np
import time

def getValueFreqOnCocluster(valueFreqencies, cocluster):
    try:
        f=valueFreqencies[cocluster]
    except KeyError:
        f=0
    return f

class ModelParser:
    def __init__(self, inputCoclusteringFileName):
        self.inputCoclusteringFileName = inputCoclusteringFileName
    
    def getN(self):
        khCoclustFile = open(self.inputCoclusteringFileName,'r')
        fileBlocks = khCoclustFile.read().split('\n\n')
        compositiosBlocks = []
        for item in fileBlocks:
            if 'Instances\t' in item:
                compositiosBlocks.append(item)
        khCoclustFile.close()
        return int(float(compositiosBlocks[0].split('\n')[1].split('\t')[1]))
        
    def getBlocks(self):
        blocks = self.__getCompositionBlocks() # get a blocks[0] - composition string of X and blocks[1] - composition string of Y 
        
        xBlock = blocks[0].split('\n')[1:]
        yBlock = blocks[1].split('\n')[1:]
        
        arrblockX = []
        XClusterFreq={}
        XValClust={}
        XValFreq={}

        XClustIndeces={}
        cluster_count = 0  
        list_clusters=[]
        
        for b in xBlock[1:]:
            fline=b.split('\t')[:3]
            arrblockX.append(fline)
            
            if fline[0] not in XClusterFreq:
                XClusterFreq[fline[0]]=0
            XClusterFreq[fline[0]]+=int(float(fline[2]))
            
            XValClust[fline[1]]=fline[0]
            XValFreq[fline[1]]=int(float(fline[2]))
            
            #to indice the order of clusters
            if fline[0] not in list_clusters:
                list_clusters.append(fline[0])
                XClustIndeces[cluster_count] = fline[0]
                cluster_count +=1
            
        arrblockY = []
        YClusterFreq={}
        YValClust={}
        YValFreq={}

        YClustIndeces={}
        cluster_count = 0  
        list_clusters=[]        
        
        for b in yBlock[1:]:
            fline=b.split('\t')[:3]
            arrblockY.append(fline)
            
            if fline[0] not in YClusterFreq:
                YClusterFreq[fline[0]]=0
            YClusterFreq[fline[0]]+=int(float(fline[2]))
            
            YValClust[fline[1]]=fline[0]
            YValFreq[fline[1]]=int(float(fline[2]))
            
            #to indice the order of clusters
            if fline[0] not in list_clusters:
                list_clusters.append(fline[0])
                YClustIndeces[cluster_count] = fline[0]
                cluster_count +=1
        
        XClustVals={}
        for k in XValClust.keys():
            if XValClust[k] not in XClustVals:
                XClustVals[XValClust[k]]=[]
            XClustVals[XValClust[k]].append(k)
                
        YClustVals={}
        for k in YValClust.keys():
            if YValClust[k] not in YClustVals:
                YClustVals[YValClust[k]]=[]
            YClustVals[YValClust[k]].append(k)
                        
        
        return XClusterFreq, YClusterFreq, XValClust, YValClust, XValFreq, YValFreq, XClustVals, YClustVals, XClustIndeces, YClustIndeces
    
    def __getCompositionBlocks(self):
        """
        get a composition blocks in the following format:
        compositiosBlocks[0] - composition string of X 
        and compositiosBlocks[1] - composition string of Y 
        """
        khCoclustFile = open(self.inputCoclusteringFileName,'r')
        
        fileBlocks = khCoclustFile.read().split('\n\n')
        
        compositiosBlocks = []
        for item in fileBlocks:
            if 'Composition\t' in item:
                compositiosBlocks.append(item)
        khCoclustFile.close()
        return compositiosBlocks
    
    def getCells(self):
        """
        get cells in the following format:
        cells[0] - cells
        """
        khCoclustFile = open(self.inputCoclusteringFileName,'r')
        fileBlocks = khCoclustFile.read().split('\n\n')
        cells = []
        for item in fileBlocks:
            if 'Cells\n' in item:
                cells.append(item)
        khCoclustFile.close()
                
        cellsBlock = cells[0].split('\n')[1:]
        
#        pdcell = []
#        print('start read cells')
#        print(cellsBlock)
        XYFreq={}
        for cc in cellsBlock[1:]:
            fline=cc.split('\t')
            if not fline[0]:
                break
#            pdcell.append(fline)
#            if fline[0] not in XYFreq:
#                XYFreq[fline[0]]={}
            XYFreq[fline[0],fline[1]]=int(fline[2])
        
        return XYFreq

class CoclusteringModel:
    """
    CX - cluster, value, freq on X
    CY - cluster, value, freq on Y
    N - number of instances
    CXY - cells: X cluster Y cluster Freq
    """
    def __init__(self, inputClusteringFileName):
        if inputClusteringFileName:
            mParser = ModelParser(inputClusteringFileName)
            self.XClusterFreq, self.YClusterFreq, self.XValClust, self.YValClust, self.XValFreq, self.YValFreq, self.XClustVals, self.YClustVals, self.XClustIndeces, self.YClustIndeces = mParser.getBlocks()
            self.I=len(self.XClusterFreq)
            self.J=len(self.YClusterFreq)
            self.N = mParser.getN()
            
            self.coclusterFreq = mParser.getCells()
#            for xCluster in self.getClusters('on_x'):
#                for yCluster in self.getClusters('on_y'):
#                    if not xCluster in self.coclusterFreq:
#                        self.coclusterFreq[xCluster]={}
#                        self.coclusterFreq[xCluster][yCluster]=0
#                    if not yCluster in self.coclusterFreq[xCluster]:
#                        self.coclusterFreq[xCluster][yCluster]=0
        
    
    def setNullModel(self):
        self.XClusterFreq={}
        self.YClusterFreq={}
        self.XClusterFreq['CX']=self.N
        self.YClusterFreq['CY']=self.N
        for k in self.XValClust.keys():
            self.XValClust[k]='CX'
        for k in self.YValClust.keys():
            self.YValClust[k]='CY'
        l=[]
        for k in self.XClustVals.keys():
            l+=self.XClustVals[k]
        self.XClustVals={}
        self.XClustVals['CX']=l
        l=[]
        for k in self.YClustVals.keys():
            l+=self.YClustVals[k]
        self.YClustVals={}
        self.YClustVals['CY']=l
                       
        self.I=1
        self.J=1
        
#        self.coclusterFreq={}
#        self.coclusterFreq['CX']={}
        self.coclusterFreq['CX','CY']=self.N     
               
        assert(self.checkModel('on_x'))
        assert(self.checkModel('on_y'))
    
    def setNullModelFromDataFile(self, dataFileName):
        f=open(dataFileName)
        lines=f.readlines()
        f.close()
        # Parsing de la ligne d'entet pour trouver les index de X, Y, et optionnellement Freq
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
            print("error in data file " + f + " (" + headerLine + ")")
            return
        
        # Parsing du fichier hors ligne d'entete
        self.XValFreq={}
        self.YValFreq={}
        self.N = 0
        for line in lines[1:] :
            sline=line[:-1].split('\t')
            # L'effectif vaut 1 par defaut
            frequency = 1
            if indexFreq != -1 and len(sline) > indexFreq:
                frequency = int(sline[indexFreq])
            self.N+=frequency
            
            if sline[indexX] not in self.XValFreq:
                self.XValFreq[sline[indexX]]=frequency
            else:
                self.XValFreq[sline[indexX]]+=frequency
                           
            if sline[indexY] not in self.YValFreq:
                self.YValFreq[sline[indexY]]=frequency
            else:
                self.YValFreq[sline[indexY]]+=frequency        
        
        self.XClusterFreq={}
        self.YClusterFreq={}
        self.XClusterFreq['CX']=self.N
        self.YClusterFreq['CY']=self.N
        self.XValClust={}
        self.YValClust={}
        for k in self.XValFreq.keys():
            self.XValClust[k]='CX'
        for k in self.YValFreq.keys():
            self.YValClust[k]='CY'
        self.XClustVals={}
        l=list(self.XValFreq.keys())
        self.XClustVals['CX']=l
        
        
        self.YClustVals={}
        l=list(self.YValFreq.keys())
        self.YClustVals['CY']=l
        
        self.I=1
        self.J=1
        
        self.coclusterFreq={}
#        self.coclusterFreq['CX']={}
        self.coclusterFreq['CX','CY']=self.N     
               
        assert(self.checkModel('on_x'))
        assert(self.checkModel('on_y'))
        
        
        
        
    def checkModel(self, option):
        #returns true of false
        isGoodModel = True
        if option=='on_x':
            if sum(self.XClusterFreq.values())!=self.N:
                print('error on: freq on X clust')
                return False
                
            if sum(self.XValFreq.values())!=self.N:
                print('error on: freq on X val')
                return False
        
        if option=='on_y':
            if sum(self.YClusterFreq.values())!=self.N:
                print('error on: freq on Y clust')
                return False
                
            if sum(self.YValFreq.values())!=self.N:
                print('error on: freq on X val')
                return False
        
        
        sumCoclusters = 0
        sumCoclusters=sum(self.coclusterFreq.values())
        
        isGoodModel = all(freq >= 0 for freq in self.coclusterFreq.values())
        if not isGoodModel:
            print('error on: cells with freq < 0')
            return False
            
        if sumCoclusters!=self.N:
            print('error on: cells with freq')
            return False
            
        return isGoodModel
            
    def delValue(self,value, option):
        oldCluster = self.getCluster(value, option)
        if option=='on_x':
            self.XValClust[value]=np.nan
            l=self.XClustVals[oldCluster]
            l.remove(value)
            if not l:
                del self.XClustVals[oldCluster]
            else:
                self.XClustVals[oldCluster]=l
            self.XClustVals[np.nan]=[value]
                           
        if option=='on_y':
            self.YValClust[value]=np.nan
            l=self.YClustVals[oldCluster]
            l.remove(value)
            if not l:
                del self.YClustVals[oldCluster]
            else:
                self.YClustVals[oldCluster]=l
            self.YClustVals[np.nan]=[value]
                           
    def addValue(self, value, cluster, option):
        if option=='on_x':
            oldCluster = self.getCluster(value, option)
            l=self.XClustVals[oldCluster]
            l.remove(value)
            if not l:
                del self.XClustVals[oldCluster]
            else:
                self.XClustVals[oldCluster]=l
                                   
            if not cluster in self.XClustVals:
                self.XClustVals[cluster]=value
            else:
                self.XClustVals[cluster].append(value)
            
            self.XValClust[value]=cluster
        if option=='on_y':
            oldCluster = self.getCluster(value, option)
            l=self.YClustVals[oldCluster]
            l.remove(value)
            if not l:
                del self.YClustVals[oldCluster]
            else:
                self.YClustVals[oldCluster]=l
                                   
            if not cluster in self.YClustVals:
                self.YClustVals[cluster]=value
            else:
                self.YClustVals[cluster].append(value)
            
            self.YValClust[value]=cluster
    
    def delFreqFromCoCluster(self, cx,cy,freq):
        self.coclusterFreq[cx,cy]-=freq
        self.XClusterFreq[cx]-=freq
        self.YClusterFreq[cy]-=freq
    
    def addFreqToCoCluster(self,cx,cy,freq):
        self.coclusterFreq[cx,cy]+=freq
        self.XClusterFreq[cx]+=freq
        self.YClusterFreq[cy]+=freq
                    
    def getValueFreq(self, value, option):
        if option=='on_x':
            return self.XValFreq[value]
        elif option=='on_y':
            return self.YValFreq[value]
    
    def mergeClusters(self, cluster_source, cluster_target, option, isPrint=False):
        if isPrint:
            print('original:\n{0}'.format(self.coclusterFreq))
        cluster_new = cluster_source + cluster_target
        if option=='on_x':
            self.XClusterFreq[cluster_new] = self.getFreqCluster(cluster_source,option) + self.getFreqCluster(cluster_target,option)
            del self.XClusterFreq[cluster_source], self.XClusterFreq[cluster_target]
            
            for k in self.XValClust.keys():
                if self.XValClust[k]==cluster_source:
                    self.XValClust[k]=cluster_new
                if self.XValClust[k]==cluster_target:
                    self.XValClust[k]=cluster_new
            
            self.XClustVals[cluster_new]=self.XClustVals[cluster_source]+self.XClustVals[cluster_target]
            del self.XClustVals[cluster_source], self.XClustVals[cluster_target]
            
            for cy in self.getClusters('on_y'):
                freq_merged = self.getFreqCocluster(cluster_source,cy,option)+self.getFreqCocluster(cluster_target,cy,option)
#                if cluster_new not in self.coclusterFreq:
#                    self.coclusterFreq[cluster_new]={}
                self.coclusterFreq[cluster_new,cy]=freq_merged
            del self.coclusterFreq[cluster_source,cluster_target], self.coclusterFreq[cluster_target, cluster_source]
            
            self.I-=1
            
        if option=='on_y':
            self.YClusterFreq[cluster_new] = self.getFreqCluster(cluster_source,option) + self.getFreqCluster(cluster_target,option)
            del self.YClusterFreq[cluster_source], self.YClusterFreq[cluster_target]
            
            for k in self.YValClust.keys():
                if self.YValClust[k]==cluster_source:
                    self.YValClust[k]=cluster_new
                if self.YValClust[k]==cluster_target:
                    self.YValClust[k]=cluster_new
            
            self.YClustVals[cluster_new]=self.YClustVals[cluster_source]+self.YClustVals[cluster_target]
            del self.YClustVals[cluster_source], self.YClustVals[cluster_target]
            
            #CXY -> add new cells and delete cells
            for cx in self.getClusters('on_x'):
                freq_merged = self.getFreqCocluster(cluster_source,cx,option)+self.getFreqCocluster(cluster_target,cx,option)
                self.coclusterFreq[cx,cluster_new]=freq_merged
            
            for k in self.coclusterFreq.keys():
                del self.coclusterFreq[k,cluster_source], self.coclusterFreq[k,cluster_target]
        
            self.J-=1
            
        if isPrint:
            print('cluster source='+str(cluster_source))
            print('cluster target='+str(cluster_target))
            print('cluster_new='+str(cluster_new))
            print('merged:\n{0}'.format(self.coclusterFreq))
        
    def getCluster(self, value, option):
        if option=='on_x':
            return  self.XValClust[value]
        elif option=='on_y':
            return self.YValClust[value]
    
    def getValues(self, cluster, option):
        if option=='on_x':
            return self.XClustVals[cluster]
        elif option=='on_y':
            return self.YClustVals[cluster]
    
    def getClusters(self, option):
        if option=='on_x':
            return self.XClustVals.keys()
        if option=='on_y':
            return self.YClustVals.keys()
    

    def getFreqValuesInCluster(self, cluster, option):
        #nic
        #number of values in a cluster
        if option=='on_x':
            return len(self.XClustVals[cluster])
        elif option=='on_y':
            return len(self.YClustVals[cluster])
    
    def getFreqCluster(self, cluster, option):
        #mic 
        #frequency of a cluster
        if option=='on_x':
            return self.XClusterFreq[cluster]
        if option=='on_y':
            return self.YClusterFreq[cluster]
        
    def getFreqCocluster(self, cx, cy, option='on_x'):
        if option=='on_y':
            cx,cy=cy,cx
        try:
            return self.coclusterFreq[cx,cy]
        except KeyError:
            self.coclusterFreq[cx,cy]=0
            return self.coclusterFreq[cx,cy]
    
    def computeClusterMergeClusterDelta(self, cluster_source, cluster_target, option, isPrint=False):
        """
        compute delta of merging cluster
            cluster_source - cluster that merges 1
            cluster_target - cluster that merges 2
            option: 'on_x', 'on_y'
            isPrint(optional, by default=False): True or False
        """
        n1,n2=0,0
        delta_cluster = 0
        clusters_concerned = [cluster_source, cluster_target]
        
#        time_stamp=time.time()
        
        if option=='on_x':
            merged_mic = 0
            for cluster in clusters_concerned:
                mic = self.getFreqCluster(cluster, option)
                nic = self.getFreqValuesInCluster(cluster, option)
                n1+=nic
                merged_mic+=mic
                delta_cluster-=KS.logbinomial(mic+nic-1,nic-1)
            delta_cluster+=KS.logbinomial(merged_mic+n1-1,n1-1)
            
            for cy in self.getClusters('on_y'):
                sum_freq_cocluster = 0
                for cx in clusters_concerned:
                    freq_cocluster = self.getFreqCocluster(cx, cy, option)
#                    print('{0}:{1}'.format(freq_cocluster,type(freq_cocluster)))
                    delta_cluster+=KS.logfactorial(freq_cocluster) # ( - & - => + )
                    sum_freq_cocluster+=freq_cocluster
                delta_cluster-=KS.logfactorial(sum_freq_cocluster) # ( + & - => - )
                
            sum_freq_cluster = 0
            for cluster in clusters_concerned:
                freq_cluster = self.getFreqCluster(cluster, option)
                sum_freq_cluster+=freq_cluster
                delta_cluster-=KS.logfactorial(freq_cluster)
            
            delta_cluster+=KS.logfactorial(sum_freq_cluster)
        
#               
            
        if option=='on_y':
            merged_mic = 0
            for cluster in clusters_concerned:
                mjc = self.getFreqCluster(cluster, 'on_y')
                njc = self.getFreqValuesInCluster(cluster, 'on_y')
                n2+=njc
                merged_mic+=mjc
                delta_cluster-=KS.logbinomial(mjc+njc-1,njc-1)
            delta_cluster+=KS.logbinomial(merged_mic+n2-1,n2-1)
            
            for cx in self.getClusters('on_x'):
                sum_freq_cocluster = 0
                for cy in clusters_concerned:
                    freq_cocluster = self.getFreqCocluster(cy, cx, option)
                    delta_cluster+=KS.logfactorial(freq_cocluster) # ( - & - => + )
                    sum_freq_cocluster+=freq_cocluster
                delta_cluster-=KS.logfactorial(sum_freq_cocluster) # ( + & - => - )
                
            sum_freq_cluster = 0
            for cluster in clusters_concerned:
                freq_cluster = self.getFreqCluster(cluster, option)
                sum_freq_cluster+=freq_cluster
                delta_cluster-=KS.logfactorial(freq_cluster)
            
            delta_cluster+=KS.logfactorial(sum_freq_cluster)
        
        
        if isPrint:
            print('concerned cluster:\t'.format(clusters_concerned))
            for cluster in clusters_concerned:
                mic = self.getFreqCluster(cluster, option)
                nic = self.getFreqValuesInCluster(cluster, option)
                n1+=nic
                merged_mic+=mic
                print('freq on cluster {0}:\t{1}:'.format(cluster, mic))
                print('freq values in cluster {0}:\t{1}'.format(cluster,nic))
                print('compute delta cluster (-original):\t{0}'.format(-KS.logbinomial(mic+nic-1,nic-1)))
            print('merged freq on cluster:'+str(merged_mic))
            print('freq values in cluster {0}:\t{1}'.format(cluster,n1))
            print('compute delta cluster (+merged):\t{0}'.format(KS.logbinomial(merged_mic+n1-1,n1-1)))
            
            
            for cy in self.getClusters('on_y'):
                sum_freq_cocluster = 0
                for cx in clusters_concerned:
                    freq_cocluster = self.getFreqCocluster(cx, cy, option)
                    print('{0} / {1} :\t {2}'.format(cx,cy,freq_cocluster))
                    delta_cluster+=KS.logfactorial(freq_cocluster) # ( - & - => + )
                    print('compute delta cluster (-original):\t{0}'.format(KS.logfactorial(freq_cocluster)))
                    sum_freq_cocluster+=freq_cocluster
                print('freq coclusters on x (2 concerned):\t'+str(sum_freq_cluster))
                print('compute delta cluster (+merged):\t{0}'.format(KS.logfactorial(sum_freq_cocluster)))# ( + & - => - )
            
            
            sum_freq_cluster = 0
            for cluster in clusters_concerned:
                freq_cluster = self.getFreqCluster(cluster, option)
                print('{0} :\t {1}'.format(cluster,freq_cocluster))
                sum_freq_cluster+=freq_cluster
                print('compute delta cluster (-original):\t'+str(KS.logfactorial(freq_cluster)))
            
            print('merged freq: \t'+str(sum_freq_cluster))
            print('compute delta cluster (+merged):\t{0}'.format(KS.logfactorial(sum_freq_cluster)))
            
        return delta_cluster
            
            
     
    def computeClusterMergeStructureDelta(self, option, isPrint=False):
        clustersX = self.getClusters('on_x')
        clustersY = self.getClusters('on_y')
        k1,k2=len(clustersX),len(clustersY)
        n1,n2=0,0
        delta_structured = 0
        if option=='on_x':
            for cluster in clustersX:
                nic = self.getFreqValuesInCluster(cluster, option)
                n1+=nic
            delta_structured+=KS.setDicoLnBell(n1)[(k1-1)]
            delta_structured-=KS.setDicoLnBell(n1)[k1]
            delta_structured+=KS.logbinomial(self.N+(k1-1)*k2-1,(k1-1)*k2-1)
            delta_structured-=KS.logbinomial(self.N+k1*k2-1,k1*k2-1)
            
        if option=='on_y':
            for cluster in clustersY:
                njc = self.getFreqValuesInCluster(cluster, option)
                n2+=njc
            delta_structured+=KS.setDicoLnBell(n2)[(k2-1)]
            delta_structured-=KS.setDicoLnBell(n2)[k2]
            delta_structured+=KS.logbinomial(self.N+k1*(k2-1)-1,k1*(k2-1)-1)
            delta_structured-=KS.logbinomial(self.N+k1*k2-1,k1*k2-1)
        
        if isPrint:
            k1,k2=len(clustersX),len(clustersY)
            n1,n2=0,0
            print('Clusters on X: {0}, Cluster on Y {1}'.format(k1,k2))
            if option=='on_x':
                for cluster in clustersX:
                    nic = self.getFreqValuesInCluster(cluster, option)
                    n1+=nic
                print('Delta Structured merged +lnBell(n1)[k-1]'.format(KS.setDicoLnBell(n1)[(k1-1)]))
                print('Delta Structured original -lnBell(n1)[k]'.format(KS.setDicoLnBell(n1)[(k1)]))
                print('Delta Structured merged +logbinomial(N+(k1-1)*k2-1,(k1-1)*k2-1):'.format(KS.logbinomial(self.N+(k1-1)*k2-1,(k1-1)*k2-1)))
                print('Delta Structured original -logbinomial(N+k1*k2-1,k1*k2-1):'.format(KS.logbinomial(self.N+k1*k2-1,k1*k2-1)))

            if option=='on_y':
                for cluster in clustersY:
                    njc = self.getFreqValuesInCluster(cluster, option)
                    n2+=njc
                    
                print('Delta Structured merged +lnBell(n1)[k-1]'.format(KS.setDicoLnBell(n2)[(k2-1)]))
                print('Delta Structured original -lnBell(n1)[k]'.format(KS.setDicoLnBell(n2)[k2]))
                print('Delta Structured merged +logbinomial(N+k1*(k2-1)-1,k1*(k2-1)-1):'.format(KS.logbinomial(self.N+k1*(k2-1)-1,k1*(k2-1)-1)))
                print('Delta Structured original -logbinomial(N+k1*k2-1,k1*k2-1):'.format(KS.logbinomial(self.N+k1*k2-1,k1*k2-1)))
                
        return delta_structured
        
    
    def computeValueChangeDelta(self,value,f_value,cluster,isAdd, option, isPrint=False):
        """
        compute Delta
        with:
            value: value that makes change in the mode
            f_value: frequencies of the value on the coclusters
            cluster: cluster to be modified
            option: 'on_x' or 'on_y'
            isAdd: True(plus value) or False(minus value)
            isPrint (optional, by default=False): True or False
        """
        
        #prior
        mic_original = self.getFreqCluster(cluster, option)
        nic_original = self.getFreqValuesInCluster(cluster, option)
        if isAdd:
                #adding a value
                mic=mic_original + self.getValueFreq(value, option)
                nic=nic_original + 1
        else:
            #deleating value
            mic=mic_original - self.getValueFreq(value, option)
            nic=nic_original - 1
        
        
        delta_prior= KS.logbinomial(mic+nic-1,nic-1) - KS.logbinomial(mic_original+nic_original-1,nic_original-1)
        
        ll=0
        ll_original = 0  
        ll += KS.logfactorial(mic)
        ll_original +=KS.logfactorial(mic_original)
           
        if option=='on_x':    
            #likelihood
            clustersY = self.getClusters('on_y')
            for cy in clustersY:
                freq_cocluster_original = self.getFreqCocluster(cluster, cy)
                if isAdd: 
                    freq_cocluster = freq_cocluster_original + getValueFreqOnCocluster(f_value, cy)
                else:
                    freq_cocluster = freq_cocluster_original - getValueFreqOnCocluster(f_value, cy)
                ll-=KS.logfactorial(freq_cocluster)
                ll_original -= KS.logfactorial(freq_cocluster_original)
            
        if option=='on_y':    
            #likelihood
            clustersX = self.getClusters('on_x')
            for cx in clustersX:
                freq_cocluster_original = self.getFreqCocluster(cluster, cx, option)
                if isAdd: 
                    freq_cocluster = freq_cocluster_original + getValueFreqOnCocluster(f_value, cx)
                else:
                    freq_cocluster = freq_cocluster_original - getValueFreqOnCocluster(f_value, cx)
                ll-=KS.logfactorial(freq_cocluster)
                ll_original -= KS.logfactorial(freq_cocluster_original)
                
        delta_ll=ll - ll_original     
            
        delta = delta_prior + delta_ll

        if isPrint:
            mic_original = self.getFreqCluster(cluster, option)
            nic_original = self.getFreqValuesInCluster(cluster, option)
            if isAdd:
                    #adding a value
                    mic=self.getFreqCluster(cluster, option) + self.getValueFreq(value, option)
                    nic=self.getFreqValuesInCluster(cluster, option) +1
            else:
                #deleating value
                mic=self.getFreqCluster(cluster, option) - self.getValueFreq(value, option)
                nic=self.getFreqValuesInCluster(cluster, option) - 1
            print('Freq original on cluster {0}={1} and changed ={2}'.format(cluster,mic_original,mic))
            print('Values original on cluster {0}={1} and changed ={2}'.format(cluster,nic_original,nic))
            delta_prior_changed = KS.logbinomial(mic+nic-1,nic-1)
            
            
            delta_prior_oritinal = KS.logbinomial(mic_original+nic_original-1,nic_original-1)
            print('delta prior original: '+str(delta_prior_oritinal))
            print('delta prior changed: '+str(delta_prior_changed))
            print('delta prior: '+str(delta_prior_oritinal-delta_prior_changed))
            
            #likelihood 
            if option=='on_x':
                f=[]
                f_original=[]
                clustersY = self.getClusters('on_y')
                for cy in clustersY:
                    freq_cocluster_original = self.getFreqCocluster(cluster, cy)
                    if isAdd: 
                        freq_cocluster = freq_cocluster_original + getValueFreqOnCocluster(f_value, cy)
                    else:
                        freq_cocluster = freq_cocluster_original - getValueFreqOnCocluster(f_value, cy) 
                    ll=-KS.logfactorial(freq_cocluster)
                    ll_original = -KS.logfactorial(freq_cocluster_original)
                    f_original.append(freq_cocluster_original)
                    f.append(freq_cocluster)
                    print('freq: '+str(freq_cocluster) + ' ll original : '+str(ll_original) + ' ll: '+str(ll))
                    print('delta ll cocluster = '+str(ll_original-ll))
            
            if option=='on_y':
                f=[]
                f_original=[]
                clustersX = self.getClusters('on_x')
                for cx in clustersX:
                    freq_cocluster_original = self.getFreqCocluster(cluster, cx, option)
                    if isAdd: 
                        freq_cocluster = freq_cocluster_original + getValueFreqOnCocluster(f_value, cx)
                    else:
                        freq_cocluster = freq_cocluster_original - getValueFreqOnCocluster(f_value, cx) 
                    ll=-KS.logfactorial(freq_cocluster)
                    ll_original = -KS.logfactorial(freq_cocluster_original)
                    f_original.append(freq_cocluster_original)
                    f.append(freq_cocluster)
                    print('freq: '+str(freq_cocluster) + ' ll original : '+str(ll_original) + ' ll: '+str(ll))
                    print('delta ll cocluster = '+str(ll_original-ll))
                
            print('Original freq on cocluster of the cluster {0}:{1}'.format(cluster,f_original))
            print('Freq on cocluster of the cluster {0}:{1}'.format(cluster,f))
            
            freq_cluster_original = self.getFreqCluster(cluster, option)
            if isAdd:
                freq_cluster = freq_cluster_original + self.getValueFreq(value, option)
            else:
                freq_cluster = freq_cluster_original - self.getValueFreq(value, option)
            
            ll = KS.logfactorial(freq_cluster)
            ll_original =KS.logfactorial(freq_cluster_original)
            print('Original Freq on cluster {0}:{1}'.format(cluster,freq_cluster_original))
            print('Freq on cluster {0}:{1}'.format(cluster,freq_cluster))
            print('ll original : '+str(ll_original) + ' ll: '+str(ll))
            print('Delta ll cluster: '+str(ll_original-ll))
        
        return delta
    
    def computePrior(self, showData=False, showCriterion=False):
        clustersX = self.getClusters('on_x')
        clustersY = self.getClusters('on_y')
        k1,k2,m=len(clustersX),len(clustersY),self.N
        n1,n2=0,0
        prior=math.log(2)+KS.logbinomial(3,2)
        for cluster in clustersX:
            mic = self.getFreqCluster(cluster, 'on_x')
            nic = self.getFreqValuesInCluster(cluster, 'on_x')
            n1+=nic
            prior+=KS.logbinomial(mic+nic-1,nic-1)
        
        for cluster in clustersY:
            mjc = self.getFreqCluster(cluster, 'on_y')
            njc = self.getFreqValuesInCluster(cluster, 'on_y')
            n2+=njc
            prior+=KS.logbinomial(mjc+njc-1,njc-1)
        
        prior+=math.log(n1)
        prior+=math.log(n2)
        prior+=KS.setDicoLnBell(n1)[k1]
        prior+=KS.setDicoLnBell(n2)[k2]
        prior+=KS.logbinomial(m+k1*k2-1,k1*k2-1)
        # Affichage de la structure du coclustering
        if showData:
            print("Instances: "+str(self.N))
            print("Partition X: "+ str(n1) + ", " + str(k1))
            for i, cluster in enumerate(sorted(self.getClusters('on_x'))):
                print('\tPartX {0} ({1}:{2})'.format(i,self.getFreqValuesInCluster(cluster, 'on_x'), self.getValues(cluster, 'on_x')))
            
            print("Partition Y: "+ str(n2) + ", " + str(k2))
            for i, cluster in enumerate(sorted(self.getClusters('on_y'))):
                print('\tPartY {0} ({1}:{2})'.format(i,self.getFreqValuesInCluster(cluster, 'on_y'), self.getValues(cluster, 'on_y')))
                
        if showCriterion:
            print("prior:\t"+str(prior))
            print("prior vars:\t"+str(math.log(2)+KS.logbinomial(3,2)))
            print("prior partition X:\t"+str(math.log(n1)+KS.setDicoLnBell(n1)[k1]))
            print("prior partition Y:\t"+str(math.log(n2)+KS.setDicoLnBell(n2)[k2]))
            print("prior data grid multinomial:\t"+str(KS.logbinomial(m+k1*k2-1,k1*k2-1)))
            for cluster in sorted(self.getClusters('on_x')):
                mic = self.getFreqCluster(cluster, 'on_x')
                nic = self.getFreqValuesInCluster(cluster, 'on_x')
                n1+=nic
                pxprior=KS.logbinomial(mic+nic-1,nic-1)
                print("prior part X (" + str(mic) + ", " + str(nic) + "):\t"+str(pxprior))
            for cluster in sorted(self.getClusters('on_y')):
                mjc = self.getFreqCluster(cluster, 'on_y')
                njc = self.getFreqValuesInCluster(cluster, 'on_y')
                n2+=njc
                pyprior=KS.logbinomial(mjc+njc-1,njc-1)
                print("prior part Y (" + str(mjc) + ", " + str(njc) + "):\t"+str(pyprior))
        return prior
    
    def computeLikelihood(self, showData=False, showCriterion=False):
        likelihood=KS.logfactorial(self.N)
        clustersX = self.getClusters('on_x')
        clustersY = self.getClusters('on_y')
        valuesX = self.XValFreq.keys()
        valuesY = self.YValFreq.keys()
        
        
        for cx in clustersX:
            for cy in clustersY:
                try:
                    likelihood-=KS.logfactorial(self.getFreqCocluster(cx, cy))
                except : pass
         
        for cluster in clustersX:
            likelihood+=KS.logfactorial(self.getFreqCluster(cluster, 'on_x'))
    
        for cluster in clustersY:
            likelihood+=KS.logfactorial(self.getFreqCluster(cluster, 'on_y'))
        
        for valX in valuesX:
            likelihood-=KS.logfactorial(self.getValueFreq(valX, 'on_x'))
        for valY in valuesY:
            likelihood-=KS.logfactorial(self.getValueFreq(valY, 'on_y'))
        # Affichage de la structure du coclustering
        if showData:
            print("Cells: "+str(len(clustersX)*len(clustersY)))
        if showCriterion:
            print("likelihood:\t"+str(likelihood))
            ll=KS.logfactorial(self.N)
            print("ll global (" + str(self.N) + "):\t"+str(ll))
            llAll = 0
            freq_ll_cell = np.zeros((len(clustersX), len(clustersY)))
            ll_cell = np.zeros((len(clustersX), len(clustersY)))-np.NaN
            for i,clusterX in enumerate(sorted(clustersX)):
                for j,clusterY in enumerate(sorted(clustersY)):
                    try:
                        ll=-KS.logfactorial(self.getFreqCocluster(clusterX, clusterY))
                        llAll += ll
                        #print('{0}_____{1}'.format(px.getId(),py.getId()))
                        print("ll cell (" + str(i+1) + ", " + str(j+1) + " " + str(self.getFreqCocluster(clusterX, clusterY)) + "):\t"+str(ll))
                        freq_ll_cell[i, j] = self.getFreqCocluster(clusterX, clusterY)
                        ll_cell[i, j] = ll
                    except : pass
            print('Freq on cells:')
            print(*freq_ll_cell.astype(int), sep=' ')
            print("all cells:\t" + str(llAll))
            llAll = 0
            freq_X_part = np.zeros(len(clustersX))
            freq_Y_part = np.zeros(len(clustersY))
            
            for i, cx in enumerate(sorted(clustersX)):
                ll=KS.logfactorial(self.getFreqCluster(cx, 'on_x'))
                llAll += ll
                print("ll part X (" + str(i+1) + ":" + str(self.getFreqCluster(cx, 'on_x')) + "):\t"+str(ll))
                freq_X_part[i] = self.getFreqCluster(cx, 'on_x')
            print("all part X:\t" + str(llAll))
            llAll = 0
            for j, cy in enumerate(sorted(clustersY)):
                ll=KS.logfactorial(self.getFreqCluster(cy, 'on_y'))
                llAll += ll
                print("ll part Y (" + str(j+1) + ": " + str(self.getFreqCluster(cy, 'on_y')) + "):\t"+str(ll))
                freq_Y_part[j] = self.getFreqCluster(cy, 'on_y')
            print("all part Y:\t" + str(llAll))
            print('X part freq')
            print(*freq_X_part.astype(int), sep=' ')
            print('Y part freq')
            print(*freq_Y_part.astype(int), sep=' ')
            
            llAll = 0
            for valX in self.XValFreq.keys():
                ll=-KS.logfactorial(self.getValueFreq(valX, 'on_x'))
                llAll += ll
                print("ll value X (" + str(valX) + "): freq= "+str(self.getValueFreq(valX, 'on_x')) +' = ' + str(ll))
            print("all values X: " + str(llAll))
            llAll = 0
            for valY in self.YValFreq.keys() :
                ll=-KS.logfactorial(self.getValueFreq(valY, 'on_y'))
                llAll += ll
                print("ll value Y (" + str(valY) + "): freq= "+str(self.getValueFreq(valY, 'on_y')) +' = ' +str(ll))
            print("all values Y: " + str(llAll))            
        return likelihood
    
    def computeCriterion(self,isPrint = False):
        return self.computePrior(isPrint, isPrint) + self.computeLikelihood(isPrint, isPrint)


def testModel():
    directory = 'C:/Users/hztt9795/Documents/python/wk/ScaledCoclustering_v3/test/'
    modelFile=directory+'TClGeneratedDataGrad_N1000000_V20000_nr1.khc'
    data = directory+'GeneratedDataGrad_N1000000_V20000_nr1.txt'
    
    c1=CoclusteringModel('')
    c1.setNullModelFromDataFile(data)
    print('null model:'+str(c1.computeCriterion(False)))
    print('============================================================================')
    c2=CoclusteringModel(modelFile)
    print('model:'+str(c2.computeCriterion(False)))
    
    print('level:'+str(1-(c2.computeCriterion(False)/c1.computeCriterion(False) )))
    
    
    
    modelFile=directory+'valChPostOptGeneratedDataGrad_nr1_p64.khc'
    c3=CoclusteringModel(modelFile)
    print('model VC:'+str(c3.computeCriterion(False)))
    
    print('level VC:'+str(1-(c3.computeCriterion(False)/c1.computeCriterion(False) )))
    
#    return c2

#testModel()