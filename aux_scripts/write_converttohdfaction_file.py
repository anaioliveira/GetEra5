#!/usr/bin/python

import datetime
from dateutil.relativedelta import relativedelta

def manipulate_dates(date, id):


    date_ = str(date)
    date__ = date_.split(' ')[0]
    year = date__.split('-')[0]
    month = date__.split('-')[1]
    day = date__.split('-')[2]

    if id == 1:
        str_date = year + ' ' + month + ' ' + day + ' ' + '00 00 00'
    elif id == 2:
        str_date = year + ' ' + month + ' ' + day + ' ' + '23 00 00'
    else:
        str_date = year + ' ' + month + ' ' + day + ' ' + '00 00 00'

    return str_date

def write_convert_file(template_file, input_file):

    #Input file
    fin = open(template_file, 'r')

    #Output file
    file_to_write = template_file.rsplit('/', 1)[0] + '/ConvertToHDF5Action.dat'
    fout = open(file_to_write, 'w')

    lines = fin.readlines()

    for l in lines:
        if 'output_hdf_file' in l:
            output_file = input_file.replace('nc', 'hdf5')
            l = l.replace('output_hdf_file', output_file)
            fout.writelines(l)
        elif 'input_nc_file' in l:
            l = l.replace('input_nc_file', input_file)
            fout.writelines(l)
        else:
            fout.writelines(l)

    fin.close()
    fout.close()

    return

def write_interpolate_file(template_file, input_file, begin_date, grid):

    # Input file
    fin = open(template_file, 'r')

    # Output file
    file_to_write = template_file.rsplit('/', 1)[0] + '/ConvertToHDF5Action.dat'
    fout = open(file_to_write, 'w')

    lines = fin.readlines()

    for l in lines:
        if 'output_file' in l:
            output_file = input_file.replace('.hdf5', '_interpolated.hdf5')
            l = l.replace('output_file', output_file)
            fout.writelines(l)
        elif 'input_file' in l:
            l = l.replace('input_file', input_file)
            fout.writelines(l)
        elif 'begin_date' in l:
            begin_date_str = manipulate_dates(begin_date, 1)
            l = l.replace('begin_date', begin_date_str)
            fout.writelines(l)
        elif 'end_date' in l:
            end_date_str = manipulate_dates(begin_date, 2)
            l = l.replace('end_date', end_date_str)
            fout.writelines(l)
        elif 'father_grid' in l:
            l = l.replace('father_grid', '../ERA5_grid.dat')
            fout.writelines(l)
        elif 'casestudy_grid' in l:
            l = l.replace('casestudy_grid', grid)
            fout.writelines(l)
        else:
            fout.writelines(l)

    fin.close()
    fout.close()

    return

def write_file(template_file, input_file, option, *args):

    if option == 'convert':
        write_convert_file(template_file, input_file)
    elif option == 'interpolate':

        i = 0
        for arg in args:
            if i == 0:
                start_date = arg
            elif i == 1:
                grid = arg
            else:
                pass
            i = i + 1

        write_interpolate_file(template_file, input_file, start_date, grid)
    else:
        print ('\x1b[1;31;40m' + 'Error!!! Neither convertion or interpolation was selected!' + '\x1b[0m')

    return