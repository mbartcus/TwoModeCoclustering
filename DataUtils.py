# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 11:36:23 2017

@author: HZTT9795
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 09:44:12 2017

@author: HZTT9795
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from math import sqrt, fabs
#from random import randint
import FileInfos as finfo
import utils as utl
import random
import math
import time
import operator
import pandas as pd

def writeDataToFile(D, DF):
    """
        write data to the dataFileName
    """
    dataFileName = DF.pathToFile + DF.dataFileInfo
    D.to_csv(dataFileName, index=False, sep='\t')


def generateData(option = 'on_diag', nrValues=100,totalArcNumber=2000, shape=1, isPlot=False, fig_name='', density_parameter=1):
    cMatrix={}
    if option=='on_diag':
        cMatrix = fillDataTest(cMatrix)
    elif option =='on_grad':
        cMatrix, xyValuePairs = fillGradiantDataTest(cMatrix, nrValues,totalArcNumber, shape, density_parameter)
    
#    print(isPlot)
    if isPlot:
        cM=np.zeros((nrValues,nrValues))
        for k in cMatrix.keys():
            x=k[0]
            y=k[1]
            cM[x,y] += cMatrix[k]
        c = pd.DataFrame(cM)
        plt.figure();
        sns.heatmap(c,xticklabels=False, yticklabels=False)
        plt.savefig(fig_name)  
        plt.close()
    
    D = getDataFromCMatrix(cMatrix, nrValues, xyValuePairs)
    return D

        
def getDataFromCMatrix(cMatrix,nrValues, xyValuePairs):
    """
        generate data from contingence matrix
        : where a value in cmatrix is > then 1 we save to dataList the values of : freq, xValue(row index) and yValue(column index)
        the data is a dataframe with 3 columns: Frequency X Y
    """
    dataList=[]
    maxXVal = max(xyValuePairs.keys())+1
    
   
    for xyValues in cMatrix.keys():
        freq = int(cMatrix[xyValues[0],xyValues[1]])
        dataList.append([freq, xyValues[0], xyValues[1]+maxXVal])
    
#    for x in xyValuePairs.keys():
#        xVal = x
#        for y in xyValuePairs[xVal]:
#            yVal=y
#            freq = int(cMatrix[xVal,yVal])
#            dataList.append([freq, x, yVal+maxXVal])
            
    return pd.DataFrame(dataList, columns=['Freq','X', 'Y'])


def fillDataTest(cmatrix):
    iterX=iterY=10
    cmatrix = fillCMatrix(cmatrix,0,0,iterX,iterY)
    cmatrix = fillCMatrix(cmatrix,10,10,iterX,iterY)
    cmatrix = fillCMatrix(cmatrix,20,20,iterX,iterY)
    cmatrix = fillCMatrix(cmatrix,30,30,iterX,iterY)
    cmatrix = fillCMatrix(cmatrix,40,40,iterX,iterY)
    cmatrix = fillCMatrix(cmatrix,50,50,iterX,iterY)
    cmatrix = fillCMatrix(cmatrix,60,60,iterX,iterY)
    cmatrix = fillCMatrix(cmatrix,70,70,iterX,iterY)
    cmatrix = fillCMatrix(cmatrix,80,80,iterX,iterY)
    cmatrix = fillCMatrix(cmatrix,90,90,iterX,iterY)
    
    #fill the center matrix with a zic-zac
    cmatrix = fillCMatrix(cmatrix,50,0,iterX,iterY)
    cmatrix = fillCMatrix(cmatrix,40,10,iterX,iterY)
    cmatrix = fillCMatrix(cmatrix,50,20,iterX,iterY)
    cmatrix = fillCMatrix(cmatrix,40,30,iterX,iterY)
    cmatrix = fillCMatrix(cmatrix,50,40,iterX,iterY)
    cmatrix = fillCMatrix(cmatrix,40,50,iterX,iterY)
    cmatrix = fillCMatrix(cmatrix,50,60,iterX,iterY)
    cmatrix = fillCMatrix(cmatrix,40,70,iterX,iterY)
    cmatrix = fillCMatrix(cmatrix,50,80,iterX,iterY)
    cmatrix = fillCMatrix(cmatrix,40,90,iterX,iterY)
    return cmatrix

def fillGradiantDataTest(cmatrix, nrValues=100, totalArcNumber=2000, shape=1, density_parameter=1):
    xValues=[]
    yValues=[]
    xyValuesPairs={}
    arcNumber = 0
    
#    x_values_prob = np.random.power(shape, nrValues)
#    y_values_prob = np.random.power(shape, nrValues)
#    
#    for count_x,x_prob in enumerate(x_values_prob):
#        if x_prob<.5:
#            xValues.append(count_x)
#    for count_y,y_prob in enumerate(y_values_prob):
#        if y_prob<.5:
#            yValues.append(count_y)
            
            
    while arcNumber < totalArcNumber:
#        i = randint(0, nrValues-1)
#        j = randint(0, nrValues-1)
        i = int(round(np.random.power(shape, 1)[0] * nrValues))
        j = int(round(np.random.power(shape, 1)[0] * nrValues))
        if i==nrValues:
            i-=1
        if j==nrValues:
            j-=1
        xValues.append(i)
        yValues.append(j)
#        x_values_prob = np.random.power(shape, 1)
#        y_values_prob = np.random.power(shape, 1)

        
        if i not in xyValuesPairs:
            xyValuesPairs[i]=[]
        if j not in xyValuesPairs[i]:
            xyValuesPairs[i].append(j)
        
        #compute the prob_arc
#        p_arc = (1-pow(fabs(i-j)/nrValues,1))
        p_arc = (1-pow(fabs(i-j)/nrValues,density_parameter))
        r = np.random.uniform(0,1,1)[0]
        if r <= p_arc:
            try:
                cmatrix[i, j] += 1
            except KeyError:
                cmatrix[i, j] = 1
            arcNumber += 1
             
    return cmatrix, xyValuesPairs

def fillCMatrix(cmatrix,startrow,startcolumn,nitemsrow,nitemscolumns):
        """
            generate contingency matrix
            write 1 on a specific cell (starting row, starting column, 
                                        with nitemsrow and nitemscolumns
                                        number of items on rows and columns
                                        respectively)
        """
        for i in range(startrow, startrow+nitemsrow):
            for j in range(startcolumn, startcolumn+nitemscolumns):
                cmatrix[i,j]=1
#        cmatrix[startrow:startrow+nitemsrow, startcolumn:startcolumn+nitemscolumns] = 1
        return cmatrix
    


def dataGenerationExperimentalProtocol():
    pathFiles = 'D:/Utilisateur/Marius/ScaledCoclustering/ExperimentalProtocol/ChooseK/original_data/GeneratedData_diag_density_original/'
    shape=1
    density_parameter=0.01
    N=[pow(10,7)]
    V=[pow(10,2)*2,pow(10,3)*2,pow(10,4)*2]
    i=1
#    for i in range(1,11):
    isPlot=False
    if i==1:
        isPlot=False
    for n in N:
        for v in V:
            print('generating data: '+str([n,v]))
            directory = 'N'+str(n)+'_V'+str(v)+'/data_N'+str(n)+'_V'+str(v)+'_nr'+str(i)+'/'
            pathToFiles = pathFiles + directory
            dataFileName = 'GeneratedDataGrad_N'+str(n)+'_V'+str(v)+'_nr'+str(i) +'.txt'
            DF= finfo.DataFileInfo(pathToFiles,dataFileName)
            fig_name = pathToFiles+'CMatrixGeneratedDataGrad_N'+str(n)+'_V'+str(v)+'_nr'+str(i) +'.png'
            d = generateData(option = 'on_grad', nrValues=v,totalArcNumber=n, shape=shape, isPlot=isPlot, fig_name=fig_name, density_parameter=density_parameter)
            writeDataToFile(d, DF)
            outputXsortedFile = pathToFiles+'GeneratedDataGradSortX_N'+str(n)+'_V'+str(v)+'_nr'+str(i) +'.txt'
            outputYsortedFile = pathToFiles+'GeneratedDataGradSortY_N'+str(n)+'_V'+str(v)+'_nr'+str(i) +'.txt'
            utl.writeSortedData(pathToFiles+dataFileName, outputXsortedFile, outputYsortedFile)
    
    

def dataGenerationStrinctDiagonal():
    i=1
    n=pow(10,6)
    v=200
    pathFiles = 'D:/Utilisateur/Marius/ScaledCoclustering/ExperimentalProtocol/GeneratedData_diag_strict/N{0}_V{1}/data_N{0}_V{1}_nr{2}/'.format(n,v,i)
    utl.detect_path(pathFiles)
    data_name = 'GeneratedDataGrad_N{0}_V{1}_nr{2}.txt'.format(n,v,i)
    data_sortX = 'GeneratedDataGradSortX_N{0}_V{1}_nr{2}.txt'.format(n,v,i)
    data_sortY = 'GeneratedDataGradSortX_N{0}_V{1}_nr{2}.txt'.format(n,v,i)
    data={}
    
    
    while sum(data.values())!=n:
        values = list(range(v))
        while(len(values)!=0):
            random.shuffle(values)
            val = values[0]
            del values[0]
            
            if (val,val) in data:
                data[(val,val)]+=1
            else:
                data[(val,val)]=1
            
            if sum(data.values())==n:
                break
                
    f = open(pathFiles + data_name,'w')
    f.write('X\tY\tFreq\n')
    for k in data.keys():
        f.write('{0}\t{1}\t{2}\n'.format(k[0],k[1],data[k]))
    f.close()
    utl.writeSortedData(pathFiles+data_name , pathFiles + data_sortX, pathFiles + data_sortY)            
#dataGenerationExperimentalProtocol()  





def dataGenerationStrinctDiagonal2DifVals():
    i=1
    n=pow(10,6)
    vx=400
    vy=2000
    v=vy#for name
    pathFiles = 'D:/Utilisateur/Marius/TwoModeCoclustering/ExperimentalProtocol/GeneratedData_diag_strict/test/N{0}_V{1}/data_N{0}_V{1}_nr{2}/'.format(n,v,i)
    utl.detect_path(pathFiles)
    data_name = 'GeneratedDataGrad_N{0}_V{1}_nr{2}.txt'.format(n,v,i)
    data_sortX = 'GeneratedDataGradSortX_N{0}_V{1}_nr{2}.txt'.format(n,v,i)
    data_sortY = 'GeneratedDataGradSortX_N{0}_V{1}_nr{2}.txt'.format(n,v,i)
    data={}
    
    
    while sum(data.values())!=n:
        valuesX = list(range(vx))
        valuesY = list(range(vy))
       
        while(len(valuesY)!=0):
            if len(valuesX)==0:
                valuesX = list(range(vx))
            random.shuffle(valuesX)
            valX = valuesX[0]
            del valuesX[0]
            
            random.shuffle(valuesY)
            valY = valuesY[0]
            del valuesY[0]
            
            if (valX,valY) in data:
                data[(valX,valY)]+=1
            else:
                data[(valX,valY)]=1
            
            if sum(data.values())==n:
                break
                
    f = open(pathFiles + data_name,'w')
    f.write('X\tY\tFreq\n')
    for k in data.keys():
        f.write('{0}\t{1}\t{2}\n'.format(k[0],k[1],data[k]))
    f.close()
    utl.writeSortedData(pathFiles+data_name , pathFiles + data_sortX, pathFiles + data_sortY)            

#dataGenerationStrinctDiagonal2DifVals()



def dataGenerationStrinctDiagonal2():
    n=pow(10,7)
    v=20000
    i=1
    pathFiles = 'D:/Utilisateur/Marius/ScaledCoclustering/ExperimentalProtocol/GeneratedData_diag_strict/N{0}_V{1}/data_N{0}_V{1}_nr{2}/'.format(n,v,i)
    utl.detect_path(pathFiles)
    data_name = 'GeneratedDataGrad_N{0}_V{1}_nr{2}.txt'.format(n,v,i)
    data_sortX = 'GeneratedDataGradSortX_N{0}_V{1}_nr{2}.txt'.format(n,v,i)
    data_sortY = 'GeneratedDataGradSortY_N{0}_V{1}_nr{2}.txt'.format(n,v,i)
    data={}
    
    for i in range(n):
        val = random.randint(0,v-1)
        if (val,val+v) in data:
            data[(val,val+v)]+=1
        else:
            data[(val,val+v)]=1
    
    f = open(pathFiles + data_name,'w')
    f.write('X\tY\tFreq\n')
    for k in data.keys():
        f.write('{0}\t{1}\t{2}\n'.format(k[0],k[1],data[k]))
    f.close()
    utl.writeSortedData(pathFiles+data_name , pathFiles + data_sortX, pathFiles + data_sortY)    

#def test_generate_data():
#    option='on_grad'
#    n=100000
#    v=200
#    i=1
#    pathFiles = '/test/'
#    dataFileName = 'GeneratedDataGrad_N'+str(n)+'_V'+str(v)+'_nr'+str(i) +'.txt'
#    DF= finfo.DataFileInfo(pathFiles,dataFileName)
#    d = generateData(option = 'on_grad', nrValues=v,totalArcNumber=n,shape=1.5, isPlot=True)
#    writeDataToFile(d, DF)
#    
#test_generate_data()

def dataGeneration3(n,v,i):
    pathFiles = 'D:/Utilisateur/Marius/TwoModeCoclustering/ExperimentalProtocol/GeneratedData_optimalI/N{0}_V{1}/data_N{0}_V{1}_nr{2}/'.format(n,v,i)
    utl.detect_path(pathFiles)
    data_name = 'GeneratedDataGrad_N{0}_V{1}_nr{2}.txt'.format(n,v,i)
    data={}
#    for i in range(n):
#        r = np.random.uniform(0,1,1)[0]
#        if r>=0.5:
#            x_val = random.randint(0,v-1)
#            y_val = x_val
#        else:
#            x_val = random.randint(0,v-1)
#            y_val = random.randint(0,v-1)
#        
#        if (x_val, y_val+v) in data:
#            data[(x_val,y_val+v)]+=1
#        else:
#            data[(x_val,y_val+v)]=1
            
    
    
    for i in range(int(n/2)):
        x_val = random.randint(0,v-1)
        y_val = x_val
        if (x_val, y_val+v) in data:
            data[(x_val,y_val+v)]+=1
        else:
            data[(x_val,y_val+v)]=1
        
    for i in range(int(n/2)):    
        x_val = random.randint(0,v-1)
        y_val = random.randint(0,v-1)
        
        if (x_val, y_val+v) in data:
            data[(x_val,y_val+v)]+=1
        else:
            data[(x_val,y_val+v)]=1
            
    
    f = open(pathFiles + data_name,'w')
    f.write('X\tY\tFreq\n')
    for k in data.keys():
        f.write('{0}\t{1}\t{2}\n'.format(k[0],k[1],data[k]))
    f.close()
    
#dataGeneration3()   

def generateRandom_I_Partition(pathFiles, data_name, nr_partitions):
    d = open(pathFiles + data_name, 'r')
    lines = d.readlines()
    d.close()
    data = {}
    nrValsX = {}
    nrValsY = {}
    
    if len(lines)>1:
        for e, l in enumerate(lines):
            if e==0:
                continue
            x_val=l.split('\t')[0]
            y_val=l.split('\t')[1]
            freq=l.split('\t')[2]
            
            if x_val in nrValsX:
                nrValsX[x_val] +=int(freq)
            else:
                nrValsX[x_val] = int(freq)
                
            if y_val in nrValsY:
                nrValsY[y_val] +=int(freq)
            else:
                nrValsY[y_val] = int(freq)
            
            if (x_val, y_val) in data:
                data[(x_val,y_val)]+=int(freq)
            else:
                data[(x_val,y_val)]=int(freq)
    partsX = {}
    partsY = {}
    N=sum(data.values())    
    
    xkeys = list(nrValsX.keys())
    random.shuffle(xkeys)
    ykeys = list(nrValsY.keys())
    random.shuffle(ykeys)
    
    
    current_vals = len(xkeys)
    current_I_max = nr_partitions
    count=0
    i=0
    while current_I_max>0:
        nr_ins = round(current_vals/current_I_max)
        current_vals-=nr_ins
        current_I_max-=1
        for k in xkeys[i:i+nr_ins]:
            partsX[k] = 'CX_{0}'.format(count)
        i+=nr_ins 
        count+=1
            
    cols=['Value','Cluster'] 
    partsX = pd.DataFrame(list(partsX.items()), columns=cols).sort_values(by='Cluster')
                
    
    current_vals = len(ykeys)
    current_I_max = nr_partitions
    count=0
    i=0
    while current_I_max>0:
        nr_ins = round(current_vals/current_I_max)
        current_vals-=nr_ins
        current_I_max-=1
        for k in ykeys[i:i+nr_ins]:
            partsY[k] = 'CY_{0}'.format(count)
        i+=nr_ins 
        count+=1
        
    cols=['Value','Cluster'] 
    partsY = pd.DataFrame(list(partsY.items()), columns=cols).sort_values(by='Cluster')
    
    khc_name = data_name.split('.')[0] + '.khc'
    f = open(pathFiles + khc_name, 'w')
    f.write('#Khiops 8.4.7.3i\n')
    f.write('Dimensions\t2\n')
    f.write('Name\tType\tParts\tInitial parts\tValues\tInterest\tDescription\t\n')
    f.write('X\tCategorical\t{0}\t{1}\t{2}\t{3}\t\n'.format(len(partsX.Cluster.unique()), len(partsX.Cluster.unique()), len(partsX.Value.unique()), 1))
    f.write('Y\tCategorical\t{0}\t{1}\t{2}\t{3}\t\n'.format(len(partsY.Cluster.unique()), len(partsY.Cluster.unique()), len(partsY.Value.unique()), 1))
    f.write('\n')
    
    f.write('Composition\tX\n')
    f.write('Cluster\tValue\tFrequency\tTypicality\n')
    for index, row in partsX.iterrows():
        val = row['Value']        
        klas = row['Cluster']
        val_freq=nrValsX[val]        
        f.write('{0}\t{1}\t{2}\t{3}\n'.format(klas,val,val_freq,1))
    f.write('\n')
    
    f.write('Composition\tY\n')
    f.write('Cluster\tValue\tFrequency\tTypicality\n')
    for index, row in partsY.iterrows():
        val = row['Value']        
        klas = row['Cluster']
        val_freq=nrValsY[val]        
        f.write('{0}\t{1}\t{2}\t{3}\n'.format(klas,val,val_freq,1))
    f.close()

def generateRandomPartition(pathFiles, data_name):
    d = open(pathFiles + data_name, 'r')
    lines = d.readlines()
    d.close()
    data = {}
    nrValsX = {}
    nrValsY = {}
    
    if len(lines)>1:
        for e, l in enumerate(lines):
            if e==0:
                continue
            x_val=l.split('\t')[0]
            y_val=l.split('\t')[1]
            freq=l.split('\t')[2]
            
            if x_val in nrValsX:
                nrValsX[x_val] +=int(freq)
            else:
                nrValsX[x_val] = int(freq)
                
            if y_val in nrValsY:
                nrValsY[y_val] +=int(freq)
            else:
                nrValsY[y_val] = int(freq)
            
            if (x_val, y_val) in data:
                data[(x_val,y_val)]+=int(freq)
            else:
                data[(x_val,y_val)]=int(freq)
    partsX = {}
    partsY = {}
    N=sum(data.values())    
    I_max=math.sqrt(N)
    
    xkeys = list(nrValsX.keys())
    random.shuffle(xkeys)
    ykeys = list(nrValsY.keys())
    random.shuffle(ykeys)
    
#    print(len(nrValsX))
#    print(I_max)
    
    if len(nrValsX)<I_max:
        count=0
        for k in xkeys:
            partsX[k] = 'CX_{0}'.format(count)
            count+=1
    else:
        current_vals = len(xkeys)
        current_I_max = round(math.sqrt(N))
        count=0
        i=0
        while current_I_max>0:
            nr_ins = round(current_vals/current_I_max)
            current_vals-=nr_ins
            current_I_max-=1
            for k in xkeys[i:i+nr_ins]:
                partsX[k] = 'CX_{0}'.format(count)
            i+=nr_ins 
            count+=1
            
    cols=['Value','Cluster'] 
    partsX = pd.DataFrame(list(partsX.items()), columns=cols).sort_values(by='Cluster')
                
    if len(nrValsY)<I_max:
        count=0
        for k in ykeys:
            partsY[k] = 'CY_{0}'.format(count)
            count+=1
    
    else:
        current_vals = len(ykeys)
        current_I_max = round(math.sqrt(N))
        count=0
        i=0
        while current_I_max>0:
            nr_ins = round(current_vals/current_I_max)
            current_vals-=nr_ins
            current_I_max-=1
            for k in ykeys[i:i+nr_ins]:
                partsY[k] = 'CY_{0}'.format(count)
            i+=nr_ins 
            count+=1
        
    cols=['Value','Cluster'] 
    partsY = pd.DataFrame(list(partsY.items()), columns=cols).sort_values(by='Cluster')
    
    khc_name = data_name.split('.')[0] + '.khc'
    f = open(pathFiles + khc_name, 'w')
    f.write('#Khiops 8.4.7.3i\n')
    f.write('Dimensions\t2\n')
    f.write('Name\tType\tParts\tInitial parts\tValues\tInterest\tDescription\t\n')
    f.write('X\tCategorical\t{0}\t{1}\t{2}\t{3}\t\n'.format(len(partsX.Cluster.unique()), len(partsX.Cluster.unique()), len(partsX.Value.unique()), 1))
    f.write('Y\tCategorical\t{0}\t{1}\t{2}\t{3}\t\n'.format(len(partsY.Cluster.unique()), len(partsY.Cluster.unique()), len(partsY.Value.unique()), 1))
    f.write('\n')
    
    f.write('Composition\tX\n')
    f.write('Cluster\tValue\tFrequency\tTypicality\n')
    for index, row in partsX.iterrows():
        val = row['Value']        
        klas = row['Cluster']
        val_freq=nrValsX[val]        
        f.write('{0}\t{1}\t{2}\t{3}\n'.format(klas,val,val_freq,1))
    f.write('\n')
    
    f.write('Composition\tY\n')
    f.write('Cluster\tValue\tFrequency\tTypicality\n')
    for index, row in partsY.iterrows():
        val = row['Value']        
        klas = row['Cluster']
        val_freq=nrValsY[val]        
        f.write('{0}\t{1}\t{2}\t{3}\n'.format(klas,val,val_freq,1))
    f.close()
    

#n=pow(10,6)
#v=pow(10,2)
#i=1
#pathFiles = 'D:/Utilisateur/Marius/TwoModeCoclustering/ExperimentalProtocol/GeneratedData_optimalI/N{0}_V{1}/data_N{0}_V{1}_nr{2}/'.format(n,v,i)
#data_name = 'GeneratedDataGrad_N{0}_V{1}_nr{2}.txt'.format(n,v,i)
#generateRandomPartition(pathFiles, data_name)