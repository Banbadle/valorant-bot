# Invertible dictionary
# Can be used as a regular dictionary
# Additional getInv(val) method, which returns a tuple of all keys which have a value of val
class InvDict():
    
    def __init__(self, iterable=None):
        self.dict       = dict()
        self.inverse    = dict()
        
        if iterable == None:
            return
            
        for key, val in iterable:
                self[key] = val
            
    def clear(self):
        self.dict.clear()
        self.inverse.clear()   
        
    def copy(self):
        dic = self.dict().copy()
        inv = self.inverse().copy()
        
        newInvDict          = InvDict()
        newInvDict.dict     = dic
        newInvDict.inverse  = inv
        
        return newInvDict
        
    def fromkeys(self, sequence, val=None):
        for key in sequence:
            self[key] = val
    
    def get(self, key):
        return self.dict.get(key)
    
    def items(self):
        return self.dict.items()
    
    def keys(self):
        return self.dict.items()
    
    def pop(self, key):
        
        val = self.dict.pop(key)
        self.inverse[val].pop(key)
        
        if len(self.getInv(val))  == 0 :
            self.inverse.pop(val)
        return val
            
    def popitem(self):
        key, val = self.dict.popitem()
        self.inverse[val].remove(key)
            
        return val;
    
    def setdefault(self, key, defaultValue=None):
        if key not in self.dict:
            self[key] = defaultValue
            
    def update(self, iterable):
        if type(iterable) == dict:
            for key, val in iterable.items():
                self[key] = val
                
        else:
            for key, val in iterable:
                self[key] = val
    
    def values(self):
        return self.dict.values()
    
    #Returns a tuple of all keys which have a value of val
    def getInv(self, val):
        return tuple(self.inverse[val])
        
    def __setitem__(self, key, val):
        
        #If key is not new
        if key in self.dict:
            
            oldVal = self.dict[key]
            if oldVal == val:
                return
            
            self.dict[key] = val        
            self.inverse[oldVal].remove(key)
            
            if len(self.getInv(oldVal)) == 0:
                self.inverse.pop(oldVal)
                
        #If key is new
        else:
            self.dict[key] = val

        #If value is not new
        if val in self.inverse:
            self.inverse[val].append(key)

        #If value is new
        else:
            self.inverse[val] = [key]
            
    def __iter__(self):
        return self.dict.__iter__()

    def __getitem__(self, key):
        return self.dict[key]


    def __str__(self):
        return self.dict.__str__()

