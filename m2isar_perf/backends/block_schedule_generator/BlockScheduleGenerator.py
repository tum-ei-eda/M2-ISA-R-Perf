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

class Block:

    def __init__(self, id_:int, startPc_:int, endPc_:int, callCnt_:int):
        self.id = id_
        self.startPc = startPc_
        self.endPc = endPc_
        self.callCnt = callCnt_
        self.code = ""

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

#        isFirst = True
#        for block_i in self.blockDict["blocks"]:
#
#            block = Block(block_i['id'], block_i['startPc'], block_i['endPc'])
#
#            blockMatrix = None
#            for instr_i in block_i["instrs"]:
#                if blockMatrix is None:
#                    blockMatrix = variant_.getMatrix(instr_i)
#                else:
#                    blockMatrix = variant_.mulMatrix(blockMatrix, instr_i)
#
#            block.setCode(self.__getScheduleFunctionCode(blockMatrix))
#
#            if isFirst:
#                isFirst = False
#                print()
#                variant_.showMatrix(blockMatrix)
#                print()
#                print(self.__getScheduleFunctionCode(blockMatrix))
#                print()

    def __getBlocks(self, variant_):
        blocks = []
        for block_i in self.blockDict["blocks"]:

            block = Block(block_i['id'], block_i['startPc'], block_i['endPc'], block_i['callCnt'])

            blockMatrix = None
            for instr_i in block_i["instrs"]:
                if blockMatrix is None:
                    blockMatrix = variant_.getMatrix(instr_i)
                else:
                    blockMatrix = variant_.mulMatrix(blockMatrix, instr_i)

            block.code = self.__getScheduleFunctionCode(blockMatrix)
            blocks.append(block)

        blocks.sort(key=lambda x: x.callCnt, reverse=True)
        return blocks

    def __getScheduleFunctionCode(self, matrix_):
        code = ""

        assignRowIdxs = []
        
        for i, row_i in enumerate(matrix_):
            if self.__isUnitOrEmpty(i, row_i):
                continue

            assignRowIdxs.append(i)

            code += "\n\t" + f"int out_{i} = "

            elements = []
            for j, elem_i in enumerate(row_i):
                if elem_i != -1:
                    elements.append(f"vec_[{j}] + {elem_i}")

            if len(elements) < 1:
                raise RuntimeError("Number of elements is less than 1. This should never happen!")
            elif len(elements) == 1:
                code += elements[0] + ";"
            else:
                code += "std::max({"
                isFirst = True
                for elem_i in elements:
                    if isFirst:
                        isFirst = False
                    else:
                        code += ", "
                    code += elem_i
                code += "});"

        code += "\n"

        for idx_i in assignRowIdxs:
            code += "\n\t" + f"vec_[{idx_i}] = out_{idx_i};"

        return code

    
    def __isUnitOrEmpty(self, i_, row_):
        unitOrEmpty = True
        for j, elem_i in enumerate(row_):
            if elem_i != -1:
                if not (i_ == j and elem_i == 0):
                    unitOrEmpty = False
                    break
        return unitOrEmpty