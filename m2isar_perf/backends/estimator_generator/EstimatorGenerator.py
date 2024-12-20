# 
# Copyright 2024 Chair of EDA, Technical University of Munich
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
from collections import deque

from .CodeBuilder import CodeBuilder as Builder
from backends.common import dirUtils

class EstimatorGenerator:

    def __init__(self):
        self.templateDir = pathlib.Path(__file__).parents[0] / "templates"

    def execute(self, model_, outDir_):

        self.outDir = outDir_
        
        print()
        print("-- BACKEND: ESTIMATOR_GENERATOR --")

        for variant_i in model_.getAllVariants():

            print(f" > Creating output directory for {variant_i.name}")
            outDir = dirUtils.getCodeDirPath(outDir_, variant_i.name) / "perf_model"
            dirUtils.createOrReplaceDir(outDir / "src")
            dirUtils.createOrReplaceDir(outDir / "include")
            
            print(f" > Generating estimator for {variant_i.name}")
            self.builder = Builder(variant_i)
            self.__generatePerformanceModel(variant_i, outDir)
            self.__generateSchedulingFunctions(variant_i, outDir)
            

    def __generatePerformanceModel(self, variant_, outDir_):

        template_header = Template(filename = str(self.templateDir) + "/include/PerformanceModel.mako")
        code_header = template_header.render(**{"variant_": variant_, "builder_": self.builder})
        outFile_header = outDir_ / "include" / (variant_.name + "_PerformanceModel.h")
        with outFile_header.open('w') as f:
            f.write(code_header)

        template_src = Template(filename = str(self.templateDir) + "/src/PerformanceModel.mako")
        code_src = template_src.render(**{"variant_": variant_})
        outFile_src = outDir_ / "src" / (variant_.name + "_PerformanceModel.cpp")
        with outFile_src.open('w') as f:
            f.write(code_src)
            
    def __generateSchedulingFunctions(self, variant_, outDir_):

        # For each scheduling function, create code body
        codeBodyDict = {}
        for schedFunc_i in variant_.getAllSchedulingFunctions():
            inputDict = {"code": ""}
            self.__visitNodes(schedFunc_i.getRootNode(), self.__generateNodeCode, inputDict)
            codeBodyDict[schedFunc_i.name] = inputDict["code"]

        # Generate SchedulingFunction file
        template = Template(filename = str(self.templateDir) + "/src/SchedulingFunction.mako")
        code = template.render(**{"variant_": variant_, "codeBodyDict_": codeBodyDict})
        outFile = outDir_ / "src" / (variant_.name + "_SchedulingFunction.cpp")
        with outFile.open('w') as f:
            f.write(code)
        
    def __visitNodes(self, root_, func_, inputDict_):
        """
        Iterate through scheduling function nodes breadth-first.

        Every node is only visited once.
        Function func_ is executed for each node (input arguments: node_ (type Node) and inputDict_ (Dictionary containing inputs expected by function))
        """

        visitedNodes = []
        nodeQueue = deque([root_])

        while nodeQueue:
            curNode = nodeQueue.popleft()
            if curNode not in visitedNodes:
                visitedNodes.append(curNode)
                func_(curNode, inputDict_)

                for nxtNode_i in curNode.getAllOutNodes():
                    nodeQueue.append(nxtNode_i)
                
    def __generateNodeCode(self, node_, inputDict_):
        """
        Function to generade C++ code for every node

        Use with __visitNodes walker-function.
        """

        nodeTemplateDir = self.templateDir / "src" / "nodes"
        
        if node_.hasMultipleInElements():
            if node_.hasZeroDelay():
                template = Template(filename = str(nodeTemplateDir) + "/ZeroDelayNode.mako")
            else:
                template = Template(filename = str(nodeTemplateDir) + "/FullNode.mako")
        elif node_.hasSingleInElement():
            if node_.hasZeroDelay():
                template = Template(filename = str(nodeTemplateDir) + "/EmptyNode.mako")
            else:
                template = Template(filename = str(nodeTemplateDir) + "/SingleInputNode.mako")
        else:
            raise RuntimeError(f"Node {node_.name} has no input element! This should never happen...")

        inputDict_["code"] = inputDict_["code"] + template.render(**{"node_":node_, "builder_":self.builder})
        
        
