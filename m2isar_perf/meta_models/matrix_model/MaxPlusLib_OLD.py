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

def mp_add(op_a_, op_b_):

    if isinstance(op_a_, SumOfProducts):

        if isinstance(op_b_, int):
            if op_b_ <= op_a_.getMinValue():
                return op_a_
            else:
                res = SumOfProducts()
                if op_a_.products:
                    res.products = [Product(prod_=p, val_=op_a_.commonValue, symbols_=op_a_.commonSymbols) for p in op_a_.products]
                else:
                    res.products = [Product(val_=op_a_.commonValue, symbols_=op_a_.commonSymbols)]
                res.products.append(Product(val_=op_b_))

        elif isinstance(op_b_, SumOfProducts):
            pass

    return op_a_


def mp_mul(op_a_, op_b_):

    # TODO: Rearrange order of if-statements to prioritize frequent use-cases (int, int)?

    if isinstance(op_a_, SumOfProducts):
        
        if isinstance(op_b_, SumOfProducts):
            res = SumOfProducts()
            res.commonValue = op_a_.commonValue + op_b_.commonValue
            res.commonSymbols = op_a_.commonSymbols + op_b_.commonSymbols

            if not op_a_.products and not op_b_.products:
                return res
            elif not op_a_.products:
                res.products = [Product(prod_=p) for p in op_b_.products]
            elif not op_b_.products:
                res.products = [Product(prod_=p) for p in op_a_.products]
            else:
                for p_i in op_a_.products:
                    for p_ii in op_b_.products:
                        prod = Product()
                        prod.value = p_i.value + p_ii.value
                        prod.symbols = p_i.symbols + p_ii.symbols
                        res.products.append(prod)

            return res
        
        elif isinstance(op_b_, int):
            res = SumOfProducts(op_a_)
            res.commonValue += op_b_
            return res

        else:
            raise RuntimeError(f"Cannot handle operand-type ({op_b_}) for op_b_ in mp_mul")
        
    elif isinstance(op_a_, int):

        if isinstance(op_b_, SumOfProducts):
            res = SumOfProducts(op_b_)
            res.commonValue += op_a_
            return res
        
        elif isinstance(op_b_, int):
            return op_a_ + op_b_
        
        else:
            raise RuntimeError(f"Cannot handle operand-type ({op_b_}) for op_b_ in mp_mul")
        
    else:
        raise RuntimeError(f"Cannot handle operand-type ({op_a_}) for op_a_ in mp_mul")
    
    return None # Should never happen

class SumOfProducts(FrozenBase):

    def __init__(self, sop_:'SumOfProducts'=None):
        self.commonValue:int = 0
        self.commonSymbols:List[Symbol] = []
        self.products:List[Product] = []

        if sop_ is not None:
            self.commonValue = sop_.commonValue
            self.commonSymbols = sop_.commonSymbols[:]
            self.products = [Product(prod_=p) for p in sop_.products]

        super().__init__

    def __str__(self):
        retStr = ""
        if (v := self.commonValue) != 0:
            retStr += str(v)
        for s in self.commonSymbols:
            retStr += str(s)
        if self.products:
            retStr += "("
            skipOperator = True
            for p in self.products:
                if skipOperator:
                    skipOperator = False
                else:
                    retStr += "+"
                retStr += str(p)
            retStr += ")"
        return retStr
    
    def create(self, val_:int=0, symHandles_:List[int]=[]):
        self.commonValue = val_
        for s in symHandles_:
            self.commonSymbols.append(Symbol(s))
        return self
    
    def getMinValue(self):
        minVal = 0
        for p_i in self.products:
            minVal = max(minVal, p_i.getMinValue())
        minVal += self.commonValue + len(self.commonSymbols)
        return minVal
    
class Product(FrozenBase):

    def __init__(self, prod_:'Product'=None, val_:int=0, symbols_:List['Symbol']=[]):
        self.value:int = val_
        self.symbols:List[Symbol] = symbols_

        if prod_ is not None:
            self.value += prod_.value
            self.symbols.extend(prod_.symbols)

        super().__init__

    def __str__(self):
        retStr = ""
        if (v := self.value) != 0:
            retStr += str(v)
        for s in self.symbols:
            retStr += str(s)

    def getMinValue(self):
        return self.value + len(self.symbols)

# TODO: Make explicitly immutable?
class Symbol(FrozenBase):

    def __init__(self, handle_:int):
        self.handle = handle_

        super().__init__

    def __str__(self):
        return f"d{self.handle}"
