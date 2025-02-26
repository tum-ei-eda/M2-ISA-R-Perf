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

        schedulingModel = SchedulingModel()

        for var_i in structuralModel_.getAllVariants():

            variant = schedulingModel.createVariant(var_i.name)

            self.__generateResourceModels(var_i, variant)
            self.__generateConnectorModels(var_i, variant)
            self.__generateTimingVariables(var_i, variant)
            self.__generateSchedulingFunction(var_i, variant)
            
        return schedulingModel

    def __generateResourceModels(self, structVariant_, schedVariant_):
        for resM_i in structVariant_.getAllResourceModels():
            resModel = schedVariant_.createResourceModel(resM_i.name, resM_i.link)
            resModel.addTraceValues([t.name for t in resM_i.getTraceValues()])

    def __generateConnectorModels(self, structVariant_, schedVariant_):
        for conM_i in structVariant_.getAllConnectorModels():
            conModel = schedVariant_.createConnectorModel(conM_i.name, conM_i.link)
            conModel.addTraceValues([t.name for t in conM_i.getTraceValues()])

    def __generateTimingVariables(self, structVariant_, schedVariant_):

        for st_i in structVariant_.getAllStages():
            
            schedVariant_.createTimingVariable(st_i.name, st_i.capacity)

            # # Create timing variable or alias
            # if self.__stageHasOwnTimingVariable(st_i):
            #     schedVariant_.createTimingVariable(st_i.name, st_i.capacity)
            # else:
            #     schedVariant_.createTimingVariableAlias(st_i.name, st_i.getParentStage().name)


            
            ## Check if (sub-)stage requires own timing variable, or can use parentStage's timing variable (via alias)
            ## (Ref. "Flexible Generation" paper, eq.: 21)
            #createVariable = False
            #createAlias = False
            #if st_i.isPrimaryStage():
            #    createVariable = True
            #else:
            #    parentStage = st_i.getParentStage()
            #    if st_i in parentStage.getLastSubStages():
            #        if parentStage.hasOutputBuffer:
            #            createVariable = True
            #        else:
            #            createAlias = True
            #            targetName = parentStage.name
            #    else:
            #        createVariable = True
            
            ## Create timing variable or alias
            #if (createVariable and createAlias) or (not createVariable and not createAlias):
            #    raise RuntimeError(f"Stage {st_i.name} is misbehaving: Each stage should either create a timing variable or an alias!")
            #elif createVariable:
            #    print(f"{st_i.name}: {st_i.isPrimaryStage()} -> implement")
            #    schedVariant_.createTimingVariable(st_i.name)
            #elif createAlias:
            #    print(f"{st_i.name}: {st_i.isPrimaryStage()} -> shadow")
            #    schedVariant_.createTimingVariableAlias(st_i.name, targetName)

        # TODO: Check what makes sense here
        #lastStageName = structVariant_.getPipeline().getLastStage().name
        #schedVariant_.getTimingVariable(lastStageName).setLastStage()
        endStages = [x.name for x in structVariant_.getPipeline().getLastStages()]
        for st_i in endStages:
            schedVariant_.getTimingVariable(st_i).setEndStage()
        
    #def __generateTimingVariables(self, structVariant_, schedVariant_):
    #    for st_i in structVariant_.getAllStages():
    #        schedVariant_.createTimingVariable(st_i.name)
    #
    #    lastStageName = structVariant_.getPipeline().getLastStage().name
    #    schedVariant_.getTimingVariable(lastStageName).setLastStage()

    def __generateSchedulingFunction(self, structVariant_, schedVariant_):

        for instr_i in structVariant_.getAllInstructions():
            pipeline = structVariant_.getPipeline()

            # Create scheduling function and root node
            schedFunc = schedVariant_.createSchedulingFunction(instr_i.name, instr_i.identifier)
            stageNode = schedFunc.createNode("Enter") # Create root node
            schedFunc.setRootNode(stageNode)

            self.__unnamedHelper(schedFunc, instr_i, pipeline.getFirstStages(), stageNode)
            
            #resolvedStages = {}
            #openStages = []
            #for st_i in pipeline.getFirstStages():
            #    openStages.append((st_i, stageNode))
            #
            #while openStages:
            #    (curStage, curNode) = openStages.pop(0)
            #    
            #    if curStage.name in resolvedStages:
            #        nxNode = resolvedStages[curStage.name]
            #    else:
            #        # Create a node for stage
            #        nxNode = schedFunc.createNode(curStage.name)
            #        resolvedStages[curStage.name] = nxNode
            #
            #        # Add next stages for this stage
            #        for nxStage_i in curStage.getNextStages():
            #            openStages.append((nxStage_i, nxNode))
            #
            #    curNode.connectNode(nxNode)
                    
                
    def __unnamedHelper(self, schedFunc_, instr_, initStages_, root_):
        initialStages = [s.name for s in initStages_]
        openStages = [(s, root_) for s in initStages_] # (stage, <node to be connected to this stage>)
        resolvedStages = {} # stageName: <list of pathStartNodes of this stage>
        startNodes = []
        endNodes = []
        
        while openStages:
            (curStage, prevNode) = openStages.pop(0)

            # Ignore stage if it is not used by the instr (i.e. none of its microactions are mapped to the instr)
            # NOTE: This will abord the entire path (i.e. also following stages) Is this the wanted behavior?
            if not curStage.isUsedBy(instr_):
                continue
            
            if curStage.name not in resolvedStages:

                # Create node for this stage
                curStageNode = schedFunc_.createNode(curStage.name)
                curStageNode.createStaticOutEdge(curStage.name)

                # If stage can hold multiple instructions (capacity > 1), set in-order guards
                # (Ref. "Flexible Generation" paper, eq.: 22)
                if curStage.capacity > 1:
                    curStageNode.createStaticInEdge(curStage.name, 1)

                ## Create node for this stage (unless stage shares node with it's parent stage)
                #if self.__stageHasOwnTimingVariable(curStage):
                #    curStageNode = schedFunc_.createNode(curStage.name)
                #    curStageNode.createStaticOutEdge(curStage.name)
                #
                #    # If stage can hold multiple instructions (capacity > 1), set in-order guards
                #    # (Ref. "Flexible Generation" paper, eq.: 22)
                #    if curStage.capacity > 1:
                #        curStageNode.createStaticInEdge(curStage.name, 1)
                    
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
                    if microAction_i in instr_.getUsedMicroactions():

                        # Create resource node
                        if microAction_i.hasResource():
                            resource = microAction_i.getResource()
                            resNode = schedFunc_.createNode(resource.name)
                            if resource.hasDynamicDelay():
                                resNode.linkResourceModel(resource.getResourceModelName())
                            else:
                                resNode.setDelay(resource.delay)
                        else: # Zero node, if microaction does not specify a resource
                            resNode = schedFunc_.createNode(microAction_i.name)

                        # Connect resource node to previous stage (prevNode), and mark as pathStartNode
                        prevNode.connectNode(resNode)
                        pathStartNodes.append(resNode)
                        
                        # Connect resource node to this stage's node
                        resNode.connectNode(curStageNode)
                        
                        #pathEndNodes.append(resNode)
                            
                        # Add dynamic edges to resource node
                        if microAction_i.hasInConnector():
                            connector = microAction_i.getInConnector()
                            resNode.createDynamicInEdge(connector.name, connector.getConnectorModel().name)
                        if microAction_i.hasOutConnector():
                            connector = microAction_i.getOutConnector()
                            resNode.createDynamicOutEdge(connector.name, connector.getConnectorModel().name)
                
                # Resolve sub-pipelines if existing:
                # This will connect the startNodes of the sub-pipelines to prevNode!
                if curStage.getFirstSubStages():
                    subNodes = self.__unnamedHelper(schedFunc_, instr_, curStage.getFirstSubStages(), prevNode)
                    #pathStartNodes.extend(subNodes[0])
                    #pathEndNodes.extend(subNodes[1])

                    subPipeStartNodes = subNodes[0]
                    subPipeEndNodes = subNodes[1]

                    for endNode_i in subPipeEndNodes:
                        if curStage.hasOutputBuffer:
                            endNode_i.connectNode(curStageNode)
                        else:
                            curStageNode.mergeNode(endNode_i)

                    pathStartNodes.extend(subPipeStartNodes)
                            
                ## Connect the endNodes of current stage's paths, with current stages main node
                #if self.__stageHasOwnTimingVariable(curStage):
                #    for node_i in pathEndNodes:
                #        node_i.connectNode(curStageNode)
                
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
                #else: # No next stage -> report endNodes to parentStage
                #    if self.__stageHasOwnTimingVariable(curStage):
                #        endNodes.append(curStageNode)
                #    else:
                #        endNodes.extend(pathEndNodes)
        
                
            else: # curStage already resolved
                curStartNodes = resolvedStages[curStage.name]

                # Connect start nodes of current stage's paths with previous node
                for node_i in curStartNodes:
                    prevNode.connectNode(node_i)

        return (startNodes, endNodes)

    # Check if (sub-)stage requires own timing variable, or can use parentStage's timing variable (via alias)
    # (Ref. "Flexible Generation" paper, eq.: 21)
    def __stageHasOwnTimingVariable(self, stage_):
        if stage_.isPrimaryStage():
            return True
        else:
            parentStage = stage_.getParentStage()
            if stage_ in parentStage.getLastSubStages():
                if parentStage.hasOutputBuffer:
                    return True
                else:
                    return False
            else:
                return True

    
    
#    def __generateSchedulingFunction(self, structVariant_, schedVariant_):
#        for instr_i in structVariant_.getAllInstructions():
#            pipeline = structVariant_.getPipeline()
#            
#            # Create scheduling function and root node
#            schedFunc = schedVariant_.createSchedulingFunction(instr_i.name, instr_i.identifier)
#            stageNode = schedFunc.createNode("Enter") # Create root node
#            schedFunc.setRootNode(stageNode)
#            stageNode.createStaticInEdge(pipeline.getFirstStage().name)
#
#            
#            for stage_i in structVariant_.getPipeline().stages:
#
#                # Create resource nodes
#                resourceNodes = []
#                for microAction_i in stage_i.getUsedMicroactions():
#                    if microAction_i in instr_i.getUsedMicroactions():
#                        
#                        # Add resource node
#                        if microAction_i.hasResource():
#                            resource = microAction_i.getResource()
#                            resNode = schedFunc.createNode(resource.name)
#                            if resource.hasDynamicDelay():
#                                resNode.setResourceModel(schedVariant_.getResourceModel(resource.getResourceModelName()))
#                            else:
#                                resNode.setDelay(resource.delay)
#                        else:
#                            resNode = schedFunc.createNode(microAction_i.name) # Zero node if microaction does not specify a resource
#                            resourceNodes.append(resNode)
#                            stageNode.connectNode(resNode) # Connect resource node to previous stage node
#
#                        # Add dynamic egdes to resource node
#                        if microAction_i.hasInConnector():
#                            connector = microAction_i.getInConnector()
#                            resNode.createDynamicInEdge(connector.name, connector.getConnectorModel().name)
#                        if microAction_i.hasOutConnector():
#                            connector = microAction_i.getOutConnector()
#                            resNode.createDynamicOutEdge(connector.name, connector.getConnectorModel().name)
#
#                            
#                # Create stage node
#                if resourceNodes: # Do not consider this stage, if it is not used (i.e. has no resource-node). TODO: Makes sense for CV32E40P? How about others?
#                    stageNode = schedFunc.createNode(stage_i.name)
#                    stageNode.createStaticOutEdge(stage_i.name)
#                    if not pipeline.isLastStage(stage_i):
#                        stageNode.createStaticInEdge(pipeline.getNextStage(stage_i).name)
#                        # Connect resource nodes of this stage to stageNode
#                    for rn_i in resourceNodes:
#                        rn_i.connectNode(stageNode)
#
#            # Set end node
#            schedFunc.setEndNode(stageNode)
