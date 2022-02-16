import pandas as pd 
import numpy as np 

from .coordinate_map import CoordinateMapping3D as CoordinateMapping3D 

class StructuredBase:
    '''
    Base class for structured geometric data such as regular grids and regulat surfaces
    '''
    
    DIMS = 3 
    
    def __init__( self, ncols:int, nrows:int, nlayers:int, extent:'np.array2d', reference:'CoordinateMapping3D'=None ):
        
        
        if (ncols < 0) or (nrows <0) or (nlayers<0):
            raise ValueError('num cols, rows and layers must be >= 0')
            
        self._node_count = [ ncols, nrows, nlayers, nlayers ]
        self._length = extent.copy()
        self.reference = reference.copy() if reference is not None else CoordinateMapping3D()  
        
    def __repr__(self):
        os = "<StructuredBase>\n"
        os += " <ncols>  {}\n".format(self.ncols)
        os += " <nrows>  {}\n".format(self.nrows)
        os += " <nlayers>  {}\n".format(self.nsurfaces)
        
        os += " <length> {}\n".format(self.length)
        os += str( self.reference );
        os += "<\StructuredBase>\n"
        os +='\n'
        return os;
        
    def __str__(self):
        return self.__repr__()
   
    @property
    def ncols( self ): 
        return self._node_count[0]
             
    @property
    def nrows( self ): 
        return self._node_count[1]
    
    @property
    def nsurfaces( self ): return self._node_count[2]
    
    @property
    def nlayers( self ): return self.nsurfaces
    

    @property
    def length( self ):
        return self._length
    
    @length.setter
    def length( self, value ):
        self._length = value 
    
    
    @ncols.setter
    def ncols(self, value):
        if value<0:
            raise ValueError( 'Error when setting the grid num cols to less than 0')
        self._node_count[0] =  value 

    @nrows.setter
    def nrows(self, value):
        if value<0:
            raise ValueError( 'Error when setting the grid num rows to less than 0')
        self._node_count[1] =  value 

    @nsurfaces.setter
    def nsurfaces(self, value):
        if value<0:
            raise ValueError( 'Error when setting the grid num surfaces to less than 0')
        self._node_count[2] = value       

    @nlayers.setter 
    def nlayers( self,value ): self.nsurfaces = value 
    
    
    @property 
    def num_nodes(self): return max(0,self.ncols) * max(0,self.nrows) * max(0,self.nlayers)
    
    @property
    def num_cells(self): return ( max(0,self.ncols-1)) * (max(0,self.nrows-1)) * (max(0,self.nlayers-1))

    @property 
    def total_elements(self): return self.num_cells

    @property 
    def node_count(self):  return self._node_count

    @property
    def element_count(self):  
        return [max(0,self._node_count[0]-1), max(0,self._node_count[1]-1),max(0,self._node_count[2]-1)]  
    
    @property 
    def nodes_per_layer( self ) : return self.ncols * self.nrows 

    
    def get_geometry_description(self):
        return self.ncols,self.nrows,self.nsurfaces,self.num_nodes, self.num_cells
    
    
    def get_node_indices_for_element(self, element: int)->list:
    
        '''
        Returns the 4 node indices at the base of an element
        
        The order is counter-clock when looking at the base from the inside of the element 
      
       
        top of the element 
        
             7     6 
         4  / |    |
           |  |    |
           | 3|_ __| 2
         z | /     /
           |/     /  base of the element 
           0-----1

               z 
              |
              |
           x  /-----y
             /
         
         base  
       
            3 _ __ 2
            /      /
           /      /
          0------1
          
              top 
          
             7 _ __ 6
            /      /
           /      /
          4------5
          

        Note tha tthe other 4 a the top are the same but need to add nodes_per_layer  
        
        Tested 
        '''
    
        nodes = self.node_count
        cells = self.element_count
        
        c_k, c_ij, cell_i, cell_j = self.get_element_indices(element)

        n1 = cell_j * nodes[0] + cell_i + c_k * (nodes[0] * nodes[1])
        n2 = n1 + 1
        n3 = n2 + nodes[0]
        n4 = n1 + nodes[0]

        return n1, n2, n3, n4; #should return n1,n2,n4,n3. It would be more consistent 
    
    
    def get_node_indices( self, surface_index: int ):
        '''
        returns [first_node, last_node).
        
        Returns: 
            first_node is the index of the first node in surface = surface_index
            last_node (NOT INCLUSIVE) is the upper node index for nodes in this surface. 
        
        Parameters:
            surface_index:  The inde of the horizontal layer of nodes (the index of the horizon in Petrel grids)
            
            This index starts with 0 at the bottom 
            
        Tested 
        '''
        
        
        #first nodes_per_layer are for surface= 0; , [nodes_per_layer, 2*nodes_per_layer ] -> surface = 1 ,....
        n1 = surface_index * self.nodes_per_layer;
        return [n1, n1 + self.nodes_per_layer ];
    

    def get_side_node_indices( self ):
    
        '''
        Returns a list of node indices at the faces of the grid
        xmin, xmax, ymin, ymax, zmin, zmax 
        
        This is pretty brute force. 
        
        Tested 
        ''' 
    
        ncols,nrows,nsurfaces,num_nodes, num_cells = self.get_geometry_description()
    
        aux = nsurfaces * ( ncols if ncols > nrows else nrows);
        node_indices = [ [],[],[], [] ] #left i, rght i, left j, right j
        
        counter = 0;
        for nk in range( 0, nsurfaces):
            for nj in range( 0,  nrows):
                for ni in range(0, ncols):
                    
                    if ni == 0: 
                        node_indices[0].append( counter );
                    
                    elif ni == ncols - 1:
                        node_indices[1].append( counter ); 
                    else:
                        pass
                    
                    if nj == 0:
                        node_indices[2].append( counter );
                        
                    elif nj == nrows- 1:
                        node_indices[3].append( counter );
                    else:
                        pass

                    counter += 1;
               
                
        return node_indices
        
    
    def get_element_indices_for_node( self, node:int )->list:
        
        '''
        Returns the element indices that contain the node as one of its vertices 
        
        Tested 
        '''
        nodes = self.node_count
        n_k = int( node / (nodes[0] * nodes[1]) );
        n_ij = node - n_k * (nodes[0] * nodes[1]);
        n_j = int( n_ij / (nodes[0]) );
        n_i = n_ij - n_j * nodes[0];

        elements = [];
        cells = self.element_count
        
        for ci  in range(max( n_i - 1, 0 ), min( cells[0] - 1, n_i )+1):
            for cj  in range(max( n_j - 1, 0 ), min( cells[1] - 1, n_j )+1):
                for ck  in range(max( n_j - 1, 0 ), min( cells[2] - 1, n_k )+1):
        
                    cell = ci + cj * cells[0] + ck * (cells[0] * cells[1]);
                    elements.append( cell )
        return elements;
    
    def get_element_indices(self, element:int)->list: #returns (i,j,k) of an element
        '''Tested '''
        cells = self.element_count

        c_k = int(element / (cells[0] * cells[1]))
        c_ij = element - c_k * (cells[0] * cells[1])
        cell_j = int(c_ij / (cells[0]))
        cell_i = c_ij - cell_j * cells[0]

        return c_k, c_ij, cell_i, cell_j;
    


    
    #These are in the original Visage-GPM implementation by xavier, but they may not be needed here 
    #static std::vector<float> nodal_to_elemental( int cols, int rows, int surfaces, const std::vector<float>& nodal_values )//, std::vector<float> &elemental_values)
    #std::vector<int> get_element_indices_above_node( int node )
    #static std::vector<float>  elemental_to_nodal( int node_cols, int node_rows, int node_surfaces, const std::vector<float>& elemental_values, float min_val, float max_val )
    
    
    def get_element_indices_above_node( self, node:int )->list:

        '''
        Returns the indices of all the eleements for which node is part of the base of the element 
        
        Tested 
        '''
        
        nodes = self.node_count
        cells = self.element_count

        n_k = int(node / (nodes[0] * nodes[1]))
        n_ij = node - n_k * (nodes[0] * nodes[1])
        n_j = int(n_ij / (nodes[0]))
        n_i = n_ij - n_j * nodes[0]
        
        elements = [];
        for ci in range( max(n_i - 1, 0), min(cells[0] - 1,n_i) +1):
            for cj in range( max(n_j - 1, 0), min(cells[1] - 1,n_j) +1):

                ck = n_k;
                cell = ci + cj * cells[0] + ck * (cells[0] * cells[1]);
                elements.append(cell);

        return elements;
    
    @property 
    def horizontal_spacing( self ):
        return [self.length[0] / (self.ncols - 1), self.length[1] / (self.nrows - 1)];
    


