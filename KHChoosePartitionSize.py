import math
import constants as const

########################################################
# Choice of partition size
# Inputs: 
#   N: size of datasets
#   VX: number of X values
#   VY: number of Y values
# Outputs:
#   Ic_best, Jc_best, time_best: optimal number of coarse clusters on X and Y, and best time
def ChoosePartitionSize(N, VX, VY, traceFile=None):
    # Initial solution with KHC alone
    Ic_best=1
    Jc_best=1
    time_best = TimeKHC(N, VX, VY)
    time_result = time_best
    tolerance = 0.5
    
    # Gestion de la trace pour la solution initiale
    if not traceFile is None:
        traceFile.write(str(N) + "\t")
        traceFile.write(str(VX) + "\t")
        traceFile.write(str(VY) + "\t")
        traceFile.write("1\t1\t")
        traceFile.write(str(time_best) + "\t")
        traceFile.write("0\t0\t0\t0\t0\t0\t0\n")

    # Optimize number of coarse clusters for 2L-KHC.
    Ic=1
    Jc=1
    while True:
        # Increment number of coarse clusters
        if VX/Ic > VY/Jc:
            Ic = Ic+1
        else: 
            Jc = Jc+1
        # Stop if minimum size constraint are not met
        n= N/(Ic * Jc)     # average number of instances per sub data set
        vX= VX/Ic          # number of values per sub data set
        vY= VY/Jc
        if n < const.Nmin or vX < const.Vmin or vY < const.Vmin or n < vX*const.nuMin or n < vY*const.nuMin:
            return  Ic_best, Jc_best, time_result
        # Evaluate overall computation time
        Time = Time2LKHC(N, VX, VY, Ic,Jc, traceFile)
        if Time < time_best:
            time_best = Time
            time_result = time_best
            Ic_best = Ic
            Jc_best = Jc
        if Time < time_best*(1+tolerance):
            time_result = Time
            Ic_best = Ic
            Jc_best = Jc


########################################################
# Estimation of the computation time for 2L-KHC

# Computation time of 2L-KHC
def Time2LKHC(N, VX, VY, Ic, Jc, traceFile=None):
    time = 0
    
    # Partitioning step
    time_part = TimeKHCp(N, VX, VY, Ic, Jc)
    time += time_part

    # Fine co-clustering step
    n= N/(Ic * Jc)     # average number of instances per sub data set
    vX= VX/Ic          # number of values per sub data set
    vY= VY/Jc
    time_fcc = TimeKHCc(n, vX, vY, const.Imax)
    time += Ic * Jc * time_fcc

    # Amalgamate step: columns
    time_ssd = 0
    time_acd = 0
    time_scd = 0
    if VX > const.Vmax and Ic > 1:
        # Amalgamate step: simplify sub data set models
        jmax = min (const.Imax, math.sqrt(n), vY)     # maximum number of fine clusters on Y per sub data set
        if Jc * jmax > const.Vmax:
            time_ssd = TimeKHCs(n, vX, vY, const.Imax)
            time += Ic * Jc * time_ssd
    
        # Amalgamate step: amalgamate column data sets
        nX= N/Ic     # average number of instances per column data set
        vXcol=VX/Ic     # max number of super-values on X per column data set
        vYcol = min(VY, const.Vmax, Jc * jmax)     # max number of super-values on Y per column data set
        time_acd = TimeKHCc(nX, vXcol, vYcol, const.Imax)
        time += Ic * time_acd
    
        # Amalgamate step: simplify column data sets
        imaxX = min (const.Imax, math.sqrt(nX), vXcol)     # maximum number of mini clusters on X per column sub data set
        if Ic * imaxX > const.Vmax:
            time_scd = TimeKHCs(nX, vXcol, vYcol, const.Imax)
            time += Ic * time_scd

    # Amalgamate step: rows
    time_ard = 0
    time_srd = 0
    if VY > const.Vmax and Jc > 1:
        # Amalgamate step: amalgamate row data sets
        nY= N/Jc     # average number of instances per row data set
        vXrow = min(VX, const.Vmax, math.sqrt(Ic * N))     # max number of super-values on X per row data set
        vYrow= VY/Jc     # max number of super-values on Y per row data set
        time_ard = TimeKHCc(nY, vXrow, vYrow, const.Imax)    
        time += Jc * time_ard
    
        # Amalgamate step: simplify row data sets
        jmaxY = min (const.Imax, math.sqrt(nY), vYrow)     # maximum number of mini clusters on Y per row sub data set
        time_srd =0
        if Jc * jmaxY > const.Vmax:
            time_srd = TimeKHCs(nY, vXrow, vYrow, const.Imax)
            time += Jc * time_srd

    # Post-optimization step
    vXpost = min(VX, const.Vmax)    # max number of super-values on X and     Y    
    vYpost = min(VY, const.Vmax)     
    time_post = TimeKHCc(N, vXpost, vYpost, const.Imax)
    time += time_post
    
    # Gestion de la trace
    if not traceFile is None:
        traceFile.write(str(N) + "\t")
        traceFile.write(str(VX) + "\t")
        traceFile.write(str(VY) + "\t")
        traceFile.write(str(Ic) + "\t")
        traceFile.write(str(Jc) + "\t")
        traceFile.write(str(time) + "\t")
        traceFile.write(str(time_part) + "\t")
        traceFile.write(str(Ic * Jc * time_fcc) + "\t")
        traceFile.write(str(Ic * Jc * time_ssd) + "\t")
        traceFile.write(str(Ic * time_acd) + "\t")
        traceFile.write(str(Ic * time_scd) + "\t")
        traceFile.write(str(Jc * time_ard) + "\t")
        traceFile.write(str(Jc * time_srd) + "\t")
        traceFile.write(str(time_post) + "\n")
    
    # On retourne le temps global
    return time

# Write header of trace file
def WriteTime2LKHCTraceHeader(traceFile):
    traceFile.write("N\t")
    traceFile.write("VX\t")
    traceFile.write("VY\t")
    traceFile.write("Ic\t")
    traceFile.write("Jc\t")
    traceFile.write("time\t")
    traceFile.write("PART\t")
    traceFile.write("FCC\t")
    traceFile.write("SSD\t")
    traceFile.write("ACD\t")
    traceFile.write("SCD\t")
    traceFile.write("ARD\t")
    traceFile.write("SRD\t")
    traceFile.write("POST\n")


########################################################
# Estimation of the computation time for KHCc and KHCs

# Constants for the estimation of the computation times
a1KHCc = 2.2E-6  # For KHCc pre-optimization
a2KHCc = 2.2E-7  # For KHCc optimization
a3KHCc = 2.7E-7  # For KHCc post-optimization

# Computation time for KHC
def TimeKHC(N, VX, VY):
    return TimeKHCc(N, VX, VY, math.sqrt(N))

# Computation time for KHCc
def TimeKHCc(N, VXs, VYs, cmax):
    return TimeKHCc1(N, VXs, VYs, cmax) + TimeKHCc2(N, VXs, VYs, cmax) + TimeKHCc3(N, VXs, VYs, cmax)

# Computation time for KHCs
def TimeKHCs(N, VXs, VYs, cmax):
    return TimeKHCc2(N, VXs, VYs, cmax)

# Computation time for KHCp
def TimeKHCp(N, VX, VY, Ic, Jc):
    time = a1KHCc * min(N*math.sqrt(N), (VX+VY)*Ic*Jc/2)
    return time

# Computation time for KHCc pre-optimisation
def TimeKHCc1(N, VXs, VYs, cmax):
    IX = min(cmax, VXs, math.sqrt(N))
    IY = min(cmax, VYs, math.sqrt(N))
    time = a1KHCc * min(N*math.sqrt(N), (VXs+VYs)*IX*IY/2)
    return time

# Computation time for KHCc optimisation
def TimeKHCc2(N, VXs, VYs, cmax):
    IX = min(cmax, VXs, math.sqrt(N))
    IY = min(cmax, VYs, math.sqrt(N))
    time = a2KHCc * min(N*math.sqrt(N)*math.log(N), IX*IY*(IX*math.log(IX)+IY*math.log(IY))/2)
    return time

# Computation time for KHCc post-optimisation
def TimeKHCc3(N, VXs, VYs, cmax):
    IX = min(cmax, VXs, math.sqrt(N))
    IY = min(cmax, VYs, math.sqrt(N))
    time = a3KHCc * min(N*math.sqrt(N)*math.log(N), (VXs+VYs)*IX*IY*math.log(N)/2)
    return time

########################################################
# Test
    
def TestChoosePartitionSize(N, VX, VY):
    trace = True
    traceFile = None
    if trace:
        traceFile = open("TraceTime_" + str(N) + "_" + str(VX) + "_" + str(VY) + ".txt", "w")
        WriteTime2LKHCTraceHeader(traceFile)
    Ic, Jc, time2LKHC = ChoosePartitionSize(N, VX, VY, traceFile)
    timeKHC = TimeKHC(N, VX, VY)
    if trace:
        traceFile.close()
    print(str(N) + ", " + str(VX) + ", " + str(VY) + ": " + 
          str(Ic) + " x " + str(Jc) + ", " + 
          str(int(time2LKHC)) + ", " +
          str(int(timeKHC)) + " -> " + 
          str(int(10*timeKHC/time2LKHC)/10))

def TestAll():    
    TestChoosePartitionSize(1000000000, 1000000, 1000000)    
    TestChoosePartitionSize(10000000, 100000, 100000)    
    TestChoosePartitionSize(1000000, 200, 200)    
    TestChoosePartitionSize(1000000, 2000, 2000)    
    TestChoosePartitionSize(1000000, 20000, 20000)    
    TestChoosePartitionSize(10000000, 200, 200)    
    TestChoosePartitionSize(10000000, 2000, 2000)    
    TestChoosePartitionSize(10000000, 20000, 20000)    
    TestChoosePartitionSize(2047830, 19464, 11315)    
    TestChoosePartitionSize(2047830, 11315, 19464)    
    TestChoosePartitionSize(4562219, 18774, 61188)    
    TestChoosePartitionSize(4562219, 61188, 18774)
    TestChoosePartitionSize(13068666, 390130, 400000)    
    TestChoosePartitionSize(13068666, 400000, 390130)    
    TestChoosePartitionSize(960327, 16235, 4649)    
    TestChoosePartitionSize(960327, 4649, 16235)    
    TestChoosePartitionSize(10049248, 17764, 48068)    
    TestChoosePartitionSize(10049248, 48068, 17764)    
    TestChoosePartitionSize(100000000, 480000, 18000)    
    TestChoosePartitionSize(100000000, 18000, 480000)

def TestTimeKHc():
    N = 100000000
    VX = 100000
    VY = 100000
    time = TimeKHCc(N, VX, VY, const.Imax)
    print(str(time))
    time1 = TimeKHCc1(N, VX, VY, const.Imax)
    print(str(time1))
    time2 = TimeKHCc2(N, VX, VY, const.Imax)
    print(str(time2))
    time3 = TimeKHCc3(N, VX, VY, const.Imax)
    print(str(time3))

#TestTimeKHc()
#TestAll()

