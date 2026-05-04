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

from .CodeBuilder import CodeBuilder
from backends.common import dirUtils

from meta_models.matrix_model.MaxPlusLib_NEW import MaxPlusLib, MaxPlusElement
from meta_models.matrix_model.MaxPlusLib import MaxPlusTerm

class BlockScheduleGenerator:

    def __init__(self):
        self.templateDir = pathlib.Path(__file__).parents[0] / "templates"

        self.maxDynDelayCnt = 0 # Max number of dynamic delays per block

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
            dirUtils.createOrReplaceDir(outDir / "src/block_schedules")
            dirUtils.createOrReplaceDir(outDir / "include")

            self.builder = CodeBuilder(variant_i)

            print(f" > Generating block-schedules for {variant_i.name}")
            self.__generateBlockScheduleFunctions(variant_i, outDir)
            self.__generateMAPExplorer(variant_i, outDir)

    def __generateMAPExplorer(self, variant_, outDir_):

        template_header = Template(filename = str(self.templateDir) + "/include/MAPExplorer.mako")
        code_header = template_header.render(**{'variant_': variant_, 'builder_': self.builder, 'maxDynDelayCnt_': self.maxDynDelayCnt})
        outFile_header = outDir_ / "include" / (self.builder.getName() + "_MAPExplorer.h")
        with outFile_header.open('w') as f:
            f.write(code_header)

        template_src = Template(filename = str(self.templateDir) + "/src/MAPExplorer.mako")
        code_src = template_src.render(**{'variant_': variant_, 'builder_': self.builder})
        outFile_src = outDir_ / "src" / (self.builder.getName() + "_MAPExplorer.cpp")
        with outFile_src.open('w') as f:
            f.write(code_src)
    
    def __generateBlockScheduleFunctions(self, variant_, outDir_):

        blocks = self.__getBlocks(variant_)

        # Create Header
        template_header = Template(filename = str(self.templateDir) + "/include/BlockSchedulingFunctions.mako")
        code_header = template_header.render(**{'size_': len(blocks), 'builder_': self.builder})
        outFile_header = outDir_ / "include" / (self.builder.getName() + "_BlockSchedulingFunctions.h")
        with outFile_header.open('w') as f:
            f.write(code_header)

        # Create block schedules (splitted to keep file-size manageable)
        template_src = Template(filename = str(self.templateDir) + "/src/block_schedules/BlockSchedules_.mako")
        curBlocks = []
        splitCnt = 0
        blkCnt = 0
        numBlocks = len(blocks)
        for i, block_i in enumerate(blocks):
            curBlocks.append(block_i)
            blkCnt += 1
            if (blkCnt == 20) or (i == numBlocks-1):
                code_src = template_src.render(**{'blocks_': curBlocks, 'builder_': self.builder})
                outFile_src = outDir_ / "src" / "block_schedules" / (self.builder.getName() + "_BlockSchedules_" + str(splitCnt) + ".cpp")
                with outFile_src.open('w') as f:
                    f.write(code_src)
                curBlocks = []
                blkCnt = 0
                splitCnt += 1
        
        # Create CMakeLists
        template_cmake = Template(filename = str(self.templateDir) + "/src/block_schedules/CMakeLists.mako")
        code_cmake = template_cmake.render(**{'splitCnt_': splitCnt, 'builder_': self.builder})
        outFile_cmake = outDir_ / "src" / "block_schedules" / "CMakeLists.txt"
        with outFile_cmake.open('w') as f:
            f.write(code_cmake)

        # Create main source file
        template_src = Template(filename = str(self.templateDir) + "/src/BlockSchedulingFunctions.mako")
        code_src = template_src.render(**{'blocks_': blocks, 'builder_': self.builder})
        outFile_src = outDir_ / "src" / (self.builder.getName() + "_BlockSchedulingFunctions.cpp")
        with outFile_src.open('w') as f:
            f.write(code_src)

    def __getBlocks(self, variant_):
        blocks = []

        for block_i in self.blockDict["blocks"]:

            block = Block(block_i['id'], block_i['startPc'], block_i['endPc'], block_i['callCnt'])
            dynDelayCnt = 0

            mpLib = MaxPlusLib()

            blockMatrix = None
            for instr_i in block_i["instrs"]:
                
                #if block_i['id'] == 29:
                #    print(f">>>> Handling instr: {instr_i['typeId']}")

                instr = variant_.getInstruction(instr_i["typeId"])
                    
                if blockMatrix is None:
                    blockMatrix = instr.getMatrix(instr_i, dynDelayCnt) 
                else:
                    blockMatrix = instr.mulMatrix(blockMatrix, instr_i, dynDelayCnt, mpLib)

                #if block_i['id'] == 29:
                #    print()
                #    variant_.showMatrix(blockMatrix)
                #    print()

                dynDelayCnt += instr.getNumDynDelays()

            #if block_i['id'] == 29:
            #    print()
            #    variant_.showMatrix(blockMatrix)
            #    print()
            #    raise RuntimeError("Catch program...")

            #if block_i['id'] == 29:
            #    self.__tempCheck_HACK(mpLib.getTempList())
            #    raise RuntimeError("Catch the program...")

            #block.code = self.__getScheduleFunctionCode(blockMatrix)
            block.code = self.__getScheduleFunctionCode_HACK(blockMatrix, mpLib.getTempList())
            blocks.append(block)

            self.maxDynDelayCnt = max(self.maxDynDelayCnt, dynDelayCnt)

        blocks.sort(key=lambda x: x.callCnt, reverse=True)
        return blocks

    def __tempCheck_HACK(self, temps_):

        print("START HACK")
        print()
        print("+++ TEMPS +++")
        print()

        unrolledTemps = []

        for x, temp_i in enumerate(temps_):
            #print(f"Handling temp_{x}")

            #print(f"temp_{x}: {temp_i.getExpression()}")

            newElements = {
                0: [],
                1: []
            }      
            for i, elem_i in enumerate(temp_i.elements):
                
                if len(elem_i.temps) == 0:
                    newElements[i].append(elem_i)

                else:
                    buffer = []
                    for subTemp_i in elem_i.temps:
                        buffer = newElements[i][:]
                        newElements[i] = []
                        for e_i in unrolledTemps[subTemp_i]:

                            if len(buffer) == 0:
                                newElement = MaxPlusElement()
                                newElement.value = elem_i.value + e_i.value
                                newElement.symbols = elem_i.symbols + e_i.symbols
                                newElements[i].append(newElement)

                            else:
                                for e_ii in buffer:
                                    newElement = MaxPlusElement()
                                    newElement.value = e_ii.value + e_i.value
                                    newElement.symbols = e_ii.symbols + e_i.symbols
                                    newElements[i].append(newElement)

#                elif len(e_i.temps) == 1:
#                    unrolledSubTemp = unrolledTemps[e_i.temps[0]]
#                    for e_ii in unrolledSubTemp:
#                        if len(e_ii.temps) != 0:
#                            raise RuntimeError("Element of unrolled-sub-temp has a temp. This should never happen")
#
#                        newElement = MaxPlusElement()
#                        newElement.value = e_ii.value + e_i.value
#                        newElement.symbols = e_ii.symbols + e_i.symbols
#                        newElements[i].append(newElement)
#
#                else:
#                    raise RuntimeError("More than one temp for an elemet... Cannot handle this yet") 

            #for i in [0,1]:
            #    print(f"newElements[{i}]: ", end="")
            #    for e_i in newElements[i]:
            #        print(f"{e_i.getExpression()} , ", end="")
            #    print()

            unrolled = []
            idxs_2ndElement = list(range(len(newElements[1])))
            for i, e_i in enumerate(newElements[0]):
                add_e_i = True
                
                for ii, e_ii in enumerate(newElements[1]):

                    if ii not in idxs_2ndElement: # This element is already removed
                        continue

                    e_i_mask = e_i.getSymbolMask()
                    e_ii_mask = e_ii.getSymbolMask()

                    e_i_minVal = e_i.getMinValue()
                    e_ii_minVal = e_ii.getMinValue()

                    common_mask = e_i_mask & e_ii_mask

                    if(common_mask == e_i_mask): # e_i covered by e_ii
                        if(e_ii_minVal >= e_i_minVal):
                            #print(f"Skipping: {e_i.getExpression()}")
                            add_e_i = False
                            break # skip e_i

                    if(common_mask == e_ii_mask): # e_ii covered by e_i
                        if(e_i_minVal >= e_ii_minVal):
                            #print(f"Skipping: {e_ii.getExpression()}")
                            idxs_2ndElement.remove(ii)

                if add_e_i:
                    unrolled.append(e_i)

            for idx_i in idxs_2ndElement:
                unrolled.append(newElements[1][idx_i]) 

            unrolledTemps.append(unrolled)

            if x > 300:
                break

        print(f"Num temps: {x}")

        unrolledTuples = []
        for temp_i in unrolledTemps:
            unrolledTuples.append([e.makeTuple() for e in temp_i])


        print()
        print("+++ DUPS +++")
        print()

        seen = {}
        dupCnt = 0
        for i, temp_i in enumerate(unrolledTuples):
            #print(f"{i}: {temp_i}")
            
            key = frozenset(temp_i)
            if key in seen:
                print(f"temp_{i} is a duplicate of temp_{seen[key]}")
                dupCnt += 1
            else:
                seen[key] = i
        print(f"Num duplicates: {dupCnt}")
        

        #for i, temp_i in enumerate(unrolledTemps):
        #    show = f"temp_{i} : "
        #    for e_i in temp_i:
        #        show += e_i.getExpression()
        #        show += " , "
        #    show += "\n"
        #    print(show)


    def __getScheduleFunctionCode_HACK(self, matrix_, temps_, verbose_=False):
        mp = MaxPlusLib()
        
        code = ""
        footer = ""

        for temp_i in temps_:
            code += "\n\t" + temp_i.getExpression()

        code += "\n"

        if verbose_:
            print()
            print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            print()
            print(code)
            print()
            print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            print()

        dim = len(matrix_)
        for idx_i in range(dim):
            row = matrix_[idx_i]

            # Ignore unit and empty rows
            unitOrEmpty = True
            for j, elem_i in enumerate(row):
                if elem_i != -1:
                    if not (idx_i == j and elem_i == 0):
                        unitOrEmpty = False
                        break
            if unitOrEmpty:
                continue

            code += "\n\t" + f"uint64_t out_{idx_i} = "
            code += "std::max({"
            isFirst = True
            for j, elem_i in enumerate(row):
                if elem_i != -1:
                    if isFirst:
                        isFirst = False
                    else:
                        code += ", "
                    code += f"vec_[{j}] "
                    code += mp.resloveElement(elem_i).getExpression()

            code += "});"
            footer += "\n\t" + f"vec_[{idx_i}] = out_{idx_i};"

        return code + "\n" + footer

    def __getScheduleFunctionCode(self, matrix_):
        
        code = ""
        handledRowIdxs = []

        unhandledRowExps = self.__getRowExpressions(matrix_)

        # Process rowExpressions
        while unhandledRowExps:
            
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
                            if type(elem_i) is int:
                                code += f"vec_[{colIdx_i}] + {elem_i}"
                            else:
                                code += f"vec_[{colIdx_i}] {elem_i.getExpression()}"
                        code += "});"
                    else:
                        colIdx, elem = rowExp_i.dimensions[0]
                        if type(elem) is int:
                            code += f"vec_[{colIdx}] + {elem}"
                        else:
                            code += f"vec_[{colIdx}] {elem.getExpression()}"
                    handledRowIdxs.append(rowExp_i.idx)

                elif rowExp_i.refIdx in handledRowIdxs:

                    # Implement dim-shift rows
                    if rowExp_i.isDimShiftRow():
                        code += "\n\t" + f"uint64_t out_{rowExp_i.idx}" + " = std::max({"
                        code += f"out_{rowExp_i.refIdx}"
                        if type((offset := rowExp_i.offset)) is int:
                            if offset > 0:
                                code += f" + {offset}"
                            elif offset < 0:
                                code += f" - {abs(offset)}"
                        else:
                            code += offset.getExpression()
                        for (colIdx_i, elem_i) in rowExp_i.dimensions:
                            if type(elem_i) is int:
                                code += f", vec_[{colIdx_i}] + {elem_i}"
                            else:
                                code += f", vec_[{colIdx_i}] {elem_i.getExpression()}"
                        code += "});"
                        handledRowIdxs.append(rowExp_i.idx)

                    # Implement offset and identical rows
                    # TODO: This implies that also identical rows get a temp "out_x" assignment. Strictly not necessary
                    # NOTE: Might be necessary: vec_[5] = out_4, vec_[6] = out_5, but out_5 never defined
                    elif rowExp_i.isOffsetRow() or rowExp_i.isIdenticalRow():
                        code += "\n\t" + f"uint64_t out_{rowExp_i.idx} = out_{rowExp_i.refIdx}"
                        if type((offset := rowExp_i.offset)) is int:
                            if offset > 0:
                                code += f" + {offset}"
                            elif offset < 0:
                                code += f" - {abs(offset)}"
                        else:
                            code += offset.getExpression()
                        code += ";"
                        handledRowIdxs.append(rowExp_i.idx)

            unhandledRowExps = [rowExp_i for rowExp_i in unhandledRowExps if rowExp_i.idx not in handledRowIdxs]

        code += "\n"
        
        for idx_i in handledRowIdxs:
            code += "\n\t" + f"vec_[{idx_i}] = out_{idx_i};"

        return code

    
    def __getRowExpressions(self, matrix_):
        
        rowExpressions = []

        dim = len(matrix_)
        unhandledIdxs = list(range(dim))
        
        # Compare every row with all rows above:
        # Find:
        #   1) Unit and empty rows
        #   2) Identical rows (offset = 0)
        for idx_i in range(dim -1, -1, -1):
            row_i = matrix_[idx_i]
            
            # Identify unit and empty rows
            if self.__isUnitOrEmpty(idx_i, row_i):
                unhandledIdxs.remove(idx_i)
                continue

            # Convert SoPs to MaxPlusTerm
            # TODO: Evaluate how costly that is? Alternatively do it on a need-to-do basis in the following analysis?
            for i in range(len(row_i)):
                if type((e := row_i[i])) is not int:
                    row_i[i] = MaxPlusTerm(e)

            # Identify indentical rows
            for idx_ii in range(idx_i-1, -1, -1):
                row_ii = matrix_[idx_ii]
                if self.__checkIdenticalRow(row_i, row_ii):
                    rowExp = RowExpression(idx_i)
                    rowExp.setOffsetRow(idx_ii, 0)
                    rowExpressions.append(rowExp)
                    unhandledIdxs.remove(idx_i)
                    break

        # Find offset-rows
        addedHandledIdxs = []
        for idx_i in unhandledIdxs:
            for idx_ii in unhandledIdxs:
                if idx_i == idx_ii or (idx_ii in addedHandledIdxs):
                    continue

                row_i = matrix_[idx_i]
                row_ii = matrix_[idx_ii]
 
                if (offset := self.__checkOffsetRow(row_i, row_ii)) is not None:
                    rowExp = RowExpression(idx_i)
                    rowExp.setOffsetRow(idx_ii, offset)
                    rowExpressions.append(rowExp)
                    addedHandledIdxs.append(idx_i)
                    break
        unhandledIdxs = [i for i in unhandledIdxs if not i in addedHandledIdxs]

        # Compare every remaining row with every remaining row
        # Find:
        #   1) Dim-Shift rows
        addedHandledRowIdxs = []
        for rowIdx_i in unhandledIdxs:        
            numDims = None
            expressionFound = False
            rowExp = None
    
            for rowIdx_ii in unhandledIdxs:
                if rowIdx_i == rowIdx_ii:
                    continue

                row_i = matrix_[rowIdx_i]
                row_ii = matrix_[rowIdx_ii]
                if (res := self.__checkDimShiftRow(row_i, row_ii)) is not None:
                    offset, dims = res
                    if (numDims is None) or (len(dims) < numDims):
                        expressionFound = True
                        rowExp = RowExpression(rowIdx_i)
                        rowExp.setDimShiftRow(rowIdx_ii, offset, dims)

            if expressionFound:
                rowExpressions.append(rowExp)
                addedHandledRowIdxs.append(rowIdx_i)


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

    # TODO: These functions are only called from one callee? Move functionality there!?

    def __isUnitOrEmpty(self, i_, row_):
        unitOrEmpty = True
        for j, elem_i in enumerate(row_):
            if elem_i != -1:
                if not (i_ == j and elem_i == 0):
                    unitOrEmpty = False
                    break
        return unitOrEmpty
    
    def __checkIdenticalRow(self, row_i_, row_ii_):
        for elem_i, elem_ii in zip(row_i_, row_ii_):
            if not self.__identicalElement(elem_i, elem_ii):
                return False
        return True
    
    def __checkOffsetRow(self, row_i_, row_ii_):
        offset = None
        for elem_i, elem_ii in zip(row_i_, row_ii_):
            if (elem_i == -1) and (elem_ii == -1):
                continue
            if (elem_i == -1) or (elem_ii == -1):
                return None

            if (o := self.__getOffset(elem_i, elem_ii)) is None:
                return None
            else:
                if offset is None:
                    offset = o
                elif not self.__identicalElement(o, offset):
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
                    if (o := self.__getOffset(elem_i, elem_ii)) is None:
                        return None
                    else:
                        if offset is None:
                            offset = o
                        elif not self.__identicalElement(o, offset):
                            return None

        if offset is None:
            raise RuntimeError(f"Cannot find valid offset for these rows\n{row_i_}\n{row_ii_}")
        if not dimensions:
            raise RuntimeError(f"Cannot find any \"free dimensions\" for these rows\n{row_i_}\n{row_ii_}")
        
        return (offset, dimensions)
    
    def __getOffset(self, elem_a_, elem_b_):
        
        if type(elem_a_) is int:
            if type(elem_b_) is int:
                return elem_a_ - elem_b_
            return None 
            
        elif type(elem_a_) is MaxPlusTerm:
            return elem_a_.getOffset(elem_b_)

        else:
            raise RuntimeError(f"Unexpected type for element elem_a_ ({elem_a_})")
        
    def __identicalElement(self, elem_a_, elem_b_):
        if (type(elem_a_) is int) and (type(elem_b_) is int):
            return (elem_a_ == elem_b_)
        elif type(elem_a_) is MaxPlusTerm:
            return elem_a_.isIdentical(elem_b_)
        elif type(elem_b_) is MaxPlusTerm:
            return elem_b_.isIdentical(elem_a_)

        return False
                

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