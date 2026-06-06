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

    def __init__(self, n_I_="0", n_D_="0", n_BrPred_="0"):
        
        # TODO: For quick test. Remove
        self.n_I = int(n_I_)
        self.n_D = int(n_D_)
        self.n_BrPred = int(n_BrPred_)

        #pass

    def transform(self, schedulingModel_:SchedulingModel):
        matrixModel = MatrixModel(schedulingModel_.name)

        for schedVar_i in schedulingModel_.getAllVariants():
            matrixVar = matrixModel.createVariant(schedVar_i.name)

            # TODO: Hack to create resource-groups. Need to get this information from SchedModel / CorePerfDSL
            for rMod_i in schedVar_i.getAllResourceModels():
                rGroup = matrixVar.createResourceGroup(rMod_i.name.upper())
                
                if rMod_i.name == "iCache":

                    iCacheConfigs = [
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 5, 'NUM_WAYS': 4, 'NUM_ROWS': 256}, # Default
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 5, 'NUM_WAYS': 2, 'NUM_ROWS': 512},
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 5, 'NUM_WAYS': 1, 'NUM_ROWS': 1024},
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 5, 'NUM_WAYS': 8, 'NUM_ROWS': 128},
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 5, 'NUM_WAYS': 16, 'NUM_ROWS': 64},
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 5, 'NUM_WAYS': 32, 'NUM_ROWS': 32},

                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 4, 'NUM_WAYS': 4, 'NUM_ROWS': 128}, # Faster memory, 1/2 cache
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 4, 'NUM_WAYS': 2, 'NUM_ROWS': 256},
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 4, 'NUM_WAYS': 1, 'NUM_ROWS': 512},
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 4, 'NUM_WAYS': 8, 'NUM_ROWS': 64},
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 4, 'NUM_WAYS': 16, 'NUM_ROWS': 32},

                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 6, 'NUM_WAYS': 4, 'NUM_ROWS': 512}, # Slower memory, 2x cache
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 6, 'NUM_WAYS': 2, 'NUM_ROWS': 1024},
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 6, 'NUM_WAYS': 1, 'NUM_ROWS': 2048},
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 6, 'NUM_WAYS': 8, 'NUM_ROWS': 256},
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 6, 'NUM_WAYS': 16, 'NUM_ROWS': 128}
                    ]

                    n = self.n_I # max: 4
                    for i in range(2**n):
                        mod = rGroup.createResourceModel((rMod_i.name + "_" + str(i)), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
                        mod.addConfig(iCacheConfigs[i])

                elif rMod_i.name == "dCache":
                    
                    dCacheConfigs = [
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 5, 'NUM_WAYS': 4, 'NUM_ROWS': 256}, # Default
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 5, 'NUM_WAYS': 2, 'NUM_ROWS': 512},
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 5, 'NUM_WAYS': 1, 'NUM_ROWS': 1024},
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 5, 'NUM_WAYS': 8, 'NUM_ROWS': 128},
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 5, 'NUM_WAYS': 16, 'NUM_ROWS': 64},
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 5, 'NUM_WAYS': 32, 'NUM_ROWS': 32},

                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 4, 'NUM_WAYS': 4, 'NUM_ROWS': 128}, # Faster memory, 1/2 cache
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 4, 'NUM_WAYS': 2, 'NUM_ROWS': 256},
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 4, 'NUM_WAYS': 1, 'NUM_ROWS': 512},
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 4, 'NUM_WAYS': 8, 'NUM_ROWS': 64},
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 4, 'NUM_WAYS': 16, 'NUM_ROWS': 32},

                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 6, 'NUM_WAYS': 4, 'NUM_ROWS': 512}, # Slower memory, 2x cache
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 6, 'NUM_WAYS': 2, 'NUM_ROWS': 1024},
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 6, 'NUM_WAYS': 1, 'NUM_ROWS': 2048},
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 6, 'NUM_WAYS': 8, 'NUM_ROWS': 256},
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 6, 'NUM_WAYS': 16, 'NUM_ROWS': 128}
                    ]

                    n = self.n_D # max: 4
                    for i in range(2**n):
                        mod = rGroup.createResourceModel((rMod_i.name + "_" + str(i)), "map_models/DCacheModel.h", rMod_i.getAllTraceValues())
                        mod.addConfig(dCacheConfigs[i])

                elif rMod_i.name == "divider":
                    if "CV32E40P" in schedVar_i.name:
                        modelLink = "map_models/Divider_CV32E40P.h"
                    elif "CVA6" in schedVar_i.name:
                        modelLink = "map_models/Divider_CVA6.h"
                    else:
                        raise RuntimeError("Cannot handle this variant yet. Expand HACK!")
                    rGroup.createResourceModel(rMod_i.name, modelLink, rMod_i.getAllTraceValues())

                elif rMod_i.name == "divider_u":
                    if "CV32E40P" in schedVar_i.name:
                        modelLink = "map_models/DividerUnsigned_CV32E40P.h"
                    elif "CVA6" in schedVar_i.name:
                        modelLink = "map_models/DividerUnsigned_CVA6.h"
                    else:
                        raise RuntimeError("Cannot handle this variant yet. Expand HACK!")
                    rGroup.createResourceModel(rMod_i.name, modelLink, rMod_i.getAllTraceValues())
                    
                else:
                    print(f"WARNING: Currently no idea how to handle resource-model {rMod_i.name}...EXPAND HACK!")

            matrixVar.createAllResourceCombinations()

            # TODO: Hack to create branch-group
            brGroup = matrixVar.createBranchGroup()
            
            if "CV32E40P" in schedVar_i.name:

                branchConfig = [
                    {'NUM_PAGES': 2, 'NUM_ROWS': 64}, # Default
                    {'NUM_PAGES': 4, 'NUM_ROWS': 32},
                    {'NUM_PAGES': 2, 'NUM_ROWS': 128}, # Increased size
                    {'NUM_PAGES': 4, 'NUM_ROWS': 64},
                    {'NUM_PAGES': 2, 'NUM_ROWS': 32}, # Decreased size
                    {'NUM_PAGES': 4, 'NUM_ROWS': 16},
                ]

                n = self.n_BrPred # max: 3
                for i in range(2**n):
                    if i == 0:
                        brGroup.createBranchModel("branch_ant", "map_models/Branch_ant.h", ["pc", "brTarget"]) # always non-taken
                    elif i == 1:
                        brGroup.createBranchModel("branch_fnt_bt", "map_models/Branch_fnt_bt.h", ["pc", "brTarget"]) # forward: non-taken, backward: taken
                    else:
                        j = i-2
                        mod = brGroup.createBranchModel("branch_2sat_" + str(j), "map_models/Branch_2sat.h", ["pc", "brTarget"]) # Dynamic 2-sat.
                        mod.addConfig(branchConfig[j])

            elif "CVA6" in schedVar_i.name:

                branchConfig = [
                    {'BHT_NUM_PAGES': 2, 'BHT_NUM_ROWS': 64, 'BTB_NUM_PAGES': 2, 'BTB_NUM_ROWS': 16, 'RAS_SIZE': 2},  # Default
                    {'BHT_NUM_PAGES': 2, 'BHT_NUM_ROWS': 128, 'BTB_NUM_PAGES': 2, 'BTB_NUM_ROWS': 16, 'RAS_SIZE': 2},
                    {'BHT_NUM_PAGES': 2, 'BHT_NUM_ROWS': 64, 'BTB_NUM_PAGES': 2, 'BTB_NUM_ROWS': 32, 'RAS_SIZE': 2},
                    {'BHT_NUM_PAGES': 2, 'BHT_NUM_ROWS': 128, 'BTB_NUM_PAGES': 2, 'BTB_NUM_ROWS': 32, 'RAS_SIZE': 2},
                    {'BHT_NUM_PAGES': 2, 'BHT_NUM_ROWS': 64, 'BTB_NUM_PAGES': 2, 'BTB_NUM_ROWS': 16, 'RAS_SIZE': 4},
                    {'BHT_NUM_PAGES': 2, 'BHT_NUM_ROWS': 128, 'BTB_NUM_PAGES': 2, 'BTB_NUM_ROWS': 16, 'RAS_SIZE': 4},
                    {'BHT_NUM_PAGES': 2, 'BHT_NUM_ROWS': 64, 'BTB_NUM_PAGES': 2, 'BTB_NUM_ROWS': 32, 'RAS_SIZE': 4},
                    {'BHT_NUM_PAGES': 2, 'BHT_NUM_ROWS': 128, 'BTB_NUM_PAGES': 2, 'BTB_NUM_ROWS': 32, 'RAS_SIZE': 4},
                ]

                n = self.n_BrPred # max: 3
                for i in range(2**n):
                    mod = brGroup.createBranchModel("branch_cva6", "map_models/Branch_CVA6.h", ["pc", "brTarget", "imm", "typeId", "rs1", "rd"])
                    mod.addConfig(branchConfig[i]) # Default

            else:
                raise RuntimeError("No idea how to generate a branch model here. Expand the hack...")

            # Create combinations for all involved models
            matrixVar.createAllCombinations()

            matrixVar.createTimingVariableSet([(t.name, t.numElements) for t in schedVar_i.getAllTimingVariables()])
            # TODO: Need to get this information from the model
            if "CV32E40P" in schedVar_i.name:
                matrixVar.addStaticConnectorSet("R", [("Xa", "rs1"), ("Xb", "rs2")], [("Xd", "rd")], 32)
                matrixVar.createBranchSet(["Pc"], ["Pc_p", "Pc_np"])
            elif "CVA6" in schedVar_i.name:
                matrixVar.addStaticConnectorSet("R", [("Xa", "rs1"), ("Xb", "rs2")], [("Xd", "rd")], 32)
                matrixVar.addStaticConnectorSet("Cb", [("Cb_out", "rd")], [("Cb_in", "rd")], 32, [0])

                matrixVar.createBranchSet(["Pc_mp", "Pc_pt"], ["Pc_p", "Pc_p_j", "Pc_p_jr", "Pc_c"])
            else:
                raise RuntimeError("Cannot handle this variant yet. Expand hack!")

            for schedFunc_i in schedVar_i.getAllSchedulingFunctions():

                instr = matrixVar.createInstruction(schedFunc_i.name, schedFunc_i.identifier)

                # Generate Scheduling-Graph (networkx)
                schedGraph = nx.DiGraph()
                openNodes = [schedFunc_i.getRootNode()]
                while openNodes:
                    curNode = openNodes.pop(0)

                    if curNode.hasDynamicDelay():
                        resModel = curNode.getResourceModel() # TODO: Hack to find a resource-group

                        if resModel.name == "iCache":
                            weight = DynamicElement(instr.createDynamicDelay(resModel.name.upper(), condition_=("pc & 0xC != 0", ["pc"], 1)))
                        else:
                            weight = DynamicElement(instr.createDynamicDelay(resModel.name.upper()))
                        
                        #weight = DynamicElement(instr.createDynamicDelay(resModel.name.upper()))
                    else:
                        weight = curNode.getDelay()

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
                                    maxWeight.max(weight)
                                else:
                                    if isinstance(weight, DynamicElement):
                                        maxWeight = DynamicElement(maxWeight)
                                        maxWeight.max(weight)
                                    else:
                                        maxWeight = max(maxWeight, weight)                            

                        cInstrMatrix.addElement(inVar_i, outVar_i, maxWeight)

                cInstrMatrix.finalize()

                #if instr.name == "divu":
                #    cInstrMatrix.show()
                #    print()
                #    raise RuntimeError("COFO")

            matrixVar.finalize()

            #print("+++++++++++++++++++++++++++ BRANCH INFO +++++++++++++++++++++++++++")
            #brSet = matrixVar.branchSet
            #for i, inVar_i in enumerate(brSet.inVariables):
            #    print(f"{inVar_i.name} -> row: {brSet.rowOffsetIn+i} | col: {brSet.colOffsetIn+i}")
            #for i, outVar_i in enumerate(brSet.outVariables):
            #    print(f"{outVar_i.name} -> row: {brSet.rowOffsetOut+i} | col: {brSet.colOffsetOut+i}")
            #print(f"Dimension: {matrixVar.dimension}")

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
            tv = edge_.getTimingVariable()
            if tv.hasMultiElements():
                return f"{tv.name}__{edge_.depth}"
            else:
                return tv.name
        return edge_.name