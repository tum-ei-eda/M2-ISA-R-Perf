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
# /

def mp_add(orig_, comp_):
    
    if type(orig_) is int:

        if type(comp_) is int:
            return max(orig_, comp_)
        
        elif type(comp_) is SumOfProducts:
            res = SumOfProducts([prod_i[:] for prod_i in comp_])
            a = orig_
            for prod_i in res:
                if prod_i[2] >= a:
                    return res
            res.append([a, 0, a])
            return res

        else:
            raise RuntimeError(f"Unexpected operand-type ({comp_}) for comp_ in mp_add.")
        
    elif type(orig_) is SumOfProducts:
        
        if type(comp_) is int:
            a = comp_
            for prod_i in orig_:
                if prod_i[2] >= a:
                    return orig_
            orig_.append([a, 0, a])
            return orig_

        elif type(comp_) is SumOfProducts:
            for prod_i in comp_:
                val_i, mask_i, min_i = prod_i
                doAppend = True
                for ii in reversed(range(len(orig_))):
                    val_ii, mask_ii, min_ii = orig_[ii]
                    # Identical symbols
                    if mask_i == mask_ii:
                        if val_i > val_ii:
                            orig_[ii] = (val_i, mask_i, min_i)
                        doAppend = False
                        break
                    # New product (prod_i) contains all symbols of product in orig_ (prod_ii), and remaining symbols+value for new product are larger
                    elif ((mask_ii & mask_i) == mask_ii) and (min_i >= min_ii):
                        orig_.pop(ii)
                    # Product in orig_ (prod_ii) contains all symbols of new product (prod_i), and remaining symbols+value for new product are larger
                    elif((mask_i & mask_ii) == mask_i) and (min_ii >= min_i):
                        doAppend = False
                        break # Do not insert prod_i
                
                if doAppend:
                    orig_.append([val_i, mask_i, min_i])
            return orig_

        else:
            raise RuntimeError(f"Unexpected operand-type ({comp_}) for comp_ in mp_add.")   

    else:
        raise RuntimeError(f"Unexpected operand-type ({orig_}) for orig_ in mp_add.")


def mp_mul(op_a_, op_b_):
    
    if type(op_a_) is int:

        if type(op_b_) is int:
            return op_a_ + op_b_
        
        elif type(op_b_) is SumOfProducts:
            a = op_a_
            return SumOfProducts([[prod_i[0] + a, prod_i[1], prod_i[2] + a] for prod_i in op_b_])
        
        else:
            raise RuntimeError(f"Unexpected operand-type ({op_b_}) for op_b_ in mp_mul.")
        
    elif type(op_a_) is SumOfProducts:

        if type(op_b_) is int:
            b = op_b_
            return SumOfProducts([[prod_i[0] + b, prod_i[1], prod_i[2] + b] for prod_i in op_a_])
        
        elif type(op_b_) is SumOfProducts:
            res = SumOfProducts()
            for p_i in op_a_:
                for p_ii in op_b_:
                    val_i, mask_i, _ = p_i
                    val_ii, mask_ii, _ = p_ii
                    val = val_i + val_ii
                    mask = mask_i | mask_ii
                    # TODO: Replace as soon as we run with Python 3.10+
                    res.append([val, mask, bin(mask).count('1') + val])
                    #res.append([val, mask, mask.bit_count() + val])
            return res

        else:
            raise RuntimeError(f"Unexpected operand-type ({op_b_}) for op_b_ in mp_mul.")
        
    else:
        raise RuntimeError(f"Unexpected operand-type ({op_a_}) for op_a_ in mp_mul.")
    
# Input: List[List[value:int, symbolMask:int]]
def mp_create_sop(prod_=[[]]):
    products = []
    for prod_i in prod_:
        val, mask = prod_i
        products.append([val, mask, bin(mask).count('1') + val])
    return SumOfProducts(products)

# SumOfProducts:List[product:"Product"]
# Product:fixed List[value:int, symbolMask:int, minValue:int]
class SumOfProducts(list):
    __slots__ = ()

class MaxPlusTerm:

    def __init__(self, sop_:'SumOfProducts'=None):
        
        self.value = 0
        self.symbolMask = 0
        self.products = []

        if sop_ is not None:

            if not type(sop_) is SumOfProducts:
                raise RuntimeError(f"Try to build a MaxPlusTerm from an unexpected data-type ({sop_})")

            minVal, minMask, _ = sop_[0]
            newProducts = []

            for val_i, mask_i, _ in sop_[1:]:
                minVal = min(minVal, val_i)
                minMask &= mask_i

            for val_i, mask_i, _ in sop_:
                val = val_i - minVal
                mask = mask_i & ~minMask
                if val==0 and mask==0:
                    continue
                # TODO: Replace with mask.bit_count() soon as we run with Python 3.10+
                self.products.append([val, mask, bin(mask).count('1') + val])

            self.value = minVal
            self.symbolMask = minMask
            self.products.sort(key=lambda prod: prod[1]) # Sort according to mask
            
#    def copy(self):
#        res = MaxPlusTerm()
#        res.value = self.value
#        res.symbolMask = self.symbolMask
#        res.products = [prod_i[:] for prod_i in self.products]
#        return res
    
    def isIdentical(self, term_):
        #if not type(term_) is MaxPlusTerm:
        #    return False
        
        if type(term_) is int:
            return (self.value == term_ and self.symbolMask == 0 and not self.products)
        elif type(term_) is MaxPlusTerm:
            return (self.value == term_.value and self.symbolMask == term_.symbolMask and self.products == term_.products)

        #if (self.value == term_.value) and (self.symbolMask == term_.symbolMask) and (self.products == term_.products):
        #    return True
        
        return False

    def getOffset(self, term_):

        if type(term_) is int:
            res = MaxPlusTerm()
            #res.value -= term_
            res.value = self.value - term_
            res.symbolMask = self.symbolMask
            if self.products:
                res.products = [prod_i[:] for prod_i in self.products]
            return res
        
        elif type(term_) is MaxPlusTerm:

            # Check that term_ covers all common symbols of self
            #if not((self.symbolMask & term_.symbolMask) == self.symbolMask):
            if not((self.symbolMask & term_.symbolMask) == term_.symbolMask):
                return None

            prod = None
            if self.products:
                if not term_.products:
                    prod = [prod_i[:] for prod_i in self.products]
                elif self.products != term_.products:
                    return None
            elif term_.products:
                return None
            
            res = MaxPlusTerm()
            res.value = self.value - term_.value
            res.symbolMask = self.symbolMask & ~term_.symbolMask
            if prod is not None:
                res.products = prod
            return res

        else:
            raise RuntimeError(f"Cannot derive offset for non-MaxPlusTerm term_ ({term_})")
        
    def getExpression(self):
        retStr = ""
        if self.value > 0:
            retStr += f"+{str(self.value)}"
        elif self.value < 0:
            retStr += f"-{str(abs(self.value))}"

        if self.symbolMask != 0:
            retStr += self.__getSymbolExpression(self.symbolMask)

        if self.products:
            if len(self.products) == 1:
                val, mask, _ = self.products[0]
                if val > 0:
                    retStr += f"+{str(self.value)}"
                elif val < 0:
                    retStr += f"-{str(abs(self.value))}"
                retStr += self.__getSymbolExpression(mask)
            
            else:
                skipDelim = True
                retStr += "+ std::max<uint64_t>({"
                for prod_i in self.products:
                    val_i, mask_i, _ = prod_i
                    if skipDelim:
                        skipDelim = False
                    else:
                        retStr += ", "
                    if val_i > 0:
                        retStr += str(val_i)
                    elif val_i < 0:
                        retStr += "-" + str(abs(val_i))
                    retStr += self.__getSymbolExpression(mask_i, skipLeadingAdd_=(val_i == 0))
                retStr += "})"

        return retStr

    def __getSymbolExpression(self, symMask_, skipLeadingAdd_=False, showAdd_=True):
        retStr = ""
        symIdxs = [i for i in range(symMask_.bit_length()) if (symMask_ >> i) & 1]
        for s_i in symIdxs:
            if skipLeadingAdd_:
                skipLeadingAdd_ = False
            else:
                retStr += "+" if showAdd_ else ""
            retStr += f"d_[{s_i}]"
        return retStr
    
    def __str__(self):
        retStr = ""
        
        if self.value > 0:
            retStr += str(self.value)
        elif self.value < 0:
            retStr += "-" + str(abs(self.value))

        if self.symbolMask != 0:
            retStr += self.__getSymbolExpression(self.symbolMask, showAdd_=False)

        if self.products:
            retStr += "("
            skipDelim = True
            for prod_i in self.products:
                val_i, mask_i, _ = prod_i
                if skipDelim:
                    skipDelim = False
                else:
                    retStr += " + "

                if val_i > 0:
                    retStr += str(val_i)
                elif val_i < 0:
                    retStr += "-" + str(abs(val_i))

                retStr += self.__getSymbolExpression(mask_i, showAdd_=False)    
            retStr += ")"

        return retStr