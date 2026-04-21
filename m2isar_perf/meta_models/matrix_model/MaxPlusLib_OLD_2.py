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

from meta_models.common.FrozenBase import FrozenBase

from typing import List

def mp_add(val_, comp_):

    if isinstance(val_, int):

        if isinstance(comp_, int):
            return max(val_, comp_)
        
        elif isinstance(comp_, SumOfProducts):
            res = SumOfProducts(comp_)
            if val_ > res.getMinValue():
                res.products.append(Product(val_=val_))
            return res

        else:
            raise RuntimeError(f"Cannot handle operand-type ({comp_}) for comp_ in mp_add")

    elif isinstance(val_, SumOfProducts):

        # NOTE: Not creating a new object here, but update val
        
        if isinstance(comp_, int):
            if comp_ > val_.getMinValue():
                val_.products.append(Product(val_=comp_))
            return val_

        elif isinstance(comp_, SumOfProducts):
            #val_.products.extend([Product(prod_=p) for p in comp_.products])
            for p_i in comp_.products:
                val_.insertProduct(p_i)
            return val_

        else:
            raise RuntimeError(f"Cannot handle operand-type ({comp_}) for comp_ in mp_add")

    else:
        raise RuntimeError(f"Cannot handle operand-type ({val_}) for val_ in mp_add")
    
    return None # Should never happen


def mp_mul(op_a_, op_b_):
    
    if isinstance(op_a_, int):

        if isinstance(op_b_, int):
            return op_a_ + op_b_
        
        elif isinstance(op_b_, SumOfProducts):
            res = SumOfProducts(op_b_)
            for prod_i in res.products:
                prod_i.value += op_a_
            return res
        
        else:
            raise RuntimeError(f"Cannot handle operand-type ({op_b_}) for op_b_ in mp_mul")
        
    elif isinstance(op_a_, SumOfProducts):

        if isinstance(op_b_, int):
            res = SumOfProducts(op_a_)
            for prod_i in res.products:
                prod_i.value += op_b_
            return res
        
        elif isinstance(op_b_, SumOfProducts):
            res = SumOfProducts()
            for prod_i in op_a_.products:
                for prod_ii in op_b_.products:
                    prod = Product(prod_i)
                    prod.value += prod_ii.value
                    prod.extendSymbols(prod_ii)
                    res.products.append(prod)
            return res
        
        else:
            raise RuntimeError(f"Cannot handle operand-type ({op_b_}) for op_b_ in mp_mul")
        
    else:
        raise RuntimeError(f"Cannot handle operand-type ({op_a_}) for op_a_ in mp_mul")
    
    return None # Should never happen


class SumOfProducts(FrozenBase):

    def __init__(self, sop_:'SumOfProducts'=None):
        self.products:List[Product] = []

        if sop_ is not None:
            self.products = [Product(prod_=p) for p in sop_.products]

        super().__init__()

    def __str__(self):
        retStr = ""
        if len(self.products) > 1:
            retStr += "("
            skipOperator = True
            for p in self.products:
                if skipOperator:
                    skipOperator = False
                else:
                    retStr += "+"
                retStr += str(p)
            retStr += ")"
        else:
            retStr += str(self.products[0])
        return retStr

    def create(self, val_:int, symHandles_:List[int]):
        symbols = [Symbol(s) for s in symHandles_]
        self.products = [Product(val_=val_, symbols_=symbols)]
        return self
    
    def getMinValue(self):
        minVal = 0
        for p_i in self.products:
            minVal = max(minVal, p_i.getMinValue())
        return minVal

    def insertProduct(self, newProd_:'Product'):

        newMask = newProd_._symbol_mask
        newMinVal = newProd_.getMinValue()

        for i in reversed(range(len(self.products))):
            prod_i = self.products[i]
            mask_i = prod_i._symbol_mask
            minVal_i = prod_i.getMinValue()

            #Identical symbols:
            if mask_i == newMask:
                if newProd_.value > prod_i.value:
                    self.products[i] = Product(prod_=newProd_)
                return
            # New product contains all symbols of prod_i, and remaining symbols+value for new product are larger 
            elif ((mask_i & newMask) == mask_i) and (newMinVal >= minVal_i):
                self.products.pop(i)
                # TODO: Check if it is actually ok to append and return here, if we call this function consistently
            # Old product (prod_i) contains all symbols of new product, and remaining symbols+value for new prod_i are larger 
            elif ((newMask & mask_i) == newMask) and (minVal_i >= newMinVal):
                return
        
        self.products.append(Product(prod_=newProd_))
    
class Product(FrozenBase):

    def __init__(self, prod_:'Product'=None, val_:int=0, symbols_:List['Symbol']=None):
        self.value:int = val_
        self.symbols:List[Symbol] = symbols_[:] if symbols_ else []

        if prod_ is not None:
            self.value += prod_.value
            self.symbols.extend(prod_.symbols)

        self._symbol_cnt = len(self.symbols)
        self._symbol_mask = 0
        for s in self.symbols:
            self._symbol_mask |= 1 << s.handle

        super().__init__()

    def __str__(self):
        retStr = ""
        if (v := self.value) != 0:
            retStr += str(v)
        for s in self.symbols:
            retStr += str(s)
        return retStr

    def getMinValue(self):
        return self.value + self._symbol_cnt

    def extendSymbols(self, prod_:'Product'):
        self.symbols.extend(prod_.symbols)
        self._symbol_mask |= prod_._symbol_mask
        self._symbol_cnt += prod_._symbol_cnt

# TODO: Make explicitly immutable?
class Symbol(FrozenBase):

    def __init__(self, handle_:int):
        self.handle = handle_

        super().__init__()

    def __str__(self):
        return f"d{self.handle}"
