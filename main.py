#!/usr/bin/env python3
"""
 main.py
"""

import os.path
import numpy as np
from globals import *
from utils import loadMatrix, saveMatrix, loadQUANTCSV
#from zonecodes import ZoneCodes #you need loadZoneLookup function from this
from models.SingleOrigin import SingleOrigin


###############################################################################

def main():
    print("QUANT_RUBICON")

    #======This is model calibration======
    #load TObs x 3, cij x 3 and calibrate betas
    #MODES: 1=road, 2=bus, 3=rail OR 0,1,2 if we're zero based
    TObs1 = loadMatrix(os.path.join(modelRunsDir,PyTObsRoadFilename))
    TObs2 = loadMatrix(os.path.join(modelRunsDir,PyTObsBusFilename))
    TObs3 = loadMatrix(os.path.join(modelRunsDir,PyTObsGBRailFilename))
    TObs = [TObs1, TObs2, TObs3]
    Cij1 = loadMatrix(os.path.join(modelRunsDir,PyCijRoadMinFilename))
    Cij2 = loadMatrix(os.path.join(modelRunsDir,PyCijBusMinFilename))
    Cij3 = loadMatrix(os.path.join(modelRunsDir,PyCijGBRailMinFilename))
    Cij = [Cij1,Cij2,Cij3]
    print("loaded matrices")
    #set up model information to calibrate
    model = SingleOrigin()
    model.TObs = TObs
    model.Cij=Cij
    model.isUsingConstraints=False
    print("calibrate model")
    model.run()
    print("beta: road="+str(model.Beta[0])+" bus="+str(model.Beta[1])+" rail="+str(model.Beta[2]))
    #rodo: goodness of fit?

###############################################################################


if __name__ == '__main__':
    main()