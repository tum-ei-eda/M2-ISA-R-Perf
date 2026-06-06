# 
#  Copyright 2026 Chair of EDA, Technical University of Munich
# 
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
# 
# 	 http://www.apache.org/licenses/LICENSE-2.0
# 
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# 

from typing import List

# NOTE:
# 1) This class expects operands of type:
#  a) int
#  b) a tuple representing an mp-product: (value, symbol_mask, temp_mask, min_value). Eg.: 5d1d2 -> (5, 0110, 0000, 7)
# 
# 2) As this class is performance-critical, type-checking is reduced (i.e. only checking for tuples)

class MaxPlusLib:

    def __init__(self, allowTempCreation_=True):
        self._tempDict = {} # Temp: (id, [op_a, op_b], min_value)
        self._tempList = []
        self._tempCnt = 0
        self._allowTempCreation = allowTempCreation_

    def createElement(self, val_:int, symIds_:List[int]):
        symMask = 0
        for sId_i in symIds_:
            symMask |= 1 << sId_i
        #return (val_, symMask, 0, bin(symMask).count('1') + 1)
        return (val_, symMask, 0, symMask.bit_count() + 1)
    
    def forAllMaskIdxs(self, mask_):
        while mask_:
            lsb = mask_ & -mask_
            idx = lsb.bit_length() - 1
            mask_ ^= lsb
            yield idx

    def str(self, op_):
        
        if type(op_) is int:
            return str(op_)
        
        elif type(op_) is tuple:
            ret = ""

            val = op_[0]
            symMask = op_[1]
            tempMask = op_[2]

            if val != 0:
                ret += str(val)

            if symMask != 0:
                for sym_i in self.__getMaskIdxs(symMask):
                #for sym_i in self.getMaskIdxs(symMask):
                    ret += f"d{sym_i}"

            if tempMask != 0:
                for temp_i in self.__getMaskIdxs(tempMask):
                #for temp_i in self.getMaskIdxs(tempMask):
                    ret += f"t{temp_i}"

            return ret
        
        return "<UNKNOWN>"


    def mul(self, op_a_, op_b_):

        if type(op_a_) is int:

            if type(op_b_) is int:
                return op_a_ + op_b_
            
            elif type(op_b_) is tuple:
                return (op_b_[0]+op_a_,
                        op_b_[1],
                        op_b_[2],
                        op_b_[3]+op_a_)
            
            else:
                raise RuntimeError(f"Unexpected operand-type ({op_b_}) for op_b_ in MaxPlusLib::mul.")
            
        elif type(op_a_) is tuple:

            if type(op_b_) is int:
                return (op_a_[0]+op_b_,
                        op_a_[1],
                        op_a_[2],
                        op_a_[3]+op_b_)
            
            elif type(op_b_) is tuple:
                val_ret = op_a_[0] + op_b_[0]
                symMask_ret = op_a_[1] | op_b_[1]
                tempMask_ret = op_a_[2] | op_b_[2]
                #minVal_ret = val_ret + bin(symMask_ret).count('1') + self.__getTempMinValue(tempMask_ret) # TODO: replace with .bit_count()!!
                minVal_ret = val_ret + symMask_ret.bit_count() + self.__getTempMinValue(tempMask_ret)

                if (val_ret == 0 and symMask_ret == 0 and tempMask_ret == 0 and minVal_ret != 0):
                    print(f"Creating something weird...")

                return(val_ret, symMask_ret, tempMask_ret, minVal_ret)
            
            else:
                raise RuntimeError(f"Unexpected operand-type ({op_b_}) for op_b_ in MaxPlusLib::mul.")
            
        else:
            raise RuntimeError(f"Unexpected operand-type ({op_a_}) for op_a_ in MaxPlusLib::mul.")
        
    def add(self, orig_, comp_, verbose_=False):

        if type(orig_) is int:

            if type(comp_) is int:
                return max(orig_, comp_)
            
            elif type(comp_) is tuple:
                minVal_comp = comp_[3]
                if orig_ > minVal_comp:
                    val_comp = comp_[0]
                    symMask_comp = comp_[1]
                    tempMask_comp = comp_[2]
                    
                    val_common = min(orig_, val_comp)

                    val_a = orig_ - val_common
                    minVal_a = val_a

                    val_b = val_comp - val_common
                    minVal_b = minVal_comp - val_common

                    tempMask = self.__getTemp((val_a, 0, 0, minVal_a), (val_b, symMask_comp, tempMask_comp, minVal_b))

                    return (val_common, 0, tempMask, val_common + self.__getTempMinValue(tempMask))
                else:
                    return comp_
                
            else:
                raise RuntimeError(f"Unexpected operand-type ({comp_}) for comp_ in MaxPlusLib::add.")

        elif type(orig_) is tuple:
            val_orig = orig_[0]
            symMask_orig = orig_[1]
            tempMask_orig = orig_[2]
            minVal_orig = orig_[3]

            if type(comp_) is int:
                if comp_ > minVal_orig:
                    val_common = min(val_orig, comp_)

                    val_a = val_orig - val_common
                    minVal_a = minVal_orig - val_common

                    val_b = comp_ - val_common
                    minVal_b = val_b

                    tempMask = self.__getTemp((val_a, symMask_orig, tempMask_orig, minVal_a), (val_b, 0, 0, minVal_b))

                    return(val_common, 0, tempMask, val_common + self.__getTempMinValue(tempMask))
                else:
                    return orig_
                
            elif type(comp_) is tuple:
                val_comp = comp_[0]
                symMask_comp = comp_[1]
                tempMask_comp = comp_[2]
                minVal_comp = comp_[3]

                if (verbose_):
                    print()
                    print(f" >> orig_: {orig_}")
                    print(f" >> comp_: {comp_}")


                symMask_common = symMask_orig & symMask_comp
                tempMask_common = tempMask_orig & tempMask_comp

                # orig_ covers all symbols of comp_
                if (symMask_common == symMask_comp) and (tempMask_common == tempMask_comp): 
                    if(minVal_orig >= minVal_comp):
                        return orig_
                
                # comp_ covers all symbols of orig_
                if (symMask_common == symMask_orig) and (tempMask_common == tempMask_orig):
                    if(minVal_comp >= minVal_orig):
                        return comp_
                    
                val_common = min(val_orig, val_comp)

                val_1 = val_orig - val_common
                symMask_1 = symMask_orig & ~symMask_common
                tempMask_1 = tempMask_orig & ~tempMask_common
                minVal_1 = val_1 + symMask_1.bit_count() + self.__getTempMinValue(tempMask_1)

                val_2 = val_comp - val_common
                symMask_2 = symMask_comp & ~symMask_common
                tempMask_2 = tempMask_comp & ~tempMask_common
                minVal_2 = val_2 + symMask_2.bit_count() + self.__getTempMinValue(tempMask_2)

                op_a, op_b = self.__checkDominance(
                    (val_1, symMask_1, tempMask_1, minVal_1),
                    (val_2, symMask_2, tempMask_2, minVal_2)
                )

                # op_a completely dominates op_b
                if op_b is None:
                    val_a, symMask_a, tempMask_a, minVal_a = op_a
                    val_common += val_a
                    symMask_common |= symMask_a
                    tempMask_common |= tempMask_a
                else:
                    tempMask = self.__getTemp(op_a, op_b)
                    tempMask_common |= tempMask

                minVal_common = val_common + symMask_common.bit_count() + self.__getTempMinValue(tempMask_common)
                return (val_common, symMask_common, tempMask_common, minVal_common)

#                if (dom := self.__checkDominance(
#                    (val_a, symMask_a, tempMask_a, minVal_a),
#                    (val_b, symMask_b, tempMask_b, minVal_b)
#                )) is not None:
#                    val_dom, symMask_dom, tempMask_dom, minVal_dom = dom
#                    val_common += val_dom
#                    symMask_common |= symMask_dom
#                    if tempMask_dom != 0:
#                        raise RuntimeError("This is odd.....")
#                    tempMask_ret = tempMask_common | tempMask_dom
#                
#                else:
#                    tempMask = self.__getTemp(
#                        (val_a, symMask_a, tempMask_a, minVal_a),
#                        (val_b, symMask_b, tempMask_b, minVal_b)
#                    )
#                    tempMask_ret = tempMask | tempMask_common
#
#                minVal_ret = val_common + symMask_common.bit_count() + self.__getTempMinValue(tempMask_ret)
#                return (val_common, symMask_common, tempMask_ret, minVal_ret)
            
            else:
                raise RuntimeError(f"Unexpected operand-type ({comp_}) for comp_ in MaxPlusLib::add.")
            
        else:
            raise RuntimeError(f"Unexpected operand-type ({orig_}) for orig_ in MaxPlusLib::add.")
        
    #def getTempList(self):
    #    return [MaxPlusTemp(t) for t in self._tempList]
    
    def getNumTemps(self) -> int:
        return len(self._tempList)

    def forAllTemps(self):
        for t in self._tempList:
            yield MaxPlusTemp(t)

    def forAllTemps_reversed(self):
        for t in reversed(self._tempList):
            yield MaxPlusTemp(t)

    def resolveElement(self, e_):
        return MaxPlusElement(e_)

    def __checkDominance(self, op_a_, op_b_):

        def check(dom_, sub_):
            _, symMask_dom, tempMask_dom, minVal_dom = dom_
            val_sub, symMask_sub, tempMask_sub, _ = sub_

            if(tempMask_dom == 0):
                if(val_sub == 0) and (symMask_sub == 0) and (tempMask_sub.bit_count() == 1):
                    temp_sub = self._tempList[tempMask_sub.bit_length()-1]
                    e1, e2 = temp_sub[1]
                    c1 = subCheck(symMask_dom, minVal_dom, e1)
                    c2 = subCheck(symMask_dom, minVal_dom, e2)

                    if c1 and c2:
                        return (dom_, None)
                    elif c1:
                        return (dom_, e2)
                    elif c2:
                        return (dom_, e1)
            
            return None

        def subCheck(symMask_, minVal_, e_):
            _, symMask_e, tempMask_e, minVal_e = e_
            if (tempMask_e == 0):
                if((symMask_ & symMask_e) == symMask_e) and (minVal_ >= minVal_e):
                    return True

        if (res := check(op_b_, op_a_)) is not None:
            return res
        elif (res := check(op_a_, op_b_)) is not None:
            return res
        
        return (op_a_, op_b_) 

#    def __checkDominance(self, op_a_, op_b_):
#
#        val_a, symMask_a, tempMask_a, minVal_a = op_a_
#        val_b, symMask_b, tempMask_b, minVal_b = op_b_
#
#        # Check if op_b_ dominates op_a_:
#        if (tempMask_b == 0):
#            if (val_a == 0) and (symMask_a == 0) and (tempMask_a.bit_count() == 1):
#                temp_a = self._tempList[tempMask_a.bit_length()-1]
#                domCnt = 0
#                for e_i in temp_a[1]:
#                    val_e, symMask_e, tempMask_e, minVal_e = e_i
#                    if (tempMask_e == 0):
#                        symMask_common = symMask_b & symMask_e
#                        if(symMask_common == symMask_e) and (minVal_b >= minVal_e):
#                            domCnt += 1
#                if domCnt == 2:
#                    return op_b_
#
#        # Check if op_a_ dominates op_b_:       
#        if (tempMask_a == 0):
#            if (val_b == 0) and (symMask_b == 0) and (tempMask_b.bit_count() == 1):
#                temp_b = self._tempList[tempMask_b.bit_length()-1]
#                domCnt = 0
#                for e_i in temp_b[1]:
#                    val_e, symMask_e, tempMask_e, minVal_e = e_i
#                    if (tempMask_e == 0):
#                        symMask_common = symMask_a & symMask_e
#                        if(symMask_common == symMask_e) and (minVal_a >= minVal_e):
#                            domCnt += 1
#                if domCnt == 2:
#                    return op_a_
#                        
#        return None

    def __getTemp(self, op_a_, op_b_):
        
        if not self._allowTempCreation:
            raise RuntimeError("Attempting to create a temp-variable. Not allowed for the current MaxPlusLib instance")
        
        #key = (*op_a_, *op_b_) if op_a_ <= op_b_ else (*op_b_, *op_a_)
        key = (op_a_, op_b_) if op_a_ <= op_b_ else (op_b_, op_a_)

        # If operator-pair is already registered as a temp, look it up
        temp = self._tempDict.get(key)
            
        # Check if duplicate of an existing temp: New temp can be expressed by op_a_
        if temp is None:
            val_a = op_a_[0]
            symMask_a = op_a_[1]
            tempMask_a = op_a_[2]
            #if (val_a == 0) and (symMask_a == 0):
            if (val_a == 0) and (symMask_a == 0) and (tempMask_a.bit_count() == 1):
            #if (val_a == 0) and (symMask_a == 0) and (tempMask_a != 0) and ((tempMask_a & (tempMask_a - 1)) == 0): # Check if tempMask_a is a power of two (i.e. only one bit set)
                subTemp_a = self._tempList[tempMask_a.bit_length()-1]
                if self.__checkDuplicate(subTemp_a, op_b_):
                    temp = subTemp_a
                    self._tempDict[key] = temp
                
                #subTemps_a = [self._tempList[i] for i in range(tempMask_a.bit_length()) if (tempMask_a >> i) & 1]
                #if len(subTemps_a) == 1:
                #    if self.__checkDuplicate(subTemps_a[0], op_b_):
                #        self._tempDict[key] = temp
                #        temp = subTemps_a[0]

        # Check if duplicate of an existing temp: New temp can be expressed by op_b_
        if temp is None:
            val_b = op_b_[0]
            symMask_b = op_b_[1]
            tempMask_b = op_b_[2]
            #if (val_b == 0) and (symMask_b == 0):
            if (val_b == 0) and (symMask_b == 0) and (tempMask_b.bit_count() == 1):    
                subTemp_b = self._tempList[tempMask_b.bit_length()-1]
                if self.__checkDuplicate(subTemp_b, op_a_):
                    temp = subTemp_b
                    self._tempDict[key] = temp

                #subTemps_b = [self._tempList[i] for i in range(tempMask_b.bit_length()) if (tempMask_b >> i) & 1]
                #if len(subTemps_b) == 1:
                #    if self.__checkDuplicate(subTemps_b[0], op_a_):
                #        self._tempDict[key] = temp
                #        temp = subTemps_b[0]

        # Create a new temp
        if temp is None:
            minVal = max(op_a_[3], op_b_[3])
            temp = (self._tempCnt, [op_a_, op_b_], minVal)
            self._tempDict[key] = temp
            self._tempList.append(temp)
            self._tempCnt += 1

        # Return temp mask
        return  1 << temp[0]
    
    def __getTempMinValue(self, mask_):
        ret = 0
        if mask_ != 0:
            idxs = []
            while mask_:
                lsb = mask_ & -mask_
                idx = lsb.bit_length() - 1
                idxs.append(idx)
                mask_ ^= lsb
            
            for i in idxs:
                ret += self._tempList[i][2]

        return ret
    
    def __getMaskIdxs(self, mask_):
        return [i for i in range(mask_.bit_length()) if (mask_ >> i) & 1]


    def __checkDuplicate(self, temp_, op_, pathWeight_=0, searchDepth_=0):

        if searchDepth_ >= 5:
            return False

        #op = (op_[0]-pathWeight_, *op_[1:3], op_[3]-pathWeight_)
        for e_i in temp_[1]:
            symMask_common = op_[1] & e_i[1]
            tempMask_common = op_[2] & e_i[2]
            if (symMask_common == op_[1]) and (tempMask_common == op_[2]):
                if e_i[3] >= (op_[3]-pathWeight_):
                    #print(f">Duplicate found at depth:{searchDepth_}")
                    return True
        
        for e_i in temp_[1]:
            val_i = e_i[0]
            symMask_i = e_i[1]
            tempMask_i = e_i[2]
            if symMask_i == 0 and tempMask_i.bit_count() == 1:
                subTemp = self._tempList[tempMask_i.bit_length()-1]
                if self.__checkDuplicate(subTemp, op_, pathWeight_+val_i, searchDepth_+1):
                    return True
            #if symMask_i == 0:
            #    subTemps = [self._tempList[i] for i in self.__getMaskIdxs(tempMask_i)]
            #    if len(subTemps) == 1:
            #        return self.__checkDuplicate(subTemps[0], op_, pathWeight_+val_i, searchDepth_+1)

        return False


#    def __checkDuplicate(self, temp_, op_, pathWeight_=0, searchDepth_=0):
#
#        if searchDepth_ >= 1:
#            return False
#
#        op = (op_[0]-pathWeight_, *op_[1:3], op_[3]-pathWeight_)
#        for e_i in temp_[1]:
#            symMask_common = op[1] & e_i[1]
#            tempMask_common = op[2] & e_i[2]
#            if (symMask_common == op[1]) and (tempMask_common == op[2]):
#                if e_i[3] >= op[3]:
#                    return True
#        
#        for e_i in temp_[1]:
#            val_i = e_i[0]
#            symMask_i = e_i[1]
#            tempMask_i = e_i[2]
#            if symMask_i == 0:
#                subTemps = [self._tempList[i] for i in self.__getMaskIdxs(tempMask_i)]
#                if len(subTemps) == 1:
#                    return self.__checkDuplicate(subTemps[0], op_, pathWeight_+val_i, searchDepth_+1)
#
#        return False


class MaxPlusElement:

    def __init__(self, elem_=None):
        
        self.value = 0
        self.symbolMask = 0
        self.tempMask = 0

        #self.symbolIdxs = [] # TODO: Dangerous to dublicate information (ref. masks). Rather have a member function to derive idxs when necessary!?
        #self.tempIdxs = [] # TODO: Dangerous to dublicate information (ref. masks). Rather have a member function to derive idxs when necessary!?

        self.zeroElement = False

        if type(elem_) is int:
            if elem_ == -1:
                self.zeroElement = True
            self.value = elem_
            
        elif type(elem_) is tuple:
            
            self.value = elem_[0]
            self.symbolMask = elem_[1]
            self.tempMask = elem_[2]
            
            #self.symbolIdxs = [i for i in range(self.symbolMask.bit_length()) if (self.symbolMask >> i) & 1]
            #self.tempIdxs = [i for i in range(self.tempMask.bit_length()) if (self.tempMask >> i) & 1]

        elif elem_ is not None:
            raise RuntimeError(f"Unexpected input {elem_} for MaxPlusElement")

    def isZeroElement(self):
        return self.zeroElement
    
    def isUnitElement(self):
        return (self.value == 0 and self.symbolMask == 0 and self.tempMask == 0)

    def isIdentical(self, elem_:'MaxPlusElement'):
        return (self.value == elem_.value) and (self.symbolMask == elem_.symbolMask) and (self.tempMask == elem_.tempMask)
    
    def getTempMask(self):
        return self.tempMask
    
    def getOffset(self, elem_:'MaxPlusElement'):
        symMask_common = self.symbolMask & elem_.symbolMask
        tempMask_common = self.tempMask & elem_.tempMask

        if (symMask_common == elem_.symbolMask) and (tempMask_common == elem_.tempMask):
            val_ret = self.value - elem_.value
            symMask_ret = self.symbolMask & ~elem_.symbolMask
            tempMask_ret = self.tempMask & ~elem_.tempMask
            return MaxPlusElement((val_ret, symMask_ret, tempMask_ret, -1))
        
        return None

    def getExpression(self):
        ret = ""

        if self.value > 0:
            ret += f"+{self.value}"
        elif self.value < 0:
            ret += f"-{abs(self.value)}"

        #for sym_i in self.symbolIdxs:
        #    ret += f"+d_[{sym_i}]"
        for sym_i in self.__getMaskIdxs(self.symbolMask):
            ret += f"+d_[{sym_i}]"

        #for temp_i in self.tempIdxs:
        #    ret += f"+t_{temp_i}"
        for temp_i in self.__getMaskIdxs(self.tempMask):
            ret += f"+t_{temp_i}"
            #ret += f"+t[{temp_i}]"

        return ret
    
    def __getMaskIdxs(self, mask_):
        while mask_:
            lsb = mask_ & -mask_
            idx = lsb.bit_length() - 1
            mask_ ^= lsb
            yield idx
            

    # TODO: Temporary hack. Remove:
    def getSymbolMask(self):
        return self.symbolMask
    
    # TODO: Temporary hack. Remove:
    def getMinValue(self):
        return self.value + len(self.symbols) # Note: Only true if self.temps == []
    
    # TODO: Temporary hack? Remove?
    def makeTuple(self):
        return (self.value, self.getSymbolMask(), 0, 0)

class MaxPlusTemp:

    def __init__(self, temp_):
        self.id = temp_[0]
        self.elements = [MaxPlusElement(e) for e in temp_[1]]
        self.minVal = temp_[2] # TODO: For dbg only?

    def getId(self):
        return self.id

    def forAllTempMasks(self):
        for e_i in self.elements:
            yield e_i.getTempMask()

    def getExpression(self, sep_=","):
        ret = ""
        setSep = False
        for e_i in self.elements:
            if (e := e_i.getExpression()) == "":
                raise RuntimeError("MaxPlusTemp with an empty element. This should never happen!")
            else:
                if setSep == False:
                    setSep = True
                else:
                    ret += sep_
                ret += e
        return ret
    
    def getSplitExpression(self):
        return [e.getExpression() for e in self.elements]

#    def getExpression(self, sep_=","):
#        ret = f"uint64_t t_{self.id} = "
#        ret += "std::max<uint64_t>({"
#        if (e := self.elements[0].getExpression()) == "":
#            ret += "0"
#            print(" >> Temp with empty element!?")
#        else:
#            ret += e
#        ret += sep_
#        ret += self.elements[1].getExpression()
#        ret += "});"
#        return ret

