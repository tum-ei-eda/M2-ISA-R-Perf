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
import os
import graphviz

from mako.template import Template

from backends.metaMathModel import MetaMathModel

class MathModelPrinter:

    def __init__(self, tempDir_, outDir_):
        self.tempDirBase = tempDir_ / "mathModel"
        self.outDirBase = outDir_


    def printMathModel(self, mathModel_):

        for corePerfModel in mathModel_.getAllCorePerfModels():

            self.curTempDir = self.tempDirBase / corePerfModel.name
            self.curOutDir = self.outDirBase / corePerfModel.name
            
            print()
            print("Creating math-model graphs for " + corePerfModel.name)

            for instr in corePerfModel.getInstructionDict().values():
                self.__printTimeFunction(instr)
            
    def __printTimeFunction(self, instr_):

        # Create dotGraph for instruction
        dotGraph = self.__generateDotGraph(instr_)

        # Print dotGraph source code to temp directory
        tempPath = self.__createSubDir_temp(instr_.name)
        tempFile = tempPath / (instr_.name + ".dot")
        with tempFile.open('w') as f:
            f.write(dotGraph.source)

        # Create pdf and copy to out directory
        print("\tMaking PDF for " + instr_.name)
        os.chdir(tempPath)
        os.system("dot -Tpdf %s.dot -o %s.pdf" % (instr_.name, instr_.name))
        os.replace("%s/%s.pdf" %(str(tempPath), instr_.name), "%s/%s_graph.pdf" %(str(self.__getSubDir_out(instr_.name)), instr_.name))
        
    def __generateDotGraph(self, instr_):

        dotGraph = graphviz.Digraph(comment=instr_.name)

        # Define function that shall be executed for every node of the instruction's timeFunction
        def drawNode(node_, funcDict_):

            # Unpack function dictionary
            try:
                dot = funcDict_["dotGraph"]
            except:
                raise TypeError("Function dictionary for drawNode does not contain an item with key \"dotGraph\"")
                
            # Find text description for this node
            if node_.isAddNode():
                text = '+'
                if node_.hasModel():
                    text += node_.getModel().name
                else:
                    text += str(node_.getDelay())
            elif node_.isMaxNode():
                text = 'max'                
            elif node_.hasName():
                text = node_.name
            else:
                text = node_.getIdStr()

            # Add node to graph an draw edge to previous nodes
            dot.node(node_.getIdStr(), text)
            if node_.hasMultipleInputs():
                for prev in node_.getPrev():
                    dot.edge(prev.getIdStr(), node_.getIdStr())
            elif node_.getPrev() is not None:
                dot.edge(node_.getPrev().getIdStr(), node_.getIdStr())

        # Execute drawNode for all nodes of the instruction's timeFunction
        instr_.getTimeFunction().forAllNodes((drawNode, {"dotGraph" : dotGraph}))

        return dotGraph
        
    def __createSubDir_temp(self, name_):
        subDir = self.curTempDir / name_
        pathlib.Path(subDir).mkdir(parents=True)
        return subDir

    def __getSubDir_out(self, name_):
        return self.curOutDir / name_
    
