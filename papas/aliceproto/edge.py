from heppy.papas.aliceproto.identifier import Identifier
class Edge(object): 
    '''An Edge stores end node ids, distance between the nodes, and whether they are linked
       
       attributes:
       
       id1 : element1 uniqueid generated from Identifier class
       id2 : element2 uniqueid generated from Identifier class
       key : unique key value created from id1 and id2 (order of id1 and id2 is not important) 
       distance: distance between two elements
       is_linked : boolean T/F
       edge_type : "hcal_track" "ecal_track" etc
    '''
    
    def __init__(self, id1, id2, is_linked, distance): 
        ''' The Edge knows the ids of its ends, the distance between the two ends and whether or not they are linked '''
        self.id1 = id1
        self.id2 = id2
        
        self.distance = distance
        self.edge_type = self._edge_type()
        self.linked = is_linked
        
        #should not have ecal/ecal and hcal/hcal(I think) because of merging
        #if self.edge_type=="ecal_ecal" :
        #    assert (not is_linked)
        #if self.edge_type=="hcal_hcal" :
        #    assert (not is_linked)  
            
        #for reconstruction we do not use ecal-hcal links 
        if self.edge_type == "ecal_hcal":
            is_linked =False
        self.key = Edge.make_key(id1,id2)
    
    def _edge_type(self):
        shortid1=Identifier.type_short_code(self.id1);
        shortid2=Identifier.type_short_code(self.id2);
        if shortid1 == shortid2:
            if shortid1 == "H":
                return "hcal_hcal"
            elif shortid1 == "E":
                return "ecal_ecal"
            elif shortid1 == "T":
                return "track_track"           
        elif (shortid1=="H" and shortid2 == "T" or shortid1=="T" and shortid2 == "H"):
            return "hcal_track"
        elif (shortid1=="E" and shortid2 == "T" or shortid1=="T" and shortid2 == "E"):
            return "ecal_track"  
        elif (shortid1=="E" and shortid2 == "H" or shortid1=="H" and shortid2 == "E"):
            return "ecal_hcal"  
        
        return "unknown"

    def __str__(self):
        if self.distance ==None:
            descrip = "Edge: " + str(self.id1) + " - "+ str(self.id2)  + "= None (" + str( self.linked) + " ) "
        else :
            descrip = "Edge: " + str(self.id1) + " - "+ str(self.id2)  + "=" + str(self.distance)+  " (" + str( self.linked) + " ) "
        return descrip
    
    def __repr__(self):
        return self.__str__()      
    
    @staticmethod 
    def make_key(id1,id2):
        '''method to create a key based on two ids that can then be used to retrieve a specific edge
        ''' 
        return hash(tuple(sorted([id1,id2])))

  