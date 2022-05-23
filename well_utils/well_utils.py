import pandas as pd 
import numpy as np 
import os 

import matplotlib.pyplot as plt 
from collections import Counter

 


sections = ['~Version','~Well', '~Curve', '~Ascii' ]
data_section_keywords = ['~Ascii' ]
curves_section_keywords = ['~Curve' ]
well_section_keywords = ['~Well' ]


class WellData( pd.DataFrame ):
    
    #construct an instance just as you would construct a dataframe 
    def __init__( self, df ,well_info  ): 
        super().__init__( df )    
        self.well_info = well_info 
        
    
    #this is just a trick to make the attributes copiable 
    def copy( self ):
        return Derived( super().copy(), self.well_info.copy() )
        
    @property 
    def log_names(self):
        return self.columns
    
    @property
    def log_units(self):
        d = {}
        for name in self.log_names:
            if name in self.well_info['units']:
                d[name] = self.well_info['units'][name]
            else:
                d[name] = '_'
                
        return d; 
    
    
                

class LasParser( ):

    @staticmethod
    def is_comment_line( line ): return line.strip().startswith('#')

    @staticmethod
    def is_section_line( line ):
        for section_keyword in sections:
            if section_keyword in line:
                return True
        return False 

    @staticmethod
    def is_data_section_line( line ):
        for section_keyword in data_section_keywords:
            if section_keyword in line:
                return True
        return False 

    @staticmethod
    def is_curves_section_line( line ):
        for section_keyword in curves_section_keywords:
            if section_keyword in line:
                return True
        return False 

    @staticmethod
    def is_well_section_line( line ):
        for section_keyword in well_section_keywords:
            if section_keyword in line:
                return True
        return False 

    @staticmethod
    def exract_section( file, start ):
        section = []
        line = file.readline()
        pos = file.tell() #current position of the first line of the section just after ~XXX

        keep_reading = True 

        while keep_reading: 
            if not '~' in line:
                pos = file.tell() #current position 
                section.append( line )
                line = file.readline()

            #end of the section, and new section starts go to previous line 
            else: 
                file.seek( pos )
                keep_reading = False 

        return section 

    
    #FIXME 
    @staticmethod
    def process_curves_section( lines ):
        
        curves = [] 
        for line in lines: 
            i1 = line.find('.')
            i2 = line.find(':')
            curve = ( line[0:i1].strip(), line[i1:i2].strip(), line[i2:].strip() )
            curves.append( curve )
                    
            #units =  [ line.split(':')[0].split()[1].strip()[1:] for line in lines ]

        return curves #names, units
    
    
    

    @staticmethod
    def count_header_lines_to_skip( file_name ): 

        counter = 0 
        keep_reading = True 

        with open(file_name) as f:
            while keep_reading:
                line = f.readline()
                
                counter = counter + 1 

                if not line : #eof 
                    return None 

                elif counter > 500 :
                    return None 

                elif LasParser.is_data_section_line(line):
                    keep_reading = False 

                else: #commensts, other sections, blank lines, etc... 
                    pass 

        return counter 

    @staticmethod
    def get_data( file_name ):

        header_lines_count = LasParser.count_header_lines_to_skip( file_name )
        data = pd.read_table( file_name, header=None, sep='\s+', skiprows = header_lines_count )  
        return data

        #if the ~Ascii section isnt found, will return an empty data frame 
        #data = pd.read_table( PATH, header=None, delim_whitespace=True, skiprows = header_lines_count )           
        #data = pd.read_table( PATH, header=None,skipinitialspace=True, sep=r'\s+|\t|\s+\t|\t\s+', engine='python', skiprows = header_lines_count )   
         
    @staticmethod
    def parse_las( file_name ):

        data = LasParser.get_data( file_name )
        if data.empty: 
            print('Could not find the logs data')
            return None 

        log_names = None 
        log_units = None 
        well_section_lines = [] 
        header_data = {} 
        curves = [] 
        
        #Now lets parse the header. The column names will be extracted from there.  
        with open(file_name) as f:

            keep_reading = True 
            line = f.readline()

            while keep_reading:

                if not line : 
                    print('reached end of file, we should never reach this code. ')
                    keep_reading = False 

                elif LasParser.is_comment_line( line ): 
                    line = f.readline()

                #we shold have read this as a pandas dataframe before.
                elif LasParser.is_data_section_line(line):
                    keep_reading = False  

                elif LasParser.is_section_line ( line ):
                    section_starts = line 
                    section_lines = LasParser.exract_section( f, line  )

                    if LasParser.is_curves_section_line( section_starts ):
                        curves = LasParser.process_curves_section(section_lines) 
                        
                        data.columns = [ curve[0] for curve in curves ] 
                        header_data['çurves'] = curves

                    elif LasParser.is_well_section_line( section_starts):
                        well_section_lines = section_lines 
                        
                        for l in well_section_lines:
                            words = l.split(' :')[0].split()#[0].split()
                            if len (words) >=2: 
                                word1 = words[0].replace('.','').strip()
                                word2 = words[ len(words) - 1 ].replace('.','').strip()
                                header_data[ word1] = word2 

                    else: 
                        pass             

                    line = f.readline()

                else:
                    line = f.readline() 
        
        well_data = WellData( data, header_data  )
        well_data.insert(0, 'WELLNAME',header_data['WELL'] )
        return well_data 
        
    
    
    def load_las_files( files, FOLDER ):

        well_data_array = [] 
        for file in files:
            PATH =  os.path.join( FOLDER, file )

            item = LasParser.parse_las( PATH )
            
            if 'WELLNAME' not in item: item.insert(0, 'WELLNAME', item.well_info['WELL'] )
            well_data_array.append( item )


        #lets keep only the logs that are common to all the wells 
        set0 = set( well_data_array[0].log_names )
        for n in range( 1, len(well_data_array)):
            set1 = set( well_data_array[n].log_names )
            set0 = set0.intersection( set1 )

        common_columns = list( set0 )


        for n in range( 0, len(well_data_array)):
            cols = [ log for log in well_data_array[n].log_names if log in common_columns]
            well_data_array[n] = well_data_array[n][cols ]


        #nice, lets now append pandas data frames vertically and sort by depth ? 
        well_data = pd.concat( well_data_array )
        names= well_data['WELLNAME'].unique()
        cat = { names[n]:n for n in range( 0, len(names))}
        well_data['WELLID'] = well_data['WELLNAME'].map( cat ).astype(int)

        
        return well_data 
    
   