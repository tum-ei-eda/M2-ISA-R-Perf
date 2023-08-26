# 
# Copyright 2022 Chair of EDA, Technical University of Munich
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#       http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import pathlib

from mako.template import Template

from backends.metaMathModel import MetaMathModel

from .CodeBuilder import CodeBuilder as Builder

class CodeGenerator:

    def __init__(self, templateDir_, outDir_):
        self.templateDir = templateDir_
        self.outDirBase = outDir_
    
    def generateEstimator(self, mathModel_):

        for corePerfModel_i in mathModel_.getAllCorePerfModels():

            self.__printInstructionModels(corePerfModel_i)
            self.__printModel(corePerfModel_i)
            
    def __printInstructionModels(self, corePerfModel_):

        codeArrayDict = {}
        for instr_i in corePerfModel_.getInstructionDict().values():
            codeArrayDict[instr_i.name] = self.__generateInstructionModel(instr_i)

        template = Template(filename = str(self.templateDir) + "/src/instructionModels.mako")
        code = template.render(**{"corePerfModel_" : corePerfModel_, "codeArrayDict_" : codeArrayDict})

        outFile = self.outDirBase / corePerfModel_.name / "model/src" / (corePerfModel_.name + "_InstructionModels.cpp")
        with outFile.open('w') as f:
            f.write(code)

    def __printModel(self, corePerfModel_):

        template_header = Template(filename = str(self.templateDir) + "/include/model.mako")
        code_header = template_header.render(**{"corePerfModel_" : corePerfModel_, "builder_": Builder()})

        outFile_header = self.outDirBase / corePerfModel_.name / "model/include" / (corePerfModel_.name + "_PerformanceModel.h")
        with outFile_header.open('w') as f:
            f.write(code_header)
        
        template_src = Template(filename = str(self.templateDir) + "/src/model.mako")
        code_src = template_src.render(**{"corePerfModel_" : corePerfModel_})

        outFile_src = self.outDirBase / corePerfModel_.name / "model/src" / (corePerfModel_.name + "_PerformanceModel.cpp")
        with outFile_src.open('w') as f:
            f.write(code_src)
            
    def __generateInstructionModel(self, instr_):

        # Node runner function to be executed by every node of the time function. Creates C++ code for every node
        def renderNode(node_, funcDict_):

            try:
                codeArray = funcDict_["codeArray"]
            except:
                raise TypeError("Function dictionary for renderNode does not contain an item with key \"codeArray\"")
            
            templateDir = self.templateDir / "src/nodes"
            
            if node_.isAddNode():
                templateName = "addNode"
            elif node_.isInNode():
                templateName = "inNode"
            elif node_.isMaxNode():
                templateName = "maxNode"
            elif node_.isOutNode():
                templateName = "outNode"
            else:
                raise TypeError("Unexpected node type when calling node-runner function renderNode")

            template = Template(filename = str(templateDir) + "/" + templateName + ".mako")
            codeLine = template.render(**{"node_" : node_})
                
            codeArray.append(codeLine)

        # Execute renderNode function for all nodes of the instruction's time function
        codeArray = []
        instr_.getTimeFunction().forAllNodes((renderNode, {"codeArray" : codeArray}))

        return codeArray
