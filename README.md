# DQConvert

## Description: 
#### The main purpose of this script is to access the gwf files, retrieve data quality flag
#### information and output the information to 4 .dat files.
#### Mervyn Chan 2019
 

### Usage:
#### If the data quality flag file is K-K1_C-1245460544-32.gwf, with data quality flag information written in channel: K1:DET-DQ_STATE_VECTOR, use the following command:

#####                  DQConvert -gwf K-K1_C-1245460544-32.gwf -ch K1:DET-DQ_STATE_VECTOR -SR 16 -DCf CAT

#### for multiplie files, e.g. four consecutive files: K-K1_C-1245460544-32.gwf, K-K1_C-1245460576-32.gwf K-K1_C-1245460608-32.gwf K-K1_C-1245460640-32.gwf, 
with data quality flag information written in channel: K1:DET-DQ_STATE_VECTOR

##### DQConvert -gwf K-K1_C-1245460{544-640}-32.gwf -ch K1:DET-DQ_STATE_VECTOR -SR 16 -DCf CAT

#### -gwf: a string for the name(s) of the .gwf files whose data quality flag information is to be read and written into .dat files.
####         If analysing a single .gwf file is desired, the -gwf string should just be the name of the .gwf file including the extension.
####         If analysing multiple files is desired, the -gwf string should indicate all the file names using the following format:
####         K-K1_C-1245460{544-640}-32.gwf, where the first file is K-K1_C-1245460544-32.gwf and the last file is K-K1_C-1245460640-32.gwf.
####         All the files should have the same sampling rate, all the file in between 1245460544 and 1245460640 should be present.
         
####   -ch : the channel for reading the data quality flag information from the gwf files.
####   -SR : the samepling rate of the data quality flags.
####   -DCf: the name and path for the output data category flag files. e.g. CAT. The output files will then be CAT1;CAT2;CAT3;CAT4
