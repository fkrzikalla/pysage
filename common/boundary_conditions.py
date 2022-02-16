from enum import Enum

class BOUNDARY_CONDITION(Enum):
    FIXED_ALL = 0
    DISPLACEMENT = 1
    STRAIN = 2
    FREE = 3 
    EDGELOAD = 4 
    ROLLER = 5
    FIXED_HORIZONTAL  = 6
    FIXED_VERTICAL    = 7
    
    NOSET = -1
    
    
    
class BOUNDARY_FACE(Enum):
    EASTWEST = 0
    NORTHSOUTH = 1
    BASE = 2
    TOP = 3 
    NOSET = -1
    
    
    
class Boundary_Condition:
    
    '''
    Base class to describe the basic info of different boubndary conditions.
    The class and the derived ones simply store data.
    The MII writter or other clients should know what to do with this data
    This way, the BC definition doesnt need to know about nodes, grids, etc..
    
    Parameters:
    
    direction: is the direction of the normal to the boundry faces of the model
    
        0: Strain, stress or movement constrained in the faces with normal along +-X, 
        1: Same but faces with normal in +-Y, 
        2: Strain, force, etc acting along Z on the nodes in the base of the model 
        3: Same but for the top (typiclly free or edgeload)

    btype: Constant defined in the Enum BOUNDARY_CONDITION
    '''
    
    def __init__(self, face:BOUNDARY_FACE, btype:BOUNDARY_CONDITION ):
        self.type = btype
        self.face = face 
        
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return 'type: {}  face:{}'.format( self.type, self.face )
            
        
class FixedHorizontal( Boundary_Condition ):
    
    def __init__( self,face:BOUNDARY_FACE ):
        super().__init__( face,BOUNDARY_CONDITION.FIXED_HORIZONTAL )
            
class FixedVertical( Boundary_Condition ):
    
    def __init__( self,face:BOUNDARY_FACE ):
        super().__init__( face,BOUNDARY_CONDITION.FIXED_VERTICAL )
        
class FixedAll( Boundary_Condition ):
    
    def __init__( self,face:BOUNDARY_FACE ):
        super().__init__( face,BOUNDARY_CONDITION.FIXED_ALL )

        
class NoSet( Boundary_Condition ):
    def __init__( self,face:BOUNDARY_FACE ):
        super().__init__( face,BOUNDARY_CONDITION.NOSET )
        
''' 
class FixedBoundary( Boundary_Condition ):
    
    def __init__( self,direction:BOUNDARY_FACE ):
        super().__init__( direction,BOUNDARY_CONDITION.FIXED )
        
class FreeBoundary( Boundary_Condition ):
    
    def __init__( self,direction:BOUNDARY_FACE):
        super().__init__( direction,BOUNDARY_CONDITION.FREE )
        
class RollerBoundary( Boundary_Condition ):
    
    def __init__( self,direction:BOUNDARY_FACE ):
        super().__init__( direction,BOUNDARY_CONDITION.ROLLER )
     
    
class StrainBoundary( Boundary_Condition ):
    
    def __init__( self,direction:BOUNDARY_FACE, strain:float ):
        super().__init__( direction,BOUNDARY_CONDITION.STRAIN )
        self.strain = strain 
        
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        s = super().__str__() + ' strain: {}'.format(self.strain)
        return s
    
class DisplacementBoundary( Boundary_Condition ):
    
    def __init__( self,direction:BOUNDARY_FACE, displacement:float ):
        super().__init__( direction,BOUNDARY_CONDITION.DISPLACEMENT )
        self.displacement = displacement 
        
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        s = super().__str__() + ' displacement: {}'.format(self.displacement)
        return s
    
'''
    
        
        
        
        