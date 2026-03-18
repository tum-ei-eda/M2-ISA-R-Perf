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
        self.compInstrMatrixes:Dict[int, CompressedInstructionMatrix] = {}
        self.timingVarSet = TimingVariableSet(self)
        self.regSet = RegisterSet(self)
        self.branchSet = BranchSet(self)

        # Look-up
        self.inVariables:Dict[InVariable] = {}
        self.outVariables:Dict[OutVariable] = {}

        super().__init__()

    def getParentModel(self):
        return self.parent

    def createCompInstrMatrix(self, name_:str, typeId_:int) -> 'CompressedInstructionMatrix':
        cInstrMatrix = CompressedInstructionMatrix(name_, typeId_, self)
        if typeId_ in self.compInstrMatrixes:
            raise RuntimeError(f"Cannot add compressed-instruction-matrix {name_} with type-ID {typeId_}. Type-ID is already registered.")
        self.compInstrMatrixes[typeId_] = cInstrMatrix
        return cInstrMatrix
    
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

    def getMatrix(self, instrDescription_:Dict):
        cInstrMatrix = self.compInstrMatrixes[instrDescription_["typeId"]]

        dim = self.getDimension()
        matrix = [[-1 for _ in range(dim)] for _ in range(dim)]

        colVarPairs = self.getAllColumnVariablePairs(instrDescription_)

        # Assign rows associated with timing variables
        for row_i, oVar_i in enumerate(self.timingVarSet.getAllOutVariables()):
            for (col_i, iVar_i) in colVarPairs:
                matrix[row_i][col_i] = cInstrMatrix.getElement(iVar_i, oVar_i)

        # Assign rows associated with registers
        regUnitRows = list(range(self.regSet.getRowOffset(), self.regSet.getRowOffset() + self.regSet.size))
        for oVar_i in self.regSet.getAllOutVariables():
            if(row := oVar_i.map2Row(instrDescription_)) is not None:
                row += self.regSet.getRowOffset()
                regUnitRows.remove(row)
                for (col_i, iVar_i) in colVarPairs:
                    matrix[row_i][col_i] = cInstrMatrix.getElement(iVar_i, oVar_i)

        # Set remaining register out-variables to unit-row
        for row_i in regUnitRows:
            matrix[row_i][row_i] = 0
        
        # Assign rows associated with branch-variables
        for row_i, oVar_i in enumerate(self.branchSet.getAllOutVariables()):
            row_i += self.branchSet.getRowOffset()
            for (col_i, iVar_i) in colVarPairs:
                matrix[row_i][col_i] = cInstrMatrix.getElement(iVar_i, oVar_i)

        return matrix
    
    def mulMatrix(self, matrix_, instrDescription_:Dict):
        cInstrMatrix = self.compInstrMatrixes[instrDescription_["typeId"]]

        newMatrix = copy.deepcopy(matrix_)

        def updateVal(val_, iVar_, oVar_, j_, col_):
            if ((a := cInstrMatrix.getElement(iVar_, oVar_)) != -1) and ((b := matrix_[j_][col_]) != -1):
                val_ = max(val_, a + b)
            return val_

        colVarPairs = self.getAllColumnVariablePairs(instrDescription_)

        for col_i in range(self.getDimension()):
            
            # Compute rows associated with timing variables
            for row_i, oVar_i in enumerate(self.timingVarSet.getAllOutVariables()):
                val = -1
                for (j, iVar_i) in colVarPairs:
                    val = updateVal(val, iVar_i, oVar_i, j, col_i)
                newMatrix[row_i][col_i] = val

            # Compute rows associated with register variables
            for oVar_i in self.regSet.getAllOutVariables():
                if(row := oVar_i.map2Row(instrDescription_)) is not None:
                    row += self.regSet.getRowOffset()
                    val = -1
                    for (j, iVar_i) in colVarPairs:
                        val = updateVal(val, iVar_i, oVar_i, j, col_i)
                    newMatrix[row][col_i] = val

            # Compute rows associated with branch variables
            for row_i, oVar_i in enumerate(self.branchSet.getAllOutVariables()):
                row_i += self.branchSet.getRowOffset()
                val = -1
                for (j, iVar_i) in colVarPairs:
                    val = updateVal(val, iVar_i, oVar_i, j, col_i)
                newMatrix[row_i][col_i] = val

        return newMatrix


    # TODO: DELETE? DEBUG
    def mulMatrix_full(self, matrix_, instrDescription_:Dict):
        instrMatrix = self.getMatrix(instrDescription_)

        dim = self.getDimension()

        newMatrix = [[-1 for _ in range(dim)] for _ in range(dim)]

        for row_i in range(dim):
            for col_i in range(dim):
                val = -1
                for j in range(dim):
                    if instrMatrix[row_i][j] != -1 and matrix_[j][col_i] != -1:
                        val = max(val, instrMatrix[row_i][j] + matrix_[j][col_i])
                newMatrix[row_i][col_i] = val

        return newMatrix
    
    # TODO: DELETE? DEBUG
    def compareMatrix(self, matrixA_, matrixB_, verbose_=False) -> bool:
        dim = self.getDimension()
        passed = True
        
        for row_i in range(dim):
            for col_i in range(dim):
                if matrixA_[row_i][col_i] != matrixB_[row_i][col_i]:
                    passed = False
                    if verbose_:
                        print(f"Mismatch [{row_i}][{col_i}]: {matrixA_[row_i][col_i]} vs. {matrixB_[row_i][col_i]}")
        
        return passed
    
    # TODO: Debug. Delete?
    def showMatrix(self, matrix_):

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
                colsWidths[col_i] = max(colsWidths[col_i], len(str(matrix_[row_i][col_i])))

        e = ""
        print(f"{e:{rowNameWidth}} ", end="")
        for col_i in range(dim):
            print(f"| {names[col_i]:{colsWidths[col_i]}} ", end="")
        print()
        
        for row_i in range(dim):
            print(f"{names[row_i]:{rowNameWidth}} ", end="")
            for col_i in range(dim):
                print(f"| {matrix_[row_i][col_i]:{colsWidths[col_i]}} ", end="")
            print()
        print()

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

class CompressedInstructionMatrix(FrozenBase):

    def __init__(self, name_:str, typeId_:int, parent_:'Variant'):
        self.name = name_
        self.typeId = typeId_
        self.parent = parent_

        self.data = [[-1 for _ in range(self.parent.getNumInVariables())] for _ in range(self.parent.getNumOutVariables())]

        super().__init__()

    def addElement(self, inVar_:'InVariable', outVar_:'OutVariable', elem_:int):
        self.data[outVar_.idx][inVar_.idx] = elem_

    def addDefaultRow(self, outVar_:'OutVariable'):
        self.data[outVar_.idx] = outVar_.getDefaultRow(self.parent.getNumInVariables())

    def getElement(self, inVar_:'InVariable', outVar_:'OutVariable'):
        return self.data[outVar_.idx][inVar_.idx]

    # TODO: DELETE
    def show(self):
        inVars = sorted(self.parent.inVariables.values(), key=lambda x: x.idx)
        outVars = sorted(self.parent.outVariables.values(), key=lambda x: x.idx)

        rowNameWidth = 0
        for oVar_i in outVars:
            rowNameWidth = max(rowNameWidth, len(oVar_i.name))
        rowNameWidth = int(rowNameWidth)

        colWidths = []
        for iVar_i in inVars:
            colWidths.append(len(iVar_i.name))

        e = ""
        print(f"{e:{rowNameWidth}} ", end="")
        for iVar_i in inVars:
            print(f"| {iVar_i.name} ", end="")
        print("")

        for oVar_i in outVars:
            print(f"{oVar_i.name:{rowNameWidth}} ", end="")
            for i, iVar_i in enumerate(inVars):
                print(f"| {self.data[oVar_i.idx][iVar_i.idx]:{colWidths[i]}} ", end="")
            print("")