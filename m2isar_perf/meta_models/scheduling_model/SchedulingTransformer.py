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
from meta_models.structural_model.StructuralModel import TopModel

class SchedulingTransformer:

    def __init__(self):
        pass

    def transform(self, structuralModel_:TopModel) -> SchedulingModel:

        schedulingModel = SchedulingModel()

        for var_i in structuralModel_.getAllCorePerfModels():

            variant = schedulingModel.createVariant(var_i.name)

            self.__generateResourceModels(var_i, variant)
            self.__generateConnectorModels(var_i, variant)
            self.__generateTimingVariables(var_i, variant)
            self.__generateSchedulingFunction(var_i, variant)
            
            # Generate SchedulingFunctions
            #for instr_i in var_i.getAllInstructions():
            #    schedFunc = variant.createSchedulingFunction(instr_i.name, instr_i.identifier)
            #
            #    # Create root node
            #    stageNode = schedFunc.createNode("Enter")
            #    schedFunc.setRootNode(stageNode)
            #    
            #    usedMicroActions = instr_i.getUsedMicroactions() # Microactions used by this instruction
            #    for stage_i in var_i.getPipeline().stages:
            #
            #        # Create resource nodes
            #        resourceNodes = []
            #        for microAction_i in stage_i.getUsedMicroactions():
            #            if microAction_i in usedMicroActions:
            #
            #                # Add resource node
            #                if microAction_i.hasResource():
            #                    resource = microAction_i.getResource()
            #                    resNode = schedFunc.createNode(resource.name)
            #                    if resource.hasDynamicDelay():
            #                        resNode.setResourceModel(variant.getResourceModel(resource.getResourceModelName()))
            #                    else:
            #                        resNode.setDelay(resource.delay)
            #                else:
            #                    resNode = schedFunc.createNode(microAction_i.name) # Zero node if microaction does not specify a resource
            #
            #                resourceNodes.append(resNode)
            #                    
            #                # Connect resource node to previous stage node
            #                stageNode.connectNode(resNode)
            #
            #        # Create stage node
            #        if resourceNodes: # Do not consider this stage, if it is not used. TODO: Makes sense for CV32E40P? How about others?
            #
            #            # Add stage node
            #            stageNode = schedFunc.createNode(stage_i.name)
            #
            #            # Connect resource nodes to stage node
            #            for rn_i in resourceNodes:
            #                rn_i.connectNode(stageNode)
            #
            #    # Set end node
            #    schedFunc.setEndNode(stageNode)
                
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
            schedVariant_.createTimingVariable(st_i.name)

        lastStageName = structVariant_.getPipeline().getLastStage().name
        schedVariant_.getTimingVariable(lastStageName).setLastStage()

    def __generateSchedulingFunction(self, structVariant_, schedVariant_):
        for instr_i in structVariant_.getAllInstructions():
            pipeline = structVariant_.getPipeline()
            
            # Create scheduling function and root node
            schedFunc = schedVariant_.createSchedulingFunction(instr_i.name, instr_i.identifier)
            stageNode = schedFunc.createNode("Enter") # Create root node
            schedFunc.setRootNode(stageNode)
            stageNode.createStaticInEdge(pipeline.getFirstStage().name)

            
            for stage_i in structVariant_.getPipeline().stages:

                # Create resource nodes
                resourceNodes = []
                for microAction_i in stage_i.getUsedMicroactions():
                    if microAction_i in instr_i.getUsedMicroactions():
                    
                        # Add resource node
                        if microAction_i.hasResource():
                            resource = microAction_i.getResource()
                            resNode = schedFunc.createNode(resource.name)
                            if resource.hasDynamicDelay():
                                resNode.setResourceModel(schedVariant_.getResourceModel(resource.getResourceModelName()))
                            else:
                                resNode.setDelay(resource.delay)
                        else:
                            resNode = schedFunc.createNode(microAction_i.name) # Zero node if microaction does not specify a resource
                        resourceNodes.append(resNode)
                        stageNode.connectNode(resNode) # Connect resource node to previous stage node

                        # Add dynamic egdes to resource node
                        if microAction_i.hasInConnector():
                            connector = microAction_i.getInConnector()
                            resNode.createDynamicInEdge(connector.name, connector.getConnectorModel().name)
                        if microAction_i.hasOutConnector():
                            connector = microAction_i.getOutConnector()
                            resNode.createDynamicOutEdge(connector.name, connector.getConnectorModel().name)

                            
                # Create stage node
                if resourceNodes: # Do not consider this stage, if it is not used (i.e. has no resource-node). TODO: Makes sense for CV32E40P? How about others?
                    stageNode = schedFunc.createNode(stage_i.name)
                    stageNode.createStaticOutEdge(stage_i.name)
                    if not pipeline.isLastStage(stage_i):
                        stageNode.createStaticInEdge(pipeline.getNextStage(stage_i).name)
                    # Connect resource nodes of this stage to stageNode
                    for rn_i in resourceNodes:
                        rn_i.connectNode(stageNode)

            # Set end node
            schedFunc.setEndNode(stageNode)
