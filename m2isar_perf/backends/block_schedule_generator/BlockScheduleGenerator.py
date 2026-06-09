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
from collections import deque
import time # TODO: Debug

from .CodeBuilder import CodeBuilder
from backends.common import dirUtils

from meta_models.matrix_model.MaxPlusLib_NEW import MaxPlusLib, MaxPlusElement
from meta_models.matrix_model.MaxPlusLib import MaxPlusTerm

class BlockScheduleGenerator:

    def __init__(self):
        self.templateDir = pathlib.Path(__file__).parents[0] / "templates"
        # TODO: Make nodes common if instruction scheduling is further used?
        self.estimatorGenTemplateDir = pathlib.Path(__file__).parents[0].parents[0] / "estimator_generator" / "templates"

        self.maxDynDelayCnt = 0 # Max number of dynamic delays per block

        self.totalNumTemps = 0
        self.matrixGenTime = 0
        self.matrixOptTime = 0

        self.MAX_DYN_DELAYS_PER_BLOCK = 100
        self.MAX_TEMP_COUNT_PER_BLOCK = 600
        self.CODE_LINE_LIMIT = 10000

    def getInfo(self):
        print("+++++++++++++++++++++++++++++++++++++++")
        print("BLOCK_GEN:")
        #print(f"MaxDynDelayCnt: {self.maxDynDelayCnt}")
        print(f"Total number temps: {self.totalNumTemps}")
        print(f"Matrix-Gen Time: {self.matrixGenTime}s")
        print(f"Matrix-Opt Time: {self.matrixOptTime}s")
        print("+++++++++++++++++++++++++++++++++++++++")

    def execute(self, model_, schedModel_, blockList_, outDir_):

        self.executed = True

        blockListPath = pathlib.Path(blockList_).resolve()
        with blockListPath.open('r', encoding='utf-8') as f:
            self.blockDict = json.load(f)

        print()
        print("-- BACKEND: BLOCK_SCHEDULE_GENERATOR --")

        for variant_i in model_.getAllVariants():

            schedVariant = None
            for var_i in schedModel_.variants:
                if var_i.name == variant_i.name:
                    schedVariant = var_i
                    break
            if schedVariant is None:
                raise RuntimeError(f"Could not find matching variant for {variant_i.name} in scheduling model")

            print(f" > Creating output directory for {variant_i.name}")
            outDir = dirUtils.getCodeDirPath(outDir_, variant_i, "block_sched")
            dirUtils.createOrReplaceDir(outDir / "src")
            dirUtils.createOrReplaceDir(outDir / "src/block_schedules")
            dirUtils.createOrReplaceDir(outDir / "include")

            self.builder = CodeBuilder(variant_i)

            print(f" > Generating block-schedules for {variant_i.name}")
            self.__generateBlockScheduleFunctions(variant_i, outDir)
            self.__generateInstructionSchedulingFunctions(variant_i, schedVariant, outDir)
            self.__generateMAPExplorer(variant_i, outDir)

    def __generateMAPExplorer(self, variant_, outDir_):

        template_header = Template(filename = str(self.templateDir) + "/include/MAPExplorer.mako")
        code_header = template_header.render(**{'variant_': variant_, 'builder_': self.builder})
        outFile_header = outDir_ / "include" / (self.builder.getName() + "_MAPExplorer.h")
        with outFile_header.open('w') as f:
            f.write(code_header)

        template_src = Template(filename = str(self.templateDir) + "/src/MAPExplorer.mako")
        code_src = template_src.render(**{'variant_': variant_, 'builder_': self.builder})
        outFile_src = outDir_ / "src" / (self.builder.getName() + "_MAPExplorer.cpp")
        with outFile_src.open('w') as f:
            f.write(code_src)
    
    def __generateInstructionSchedulingFunctions(self, variant_, schedVariant_, outDir_):

        instructions = self.__getInsructions(variant_, schedVariant_)

        template_header = Template(filename = str(self.templateDir) + "/include/InstructionSchedulingFunctions.mako")
        code_header = template_header.render(**{'builder_': self.builder})
        outFile_header = outDir_ / "include" / (self.builder.getName() + "_InstructionSchedulingFunctions.h")
        with outFile_header.open('w') as f:
            f.write(code_header)

        template_src = Template(filename = str(self.templateDir) + "/src/InstructionSchedulingFunctions.mako")
        code_src = template_src.render(**{'instructions_': instructions, 'builder_': self.builder})
        outFile_src = outDir_ / "src" / (self.builder.getName() + "_InstructionSchedulingFunctions.cpp")
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

        codeLines = 0

        for i, block_i in enumerate(blocks):
            curBlocks.append(block_i)
            blkCnt += 1

            #codeLines += len(block_i.code.splitlines())
            codeLines += block_i.getTotalCodeLines()

            #if (blkCnt == 20) or (i == numBlocks-1):
            #if (blkCnt == 1) or (i == numBlocks-1):
            if (codeLines > self.CODE_LINE_LIMIT) or (i == numBlocks-1):
                code_src = template_src.render(**{'blocks_': curBlocks, 'builder_': self.builder})
                outFile_src = outDir_ / "src" / "block_schedules" / (self.builder.getName() + "_BlockSchedules_" + str(splitCnt) + ".cpp")
                with outFile_src.open('w') as f:
                    f.write(code_src)
                curBlocks = []
                blkCnt = 0
                codeLines = 0
                splitCnt += 1
        
        # Create CMakeLists
        template_cmake = Template(filename = str(self.templateDir) + "/src/block_schedules/CMakeLists.mako")
        code_cmake = template_cmake.render(**{'splitCnt_': splitCnt, 'builder_': self.builder})
        outFile_cmake = outDir_ / "src" / "block_schedules" / "CMakeLists.txt"
        with outFile_cmake.open('w') as f:
            f.write(code_cmake)

        # Create main source file
        template_src = Template(filename = str(self.templateDir) + "/src/block_schedules/BlockSchedulingFunctions.mako")
        code_src = template_src.render(**{'blocks_': blocks, 'builder_': self.builder, 'maxDynDelayCnt_': self.maxDynDelayCnt})
        outFile_src = outDir_ / "src" / "block_schedules" / (self.builder.getName() + "_BlockSchedulingFunctions.cpp")
        with outFile_src.open('w') as f:
            f.write(code_src)


    def __getInsructions(self, variant_, schedVariant_):
        instructions =  []

        nodeTemplateDir = self.estimatorGenTemplateDir / "src" / "nodes"

        schedFuncs = schedVariant_.getAllSchedulingFunctions()
        schedFuncs.sort(key=lambda x: x.identifier)

        matrixInstrs = variant_.getAllInstructions()
        matrixInstrs.sort(key=lambda x: x.typeId)

        for schedFunc_i, matrixInstr_i in zip(schedFuncs, matrixInstrs):
            instruction = Instruction(schedFunc_i.name, schedFunc_i.identifier, schedFunc_i.isBranch)
            
            usedInConnectors = []
            usedOutConnectors = []

            shiftedTimingVarDict = {}
            for tVar_i in schedVariant_.getAllTimingVariables():
                if tVar_i.hasMultiElements():
                    shiftedTimingVarDict[tVar_i.name] = [i+1 for i in range(tVar_i.getNumElements())] # 1-indexed.

            #Create compute-body code
            # NOTE/TODO: This functionality is copied from EstimatorGenerator. Code-sharing?
            computeCode = "\n/* Compute body */\n"
            visitedNodes = []
            nodeQueue = deque([schedFunc_i.getRootNode()])
            self.builder.resetDelayCnt()
            while nodeQueue:
                curNode = nodeQueue.popleft()
                if curNode not in visitedNodes:
                    visitedNodes.append(curNode)
                    
                    for edge_i in curNode.getAllInEdges():
                        if edge_i.isDynamic():
                            usedInConnectors.append(edge_i.name)

                    for edge_i in curNode.getAllOutEdges():
                        if edge_i.isDynamic():
                            usedOutConnectors.append(edge_i.name)
                        else:
                            if (tv := edge_i.getTimingVariable()).hasMultiElements():
                                if (d := edge_i.depth) in (l := shiftedTimingVarDict[tv.name]):
                                    l.remove(d)

                    if curNode.hasMultipleInElements():
                        if curNode.hasZeroDelay():
                            template = Template(filename = str(nodeTemplateDir) + "/ZeroDelayNode.mako")
                        else:
                            template = Template(filename = str(nodeTemplateDir) + "/FullNode.mako")
                    elif curNode.hasSingleInElement():
                        if curNode.hasZeroDelay():
                            template = Template(filename = str(nodeTemplateDir) + "/EmptyNode.mako")
                        else:
                            template = Template(filename = str(nodeTemplateDir) + "/SingleInputNode.mako")
                    else:
                        raise RuntimeError(f"Node {curNode.name} has no input element! This should never happen...")
                    computeCode += template.render(**{"node_":curNode, "builder_":self.builder})

                    for nxtNode_i in curNode.getAllOutNodes():
                        nodeQueue.append(nxtNode_i)

            # Create code to shift buffer-variables
            bufferCode = "\n/* Buffer-Shifting */\n"
            for tVarName_i in shiftedTimingVarDict.keys():
                for idx_i in shiftedTimingVarDict[tVarName_i]:
                    #computeCode += f"{self.builder.getUnrolledStr(tVarName_i, idx_i)} = {self.builder.getUnrolledStr(tVarName_i, idx_i-1)};" + "\n"
                    bufferCode += f"{self.builder.getUnrolledStr(tVarName_i, idx_i)} = "
                    varName = self.builder.getUnrolledStr(tVarName_i, idx_i-1)
                    vecCode = None
                    for i, inVar_i in enumerate(variant_.timingVarSet.inVariables):
                        if inVar_i.name == varName:
                            vecCode = f"vec_[{i}]"
                            break
                    if vecCode is None:
                        raise RuntimeError(f"Could not find vector-description for buffer variable: {varName}")
                    bufferCode += vecCode + ";\n"

            # Create input- and output-alignment code
            inputCode = "\n/* Input Alignment */\n"
            for i, inVar_i in enumerate(variant_.timingVarSet.inVariables):
                inputCode += f"uint64_t {inVar_i.name} = vec_[{i}];" + "\n"

            for statConSet_i in variant_.statConSets:
                for inVar_i in statConSet_i.inVariables:
                    if inVar_i.name in usedInConnectors:
                        inputCode += f"uint64_t {inVar_i.name} = "
                        if len((exceptions := inVar_i.exceptions)) > 0:
                            inputCode += "("
                            for i, e_i in enumerate(exceptions):
                                if i != 0:
                                    inputCode += "||"
                                inputCode += f" {inVar_i.traceValue}_ == {e_i} "
                            inputCode += ") ? 0 : "
                        inputCode += f"vec_[{statConSet_i.rowOffset} + {inVar_i.traceValue}_];" + "\n"

            brSet = variant_.branchSet
            for i, inVar_i in enumerate(brSet.inVariables):
                if inVar_i.name in usedInConnectors:
                    inputCode += f"uint64_t {inVar_i.name} = vec_[{brSet.rowOffsetIn} + {i}];" + "\n"

            inputCode += "\n"
            for dyn_i in range(matrixInstr_i.getNumDynDelays()):
                inputCode += f"uint8_t d_{dyn_i} = d_[{dyn_i}];" + "\n"
            
            # Create output-alignement code
            outputCode = "\n/* Output Alignment */\n"
            for i, outVar_i in enumerate(variant_.timingVarSet.outVariables):
                outputCode += f"vec_[{i}] = {outVar_i.name};" + "\n"

            for statConSet_i in variant_.statConSets:
                for outVar_i in statConSet_i.outVariables:
                    if outVar_i.name in usedOutConnectors:
                        outputCode += f"vec_[{statConSet_i.colOffset} + {outVar_i.traceValue}_] = {outVar_i.name};" + "\n"

            brSet = variant_.branchSet
            for i, outVar_i in enumerate(brSet.outVariables):
                if outVar_i.name in usedOutConnectors:
                    outputCode += f"vec_[{brSet.colOffsetOut} + {i}] = {outVar_i.name};" + "\n"

            code = ""
            code += inputCode
            code += computeCode
            code += bufferCode
            code += outputCode

            instruction.code = code
            instructions.append(instruction)

        return instructions

    def __getBlocks(self, variant_):
        blocks = []

        for block_i in self.blockDict["blocks"]:

            # Create a new block-container
            block = Block(len(blocks), block_i['startPc'], block_i['callCnt'])
            blockMatrix = None
            mpLib = MaxPlusLib()
            dynDelayCnt = 0


#            print("++++++++++++++++++++++++++++++++++++++++++++++")
#            print("My test")
#            d0 = (0, 1, 0, 1)
#            x1 = mpLib.add(2, d0)
#            print(f"2 + d0 = {x1}")
#            for i, temp_i in enumerate(mpLib.getTempList()):
#                print(f"> t_{i}: {temp_i.getExpression()} -> minVal: {temp_i.minVal}")
#
#            print()
#            d1 = (1, 1, 0, 2)
#            x2 = mpLib.add(x1, d1, True)
#            print()
#            print(f"2 + d0 + 1d0 = {x2}")
#            for i, temp_i in enumerate(mpLib.getTempList()):
#                print(f"> t_{i}: {temp_i.getExpression()} -> minVal: {temp_i.minVal}")
#
#            print("++++++++++++++++++++++++++++++++++++++++++++++")
#            print()
#            raise RuntimeError("COFO")


            #numInstr = len(block_i["instrs"])
            prevPc = None
            for i, instr_i in enumerate(block_i['instrs']):
                instr = variant_.getInstruction(instr_i['typeId'])

                # Check if block should be splitted
                if ((dynDelayCnt + instr.getNumDynDelays()) > self.MAX_DYN_DELAYS_PER_BLOCK) or (mpLib.getNumTemps() > self.MAX_TEMP_COUNT_PER_BLOCK):

                    # Finalize block
                    t = time.time()
                    block.code = self.__getScheduleFunctionCode(blockMatrix, mpLib)
                    #self.__createScheduleFunctionCode(block, blockMatrix, mpLib)
                    self.matrixOptTime += (time.time() - t)
                    block.setEndPc(prevPc)
                    block.splitBlock()
                    blocks.append(block)

                    # Create new block-container
                    block = Block(len(blocks), instr_i['pc'], block_i['callCnt'])
                    blockMatrix = None
                    mpLib = MaxPlusLib()
                    dynDelayCnt = 0
                
                # Update blockMatrix
                t = time.time()
                if blockMatrix is None:
                    blockMatrix = instr.getMatrix(instr_i, dynDelayCnt)
                    #print()
                    #for i, temp_i in enumerate(mpLib.forAllTemps()):
                    #    print(f"t_{i}: {temp_i.getExpression()} -> minVal: {temp_i.minVal}")
                    #print()
                    #variant_.showMatrix(blockMatrix.matrix)
                    #print()
                else:
                    blockMatrix = instr.mulMatrix(blockMatrix, instr_i, dynDelayCnt, mpLib, False)
                    #print()
                    #for i, temp_i in enumerate(mpLib.forAllTemps()):
                    #    print(f"t_{i}: {temp_i.getExpression()} -> minVal: {temp_i.minVal}")
                    #print()
                    #variant_.showMatrix(blockMatrix.matrix)
                    #print()
                self.matrixGenTime += (time.time() - t)

                #if len(mpLib.getTempList()) > 300:
                #    print(" > More than 300 temps")
                #    print(f" >> Num instr: {i}")
                #    print(f" >> Block-ID: {block_i['id']}")
                #    print()
                #    raise RuntimeError("COFO")

                # Update loop variables
                dynDelayCnt += instr.getNumDynDelays()
                prevPc = instr_i['pc']

            # Finalize (last) block
            t = time.time()
            block.code = self.__getScheduleFunctionCode(blockMatrix, mpLib)
            #self.__createScheduleFunctionCode(block, blockMatrix, mpLib)
            self.matrixOptTime += (time.time() - t)
            block.setEndPc(block_i['endPc'])
            blocks.append(block)

            #if block_i['id'] == 0:
            #    print()
            #    raise RuntimeError("TRAP")

            self.maxDynDelayCnt = max(self.maxDynDelayCnt, dynDelayCnt)

        blocks.sort(key=lambda x: x.callCnt, reverse=True)
        return blocks

#    def __getBlocks(self, variant_):
#        blocks = []
#
#        for block_i in self.blockDict["blocks"]:
#
#            verbose = False
#            #verbose = block_i['id'] == 1
#
#            block = Block(block_i['id'], block_i['startPc'], block_i['endPc'], block_i['callCnt'])
#
#            dynDelayCnt = 0
#
#            mpLib = MaxPlusLib()
#
#            startMatrixGen = time.time()
#            blockMatrix = None
#
#            #t0 = time.time()
#
#            for i, instr_i in enumerate(block_i["instrs"]):
#
#                instr = variant_.getInstruction(instr_i["typeId"])
#
#                #print(f"Handling block: {block_i['id']}/{len(self.blockDict['blocks'])} - {i}/{len(block_i['instrs'])}")
#
#                #t1 = time.time()
#                if blockMatrix is None:
#                    blockMatrix = instr.getMatrix(instr_i, dynDelayCnt)
#                    if verbose:
#                        print("getMatrix()", end="")
#                else:
#                    blockMatrix = instr.mulMatrix(blockMatrix, instr_i, dynDelayCnt, mpLib, False)
#                    if verbose:
#                        print("mulMatrix()", end="")
#                
#                if verbose:
#                    print(f" -> {float(time.time() - t1)}s")
#                    mulTime, addTime = instr.getInfo()
#                    print("\t" + f"mulTime -> {mulTime}")
#                    print("\t" + f"addTime -> {addTime}")
#
#
#
#                #if verbose:
#                #    print(instr_i)
#                #    variant_.showMatrix(blockMatrix.matrix)
#                #    print(f"new blkMatrix unit-cols: {blockMatrix.getUnitColIdxs()}")
#                #    print(f"new blkMatrix zero-cols: {blockMatrix.getZeroColIdxs()}")
#                #    print()
#
#                dynDelayCnt += instr.getNumDynDelays()
#
#            if verbose:
#                print(f"Total -> {time.time() - t0}s")
#                raise RuntimeError("COFO")
#
#
#            #print()
#            #print(f"Block-ID: {block_i['id']}")
#            #variant_.showMatrix(blockMatrix.matrix)
#            #print()
#
#            endMatrixGen = time.time()
#            self.matrixGenTime += (endMatrixGen - startMatrixGen)
#            
#            startMatrixOpt = time.time()
#            block.code = self.__getScheduleFunctionCode(blockMatrix, mpLib)
#            endMatrixOpt = time.time()
#            self.matrixOptTime += (endMatrixOpt - startMatrixOpt)
#            
#            blocks.append(block)
#
#            self.maxDynDelayCnt = max(self.maxDynDelayCnt, dynDelayCnt)
#
#        blocks.sort(key=lambda x: x.callCnt, reverse=True)
#        return blocks

    def __getScheduleFunctionCode(self, blkMatrix_, mpLib_, verbose_=False):

        self.totalNumTemps += mpLib_.getNumTemps()
        tempUsed = [False]*mpLib_.getNumTemps()

        mainCode = ""

        unhandledRowExps = self.__getRowExpressions(blkMatrix_, mpLib_, verbose_)
        
        handledIdxs = []
        while unhandledRowExps:

            for rowExp_i in unhandledRowExps:

                if rowExp_i.isStandAloneRow() or (rowExp_i.refIdx in handledIdxs):
                    mainCode += rowExp_i.getCodeLine()
                    handledIdxs.append(rowExp_i.idx)

                    # Mark all temps used in the expression as used
                    for tempMask_i in rowExp_i.forAllTempMasks():
                        for temp_i in mpLib_.forAllMaskIdxs(tempMask_i):
                            tempUsed[temp_i] = True

            unhandledRowExps = [rowExp_i for rowExp_i in unhandledRowExps if rowExp_i.idx not in handledIdxs]

        mainCode += "\n"

        for idx_i in handledIdxs:
            mainCode += "\n\t" + f"vec_[{idx_i}] = out_{idx_i};"
                
        tempCode = ""

        # Mark all temps, used by other temps, as used
        for temp_i in mpLib_.forAllTemps_reversed():
            if tempUsed[temp_i.getId()]:
                for tempMask_i in temp_i.forAllTempMasks():
                    for idx_i in mpLib_.forAllMaskIdxs(tempMask_i):
                        tempUsed[idx_i] = True

        for temp_i in mpLib_.forAllTemps():
            if tempUsed[temp_i.getId()]:
                tempCode += getMaxExpression(temp_i.getSplitExpression(), f"t_{temp_i.getId()}")

        code = ""
        code += tempCode
        code += "\n"
        code += mainCode

        if verbose_:
            print()
            print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            print()
            print(code)
            print()
            print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            print()

        return code
   

    def __createScheduleFunctionCode(self, block_, blkMatrix_, mpLib_, verbose_=False):

        #code = ""
        tempStages = []

        block_.numTemps = mpLib_.getNumTemps()

        #code += "\t" + f"uint64 t[{len(tempList)}];" + "\n" # TODO: Do we really need uint64_t? vec_ not part of this. uint32_t might be sufficient?

        tempCnt = 0
        tempStageCode = ""
        for temp_i in mpLib_.forAllTemps():
            tempStageCode += getMaxExpression(temp_i.getSplitExpression(), f"t[{temp_i.getId()}]", useTypeDef_="")
            tempCnt += 1

            if tempCnt >= 30:
                tempStages.append(tempStageCode)
                tempCnt = 0
                tempStageCode = ""

        if tempStageCode != "":
            tempStages.append(tempStageCode)
        block_.tempStages = tempStages

        #code += "\n"

        code = ""

        unhandledRowExps = self.__getRowExpressions(blkMatrix_, mpLib_, verbose_)
        
        handledIdxs = []
        while unhandledRowExps:

            for rowExp_i in unhandledRowExps:

                if rowExp_i.isStandAloneRow():
                    code += rowExp_i.getCodeLine()
                    handledIdxs.append(rowExp_i.idx)

                elif rowExp_i.refIdx in handledIdxs:
                    code += rowExp_i.getCodeLine()
                    handledIdxs.append(rowExp_i.idx)

            unhandledRowExps = [rowExp_i for rowExp_i in unhandledRowExps if rowExp_i.idx not in handledIdxs]

        code += "\n"

        for idx_i in handledIdxs:
            code += "\n\t" + f"vec_[{idx_i}] = out_{idx_i};"
                

        if verbose_:
            print()
            print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            print()
            print(code)
            print()
            print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            print()

        block_.code = code
        return

        #return code




#    def __getRowExpressions2(self, blkMatrix_, mpLib_, verbose_=False):
#        rowExpressions = []
#
#        matrix = blkMatrix_.matrix
#        dim = blkMatrix_.dimension
#        unhandledIdxs = list(range(dim))
#
#        #rowHandled = [False]*dim
#
#        # Iterate matrix from bottom to top
#        for idx_i in range(dim-1, -1, -1):
#            row_i = matrix[idx_i]
#
#            ## Discard index if empty or unit-row
#            #if blkMatrix_.isUnitRow(idx_i) or blkMatrix_.isZeroRow(idx_i):
#            #    #unhandledIdxs.remove(idx_i)
#            #    rowHandled[idx_i] = True
#            #    continue
#
#            # Discard index if empty or unit-row
#            if self.__isUnitOrEmpty(idx_i, row_i):
#                unhandledIdxs.remove(idx_i)
#                continue
#            
#            # Convert matrix content to MaxPlusElement
#            for j, e_j in enumerate(row_i):
#                if not isinstance(e_j, MaxPlusElement):
#                    row_i[j] = mpLib_.resolveElement(e_j)
#
#            # Check if simple set row (e.g. out_7 = vec_[6])
#            if (res := self.__checkSimpleSetRow(row_i)) is not None:
#                rowExp = RowExpression(idx_i).setSimpleSetRow(res)
#                rowExpressions.append(rowExp)
#                unhandledIdxs.remove(idx_i)
#                #rowHandled[idx_i] = True
#                continue
#
#            # Check if identical to any row below
#            for idx_ii in range(idx_i+1, dim):
#                if idx_ii not in unhandledIdxs:
#                    continue
#                #if rowHandled[idx_ii]:
#                #    continue
#                
#                row_ii = matrix[idx_ii]
#                if self.__checkIdenticalRow(row_i, row_ii):
#                    rowExp = RowExpression(idx_i).setIdenticalRow(idx_ii)
#                    rowExpressions.append(rowExp)
#                    unhandledIdxs.remove(idx_i)
#                    #rowHandled[idx_i] = True
#                    break
#
#
#        # Iterate remaining unhandled indexes to identify offset-rows
#        newHandledIdxs = []
#        for idx_i in unhandledIdxs:
#            #if handled_i:
#            #    continue
#            for idx_ii in unhandledIdxs:
#                #if handled_ii:
#                #    continue
#                if idx_i == idx_ii or (idx_ii in newHandledIdxs):
#                    continue
#
#                row_i = matrix[idx_i]
#                row_ii = matrix[idx_ii]
# 
#                if (offset := self.__checkOffsetRow(row_i, row_ii)) is not None:
#                    rowExp = RowExpression(idx_i).setOffsetRow(idx_ii, offset)
#                    rowExpressions.append(rowExp)
#                    newHandledIdxs.append(idx_i)
#                    break
#        unhandledIdxs = [i for i in unhandledIdxs if not i in newHandledIdxs]
#        #for idx_i in newHandledIdxs:
#        #    rowHandled[idx_i] = True
#
#        # Iterate remaining unhandled indexes to indentify dim-shift-rows
#        newHandledIdxs = []
#        for idx_i in unhandledIdxs:        
#            #if handled_i:
#            #    continue
#            
#            numDims = None
#            expressionFound = False
#            rowExp = None
#    
#            for idx_ii in unhandledIdxs:
#                #if handled_ii:
#                #    continue
#                if idx_i == idx_ii:
#                    continue
#
#                row_i = matrix[idx_i]
#                row_ii = matrix[idx_ii]
#                #print(f"Checking: {idx_i} vs. {idx_ii}")
#                if (res := self.__checkDimShiftRow(row_i, row_ii)) is not None:
#                    offset, dims = res
#                    if (numDims is None) or (len(dims) < numDims):
#                        expressionFound = True
#                        rowExp = RowExpression(idx_i).setDimShiftRow(idx_ii, offset, dims)
#
#            if expressionFound:
#                rowExpressions.append(rowExp)
#                newHandledIdxs.append(idx_i)
#        unhandledIdxs = [i for i in unhandledIdxs if not i in newHandledIdxs]
#        #for idx_i in newHandledIdxs:
#        #    rowHandled[idx_i] = True
#
#        # Translate remaining rows to RowExpression
#        for idx_i in unhandledIdxs:
#            #if handled_i:
#            #    continue
#
#            row_i = matrix[idx_i]
#            rowExp = RowExpression(idx_i)
#            for j, e_j in enumerate(row_i):
#                if not e_j.isZeroElement():
#                    rowExp.addDimension(j, e_j)
#            rowExpressions.append(rowExp)           
#
#        return rowExpressions
    

    def __getRowExpressions(self, blkMatrix_, mpLib_, verbose_=False):
        rowExpressions = []

        matrix = blkMatrix_.matrix
        dim = blkMatrix_.dimension
        #unhandledIdxs = list(range(dim))

        rowHandled = [False]*dim

        # Iterate matrix from bottom to top
        for idx_i in range(dim-1, -1, -1):
            

            # Discard index if empty or unit-row
            if blkMatrix_.isUnitRow(idx_i) or blkMatrix_.isZeroRow(idx_i):
                #unhandledIdxs.remove(idx_i)
                rowHandled[idx_i] = True
                continue

            ## Discard index if empty or unit-row
            #if self.__isUnitOrEmpty(idx_i, row_i):
            #    unhandledIdxs.remove(idx_i)
            #    continue
            
            row_i = matrix[idx_i]

            if blkMatrix_.isSetRow(idx_i):
                res = None
                for i, e_i in enumerate(row_i):
                    if e_i == 0:
                        res = (i, mpLib_.resolveElement(e_i))
                        break
                #if res is None:
                #    print(f"row_i[{idx_i}]: {row_i}")
                #    raise RuntimeError("Did not find res")
                rowExp = RowExpression(idx_i).setSimpleSetRow(res)
                rowExpressions.append(rowExp)
                rowHandled[idx_i] = True
                continue

            # Convert matrix content to MaxPlusElement
            for j, e_j in enumerate(row_i):
                row_i[j] = mpLib_.resolveElement(e_j)

            ## Check if simple set row (e.g. out_7 = vec_[6])
            #if (res := self.__checkSimpleSetRow(row_i)) is not None:
            #    rowExp = RowExpression(idx_i).setSimpleSetRow(res)
            #    rowExpressions.append(rowExp)
            #    #unhandledIdxs.remove(idx_i)
            #    rowHandled[idx_i] = True
            #    continue

            # Check if identical to any row below
            for idx_ii in range(idx_i+1, dim):
                #if idx_ii not in unhandledIdxs:
                #    continue
                if rowHandled[idx_ii]:
                    continue
                
                row_ii = matrix[idx_ii]
                if self.__checkIdenticalRow(row_i, row_ii):
                    rowExp = RowExpression(idx_i).setIdenticalRow(idx_ii)
                    rowExpressions.append(rowExp)
                    #unhandledIdxs.remove(idx_i)
                    rowHandled[idx_i] = True
                    break


        # Iterate remaining unhandled indexes to identify offset-rows
        newHandledIdxs = []
        for idx_i, handled_i in enumerate(rowHandled):
            if handled_i:
                continue
            for idx_ii, handled_ii in enumerate(rowHandled):
                if handled_ii:
                    continue
                if idx_i == idx_ii or (idx_ii in newHandledIdxs):
                    continue

                row_i = matrix[idx_i]
                row_ii = matrix[idx_ii]
 
                if (offset := self.__checkOffsetRow(row_i, row_ii)) is not None:
                    rowExp = RowExpression(idx_i).setOffsetRow(idx_ii, offset)
                    rowExpressions.append(rowExp)
                    newHandledIdxs.append(idx_i)
                    break
        #unhandledIdxs = [i for i in unhandledIdxs if not i in newHandledIdxs]
        for idx_i in newHandledIdxs:
            rowHandled[idx_i] = True

        # Iterate remaining unhandled indexes to indentify dim-shift-rows
        newHandledIdxs = []
        for idx_i, handled_i in enumerate(rowHandled):        
            if handled_i:
                continue
            
            numDims = None
            expressionFound = False
            rowExp = None
    
            for idx_ii, handled_ii in enumerate(rowHandled):
                if handled_ii:
                    continue
                if idx_i == idx_ii:
                    continue

                row_i = matrix[idx_i]
                row_ii = matrix[idx_ii]
                #print(f"Checking: {idx_i} vs. {idx_ii}")
                if (res := self.__checkDimShiftRow(row_i, row_ii)) is not None:
                    offset, dims = res
                    if (numDims is None) or (len(dims) < numDims):
                        expressionFound = True
                        rowExp = RowExpression(idx_i).setDimShiftRow(idx_ii, offset, dims)

            if expressionFound:
                rowExpressions.append(rowExp)
                newHandledIdxs.append(idx_i)
        #unhandledIdxs = [i for i in unhandledIdxs if not i in newHandledIdxs]
        for idx_i in newHandledIdxs:
            rowHandled[idx_i] = True

        # Translate remaining rows to RowExpression
        for idx_i, handled_i in enumerate(rowHandled):
            if handled_i:
                continue

            row_i = matrix[idx_i]
            rowExp = RowExpression(idx_i)
            for j, e_j in enumerate(row_i):
                if not e_j.isZeroElement():
                    rowExp.addDimension(j, e_j)
            rowExpressions.append(rowExp)           

        return rowExpressions




    # TODO: These functions are only called from one callee? Move functionality there!?

#    def __isUnitOrEmpty(self, i_, row_):
#        unitOrEmpty = True
#        for j, elem_i in enumerate(row_):
#            if elem_i != -1:
#                if not (i_ == j and elem_i == 0):
#                    unitOrEmpty = False
#                    break
#        return unitOrEmpty
#    
#    def __checkSimpleSetRow(self, row_):
#        res = None
#        for i, elem_i in enumerate(row_):
#            if not elem_i.isZeroElement():
#                if not elem_i.isUnitElement():
#                    return None
#                else:
#                    if res is None:
#                        res = (i, elem_i)
#                        continue
#                    else:
#                        return None
#
#        return res

    def __checkIdenticalRow(self, row_i_, row_ii_):
        for e_i, e_ii in zip(row_i_, row_ii_):
            if not e_i.isIdentical(e_ii):
                return False
        return True
    
    def __checkOffsetRow(self, row_i_, row_ii_):
        offset = None
        for e_i, e_ii in zip(row_i_, row_ii_):
            if e_i.isZeroElement() and e_ii.isZeroElement():
                continue
            elif e_i.isZeroElement() or e_ii.isZeroElement():
                return None
            
            if (o := e_i.getOffset(e_ii)) is None:
                return None
            else:
                if offset is None:
                    offset = o
                elif not offset.isIdentical(o):
                    return None
                
        if offset is None:
            raise RuntimeError("Failed to indentify a valid row-offset")
        return offset

    def __checkDimShiftRow(self, row_i_, row_ii_):
        dimensions = []
        offset = None

        for i, (e_i, e_ii) in enumerate(zip(row_i_, row_ii_)):
            if e_i.isZeroElement():
                if e_ii.isZeroElement():
                    continue
                else:
                    return None
            else:
                if e_ii.isZeroElement():
                    dimensions.append((i, e_i))
                else:
                    if (o := e_i.getOffset(e_ii)) is None:
                        return None
                    else:
                        if offset is None:
                            offset = o
                        elif not offset.isIdentical(o):
                            return None

        if offset is None:
            raise RuntimeError("Cannot find valid offset")
        if not dimensions:
            raise RuntimeError("Cannot find any \"free dimensions\"")
        
        return (offset, dimensions)
    
                
## HELPER FUNCTIONS ##

def getMaxExpression(operands_, resName_, useTypeDef_="uint64_t"):
    if len(operands_) < 2:
        print(f"{resName_}: {operands_}")
        raise RuntimeError("Trying to create a max-expression for less than 2 operands")

    ret = "\t" + f"{useTypeDef_} {resName_} = "
    for i, op_i in enumerate(operands_):
        
        if op_i.startswith('+'):
            op_i = op_i[1:]
        
        if i == 0:
            ret += f"MAP_Explorer::max2({op_i}, "
        elif i == 1:
            ret += f"{op_i});" + "\n"
        else:
            ret += "\t" + f"{resName_} = MAP_Explorer::max2({resName_}, {op_i});" + "\n"

    return ret

#def getMaxExpression(operands_, resName_):
#    if len(operands_) < 2:
#        raise RuntimeError(
#            "Trying to create a max-expression for less than 2 operands"
#        )
#
#    ret = []
#    temp_idx = 0
#
#    # Current reduction level
#    current = list(operands_)
#
#    while len(current) > 1:
#        next_level = []
#
#        i = 0
#        while i < len(current):
#            # Pairwise reduction
#            if i + 1 < len(current):
#
#                lhs = current[i]
#                rhs = current[i + 1]
#
#                # Final reduction writes directly into resName_
#                if len(current) == 2:
#                    tmp_name = resName_
#                else:
#                    tmp_name = f"{resName_}_m{temp_idx}"
#                    temp_idx += 1
#
#                ret.append(
#                    f"\tuint64_t {tmp_name} = "
#                    f"MAP_Explorer::max2({lhs}, {rhs});"
#                )
#
#                next_level.append(tmp_name)
#
#            else:
#                # Odd element propagates upward unchanged
#                next_level.append(current[i])
#
#            i += 2
#
#        current = next_level
#
#    return "\n".join(ret) + "\n"

## HELPER CLASSES ##

class Block:

    def __init__(self, id_:int, startPc_:int, callCnt_:int):
        self.id = id_
        self.startPc = startPc_
        self.endPc = None
        self.callCnt = callCnt_
        self.code = ""
        self.tempStages = []
        self.numTemps = 0
        self.endsOnBranch = True

    def splitBlock(self):
        self.endsOnBranch = False

    def setEndPc(self, pc_:int):
        self.endPc = pc_

    def getTotalCodeLines(self):
        codeLines = len(self.code.splitlines())
        for tStage_i in self.tempStages:
            codeLines += len(tStage_i.splitlines())
        return codeLines

class Instruction:

    def __init__(self, name_:str, typeId_:int, branch_:bool):
        self.name = name_
        self.typeId = typeId_
        self.isBranch = branch_

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

    def setSimpleSetRow(self, entry_):
        self.dimensions = [entry_]
        return self

    def setIdenticalRow(self, refIdx_):
        self.refIdx = refIdx_
        return self

    def setOffsetRow(self, refIdx_, offset_):
        self.refIdx = refIdx_
        self.offset = offset_
        return self

    def setDimShiftRow(self, refIdx_, offset_, dims_):
        self.refIdx = refIdx_
        self.offset = offset_
        self.dimensions = dims_
        return self

    def addDimension(self, colIdx_, elem_):
        self.dimensions.append((colIdx_, elem_))
        return self

    def forAllTempMasks(self):
        if (self.offset is not None) and ((t := self.offset.getTempMask()) != 0):
            yield t
        for dim_i in self.dimensions:
            if ((t := dim_i[1].getTempMask()) != 0):
                yield t

    def getCodeLine(self):
        
        resName = f"out_{self.idx}"

        if len(self.dimensions) == 0:
            if self.refIdx is None:
                raise RuntimeError("Row expression without any dimensions and refIdx")
            ret = "\t" + f"uint64_t {resName} = {self.__getRefExpression()};" + "\n"

        # simpleSetRow
        elif (len(self.dimensions) == 1) and (self.refIdx is None):
            dim = self.dimensions[0]
            ret = "\t" + f"uint64_t {resName} = vec_[{dim[0]}] " + dim[1].getExpression() + ";\n"

        else:
            maxOps = []
            if self.refIdx is not None:
                maxOps.append(self.__getRefExpression())
            for dim_i in self.dimensions:
                maxOps.append(f"vec_[{dim_i[0]}] " + dim_i[1].getExpression())
            ret = getMaxExpression(maxOps, f"out_{self.idx}")

        return ret
    
    def __getRefExpression(self):
        ret = f"out_{self.refIdx}"
        if self.offset is not None:
            ret += " " + self.offset.getExpression()
        return ret