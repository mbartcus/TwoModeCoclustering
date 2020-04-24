# TwoModeCoclustering
A scalable two-level co-clustering algorithm

##Introduction to source code for paper: 
"A scalable two-level co-clustering algorithm"

Marius Bartcus, Marc BoullÈ, Fabrice ClÈrot

firstname.lastname@orange.com

The source code contains the following python files:

1) script_test_2LKHC.py
2) datasets.py
3) TwoLevelCoclustering.py
4) constants.py
5) KHCUtils.py
6) KhiopsCoclustering.py
7) SubDataSet.py
8) KHChoosePartitionSize.py
9) CoclusteringModel.py
10) khiopsStats.py
11) utils.py
12) DataUtils.py

## 
to obtain a detailed information on each of theese source code:
import file_name.py as f
help(f)
these gives information on the selected source code with information on classes and functions
each function and class has it's comments that will be given by "help(f)"
## 

###THE SHORT DESCRIPTION OF EACH PYTHON FILE

1) script_test_2LKHC.py
The main script that runs the optimize two level coclustering
2) datasets.py
The data sets setting names
3) TwoLevelCoclustering.py
The main two level coclustering algorithm implementation
4) constants.py
settings to run the algorithm
5) KHCUtils.py
routines for Khiops to run KHCp, KHCc, KHCe
also creates Khiops scripts 
6) KhiopsCoclustering.py
routine to run Khiops coclustering
7) SubDataSet.py
class to stock the subdata set information
8) KHChoosePartitionSize.py
routine to compute the number of parts for first variable and for the second variable
9) CoclusteringModel.py
parse the coclustering model
10) khiopsStats.py
routines MODL
11) utils.py
routines python: file reading, writing files, compute MODL, python dictionaries,list manipulations, etc
12) DataUtils.py
Generate artificial data sets
