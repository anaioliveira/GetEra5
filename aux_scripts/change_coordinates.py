#!/usr/bin/python

from netCDF4 import Dataset

def change_coord(input_file):

    fin = Dataset(input_file, mode='r+', format="NETCDF4")

    lon = fin.variables['longitude']

    for i in range(len(lon)):
        if fin.variables['longitude'][i] > 180:
            fin.variables['longitude'][i] = fin.variables['longitude'][i] - 360

    fin.close()

    return