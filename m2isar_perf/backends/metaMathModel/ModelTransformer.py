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

#!/usr/bin/env python3

import copy

from . import MetaMathModel

class ModelTransformer:

    def __init__(self):
        pass

    def transform(self, model_front):

        model_math = MetaMathModel.MathModel()
    
        for corePerfModel_front in model_front.corePerfModels:

            corePerfModel_math = MetaMathModel.CorePerfModel(corePerfModel_front.name)
            model_math.addCorePerfModel(corePerfModel_math)
            
            # For every connectorModel in frontend model, create equivalent in mathModel
            for conMod_front in corePerfModel_front.getAllConnectorModels():
                conMod_math = MetaMathModel.ConnectorModel(conMod_front.name, conMod_front.link)
                corePerfModel_math.addConnectorModel(conMod_math)
                
            # For every resourceModel in frontend model, create equivalent in mathModel
            for resMod_front in corePerfModel_front.getAllResourceModels():
                resMod_math = MetaMathModel.ResourceModel(resMod_front.name, resMod_front.link)
                corePerfModel_math.addResourceModel(resMod_math)

            # Create a pipelineModel equivalent for mathModel
            pipeline_front = corePerfModel_front.pipeline
            pipeline_math = MetaMathModel.Pipeline(pipeline_front.name)
            corePerfModel_math.pipeline = pipeline_math
            for st_front in corePerfModel_front.getAllStages():
                st_math = MetaMathModel.Stage(st_front.name)
                pipeline_math.addStage(st_math)
                
            # For every microaction in frontend model, make a MicroactionMathModel (intermediate model for transformation, not part of MetaMathModel)
            microactionMathModelDict = {}
            inConMathNodeDict = {}
            for uA_front in corePerfModel_front.getAllMicroactions():
                uA_math = MicroactionMathModel(uA_front.name)

                inCon_front = uA_front.inConnector
                if inCon_front is not None:
                    if inCon_front.name in inConMathNodeDict:
                        uA_math.setInConnector(inConMathNodeDict[inCon_front.name])
                    else:
                        inConMathNodeDict[inCon_front.name] = uA_math.addInConnector(inCon_front.name, corePerfModel_math.getConnectorModel(inCon_front.connectorModel.name))
                        
                res_front = uA_front.resource
                if res_front is not None:
                    resModel_front = res_front.resourceModel
                    if resModel_front is not None:
                        uA_math.addResource(model_=corePerfModel_math.getResourceModel(resModel_front.name))
                    else:
                        uA_math.addResource(delay_=res_front.delay)

                outCon_front = uA_front.outConnector
                if outCon_front is not None:
                    uA_math.addOutConnector(outCon_front.name, corePerfModel_math.getConnectorModel(outCon_front.connectorModel.name))

                microactionMathModelDict[uA_math.name] = uA_math

            # Create MathModel for each instruction and generate the time-function for the instruction
            pipelineUsageDict = corePerfModel_front.getPipelineUsageDict()
            for instr_front in corePerfModel_front.getAllInstructions():
                instr_math = MetaMathModel.Instruction(instr_front.name)

                # Deepcopy the microaction dictionary. Otherwise linking of nodes for this instruction will affect other instructions
                microactionMathModelDict_cpy = copy.deepcopy(microactionMathModelDict)
                
                try:
                    pipelineUsage = pipelineUsageDict[instr_front.name]
                except KeyError:
                    raise TypeError("Cannot look up pipeline-usage for instruction %s" %instr_front.name)

                allStages_math = corePerfModel_math.getAllStages()
                numStages = len(allStages_math)

                firstStage_math = allStages_math[0]
                currentNode = MetaMathModel.InNode(firstStage_math.name, firstStage_math)
                
                for i, st_math in enumerate(allStages_math):

                    # TODO/NOTE: This method makes certain assumptions, which might need to be re-evluated for more complex cores:
                    # - Assumes that stages are executed in order of the stages-list in the pipeline models
                    # - Assumes that every instruction stays at least 1 clock cycle in each stage. I.e. if no microaction is defined for a stage a "bypass delay" of 1 is implemented
                    
                    # For each used microaction, connect currentNode (i.e. start point of current stage) to inNode, and store outNode
                    microactionOutNodes = []
                    for uA_front in pipelineUsage[st_math.name]:
                        uA_math = microactionMathModelDict_cpy[uA_front.name]
                        uA_math.inNode.replace(currentNode)
                        microactionOutNodes.append(uA_math.outNode)

                    # If no microaction is defined for the stage, add a "bypass delay"
                    if(len(microactionOutNodes) < 1):
                        bypassDelayNode = MetaMathModel.AddNode(delay_=1)
                        bypassDelayNode.connect(currentNode)
                        microactionOutNodes.append(bypassDelayNode)
                        print("INFO: For instruction %s: No microaction is used in stage %s. Current handling: Adding a single \"bypass resource\" with delay 1 into the stage." % (instr_front.name, st_math.name))
                        
                    # If there is a next stage, create an inNode representing that stage ("backwards preasure" of next stage)
                    if (i < numStages - 1):
                        nxSt_math = allStages_math[i+1]
                        nxStInNode = MetaMathModel.InNode(nxSt_math.name, nxSt_math)
                    else:
                        nxStInNode = None

                    # Combine outNodes from microactions and nextStageInNode. Result is outNode for this stage (curStOutNode)
                    curStOutNode = MetaMathModel.OutNode(st_math.name, st_math)
                    if (nxStInNode is not None) or (len(microactionOutNodes) > 1):
                        maxOp = MetaMathModel.MaxNode()
                        if(nxStInNode is not None):
                            maxOp.connect(nxStInNode)
                        for n in microactionOutNodes:
                            maxOp.connect(n)
                        curStOutNode.connect(maxOp)
                    else:
                        curStOutNode.connect(microactionOutNodes[0])

                    # Set currentNode for next stage
                    currentNode = curStOutNode

                # Assign unique ID to all nodes
                self.__assignNodeId_recursive(currentNode, 0)
                
                # Create time function and add instruction to corePerfModel
                instr_math.timeFunction = MetaMathModel.TimeFunction(currentNode)
                corePerfModel_math.addInstruction(instr_math)

        return model_math 


    def __assignNodeId_recursive(self, node_, id_):

        if node_.hasMultipleInputs():
            id = id_
            for prev in node_.getPrev():
                id = self.__assignNodeId_recursive(prev, id)
                
        else:
            prev = node_.getPrev()
            if prev is not None:
                id = self.__assignNodeId_recursive(prev, id_)
            else:
                id = id_

        node_.setId(id)
        return (id + 1)
                
class MicroactionMathModel:

    def __init__(self, name_):
        self.name = name_
        self.inNode = MetaMathModel.SimpleNode()
        self.outNode = self.inNode
        
        self.__addOpSet = False
                
    def addInConnector(self, name_, model_):
        if self.__addOpSet:
            raise TypeError("ModelTransformer.MicroactionMathModel.addInConnector: Cannot call this function after an AddOperator has been added to the same object!")

        inCon = MetaMathModel.InNode(name_, model_)
                
        maxOp = MetaMathModel.MaxNode()
        maxOp.connect(self.inNode)
        maxOp.connect(inCon)
        self.outNode = maxOp

        return inCon

    # Same as addInConnector but uses an existing InNode instead of creating one
    def setInConnector(self, inCon_):

        maxOp = MetaMathModel.MaxNode()
        maxOp.connect(self.inNode)
        maxOp.connect(inCon_)
        self.outNode = maxOp
        
    def addResource(self, delay_=0, model_=None):

        addOp = MetaMathModel.AddNode(delay_, model_)
        
        addOp.connect(self.outNode)
        self.outNode = addOp
        self.__addOpSet = True
        
    def addOutConnector(self, name_, model_):
        if not self.__addOpSet:
            raise TypeError("ModelTransformer.MicroactionMathModel.addOutConnector: Cannot add an OutConnector for this object. The object has no AddOperator assigned to it!")

        outCon = MetaMathModel.OutNode(name_, model_)
                
        outCon.connect(self.outNode)
        self.outNode = outCon

        
