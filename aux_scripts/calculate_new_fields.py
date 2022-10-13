#!/usr/bin/python

from netCDF4 import Dataset
import numpy
import sys

def calculate_fields(input_file, output_file, transform_wind_to_2m):

    fin = Dataset(input_file, mode='r', format="NETCDF4")
    fout = Dataset(output_file, mode='w', format="NETCDF4")
    
    times_in = fin.variables['time']
    lon_in = fin.variables['longitude']
    lat_in = fin.variables['latitude']

    dimtime = fout.createDimension("time", len(times_in))
    dimlat = fout.createDimension("latitude", len(lat_in))
    dimlon = fout.createDimension("longitude", len(lon_in))
    
    times = fout.createVariable("time", numpy.int32,("time",))
    latitudes = fout.createVariable("latitude",float,("latitude"))
    longitudes = fout.createVariable("longitude",float,("longitude",))

    times[:] = times_in[:]
    times.units = "hours since 1900-01-01 00:00:0.0"
    latitudes[:] = lat_in[:]
    longitudes[:] = lon_in[:]

    #Rain in mm
    #add_offset = fin.variables['tp'].add_offset
    #scale_factor = fin.variables['tp'].scale_factor
    tp_in = fin['tp'][:][:][:]#*scale_factor+add_offset
    tp_out = tp_in[:][:][:]*1000

    prop_out = fout.createVariable('tp', float, ("time", "latitude", "longitude",))
    prop_out[:, :, :] = tp_out
    prop_out.long_name = 'Total precipitation'
    prop_out.units = 'mm'
    
    #Total cloud cover
    #add_offset = fin.variables['tcc'].add_offset
    #scale_factor = fin.variables['tcc'].scale_factor
    tcc_in = fin['tcc'][:][:][:]#*scale_factor+add_offset
    tcc_out = tcc_in[:][:][:]

    prop_out = fout.createVariable('tcc', float, ("time", "latitude", "longitude",))
    prop_out[:, :, :] = tcc_out
    prop_out.long_name = 'Total cloud cover'
    prop_out.units = '(0-1)'
    
    #Solar radiation
    #add_offset = fin.variables['ssrd'].add_offset
    #scale_factor = fin.variables['ssrd'].scale_factor
    ssrd_in = fin['ssrd'][:][:][:]#*scale_factor+add_offset
    ssrd_out = ssrd_in[:][:][:]/3600

    prop_out = fout.createVariable('ssrd', float, ("time", "latitude", "longitude",))
    prop_out[:, :, :] = ssrd_out
    prop_out.long_name = 'Surface solar radiation downwards'
    prop_out.units = 'W**m-2'
    
    #Air temperature
    #add_offset = fin.variables['t2m'].add_offset
    #scale_factor = fin.variables['t2m'].scale_factor
    t2m_in = fin['t2m'][:][:][:]#*scale_factor+add_offset
    t2m_out = t2m_in[:][:][:]-273.15

    prop_out = fout.createVariable('t2m', float, ("time", "latitude", "longitude",))
    prop_out[:, :, :] = t2m_out
    prop_out.long_name = '2 metre temperature'
    prop_out.units = 'C'
    
    #Dewpoint temperature
    #add_offset = fin.variables['d2m'].add_offset
    #scale_factor = fin.variables['d2m'].scale_factor
    d2m_in = fin['d2m'][:][:][:]#*scale_factor+add_offset
    d2m_out = d2m_in[:][:][:]-273.15

    prop_out = fout.createVariable('d2m', float, ("time", "latitude", "longitude",))
    prop_out[:, :, :] = d2m_out
    prop_out.long_name = '2 metre dewpoint temperature'
    prop_out.units = 'C'
    
    #Relative humidity
    #Calculate relative humidity from dewpoint according to FAO
    ea = 0.6108*numpy.exp(17.27*d2m_out/(d2m_out+237.3))
    e0 = 0.6108*numpy.exp(17.27*t2m_out/(t2m_out+237.3))
    rel_hum = ea/e0
    
    rel_hum [rel_hum > 1] = 1

    prop_out = fout.createVariable('rh', float, ("time", "latitude", "longitude",))
    prop_out[:, :, :] = rel_hum
    prop_out.long_name = 'Relative humidity calculated according FAO'
    prop_out.units = '(0-1)'
    
    #Wind v component - transformed to 2m wind according FAO wind profile relationship
    #add_offset = fin.variables['v10'].add_offset
    #scale_factor = fin.variables['v10'].scale_factor
    v10_in = fin['v10'][:][:][:]#*scale_factor+add_offset
    if transform_wind_to_2m == 1:
        v_out = v10_in*4.87/numpy.log(67.8*10-5.42)
        name_variable = 'v2'
        long_name_variable = '2 metre V wind component'
    else:
        v_out = v10_in[:][:][:]
        name_variable = 'v10'
        long_name_variable = '10 metre V wind component'

    prop_out = fout.createVariable(name_variable, float, ("time", "latitude", "longitude",))
    prop_out[:, :, :] = v_out
    prop_out.long_name = long_name_variable
    prop_out.units = 'm s**-1'
    
    #Wind u component - transformed to 2m wind according FAO wind profile relationship
    #add_offset = fin.variables['u10'].add_offset
    #scale_factor = fin.variables['u10'].scale_factor
    u10_in = fin['u10'][:][:][:]#*scale_factor+add_offset
    if transform_wind_to_2m == 1:
        u_out = u10_in*4.87/numpy.log(67.8*10-5.42)
        name_variable = 'u2'
        long_name_variable = '2 metre U wind component'
    else:
        u_out = u10_in[:][:][:]
        name_variable = 'u10'
        long_name_variable = '10 metre U wind component'

    prop_out = fout.createVariable(name_variable, float, ("time", "latitude", "longitude",))
    prop_out[:, :, :] = u_out
    prop_out.long_name = long_name_variable
    prop_out.units = 'm s**-1'
    
    fin.close()
    fout.close()

    return