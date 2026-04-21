# 
#  Copyright 2026 Chair of EDA, Technical University of Munich
# 
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
# 
# 	 http://www.apache.org/licenses/LICENSE-2.0
# 
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

from .MatrixModel import MatrixModel, DynamicElement
from meta_models.scheduling_model.SchedulingModel import SchedulingModel

import networkx as nx
from itertools import product

class MatrixTransformer:

    def __init__(self):
        pass

    def transform(self, schedulingModel_:SchedulingModel):
        matrixModel = MatrixModel(schedulingModel_.name)

        for schedVar_i in schedulingModel_.getAllVariants():
            matrixVar = matrixModel.createVariant(schedVar_i.name)

            # TODO: Hack to create resource-groups. Need to get this information from SchedModel / CorePerfDSL
            for rMod_i in schedVar_i.getAllResourceModels():
                rGroup = matrixVar.createResourceGroup(rMod_i.name.upper())
                
                if rMod_i.name == "iCache":
                    rGroup.createResourceModel(rMod_i.name, "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
                elif rMod_i.name == "divider":
                    rGroup.createResourceModel(rMod_i.name, "map_models/Divider_CV32E40P.h", rMod_i.getAllTraceValues())
                elif rMod_i.name == "divider_u":
                    rGroup.createResourceModel(rMod_i.name, "map_models/DividerUnsigned_CV32E40P.h", rMod_i.getAllTraceValues())
                else:
                    print(f"WARNING: Currently no idea how to handle resource-model {rMod_i.name}...EXPAND HACK!")

            # TODO: Hack to create branch-group
            brGroup = matrixVar.createBranchGroup()
            brGroup.createBranchModel("branch_ant", "map_models/Branch_ant.h", ["pc", "brTarget"])

            # Create combinations for all involved models
            for brMod_i in matrixVar.getBranchGroup().getAllModels():
                for resModComb_i in product(*(g.getAllModels() for g in matrixVar.getAllResourceGroups())):
                    matrixVar.createCombination(brMod_i, resModComb_i)


            for timingVar_i in schedVar_i.getAllTimingVariables():
                matrixVar.addTimingVariable(timingVar_i.name, timingVar_i.numElements)

            # TODO: Need to get this information from the model
            matrixVar.addRegisterSet([("Xa", "rs1"), ("Xb", "rs2")], [("Xd", "rd")], 32)
            matrixVar.addBranchSet(["Pc"], ["Pc_p", "Pc_np"])

            for schedFunc_i in schedVar_i.getAllSchedulingFunctions():

                #skipInstr = False # TODO: This should be removed as soon as we can cover all features (e.g. dynamic delays)

                instr = matrixVar.createInstruction(schedFunc_i.name, schedFunc_i.identifier)

                # Generate Scheduling-Graph (networkx)
                schedGraph = nx.DiGraph()
                openNodes = [schedFunc_i.getRootNode()]
                while openNodes:
                    curNode = openNodes.pop(0)

                    if curNode.hasDynamicDelay():

                        # TODO: Hack to find a resource-group
                        resModel = curNode.getResourceModel()

                        weight = DynamicElement(instr.createDynamicDelay(resModel.name.upper()))
                    else:
                        weight = curNode.getDelay()

#                    if curNode.hasDynamicDelay():
#                        print(f"{schedVar_i.name}::{schedFunc_i.name}::{curNode.name} has dynamic delay. I cannot handle that yet!")
#                        skipInstr = True
#                        break
#                    delay = curNode.getDelay()

                    for inEdge_i in curNode.getAllInEdges():
                        inVar = matrixVar.getInVariable(self.__getEdgeName(inEdge_i))
                        schedGraph.add_edge(inVar.getGraphName(), curNode.name, weight=0)

                    for outNode_i in curNode.getAllOutNodes():
                        if outNode_i not in openNodes:
                            openNodes.append(outNode_i)
                        schedGraph.add_edge(curNode.name, outNode_i.name, weight=weight)

                    for outEdge_i in curNode.getAllOutEdges():
                        outVar = matrixVar.getOutVariable(self.__getEdgeName(outEdge_i))
                        schedGraph.add_edge(curNode.name, outVar.getGraphName(), weight=weight)

                #if skipInstr:
                #    continue
                
                # Calculate longest path between all out- and in-variable pairs to create the compressed Instr-Matrix
                cInstrMatrix = instr.getCompressedInstructionMatrix()
                for outVar_i in matrixVar.getAllOutVariables():
                    
                    if outVar_i.getGraphName() not in schedGraph:                        
                        cInstrMatrix.addDefaultRow(outVar_i)
                        continue
                    
                    for inVar_i in matrixVar.getAllInVariables():
                        
                        if inVar_i.getGraphName() not in schedGraph:
                            cInstrMatrix.addElement(inVar_i, outVar_i, -1)
                            continue
                        
                        paths = list(nx.all_simple_paths(schedGraph, inVar_i.getGraphName(), outVar_i.getGraphName()))

                        if not paths:
                            cInstrMatrix.addElement(inVar_i, outVar_i, -1)
                            continue

                        maxWeight = -1
                        for path_i in paths:
                            weight = self.__getPathWeight(schedGraph, path_i)
                            if maxWeight == -1:
                                maxWeight = weight
                            else:
                                if isinstance(maxWeight, DynamicElement):
                                    #maxWeight = maxWeight.compare(weight)
                                    maxWeight.max(weight)
                                else:
                                    if isinstance(weight, DynamicElement):
                                        maxWeight = DynamicElement(maxWeight)
                                        #maxWeight = maxWeight.compare(weight)
                                        maxWeight.max(weight)
                                    else:
                                        maxWeight = max(maxWeight, weight)                            

                        cInstrMatrix.addElement(inVar_i, outVar_i, maxWeight)

        return matrixModel

    def __getPathWeight(self, schedGraph_, path_):
        weight = 0
        for i, j in zip(path_[:-1], path_[1:]):
            w = schedGraph_[i][j]["weight"]
            if isinstance(weight, DynamicElement):
                weight.add(w)
            else:
                if isinstance(w, DynamicElement):
                    weight = DynamicElement(weight)
                    weight.add(w)
                else:
                    weight += w
        return weight

    def __getEdgeName(self, edge_):
        if not edge_.isDynamic():
            if edge_.depth > 1:
                raise RuntimeError(f"Edge-depth is {edge_.depth} (>1). I cannot handle this yet!")
        return edge_.name if edge_.isDynamic() else edge_.getTimingVariable().name