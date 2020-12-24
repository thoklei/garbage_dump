import numpy as np 
np.set_printoptions(linewidth=160)

def high(x, u):
    assert x < u, "x must be smaller than u"
    assert x >= 0, "x must be positive"
    high = np.floor(x/np.sqrt(u))
    return int(high)

def low(x, u):
    assert x < u, "x must be smaller than u"
    assert x >= 0, "x must be positive"
    low = x % np.sqrt(u)
    return int(low)
    

def bits(value):
    bit = 0
    while 2**bit <= value:
        bit += 1
    return bit

def check(value):
    if value == 4:
        return True
    elif value < 4:
        return False
    else: 
        return check( np.sqrt(value) )


class VEB_Tree:

    def __init__(self, u):
        """
        Constructor.
        Setting min, max, count.
        Creating bitfield if small enough.
        TODO
        Not initializing trees yet if not necessary. ( currently works up to 2**(2**4) )
        """
        self._u = int(u)
        #print("Trying to create vEB-Tree of size", self._u)

        assert check(self._u), "vEB-size u must be 2^(2^i) for some i."

        self._min = None
        self._max = None
        self._count = 0

        if self._u <= 16 :
            self._bitfield = np.zeros((self._u,), dtype='bool')
            self._status = False # allows me to omit w in the insert-function
        else:
            self._overview = VEB_Tree(np.sqrt(self._u))
            self._details = [VEB_Tree(np.sqrt(self._u)) for _ in range(int(np.sqrt(self._u)))]
            self._status = True

    def insert(self, value):

        # increment count
        self._count += 1

        # check if tree is empty
        if self._min is None:
            self._max = value
            self._min = value 

        # check if outside of range, switch
        # TODO use fancy python syntax
        if value < self._min:
            temp = self._min
            self._min = value 
            value = temp 
        if value > self._max:
            temp = self._max 
            self._max = value 
            value = temp 

        # check if we are a complicated vEB-tree
        if self._status: 
            
            # check if details-vEB is empty
            if self._details[high(value, self._u)]._count == 0:
                self._overview.insert(high(value, self._u))

            # finally, insert into correct details-tree
            self._details[high(value, self._u)].insert(low(value, self._u))
        
        else: # we are only a bitfield
            self._bitfield[value] = True

# for debugging only, makes no sense for larger vEBs
    # def show(self):
    #     if not self._min is None:
    #         print("Min: ", self._min, ", Max: ", self._max)
    #     if self._status:
    #         for child in self._details:
    #             child.show()
    #     else:
    #         print(self._bitfield)


    def delete(self, value):

        # check if we even have this
        if not self.find(value):
            return

        hival = high(value, self._u)
        loval = low(value, self._u)
        
        # TODO handle special cases of count < 3 ?
        if self._count == 1:

            # we have only one value that is both min and max
            self._count = 0
            self._min = self._max = None

            if self._status:
                self._details[hival].delete(loval)
                self._overview.delete(hival)
            else:
                self._bitfield[value] = False
            return

        elif self._count == 2:

            # we have min and max but no other values
            if self._min == value:
                self._min = self._max

            if self._max == value:
                self._max = self._min

        else:

            # if we delete the min/max, we nee to fix that
            if self._min == value:
                self._min = self.closeAbove(self._min)

            if self._max == value:
                self._max = self.closeBelow(self._max)

        self._count -= 1
        
        if self._status:
            self._details[hival].delete(loval)    # tell responsible child to delete
            if self._details[hival]._count == 0:  # if it's empty now, update overview
                self._overview.delete(hival)
        else:
            self._bitfield[value] = False


    def find(self, search):
        """
        Not addressing bitfield directly, runtime O(log log u).
        """

        # check if empty
        if self._min is None:
            return False 

        # check if out of range
        if search < self._min or search > self._max:
            return False 

        # check if min/max
        if search == self._min or search == self._max:
            return True

        # check if bitfield
        if not self._status:
            return self._bitfield[search]
        else:
            return self._details[high(search, self._u)].find(low(search, self._u))


    def min(self):
        return self._min

    def max(self):
        return self._max 


    def closeAbove(self, value):
        return self._closeAbove(np.log2(self._u), value)

    def _closeAbove(self, w, value):

        w = int(np.floor(w))

        # check if empty
        if self._min is None:
            return None
        
        # check if smaller than everything
        if value < self._min:
            return self._min

        # check if greater than everything
        if value >= self._max:
            return None 

        # if bitfield, just find next bigger value
        if not self._status:
            
            for i in range(value+1, self._max):
                if self._bitfield[i] :
                    result = i 
                    break
            else:
                result = self._max
            return result

        hival = high(value, self._u) 
        loval = low(value, self._u)

        # check if responsible details-vEB can do this
        if self._details[hival]._count > 0 and self._details[hival]._max > loval:
            H = hival
            L = int(self._details[hival]._closeAbove(w/2, loval))
        else:
            H = self._overview._closeAbove(w/2, hival)
            if H is None:
                return self._max
            else:
                L = self._details[int(H)].min()
        return int(H * 2**(w/2) + L)


    def closeBelow(self, value):
        return self._closeBelow(np.log2(self._u), value) 

    def _closeBelow(self, w, value):

        w = int(np.floor(w))

        # check if empty
        if self._min is None:
            return None
        
        # check if greater than everything
        if value > self._max:
            return self._max

        # check if smaller than everything
        if value <= self._min:
            return None 

        # if bitfield, just find next smaller value
        if not self._status:
            
            for i in range(value-1, -1, -1):
                if self._bitfield[i] :
                    return i

        # if full vEB-Tree, do complicated stuff

        hival = high(value, self._u) 
        loval = low(value, self._u)

        # check if responsible details-vEB can do this
        if self._details[hival]._count > 0 and self._details[hival]._min < loval:
            H = hival
            L = int(self._details[hival]._closeBelow(w/2, loval))
        else:
            H = self._overview._closeBelow(w/2, hival)
            if H is None:
                return self._min
            else:
                L = self._details[int(H)].max()
        return int(H * 2**(w/2) + L)


def test():

    # creating a legitimate vEB-Tree
    size = 4 # everything after 4 takes too long, I still need to optimize 
    size = 2**(2**size)
    print("Testing with vEB-Tree of size: ", size)
    boas = VEB_Tree(size)

    # basic testing, not properly testing all corner-cases

    # inserting a bunch of values
    boas.insert(3)
    boas.insert(13)
    boas.insert(67)
    boas.insert(157)
    boas.insert(675)
    boas.insert(1337)
    boas.insert(3422)
    boas.insert(10589)
    boas.insert(24373)
    boas.insert(37899)
    boas.insert(47257)
    boas.insert(55812)
    boas.insert(65529)

    # testing find
    assert boas.find(3) == True, "find is not working"
    assert boas.find(65529) == True, "find is not working"

    assert boas.find(24373) == True, "find is not working"
    assert boas.find(43) == False, "find is not working"

    # testing closeAbove
    assert boas.closeAbove(11) == 13, "closeAbove is not working"
    assert boas.closeAbove(45) == 67, "closeAbove is not working"
    assert boas.closeAbove(255) == 675, "closeAbove is not working"
    assert boas.closeAbove(818) == 1337, "closeAbove is not working"
    assert boas.closeAbove(55777) == 55812, "closeAbove is not working"

    # testing closeBelow
    assert boas.closeBelow(14) == 13, "closeBelow is not working"
    assert boas.closeBelow(72) == 67, "closeBelow is not working"
    assert boas.closeBelow(680) == 675, "closeBelow is not working"
    assert boas.closeBelow(1390) == 1337, "closeBelow is not working"
    assert boas.closeBelow(60000) == 55812, "closeBelow is not working"

    # testing delete
    boas.delete(675)
    boas.delete(47257)

    # retesting find
    assert boas.find(3) == True, "find is not working after delete"
    assert boas.find(65529) == True, "find is not working after delete"

    assert boas.find(675) == False, "find is not working after delete"
    assert boas.find(47257) == False, "find is not working after delete"

    # retesting closeAbove
    assert boas.closeAbove(255) == 1337, "closeAbove is not working after delete"
    assert boas.closeAbove(38000) == 55812, "closeAbove is not working after delete"

    # retesting closeBelow
    assert boas.closeBelow(1300) == 157, "closeBelow is not working after delete"
    assert boas.closeBelow(55000) == 37899, "closeBelow is not working after delete"

    # testing deletion with only 1 value
    size = 3 # everything after 4 takes too long, I still need to optimize 
    size = 2**(2**size)
    print("Testing with vEB-Tree of size: ", size)
    boas2 = VEB_Tree(size)

    boas2.insert(3)
    boas2.delete(3)
    assert boas2.find(3) == False, "Corner case: deletion of 1 elem not working"
    assert boas2._count == 0, "Corner case: deletion of 1 elem not working"    

    boas2.insert(45)
    boas2.insert(13)
    assert boas2.find(45) == True, "Corner case: deletion of 1 elem not working"
    assert boas2.closeBelow(45) == 13, "Corner case: deletion of 1 elem not working"

    # testing deletion with 2 values
    size = 3 # everything after 4 takes too long, I still need to optimize 
    size = 2**(2**size)
    print("Testing with vEB-Tree of size: ", size)
    boas3 = VEB_Tree(size)

    boas3.insert(3)
    boas3.insert(11)
    boas3.delete(3)
    assert boas3.find(3) == False, "Corner case: deletion of 1 elem not working"
    assert boas3.find(11) == True, "Corner case: deletion of 1 elem not working"
    assert boas3.min() == 11, "Corner case: deletion of 1 elem not working"
    assert boas3.max() == 11, "Corner case: deletion of 1 elem not working"
    assert boas3._count == 1, "Corner case: deletion of 1 elem not working"    

    boas3.insert(45)
    boas3.insert(13)
    assert boas3.find(45) == True, "Corner case: deletion of 1 elem not working"
    assert boas3.closeBelow(45) == 13, "Corner case: deletion of 1 elem not working"

    print("Everything works.")

if __name__ == "__main__":
    test()