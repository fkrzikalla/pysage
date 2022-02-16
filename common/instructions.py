from enum import Enum


class FAILURE_MODE(Enum):
    ELASTIC = 0
    MOHR_COULOMB = 1
    CAP = 2
    
    


class InstructionBase:

    def __init__(self, name: str = None, value:str = None ):
        self.name = name 
        self.value = value 

class InstructionBlock( InstructionBase ):
    
    def __init__( self, name: str = None, value:str = None, hashes: dict = None  ):
        super().__init__( name, value )
        self.hashes = hashes.copy() if hashes is not None else {}
        
    def __contains__(self, hash_name:str): return True if hash_name in self.hashes else False 
  
    def __getitem__(self, key): return self.hashes[key] if key in self.hashes else '' 
  
    def __setitem__(self, key, value):  self.set_instruction( key, value )
        
    def keys( self ) : return [str(key) for key in self.hashes.keys()]
         
    def set_instruction(self, hash_name:str, value:str): 
        self.hashes[ hash_name.strip()] = str(value).strip() 
        
    def set_instructions( self, hashes: dict ):
        for key,value in hashes.items(): self.set_instruction( key, value )
     
    def delete_instruction(self, name:str): 
        if name.strip() in self.hashes: self.hashes.pop( name.strip() )
            
    def clear( self ): self.hashes  = {} 
    
    
class VisageSimulationOptions:
          
    def __init__(self):
        self.commands = {} # a map of instruction blocks, thats what an MII is 
        
        self.path = None 
        self._model_name = None 
        self.step = -1 
        self.pinchout_tolerance = 1.0e-6
        self.auto_config_solver = True
        self.use_tables = True 
        self.use_fences = False 
        self.tables = [] 
        self.use_tables = True 
        self.geometry = None 
        self.cummulate_displacements = True 
        self.failure_mode =  FAILURE_MODE.ELASTIC #0-elastic 1- plastic 
        self.multi_step = True 
        self.gravity = True 
        self.use_gid = False
        self.dummy=False 
        self.include_files = [] 
        
        self.array_data = {} 
        self.boundary_conditions = {}
        
        #this is a pointer to a function that prints command blocks.
        #it can be changed to print as xml or json, or html from outside as object.stringtify = funtion.
        #function must receive a single object as argument 
        #Here it is preconfigued to print as required in an MII file 
        self.stringtify = VisageSimulationOptions.default_writter
        
        self.set_defaults()
        

        
    @property
    def model_name( self ):  return self._model_name
    
    @model_name.setter 
    def model_name( self, value ):
        #############################
        #verify the name is compliant 
        #############################
        print('FIXME: verify the name is compliant [2534254]' )
        self.set_command('MODELNAME', str(value) )
        self._model_name = value 
        
        
    def set_command(self,name, value=None, hashes:dict  = None ):
        self.commands[ name.strip() ] = InstructionBlock(name.strip(), str(value) if value is not None else None, hashes );
        
    def set_instruction( self,command_name, hash_name, hash_value):
        
        command_name = command_name.strip();
        hash_name = hash_name.strip();
        hash_value = str( hash_value ).strip();
        
        if command_name not in self.commands: 
            self.set_command( command_name, None, None )
            
        self.commands[ command_name ][ hash_name ] = hash_value 
            
        
    def configure_default_echo(self):
        hashedValues = {}
        hashedValues["snodes"]    = 1
        hashedValues["scgm"]      = -100
        hashedValues["selements"] = 1
        hashedValues["smaterials"]= 1
        hashedValues["sload"]     = 1
        self.set_command("NOECHO", "", hashedValues)
    
    def configure_tidy_name(self):
        self.set_command("TIDY", "  ");
        self.set_command("MODELNAME", self.model_name);

    def configure_default_header(self):
        hashedValues = {}
        hashedValues["module"]= "static"
        hashedValues["solution"]= "1"
        hashedValues["analysis"]= "3-D"
        hashedValues["sautoplastictime"]= "5"
        hashedValues["vp_timestep_factor"]= "0.5"
        hashedValues["sconvergencemethod"]= "0"
        hashedValues["Sanisotropic"]= "0"
        hashedValues["Slocalanisotropy"]= "0"
        hashedValues["Sjoint_anisotropy"]= "1"
        hashedValues["Smpc"]= "0"
        hashedValues["Nmpc"]= "0"
        hashedValues["Sporepressures"]= "0"
        hashedValues["numMeshBlocks"]= "1"

        hashedValues["Nelements"]= "1"
        hashedValues["Nnodes"]= "8"
        hashedValues["Nmaterials"]= "1"
        hashedValues["Nconstraints"]= "0"
        hashedValues["gaussrulebricks"]= "2"
        hashedValues["Niterations"]= "1"

        hashedValues["Sdisplacements"]= "0"
        hashedValues["Ndisplacements"]= "0"

        hashedValues["Nsub_increments"]= "1"
        hashedValues["Nfaults"]= "0"
        hashedValues["Sfaults"]= "0"
        hashedValues["Ndfn"]= "0"
        hashedValues["Sdfn"]= "0"
        hashedValues["Nmax_ele_per_dfn"]= "0"
        hashedValues["Nmax_ele_per_fault"]= "0"

        hashedValues["vcreep_tolerance"]= "1.000000E+000"

        hashedValues["Sedgeload"]= "0"
        hashedValues["Stemperatures"]= "0"
        hashedValues["Sgravity"]= "1"
        hashedValues["Saturation"]= "0"
        hashedValues["Sconnect"]= "0"
        hashedValues["Nconnect"]= "0"
        hashedValues["Npointload"]= "0"
        hashedValues["Screep"]= "0"
        hashedValues["Saccelerator"]= "0"
        hashedValues["sperformance_type"]= "2"

        hashedValues["nyield_gp_number"]= "1"
        hashedValues["Nsub_increments"]= "10"
        hashedValues["Nquickcalculation"]= "50"
        hashedValues["Niterations"]= "10"
        hashedValues["suse_all_disp"]= "1"
        self.set_command("HEADER", "", hashedValues);
                 
            
    def configure_default_solver_section(self):
        hashedValues = {}
        hashedValues["type"]= "7" 
        hashedValues["sdeflation "]= "0" 
        hashedValues["vtolerance"]= "1.00000E-08" 
        hashedValues["niter_stagnation"]= "5" 
        hashedValues["serrortrap"]= "3" 
        hashedValues["device"]= "" 
        self.set_command("SOLVER", "", hashedValues);
        
    def configure_load_increments(self):

        self.set_command("INCREMENTS,S", "5     5");
        self.set_command("VISCOPLASTICMETHOD,S", "1.000000000E+000    1.000000000E-003");
        self.set_command("LOADSTEP", "0");
              
    def configure_structured_grid(self):
        
        cells = [1,1,1]
        if self.geometry is not None:
            cells = self.geometry.element_count
                                  
        hashes = {}
        hashes["idimension"]= cells[0]
        hashes["jdimension"]= cells[1]
        hashes["kdimension"]= cells[2]
        hashes["ordering"]  = "gpp"
        self.set_command("STRUCTUREDGRID", "", hashes);      
        
        #this is needed 
        #cells = self.geometry.element_count
        nCells = cells[0]*cells[1]*cells[2]
        nNodes = (1+cells[0])*(1+cells[1])*(1+cells[2])
        self.set_instruction("HEADER", "Nelements", str(nCells));
        self.set_instruction("HEADER", "Nnodes", str(nNodes));
        self.set_instruction("HEADER", "Nmaterials", str(nCells));
        
            
    def configure_default_restart( self):
        hashedValues = {}
        current_step = str(self.step )
        prev_step = str(max(0, self.step- 1));

        hashedValues["Swriterestart"]= "1"
        hashedValues["Nwrite_number"]= current_step;
        hashedValues["Sreadrestart"]= "0";
        hashedValues["Suse_hdf5"]= "0";
        self.set_command("RESTART", "", hashedValues);
    
    
    def configure_default_results(self):
        hashedValues = {}
        
        hashedValues["petrel_units"]= "metric" 
        hashedValues["material_data"]= "1" 
        hashedValues["petrel"]= "1" 
        hashedValues["GID"]= "1" if self.use_gid else "0" 

        hashedValues["ele_pressures"]= "1" 
        hashedValues["ele_strain"]= "1" 
        hashedValues["ele_stresses"]= "1" 
        hashedValues["ele_total_stresses"]= "1" 

        hashedValues["ele_yield_values"]= "1" 
        hashedValues["ele_failure_mode"]= "1" 

        hashedValues["ele_fault_disps"]= "0" 
        hashedValues["ele_fault_strain"]= "0" 
        hashedValues["ele_fracture_disps"]= "0" 
        hashedValues["ele_fracture_strain"]= "0" 

        hashedValues["unify_faults"]= "1" 
        hashedValues["unify_fractures"]= "1" 

        hashedValues["nodal_total_disps"]= "2" 
        hashedValues["petrel_nodal"]= "2" 

        hashedValues["ele_creep_strains"]= "0" 
        hashedValues["ele_dvt_variation"]= "0" 
        hashedValues["ele_tot_pl_strain"]= "1" 
        hashedValues["permeability_update"]= "0" 
        self.set_command("RESULTS", "",hashedValues);
    
 
    
    def set_defaults(self):
        self.configure_default_echo()
        self.configure_tidy_name()
        self.configure_default_header()
        
        self.configure_default_solver_section()
        self.configure_load_increments()
        self.configure_structured_grid()
               
        self.configure_default_restart();
        self.configure_default_results();
        
                   
    def configure_multistep_restart(self):
        
        hashedValues = {};
        current_step = str(self.step);
        prev_step = str(max(0, self.step - 1));

        hashedValues["Swriterestart"]= "1"
        hashedValues["Nwrite_number"]= current_step;
        hashedValues["Sreadrestart"] = " 0 " if self.step ==0 else " 1 ";
        hashedValues["Nread_number"] = str(prev_step) if self.step > 0 else " 0 ";
        hashedValues["Suse_hdf5"]= "0"
        hashedValues["writerestart_file"]= self.model_name

        if self.step <= 0: self.commands.pop("LOADSTEP") 
            
        else: self.set_command("LOADSTEP", " 1 ");
            
        if self.step >= 1:
            hashedValues["readrestart_file"]= self.model_name;

        if self.step >= 2:
            self.set_instruction("RESULTS", "append_loadstep", str(self.step - 1));
            hashedValues["szerotime"] = "1";

        self.set_command("RESTART", "", hashedValues);
        
            
    
    def config_super_fast_run( options ):
        print("This is a fast deck ")
        options.set_instruction( "HEADER", "Nquickcalculation", "1" );
        options.set_instruction( "HEADER", "Niterations", "1" );
        options.set_instruction( "HEADER", "Nsub_increments", "1" );
        
        
    def config_solver( options ):
        if options.failure_mode == FAILURE_MODE.ELASTIC: 
            print('auto-config solver enabled for elastic runs')
            options.set_instruction( "HEADER", "Nquickcalculation", 1 );
            options.set_instruction( "HEADER", "Niterations", 1 );
            options.set_instruction( "HEADER", "Nsub_increments", 1 );
        else:
            print('auto-config solver enabled for plastic runs')
            #allow a max 5% of the gaussian points above tolerance 
            n_nodes = 1 + (int)(0.05 * 8 * geometry.num_nodes);
            options.set_instruction( "HEADER", "nyield_gp_number", str( n_nodes ) );
            options.set_instruction( "HEADER", "Nquickcalculation", str( 15 ) );
            options.set_instruction( "HEADER", "Niterations", str( 15 ) );
            options.set_instruction( "HEADER", "vyieldtolerance", str( 250.0 ) );
        
       
    
    def update( self ):
        
        if self.step < 0: self.step = 0 
        
        #gravity
        g = "0.0 1.0 0.0" if self.gravity == True else "0.0 0.0 0.0"
        self.set_command("GRAVITY", g);
        
        #failure mode 
        if self.failure_mode == FAILURE_MODE.ELASTIC: 
            self.set_command("ELASTIC");
            self.set_instruction( "RESULTS", "ele_tot_pl_strain", '0' );
            self.set_instruction( "HEADER", "Nsub_increments", '1' );

        else:
            self.commands.pop("ELASTIC")
            self.set_instruction( "RESULTS", "ele_tot_pl_strain", '1' );
        
        #restart 
        self.configure_multistep_restart()
        #self.set_instruction('RESTART',"Sreadrestart", 0 );
        
        
        #solver 
        self.config_solver(  )
        
        #quick or dummy run ? 
        if self.dummy == True: self.config_super_fast_run()
        
        
        #dates 
        year = str(1900 + self.step);
        date = "1" + " \n01/01/" + year + " 00:00:00.000";
        self.set_command("PRINTDATES", date);
    
        #grid with new nodes for instance 
        self.configure_structured_grid()
                          
        #model name
        self.set_command('MODELNAME', str(self.model_name)) 
        
        if self.use_tables == True and 'dvt_table_index' in self.array_data and len(self.tables) > 0 : 
            self.set_instruction( "RESULTS", "ele_dvt_variation", "1" );
            self.set_instruction( "HEADER", "ndvttables", str( len(self.tables) ))
        else:
            self.set_instruction( "RESULTS", "ele_dvt_variation", "0" );
            self.set_instruction( "HEADER", "ndvttables", "0" );
                                    
    
    def to_string(self):
        
        self.update()
        commands = self.commands

        #these need to be at the top of the MII file 
        first_commands = [ "MODELNAME","NOECHO",  "HEADER" ]
        
        s= ''
        for block_name in first_commands: 
            if block_name in commands: s += self.stringtify(commands[block_name])
        
        for block_name, block in commands.items():   
            if block_name not in first_commands:s += self.stringtify(block)
                   
        s += '*END\n'
        print(s)
        #echo = commands['NOECHO']
        #print( self.stringtify(echo) )
        
    @staticmethod
    def default_writter( item ):
        
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
    
    
    
    