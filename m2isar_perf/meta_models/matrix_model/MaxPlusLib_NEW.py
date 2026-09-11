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
import time, atexit

# NOTE:
# 1) This class expects operands of type:
#  a) int
#  b) a tuple representing an mp-product: (value, symbol_mask, temp_mask, min_value). Eg.: 5d1d2 -> (5, 0110, 0000, 7)
# 
# 2) As this class is performance-critical, type-checking is reduced (i.e. only checking for tuples)

class MaxPlusLib:

    # -- Instrumentation: class-level counters, accumulated across ALL instances
    #    (one mpLib per block), printed once at program exit. ----------------
    _STAT_LABEL = "NEW"
    _stat_registered = False
    _stat_instances = 0
    _stat_calls = 0          # __getTemp calls
    _stat_pairHit = 0        # found via the (op_a, op_b) pair key
    _stat_dupHit = 0         # found via __checkDuplicate absorption
    _stat_fullRed = 0
    _stat_hitOLD = 0
    _stat_hitNEW = 0
    _stat_newTemp = 0        # a new temp was actually created
    _stat_maxTempsPerInstance = 0
    _stat_time = 0.0         # cumulative seconds spent in __getTemp

    @classmethod
    def printStats(cls):
        if cls._stat_calls == 0:
            return
        avoided = cls._stat_calls - cls._stat_newTemp
        rate = 100.0 * avoided / cls._stat_calls
        print("=" * 56)
        print(f"[MaxPlusLib STATS - {cls._STAT_LABEL}]")
        print(f"  instances (blocks)   : {cls._stat_instances}")
        print(f"  __getTemp calls      : {cls._stat_calls}")
        print(f"    pair-key hits      : {cls._stat_pairHit}")
        print(f"    dedup/absorb hits  : {cls._stat_dupHit}")
        print(f"    fully reduced      : {cls._stat_fullRed}")
        print(f"    caught by OLD only : {cls._stat_hitOLD}")
        print(f"    caught by NEW only : {cls._stat_hitNEW}")
        print(f"    new temps created  : {cls._stat_newTemp}")
        print(f"  dedup rate           : {rate:.1f}%  ({avoided}/{cls._stat_calls} calls avoided a new temp)")
        print(f"  max temps / instance : {cls._stat_maxTempsPerInstance}")
        print(f"  time in __getTemp    : {cls._stat_time:.3f} s")
        print("=" * 56)

    def __init__(self, allowTempCreation_=True):

        if not MaxPlusLib._stat_registered:
            atexit.register(MaxPlusLib.printStats)
            MaxPlusLib._stat_registered = True
        MaxPlusLib._stat_instances += 1

        # Containers for temp-handling during computation
        self._tempDict = {} # Temp: (id, [op_a, op_b], min_value)
        self._tempList = []
        self._tempCnt = 0
        self._allowTempCreation = allowTempCreation_

        self._myTest = {}

        # Containers for temp-handling during resolvement
        self._activeTempIdxs = []
        self._unrolledTemps = [] # List[elements [Tuple[int, int, int, int]]]
        self._singleTemps = {} # idx[int] -> element [Tuple[int, int, int, int]]
        self._duplicateTemps = {} # duplicate (int) -> reference (int)

    def createElement(self, val_:int, symIds_:List[int]):
        symMask = 0
        for sId_i in symIds_:
            symMask |= 1 << sId_i
        return (val_, symMask, 0, symMask.bit_count() + val_)
    
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
                    raise RuntimeError(f"Creating something weird...")

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
                    minVal_common = val_common

                    val_orig = orig_ - val_common
                    op_orig = (val_orig, 0, 0, val_orig)

                    val_comp -= val_common
                    minVal_comp -= val_common
                    op_comp = (val_comp, symMask_comp, tempMask_comp, minVal_comp)

                    val_t, symMask_t, tempMask_t, minVal_t = self.__getTemp(op_orig, op_comp)

                    return (val_common + val_t, symMask_t, tempMask_t, minVal_common + minVal_t)
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
                    minVal_common = val_common

                    val_orig -= val_common
                    minVal_orig -= val_common
                    op_orig = (val_orig, symMask_orig, tempMask_orig, minVal_orig)

                    val_comp = comp_ - val_common
                    op_comp = (val_comp, 0, 0, val_comp)

                    val_t, symMask_t, tempMask_t, minVal_t = self.__getTemp(op_orig, op_comp)

                    return(val_common + val_t, symMask_t, tempMask_t, minVal_common + minVal_t)
                else:
                    return orig_
                
            elif type(comp_) is tuple:
                val_comp = comp_[0]
                symMask_comp = comp_[1]
                tempMask_comp = comp_[2]
                minVal_comp = comp_[3]

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

                # Extract common "factors"  
                val_common = min(val_orig, val_comp)
                minVal_common = val_common + symMask_common.bit_count() + self.__getTempMinValue(tempMask_common)

                val_orig -= val_common
                symMask_orig &= ~symMask_common
                tempMask_orig &= ~tempMask_common
                minVal_orig -= minVal_common
                op_orig = (val_orig, symMask_orig, tempMask_orig, minVal_orig)

                val_comp -= val_common
                symMask_comp &= ~symMask_common
                tempMask_comp &= ~tempMask_common
                minVal_comp -= minVal_common
                op_comp = (val_comp, symMask_comp, tempMask_comp, minVal_comp)

                val_t, symMask_t, tempMask_t, minVal_t = self.__getTemp(op_orig, op_comp)

                return(val_common + val_t, symMask_common | symMask_t, tempMask_common | tempMask_t, minVal_common + minVal_t)

                #tempMask = self.__getTemp(op_orig, op_comp)
                #tempMask_common |= tempMask

                #minVal_common = val_common + symMask_common.bit_count() + self.__getTempMinValue(tempMask_common)
                #return (val_common, symMask_common, tempMask_common, minVal_common)


#                op_a, op_b = self.__checkDominance(
#                    (val_1, symMask_1, tempMask_1, minVal_1),
#                    (val_2, symMask_2, tempMask_2, minVal_2)
#                )
#
#                # op_a completely dominates op_b
#                if op_b is None:
#                    val_a, symMask_a, tempMask_a, minVal_a = op_a
#                    val_common += val_a
#                    symMask_common |= symMask_a
#                    tempMask_common |= tempMask_a
#                else:
#                    tempMask = self.__getTemp(op_a, op_b)
#                    tempMask_common |= tempMask
#
#                minVal_common = val_common + symMask_common.bit_count() + self.__getTempMinValue(tempMask_common)
#                return (val_common, symMask_common, tempMask_common, minVal_common)

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
        
    def registerUsedTemps(self, elem_):

        if type(elem_) is int:
            return

        _, _, tempMask, _ = elem_
        for idx_i in self.forAllMaskIdxs(tempMask):
            if idx_i not in self._activeTempIdxs:
                self._activeTempIdxs.append(idx_i)




    def checkDuplicates(self, usedTemps_):

        def prune(term_):
            pruned = []
            for i, elem_i in enumerate(term_):
                insert = True
                for j in range(i+1, len(term_)):
                    dom_i = term_[j]
                    if dom_i[3] >= elem_i[3]:
                        if ((dom_i[1] & elem_i[1]) == elem_i[1] and (dom_i[2] & elem_i[2]) == elem_i[2]):
                            insert = False
                            break
                if insert:
                    pruned.append(elem_i)
            return pruned


        def rollOut(op_):
            val, symMask, tempMask, _ = op_
                    
            if tempMask == 0:
                return [op_]
              
            fix = (val, symMask, 0, symMask.bit_count() + val)
            res = [fix]

            for tempIdx_i in self.forAllMaskIdxs(tempMask):
                update = []
                for op_i in res:
                    for op_ii in unrolledTemps[tempIdx_i]:
                        update.append(self.mul(op_i, op_ii))
                        #e = self.mul(op_i, op_ii)
                        #update = checkInsert(e,update)
                res = update
            return prune(res)
        
        def stripCommon(term_):
            val_common = None
            symMask_common = None

            for e_i in term_:
                if val_common is None:
                    val_common = e_i[0]
                    symMask_common = e_i[1]
                else:
                    val_common = min(val_common, e_i[0])
                    symMask_common &= e_i[1]

            ret = []
            for e_i in term_:
                val_e, symMask_e, _, minVal_e = e_i
                val_e -= val_common
                symMask_e &= ~symMask_common
                minVal_e -= (val_common + symMask_common.bit_count())
                ret.append((val_e, symMask_e, 0, minVal_e))
            return ret, (val_common, symMask_common)

        # -- UNROLL TEMPS -- #
        unrolledTemps = [] # List[Tuple(int, int, int, int)]
        for temp_i in self._tempList:
            op_a, op_b = temp_i[1]
            unrolled = rollOut(op_a)
            unrolled.extend(rollOut(op_b))
            unrolled = prune(unrolled)
            #for e_i in rollOut(op_b):
            #    unrolled = checkInsert(e_i, unrolled)
            unrolledTemps.append(unrolled)


        # Strip common
        commonList = {}
        for i, used_i in enumerate(usedTemps_):
            if used_i:
                unrolledTemps[i], commonList[i] = stripCommon(unrolledTemps[i])

        seen = {}
        duplicates = {}
        dupCnt = 0
        for i, used_i in enumerate(usedTemps_):
            if used_i:
                key = frozenset(unrolledTemps[i])
                if key in seen:
                    dupCnt += 1
                    duplicates[i] = seen[key]
                else:
                    seen[key] = i

        #if len(duplicates) != 0:
        #    for i in duplicates.keys():
        #        dup_raw = self._tempList[i]
        #        dup = MaxPlusTemp(dup_raw[0], dup_raw[1])
        #        ref_raw = self._tempList[duplicates[i]]
        #        ref = MaxPlusTemp(ref_raw[0], ref_raw[1])
        #        print("----")
        #        print(f"Duplicate: t_{dup.id} = {dup.getExpressions()}, common: {commonList[i]}")
        #        print(f"Reference: t_{ref.id} = {ref.getExpressions()}, common: {commonList[duplicates[i]]}")
        #        print("----")
        #    print()
        #    #raise RuntimeError("TRAP")

        return dupCnt

    def resolveTemps(self):

        def checkInsert(elem_, sum_):
            insert = True
            rmv = []
            for s_i in sum_:
                _, e_mask, _, e_minVal = elem_
                _, s_mask, _, s_minVal = s_i

                common_mask = e_mask & s_mask

                # s dominates e
                if(e_mask == common_mask) and (s_minVal >= e_minVal):
                    insert = False
                    break

                # e dominates s
                if(s_mask == common_mask) and (e_minVal >= s_minVal):
                    rmv.append(s_i)

            if insert:
                sum_.append(elem_)

            res = [e for e in sum_ if e not in rmv]
            return res

        def rollOut(op_):
            val, symMask, tempMask, _ = op_
                    
            if tempMask == 0:
                return [op_]
              
            fix = (val, symMask, 0, symMask.bit_count() + val)
            res = [fix]

            for tempIdx_i in self.forAllMaskIdxs(tempMask):
                update = []
                for op_i in res:
                    for op_ii in self._unrolledTemps[tempIdx_i]:
                        e = self.mul(op_i, op_ii)
                        update = checkInsert(e,update)
                res = update
            return res

        # -- UNROLL TEMPS -- #
        #unrolledTemps = [] # List[Tuple(int, int, int, int)]
        for temp_i in self._tempList:
            op_a, op_b = temp_i[1]
            unrolled = rollOut(op_a)
            for e_i in rollOut(op_b):
                unrolled = checkInsert(e_i, unrolled)
            self._unrolledTemps.append(unrolled)
        
#        # -- CHECK FOR TEMPS WITH ONLY ONE ELEMENT -- #
#        for tempIdx_i in self._activeTempIdxs:
#            if len((elements := self._unrolledTemps[tempIdx_i])) == 1:
#                self._singleTemps[tempIdx_i] = elements[0]
#        self._activeTempIdxs = [i for i in self._activeTempIdxs if i not in self._singleTemps.keys()]
#
#        # -- CHECK FOR DUPLICATES -- #
#        seen = {}
#        for tempIdx_i in self._activeTempIdxs:
#            key = frozenset(self._unrolledTemps[tempIdx_i])
#            if key in seen:
#                self._duplicateTemps[tempIdx_i] = seen[key]
#            else:
#                seen[key] = tempIdx_i
#        self._activeTempIdxs = [i for i in self._activeTempIdxs if i not in self._duplicateTemps.keys()]



    def forAllActiveTemps(self):
        for t in self._tempList:
            yield MaxPlusTemp(t[0], t[1])
        
        
        #for idx_i in self._activeTempIdxs:
        #    yield MaxPlusTemp(idx_i, self._unrolledTemps[idx_i])

    # TODO: Check which of these temp functions are still required
    def getNumTemps(self) -> int:
        return len(self._tempList)

    def forAllTemps(self):
        for t in self._tempList:
            yield MaxPlusTemp(t[0], t[1])

    def forAllTemps_reversed(self):
        for t in reversed(self._tempList):
            yield MaxPlusTemp(t[0], t[1])

    def resolveElement(self, e_):
        return MaxPlusElement(e_)

#        if type(e_) is int:
#            return MaxPlusElement(e_)
#        
#        val, symMask, tempMask, _ = e_
#
#        # Replace temps if possible
#        for tempIdx_i in self.forAllMaskIdxs(tempMask):
#            
#            # Insert single-element temps
#            if elem := self._singleTemps.get(tempIdx_i):
#                val_e, symMask_e, tempMask_e, _ = elem
#                if tempMask_e != 0:
#                    raise RuntimeError("Temp-Mask of an element of an unrolled-temp is not zero")
#                if symMask_e & symMask != 0:
#                    raise RuntimeError("Symbols are already set")
#                val += val_e
#                symMask |= symMask_e
#                tempMask &= ~(1 << tempIdx_i)
#
#            # Duplicate-temps
#            if refIdx := self._duplicateTemps.get(tempIdx_i):
#                if ((1 << refIdx) & tempMask) != 0:
#                    raise RuntimeError("Ref-temp is already set")
#                tempMask &= ~(1 << tempIdx_i)
#                tempMask |= (1 << refIdx)
#
#        return MaxPlusElement((val, symMask, tempMask, _))

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


#    def __getTemp(self, op_a_, op_b_):
#
#        if not self._allowTempCreation:
#            raise RuntimeError("Attempting to create a temp-variable. Not allowed for the current MaxPlusLib instance")
#
#        MaxPlusLib._stat_calls += 1
#        _t0 = time.perf_counter()
#
#        #key = (*op_a_, *op_b_) if op_a_ <= op_b_ else (*op_b_, *op_a_)
#        #key = (op_a_, op_b_) if op_a_ <= op_b_ else (op_b_, op_a_)
#        key = frozenset((op_a_, op_b_))
#
#
#        # If operator-pair is already registered as a temp, look it up
#        temp = self._tempDict.get(key)
#        if temp is not None:
#            MaxPlusLib._stat_pairHit += 1
#
#        # Check if duplicate of an existing temp: New temp can be expressed by op_a_
#        if temp is None:
#            val_a = op_a_[0]
#            symMask_a = op_a_[1]
#            tempMask_a = op_a_[2]
#            #if (val_a == 0) and (symMask_a == 0):
#            if (val_a == 0) and (symMask_a == 0) and (tempMask_a.bit_count() == 1):
#            #if (val_a == 0) and (symMask_a == 0) and (tempMask_a != 0) and ((tempMask_a & (tempMask_a - 1)) == 0): # Check if tempMask_a is a power of two (i.e. only one bit set)
#                subTemp_a = self._tempList[tempMask_a.bit_length()-1]
#                if self.__checkDuplicate(subTemp_a, op_b_):
#                    temp = subTemp_a
#                    self._tempDict[key] = temp
#                    MaxPlusLib._stat_dupHit += 1
#
#                #subTemps_a = [self._tempList[i] for i in range(tempMask_a.bit_length()) if (tempMask_a >> i) & 1]
#                #if len(subTemps_a) == 1:
#                #    if self.__checkDuplicate(subTemps_a[0], op_b_):
#                #        self._tempDict[key] = temp
#                #        temp = subTemps_a[0]
#
#        # Check if duplicate of an existing temp: New temp can be expressed by op_b_
#        if temp is None:
#            val_b = op_b_[0]
#            symMask_b = op_b_[1]
#            tempMask_b = op_b_[2]
#            #if (val_b == 0) and (symMask_b == 0):
#            if (val_b == 0) and (symMask_b == 0) and (tempMask_b.bit_count() == 1):
#                subTemp_b = self._tempList[tempMask_b.bit_length()-1]
#                if self.__checkDuplicate(subTemp_b, op_a_):
#                    temp = subTemp_b
#                    self._tempDict[key] = temp
#                    MaxPlusLib._stat_dupHit += 1
#
#                #subTemps_b = [self._tempList[i] for i in range(tempMask_b.bit_length()) if (tempMask_b >> i) & 1]
#                #if len(subTemps_b) == 1:
#                #    if self.__checkDuplicate(subTemps_b[0], op_a_):
#                #        self._tempDict[key] = temp
#                #        temp = subTemps_b[0]
#
#        # Create a new temp
#        if temp is None:
#            minVal = max(op_a_[3], op_b_[3])
#            temp = (self._tempCnt, [op_a_, op_b_], minVal)
#            self._tempDict[key] = temp
#            self._tempList.append(temp)
#            self._tempCnt += 1
#            MaxPlusLib._stat_newTemp += 1
#            if self._tempCnt > MaxPlusLib._stat_maxTempsPerInstance:
#                MaxPlusLib._stat_maxTempsPerInstance = self._tempCnt
#
#        MaxPlusLib._stat_time += time.perf_counter() - _t0
#
#        # Return temp mask
#        return  (0, 0, 1 << temp[0], temp[2])



    def __getTemp(self, *ops_):

        if not self._allowTempCreation:
            raise RuntimeError("Attempting to create a temp-variable. Not allowed for the current MaxPlusLib instance")

        MaxPlusLib._stat_calls += 1
        _t0 = time.perf_counter()

        # If operator-pair is already registered as a temp, look it up
        opKey = frozenset(ops_)

        if (elem := self._myTest.get(opKey)) is not None:
            return elem

        temp = self._tempDict.get(opKey)
        if temp is not None:
            MaxPlusLib._stat_pairHit += 1


        def rollOut(maxTerm_, op_, compOp_, pathVal, pathSymMask, branch_, depth_=0):
            val, symMask, tempMask, minVal = op_

            val_resolved = val + pathVal
            symMask_resolved = symMask | pathSymMask
            minVal_resolved = minVal + (pathVal + pathSymMask.bit_count())

            #op = (val + pathVal, symMask | pathSymMask, tempMask, minVal + (pathVal + pathSymMask.bit_count()))
            #if op == compOp_:
            #    return True
            
            if minVal_resolved >= compOp_[3]:
                if((symMask_resolved & compOp_[1]) == compOp_[1]) and ((tempMask & compOp_[2]) == compOp_[2]):
                    return True

            # IDEA: Do some pruning already here? -> Why?

            # IDEA: Also abort if maxTerm_ is getting too long?
            #if (len(maxTerm_) > (32*(1+branch_))) or (tempMask.bit_count() != 1):
            if depth_==5 or (tempMask.bit_count() != 1):
                maxTerm_.append((val_resolved, symMask_resolved, tempMask, minVal_resolved))
                return False
                #val += pathVal
                #symMask |= pathSymMask
                #minVal += (pathVal + pathSymMask.bit_count())
                #maxTerm_.append((val, symMask, op_[2], minVal))
                #return

            pathVal += val
            pathSymMask |= symMask

            temp = self._tempList[tempMask.bit_length() - 1]
            #for op_i in temp[1]:
            #    # IDEA: Check if a (short) un-rolled list exists for that temp?
            #    rollOut(maxTerm_, op_i, pathVal, pathSymMask, depth_+1)
            if any(rollOut(maxTerm_, op_i, compOp_, pathVal, pathSymMask, branch_, depth_+1) for op_i in temp[1]):
                return True
            
            return False


        #TODO: Debug: DELETE
        def printTerm(term_):
            ret = "[ "
            for e in term_:
                ret += f"({e[0]}, "
                ret += f"{e[1]:b}, "
                ret += f"{e[2]:b}, "
                ret += f"{e[3]}) "
            ret += "]"
            return ret

        prunedKey = None
        if temp is None:
            maxTerm = []

            #print(f"Input {printTerm(ops_)}")

            if rollOut(maxTerm, ops_[0], ops_[1], 0, 0, 0):
                self._myTest[opKey] = ops_[0]
                return ops_[0] # TODO: Mark in some list
            if (rollOut(maxTerm, ops_[1], ops_[0], 0, 0, 1)):
                self._myTest[opKey] = ops_[1]
                return ops_[1] # TODO: Mark in some list

            #for op_i in ops_:
            #    rollOut(maxTerm, op_i, 0, 0)

            #print(f"Unrolled: {printTerm(maxTerm)}")
            
            #maxTerm.sort(key=lambda e: -e[3]) # Sort decreasing minVal
            ##print(f"Sorted: {maxTerm}")
            #prunedMaxTerm = []
            #for elem_i in maxTerm:
            #    if not any(( (dom_i[1] & elem_i[1]) == elem_i[1] and (dom_i[2] & elem_i[2]) == elem_i[2]) for dom_i in prunedMaxTerm):
            #        prunedMaxTerm.append(elem_i)
            

            def dominates(dom_, elem_):
                if dom_[3] >= elem_[3]:
                    if((dom_[1] & elem_[1]) == elem_[1] and (dom_[2] & elem_[2]) == elem_[2]):
                        return True

            prunedMaxTerm = []
            for i, elem_i in enumerate(maxTerm):
                insert = True
                for ii, dom_i in enumerate(maxTerm):
                    if i == ii:
                        continue
                    if (dom_i == elem_i):
                        if i > ii:
                            insert = False
                            break
                        else:
                            continue

                    if dom_i[3] >= elem_i[3]:
                        if ((dom_i[1] & elem_i[1]) == elem_i[1] and (dom_i[2] & elem_i[2]) == elem_i[2]):
                            insert = False
                            break

                if insert:
                    prunedMaxTerm.append(elem_i)


#            #maxTerm.sort(key=lambda e: -e[3])
#            prunedMaxTerm = []
#            for i, elem_i in enumerate(maxTerm):
#                insert = True
#                #for j in range(i+1, len(maxTerm)):
#                #    dom_i = maxTerm[j]
#                for ii, dom_i in enumerate(maxTerm):
#                    if i == ii:
#                        continue
#
#                    if dom_i[3] >= elem_i[3]:
#                        if ((dom_i[1] & elem_i[1]) == elem_i[1] and (dom_i[2] & elem_i[2]) == elem_i[2]):
#                            insert = False
#                            break
#                if insert:
#                    prunedMaxTerm.append(elem_i)

#            if len(prunedMaxTerm) == 0:
#                print(f"Input {printTerm(ops_)}")
#                print(f"Unrolled: {printTerm(maxTerm)}")
#                print(f"Pruned: {printTerm(prunedMaxTerm)}")
#                print(f"New List: {printTerm(newList)}")

            #print(f"Pruned: {printTerm(prunedMaxTerm)}")

#            commonVal = None
#            commonSymMask = None
#            for elem_i in maxTerm:
#                if commonVal is None:
#                    commonVal = elem_i[0]
#                    commonSymMask = elem_i[1]
#                else:
#                    commonVal = min(commonVal, elem_i[0])
#                    commonSymMask &= elem_i[1]
#
#                if commonVal == 0 and commonSymMask == 0:
#                    break
#
#            if not (commonVal == 0 and commonSymMask == 0):
#                print(f"Pruned: {prunedMaxTerm}")
#                print(f"Common value: {commonVal}, Common symMask: {commonSymMask}")
#                print()


            prunedKey = frozenset(prunedMaxTerm)

            if len(prunedMaxTerm) == 2:
                #opKey = frozenset(prunedMaxTerm)
                #temp = self._tempDict.get(opKey)
                temp = self._tempDict.get(prunedKey)
                if temp is not None:
                    self._tempDict[opKey] = temp
                    MaxPlusLib._stat_dupHit += 1
                else:
                    
                    # Use the pruned-set instead of the original operands
                    ops_ = prunedMaxTerm
                    opKey = frozenset(ops_)

            elif len(prunedMaxTerm) == 1:
                MaxPlusLib._stat_fullRed += 1
                self._myTest[opKey] = prunedMaxTerm[0]
                return prunedMaxTerm[0]  # TODO: Mark in some list
            elif len(prunedMaxTerm) < 1:
                raise RuntimeError("EMPTY MAX-TERM?")
            else:
                #temp = self._myTest.get(prunedKey)
                temp = self._tempDict.get(prunedKey)
                if temp is not None:
                    self._tempDict[opKey] = temp
                    MaxPlusLib._stat_dupHit += 1

        # Check if duplicate of an existing temp: New temp can be expressed by op_a_
        
#        oldDbg = []
#        tempOLD = None
#        
#        if temp is None:
#            val_a = ops_[0][0]
#            symMask_a = ops_[0][1]
#            tempMask_a = ops_[0][2]
#            #if (val_a == 0) and (symMask_a == 0):
#            if (val_a == 0) and (symMask_a == 0) and (tempMask_a.bit_count() == 1):
#            #if (val_a == 0) and (symMask_a == 0) and (tempMask_a != 0) and ((tempMask_a & (tempMask_a - 1)) == 0): # Check if tempMask_a is a power of two (i.e. only one bit set)
#                subTemp_a = self._tempList[tempMask_a.bit_length()-1]
#                if self.__checkDuplicate(subTemp_a, ops_[1]):
#                    tempOLD = subTemp_a
#                    self._tempDict[opKey] = tempOLD
#                    MaxPlusLib._stat_dupHit += 1
#                    oldDbg.append(ops_[0])
#
#        # Check if duplicate of an existing temp: New temp can be expressed by op_b_
#        if temp is None and (tempOLD is None):
#            val_b = ops_[1][0]
#            symMask_b = ops_[1][1]
#            tempMask_b = ops_[1][2]
#            #if (val_b == 0) and (symMask_b == 0):
#            if (val_b == 0) and (symMask_b == 0) and (tempMask_b.bit_count() == 1):
#                subTemp_b = self._tempList[tempMask_b.bit_length()-1]
#                if self.__checkDuplicate(subTemp_b, ops_[0]):
#                    tempOLD = subTemp_b
#                    self._tempDict[opKey] = tempOLD
#                    MaxPlusLib._stat_dupHit += 1
#                    oldDbg.append(ops_[1])      


#        if (tempNEW is None) and (tempOLD is not None):
#            MaxPlusLib._stat_hitOLD += 1
#            temp = tempOLD
#            print("+"*50)
#            for t in self._tempList:
#                print(f"t_{t[0]}: {t[1]}")
#            print("+"*50)
#            print(f"Input {printTerm(ops_)}")
#            print(f"Unrolled: {printTerm(maxTerm)}")
#            print(f"Pruned: {printTerm(prunedMaxTerm)}")
#            print(f"OLD: {printTerm(oldDbg)}")
#            
#            print("+"*50)
#            print()
#            raise RuntimeError("TRAP")
#        elif(tempNEW is not None) and (tempOLD is None):
#            MaxPlusLib._stat_hitNEW += 1
#            temp = tempNEW
#
#        if temp is None:
#            if tempNEW is not None:
#                temp = tempNEW
#            elif tempOLD is not None:
#                temp = tempOLD

        # Create a new temp
        if temp is None:
            minVal = max(ops_[0][3], ops_[1][3])
            temp = (self._tempCnt, [ops_[0], ops_[1]], minVal)
            self._tempDict[opKey] = temp
            self._tempList.append(temp)

            #self._myTest[prunedKey] = temp
            self._tempDict[prunedKey] = temp

            self._tempCnt += 1
            MaxPlusLib._stat_newTemp += 1
            if self._tempCnt > MaxPlusLib._stat_maxTempsPerInstance:
                MaxPlusLib._stat_maxTempsPerInstance = self._tempCnt

        MaxPlusLib._stat_time += time.perf_counter() - _t0

        return  (0, 0, 1 << temp[0], temp[2])



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

        self.zeroElement = False

        if type(elem_) is int:
            if elem_ == -1:
                self.zeroElement = True
            self.value = elem_
            
        elif type(elem_) is tuple:
            
            self.value = elem_[0]
            self.symbolMask = elem_[1]
            self.tempMask = elem_[2]

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

    def getKey(self):
        return (self.value, self.symbolMask, self.tempMask)
    
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

    def __init__(self, id_:int, elems_:tuple):
        self.id = id_
        self.elements = [MaxPlusElement(e) for e in elems_]

    def getExpressions(self):
        return [e.getExpression() for e in self.elements]

#    def getId(self):
#        return self.id
#
    def forAllTempMasks(self):
        for e_i in self.elements:
            yield e_i.getTempMask()
#
#    def getExpression(self, sep_=","):
#        ret = ""
#        setSep = False
#        for e_i in self.elements:
#            if (e := e_i.getExpression()) == "":
#                raise RuntimeError("MaxPlusTemp with an empty element. This should never happen!")
#            else:
#                if setSep == False:
#                    setSep = True
#                else:
#                    ret += sep_
#                ret += e
#        return ret
#    
#    def getSplitExpression(self):
#        return [e.getExpression() for e in self.elements]


