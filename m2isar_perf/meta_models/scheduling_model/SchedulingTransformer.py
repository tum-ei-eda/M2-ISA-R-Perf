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

from .SchedulingModel import SchedulingModel
from meta_models.structural_model.StructuralModel import StructuralModel

class SchedulingTransformer:

    def __init__(self):
        pass

    def transform(self, structuralModel_:StructuralModel) -> SchedulingModel:

        schedulingModel = SchedulingModel(structuralModel_.name)

        for var_i in structuralModel_.getAllVariants():
            variant = schedulingModel.createVariant(var_i.name)
            self.__generateExternalModels(var_i, variant)
            self.__generateTimingVariables(var_i, variant)
            self.__generateSchedulingFunction(var_i, variant)
        return schedulingModel

    def __generateExternalModels(self, structVariant_, schedVariant_):
        for model_i in structVariant_.getAllModels():
            extModel = schedVariant_.createExternalModel(model_i.name, model_i.link, model_i.isConnectorModel, model_i.isResourceModel, model_i.isConfigurable())
            extModel.addTraceValues([t.name for t in model_i.getTraceValues()])
    
    def __generateTimingVariables(self, structVariant_, schedVariant_):
        for st_i in structVariant_.getAllStages():            
            schedVariant_.createTimingVariable(st_i.name, st_i.capacity, st_i.isPrimaryStage())
        
    def __generateSchedulingFunction(self, structVariant_, schedVariant_):

        for instr_i in structVariant_.getAllUsedInstructions():
            pipeline = structVariant_.getPipeline()

            # Create scheduling function and root node
            schedFunc = schedVariant_.createSchedulingFunction(instr_i.name, instr_i.identifier)
            stageNode = schedFunc.createNode("Enter") # Create root node
            schedFunc.setRootNode(stageNode)

            self.__createStageNodes(schedFunc, instr_i, pipeline.getFirstStages(), stageNode)
                
    def __createStageNodes(self, schedFunc_, instr_, initStages_, root_):
        initialStages = [s.name for s in initStages_]
        openStages = [(s, root_) for s in initStages_] # (stage, <node to be connected to this stage>)
        resolvedStages = {} # stageName: <list of pathStartNodes of this stage>
        startNodes = []
        endNodes = []
        
        while openStages:
            (curStage, prevNode) = openStages.pop(0)

            # Ignore stage if it is not used by the instr (i.e. none of its microactions are mapped to the instr)
            # NOTE: This will abord the entire path (i.e. also following stages) Is this the wanted behavior?
            if not curStage.isUsedByInstr(instr_):
                continue
            
            if curStage.name not in resolvedStages:

                # Create node for this stage
                curStageNode = schedFunc_.createNode(curStage.name)
                curStageNode.createStaticOutEdge(curStage.name)

                # If stage can hold multiple instructions (capacity > 1), set in-order guards
                # (Ref. "Flexible Generation" paper, eq.: 22)
                if curStage.capacity > 1:
                    curStageNode.createStaticInEdge(curStage.name, 1)
                    
                # Put back-pressure from this stage on previous node
                prevNode.createStaticInEdge(curStage.name, curStage.capacity)

                # If this stage is blocked, put back-pressure of blocking stage on previous node
                for blockStage_i in curStage.getBlockingStages():
                    prevNode.createStaticInEdge(blockStage_i.name, 1)
                
                # Lists to hold start and end nodes of this stage's paths
                pathStartNodes = []
                pathEndNodes = []
                
                # Resolve the microactions if existing
                for microAction_i in curStage.getMicroactions():
                    if microAction_i.isUsedByInstr(instr_):
                    
                        # Create resource nodes
                        resNodes = []
                        if microAction_i.hasResources():
                            for res_i in microAction_i.getResources():
                                resNode = schedFunc_.createNode(res_i.name)
                                if res_i.hasDynamicDelay():
                                    resNode.linkResourceModel(res_i.getResourceModelName())
                                else:
                                    resNode.setDelay(res_i.delay)
                                resNodes.append(resNode)
                        else:  # Zero node, if microaction does not specify a resource
                            resNode = schedFunc_.createNode(microAction_i.name)
                            resNodes.append(resNode)

                        # Connect resource nodes
                        for resNode_i in resNodes:

                            # Connect resource nodes to previous stage (prevNode), and mark as pathStartNode
                            prevNode.connectNode(resNode_i)
                            pathStartNodes.append(resNode_i)
                            
                            # Connect resource node to this stage's node
                            resNode_i.connectNode(curStageNode)                        

                            # Add dynamic edges to resource node
                            for inCon_i in microAction_i.getInConnectors():
                                resNode_i.createDynamicInEdge(inCon_i.name, inCon_i.getConnectorModel().name)
                            for outCon_i in microAction_i.getOutConnectors():
                                resNode_i.createDynamicOutEdge(outCon_i.name, outCon_i.getConnectorModel().name)
                                            
                # Resolve sub-pipelines if existing:
                # This will connect the startNodes of the sub-pipelines to prevNode!
                if curStage.getFirstSubStages():
                    subNodes = self.__createStageNodes(schedFunc_, instr_, curStage.getFirstSubStages(), prevNode)
                    subPipeStartNodes = subNodes[0]
                    subPipeEndNodes = subNodes[1]

                    for endNode_i in subPipeEndNodes:
                        if curStage.hasOutputBuffer:
                            endNode_i.connectNode(curStageNode)
                        else:
                            curStageNode.mergeNode(endNode_i)

                    pathStartNodes.extend(subPipeStartNodes)
                                            
                # Mark stage as resolved and store start nodes as reference
                resolvedStages[curStage.name] = pathStartNodes

                # If current state is one of the first stages of this (sub-)pipeline, store its startNodes as entry points for the parent stage
                if curStage.name in initialStages:
                    startNodes.extend(pathStartNodes)
                    
                # Schedule this stage's next stages to be resolved,
                # or report endNodes to parentStage
                nxtStages = curStage.getNextStages()
                if nxtStages:
                    for i in nxtStages:
                        openStages.append((i, curStageNode))
                else: # No next stage -> report stageNode as endNode to parentStage
                    endNodes.append(curStageNode)        
                
            else: # curStage already resolved
                curStartNodes = resolvedStages[curStage.name]

                # Connect start nodes of current stage's paths with previous node
                for node_i in curStartNodes:
                    prevNode.connectNode(node_i)

        return (startNodes, endNodes)
