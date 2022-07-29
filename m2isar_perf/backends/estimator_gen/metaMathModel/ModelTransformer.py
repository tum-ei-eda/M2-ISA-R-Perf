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
            for uA_front in corePerfModel_front.getAllMicroactions():
                uA_math = MicroactionMathModel(uA_front.name)

                inCon_front = uA_front.inConnector
                if inCon_front is not None:
                    uA_math.addInConnector(inCon_front.name, corePerfModel_math.getConnectorModel(inCon_front.connectorModel.name))

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

                try:
                    pipelineUsage = pipelineUsageDict[instr_front.name]
                except KeyError:
                    raise TypeError("Cannot look up pipeline-usage for instruction %s" %instr_front.name)

                allStages_math = corePerfModel_math.getAllStages()
                numStages = len(allStages_math)

                firstStage_math = allStages_math[0]
                currentNode = MetaMathModel.InNode(firstStage_math.name, firstStage_math, firstStage_math.name + "_prev")
                
                for i, st_math in enumerate(allStages_math):

                    # TODO/NOTE: This method makes certain assumptions, which might need to be re-evluated for more complex cores:
                    # - Assumes that stages are executed in order of the stages-list in the pipeline models
                    # - Assumes that every stage has at least one used microaction
                    
                    # For each used microaction, connect currentNode (i.e. start point of current stage) to inNode, and store outNode
                    microactionOutNodes = []
                    for uA_front in pipelineUsage[st_math.name]:
                        uA_math = copy.deepcopy(microactionMathModelDict[uA_front.name])
                        uA_math.inNode.replace(currentNode)
                        microactionOutNodes.append(uA_math.outNode)

                    if(len(microactionOutNodes) < 1):
                        raise TypeError("For instruction %s: No microaction is used in stage %s. Currently not supported!" % (instr_front.name, st_math.name))
                        
                    # If there is a next stage, create an inNode
                    if (i < numStages - 1):
                        nxSt_math = allStages_math[i+1]
                        nxStInNode = MetaMathModel.InNode(nxSt_math.name, nxSt_math, nxSt_math.name + "_prev")
                    else:
                        nxStInNode = None

                    # Combine outNodes from microactions and nextStageInNode. Result is outNode for this stage
                    curStOutNode = MetaMathModel.OutNode(st_math.name, st_math, st_math.name + "_next")
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

                timeFunc_math = MetaMathModel.TimeFunction(currentNode)
                instr_math.timeFunction = timeFunc_math

        return model_math 
    
# FOR DEGUG -> DELETE
#    def __recSearch(self, node_, prefix_=""):
#
#        if type(node_) is MetaMathModel.MaxNode:
#            for n in node_.getPrev():
#                self.__recSearch(n, prefix_="  ")
#            print(prefix_ + "max")
#        elif node_.getPrev() is None:
#            print(prefix_ + node_.id)
#            return
#        else:
#            self.__recSearch(node_.getPrev())
#            if type(node_) is MetaMathModel.AddNode:
#                print(prefix_ + "+")
#            else:
#                print(prefix_ + node_.id)
                    
                
class MicroactionMathModel:

    def __init__(self, name_):
        self.name = name_
        self.inNode = MetaMathModel.SimpleNode(self.name + "_0")
        self.outNode = self.inNode
        
        self.__addOpSet = False
        self.__idCnt = 1
        
    def addInConnector(self, name_, model_):
        if self.__addOpSet:
            raise TypeError("ModelTransformer.MicroactionMathModel.addInConnector: Cannot call this function after an AddOperator has been added to the same object!")

        inCon = MetaMathModel.InNode(name_, model_, self.name + "_" + str(self.__idCnt))
        self.__idCnt += 1
        
        maxOp = MetaMathModel.MaxNode()
        maxOp.connect(self.inNode)
        maxOp.connect(inCon)
        self.outNode = maxOp

    def addResource(self, delay_=0, model_=None):

        addOp = MetaMathModel.AddNode(delay_, model_)
        
        addOp.connect(self.outNode)
        self.outNode = addOp
        self.__addOpSet = True
        
    def addOutConnector(self, name_, model_):
        if not self.__addOpSet:
            raise TypeError("ModelTransformer.MicroactionMathModel.addOutConnector: Cannot add an OutConnector for this object. The object has no AddOperator assigned to it!")

        outCon = MetaMathModel.OutNode(name_, model_, self.name + "_" + str(self.__idCnt))
        self.__idCnt += 1
        
        outCon.connect(self.outNode)
        self.outNode = outCon

        
