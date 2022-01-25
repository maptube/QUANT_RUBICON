"""
databuilder.py
Builds the data needed by the test models
Run this file first to auto generate all the trips matrices and raw data needed to run the models.
Look in globals.py for the names of all the files it creates.

NOTE: the "zonecodes.csv" file is central to the code and contains a lookup between the geographic
area code (e.g. "E02000001") and the zone number (e.g. "0") which is the row and col number in all
the matrices.


The QUANT2 installer is an update to the GISTAM 2019 paper, as QUANT2 now adds
data for Scotland to make an integrated Great Britain model where QUANT1 was just
England and Wales. All the trips and cost matrices are essentially identical, it's just
that there are more areas.

All configuration for what to install is in the main program at the end of this
listing.

The 'tmpDataDir' is where temporary files are downloaded to that can be deleted after
installation. The 'modelRunsDir' contains the live files which are needed to run models.
"""

import os
import os.path
import zipfile
import urllib.request
import ssl
#THIS IS VERY BAD - urllib request throws bad cert on OSF.io otherwise
ssl._create_default_https_context = ssl._create_unverified_context
import numpy as np
from shutil import copyfile
from globals import *
#from utils import loadZoneLookup #moved to zonecodes
#from zonecodes import ZoneCodes
from utils import generateTripsMatrix
from utils import loadMatrix, saveMatrix, loadQUANTMatrix, loadQUANTCSV


#definitions of where everything downloads from and goes to

tmpDataDir = 'data' #tmpDataDir contains data downloaded or created from QUANT used to make training sets
modelRunsDir = 'model-runs' #where the 'live' data needed to run models goes

urlWU03EU = 'https://www.nomisweb.co.uk/output/census/2011/wu03ew_msoa.zip'
#QUANT1 matrices for GISTAM 2019 are available here (England/Wales only 7201 zones):
#https://osf.io/bgcen/ for the project containing the QUANT1 data
url_QUANT1_trainingdata_Road_csv = 'https://osf.io/8vcjq/download' #this is origin, dest, TObsFlow, Cij data
url_QUANT1_trainingdata_Bus_csv = 'https://osf.io/abjqm/download'
url_QUANT1_trainingdata_GBRail_csv = 'https://osf.io/fvqn4/download'
url_QUANT1_TijRoad_csv = 'https://osf.io/sp4qd/download' #TijRoadObs.csv
url_QUANT1_TijBus_csv = 'https://osf.io/7ujrz/download' #TijBusObs.csv
url_QUANT1_TijGBRail_csv = 'https://osf.io/kdt5b/download' #TijRailObs.csv
url_QUANT1_TijRoad_qcs = 'https://osf.io/65zy9/download' #TObs_1.bin (QUANT C Sharp)
url_QUANT1_TijBus_qcs = 'https://osf.io/e4hy7/download' #TObs_2.bin (QUNAT C Sharp)
url_QUANT1_TijGBRail_qcs = 'https://osf.io/e6fm5/download' #TObs_3.bin (QUANT C Sharp)
url_QUANT1_CijRoadMin_csv = 'https://osf.io/4fhp3/download' #dijRoad_min.csv
url_QUANT1_CijBusMin_csv = 'https://osf.io/wjmsa/download' #dijBus_min.csv
url_QUANT1_CijRailMin_csv = 'https://osf.io/rtme9/download' #dijRail_min.csv
url_QUANT1_CijRoadMin_qcs = 'https://osf.io/7jpvm/download' #dis_roads_min.bin (QUANT C Sharp)
url_QUANT1_CijBusMin_qcs = 'https://osf.io/7wqf3/download' #dis_bus_min.bin (QUANT C Sharp)
url_QUANT1_CijGBRailMin_qcs = 'https://osf.io/4m6ug/download' #dis_gbrail_min.bin (QUANT C Sharp)
url_QUANT1_CijCrowflyKM_qcs = 'https://osf.io/5cjyn/download' #dis_crowfly_KM.bin (QUANT C Sharp)
url_QUANT1_ZoneCodesText = 'https://osf.io/hu9zw/download' #ZoneCodesText.csv

#QUANT2 matrices, from OSF data site, which now include Scotland (8436 zones):
#url_QUANT2_EWS_censustraveltowork = 'https://osf.io/du8ar/download' #makes Tij matrices
#NOTE: I haven't created any training data files for QUANT2
#url_QUANT2_trainingdata_Road_csv = '' #this is origin, dest, TObsFlow, Cij data
#url_QUANT2_trainingdata_Bus_csv = ''
#url_QUANT2_trainingdata_GBRail_csv = ''
url_QUANT2_TijRoad_qcs = 'https://osf.io/ga9m3/download'
url_QUANT2_TijBus_qcs = 'https://osf.io/nfepz/download'
url_QUANT2_TijRail_qcs = 'https://osf.io/at9vc/download'
url_QUANT2_CijRoadMin_qcs = 'https://osf.io/u2mz6/download'
url_QUANT2_CijBusMin_qcs = 'https://osf.io/bd4s2/download'
url_QUANT2_CijGBRailMin_qcs = 'https://osf.io/gq8z7/download'
url_QUANT2_ZoneCodesText = 'https://osf.io/hu7bd/download'

"""
Utility to check if files exist and download QUANT format C Sharp binary files and convert
to pickle for python. The QUANT matrices are just m,n dimensions as two 4 byte IEEE754 floats
then m x n 4 byte floats containing all the row and column data.
@param localFilename This is the file that we're going to create - this is the pickled one
@param localDir This is the dir that contains localFilename
@param url This is the url to download it from if above localFilename doesn't exist
@param qcsFilename This is the filename of the C Sharp binary file downloaded from the url
which may be the same as the localFilename, or could be different. NOTE: the quant file is
always downloaded to tmpDataDir/fromQUANT regardless of localDir. This makes sense as it is
a CS file, not a Python one, so shouldn't be in model-runs
"""
def ensureMatrixFileQUANTtoPickle(localFilename, localDir, url, qcsFilename):
    if os.path.isfile(os.path.join(localDir, localFilename)):
        print('databuilder.py:',localFilename,' exists - skipping')
    else:
        print('databuilder.py: ',localFilename,' downloading from ',url)
        path_qcs = os.path.join(tmpDataDir+'/fromQUANT',qcsFilename) #download to the temp dir where QUANT CS mats are stored
        urllib.request.urlretrieve(url, path_qcs)
        #load the QUANT CSharp format matrix and pickle it for python
        M = loadQUANTMatrix(path_qcs)
        path_pic = os.path.join(localDir,localFilename)
        print('databuilder.py: saving file ',path_pic)
        saveMatrix(M,path_pic) #save pickled matrix
###

"""
Utility to check for the existence of a plain file and download it from the given url if
it does not exist.
@param localFilename the name of the file in the localDir dir
@param localDir the dir containing localFilename
@param the url to download it from if not present on the current file system
"""
def ensurePlainFile(localFilename, localDir, url):
    if os.path.isfile(os.path.join(localDir, localFilename)):
        print('databuilder.py:',localFilename,' exists - skipping')
    else:
        print('databuilder.py: ',localFilename,' downloading from ',url)
        path = os.path.join(localDir,localFilename)
        urllib.request.urlretrieve(url, path)
        print('databuilder.py: created file ',localFilename,' in',localDir)
###

"""
Check if localFilename exists in the dir directory. If not, then download
it (as a zip file) from the given url and unzip it in dir.
@param localFilename The file we're checking for its existence
@param localDir The directory containing localFilename
@param url The url to download localFilename from if it doesn't exist. Download goes into
dir/localFilename and then gets unzipped into the same directory.
"""
def ensurePlainZIPFile(localFilename, localDir, url):
    if os.path.isfile(os.path.join(localDir, localFilename)):
        print('databuilder.py:',localFilename,' exists - skipping')
    else:
        #NO! need to download a zip! Change the name first as localFilename is the unzipped version
        print('databuilder.py: ',localFilename,' downloading from ',url)
        basename, ext = os.path.splitext(localFilename) #what we download is a .zip file
        zippath = os.path.join(localDir,basename+'.zip')
        urllib.request.urlretrieve(url, zippath)
        print('databuilder.py: created file ',localFilename,' in ',localDir)
        #now unzip it into localFilename
        zip_ref = zipfile.ZipFile(zippath, 'r')
        zip_ref.extractall(localDir)
        zip_ref.close()
###

################################################################################
# Now on to the data production
################################################################################



################################################################################

"""
Download and install all the data for the updated QUANT version 2, which
also contains Scotland data.
Rather than building the flow matrices from the Census file, just download
the matrices from the Open Science Foundation data dump. This makes a lot
more sense as the QUANT 2 data contains Scotland flows which are in a different
file to the England and Wales one. Using the pre-computed matrices like this
means that the real QUANT2 can do the hard part of stitching all the data back
together again. If you want to know where the data comes from, the flows including
Scotland are in the file you can download from wicid directly:
https://wicid.ukdataservice.ac.uk
TODO: convert this to using the training data and just mention that the individual
files are in the archive too.
"""
def quant2Install():
    #make a temporary data directory if it doesn't already exist
    if not os.path.exists(tmpDataDir):
        os.mkdir(tmpDataDir)
    if not os.path.exists(tmpDataDir+'/fromQUANT'):
        os.mkdir(tmpDataDir+'/fromQUANT')

    #first off the TObs trip flow matrices
    #mode 1 = road, mode 2 = bus, mode 3 = rail

    #NOTE: the Tij matrices always get downloaded as csharp binary dumps, converted
    #to numpy matrices, pickled and saved over the top of the original downloads

    #Tij road, mode 0
    ensureMatrixFileQUANTtoPickle(PyTObsRoadFilename, modelRunsDir, url_QUANT2_TijRoad_qcs, QUANTTObsRoadFilename)
    #Tij bus mode 1
    ensureMatrixFileQUANTtoPickle(PyTObsBusFilename, modelRunsDir, url_QUANT2_TijBus_qcs, QUANTTObsBusFilename)
    #Tij rail mode 2
    ensureMatrixFileQUANTtoPickle(PyTObsGBRailFilename, modelRunsDir, url_QUANT2_TijRail_qcs, QUANTTObsGBRailFilename)

    #now the cost files

    #Cij road mode 0
    ensureMatrixFileQUANTtoPickle(PyCijRoadMinFilename, modelRunsDir, url_QUANT2_CijRoadMin_qcs, QUANTCijRoadMinFilename)
    #Cij bus mode 1
    ensureMatrixFileQUANTtoPickle(PyCijBusMinFilename, modelRunsDir, url_QUANT2_CijBusMin_qcs, QUANTCijBusMinFilename)
    #Cij rail mode 2
    ensureMatrixFileQUANTtoPickle(PyCijGBRailMinFilename, modelRunsDir, url_QUANT2_CijGBRailMin_qcs, QUANTCijGBRailMinFilename)

    #and finally the zone codes lookup

    #zonecodes text file
    ensurePlainFile(ZoneCodesFilename, tmpDataDir, url_QUANT2_ZoneCodesText)

    #and that's all there is to it...
###

"""
Perform a clean of the matrices in the modelruns directory. This ONLY removes the files
specified in the list below, which are the trips, costs, zonecodes and raw travel to work
files.
"""
def clean():
    #todo: FIX!
    print('databuilder: clean')
    files = [
        TravelToWorkFilename,
        ZoneCodesFilename,
        PyCijRoadMinFilename, PyCijBusMinFilename, PyCijGBRailMinFilename,
        PyTObsAllFilename,
        PyTObsRoadFilename, PyTObsBusFilename, PyTObsGBRailFilename,
        #TObsFilename,
        #TObs21Filename, TObs22Filename,
        #TObs31Filename, TObs32Filename, TObs33Filename,
        QUANTCijRoadMinFilename, QUANTCijBusMinFilename, QUANTCijRailMinFilename
    ]
    fromQUANTDir = os.path.join(tmpDataDir,'fromQUANT')
    for file in files:
        path = os.path.join(tmpDataDir, file)
        if os.path.isfile(path):
            print('databuilder: deleting ',path) 
            #os.remove(path) todo: check it first!!!
        path = os.path.join(fromQUANTDir,file)
        if os.path.isfile(path):
            print('databuilder: deleting ',path) 
            #os.remove(path) todo: check it first!!!
###

################################################################################
# Main Program
# Install QUANT2 data
################################################################################


#clean() #if you want to remove all the files and start again from scratch e.g. change from QUANT 1 to 2

#make sure we have a model runs dir
if not os.path.exists(modelRunsDir):
    os.mkdir(modelRunsDir)

################################################################################
# QUANT 2 New Work
################################################################################

quant2Install()