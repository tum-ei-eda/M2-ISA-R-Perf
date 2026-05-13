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
import copy

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

        # TODO: Add control-flow to make sure the sets are created in-order!
        #self.timingVarSetCreated = False
        #self.regSetCreated = False
        #self.branchSetCreated = False

        # Owned instances
        self.instructions:Dict[int, Instruction] = {}
        self.timingVarSet = TimingVariableSet(self)
        self.regSet = RegisterSet(self)
        self.branchSet = BranchSet(self)
        self.resourceGroups:Dict[str, ResourceGroup] = {}
        self.branchGroup = None
        self.combinations:List[Combination] = []

        # Look-up
        self.inVariables:Dict[InVariable] = {}
        self.outVariables:Dict[OutVariable] = {}

        super().__init__()

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
    
    def createCombination(self, brMod_:'BranchModel', resMods_:List['ResourceModel']) -> 'Combination':
        comb = Combination(len(self.combinations), brMod_, resMods_)
        self.combinations.append(comb)
        return comb
    
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

    def addRegisterSet(self, inVars_:List[Tuple[str,str]], outVars_:List[Tuple[str,str]], size_:int):
        self.regSet.size = size_
        for var_i, trVal_i in inVars_:
            self.regSet.createInVariable(var_i, trVal_i)
        for var_i, trVal_i in outVars_:
            self.regSet.createOutVariable(var_i, trVal_i)

    def addBranchSet(self, inVars_:List[str], outVars_:List[str]):
        for inVar_i in inVars_:
            self.branchSet.createInVariable(inVar_i)
        for outVar_i in outVars_:
            self.branchSet.createOutVariable(outVar_i)

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
    
    def getDimension(self):
        return self.timingVarSet.size + self.regSet.size + self.branchSet.getNumVariables()
    
    def getAllColumnVariablePairs(self, instrDescription_):
        colVarPairs = self.timingVarSet.getColumnVariablePairs()
        colVarPairs.extend(self.regSet.getColumnVariablePairs(instrDescription_))
        colVarPairs.extend(self.branchSet.getColumnVariablePairs())
        return colVarPairs

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
    
    def getAllCombinations(self) -> List['Combination']:
        return self.combinations
    
    def getNumInstructions(self) -> int:
        return len(self.instructions)

    def getNumResourceGroups(self) -> int:
        return len(self.resourceGroups)

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
    
#    def getNumMaxDynamicDelays(self) -> int:
#        # TODO: Currently hard-coded. Derive automatically!
#        return 50

#    # TODO: Cleaner if this would be a member-function of Instruction-class?
#    def getMatrix(self, instrDescription_:Dict, dynDelayCnt_:int=0):
#        cInstrMatrix = self.getInstruction(instrDescription_["typeId"]).getCompressedInstructionMatrix()
#
#        dim = self.getDimension()
#        matrix = [[-1 for _ in range(dim)] for _ in range(dim)]
#
#        colVarPairs = self.getAllColumnVariablePairs(instrDescription_)
#
#        # Assign rows associated with timing variables
#        for row_i, oVar_i in enumerate(self.timingVarSet.getAllOutVariables()):
#            for (col_i, iVar_i) in colVarPairs:
#                matrix[row_i][col_i] = cInstrMatrix.getResolvedElement(iVar_i, oVar_i, dynDelayCnt_)
#
#        # Assign rows associated with registers
#        regUnitRows = list(range(self.regSet.getRowOffset(), self.regSet.getRowOffset() + self.regSet.size))
#        for oVar_i in self.regSet.getAllOutVariables():
#            if(row := oVar_i.map2Row(instrDescription_)) is not None:
#                row += self.regSet.getRowOffset()
#                regUnitRows.remove(row)
#                for (col_i, iVar_i) in colVarPairs:
#                    matrix[row][col_i] = cInstrMatrix.getResolvedElement(iVar_i, oVar_i, dynDelayCnt_)
#
#        # Set remaining register out-variables to unit-row
#        for row_i in regUnitRows:
#            matrix[row_i][row_i] = 0
#        
#        # Assign rows associated with branch-variables
#        for row_i, oVar_i in enumerate(self.branchSet.getAllOutVariables()):
#            row_i += self.branchSet.getRowOffset()
#            for (col_i, iVar_i) in colVarPairs:
#                matrix[row_i][col_i] = cInstrMatrix.getResolvedElement(iVar_i, oVar_i, dynDelayCnt_)
#
#        return matrix

#    # TODO: Cleaner if this would be a member-function of Instruction-class?
#    def mulMatrix(self, matrix_, instrDescription_:Dict):
#        cInstrMatrix = self.getInstruction(instrDescription_["typeId"]).getCompressedInstructionMatrix()
#
#        dim = self.getDimension()
#        newMatrix = [[None]*dim for _ in range(dim)]
#
#        def updateVal(val_, iVar_, oVar_, j_, col_):
#            if ((a := cInstrMatrix.getElement(iVar_, oVar_)) != -1) and ((b := matrix_[j_][col_]) != -1):
#                val_ = max(val_, a + b)
#            return val_
#
#        colVarPairs = self.getAllColumnVariablePairs(instrDescription_)
#        remainingRows = list(range(dim))
#
#        # Compute rows associated with timing variables
#        for row_i, oVar_i in enumerate(self.timingVarSet.getAllOutVariables()):
#            remainingRows.remove(row_i)
#            for col_i in range(dim):
#                val = -1
#                for (j, iVar_i) in colVarPairs:
#                    val = updateVal(val, iVar_i, oVar_i, j, col_i)
#                newMatrix[row_i][col_i] = val
#
#        # Compute rows associated with register variables
#        for oVar_i in self.regSet.getAllOutVariables():
#            if(row := oVar_i.map2Row(instrDescription_)) is not None:
#                row += self.regSet.getRowOffset()
#                remainingRows.remove(row)
#                for col_i in range(dim):
#                    val = -1
#                    for (j, iVar_i) in colVarPairs:
#                        val = updateVal(val, iVar_i, oVar_i, j, col_i)
#                    newMatrix[row][col_i] = val
#
#        # Compute rows associated with branch variables
#        for row_i, oVar_i in enumerate(self.branchSet.getAllOutVariables()):
#            row_i += self.branchSet.getRowOffset()
#            remainingRows.remove(row_i)
#            for col_i in range(dim):
#                val = -1
#                for (j, iVar_i) in colVarPairs:
#                    val = updateVal(val, iVar_i, oVar_i, j, col_i)
#                newMatrix[row_i][col_i] = val
#
#        # Handle other rows (unit rows)
#        for row_i in remainingRows:
#            newMatrix[row_i] = matrix_[row_i]  
#
#        return newMatrix


#    # TODO: DELETE? DEBUG
#    def mulMatrix_full(self, matrix_, instrDescription_:Dict):
#        instrMatrix = self.getMatrix(instrDescription_)
#
#        dim = self.getDimension()
#
#        newMatrix = [[-1 for _ in range(dim)] for _ in range(dim)]
#
#        for row_i in range(dim):
#            for col_i in range(dim):
#                val = -1
#                for j in range(dim):
#                    if instrMatrix[row_i][j] != -1 and matrix_[j][col_i] != -1:
#                        val = max(val, instrMatrix[row_i][j] + matrix_[j][col_i])
#                newMatrix[row_i][col_i] = val
#
#        return newMatrix
    
#    # TODO: DELETE? DEBUG
#    def compareMatrix(self, matrixA_, matrixB_, verbose_=False) -> bool:
#        dim = self.getDimension()
#        passed = True
#        
#        for row_i in range(dim):
#            for col_i in range(dim):
#                if matrixA_[row_i][col_i] != matrixB_[row_i][col_i]:
#                    passed = False
#                    if verbose_:
#                        print(f"Mismatch [{row_i}][{col_i}]: {matrixA_[row_i][col_i]} vs. {matrixB_[row_i][col_i]}")
#        
#        return passed
    
    # TODO: Debug. Delete?
    # TODO: Cleaner if this would be a member-function of Instruction-class?
    def showMatrix(self, matrix_):

        mp = MaxPlusLib() # TODO: Where to implement this?

        names = [v.name for v in self.timingVarSet.getAllInVariables()]
        for r in range(self.regSet.size):
            names.append("R" + str(r))
        names.extend([v.name for v in self.branchSet.getAllInVariables()])
        names.extend([v.name for v in self.branchSet.getAllOutVariables()])

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
        
        #Owned instances
        self.timingVariables:Dict[str, Tuple[InVariable, OutVariable]] = {} # TODO: Dict or List?

    def createTimingVariable(self, name_:str, numElements_:int):
        if numElements_ > 1:
            raise RuntimeError(f"Trying to create a timing variable with numElements: {numElements_} (>1). I cannot handle this yet!")

        inVar = InVariable(name_, self.size)
        outVar = OutVariable(name_, self.size, defaultSetCol_=self.size)
        self.parent.addInVariable(inVar)
        self.parent.addOutVariable(outVar)

        if name_ in self.timingVariables:
            raise RuntimeError(f"Trying to create timing variable {name_}, but that name already exists")
        self.timingVariables[name_] = (inVar, outVar)
        self.size += 1
        return self.timingVariables[name_]
    
    def getAllInVariables(self) -> List['InVariable']:
        return sorted([x for (x,_) in self.timingVariables.values()], key=lambda x: x.idx)

    def getAllOutVariables(self) -> List['OutVariable']:
        return sorted([x for (_,x) in self.timingVariables.values()], key=lambda x: x.idx)
    
    def getColumnVariablePairs(self) -> List[Tuple[int,'InVariable']]:
        return list(enumerate(self.getAllInVariables()))

class RegisterSet(FrozenBase):

    def __init__(self, parent_):
        self.size = 0
        self.parent = parent_

        #Owned instances
        self.inVariables:Dict[str, InVariable] = {} # TODO: Dict or List?
        self.outVariables:Dict[str, OutVariable] = {} # TODO: Dict or List?

    def createInVariable(self, name_:str, trVal_:str):
        inVar = InVariable(name_, self.parent.getNumInVariables(), trVal_=trVal_)
        self.parent.addInVariable(inVar)
        
        if name_ in self.inVariables:
            raise RuntimeError(f"Trying to create in-variable {name_}, but that name already exists")
        self.inVariables[name_] = inVar
        return self.inVariables[name_]

    def createOutVariable(self, name_:str, trVal_:str):
        outVar = OutVariable(name_, self.parent.getNumOutVariables(), trVal_=trVal_)
        self.parent.addOutVariable(outVar)

        if name_ in self.outVariables:
            raise RuntimeError(f"Trying to create out-variable {name_}, but that name already exists")
        self.outVariables[name_] = outVar
        return self.outVariables[name_]
    
    def getAllRegisterRows(self):
        return list(range(self.getRowOffset(), self.getRowOffset() + self.size))

    def getAllInVariables(self) -> List['InVariable']:
        return self.inVariables.values()
    
    def getAllOutVariables(self) -> List['OutVariable']:
        return self.outVariables.values()

    def getColOffset(self) -> int:
        return self.parent.timingVarSet.size
    
    def getRowOffset(self) -> int:
        return self.parent.timingVarSet.size
    
    def getColumnVariablePairs(self, instrDescription_=Dict) -> List[Tuple[int,'InVariable']]:
        retList = []
        for iVar_i in self.getAllInVariables():
            if (col := iVar_i.map2Col(instrDescription_)) is not None:
                retList.append((col + self.getColOffset(), iVar_i))
        return retList

class BranchSet(FrozenBase):

    def __init__(self, parent_):
        self.parent = parent_

        #Owned instances
        self.inVariables:Dict[str, InVariable] = {} # TODO: Dict or List?
        self.outVariables:Dict[str, OutVariable] = {} # TODO: Dict or List?

        super().__init__()

    def createInVariable(self, name_:str):
        inVar = InVariable(name_, self.parent.getNumInVariables())
        self.parent.addInVariable(inVar)
        
        if name_ in self.inVariables:
            raise RuntimeError(f"Trying to create in-variable {name_}, but that name already exists")
        self.inVariables[name_] = inVar
        return self.inVariables[name_]

    def createOutVariable(self, name_:str):
        outVar = OutVariable(name_, self.parent.getNumOutVariables())
        self.parent.addOutVariable(outVar)

        if name_ in self.outVariables:
            raise RuntimeError(f"Trying to create out-variable {name_}, but that name already exists")
        self.outVariables[name_] = outVar
        return self.outVariables[name_]
    
    def getNumVariables(self) -> int:
        return len(self.inVariables) + len(self.outVariables)
    
    def getAllInVariables(self) -> List['InVariable']:
        return self.inVariables.values()

    def getAllOutVariables(self) -> List['OutVariable']:
        return self.outVariables.values()

    def getColOffset(self) -> int:
        return self.parent.timingVarSet.size + self.parent.regSet.size
    
    def getRowOffset(self) -> int:
        return self.parent.timingVarSet.size + self.parent.regSet.size + len(self.inVariables)
    
    def getColumnVariablePairs(self) -> List[Tuple[int,'InVariable']]:
        retList = list(enumerate(self.getAllInVariables()))
        colOffset = self.getColOffset()
        retList = [(c + colOffset,v) for (c,v) in retList]
        return retList

class Variable(FrozenBase):

    # "Virtual Class"

    def __init__(self, name_:str, idx_:int, trVal_="UNDEFINED"):
        self.name = name_
        self.idx = idx_
        self.traceValue = trVal_

class InVariable(Variable):

    def __init__(self, name_:str, idx_:int, trVal_:str="UNDEFINED"):

        super().__init__(name_, idx_, trVal_)

    def getGraphName(self):
        return self.name + "_i"
    
    def map2Col(self, instrDescription_:Dict) -> int:
        # TODO: Return None in case that no value is registered for this trace value (e.g.: No RS2 register)
        return instrDescription_[self.traceValue]

class OutVariable(Variable):

    def __init__(self, name_:str, idx_:int, trVal_:str="UNDEFINED", defaultSetCol_:int=-1):
        self.defaultSetCol = defaultSetCol_ 

        super().__init__(name_, idx_, trVal_)

    def getGraphName(self):
        return self.name + "_o"
    
    def map2Row(self, instrDescription_:Dict) -> int:
        # TODO: Return None in case that no value is registered for this trace value (e.g.: No RD register)
        return instrDescription_[self.traceValue]

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

    def getCompressedInstructionMatrix(self):
        return self.compInstrMatrix
    
    def createDynamicDelay(self, resGrName_:str):
        dynDelay = DynamicDelay(len(self.dynamicDelays), self.parent.getResourceGroup(resGrName_))
        self.dynamicDelays.append(dynDelay)
        return dynDelay
    
    def getNumDynDelays(self):
        return len(self.dynamicDelays)
    
    def getMatrix(self, instrDescription_:Dict, dynDelayCnt_:int=0):
        cInstrMatrix = self.getCompressedInstructionMatrix()
        variant = self.parent

        dim = variant.getDimension()
        matrix = [[-1 for _ in range(dim)] for _ in range(dim)]

        colVarPairs = variant.getAllColumnVariablePairs(instrDescription_)

        # Assign rows associated with timing variables
        for row_i, oVar_i in enumerate(variant.timingVarSet.getAllOutVariables()):
            for (col_i, iVar_i) in colVarPairs:
                matrix[row_i][col_i] = cInstrMatrix.getResolvedElement(iVar_i, oVar_i, dynDelayCnt_)

        # Assign rows associated with registers
        regUnitRows = variant.regSet.getAllRegisterRows()
        for oVar_i in variant.regSet.getAllOutVariables():
            if(row := oVar_i.map2Row(instrDescription_)) is not None:
                row += variant.regSet.getRowOffset()
                regUnitRows.remove(row)
                for (col_i, iVar_i) in colVarPairs:
                    matrix[row][col_i] = cInstrMatrix.getResolvedElement(iVar_i, oVar_i, dynDelayCnt_)

        # Set remaining register out-variables to unit-row
        for row_i in regUnitRows:
            matrix[row_i][row_i] = 0
        
        # Assign rows associated with branch-variables
        for row_i, oVar_i in enumerate(variant.branchSet.getAllOutVariables()):
            row_i += variant.branchSet.getRowOffset()
            for (col_i, iVar_i) in colVarPairs:
                matrix[row_i][col_i] = cInstrMatrix.getResolvedElement(iVar_i, oVar_i, dynDelayCnt_)

        return matrix
    
#    def mulMatrix(self, matrix_, instrDescription_:Dict, dynDelayCnt_:int):
#        variant = self.parent
#        cInstrMatrix = self.getCompressedInstructionMatrix()
#
#        dim = variant.getDimension()
#        newMatrix = [[None]*dim for _ in range(dim)]
#
#        def updateVal(val_, iVar_, oVar_, j_, col_):
#            if ((a := cInstrMatrix.getResolvedElement(iVar_, oVar_, dynDelayCnt_)) != -1) and ((b := matrix_[j_][col_]) != -1):
#                #val_ = max(val_, a+b)
#                temp = mp_mul(a, b)
#                val_ = mp_add(val_, temp)
#            return val_
#
#        colVarPairs = variant.getAllColumnVariablePairs(instrDescription_)
#        remainingRows = list(range(dim))
#
#        # Compute rows associated with timing variables
#        for row_i, oVar_i in enumerate(variant.timingVarSet.getAllOutVariables()):
#            remainingRows.remove(row_i)
#            for col_i in range(dim):
#                val = -1
#                for (j, iVar_i) in colVarPairs:
#                    val = updateVal(val, iVar_i, oVar_i, j, col_i)
#                newMatrix[row_i][col_i] = val
#
#        # Compute rows associated with register variables
#        for oVar_i in variant.regSet.getAllOutVariables():
#            if(row := oVar_i.map2Row(instrDescription_)) is not None:
#                row += variant.regSet.getRowOffset()
#                remainingRows.remove(row)
#                for col_i in range(dim):
#                    val = -1
#                    for (j, iVar_i) in colVarPairs:
#                        val = updateVal(val, iVar_i, oVar_i, j, col_i)
#                    newMatrix[row][col_i] = val
#
#        # Compute rows associated with branch variables
#        for row_i, oVar_i in enumerate(variant.branchSet.getAllOutVariables()):
#            row_i += variant.branchSet.getRowOffset()
#            remainingRows.remove(row_i)
#            for col_i in range(dim):
#                val = -1
#                for (j, iVar_i) in colVarPairs:
#                    val = updateVal(val, iVar_i, oVar_i, j, col_i)
#                newMatrix[row_i][col_i] = val
#
#        # Handle other rows (unit rows)
#        for row_i in remainingRows:
#            newMatrix[row_i] = matrix_[row_i]  
#
#        return newMatrix

    def mulMatrix(self, matrix_, instrDescription_:Dict, dynDelayCnt_:int, mpLib_:'MaxPlusLib'):
        variant = self.parent
        cInstrMatrix = self.getCompressedInstructionMatrix()

        dim = variant.getDimension()
        newMatrix = [[None]*dim for _ in range(dim)]

        def updateVal(val_, iVar_, oVar_, j_, col_):
            if ((a := cInstrMatrix.getResolvedElement(iVar_, oVar_, dynDelayCnt_)) != -1) and ((b := matrix_[j_][col_]) != -1):
                #val_ = max(val_, a+b)
                p = mpLib_.mul(a, b)
                val_ = mpLib_.add(val_, p)
            return val_

        colVarPairs = variant.getAllColumnVariablePairs(instrDescription_)
        remainingRows = list(range(dim))

        # Compute rows associated with timing variables
        for row_i, oVar_i in enumerate(variant.timingVarSet.getAllOutVariables()):
            remainingRows.remove(row_i)
            for col_i in range(dim):
                val = -1
                for (j, iVar_i) in colVarPairs:
                    val = updateVal(val, iVar_i, oVar_i, j, col_i)
                newMatrix[row_i][col_i] = val

        # Compute rows associated with register variables
        for oVar_i in variant.regSet.getAllOutVariables():
            if(row := oVar_i.map2Row(instrDescription_)) is not None:
                row += variant.regSet.getRowOffset()
                remainingRows.remove(row)
                for col_i in range(dim):
                    val = -1
                    for (j, iVar_i) in colVarPairs:
                        val = updateVal(val, iVar_i, oVar_i, j, col_i)
                    newMatrix[row][col_i] = val

        # Compute rows associated with branch variables
        for row_i, oVar_i in enumerate(variant.branchSet.getAllOutVariables()):
            row_i += variant.branchSet.getRowOffset()
            remainingRows.remove(row_i)
            for col_i in range(dim):
                val = -1
                for (j, iVar_i) in colVarPairs:
                    val = updateVal(val, iVar_i, oVar_i, j, col_i)
                newMatrix[row_i][col_i] = val

        # Handle other rows (unit rows)
        for row_i in remainingRows:
            newMatrix[row_i] = matrix_[row_i]  

        return newMatrix
    
    def getRequiredResourceGroups(self) -> List['ResourceGroup']:
        return [d.resourceGroup for d in self.dynamicDelays]

class DynamicDelay(FrozenBase):

    def __init__(self, id_:int, resGr_:'ResourceGroup'):
        self.id = id_
        self.resourceGroup = resGr_

        super().__init__()

class CompressedInstructionMatrix(FrozenBase):

    def __init__(self, parent_:'Instruction', parentVar_:'Variant'):
        self.parent = parent_
        self.parentVariant = parentVar_

        self.data = [[-1 for _ in range(self.parentVariant.getNumInVariables())] for _ in range(self.parentVariant.getNumOutVariables())]

        super().__init__()

    def addElement(self, inVar_:'InVariable', outVar_:'OutVariable', elem_:int):
        self.data[outVar_.idx][inVar_.idx] = elem_

    def addDefaultRow(self, outVar_:'OutVariable'):
        self.data[outVar_.idx] = outVar_.getDefaultRow(self.parentVariant.getNumInVariables())

    def getElement(self, inVar_:'InVariable', outVar_:'OutVariable'):
        return self.data[outVar_.idx][inVar_.idx]
    
    def getResolvedElement(self, inVar_:'InVariable', outVar_:'OutVariable', dynDelayCnt_:int):
        elem = self.data[outVar_.idx][inVar_.idx]
        if isinstance(elem, DynamicElement):
            return elem.resolve(dynDelayCnt_)
        return elem

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
        fixedAddend = 0
        symbolicAddends:List[int] = []
        if orig_ is not None:
            if isinstance(orig_, int):
                fixedAddend += orig_
            elif isinstance(orig_, DynamicDelay):
                symbolicAddends.append(orig_.id)
            else:
                raise RuntimeError("Unsupported object-type for generation of DynamicElement")
        
        self.mpLib = MaxPlusLib(allowTempCreation_=False)
        self.mpElement = self.mpLib.createElement(fixedAddend, symbolicAddends)

        super().__init__()

    def __str__(self):
        return "<UNDEFINED>"

    def add(self, elem_):
        if isinstance(elem_, int):
            self.mpElement = self.mpLib.mul(self.mpElement, elem_)
        elif isinstance(elem_, DynamicElement):
            self.mpElement = self.mpLib.mul(self.mpElement, elem_.mpElement)
        else:
            raise RuntimeError("Unsupported object-type for addition with DynamicElement")
        
    def max(self, elem_):     
        if isinstance(elem_, int):
            self.mpElement = self.mpLib.add(self.mpElement, elem_)
        elif isinstance(elem_, DynamicElement):
            self.mpElement = self.mpLib.add(self.mpElement, elem_.mpElement)
        else:
            raise RuntimeError("Unsupported object-type for max-operation with DynamicElement")
    
    def resolve(self, dynDelayCnt_:int): # Returns an element of the MP-Lib, i.e. tuple
        e = self.mpElement
        return (e[0], e[1] << dynDelayCnt_, e[2], e[3])

#class DynamicElement(FrozenBase):
#
#    def __init__(self, orig_=None):
#        fixedAddend = 0
#        dynamicAddends:List[DynamicDelay] = []
#        if orig_ is not None:
#            if isinstance(orig_, int):
#                fixedAddend += orig_
#            elif isinstance(orig_, DynamicDelay):
#                dynamicAddends.append(orig_)
#            else:
#                raise RuntimeError("Unsupported object-type for generation of DynamicElement")
#        
#        symbolMask = 0
#        for dynDelay_i in dynamicAddends:
#            symbolMask |= 1 << dynDelay_i.id
#        self.sop = mp_create_sop([[fixedAddend, symbolMask]])
#
#        super().__init__()
#
#    def __str__(self):
#        retStr = ""
#        skipOp = True
#        for prod_i in self.sop:
#            val, mask, _ = prod_i
#            if skipOp:
#                skipOp = False
#            else:
#                retStr += " + "
#            if val != 0:
#                retStr += str(val)
#            for s_i in [i for i in range(mask.bit_length()) if (mask >> i) & 1]:
#                retStr += f"d_{s_i}"
#        return retStr
#
#    def add(self, elem_):
#        if isinstance(elem_, int):
#            self.sop = mp_mul(self.sop, elem_)
#        elif isinstance(elem_, DynamicElement):
#            self.sop = mp_mul(self.sop, elem_.sop)
#        else:
#            raise RuntimeError("Unsupported object-type for addition with DynamicElement")
#        
#    def max(self, elem_):     
#        if isinstance(elem_, int):
#            self.sop = mp_add(self.sop, elem_)
#        elif isinstance(elem_, DynamicElement):
#            self.sop = mp_add(self.sop, elem_.sop)
#        else:
#            raise RuntimeError("Unsupported object-type for max-operation with DynamicElement")
#    
#    def resolve(self, dynDelayCnt_:int) -> SoP:
#        products = []
#        for prod_i in self.sop:
#            val, symMask, _ = prod_i
#            symMask = symMask << dynDelayCnt_
#            products.append([val, symMask])
#        return mp_create_sop(products)


#class DynamicElement(FrozenBase):
#
#    def __init__(self, orig_=None):
#        self.fixedAddend = 0
#        self.dynamicAddends:List[DynamicDelay] = []
#        if orig_ is not None:
#            if isinstance(orig_, int):
#                self.fixedAddend += orig_
#            elif isinstance(orig_, DynamicDelay):
#                self.dynamicAddends.append(orig_)
#            else:
#                raise RuntimeError("Unsupported object-type for generation of DynamicElement")
#
#        super().__init__()
#
#    def __str__(self):
#        retStr = ""
#        if self.fixedAddend != 0:
#            retStr += str(self.fixedAddend)
#        for d in self.dynamicAddends:
#            retStr += f"d{d.id}"
#        return retStr
#
#    def add(self, elem_):
#        if isinstance(elem_, int):
#            self.fixedAddend += elem_
#        elif isinstance(elem_, DynamicElement):
#            self.fixedAddend += elem_.fixedAddend
#            self.dynamicAddends.extend(elem_.dynamicAddends)
#        else:
#            raise RuntimeError("Unsupported object-type for addition with DynamicElement")
#        
#    def compare(self, elem_):
#        if isinstance(elem_, int):
#            if elem_ <= self.getMinValue():
#                return self
#            else:
#                raise RuntimeError("Unexpected use-case from DynamicElement.compare() [1]")
#        elif isinstance(elem_, DynamicElement):
#            if self.isIdentical(elem_):
#                return self
#            elif self.dynamicAddends == elem_.dynamicAddends:
#                if self.fixedAddend < elem_.fixedAddend:
#                    return elem_
#                else:
#                    return self
#            else:
#                print(str(self))
#                print(str(elem_))
#                raise RuntimeError("Unexpected use-case from DynamicElement.compare() [2]")
#        else:
#            print(elem_)
#            raise RuntimeError("Unsupported object-type for comparison with DynamicElement")
#
#    def isIdentical(self, dynElem_):
#        return (self.fixedAddend == dynElem_.fixedAddend) and (self.dynamicAddends == dynElem_.dynamicAddends)
#
#    def getMinValue(self):
#        return self.fixedAddend + len(self.dynamicAddends)
#    
#    def resolve(self, dynDelayCnt_:int) -> SoP:
#        # TODO: Move the creation specifics of SoP to MaxPlusLib
#        symbolMask = 0
#        for dynDelay_i in self.dynamicAddends:
#            symbolMask |= 1 << (dynDelay_i.id + dynDelayCnt_)
#        #return SoP([[self.fixedAddend, symbolMask, bin(symbolMask).count('1') + self.fixedAddend]])
#        return mp_create_sop([[self.fixedAddend, symbolMask]])
    
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

class Combination(FrozenBase):

    def __init__(self, id_:int, brMod_:'BranchModel', resMods_:List['ResourceModel']):
        self.id = id_
        self.branchModel = brMod_
        self.resourceModels = resMods_

        super().__init__()

    def getAllResourceModels(self):
        return self.resourceModels
    
    def getBranchModel(self):
        return self.branchModel