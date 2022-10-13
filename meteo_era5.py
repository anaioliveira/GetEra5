##################################################################
#
#     Developed by: Ana Isabel Oliveira
#     Project: HazRunoff
#     Date: MARETEC IST, 28/06/2018
#
##################################################################

#!/usr/bin/python

import sys
import os
import shutil
import datetime
from dateutil.relativedelta import relativedelta
import subprocess
import numpy
from netCDF4 import Dataset
import cdsapi
sys.path.insert(0, 'E:/Omega/Meteo/Script/aux_scripts')
import change_coordinates, calculate_new_fields, write_converttohdfaction_file

def get_dates_py(d_str):

    d_py = datetime.datetime.strptime(d_str, "%d/%m/%Y")

    return d_py

def get_date_string(d_py):

    d_str = d_py.strftime('%d/%m/%Y')

    return d_str

def change_date_to_era5(date_to_print):

    d1 = date_to_print.split("/")
    day = d1[0]
    month = d1[1]
    year = d1[2]
    d_era5 = year + '-' + month + '-' +  day

    return d_era5

def getERA5(date, parameters, w):

    year = date.split('-')[0]
    month = date.split('-')[1]
    day = date.split('-')[2]

    c = cdsapi.Client()
    r = c.retrieve(
        'reanalysis-era5-single-levels', {
                'variable'    : parameters,
                'product_type': 'reanalysis',
                'year'        : year,
                'month'       : month,
                'day'         : day,
                'time'        : [
                    '00:00','01:00','02:00',
                    '03:00','04:00','05:00',
                    '06:00','07:00','08:00',
                    '09:00','10:00','11:00',
                    '12:00','13:00','14:00',
                    '15:00','16:00','17:00',
                    '18:00','19:00','20:00',
                    '21:00','22:00','23:00'
                ],
        'area': w,
                'format'      : 'netcdf'
        })
    r.download(date + '.nc')

    return

def get_father_grid(hdf_input_file):

    fin = Dataset(hdf_input_file, mode='r', format="NETCDF4")

    lat = fin.variables['latitude'][:]
    lon = fin.variables['longitude'][:]

    lat = numpy.sort(lat)[::-1]
    lon = numpy.sort(lon)

    x = []
    for i in range(len(lon)-1):
        aux = (lon[i]+lon[i+1])/2
        x.append(aux)

    y = []
    for j in range(len(lat) - 1):
        aux = (lat[j]+lat[j + 1]) / 2
        y.append(aux)

    fout = open('ERA5_grid.dat', 'w')

    fout.writelines('PROJ4_STRING           : +proj=longlat +datum=WGS84 +no_defs\n')
    fout.writelines('ILB_IUB                : 1 ' + str(len(y)-1) + '\n')
    fout.writelines('JLB_JUB                : 1 ' + str(len(x)-1) + '\n')
    fout.writelines('COORD_TIP              : 4\n')
    fout.writelines('ORIGIN                 : 0 0\n')
    fout.writelines('GRID_ANGLE             : 0.0000000E+00\n')
    fout.writelines('LATITUDE               : 0\n')
    fout.writelines('LONGITUDE              : 0\n')
    fout.writelines('FILL_VALUE             : -99\n\n')
    fout.writelines('<BeginXX>\n')
    for i in range(len(x)):
        x_ = str(x[i])
        fout.writelines(x_ + '\n')
    fout.writelines('<EndXX>\n')
    fout.writelines('<BeginYY>\n')
    for j in range(len(y)):
        y_ = str(y[j])
        fout.writelines(y_ + '\n')
    fout.writelines('<EndYY>\n')
    fout.writelines('<BeginGridData2D>\n')
    for i in range(len(x)-1):
        for j in range(len(y)-1):
            fout.writelines('1\n')
    fout.writelines('<EndGridData2D>')

    fout.close()
    fin.close()

    return

############# MAIN FUNCTION #############
if __name__ == '__main__':

    begin_date = "01/01/2001"
    end_date = "03/01/2001"
    parameters = ['10m_u_component_of_wind', '10m_v_component_of_wind', '2m_dewpoint_temperature','2m_temperature', 'surface_solar_radiation_downwards', 'total_cloud_cover','total_precipitation']
    window = [45, -20, 35, 0] #N/W/S/E
    casestudy_grid = 'Maranhao.dat'
    #######
    get_meteo_files = 0
    convert_and_interpolate = 1
    transform_wind_to_2m = 1

    #Define folders
    work_folder = 'E:/Omega/Meteo/Script/'
    original_netcdf_ERA5 = 'E:/Omega/Meteo/Script/ERA5OriginalFiles/'
    interpolated_files = 'E:/Omega/Meteo/Script/InterpolatedFiles/'
    convert_folder = 'E:/Omega/Meteo/Script/ConvertToHDF5_Convert/'
    interpolate_folder = 'E:/Omega/Meteo/Script/ConvertToHDF5_Interpolate/'

    #Define template files location
    convert_netcdftohdf = 'ConvertToHDF5Action_NetCDFToHDF.dat'
    interpolate = 'ConvertToHDF5Action_Interpolate.dat'

    # Initialize variables
    end_date_py = get_dates_py(end_date)
    actual_date_py = get_dates_py(begin_date)

    #Start
    while actual_date_py <= end_date_py:
        date_to_print = get_date_string(actual_date_py)

        print
        print('\x1b[0;33;40m' + "# # # # # # # # # # # # # # # # # # # #" + '\x1b[0m')
        print('\x1b[0;33;40m' + "        Doing " + date_to_print + " ..." + '\x1b[0m')
        print('\x1b[0;33;40m' + "# # # # # # # # # # # # # # # # # # # #" + '\x1b[0m')

        date = change_date_to_era5(date_to_print)
        # Get ERA 5 file
        if get_meteo_files == 1:
            getERA5(date, parameters, window)
            shutil.move(date + '.nc ', original_netcdf_ERA5 + date + '.nc')

        # Get ERA 5 file
        if convert_and_interpolate == 1:
            shutil.copy(original_netcdf_ERA5 + date + '.nc', work_folder + date + '.nc')

            print ('\x1b[0;36;40m Making adjustments in fields... \x1b[0m')
            #Modify longitude coordinates to [-180,180]
            change_coordinates.change_coord(work_folder + date + '.nc')

            #Calculate new_fields
            calculate_new_fields.calculate_fields(work_folder + date + '.nc', work_folder + date + '_.nc', transform_wind_to_2m)

            #Get father grid
            if actual_date_py == get_dates_py(begin_date):
                get_father_grid(work_folder + date + '_.nc')

            #Convert NetCDF to HDF5 (with MOHID tool)
            os.chdir(convert_folder)
            print ('\x1b[0;36;40m Converting NetCDF to HDF5... \x1b[0m')
            write_converttohdfaction_file.write_file(convert_folder + convert_netcdftohdf, work_folder + date + '_.nc', 'convert')
            os.system(convert_folder + "ConvertToHDF5.exe")

            #Interpolate HDF5 file
            os.chdir(interpolate_folder)
            print ('\x1b[0;36;40m Interpolating HDF5... \x1b[0m')
            write_converttohdfaction_file.write_file(interpolate_folder + interpolate, work_folder + date + '_.hdf5', 'interpolate', actual_date_py, casestudy_grid)
            os.system(interpolate_folder + "ConvertToHDF5.exe")
            shutil.move(work_folder + date + '__interpolated.hdf5', interpolated_files + date.replace('-', '') + '.hdf5')
            sys.exit()

            #Delete auxiliar files
            os.chdir(work_folder)
            for item in os.listdir(work_folder):
                if item.endswith(".hdf5") or item.endswith(".nc"):
                    os.remove(os.path.join(work_folder, item))

        actual_date_py += relativedelta(days=1)