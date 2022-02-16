from enum import Enum
import numpy as np
import sys, os  

from pysage.common.coordinate_map import CoordinateMapping3D as CoordinateMapping3D 
from pysage.common.structured_base import StructuredBase as StructuredBase 
from pysage.common.structured_grid import StructuredGrid as StructuredGrid 
from pysage.common.boundary_conditions import * 
from pysage.common.table import Table  
from pysage.common.instructions import *  



class VisageDeckWritter:
    
    
    @staticmethod
    def get_file_write_file_name( model_name, step, extension):
        return model_name + '_' + str(step) + '.' + extension 
        
        
    @staticmethod 
    def ensure_paths( *args ):

        prev = ''
        for key in args: 
            p = os.path.join(prev,key) 
            if not os.path.exists(p): os.mkdir( p )#, exist_ok = True  )
            prev = p
            
        return p;
 
    @staticmethod    
    def write_dvt_tables( options ):
            
        print('writting  dvt tables ...',options.use_tables )
        if options.use_tables == True and 'dvt_table_index' in options.array_data and len(options.tables) > 0 : 
            #options.set_instruction( "RESULTS", "ele_dvt_variation", "1" );
            #options.set_instruction( "HEADER", "ndvttables", str( len(options.tables) ))
            
            #lets write now an ascii file      
            model_name = options.model_name
            step = options.step;
            exension = 'dvt' 
            file_name = VisageDeckWritter.get_file_write_file_name( model_name, step, 'dvt' )
            VisageDeckWritter.ensure_paths( options.path )
            print('The dvt to be will be in ', file_name )
            
            #first, all the tables need to have the same length. 
            #Lets use the maximum length of all available but do not rescale if only one table
            max_length = options.tables[0].size 
            if len( options.tables) > 1: 
                max_length = max( options.tables, key = lambda x: x.size ).size 
                for t in options.tables: t.resample( max_length )
                
            t = options.tables[0] 
            s = "*DVTTABLES" + '\n' + "1" + " " + str(max_length)+ '\n\n'+ t.independent_variable_name+' '+t.dependent_variable_name+'\n';
            for t in options.tables: 
                for point in range(0,len(t)): s+= (str(t[point][0]) + ' ' + str(t[point][1])+'\n')
                s+='\n'
            
            
            file_path = os.path.join( options.path, file_name )
            with open( file_path, 'w') as f:
                f.write(s)
                
            return file_name       
                
        else: 
            options.set_instruction( "RESULTS", "ele_dvt_variation", "0" );
            options.set_instruction( "HEADER", "ndvttables", "0" );
            return '' 
                   
    @staticmethod    
    def write_materials( options, unit_conversion: dict = None )->str:  
        #lets write now an ascii file      
        file_name = VisageDeckWritter.get_file_write_file_name( options.model_name, options.step, 'mat' )
        VisageDeckWritter.ensure_paths( options.path )
        print('Writting materials... ', file_name )
        
        file_path = os.path.join( options.path, file_name )
        
        def write_property_array(values, options, file_descriptor):
            if type(values)==float or type(values)==int:
                num_cells=  options.geometry.num_cells
                for n in range( 0, num_cells):
                    pass
        
        def write_plastic_materials( options, unit_conversion:dict=None)->str:
            print('Not implemented yet')
            raise ValueError('Plastic simulations are not implemented yet')
            
            
        def write_elastic_materials( options, unit_conversion:dict=None )->str:
            if unit_conversion is None: unit_conversion = {} 
                
            print("elastic materials...")
            data = options.array_data 
            if 'YOUNGMOD' in data and 'POISSONR' in data and 'DENSITY' in data:
                ym  = np.array(data['YOUNGMOD'])* 1 if 'YOUNGMOD' not in unit_conversion else unit_conversion['YOUNGMOD']
                pr  = np.array(data['POISSONR'])* 1 if 'POISSONR' not in unit_conversion else unit_conversion['POISSONR']
                rho = np.array(data['DENSITY'] )* 1 if 'DENSITY'  not in unit_conversion else unit_conversion['DENSITY']
                phi = np.array(data['POROSITY'] ) if 'POROSITY' in data else np.array([0.2]) 
                biot = np.array(data['BIOTC'] ) if 'BIOTC' in data else np.array([1.0]) 
                
                with open( file_path, 'w') as f: 
                    ym_mult = 0 if ym.size == 1 else 1
                    pr_mult = 0 if pr.size == 1 else 1
                    num_cells=  options.geometry.num_cells
                    
                    f.write("*ELASTIC_DATA,NOCOM\n")
                    for n in range(0, num_cells):f.write( '1  {} {}\n'.format( ym[n*ym_mult], pr[pr_mult*n] ) )
                    f.write('\n')
                    
                    phi_mult = 0 if phi.size == 1 else 1
                    f.write("*POROSITY, NOCOM\n")
                    for n in range(0, num_cells):f.write( '{}\n'.format( phi[n*phi_mult] ) )
                    f.write('\n')
                    
                    biot_mult = 0 if biot.size == 1 else 1
                    f.write("*BIOTS_MODULUS,NOCOM\n")
                    for n in range(0, num_cells):f.write( '{}\n'.format( biot[n*biot_mult] ) )
                    f.write('\n')
                    
                    rho_mult = 0 if rho.size == 1 else 1
                    f.write("*SOLID_UNIT_W,NOCOM\n")
                    for n in range(0, num_cells):f.write( '{}\n'.format( rho[n*rho_mult] ) )
                    f.write('\n')
                                    
                
            else:
                raise ValueError( 'Missing mech properties. YOUNGMOD, POISSONR and DENSITY needed')

        if options.failure_mode != FAILURE_MODE.ELASTIC:
            write_plastic_materials( options)
        else:
            write_elastic_materials( options )

        return file_name 
     
    #requires the explicit node coordinates in the visage reference frame
    @staticmethod 
    def write_node_files( options: VisageSimulationOptions, xyz:list ):

        file_name = VisageDeckWritter.get_file_write_file_name( options.model_name, options.step, 'nod' )
        VisageDeckWritter.ensure_paths( options.path )
        print('Writting node file ', file_name )
        file_path = os.path.join( options.path, file_name )
        
        with open( file_path, 'w') as f: 
            
            f.write("*COORDS, NOCOM\n")
            num_nodes = options.geometry.num_nodes
            for n in range(0, num_nodes):
                f.write( '{}\t{}\t{}\t{}\n'.format( n+1,xyz[3*n], xyz[3*n+1],xyz[3*n+2]))
            
            return file_name;
    
    @staticmethod
    def write_boundary_conditions( options : VisageSimulationOptions ):
      
        g = options.geometry
        indices = g.get_side_node_indices(  )    

        #not used now, but will be used for more complex BC as in GPM
        #left  = indices[0][0:int( len(indices[0])/2 )]  #dir 0 x
        #right = indices[0][0:int( len(indices[0])/2 )]  #dir 0 x 
        #north  = indices[1][0:int( len(indices[1])/2 )] #dir 1 y
        #south  = indices[1][0:int( len(indices[1])/2 )] #dir 1 y 
        base  = np.arange( 0, g.nodes_per_layer, 1 )
        top   = np.arange( g.nodes_per_layer * (g.nlayers-1), g.num_nodes, 1 )
             
        VisageDeckWritter.ensure_paths( options.path )
        fixitites_file_name = VisageDeckWritter.get_file_write_file_name( options.model_name, options.step, 'fix' )
        fixitites_file = os.path.join( options.path, fixitites_file_name )
        with open( fixitites_file, 'w') as f: f.write('*CONSTRAINTS\n')
            
            
            
        fixities = 0
        displacments = 0
        print('Boundary conditions')
        for bc in options.boundary_conditions: #only fixities for now 
            
            s = ''
            the_nodes = []
            if bc.type in [BOUNDARY_CONDITION.FIXED_ALL,BOUNDARY_CONDITION.FIXED_VERTICAL,BOUNDARY_CONDITION.FIXED_HORIZONTAL]:
                    
                if bc.face == BOUNDARY_FACE.EASTWEST:   the_nodes = indices[0]
                if bc.face == BOUNDARY_FACE.NORTHSOUTH: the_nodes = indices[1]
                if bc.face == BOUNDARY_FACE.BASE:       the_nodes = base
                if bc.face == BOUNDARY_FACE.TOP:        the_nodes = top
                        
                if bc.type == BOUNDARY_CONDITION.FIXED_VERTICAL:   s = '0    1   0'
                if bc.type == BOUNDARY_CONDITION.FIXED_HORIZONTAL: s = '1    0   1'
                if bc.type == BOUNDARY_CONDITION.FIXED_ALL:        s = '1    1   1'
                        
                with open( fixitites_file, 'a') as f:
                    print('  ',bc.face, ' is a fixity bc')
                    for node in the_nodes: f.write('{}\t{}\t\n'.format(1+node,s))
                    fixities+= len( the_nodes )
                    
                   
            else:
                raise ValueError('Only fixity-type bcs are implemented 54667')
                        
        print('total fixities ', fixities)
        print('total displacements ', 0)
                
            
        displacements =0
        displacement_file='' 
        return fixities,fixitites_file_name, displacements, displacement_file 
           
    @staticmethod
    def write_elements( options : VisageSimulationOptions ):
        g = options.geometry
        activity = options.array_data['ACTIVITY'] if 'ACTIVITY' in options.array_data else g.total_elements*[0] 
            
        if options.use_tables == True and 'dvt_table_index' in options.array_data and len(options.tables) > 0 : 
            dvt = options.array_data['dvt_table_index']
        else: 
            dvt = g.total_elements*[0]
            
        VisageDeckWritter.ensure_paths( options.path )
        ele_file_name = VisageDeckWritter.get_file_write_file_name( options.model_name, options.step, 'ele' )
        ele_file_path = os.path.join( options.path, ele_file_name )
    
        ele_shape = 13;
        offset = (1+g.element_count[0])*(1+g.element_count[1])
        
        with open( ele_file_path, 'w') as f:
            f.write("*TOPOLOGY,NOCOM\n")
            
            for n in range(0, g.total_elements):
                
                #n1,n4,n3,n2 = g.get_node_indices_for_element(n)
                #f.write( '{}\t{}\t{}\t{} '.format(n2 + 1, n1 + 1,n4 + 1,n3 + 1))
                #f.write( '{}\t{}\t{}\t{} \n'.format(offset + n2 + 1,offset + n1 + 1,offset + n4 + 1,offset + n3 + 1))
                
                n1,n2,n3,n4 = g.get_node_indices_for_element(n)
                n5,n6,n7,n8 = n1+offset,n2+offset,n3+offset,n4+offset
                ele_dvt = dvt[n]
                ele_activity = activity[n]
                ele_zero_vol = 0
                f.write( '{}\t{}\t{}    {}     {}     {}     \n'.format(1+n,ele_shape,1+n,ele_activity,ele_zero_vol,ele_dvt+1))
                f.write( '{}\t{}\t{}\t{} '.format(n1+1, n5+1, n6+1, n2+1))
                f.write( '{}\t{}\t{}\t{} \n'.format( n4+1, n8+1, n7+1, n3+1))
                
                
                    
        
        return ele_file_name
    
    @staticmethod
    def mii_string( options ):
        
        def command_to_str( item ):
            preffix1 = '*'
            preffix2 = '#'
            if isinstance( item, InstructionBlock ):
                if item.name is None: return ''

                s = preffix1 + item.name + '\n'
                if (item.value is not None) and (len(item.value)>=1):
                    s+=(item.value+'\n')

                if (item.hashes is not None) and (len(item.hashes)>0):
                    for key,value in item.hashes.items():
                        s += (preffix2 + key + "\t" + str(value) + "\n");
                    s += "#end\n";

            return s+'\n'
        
        s = ''
        preffix1 = '*'
        preffix2 = '#'
        first_commands = [ "MODELNAME","NOECHO",  "HEADER", "ELASTIC", "GRAVITY" ]
        
        commands = options.commands 
        command_names = list(commands.keys())
        for block_name in first_commands: 
            if block_name in command_names: 
                s+=command_to_str( commands[ block_name ] )
                
        for block_name, block in commands.items():   
            #print(block_name, block)
            if block_name not in first_commands:
                s+=command_to_str( block )
                   
        for file_name in options.include_files:
            s += "INCLUDE " + file_name + "\n";
        

        s += "*END\n";
        
        return s+'\n' 
    
    @staticmethod
    def write_deck( options : VisageSimulationOptions, mii_stringtify = None  ):
        
        #we can configure the function to  write from the outside
        #so we can write an html, xml, or mii file formats 
        f = VisageDeckWritter.mii_string if mii_stringtify is None else mii_stringtify 

        path = options.path 
        VisageDeckWritter.ensure_paths( path ) 
        
        include_files = []            
        
        #first, transform the coordinates to the visage unit system 
        #coords are never unit-transformed. Must be meters!
        geometry = options.geometry;
        geometry_reference = geometry.reference;
        node_coordinates = geometry.get_all_local_coordinates()
 
        visage_reference = CoordinateMapping3D( [[ 1.0, 0.0, 0 ], [ 0.0, 0.0, 1.0 ], [ 0.0, 1.0, 0.0 ]] );
        transformed_coordinates = geometry_reference.convert_to( node_coordinates, visage_reference )
        
        #node file 
        node_file = VisageDeckWritter.write_node_files( options, transformed_coordinates )
        if len(node_file) > 0: 
            include_files.append( node_file )
            
        #dvt tables in the present verion several tables are allowed but only one pair dependen-independent variables
        dvt_file = VisageDeckWritter.write_dvt_tables( options )
        if( len(dvt_file) > 0 ): 
            include_files.append( dvt_file )
                     
        #boundary conditions 
        num_fixities, fixities_file, num_displacements, disp_file = VisageDeckWritter.write_boundary_conditions( options ) 
        options.set_instruction( "HEADER", "Nconstraints", str( num_fixities ) )
        options.set_instruction( "HEADER", "Ndisplacements", str( num_displacements ) );
        if num_fixities > 0: 
            include_files.append( fixities_file )
                   
        if num_displacements > 0: 
            include_files.append( dis_file )
            options.set_instruction( "HEADER", "Sdisplacements", "1" );
        else: 
            options.set_instruction( "HEADER", "Sdisplacements", "0" );
            

        #materials   
        mat_file = VisageDeckWritter.write_materials( options )
        if( len(mat_file) > 0 ): include_files.append( mat_file )
        
        #elements  
        ele_file = VisageDeckWritter.write_elements( options )
        if( len(ele_file) > 0 ): include_files.append( ele_file )
          

    
        print('INCLUDE FILES:')
        print( include_files )
        
        options.include_files = include_files 
        options.update()
        mii_file_name = VisageDeckWritter.get_file_write_file_name( options.model_name, options.step, 'MII' )
        mii_file_path = os.path.join( options.path, mii_file_name )
        
        mii = f(options)
        with open( mii_file_path, 'w') as f: f.write( mii )
            
        return mii_file_path 

   
   