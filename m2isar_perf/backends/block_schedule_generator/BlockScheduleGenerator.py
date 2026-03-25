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

import pathlib
import json
from mako.template import Template
import copy # TODO: Test. REMOVE!

from .CodeBuilder import CodeBuilder
from backends.common import dirUtils

class BlockScheduleGenerator:

    def __init__(self):
        self.templateDir = pathlib.Path(__file__).parents[0] / "templates"

    def execute(self, model_, blockList_, outDir_):

        blockListPath = pathlib.Path(blockList_).resolve()
        with blockListPath.open('r', encoding='utf-8') as f:
            self.blockDict = json.load(f)

        print()
        print("-- BACKEND: BLOCK_SCHEDULE_GENERATOR --")

        for variant_i in model_.getAllVariants():

            print(f" > Creating output directory for {variant_i.name}")
            outDir = dirUtils.getCodeDirPath(outDir_, variant_i, "block_sched")
            dirUtils.createOrReplaceDir(outDir / "src")
            dirUtils.createOrReplaceDir(outDir / "include")

            self.builder = CodeBuilder(variant_i)

            print(f" > Generating block-schedules for {variant_i.name}")
            self.__generateMAPExplorer(variant_i, outDir)
            self.__generateBlockScheduleFunctions(variant_i, outDir)

    def __generateMAPExplorer(self, variant_, outDir_):

        template_header = Template(filename = str(self.templateDir) + "/include/MAPExplorer.mako")
        code_header = template_header.render(**{'builder_': self.builder})
        outFile_header = outDir_ / "include" / (self.builder.getName() + "_MAPExplorer.h")
        with outFile_header.open('w') as f:
            f.write(code_header)
    
    def __generateBlockScheduleFunctions(self, variant_, outDir_):

        blocks = self.__getBlocks(variant_)

        template_header = Template(filename = str(self.templateDir) + "/include/BlockSchedulingFunctions.mako")
        code_header = template_header.render(**{'size_': len(blocks), 'builder_': self.builder})
        outFile_header = outDir_ / "include" / (self.builder.getName() + "_BlockSchedulingFunctions.h")
        with outFile_header.open('w') as f:
            f.write(code_header)

        template_src = Template(filename = str(self.templateDir) + "/src/BlockSchedulingFunctions.mako")
        code_src = template_src.render(**{'blocks_': blocks, 'builder_': self.builder})
        outFile_src = outDir_ / "src" / (self.builder.getName() + "_BlockSchedulingFunctions.cpp")
        with outFile_src.open('w') as f:
            f.write(code_src)

    def __getBlocks(self, variant_):
        blocks = []

        # TODO: Remove
        self.variant = variant_


        for block_i in self.blockDict["blocks"]:

            block = Block(block_i['id'], block_i['startPc'], block_i['endPc'], block_i['callCnt'])

            blockMatrix = None
            for instr_i in block_i["instrs"]:
                
                if blockMatrix is None:
                    blockMatrix = variant_.getMatrix(instr_i)
                else:
                    blockMatrix = variant_.mulMatrix(blockMatrix, instr_i)


            verbose = (block.id == 266)

            block.code = self.__getScheduleFunctionCode(blockMatrix, verbose)
            blocks.append(block)

        blocks.sort(key=lambda x: x.callCnt, reverse=True)
        return blocks

    def __getScheduleFunctionCode(self, matrix_, verbose_=False):
        
        code = ""
        handledRowIdxs = []

        unhandledRowExps = self.__getRowExpressions(matrix_)

        # Process rowExpressions
        while unhandledRowExps:
            
            #print_unhandledRows = [(e.idx, e.refIdx) for e in unhandledRowExps]
            #print(f"Unhandled rows: {print_unhandledRows}")
            #print(f"Handled rows: {handledRowIdxs}")
            
            for rowExp_i in unhandledRowExps:
                
                # Rows without any reference row
                if rowExp_i.isStandAloneRow():
                    code += "\n\t" + f"uint64_t out_{rowExp_i.idx} = "
                    if len(rowExp_i.dimensions) > 1:
                        code += "std::max({"
                        isFirst = True
                        for (colIdx_i, elem_i) in rowExp_i.dimensions:
                            if isFirst:
                                isFirst = False
                            else:
                                code += ", "
                            code += f"vec_[{colIdx_i}] + {elem_i}"
                        code += "});"
                    else:
                        colIdx, elem = rowExp_i.dimensions[0]
                        code += f"vec_[{colIdx}] + {elem}"
                    handledRowIdxs.append(rowExp_i.idx)

                elif rowExp_i.refIdx in handledRowIdxs:

                    # Implement dim-shift rows
                    if rowExp_i.isDimShiftRow():
                        code += "\n\t" + f"uint64_t out_{rowExp_i.idx}" + " = std::max({"
                        code += f"out_{rowExp_i.refIdx}"
                        if (offset := rowExp_i.offset) > 0:
                            code += f" + {offset}"
                        elif offset < 0:
                            code += f" - {abs(offset)}"
                        for (colIdx_i, elem_i) in rowExp_i.dimensions:
                            code += f", vec_[{colIdx_i}] + {elem_i}"
                        code += "});"
                        handledRowIdxs.append(rowExp_i.idx)

                    # Implement offset and identical rows
                    # TODO: This implies that also identical rows get a temp "out_x" assignment. Strictly not necessary
                    # NOTE: Might be necessary: vec_[5] = out_4, vec_[6] = out_5, but out_5 never defined
                    elif rowExp_i.isOffsetRow() or rowExp_i.isIdenticalRow():
                        code += "\n\t" + f"uint64_t out_{rowExp_i.idx} = out_{rowExp_i.refIdx}"
                        if (offset := rowExp_i.offset) > 0:
                            code += f" + {offset}"
                        elif offset < 0:
                            code += f" - {abs(offset)}"
                        code += ";"
                        handledRowIdxs.append(rowExp_i.idx)

            unhandledRowExps = [rowExp_i for rowExp_i in unhandledRowExps if rowExp_i.idx not in handledRowIdxs]

        code += "\n"
        
        for idx_i in handledRowIdxs:
            code += "\n\t" + f"vec_[{idx_i}] = out_{idx_i};"

        return code

#    def __getScheduleFunctionCode(self, matrix_):
#        code = ""
#
#        assignRowIdxs = []
#        
#        #rowExpressions = self.__getRowExpressions(matrix_)
#
#        for i, row_i in enumerate(matrix_):
#            if self.__isUnitOrEmpty(i, row_i):
#                continue
#
#            assignRowIdxs.append(i)
#
#            code += "\n\t" + f"int out_{i} = "
#
#            elements = []
#            for j, elem_i in enumerate(row_i):
#                if elem_i != -1:
#                    elements.append(f"vec_[{j}] + {elem_i}")
#
#            if len(elements) < 1:
#                raise RuntimeError("Number of elements is less than 1. This should never happen!")
#            elif len(elements) == 1:
#                code += elements[0] + ";"
#            else:
#                code += "std::max({"
#                isFirst = True
#                for elem_i in elements:
#                    if isFirst:
#                        isFirst = False
#                    else:
#                        code += ", "
#                    code += elem_i
#                code += "});"
#
#        code += "\n"
#
#        for idx_i in assignRowIdxs:
#            code += "\n\t" + f"vec_[{idx_i}] = out_{idx_i};"
#
#        return code

    
    def __getRowExpressions(self, matrix_):
        
        rowExpressions = []

        dim = len(matrix_)
        unhandledIdxs = list(range(dim))
        
        # Compare every row with all rows above:
        # Find:
        #   1) Unit and empty rows
        #   2) Identical rows (offset = 0)
        #   3) Rows with constant offset
        for idx_i in range(dim -1, -1, -1):
            row_i = matrix_[idx_i]
            
            if self.__isUnitOrEmpty(idx_i, row_i):
                unhandledIdxs.remove(idx_i)
                continue
            
            offset = None
            refIdx = None

            for idx_ii in range(idx_i -1, -1, -1): 
                row_ii = matrix_[idx_ii]
                if (tempOffset := self.__checkOffsetRow(row_i, row_ii)) is not None:
                    if (offset is None) or (tempOffset == 0):
                        offset = tempOffset
                        refIdx = idx_ii
                    # TODO: For dynamic delays, consider to check if addend is dynamic or fixed
                    
                    # Rows are identical (doesn't get better than this). Abort search
                    if offset == 0:
                        break
                
            if offset is not None:
                rowExp = RowExpression(idx_i)
                rowExp.setOffsetRow(refIdx, offset)
                rowExpressions.append(rowExp)
                unhandledIdxs.remove(idx_i)

        # Compare every remaining row with every remaining row
        # Find:
        #   1) Dim-Shift rows
        addedHandledRowIdxs = []
        for rowIdx_i in unhandledIdxs:
            for rowIdx_ii in unhandledIdxs:
                if rowIdx_i == rowIdx_ii:
                    continue
        
                row_i = matrix_[rowIdx_i]
                row_ii = matrix_[rowIdx_ii]
                if (res := self.__checkDimShiftRow(row_i, row_ii)) is not None:
                    offset, dims = res
                    rowExp = RowExpression(rowIdx_i)
                    rowExp.setDimShiftRow(rowIdx_ii, offset, dims)
                    rowExpressions.append(rowExp)
                    addedHandledRowIdxs.append(rowIdx_i)
                    break
        unhandledIdxs = [i for i in unhandledIdxs if not i in addedHandledRowIdxs]


        # Translate remaining rows to RowExpression
        for rowIdx_i in unhandledIdxs:
            row = matrix_[rowIdx_i]
            rowExp = RowExpression(rowIdx_i)
            for colIdx_i, elem_i in enumerate(row):
                if elem_i != -1:
                    rowExp.addDimension(colIdx_i, elem_i)
            rowExpressions.append(rowExp)

        return rowExpressions

    def __isUnitOrEmpty(self, i_, row_):
        unitOrEmpty = True
        for j, elem_i in enumerate(row_):
            if elem_i != -1:
                if not (i_ == j and elem_i == 0):
                    unitOrEmpty = False
                    break
        return unitOrEmpty
    
    def __checkOffsetRow(self, row_i_, row_ii_):
        offset = None
        for elem_i, elem_ii in zip(row_i_, row_ii_):
            if (elem_i == -1) and (elem_ii == -1):
                continue
            if (elem_i == -1) or (elem_ii == -1):
                return None

            if offset is None:
                offset = elem_i - elem_ii
            else:
                if offset != (elem_i - elem_ii):
                    return None

        if offset is None:
            raise RuntimeError(f"Cannot find valid offset for these rows\n{row_i_}\n{row_ii_}")
        return offset
    
    def __checkDimShiftRow(self, row_i_, row_ii_):
        dimensions = []
        offset = None

        for i, (elem_i, elem_ii) in enumerate(zip(row_i_, row_ii_)):
            if (elem_i == -1):
                if (elem_ii == -1):
                    continue
                else:
                    return None
            else:
                if (elem_ii == -1):
                    dimensions.append((i, elem_i))
                else:
                    if offset is None:
                        offset = elem_i - elem_ii
                    elif offset != (elem_i - elem_ii):
                        return None

        if offset is None:
            raise RuntimeError(f"Cannot find valid offset for these rows\n{row_i_}\n{row_ii_}")
        if not dimensions:
            raise RuntimeError(f"Cannot find any \"free dimensions\" for these rows\n{row_i_}\n{row_ii_}")
        
        return (offset, dimensions)

class Block:

    def __init__(self, id_:int, startPc_:int, endPc_:int, callCnt_:int):
        self.id = id_
        self.startPc = startPc_
        self.endPc = endPc_
        self.callCnt = callCnt_
        self.code = ""

class RowExpression:

    def __init__(self, idx_):
        self.idx = idx_
        self.refIdx = None
        self.offset = None
        self.dimensions = [] # (colIdx, elem)

    def isStandAloneRow(self):
        return (self.refIdx is None)

    def isIdenticalRow(self):
        return ((self.refIdx is not None) and (self.offset==0) and (not self.dimensions))
    
    def isOffsetRow(self):
        return ((self.refIdx is not None) and (self.offset!=0) and (not self.dimensions))
    
    def isDimShiftRow(self):
        return ((self.refIdx is not None) and (self.dimensions))

    def setOffsetRow(self, refIdx_, offset_):
        self.refIdx = refIdx_
        self.offset = offset_

    def setDimShiftRow(self, refIdx_, offset_, dims_):
        self.refIdx = refIdx_
        self.offset = offset_
        self.dimensions = dims_

    def addDimension(self, colIdx_, elem_):
        self.dimensions.append((colIdx_, elem_))