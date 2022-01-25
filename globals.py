"""
Global definitions needed across the whole project
"""

modelRunsDir = 'model-runs'

TravelToWorkFilename = 'wu03ew_msoa.csv'
ZoneCodesFilename = 'ZoneCodesText.csv'
#raw data training files - these are used to create the PyCijRoad, PyTObsRoad etc
TrainingDataRoadCSVFilename = 'trainingdata_road.csv'
TrainingDataBusCSVFilename = 'trainingdata_bus.csv'
TrainingDataGBRailCSVFilename = 'trainingdata_gbrail.csv'
#Python matrices used for training (min=minutes, Cij=cost, TObs=people flow)
#these are Python pickle
PyCijRoadMinFilename = 'Py_Cij_road.bin' #mode 1
PyCijBusMinFilename = 'Py_Cij_bus.bin' #mode 2
PyCijGBRailMinFilename = 'Py_Cij_gbrail.bin' #mode 3
PyTObsAllFilename = 'Py_TObs_all.bin' #TObs.bin
PyTObsRoadFilename = 'Py_TObs_road.bin' #TObs3_1.bin
PyTObsBusFilename = 'Py_TObs_bus.bin' #TObs3_2.bin
PyTObsGBRailFilename = 'Py_TObs_gbrail.bin' #TObs3_3.bin

#matrix filenames - these are C# matrix dumps direct from QUANT
#ONLY used in models e.g. TObs31Filename = PyTobsRoadFilename
#call these all QUANTTObs... as they are origina TObs etc files from QUANT C#
#QUANTTObsFilename = 'TObs.bin' #1 mode
#QUANTTObs21Filename = 'TObs2_1.bin' #2 mode
#QUANTTObs22Filename = 'TObs2_2.bin'
#QUANTTObs31Filename = 'TObs3_1.bin' #3 mode
#QUANTTObs32Filename = 'TObs3_2.bin'
#QUANTTObs33Filename = 'TObs3_3.bin'
QUANTTObsRoadFilename = 'TObs3_1.bin'
QUANTTObsBusFilename = 'TObs3_2.bin'
QUANTTObsGBRailFilename = 'TObs3_3.bin'
#cost matrix names
QUANTCijRoadMinFilename = 'dis_roads_min.bin' #these are C# matrix dumps
QUANTCijBusMinFilename = 'dis_bus_min.bin'
QUANTCijGBRailMinFilename = 'dis_gbrail_min.bin'
PyCijRoadMinFilename = 'Py_Cij_road_min.bin' #these are Python pickle
PyCijBusMinFilename = 'Py_Cij_bus_min.bin'
PyCijGBRailMinFilename = 'Py_Cij_gbrail_min.bin'