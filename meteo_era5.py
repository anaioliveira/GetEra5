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
sys.path.insert(0, '/aux_scripts')
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

def getERA5(date, parameters):

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

    begin_date = "31/12/2008"
    end_date = "31/12/2008"
    parameters = ['10m_u_component_of_wind','10m_v_component_of_wind','10m_wind_speed','2m_dewpoint_temperature','2m_temperature','surface_solar_radiation_downwards','total_cloud_cover','total_precipitation']
    window = [1., 179., 350., 355.] #S/N/W/E
    casestudy_grid = 'Galicia_Meteo.dat'
    #######
    get_meteo_files = 0
    convert_grib_to_netcdf = 0

    #Define folders
    work_folder = ''
    original_netcdf_ERA5 = '/home/aoliveira/disk_storage/ERA5/'
    interpolated_files = ''
    convert_folder = '/ConvertToHDF5/'

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
            getERA5(date, parameters)

            #Convert GRIB to NetCDF
            if convert_grib_to_netcdf == 1:
                print ('\x1b[0;36;40m Converting file from GRIB to NEtCDF... \x1b[0m')
                subprocess.call('ncl_convert2nc ' + date + '.grib', shell=True)
        
            subprocess.call('mv ' + date + '.nc ' + original_netcdf_ERA5 + date + '.nc', shell=True)

        shutil.copy(original_netcdf_ERA5 + date + '.nc', work_folder + date + '.nc')
        
        ##Clip NetCDF file
        #if window[2] < 0:
        #    window[2] = 360 - window[2]
        #if window[3] < 0:
        #    window[3] = 360 - window[3]
        
        print ('\x1b[0;36;40m Clipping NetCDF file... \x1b[0m')
        subprocess.call('ncks -d latitude,' + str(window[0]) + ',' + str(window[1]) + ' -d longitude,' + \
                str(window[2]) + ',' + str(window[3]) + ' ' + work_folder + date + '.nc -O ' + work_folder + date + '.nc', shell=True)

        print ('\x1b[0;36;40m Making adjustments in fields... \x1b[0m')
        #Modify longitude coordinates to [-180,180]
        change_coordinates.change_coord(work_folder + date + '.nc')

        #Calculate new_fields
        calculate_new_fields.calculate_fields(work_folder + date + '.nc', work_folder + date + '_.nc')

        #Get father grid
        get_father_grid(work_folder + date + '_.nc')

        #Convert NetCDF to HDF5 (with MOHID tool)
        os.chdir(convert_folder)
        print ('\x1b[0;36;40m Converting NetCDF to HDF5... \x1b[0m')
        write_converttohdfaction_file.write_file(convert_folder + convert_netcdftohdf, work_folder + date + '_.nc', 'convert')
        os.system(convert_folder + "ConvertToHDF5.exe")

        #Interpolate HDF5 file
        print ('\x1b[0;36;40m Interpolating HDF5... \x1b[0m')
        write_converttohdfaction_file.write_file(convert_folder + interpolate, work_folder + date + '_.hdf5', 'interpolate', actual_date_py, casestudy_grid)
        os.system(convert_folder + "ConvertToHDF5.exe")
        subprocess.call('mv ' + work_folder + date + '__interpolated.hdf5 ' + interpolated_files + date.replace('-', '') + '.hdf5', shell=True)

        os.chdir(work_folder)
        subprocess.call('rm *.hdf5 *.nc *.grib ', shell=True)

        actual_date_py += relativedelta(days=1)