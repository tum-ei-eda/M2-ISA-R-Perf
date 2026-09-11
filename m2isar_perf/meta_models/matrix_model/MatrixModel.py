#
# Copyright 2026 Chair of EDA, Technical University of Munich
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#	 http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from meta_models.common.FrozenBase import FrozenBase
#from .MaxPlusLib import SumOfProducts as SoP
#from .MaxPlusLib import mp_mul

#from .MaxPlusLib2 import SumOfProducts as SoP
#from .MaxPlusLib2 import mp_mul, mp_add

from .MaxPlusLib import SumOfProducts as SoP
from .MaxPlusLib import mp_mul, mp_add, mp_create_sop

from .MaxPlusLib_NEW import MaxPlusLib

from typing import List, Dict, Tuple
from itertools import product, chain

import time # TODO: Debug

class MatrixModel(FrozenBase):

    def __init__(self, name_:str):
        self.name = name_

        # Owned instances
        self.variants:List[Variant] = []

        super().__init__()

    def createVariant(self, name_:str) -> 'Variant':
        variant = Variant(name_, self)
        self.variants.append(variant)
        return variant
    
    def getAllVariants(self) -> List['Variant']:
        return self.variants
    
class Variant(FrozenBase):

    def __init__(self, name_:str, parent_:'MatrixModel'):
        self.name = name_
        self.parent = parent_
        
        self.dimension = 0

        # Owned instances
        self.instructions:Dict[int, Instruction] = {}
        self.timingVarSet = None
        self.statConSets = []
        self.branchSet = None
        self.resourceGroups:Dict[str, ResourceGroup] = {}
        self.branchGroup = None
        self.resourceCombinations:List[ResourceCombination] = []
        self.combinations:List[Combination] = []

        # Look-up
        self.inVariables:Dict[InVariable] = {}
        self.outVariables:Dict[OutVariable] = {}

        # Pre-computed members
        self.staticColumnVarIdxPairs = []

        # Internal state
        self.currentColVarIdxPairs = []

        super().__init__()

    def finalize(self):
        self.staticColumnVarIdxPairs.extend(self.timingVarSet.columnVarIdxPairs)
        self.staticColumnVarIdxPairs.extend(self.branchSet.columnVarIdxPairs)

    def getParentModel(self):
        return self.parent

    def createInstruction(self, name_:str, typeId_:int) -> 'Instruction':
        instr = Instruction(name_, typeId_, self)
        if typeId_ in self.instructions:
            raise RuntimeError(f"Cannot add instruction {name_} with type-ID {typeId_}. Type-ID is already registered.")
        self.instructions[typeId_] = instr
        return instr
    
    def createResourceGroup(self, name_:str) -> 'ResourceGroup':
        resGr = ResourceGroup(name_, len(self.resourceGroups))
        if name_ in self.resourceGroups:
            raise RuntimeError(f"Cannot add resource-group {name_}. Name is already registered.")
        self.resourceGroups[name_] = resGr
        return resGr
    
    def createBranchGroup(self) -> 'BranchGroup':
        self.branchGroup = BranchGroup()
        return self.branchGroup
    
    def createAllResourceCombinations(self):
        for resModComb_i in product(*(g.getAllModels() for g in self.getAllResourceGroups())):
            self.resourceCombinations.append(ResourceCombination(len(self.resourceCombinations), resModComb_i))

    def createAllCombinations(self):
        for brMod_i in self.getBranchGroup().getAllModels():
            for resComb_i in self.getAllResourceCombinations():
                self.combinations.append(Combination(len(self.combinations), brMod_i, resComb_i))
    
    def addInVariable(self, var_:'InVariable'):
        if var_.name in self.inVariables:
            raise RuntimeError(f"Trying to add in-variable {var_.name} to {self.name}, but variable already exists.")
        self.inVariables[var_.name] = var_

    def addOutVariable(self, var_:'OutVariable'):
        if var_.name in self.outVariables:
            raise RuntimeError(f"Trying to add out-variable {var_.name} to {self.name}, but variable already exists.")
        self.outVariables[var_.name] = var_

    def getNumInVariables(self):
        return len(self.inVariables)
    
    def getNumOutVariables(self):
        return len(self.outVariables)

    def addTimingVariable(self, name_:str, numElements_:int):
        self.timingVarSet.createTimingVariable(name_, numElements_)

    def createTimingVariableSet(self, tVars_:List[Tuple[str, int]]):
        if (len(self.statConSets) != 0) or (self.branchSet is not None):
            raise RuntimeError("Trying to create TimingVariableSet, but other set(s) already exist. Create TimingVariableSet first!")
        elif self.timingVarSet is not None:
            raise RuntimeError("Trying to create TimingVariableSet, but set already exists!")
        
        self.timingVarSet = TimingVariableSet(self)
        for var_i, numElem_i in tVars_:
            self.timingVarSet.createTimingVariable(var_i, numElem_i)

        self.dimension += self.timingVarSet.size
        return self.timingVarSet.finalize()

    def addStaticConnectorSet(self, name_:str, inVars_:List[Tuple[str,str]], outVars_:List[Tuple[str,str]], size_:int, except_:List[int]=[]):
        
        if self.timingVarSet is None:
            raise RuntimeError(f"Trying to add StaticConnectorSet ({name_}) before TimingVariableSet. Create TimingVariableSet first!")
        elif self.branchSet is not None:
            raise RuntimeError(f"Trying to add StaticConnectorSet ({name_}), but BranchSet already exists. Add StaticConnectorModels first!")
        
        statConSet = StaticConnectorSet(name_, size_, self.dimension, self)
        for var_i, trVal_i in inVars_:
            statConSet.createInVariable(var_i, trVal_i, except_)
        for var_i, trVal_i in outVars_:
            statConSet.createOutVariable(var_i, trVal_i, except_)
    
        self.dimension += size_
        self.statConSets.append(statConSet)
        return statConSet.finalize()  

    def createBranchSet(self, inVars_:List[str], outVars_:List[str]):
        
        if self.timingVarSet is None:
            raise RuntimeError("Trying to create BranchSet before TimingVariableSet. Create TimingVariableSet first!")
        elif self.branchSet is not None:
            raise RuntimeError("Trying to create BranchSet, but BranchSet already exists!")
        
        self.branchSet = BranchSet(self.dimension, self)
        for inVar_i in inVars_:
            self.branchSet.createInVariable(inVar_i)
        for outVar_i in outVars_:
            self.branchSet.createOutVariable(outVar_i)
        
        self.branchSet.finalize()
        self.dimension += self.branchSet.numVariables
        return self.branchSet

    def getInVariable(self, name_):
        if name_ not in self.inVariables:
            raise RuntimeError(f"In-variable {name_} does not exist for {self.name}")
        return self.inVariables[name_]
    
    def getOutVariable(self, name_):
        if name_ not in self.outVariables:
            raise RuntimeError(f"Out-variable {name_} does not exist for {self.name}")
        return self.outVariables[name_]

    def getAllInVariables(self):
        return list(self.inVariables.values())
    
    def getAllOutVariables(self):
        return list(self.outVariables.values())
    
    #def getAllOutVarIdxs(self):
    #    return list(self.outVariables.values().idx)
    
    def getDimension(self):
        return self.dimension
        #return self.timingVarSet.size + self.regSet.size + self.branchSet.getNumVariables()
    
    def getNumTimingVariables(self):
        return self.timingVarSet.size

    def updateColumnVarIdxPairs(self, instrDescription_):
        dynamicColVarIdxPairs = [
            pair
            for statConSet_i in self.statConSets
            for pair in statConSet_i.getColumnVarIdxPairs(instrDescription_)
        ]
        self.currentColVarIdxPairs = self.staticColumnVarIdxPairs + dynamicColVarIdxPairs

    def getAllColumnVarIdxPairs(self):
        return self.currentColVarIdxPairs

    def getColumn2VarIdxMap(self):
        col2VarIdxMap = [None]*self.dimension
        for (col_i, idx_i) in self.currentColVarIdxPairs:
            col2VarIdxMap[col_i] = idx_i
        return col2VarIdxMap

    def getInstruction(self, typeId_:int) -> 'Instruction':
        return self.instructions[typeId_]
    
    def getAllInstructions(self) -> List['Instruction']:
        return sorted(self.instructions.values(), key=lambda x: x.typeId)
    
    def getResourceGroup(self, resGrName_) -> 'ResourceGroup':
        if resGrName_ not in self.resourceGroups:
            raise RuntimeError(f"Cannot find resource-group {resGrName_}. Name not registered with variant {self.name}")
        return self.resourceGroups[resGrName_]
    
    def getAllResourceGroups(self) -> List['ResourceGroup']:
        return sorted(self.resourceGroups.values(), key=lambda x: x.id)
    
    def getBranchGroup(self) -> 'BranchGroup':
        return self.branchGroup
    
    def getAllResourceCombinations(self) -> List['ResourceCombination']:
        return self.resourceCombinations

    def getAllCombinations(self) -> List['Combination']:
        return self.combinations
    
    def getNumInstructions(self) -> int:
        return len(self.instructions)

    def getNumResourceGroups(self) -> int:
        return len(self.resourceGroups)

    def getNumResourceCombinations(self) -> int:
        return len(self.resourceCombinations)

    def getNumCombinations(self) -> int:
        return len(self.combinations)

    def getMaxDynDelayPerInstr(self) -> int:
        cnt = None
        for instr_i in self.instructions.values():
            if cnt is None:
                cnt = instr_i.getNumDynDelays()
            else:
                cnt = max(cnt, instr_i.getNumDynDelays())
        return cnt
    
    # TODO: Debug. Delete?
    # TODO: Cleaner if this would be a member-function of Instruction-class?
    def showMatrix(self, matrix_):

        mp = MaxPlusLib() # TODO: Where to implement this?

        names = [v.name for v in self.timingVarSet.inVariables]
        for statConSet_i in self.statConSets:
            name = statConSet_i.name
            for r in range(statConSet_i.size):
                names.append(name + str(r))
        #for r in range(self.regSet.size):
        #    names.append("R" + str(r))
        names.extend([v.name for v in self.branchSet.inVariables])
        names.extend([v.name for v in self.branchSet.outVariables])

        rowNameWidth = 0
        for rowName_i in names:
            rowNameWidth = max(rowNameWidth, len(rowName_i))

        dim = self.getDimension()

        colsWidths = [0] *dim
        for col_i in range(dim):
            colsWidths[col_i] = len(names[col_i])
            for row_i in range(dim):
                length = len(mp.str(matrix_[row_i][col_i]))
                #if isinstance((e := matrix_[row_i][col_i]), SoP):
                #    length = len(self.__stringSoP(e))
                #else:
                #    length = len(str(e))
                colsWidths[col_i] = max(colsWidths[col_i], length)

        x = ""
        print(f"{x:{rowNameWidth}}", end="")
        for col_i in range(dim):
            print(f"|{names[col_i]:{colsWidths[col_i]}}", end="")
        print()
        
        for row_i in range(dim):
            print(f"{names[row_i]:{rowNameWidth}}", end="")
            for col_i in range(dim):
                print(f"|{mp.str(matrix_[row_i][col_i]):{colsWidths[col_i]}}", end="")
                #if isinstance((e := matrix_[row_i][col_i]), SoP):
                #    print(f"|{self.__stringSoP(e):{colsWidths[col_i]}}", end="")
                #else:
                #    print(f"|{str(e):{colsWidths[col_i]}}", end="")
            print()
        print()

    # TODO: Helper function to print List-style SoP. Remove later?
    # TODO: If keep, move to MaxPlusLib
    def __stringSoP(self, sop_):
        retStr = ""
        if len(sop_) > 1:
            retStr += "("
            skipOperand = True
            for p_i in sop_:
                if skipOperand:
                    skipOperand = False
                else:
                    retStr += "+"
                retStr += self.__stringProduct(p_i)
            retStr += ")"
        else:
            retStr += self.__stringProduct(sop_[0])
        return retStr
    
    # TODO: Sub-Helper function to print List-style SoP. Remove later?
    # TODO: If keep, move to MaxPlusLib
    def __stringProduct(self, prod_):
        #val, symMask, _ = prod_
        val = prod_[0]
        symMask = prod_[1]
        retStr = ""
        if val != 0:
            retStr += str(val)
        symIdxs = [i for i in range(symMask.bit_length()) if (symMask >> i) & 1]
        for s_i in symIdxs:
            retStr += f"d{s_i}"
        return retStr

class TimingVariableSet(FrozenBase):

    def __init__(self, parent_):
        self.size = 0
        self.parent = parent_
        
        # Owned instances
        self.inVariables:List['InVariable'] = []
        self.outVariables:List['OutVariable'] = []

        # Pre-computed members
        self.rowVarIdxPairs = []
        self.columnVarIdxPairs =[]
    
    def createTimingVariable(self, name_:str, numElements_:int):

        if numElements_ > 1:
            for i in range(numElements_):
                name = f"{name_}__{i+1}"
                
                # If not explicitly set, buffer variables are shifted (e.g. EX__2 -> EX__3)
                defaultSetCol = self.size-1 if i > 0 else self.size
                
                inVar = InVariable(name, self.size)
                outVar = OutVariable(name, self.size, defaultSetCol_=defaultSetCol)
                self.parent.addInVariable(inVar)
                self.parent.addOutVariable(outVar)
                self.inVariables.append(inVar)
                self.outVariables.append(outVar)
                self.size += 1

        else:
            inVar = InVariable(name_, self.size)
            outVar = OutVariable(name_, self.size, defaultSetCol_=self.size)
            self.parent.addInVariable(inVar)
            self.parent.addOutVariable(outVar)
            self.inVariables.append(inVar)
            self.outVariables.append(outVar)
            self.size += 1

    def finalize(self):
        #self.outVarIdxs = [x.idx for x in self.outVariables]
        self.rowVarIdxPairs = list(enumerate([x.idx for x in self.outVariables]))
        #self.columnVariablePairs = list(enumerate(self.inVariables))
        self.columnVarIdxPairs = list(enumerate([x.idx for x in self.inVariables]))
        return self

class StaticConnectorSet(FrozenBase):

    def __init__(self, name_:str, size_:int, offset_:int, parent_:'Variant'):
        self.name = name_
        self.size = size_
        #self.offset = offset_
        self.parent = parent_

        self.colOffset = offset_
        self.rowOffset = offset_

        #Owned instances
        self.inVariables:List['InVariable'] = []
        self.outVariables:List['OutVariable'] = []

        # Pre-computed members
        self.allCols = []
        self.allRows = []

    def createInVariable(self, name_:str, trVal_:str, except_:List[int]=[]):
        inVar = InVariable(name_, self.parent.getNumInVariables(), trVal_=trVal_, except_=except_)
        self.parent.addInVariable(inVar)

        self.inVariables.append(inVar)
        return inVar

    def createOutVariable(self, name_:str, trVal_:str, except_:List[int]=[]):
        outVar = OutVariable(name_, self.parent.getNumOutVariables(), trVal_=trVal_, except_=except_)
        self.parent.addOutVariable(outVar)

        self.outVariables.append(outVar)
        return outVar

    def finalize(self):
        self.allCols = list(range(self.colOffset, self.colOffset + self.size))
        self.allRows = list(range(self.rowOffset, self.rowOffset + self.size))
        return self
    
    def getColumnVarIdxPairs(self, instrDescription_=Dict) -> List[Tuple[int, int]]:
        ret = []
        for iVar_i in self.inVariables:
            if (col := iVar_i.map2Col(instrDescription_)) is not None:
                ret.append((col + self.colOffset, iVar_i.idx))
        return ret

class BranchSet(FrozenBase):

    def __init__(self, offset_:int, parent_:'Variant'):
        self.offset = offset_
        self.parent = parent_

        self.colOffsetIn = offset_
        self.rowOffsetIn = offset_

        # Owned instances
        self.inVariables:List[InVariable] = []
        self.outVariables:List[OutVariable] = []

        # Pre-computed members
        self.numVariables = 0
        self.rowOffsetOut = 0
        self.colOffsetOut = 0
        self.rowVarIdxPairsOut = []
        self.rowVarIdxPairsIn = []
        self.columnVarIdxPairs = []

        super().__init__()

    def createInVariable(self, name_:str):
        inVar = InVariable(name_, self.parent.getNumInVariables())
        self.parent.addInVariable(inVar)
        
        self.inVariables.append(inVar)
        return inVar

    def createOutVariable(self, name_:str):
        outVar = OutVariable(name_, self.parent.getNumOutVariables())
        self.parent.addOutVariable(outVar)

        self.outVariables.append(outVar)
        return outVar

    def finalize(self):
        self.numVariables = len(self.inVariables) + len(self.outVariables)
        self.rowOffsetOut = self.rowOffsetIn + len(self.inVariables)
        self.colOffsetOut = self.colOffsetIn + len(self.inVariables)
        self.columnVarIdxPairs = [(c + self.colOffsetIn, v.idx) for (c,v) in enumerate(self.inVariables)]
        self.rowVarIdxPairsOut = [(r + self.rowOffsetOut, v.idx) for (r,v) in enumerate(self.outVariables)]
        self.rowVarIdxPairsIn = [(r + self.rowOffsetIn, v.idx) for (r, v) in enumerate(self.inVariables)]
        return self
    
class Variable(FrozenBase):

    # "Virtual Class"

    def __init__(self, name_:str, idx_:int, trVal_="UNDEFINED", except_:List[int]=[]):
        self.name = name_
        self.idx = idx_
        self.traceValue = trVal_
        self.exceptions = except_

class InVariable(Variable):

    def __init__(self, name_:str, idx_:int, trVal_:str="UNDEFINED", except_:List[int]=[]):

        super().__init__(name_, idx_, trVal_, except_)

    def getGraphName(self):
        return self.name + "_i"
    
    def map2Col(self, instrDescription_:Dict) -> int:
        # TODO: Return None in case that no value is registered for this trace value (e.g.: No RS2 register)
        #return instrDescription_[self.traceValue]
        col = instrDescription_[self.traceValue]
        if col in self.exceptions:
            return None
        return col

class OutVariable(Variable):

    def __init__(self, name_:str, idx_:int, trVal_:str="UNDEFINED", defaultSetCol_:int=-1, except_:List[int]=[]):
        self.defaultSetCol = defaultSetCol_
        self.defaultIsUnitRow = (defaultSetCol_ == idx_)
        self.defaultIsZeroRow = (defaultSetCol_ == -1)
        self.defaultUnitShift = None if (self.defaultIsZeroRow) else (defaultSetCol_ - idx_) 

        super().__init__(name_, idx_, trVal_, except_)

    def getGraphName(self):
        return self.name + "_o"
    
    def map2Row(self, instrDescription_:Dict) -> int:
        # TODO: Return None in case that no value is registered for this trace value (e.g.: No RD register)
        #return instrDescription_[self.traceValue]
        row = instrDescription_[self.traceValue]
        if row in self.exceptions:
            return None
        return row

    def getDefaultRow(self, numCols_:int):
        row = [-1]*numCols_
        if self.defaultSetCol != -1:
            row[self.defaultSetCol] = 0
        return row

class Instruction(FrozenBase):

    def __init__(self, name_:str, typeId_:int, parent_:'Variant'):
        self.name = name_
        self.typeId = typeId_
        self.parent = parent_
        self.compInstrMatrix = CompressedInstructionMatrix(self, self.parent)
        self.dynamicDelays:List[DynamicDelay] = []

        # TODO: DBG. DELETE
        self.mulTime = 0
        self.addTime = 0

    def getInfo(self):
        return (self.mulTime, self.addTime)

    def getCompressedInstructionMatrix(self):
        return self.compInstrMatrix
    
    def createDynamicDelay(self, resGrName_:str, condition_:Tuple[str, List[str], int]=None):
        dynDelay = DynamicDelay(len(self.dynamicDelays), self.parent.getResourceGroup(resGrName_), condition_)
        self.dynamicDelays.append(dynDelay)
        return dynDelay
    
    def getNumDynDelays(self):
        return len(self.dynamicDelays)
    
    def getDynamicDelay(self, idx_:int) -> 'DynamicDelay':
        return self.dynamicDelays[idx_]
    
    def getMatrix(self, instrDescription_:Dict, dynDelayCnt_:int=0) -> 'BlockMatrix':

        variant = self.parent

        cInstrMatrix = self.getCompressedInstructionMatrix()
        cInstrData = cInstrMatrix.getResolvedMatrix(dynDelayCnt_, instrDescription_=None) # NOTE: Currently not allowed to evaluate condition of dynamic delays if first instruction in a block

        #print("----")
        #print()
        #print(cInstrData)

        blkMatrix = BlockMatrix(variant.getDimension(), -1)
        matrix = blkMatrix.matrix

        variant.updateColumnVarIdxPairs(instrDescription_)
        colVarIdxPairs = variant.getAllColumnVarIdxPairs()

        # Assign rows associated with timing variables
        for row_i, oVarIdx_i in variant.timingVarSet.rowVarIdxPairs:
            if cInstrMatrix.isStandardRow(oVarIdx_i):
                if cInstrMatrix.isUnitRow(oVarIdx_i):
                    blkMatrix.addUnitRow(row_i)
                    matrix[row_i][row_i] = 0
                elif (s := cInstrMatrix.getUnitShift(oVarIdx_i)) is not None:
                    blkMatrix.addSetRow(row_i)
                    matrix[row_i][row_i + s] = 0
                else:
                    raise RuntimeError("Unexpected standard-row for TimingVariable-Set")
            else:
                instrRow = cInstrData[oVarIdx_i]
                for (col_i, iVarIdx_i) in colVarIdxPairs:
                    matrix[row_i][col_i] = instrRow[iVarIdx_i]

        # Assign rows associated with static-connectors (i.e. registers, reg-flags, etc.)
        for statConSet_i in variant.statConSets:
            blkMatrix.addUnitColumns(statConSet_i.allCols)

            unitRowRanges = []
            rangeStart = statConSet_i.rowOffset
            for oVar_i in statConSet_i.outVariables:
                if(row := oVar_i.map2Row(instrDescription_)) is not None:
                    row += statConSet_i.rowOffset

                    unitRowRanges.append(range(rangeStart, row))
                    rangeStart = row + 1

                    blkMatrix.unit2ZeroColumn(row) # NOTE: Assuming symmetrical NxN matrix here
                    
                    instrRow = cInstrData[oVar_i.idx]
                    for (col_i, iVarIdx_i) in colVarIdxPairs:
                        matrix[row][col_i] = instrRow[iVarIdx_i]

            unitRowRanges.append(range(rangeStart, statConSet_i.rowOffset + statConSet_i.size))

            # Remove unit/zero col, if col is associated with input-variable (i.e. source register)
            for iVar_i in statConSet_i.inVariables:
                if(idx := iVar_i.map2Col(instrDescription_)) is not None:
                    idx += statConSet_i.colOffset
                    blkMatrix.clearColumn(idx)
                    #blkMatrix.removeUnitColumn(idx)
                    #blkMatrix.removeZeroColumn(idx)

            # Set remaining rows to unit-row
            for row_i in chain.from_iterable(unitRowRanges):
                blkMatrix.addUnitRow(row_i)
                matrix[row_i][row_i] = 0

        # Assign rows associated with branch out-variables
        for row_i, oVarIdx_i in variant.branchSet.rowVarIdxPairsOut:
            blkMatrix.addZeroColumn(row_i) # NOTE: Assuming symmetrical NxN matrix here
            
            if cInstrMatrix.isStandardRow(oVarIdx_i):
                if cInstrMatrix.isZeroRow(oVarIdx_i):
                    blkMatrix.addZeroRow(row_i)
                    continue
                else:
                    raise RuntimeError("Unexpected standard-row for Branch-Set")
            else:
                instrRow = cInstrData[oVarIdx_i]
                for (col_i, iVarIdx_i) in colVarIdxPairs:
                    matrix[row_i][col_i] = instrRow[iVarIdx_i]

        # Set rows associated with branch in-variables to zero-rows
        for row_i, _ in variant.branchSet.rowVarIdxPairsIn:
            blkMatrix.addZeroRow(row_i)

        return blkMatrix

    def mulMatrix(self, blkMatrix_:'BlockMatrix', instrDescription_:Dict, dynDelayCnt_:int, mpLib_:'MaxPlusLib', verbose_:bool=False) -> 'BlockMatrix':
        
        variant = self.parent

        cInstrMatrix = self.getCompressedInstructionMatrix()
        cInstrData = cInstrMatrix.getResolvedMatrix(dynDelayCnt_, instrDescription_=instrDescription_)

        #print("----")
        #print()
        #print(cInstrData)

        dim = blkMatrix_.dimension
        matrix = blkMatrix_.matrix

        newBlkMatrix = BlockMatrix(blkMatrix_.dimension, -1)
        newMatrix = newBlkMatrix.matrix
        newBlkMatrix.assignMasks(blkMatrix_)

        #self.mulTime = 0
        #self.addTime = 0

        def updateVal(val_, a_, j_, col_):
            if (a_ != -1) and ((b := matrix[j_][col_]) != -1):
                #t1 = time.time()
                p = mpLib_.mul(a_, b)
                #t2 = time.time()
                #self.mulTime += (t2-t1)
                val_ = mpLib_.add(val_, p)
                #self.addTime += (time.time() - t2)
            return val_

        variant.updateColumnVarIdxPairs(instrDescription_)
        colVarIdxPairs = variant.getAllColumnVarIdxPairs()
        col2VarIdxMap = variant.getColumn2VarIdxMap()

        if verbose_:
            for x in colVarIdxPairs:
                print(x)
            print("-----")
            print(f"blkMatrix unit-cols: {blkMatrix_.getUnitColIdxs()}")
            print(f"blkMatrix zero-cols: {blkMatrix_.getZeroColIdxs()}")

        # Compute rows associated with timing variables
        for row_i, oVarIdx_i in variant.timingVarSet.rowVarIdxPairs:
            if cInstrMatrix.isStandardRow(oVarIdx_i):
                if cInstrMatrix.isUnitRow(oVarIdx_i):
                    newMatrix[row_i] = matrix[row_i]
                elif (s := cInstrMatrix.getUnitShift(oVarIdx_i)) is not None:
                    newBlkMatrix.clearRow(row_i)
                    #newBlkMatrix.removeUnitRow(row_i)
                    #newBlkMatrix.removeSetRow(row_i)
                    if (blkMatrix_.isUnitRow(row_i+s) or blkMatrix_.isSetRow(row_i+s)):
                        newBlkMatrix.addSetRow(row_i)
                    newMatrix[row_i] = matrix[row_i + s]
                else:
                    raise RuntimeError("Unexpected standard-row for TimingVariable-Set")
            else:
                newBlkMatrix.clearRow(row_i)
                #newBlkMatrix.removeUnitRow(row_i)
                #newBlkMatrix.removeSetRow(row_i)
                instrRow = cInstrData[oVarIdx_i]
                for col_i in range(dim):
                    
                    verbose2 = False
                    if verbose_:
                        if col_i == 79:
                            print(f" >> [{row_i}][{col_i}] -> ", end="")
                            verbose2 = True

                    if blkMatrix_.isZeroColumn(col_i):
                        
                        if verbose2:
                            print("zero column")

                        continue
                    elif blkMatrix_.isUnitColumn(col_i):

                        if verbose2:
                            print(f"unit column")

                        # TODO: Check if correct. Then make faster!
                        #for (x, iVarIdx_i) in colVarIdxPairs:
                        #    if x == col_i:
                        #        newMatrix[row_i][col_i] = cInstrData[oVarIdx_i][iVarIdx_i]
                        #        break

                        if (iVarIdx := col2VarIdxMap[col_i]) is not None:
                            newMatrix[row_i][col_i] = cInstrData[oVarIdx_i][iVarIdx]

                        #newMatrix[row_i][col_i] = cInstrData[oVarIdx_i][????]

#                        if verbose2:
#                            print(f"unit column ({matrix[row_i][col_i]})")
#
#                        newMatrix[row_i][col_i] = matrix[row_i][col_i]
                    else:
                        val = -1
                        for (j, iVarIdx_i) in colVarIdxPairs:
                            val = updateVal(val, instrRow[iVarIdx_i], j, col_i)
                        newMatrix[row_i][col_i] = val

                        if verbose2:
                            print(f"update({val})")

        # Compute rows associated with static connectors (i.e. registers, reg-flags, etc.)
        for statConSet_i in variant.statConSets:

            # Remove unit/zero col, if col is associated with input-variable (i.e. source register)
            for iVar_i in statConSet_i.inVariables:
                if(idx := iVar_i.map2Col(instrDescription_)) is not None:
                    idx += statConSet_i.colOffset
                    #newBlkMatrix.removeUnitColumn(idx)
                    #newBlkMatrix.removeZeroColumn(idx)
                    newBlkMatrix.clearColumn(idx)


            unitRowRanges = []
            rangeStart = statConSet_i.rowOffset
            for oVar_i in statConSet_i.outVariables:
                if(row := oVar_i.map2Row(instrDescription_)) is not None:
                    row += statConSet_i.rowOffset
                    
                    unitRowRanges.append(range(rangeStart, row))
                    rangeStart = row + 1
                    
                    #verbose = (row == 40)
                    #if verbose:
                    #    print(f"Updating row: {row} | R[{oVar_i.map2Row(instrDescription_)}]")

                    newBlkMatrix.unit2ZeroColumn(row) # NOTE: Assuming symmetrical NxN matrix here
                    #newBlkMatrix.removeUnitRow(row)
                    newBlkMatrix.clearRow(row)

                    instrRow = cInstrData[oVar_i.idx]
                    #if verbose:
                    #    print(f"instrRow: {instrRow}")

                    for col_i in range(dim):
                        if newBlkMatrix.isZeroColumn(col_i):
                            continue
                        elif newBlkMatrix.isUnitColumn(col_i):

                            # TODO: Check if correct. Then make faster!
                            #for (x, iVarIdx_i) in colVarIdxPairs:
                            #    if x == col_i:
                            #        newMatrix[row_i][col_i] = cInstrData[oVarIdx_i][iVarIdx_i]
                            #        break

                            if (iVarIdx := col2VarIdxMap[col_i]) is not None:
                                newMatrix[row][col_i] = cInstrData[oVarIdx_i][iVarIdx]

                            #for (col_i, iVarIdx_i) in colVarIdxPairs:
                            #    newMatrix[row_i][col_i] = instrRow[iVarIdx_i]
                            #continue

                            #newMatrix[row][col_i] = matrix[row][col_i]
                        else:
                            val = -1
                            for (j, iVarIdx_i) in colVarIdxPairs:
                                val = updateVal(val, instrRow[iVarIdx_i], j, col_i)
                            newMatrix[row][col_i] = val
            unitRowRanges.append(range(rangeStart, statConSet_i.rowOffset + statConSet_i.size))

            # Rows not handled by loop above are unit-rows
            for row_i in chain.from_iterable(unitRowRanges):
                if newBlkMatrix.isUnitRow(row_i):
                    newMatrix[row_i][row_i] = 0
                else:
                    newMatrix[row_i] = matrix[row_i]

        # Compute rows associated with branch variables
        for row_i, oVarIdx_i in variant.branchSet.rowVarIdxPairsOut:
            if cInstrMatrix.isStandardRow(oVarIdx_i):
                if cInstrMatrix.isZeroRow(oVarIdx_i):
                    continue
                else:
                    raise RuntimeError("Unexpected standard-row for Branch-Set")
            else:
                #newBlkMatrix.removeZeroRow(row_i)
                newBlkMatrix.clearRow(row_i)
                instrRow = cInstrData[oVarIdx_i]
                for col_i in range(dim):
                    if blkMatrix_.isZeroColumn(col_i):
                        continue
                    elif blkMatrix_.isUnitColumn(col_i):
                        
                        
                        # TODO: Check if correct. Then make faster!
                        #for (x, iVarIdx_i) in colVarIdxPairs:
                        #    if x == col_i:
                        #        newMatrix[row_i][col_i] = cInstrData[oVarIdx_i][iVarIdx_i]
                        #        break
                        
                        if (iVarIdx := col2VarIdxMap[col_i]) is not None:
                            newMatrix[row_i][col_i] = cInstrData[oVarIdx_i][iVarIdx]
                        
                        #for (col_i, iVarIdx_i) in colVarIdxPairs:
                        #    newMatrix[row_i][col_i] = instrRow[iVarIdx_i]
                        #continue
                        
                        
                        #newMatrix[row_i][col_i] = matrix[row_i][col_i]
                    else:
                        val = -1
                        for (j, iVarIdx_i) in colVarIdxPairs:
                            val = updateVal(val, instrRow[iVarIdx_i], j, col_i)
                        newMatrix[row_i][col_i] = val

        return newBlkMatrix
    
    def getRequiredResourceGroups(self) -> List['ResourceGroup']:
        return [d.resourceGroup for d in self.dynamicDelays]

class DynamicDelay(FrozenBase):

    def __init__(self, id_:int, resGr_:'ResourceGroup', condition_:Tuple[str, List[str], int]=None):
        self.id = id_
        self.resourceGroup = resGr_
        self.condition = None if condition_ is None else Condition(condition_)

        super().__init__()

    #def isConditional(self) -> bool:
    #    return self.condition is not None
    
    def getCondition(self) -> 'Condition':
        return self.condition

class Condition(FrozenBase):

    def __init__(self, condition_:Tuple[str, List[str], int]):
        self.condition = condition_[0]
        self.traceValues = condition_[1] # TODO: Not needed??
        self.fixValue = condition_[2]

        self.compiled = compile(self.condition, "<condition>", "eval")

    def check(self, instrDescription_:Dict) -> bool:
        return eval(self.compiled, {}, instrDescription_)
    
    def getFixValue(self) -> int:
        return self.fixValue

class CompressedInstructionMatrix(FrozenBase):

    def __init__(self, parent_:'Instruction', parentVar_:'Variant'):
        self.parent = parent_
        self.parentVariant = parentVar_

        self.data = [[-1 for _ in range(self.parentVariant.getNumInVariables())] for _ in range(self.parentVariant.getNumOutVariables())]

        self.dynElemIdxs = []
        self.finalized = False

        self.stdRowMask = 0
        self.unitRowMask = 0
        self.zeroRowMask = 0
        self.unitShifts = [None]*self.parentVariant.getNumOutVariables()

        super().__init__()

    def addElement(self, inVar_:'InVariable', outVar_:'OutVariable', elem_):
        if self.finalized:
            raise RuntimeError("Trying to add element to CompressedInstructionMatrix after it has been finalized!")
        if isinstance(elem_, DynamicElement):
            elem_.setParentInstruction(self.parent)
        self.data[outVar_.idx][inVar_.idx] = elem_

    def addDefaultRow(self, outVar_:'OutVariable'):
        if self.finalized:
            raise RuntimeError("Trying to add default row to CompressedInstructionMatrix after it has been finalized!")
        row = outVar_.getDefaultRow(self.parentVariant.getNumInVariables())
        self.data[outVar_.idx] = row

        # Mark row as a standard-row
        self.stdRowMask |= (1 << outVar_.idx)
        if outVar_.defaultIsUnitRow:
            self.unitRowMask |= (1 << outVar_.idx)
        elif outVar_.defaultIsZeroRow:
            self.zeroRowMask |= (1 << outVar_.idx)
        elif (shift := outVar_.defaultUnitShift) is not None:
            self.unitShifts[outVar_.idx] = shift
        else:
            raise RuntimeError("Default row is added, but does not match any standard-row type")

    def finalize(self):
        self.finalized = True
        for i, row_i in enumerate(self.data):
            for j, elem_i in enumerate(row_i):
                if isinstance(elem_i, DynamicElement):
                    self.dynElemIdxs.append((i,j))

    def getElement(self, inVar_:'InVariable', outVar_:'OutVariable'):
        return self.data[outVar_.idx][inVar_.idx]
    
    def isStandardRow(self, idx_:int) -> bool:
        return self.stdRowMask & (1 << idx_)

    def isUnitRow(self, idx_:int) -> bool:
        return self.unitRowMask & (1 << idx_)

    def isZeroRow(self, idx_:int) -> bool:
        return self.zeroRowMask & (1 << idx_)
    
    def getUnitShift(self, idx_:int) -> int:
        return self.unitShifts[idx_]

    def getResolvedMatrix(self, dynDelayCnt_:int, instrDescription_=None):
        res = [row[:] for row in self.data]
        for row_i, col_i in self.dynElemIdxs:
            res[row_i][col_i] = res[row_i][col_i].resolve(dynDelayCnt_, instrDescription_)
        return res

    # TODO: DELETE
    def show(self):
        inVars = sorted(self.parentVariant.inVariables.values(), key=lambda x: x.idx)
        outVars = sorted(self.parentVariant.outVariables.values(), key=lambda x: x.idx)

        rowNameWidth = 0
        for oVar_i in outVars:
            rowNameWidth = max(rowNameWidth, len(oVar_i.name))
        rowNameWidth = int(rowNameWidth)

        colWidths = []
        for i, iVar_i in enumerate(inVars):
            w = len(iVar_i.name)
            for row_i in self.data:
                w = max(w, len(str(row_i[i])))
            colWidths.append(w)

        x = ""
        print(f"{x:{rowNameWidth}} ", end="")
        for i, iVar_i in enumerate(inVars):
            print(f"| {iVar_i.name:{colWidths[i]}} ", end="")
        print("")

        for oVar_i in outVars:
            print(f"{oVar_i.name:{rowNameWidth}} ", end="")
            for i, iVar_i in enumerate(inVars):
                print(f"| {str(self.data[oVar_i.idx][iVar_i.idx]):{colWidths[i]}} ", end="")
            print("")

class DynamicElement(FrozenBase):

    def __init__(self, orig_=None):
        self.mpElement = None
        self.symbolIdx = None
        if orig_ is not None:
            if type(orig_) is tuple:
                self.mpElement = orig_
            elif type(orig_) is DynamicDelay:
                self.symbolIdx = orig_.id
            else:
                raise RuntimeError("Unsupported object-type for generation of DynamicElement")

        self.parentInstr = None

        super().__init__()

    def __str__(self):
        return "<UNDEFINED>"

    def solveMPElement(self, mpLib_):
        self.mpElement = mpLib_.createElement(0, [self.symbolIdx])
        self.symbolIdx = None # Just stored to resolve mpElement. Do not use for something else!

    def setParentInstruction(self, parent_):
        self.parentInstr = parent_
    
    def resolve(self, dynDelayCnt_:int, instrDescription_:Dict=None): # Returns an element of the MP-Lib, i.e. tuple
        #e = self.mpElement
        #return (e[0], e[1] << dynDelayCnt_, e[2], e[3])
        
        # NOTE: Make sure that parentInstr is set before resolving
        e = self.mpElement
        fixValue = e[0]
        dynDelayMask = e[1]
        minValue = e[3]
        
        # Own instance of mask-iterator to avoid keeping an mpLib-ref here
        # TODO: Avoid this code duplication if possible
        def forAllMaskIdxs(mask_):
            while mask_:
                lsb = mask_ & -mask_
                idx = lsb.bit_length() - 1
                mask_ ^= lsb
                yield idx

        # For each dynamicDelay, check if conditional
        if instrDescription_ is not None:
            for dyn_i in forAllMaskIdxs(dynDelayMask):
                dynDelay = self.parentInstr.getDynamicDelay(dyn_i)
                if (condition := dynDelay.getCondition()) is not None:
                    if condition.check(instrDescription_):
                        f = condition.getFixValue()
                        fixValue += f
                        dynDelayMask &= ~(1 << dyn_i)
                        minValue += (f-1)
        
        if dynDelayMask == 0:
            return fixValue
        else:
            return (fixValue, dynDelayMask << dynDelayCnt_, e[2], minValue)

class Group(FrozenBase):

    def __init__(self):
        self.models = []

        super().__init__()

    def getNumModels(self):
        return len(self.models)
    
    def getAllModels(self):
        return self.models

class ResourceGroup(Group):

    def __init__(self, name_:str, id_:int):
        self.name = name_
        self.id = id_

        super().__init__()

    def createResourceModel(self, name_:str, link_:str, trVals_:List[str]):
        model = ResourceModel(name_, len(self.models), link_, trVals_)
        self.models.append(model)
        return model

class BranchGroup(Group):

    def __init__(self):
        super().__init__()

    def createBranchModel(self, name_:str, link_:str, trVals_:List[str]):
        model = BranchModel(name_, len(self.models), link_, trVals_)
        self.models.append(model)
        return model

class Model(FrozenBase):

    def __init__(self, name_:str, id_:int, link_:str, trVals_:List[str]):
        self.name = name_
        self.id = id_
        self.link = link_
        self.traceValues:List[str] = trVals_
        self.config = None

        super().__init__()

    def getAllTraceValues(self):
        return self.traceValues

    def addConfig(self, config_:Dict):
        self.config = config_

    def getAllConfigs(self):
        return list(self.config.items())
    
    def hasConfig(self):
        return self.config is not None

class ResourceModel(Model):

    def __init__(self, name_:str, id_:int, link_:str, trVals_:List[str]):
        super().__init__(name_, id_, link_, trVals_)

class BranchModel(Model):

    def __init__(self, name_:str, id_:int, link_:str, trVals_:List[str]):
        super().__init__(name_, id_, link_, trVals_)

class ResourceCombination(FrozenBase):

    def __init__(self, id_:int, resMods_:List['ResourceModel']):
        self.id = id_
        self.resourceModels = resMods_

        super().__init__()

    def getAllResourceModels(self):
        return self.resourceModels

class Combination(FrozenBase):

    def __init__(self, id_:int, brMod_:'BranchModel', resComb_:'ResourceCombination'):
        self.id = id_
        self.branchModel = brMod_
        self.resourceCombination = resComb_

    # TODO: Make sure this is no longer used!
    def getAllResourceModels(self):
        return self.resourceCombination.getAllResourceModels()
    
    def getResourceCombination(self):
        return self.resourceCombination

    def getBranchModel(self):
        return self.branchModel
    

# NOTE: This is not really part of the model. 
# Rahter, it is the token, that the mulMatrix and getMatrix functions operate on
# TODO: Convenient to define here. Move later?
class BlockMatrix(FrozenBase):

    def __init__(self, dim_:int, initVal_=None):
        self.dimension = dim_
        self.matrix = [[initVal_ for _ in range(self.dimension)] for _ in range(self.dimension)]
        self.unitColMask = 0
        self.zeroColMask = 0
        self.unitRowMask = 0
        self.zeroRowMask = 0
        self.setRowMask = 0

    def addUnitColumns(self, idxs_:List[int]):
        for idx_i in idxs_:
            self.unitColMask |= (1 << idx_i)

    def addZeroColumn(self, idx_:int):
        self.zeroColMask |= (1 << idx_)

    def addUnitRow(self, idx_):
        self.unitRowMask |= (1 << idx_)

    def addZeroRow(self, idx_):
        self.zeroRowMask |= (1 << idx_)

    def addSetRow(self, idx_):
        self.setRowMask |= (1 << idx_)

    def unit2ZeroColumn(self, idx_:int):
        idxMask = 1 << idx_
        if self.unitColMask & idxMask:
            self.unitColMask &= ~idxMask
            self.zeroColMask |= idxMask

    def removeUnitColumn(self, idx_:int):
        self.unitColMask &= ~(1 << idx_)

    def removeZeroColumn(self, idx_:int):
        self.zeroColMask &= ~(1 << idx_)

    def removeUnitRow(self, idx_:int):
        self.unitRowMask &= ~(1 << idx_)

    def removeZeroRow(self, idx_:int):
        self.zeroRowMask &= ~(1 << idx_)

    def removeSetRow(self, idx_:int):
        self.setRowMask &= ~(1 << idx_)

    def clearRow(self, idx_:int):
        clrMask = ~(1 << idx_)
        self.unitRowMask &= clrMask
        self.zeroRowMask &= clrMask
        self.setRowMask &= clrMask

    def clearColumn(self, idx_:int):
        clrMask = ~(1 << idx_)
        self.unitColMask &= clrMask
        self.zeroColMask &= clrMask

    def isUnitColumn(self, idx_:int) -> bool:
        return self.unitColMask & (1 << idx_)
    
    def isZeroColumn(self, idx_:int) -> bool:
        return self.zeroColMask & (1 << idx_)
    
    def isUnitRow(self, idx_:int) -> bool:
        return self.unitRowMask & (1 << idx_)
    
    def isZeroRow(self, idx_:int) -> bool:
        return self.zeroRowMask & (1 << idx_)
    
    def isSetRow(self, idx_:int) -> bool:
        return self.setRowMask & (1 << idx_)

    def assignMasks(self, blkMatrix_:'BlockMatrix'):
        self.unitColMask = blkMatrix_.unitColMask
        self.zeroColMask = blkMatrix_.zeroColMask
        self.unitRowMask = blkMatrix_.unitRowMask
        self.zeroRowMask = blkMatrix_.zeroRowMask
        self.setRowMask = blkMatrix_.setRowMask

    # TODO: Debug function. Delete
    def getUnitColIdxs(self, cor_=0):
        return [i-cor_ for i in range(self.unitColMask.bit_length()) if (self.unitColMask >> i) & 1]
    
    # TODO: Debug function. Delete
    def getZeroColIdxs(self, cor_=0):
        return [i-cor_ for i in range(self.zeroColMask.bit_length()) if (self.zeroColMask >> i) & 1]
    
    # TODO: Debug function. Delete
    def getUnitRowIdxs(self, cor_=0):
        return [i-cor_ for i in range(self.unitRowMask.bit_length()) if (self.unitRowMask >> i) & 1]