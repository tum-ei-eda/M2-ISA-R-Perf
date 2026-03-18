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

from .MatrixModel import MatrixModel
from meta_models.scheduling_model.SchedulingModel import SchedulingModel

import networkx as nx

class MatrixTransformer:

    def __init__(self):
        pass

    def transform(self, schedulingModel_:SchedulingModel):
        matrixModel = MatrixModel(schedulingModel_.name)

        for schedVar_i in schedulingModel_.getAllVariants():
            matrixVar = matrixModel.createVariant(schedVar_i.name)

            for timingVar_i in schedVar_i.getAllTimingVariables():
                matrixVar.addTimingVariable(timingVar_i.name, timingVar_i.numElements)

            # TODO: Need to get this information from the model
            matrixVar.addRegisterSet([("Xa", "rs1"), ("Xb", "rs2")], [("Xd", "rd")], 32)
            matrixVar.addBranchSet(["Pc"], ["Pc_p", "Pc_np"])

            for schedFunc_i in schedVar_i.getAllSchedulingFunctions():

                skipInstr = False # TODO: This should be removed as soon as we can cover all features (e.g. dynamic delays)

                # Generate Scheduling-Graph (networkx)
                schedGraph = nx.DiGraph()
                openNodes = [schedFunc_i.getRootNode()]
                while openNodes:
                    curNode = openNodes.pop(0)

                    if curNode.hasDynamicDelay():
                        print(f"{schedVar_i.name}::{schedFunc_i.name}::{curNode.name} has dynamic delay. I cannot handle that yet!")
                        skipInstr = True
                        break
                    delay = curNode.getDelay()

                    for inEdge_i in curNode.getAllInEdges():
                        inVar = matrixVar.getInVariable(self.__getEdgeName(inEdge_i))
                        schedGraph.add_edge(inVar.getGraphName(), curNode.name, weight=0)

                    for outNode_i in curNode.getAllOutNodes():
                        openNodes.append(outNode_i)
                        schedGraph.add_edge(curNode.name, outNode_i.name, weight=delay)

                    for outEdge_i in curNode.getAllOutEdges():
                        outVar = matrixVar.getOutVariable(self.__getEdgeName(outEdge_i))
                        schedGraph.add_edge(curNode.name, outVar.getGraphName(), weight=delay)

                if skipInstr:
                    continue
                
                # Create compressed Instruction-Matrix object
                cInstrMatrix = matrixVar.createCompInstrMatrix(schedFunc_i.name, schedFunc_i.identifier)

                # Calculate longest path between all out- and in-variable pairs
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
                                maxWeight = max(maxWeight, weight)

                        cInstrMatrix.addElement(inVar_i, outVar_i, maxWeight)

        return matrixModel

    def __getPathWeight(self, schedGraph_, path_):
        w = 0
        for i, j in zip(path_[:-1], path_[1:]):
            w += schedGraph_[i][j]["weight"]
        return w

    def __getEdgeName(self, edge_):
        if not edge_.isDynamic():
            if edge_.depth > 1:
                raise RuntimeError(f"Edge-depth is {egde_.depth} (>1). I cannot handle this yet!")
        return edge_.name if edge_.isDynamic() else edge_.getTimingVariable().name