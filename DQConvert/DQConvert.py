#!/usr/bin/env python

"""
The main purpose of this script is to access gwf files, retrieve data quality flag
information and output the information to 4 .dat files.

Mervyn Chan 2019
"""

"""Importing Necessary Modules"""

from gwpy import timeseries
#import matplotlib
#matplotlib.use('Qt4Agg')
#import matplotlib.pyplot as plt
import numpy as np
import argparse
import re
import os




parser = argparse.ArgumentParser()
parser.add_argument("-gwf", "--GWF", dest = 'gwf', required=True,  type=str, help="The name of the frame file.")
parser.add_argument("-ch", "--channel", dest = 'ch', required=True,  type=str, help="The channel name for the Data Quality Vector.")
parser.add_argument("-SR", "--sample-rate", dest = 'SR', required=True, type=float, help="The sampling rate of the Data Quality Vector.")
parser.add_argument("-DCf", "--Data-catagory-file-names", dest = 'DCf', required=True,  type=str, help="The name for the data catagory flag files. The final output will be appended with a number depending on the catagory.")


"""-gwf: a string for the name(s) of the .gwf files whose data quality flag information is to be read and written into .dat files.
         If analysing a single .gwf file is desired, the -gwf string should just be the name of the .gwf file including the extension.
         If analysing multiple files is desired, the -gwf string should indicate all the file names using the following format:
         K-K1_C-1245460{544-640}-32.gwf, where the first file is K-K1_C-1245460544-32.gwf and the last file is K-K1_C-1245460640-32.gwf.
         All the files should have the same sampling rate, all the file in between 1245460544 and 1245460640 should be present.
         
   -ch : the channel for reading the data quality flag information from the gwf files.
   -SR : the sampling rate of the data quality flags.
   -DCf: the name and path for the output data category flag files. e.g. CAT. The output files will then be CAT1;CAT2;CAT3;CAT4"""

inputs = parser.parse_args()



gwf_input = inputs.gwf






def channels(bit):
    """This function is for when one wishes to know which channel is the reason that the data does not pass the quality check. 
       It is currently not used. """
    
    return {
        0 : 'Odd Parity',
        1 : 'Lock Flag',
        2 : 'SDF Flag',
        3 : 'Science mode',
        4 : 'OMC Overflow',
        5 : 'MCE Overflow',
        6 : 'ETMY Overflow',
        7 : 'Stock Injection',
        8 : 'CBC Injection',
        9: 'Burst Injection',
        10: 'DET Injection',
        11: 'CW Injection',
    }[bit]

def checkdq(CAT, temp):
    
    """This function checks if there are any elements that are common between a certain category and the input detector quality vector"""
    """If there is any common elements. It means that the data quality has issue in at least one of the channels that belong to the category."""
    
    
    cat_set = set(CAT) 
    temp_set = set(temp) 
    
    if len(cat_set.intersection(temp_set)) > 0: 
        return True  
    return False    

def markdq(common, CAT_switch, CAT_GPST, ts, index, gwf_file_index, length):
    
    """This function converts the data quality flag information to data category flag."""
    
    if common == True and CAT_switch == 0:
        CAT_GPST.append(ts[index])
        CAT_switch = 1
        
    if common == False and CAT_switch == 1:
        
        CAT_GPST.append(ts[index])
        CAT_switch = 0
       
    if common == True and (index + 1) * (gwf_file_index + 1) == length and len(CAT_GPST) % 2 == 1:
        CAT_GPST.append(ts[index])
        CAT_switch = 0
            
    return CAT_switch, CAT_GPST             


def wdcf(DQfname, cat_gpst):
    """This function writes the data catagory to a file."""
    f = open(DQfname,"w")
    
    for i in range(len(cat_gpst) / 2):
        
        f.write("%s\t%s\n"%(cat_gpst[2 * i], cat_gpst[2 * i + 1]))
    if cat_gpst != []:
	f.write('\n')
    f.close()




def main():

    """Checking if there are multiple input gwf files. If "{" exists in the input string, then it is a string indicating multiple gwf files. """
    if '{' in gwf_input:
        bracket1_index = gwf_input.index('{')

        if '}' not in gwf_input or '{' not in gwf_input:
            raise Exception('There is "{" in the input gwf file name but "}" is missing.')

    if '}' in gwf_input:
        bracket2_index = gwf_input.index('}')
        if '}' not in gwf_input or '{' not in gwf_input:
            raise Exception('There is "}" in the input gwf file name but "{" is missing.')

        if '-' not in gwf_input[bracket1_index:bracket2_index + 1]:
            raise Exception('There should be "-" in between the start of the GPS times and the end of the GPS times.')

        """Locating the position of the symbol '-' in the string splitting the files. """ 
        splitter_index = gwf_input[bracket1_index:bracket2_index + 1].index('-')
        splitter_index = splitter_index + bracket1_index   

        if len(gwf_input[bracket1_index + 1 : splitter_index]) != len(gwf_input[splitter_index + 1 : bracket2_index]):
            raise Exception('The format of the input gwf name for multiplie files is not correct.')

        file_begin = gwf_input[bracket1_index + 1 : splitter_index]
        file_end = gwf_input[splitter_index + 1 : bracket2_index]

        if file_begin.isdigit() == True:
            file_begin = int(file_begin)
        else:
            raise Exception('The start of the input gwf file is not an integer.')


        if file_end.isdigit() == True:
            file_end  = int(file_end)
        else:
            raise Exception('The end of the input gwf file is not an integer.')

        duration_index = len(gwf_input) - 1 - gwf_input[::-1].index('-')
        dot_index = gwf_input.index('.')
        separation = gwf_input[duration_index + 1: dot_index]
        No_of_gwf_files = (file_end - file_begin) / int(separation) + 1

    extension_index = gwf_input.index('.') 

    if gwf_input[extension_index + 1 :].lower() != 'gwf':
        raise Exception('Please check the extension of the input gwf files. It has to be "gwf", case insensitive.')
    else:
        extension = gwf_input[extension_index + 1 :]


    """If there is no '{', then the input string indicates only one file."""    
    if '{' not in gwf_input:
        exists = os.path.isfile(gwf_input)
        if exists == False:
            raise Exception('There is no such a file as the input gwf file.')
        else:
            No_of_gwf_files = 1



    """Setting the basic parameters from inputs"""
    SR = inputs.SR
    dt = 1.0 / SR

    """The path and names for saving data category flags. """
    DQfname_for_CAT1 = ''.join([inputs.DCf, '1', '.in'])
    DQfname_for_CAT2 = ''.join([inputs.DCf, '2', '.in'])
    DQfname_for_CAT3 = ''.join([inputs.DCf, '3', '.in'])
    DQfname_for_CAT4 = ''.join([inputs.DCf, '4', '.in'])

    """List used to save the GPS time at which the data is not usable because of issus that belongs to a certain category."""
    CAT1_GPST = []
    CAT2_GPST = []
    CAT3_GPST = []
    CAT4_GPST = []

    """The Categories"""
    CAT1 = [1, 2, 3]
    CAT2 = [4, 5, 6]
    CAT3 = [7]
    CAT4 = [8, 9, 10, 11]


    CAT1_switch = 0
    CAT2_switch = 0
    CAT3_switch = 0
    CAT4_switch = 0




    
    
    
    """Checking whether multiple files or one file need analysing"""
    if 'file_begin' in locals():
        file_count = file_begin

    """Looping over the number of gwf files"""    
    for i in range(No_of_gwf_files):    
        if 'bracket1_index' in locals():

            gwf_file = ''.join((gwf_input[0:bracket1_index], str(file_count),  gwf_input[bracket2_index + 1 :]))
            file_count += int(separation)

        else:
            gwf_file = gwf_input

        #print(gwf_file)


        if os.path.isfile(gwf_file) == True:
            """Reading the input frame files"""
            bitdq = timeseries.TimeSeries.read(gwf_file, inputs.ch)
            length = len(bitdq)
            GPST = np.array(bitdq.times[0])
            ts = np.arange(length) * dt + GPST
            duration = length / float(SR)


        else:
            raise Exception('There is no such a file as %s.'%(gwf_file))

        length = len(bitdq)

        for j in range(length):

            """Temporary vector used to save the binary numbers.
            Convert data quality flag from deximal to binaries"""
            binaries = bin(int(bitdq[j]))[2:].zfill(16)         

            #binaries = bin(int(0)).zfill(16)
            #if j == 65:
            #    binaries = bin(int(65535)).zfill(16)

            #if j == 110:
            #    binaries = bin(int(65535)).zfill(16)    

            #if j == 200:
            #    binaries = bin(int(65535)).zfill(16)    

            #if j == 235:
            #    binaries = bin(int(65535)).zfill(16)   
                #print(CAT1_GPST)    
            #print(ts[65], ts[110], ts[200], ts[235] )
            """If there is any zero in the binary, it means the data is affected."""
            temp = [x for x, y in enumerate(reversed(binaries)) if y == '0']

            """Check if there is any issue from category 1"""
            common = checkdq(CAT1, temp)

            CAT1_switch, CAT1_GPST = markdq(common, CAT1_switch, CAT1_GPST, ts, j, i, No_of_gwf_files * length)

            """Check if there is any issue from category 2"""
            common = checkdq(CAT2, temp)    

            CAT2_switch, CAT2_GPST = markdq(common, CAT2_switch, CAT2_GPST, ts, j, i, No_of_gwf_files * length)    

            """Check if there is any issue from category 3"""
            common = checkdq(CAT3, temp)  

            CAT3_switch, CAT3_GPST = markdq(common, CAT3_switch, CAT3_GPST, ts, j, i, No_of_gwf_files * length)  

            """Check if there is any issue from category 4"""
            common = checkdq(CAT4, temp)  

            CAT4_switch, CAT4_GPST = markdq(common, CAT4_switch, CAT4_GPST, ts, j, i, No_of_gwf_files * length)

    #if CAT1_GPST !=[]:
    wdcf(DQfname_for_CAT1, CAT1_GPST)    
    #if CAT2_GPST !=[]:
    wdcf(DQfname_for_CAT2, CAT2_GPST)    
    #if CAT3_GPST !=[]:
    wdcf(DQfname_for_CAT3, CAT3_GPST)    
    #if CAT4_GPST !=[]:    
    wdcf(DQfname_for_CAT4, CAT4_GPST)        




