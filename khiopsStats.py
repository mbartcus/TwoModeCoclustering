import math, os
import numpy as np
import time

showData = False
showCriterion = False

def setTrace(trace):
    global showData
    global showCriterion
    showData = trace
    showCriterion = trace

def binomial(n,k) :
    b=factorial(n)/(factorial(n-k)*factorial(k))
    return b

def logbinomial(n,k) :
    b=logfactorial(n)-logfactorial(n-k)-logfactorial(k)
    return b

def factorial(n) :
    f=1.
    for i in range(1,n+1) :
       f*=i
    return f

logFactorialTable = []

def logfactorial(n) :
    # Cas des petit n: version tabulee
    if n <= 1000000:
        # Precalcul si necessaire de la table des log(fact)
        if len(logFactorialTable) == 0:
            logFactorialTable.append(0)
            for i in range(1000000):
                logFactorialTable.append(logFactorialTable[i]+math.log(i+1))
#        assert(math.fabs(logFactorialTable[n] - oldlogfactorial(n)) < 1e-6)
        return logFactorialTable[n]
    # Cas des grande valeurs: approximation de Striling
    else:
        return n*math.log(n)-n+1./2.*math.log(2*math.pi*n)+1./(12.*n)-1./(360.*math.pow(n,3))+1./(1260.*math.pow(n,5))            

def oldlogfactorial(n) :
    n=int(n)
    f=1.
    for i in range(n) :
        f*=(n-i)
        if f==float('inf') :
            return n*math.log(n)-n+1./2.*math.log(2*math.pi*n)+1./(12.*n)-1./(360.*math.pow(n,3))+1./(1260.*math.pow(n,5))
    return math.log(f)


# Calcul des log des nombre de bell
# Pour obtenir Ln(Bell(n, k)): appeler setDicoLnBell(n)[k]
def setDicoLnBell(n) :
    fichier=os.popen("BellNumberGenerator.exe "+str(n), "r")
    bellList = fichier.readlines()
    fichier.close()
    del bellList[0]
    dBell={}
    for bl in bellList :
        l=bl[:-1].split('\t')
        dBell[int(l[1])]=float(l[2])
    dBell[1]=1.
    return dBell


def computePrior(G):
    k1,k2,m=len(G.getPartitionX()),len(G.getPartitionY()),G.getInstances()
    n1,n2=0,0
    prior=math.log(2)+logbinomial(3,2)
    for px in G.getPartitionX():
        #print px.getValues()
        mic=px.getWeight()
        nic=len(px.getValues())
        n1+=nic
        prior+=logbinomial(mic+nic-1,nic-1)
    for py in G.getPartitionY():
        #print py.getValues()
        mjc=py.getWeight()
        njc=len(py.getValues())
        n2+=njc
        prior+=logbinomial(mjc+njc-1,njc-1)
    prior+=math.log(n1)
    prior+=math.log(n2)
    prior+=setDicoLnBell(n1)[k1]
    prior+=setDicoLnBell(n2)[k2]
    prior+=logbinomial(m+k1*k2-1,k1*k2-1)
    # Affichage de la structure du coclustering
    if showData:
        print("Instances: "+str(m))
        print("Partition X: "+ str(n1) + ", " + str(k1))
        for p, px in enumerate(G.getPartitionX()):
            print("\tPartX" + str(p+1) + " (" + str(len(px.getValues())) +"): " + str(px.getValues()))
        print("Partition Y: "+ str(n2) + ", " + str(k2))
        for p, py in enumerate(G.getPartitionY()):
            print("\tPartY" + str(p+1) + " (" + str(len(py.getValues())) +"): " + str(py.getValues()))
    if showCriterion:
        print("prior: "+str(prior))
        print("prior vars: "+str(math.log(2)+logbinomial(3,2)))
        print("prior partition X: "+str(math.log(n1)+setDicoLnBell(n1)[k1]))
        print("prior partition Y: "+str(math.log(n2)+setDicoLnBell(n2)[k2]))
        print("prior data grid multinomial: "+str(logbinomial(m+k1*k2-1,k1*k2-1)))
        for px in G.getPartitionX():
            #print px.getValues()
            mic=px.getWeight()
            nic=len(px.getValues())
            n1+=nic
            pxprior=logbinomial(mic+nic-1,nic-1)
            print("prior part X (" + str(mic) + ", " + str(nic) + "): "+str(pxprior))
        for py in G.getPartitionY():
            #print py.getValues()
            mjc=py.getWeight()
            njc=len(py.getValues())
            n2+=njc
            pyprior=logbinomial(mjc+njc-1,njc-1)
            print("prior part Y (" + str(mjc) + ", " + str(njc) + "): "+str(pyprior))
    return prior

def computeLikelihood(G,D):
    pX, pY=G.getPartitionX(),G.getPartitionY()
    cells=G.getCells()
    m=G.getInstances()
    X,Y=D.getVarX(), D.getVarY()
    
#    print('Px:{0}\nLen Px:{1}\n'.format(pX, len(pX)))
#    print('Py:{0}\nLen Py:{1}\n'.format(pY, len(pY)))
#    for px in pX:
#        print('Px weigt:{0}\nPx Id:{1}\n'.format(px.getWeight(), px.getId()))
#    for py in pY:
#        print('Py weigt:{0}\nPy Id:{1}\n'.format(py.getWeight(), py.getId()))
#    print('m:'+str(m))
#    print('X:{0}\nLen X:{1}\n'.format(X, len(X)))
#    print('Y:{0}\nLen Y:{1}\n'.format(Y, len(Y)))
    
    likelihood=logfactorial(m)
#    print('1:'+str(likelihood))
    for px in pX :
        for py in pY:
            try:likelihood-=logfactorial(cells[px.getId(),py.getId()])
            except : pass
#    print('2:'+str(likelihood))
    for px in pX :
        likelihood+=logfactorial(px.getWeight())
#    print('3:'+str(likelihood))
    for py in pY :
        likelihood+=logfactorial(py.getWeight())
#    print('4:'+str(likelihood))
	
    for k in X.keys() :
        likelihood-=logfactorial(X[k])
#    print('5:'+str(likelihood))
    for k in Y.keys() :
        likelihood-=logfactorial(Y[k])
#    print('6:'+str(likelihood))
    # Affichage de la structure du coclustering
    if showData:
        print("Cells: "+str(len(cells)))
    if showCriterion:
#        print("likelihood: "+str(likelihood))
#        ll=logfactorial(m)
#        print("ll global (" + str(m) + "): "+str(ll))
#        llAll = 0
#        freq_ll_cell = np.zeros((len(list(enumerate(pX))), len(list(enumerate(pY)))))
#        ll_cell = np.zeros((len(list(enumerate(pX))), len(list(enumerate(pY)))))-np.NaN
#        for i, px in enumerate(pX) :
#            for j, py in enumerate(pY):
#                try:
#                    ll=-logfactorial(cells[px.getId(),py.getId()])
#                    llAll += ll
#                    #print('{0}_____{1}'.format(px.getId(),py.getId()))
#                    print("ll cell (" + str(i+1) + ", " + str(j+1) + ": " + str(cells[px.getId(),py.getId()]) + "): "+str(ll))
#                    freq_ll_cell[i, j] = cells[px.getId(),py.getId()]
#                    ll_cell[i, j] = ll
#                except : pass
#        print('Freq on cells:')
#        print(*freq_ll_cell.astype(int), sep=' ')
#        print("all cells: " + str(llAll))
#        llAll = 0
#        freq_X_part = np.zeros(len(list(enumerate(pX))))
#        freq_Y_part = np.zeros(len(list(enumerate(pY))))
#        
#        for i, px in enumerate(pX) :
#            ll=logfactorial(px.getWeight())
#            llAll += ll
#            print("ll part X (" + str(i+1) + ":" + str(px.getWeight()) + "): "+str(ll))
#            freq_X_part[i] = px.getWeight()
#        print("all part X: " + str(llAll))
#        llAll = 0
#        for j, py in enumerate(pY):
#            ll=logfactorial(py.getWeight())
#            llAll += ll
#            print("ll part Y (" + str(j+1) + ": " + str(py.getWeight()) + "): "+str(ll))
#            freq_Y_part[j] = py.getWeight()
#        print("all part Y: " + str(llAll))
#        print('X part freq')
#        print(*freq_X_part.astype(int), sep=' ')
#        print('Y part freq')
#        print(*freq_Y_part.astype(int), sep=' ')
        
        llAll = 0
        for k in X.keys() :
            ll=-logfactorial(X[k])
            llAll += ll
            print("ll value X (" + str(k) + 'freq = ' + str(X[k]) + "): "+str(ll))
        print("all values X: " + str(llAll))
        llAll = 0
        for k in Y.keys() :
            ll=-logfactorial(Y[k])
            llAll += ll
            print("ll value Y ("+ str(k) + 'freq = ' + str(Y[k]) + "): "+str(ll))
        print("all values Y: " + str(llAll))
    return likelihood