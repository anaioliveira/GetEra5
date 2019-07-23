#!/usr/bin/python

from netCDF4 import Dataset
import numpy
import sys

def calculate_fields(input_file, output_file):

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
    tp_in = fin['tp'][:][:][:]
    tp_out = tp_in[:][:][:]*1000

    prop_out = fout.createVariable('tp', float, ("time", "latitude", "longitude",))
    prop_out[:, :, :] = tp_out
    prop_out.long_name = 'Total precipitation'
    prop_out.units = 'mm'
    
    #Total cloud cover
    tcc_in = fin['tcc'][:][:][:]
    tcc_out = tcc_in[:][:][:]

    prop_out = fout.createVariable('tcc', float, ("time", "latitude", "longitude",))
    prop_out[:, :, :] = tcc_out
    prop_out.long_name = 'Total cloud cover'
    prop_out.units = '(0-1)'
    
    #Solar radiation
    ssrd_in = fin['ssrd'][:][:][:]
    ssrd_out = ssrd_in[:][:][:]/3600

    prop_out = fout.createVariable('ssrd', float, ("time", "latitude", "longitude",))
    prop_out[:, :, :] = ssrd_out
    prop_out.long_name = 'Surface solar radiation downwards'
    prop_out.units = 'W**m-2'
    
    #Air temperature
    t2m_in = fin['t2m'][:][:][:]
    t2m_out = t2m_in[:][:][:]-273.15

    prop_out = fout.createVariable('t2m', float, ("time", "latitude", "longitude",))
    prop_out[:, :, :] = t2m_out
    prop_out.long_name = '2 metre temperature'
    prop_out.units = 'C'
    
    #Dewpoint temperature
    d2m_in = fin['d2m'][:][:][:]
    d2m_out = d2m_in[:][:][:]-273.15

    prop_out = fout.createVariable('d2m', float, ("time", "latitude", "longitude",))
    prop_out[:, :, :] = d2m_out
    prop_out.long_name = '2 metre dewpoint temperature'
    prop_out.units = 'C'
    
    #Relative humidity
    #Calculate relative humidity from dewpoint - http://andrew.rsmas.miami.edu/bmcnoldy/Humidity.html
    #RH: =EXP((17.625*DEWPOINT)/(243.04+DEWPOINT))/EXP((17.625*TEMPERATURE)/(243.04+TEMPERATURE)) - graus celsius
    rel_hum = numpy.exp((17.625*d2m_out)/(243.04+d2m_out))/numpy.exp((17.625*t2m_out)/ \
                                                                           (243.04+t2m_out))

    rel_hum [rel_hum > 1] = 1

    prop_out = fout.createVariable('rh', float, ("time", "latitude", "longitude",))
    prop_out[:, :, :] = rel_hum
    prop_out.long_name = 'Relative humidity from air and dewpoint temperature'
    prop_out.units = '(0-1)'
    
    ##Wind velocity
    #wind_in = fin['wind'][:][:][:]
    #wind_out = wind_in[:][:][:]
    #
    #prop_out = fout.createVariable('wind', float, ("time", "latitude", "longitude",))
    #prop_out[:, :, :] = wind_out
    #prop_out.long_name = '10 metre wind speed'
    #prop_out.units = 'm s**-1'
    
    #Wind v component
    v10_in = fin['v10'][:][:][:]
    v10_out = v10_in[:][:][:]

    prop_out = fout.createVariable('v10', float, ("time", "latitude", "longitude",))
    prop_out[:, :, :] = v10_out
    prop_out.long_name = '10 metre V wind component'
    prop_out.units = 'm s**-1'
    
    #Wind u component
    u10_in = fin['u10'][:][:][:]
    u10_out = u10_in[:][:][:]

    prop_out = fout.createVariable('u10', float, ("time", "latitude", "longitude",))
    prop_out[:, :, :] = u10_out
    prop_out.long_name = '10 metre U wind component'
    prop_out.units = 'm s**-1'
    
    fin.close()
    fout.close()

    return