

class Table: 
        
    '''
    The class represent a columnar array of pairs (x,y) such a a discrete function.
    Visage uses this dataset as dvt tables.  
    The class also provides the functionality to interpolate and resample or resize the table
    '''
    def __init__(self, **args):
       
        '''
        Args: A dictionary containing one or more of the following parameters:
        
            name: A string identifier for the table.
            
            dependent: a name (string identifier) for th dependent variable, for instance 'Permeability'.
            
            independent: identifier for the independent variable y = f(x)
            Here x is the independent variable (for instance Porosity) and y is the dependent variable.
            
            data: A dictionary or a list of tuples as:
            
            data = { x:[1,2,3,4], y: [1,1,1,2] }.
            
            data = {'Porosity':[1,2,3,4], 'Permeability': [1,1,1,2]}.
            
            data = [(x1,y1),(x2,y2),....(xn,yn].
            
        Returns:
            An instance of the Table class.
        
        '''
        self._name = args['name'] if 'name' in args  else 'default'
        self._independent = args['independent'] if 'independent' in args  else 'x'
        self._dependent = args['dependent'] if 'dependent' in args  else 'y'
        
        if 'data' in args:
            self.set_data( args['data'] )
            
        else:
            self.set_data( [(0.0,0.0), (1.0, 1.0) ] )
             
    
    def __repr__(self):
        s1 = 'name: {}, size: {}\ndependent: {} independent {}'.format( self._name, self.count, self.dependent_variable_name, self.independent_variable_name );     
        s2 =''
        for n in range(0,len(self._x)):
            s2 = s2 + '{} {}\n'.format(self._x[n], self._y[n])
        
        return s1 + '\n' + s2 
        
    def  __str__(self):
        return self.__repr__();
    
    def __getitem__( self, index ): 
        return [self._x[index], self._y[index]]
    
    def __len__(self): return len( self._x) 
    
    @property 
    def x_values(self ):
        '''Returns the x values. '''
        return self._x
    
    @property 
    def y_values(self ):
        '''Returns the y values.'''
        return self._y
    
    @property
    def count(self):
        '''Returns the number of points (x,y).'''
        return len(self._x) 
    
    @property
    def size(self):
        '''Returns the number of x values.'''
        return len(self._x) 
    
    @property
    def name(self)->str:
        '''The name of the table'''
        return self._name
    
    @property
    def xmax(self)->float:
        return max(self._x)
    
    @property
    def xmin(self)->float:
        return min(self._x)
    
    @property 
    def x(self): return self._x.copy()
    
    @property 
    def y(self): return self._y.copy()
    
   
    @name.setter
    def name(self, value):
        
        #not allow funny names 
        #(not implemented yet)
        self._name = value
        
    @property
    def dependent_variable_name(self,)->str:
        return self._dependent

    @dependent_variable_name.setter 
    def dependent_variable_name(self, value:str ):
        self._dependent = value    

    @property
    def independent_variable_name(self)->str:
        return self._independent 

    @independent_variable_name.setter 
    def independent_variable_name(self,value:str):
        self._independent = value 
    

    
    def xmin(self)->float:
        return min(self._x) 
    
    def xmax(self)->float:
        return max(self._x) 
    
    @staticmethod
    def instance( **args ): #item must be: 
        return Table( args )
         
    def copy( self ):
        '''Returns a copy of the table.'''
        #fix style  
        t = Table();
        t.name = self._name
        t._independent = self._independent 
        t._dependent = self._dependent 
        return t;
    
        
    #this is inefficient 
    def add_point(self, x, y ):
        '''Add one arbitrary point (x,y) to the dataset. The point is added in ascending order based on the x value.'''
        xvals = self.x
        yvals = self.y
        
        xvals.append( x )
        yvals.append( y )
        
        z = sorted(zip( xvals, yvals ), key=lambda item: item[0] )
        self._x = [ value[0] for value in z ]
        self._y = [ value[1] for value in z ]
        
        
 
        
    def set_data( self, data ):
        '''Sets/repaces the stored data. The data is sorted according to the x values.'''
        self._x = []
        self._y = [] 

        #if it is a list [ (x1,y1), (x2,y2), .....] 
        #and all the elements are tuples of size 2 
        if type(data) is list:  #
            
            #all are tuples of 2 elements 
            all_ok = all( [ type(item) == type(()) and len(item)==2 for item in data ] )
                
            if all_ok is True: 
                
                #first lets be sure that the x values are in ascending order 
                s = sorted( data, key=lambda it: it [0])
                
                self._x = [ item[0] for item in s ]
                self._y = [ item[1] for item in s ]
            else:
                raise ValueError('The list should be [(x1,y1),(x2,y2),...]')
            
            

        #it is is a dict with keys x,y and both are lists of the same size 
        #of if the keys are dependent and independent
        elif type(data) is dict: # { x:[1,2,3,4], y: [1,1,1,2]}
            
             
            success  = 0 
            x = None 
            y = None 

            if self.dependent_variable_name in data: 
                y = data[self.dependent_variable_name]
                success  = success + 1 
                
            elif 'y' in data: 
                y = data['y']
                success  = success + 1 
            
            else:
                pass
            
            if self.independent_variable_name in data: 
                x = data[self.independent_variable_name]
                success  = success + 1 
                      
            elif 'x' in data: 
                x = data['x']
                success  = success + 1 
            
            else:
                pass
            
            if (x is None) or ( len(x) != len(y)): 
                success = -1 
            
            if success != 2: 
                raise ValueError('There was an error in constructing the table', success)
                
            else: 
                #sort x values in ascending order 
                values = sorted( zip(x,y), key = lambda it: it[0] )
                self._x = [value[0] for value in values ]
                self._y = [value[1] for value in values ]
                
                
        else: 
            raise ValueError('There was an error in constructing the table')
            
            
    def get_interpolated_value( self, x:float)->float:
        '''Returns the y value ( y = f(x) ) for the x value passed as argument.'''
        #helpers 
        
        #this splits an interval as part of binary search 
        def split( number, k1,k2 ):
            
            if k2 - k1 <= 1: return k1,k2;
            
            pivot = k1 + (int)(0.5*(k2 - k1));
            if number > self._x[pivot]:
                k1 = pivot;
            
            else:
                k2 = pivot;
            
            return k1, k2;
        
        def get_pair_interpolate(v, l1, l2):
            epsilon = 0.00001*(self._x[l1] + self._x[l2]);
            w0 = abs(1 / (v - self._x[l1] + epsilon));
            w1 = abs(1 / (v - self._x[l2] + epsilon));
            return ((self._y[l1]*w0 + self._y[l2]*w1) / (w0 + w1));
        

        
        #edge cases 
        #1. the table has a single value, always return the same y 
       
        if self.count  == 1: 
            return self._y[0]
        
        #2. table is empty, return the input x 
        elif self.count  ==0:
            return x
        
        #3. x is too fr to the right or left 
        elif x <= self._x[0]:
            return self._y[0]
        elif x >= self._x[ len(self._x) - 1]:
            return self._y[ len(self._y)- 1]
        
        #we need to interpolate. 
        else:
            k1, k2 = split(x, 0, len(self._x) - 1);

            while k2 > k1 + 1:
                k1, k2 = split(x, k1, k2);
            
            return get_pair_interpolate(x, k1, k2);
            
    def get_interpolated_values( self, x:list)->list:
        '''Returns a list of values [ t =f(x1), f(x2,...] for the x values passed as a list in the argument.
        
        .. code:: python
        
           x= [item for item in list ]
        
        '''
        return [ self.get_interpolated_value(value) for value in x ]

    
    def resample( self,  npoints:int, xlimits = None ):
        '''Resamples the table to contain a number of npoints. These are equialy-space and correspond to the interpolation 
        between the initial points.'''
        
        x1 = xlimits[0] if xlimits is not None else min(self.x_values)
        x2 = xlimits[1] if xlimits is not None else max(self.x_values)
        
        delta = (x2 - x1) / (npoints - 1);
        xvals = [ x1 + n * delta for n in range(0,npoints) ]
        yvals = self.get_interpolated_values( xvals );
        
        self._x = xvals
        self._y = yvals 
     
        
        