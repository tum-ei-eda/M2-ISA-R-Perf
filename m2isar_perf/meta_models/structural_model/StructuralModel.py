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

from meta_models.common.FrozenBase import FrozenBase

class StructuralModel(FrozenBase):

    def __init__(self):
        self.variants = []

        super().__init__()

    def getAllVariants(self):
        return self.variants

class Variant(FrozenBase):

    def __init__(self):
        self.name = ""
        self.pipeline = None # TopPipeline
        self.core = ""
        self.connectorModels = []
        self.resourceModels = []
        self.instructions = []

        super().__init__()

    # def getAllStages(self):
    #     if self.pipeline is None:
    #         raise TypeError("Cannot call MetaModel.CorePerfModel.getAllStages before a pipeline has been assigned!")
    #     return self.pipeline.getAllStages()
    #     
    #     #stages = []
    #     #for st in self.pipeline.stages:
    #     #    stages.append(st)
    #     #
    #     #return stages

    # Link stage and pipeline elements
    def resolvePipelineStructure(self):
        # Iterates through all (sub-)stages and (sub-)pipelines, and sets parent component.
        self.pipeline.setParent(None)

        # Double-link blocking and blocked pipelines
        for pipe_i in self.pipeline.getAllSubPipelines():
            for block_i in pipe_i.blockPipelines:
                block_i.blockedByPipelines.append(pipe_i)
                                 
    def getAllMicroactions(self):
        return self.pipeline.getAllMicroactions()

    def getAllStages(self):
        return self.pipeline.getAllStages()
    
    #def getAllMicroactions(self): # TODO: Update or rename
    #    microactions = []
    #    for st in self.getAllStages():
    #        for path_i in st.paths:
    #            microactions.append(path_i)
    #
    #    return microactions
    
    def getAllConnectorModels(self):
        return self.connectorModels
        
    def getAllResourceModels(self):
        return self.resourceModels
        
    def getAllInstructions(self):
        return self.instructions

    def getPipeline(self):
        return self.pipeline
    
    def getPipelineUsageDict(self):
        pipelineUsageDict = {}
        
        for instr in self.instructions:
            pipelineUsage = {}
   
            for st in self.getAllStages():
                usedMicroactions = []
                for uA in st.microactions:
                    if uA in instr.getUsedMicroactions():
                        usedMicroactions.append(uA)

                pipelineUsage[st.name] = usedMicroactions

            pipelineUsageDict[instr.name] = pipelineUsage
        return pipelineUsageDict                

    def getAllUsedTraceValues(self):
        usedTrVals = []

        for conM_i in self.getAllConnectorModels():
            for trVal_i in conM_i.getTraceValues():
                if trVal_i not in usedTrVals:
                    usedTrVals.append(trVal_i)

        for resM_i in self.getAllResourceModels():
            for trVal_i in resM_i.getTraceValues():
                if trVal_i not in usedTrVals:
                    usedTrVals.append(trVal_i)

        return usedTrVals
    
class Pipeline(FrozenBase):

    def __init__(self):
        self.name = ""
        self.parent = None
        self.components = [] # Stages and/or sub-pipelines
        self.isParallel = False
        self.blockPipelines = [] # List of pipelines blocked by THIS pipeline
        self.blockedByPipelines = [] # List of pipelines which are blocking THIS pipeline
        
        super().__init__()

    def setParent(self, parent_):
        self.parent = parent_
        for comp_i in self.components:
            comp_i.setParent(self)

    def setBlockedByPipeline(self, pipe_):
        self.blockedByPipelines.append(pipe_)
        for comp_i in self.components:
            if type(comp_i) is Pipeline:
                comp_i.setBlockedByPipeline(pipe_)
            
    def isTopPipeline(self):
        return self.parent is None
        
   # # TODO: Is this used anywhere? Delete?
   # def getAllStages(self):
   #     stages = []
   #     for comp_i in self.components:
   #         if type(comp_i) is Pipeline:
   #             stages.extend(comp_i.getAllStages())
   #         elif type(comp_i) is Stage:
   #             stages.append(comp_i)
   #     return stages

    # Return all microactions located in (sub-) stages of this pipeline
    def getAllMicroactions(self):
        uActions = []
        for comp_i in self.components:
            uActions.extend(comp_i.getAllMicroactions())
        return uActions

    # Return all (sub-) stages associated with this pipeline
    def getAllStages(self):
        stages = []
        for comp_i in self.components:
            if type(comp_i) is Stage:
                stages.append(comp_i)
                stages.extend(comp_i.getAllSubStages())
            elif type(comp_i) is Pipeline:
                stages.extend(comp_i.getAllStages())
        return stages

    # Returns all sub-pipelines (and sub-sub-pipelines...) associated with this pipeline (Does not return itself)
    def getAllSubPipelines(self):
        pipes = []
        for comp_i in self.components:
            if type(comp_i) is Pipeline:
                pipes.append(comp_i)
                pipes.extend(comp_i.getAllSubPipelines())
            elif type(comp_i) is Stage:
                pipes.extend(comp_i.getAllPipelines())
        return pipes
    
    # TODO: Outdated?            
    # def getFirstStage(self):
    #     return self.components[0]

    # TODO: Outdated?
    # def isLastStage(self, stage_):
    #     return stage_ == self.components[-1]

    # TODO: Outdated?
    # def getLastStage(self):
    #     return self.components[-1]

    
    # Returns first stages of this pipeline (Only 1st-level sub-stages, i.e. does not iterrate into sub-stages)
    def getFirstStages(self):
        stages = []
        if self.isParallel:
            for comp_i in self.components:
                stages.extend(self.__getFirstStagesFromComponent(comp_i))
        else: # sequential
            stages.extend(self.__getFirstStagesFromComponent(self.components[0]))
        return stages

    # Returns last stages of this pipeline (Only 1st-level sub-stages, i.e. does not iterrate into sub-stages)
    def getLastStages(self):
        stages = []
        if self.isParallel:
            for comp_i in self.components:
                stages.extend(self.__getLastStagesFromComponent(comp_i))
        else:
            comp = self.components[-1]
            stages.extend(self.__getLastStagesFromComponent(comp))
        return stages
    
    # def getNextStage(self, stage_):
    #     retStage = None
    #     found = False
    #     for st_i in self.components:
    #         if stage_ == st_i: # found current stage
    #             found = True
    #             continue
    #         if found == True:
    #             retStage = st_i
    #             break
    #     return retStage

    def getNextStages(self, comp_):

        # Sequential
        if not self.isParallel:

            # Search for next component
            nxComp = None
            found = False
            for comp_i in self.components:
                if comp_i == comp_:
                    found = True
                    continue
                if found:
                    nxComp = comp_i
                    break

            # There is a next sequential component in this pipeline
            if nxComp is not None:
                if type(nxComp) is Stage:
                    return [nxComp]
                elif type(nxComp) is Pipeline:
                    return nxComp.getFirstStages()

        # Parallel or no next sequential component
        if self.isTopPipeline():
            return []

        if type(self.parent) is Stage:
            return []
        elif type(self.parent) is Pipeline:
            return self.parent.getNextStages(self)
            
    def __getLastStagesFromComponent(self, comp_):
        if type(comp_) is Pipeline:
            return comp_.getLastStages()
        elif type(comp_) is Stage:
            return [comp_]
        return None # Should never happen

    def __getFirstStagesFromComponent(self, comp_):
        if type(comp_) is Pipeline:
            return comp_.getFirstStages()
        elif type(comp_) is Stage:
            return [comp_]
        return None # Should never happen
    
class Stage(FrozenBase):

    def __init__(self):
        self.name = ""
        self.parent = None
        self.paths = [] # List of parallel microactions and/or sub-pipelines in stage
        self.capacity = 0
        self.hasOutputBuffer = False
        
        super().__init__()

    def setParent(self, parent_):
        self.parent = parent_
        for pipe_i in self.getPipelines():
            pipe_i.setParent(self)

    # Gets parent stage. Returns None if stage is not a sub-stage
    def getParentStage(self):
        parentStage = None
        parent = self.parent
        while not parent.isTopPipeline():
            parent = parent.parent
            if type(parent) is Stage:
                parentStage = parent
                break
        return parentStage

    def isPrimaryStage(self):
        return (self.getParentStage() is None)
    
    def isSubStage(self):
        return not self.isPrimaryStage()
            
    #def getUsedMicroactions(self): # TODO: Is this still used somewhere? Replace with getMicroactions?
    #    return self.microactions

    # Returns microactions directly in this stage (not in sub-stages)
    def getMicroactions(self):
        return [p for p in self.paths if type(p) is Microaction]

    # Returns pipelines directly in this stage (no (sub-)sub-pipelines).
    def getPipelines(self):
        return [p for p in self.paths if type(p) is Pipeline]
    
    # Return all microactions in this stage and all its substages
    def getAllMicroactions(self):
        uActions = self.getMicroactions()
        for pipe_i in self.getPipelines():
            uActions.extend(pipe_i.getAllMicroactions())
        return uActions
                    
    def getPaths(self):
        return self.paths

    # Return all (sub-) pipelines associated with this pipeline
    def getAllPipelines(self):
        pipes = []
        for path_i in self.paths:
            if type(path_i) is Pipeline:
                pipes.append(path_i)
                pipes.extend(path_i.getAllSubPipelines())
        return pipes
    
    # Recursively returns all sub-stages (and sub-sub-...stages) of this stage (Does not return itself)
    def getAllSubStages(self):
        subStages = []
        for pipe_i in self.getPipelines():
            subStages.extend(pipe_i.getAllStages())
        return subStages

    # Return last sub-stages for each of this stages paths (Non-recursively, i.e. only returns 1st-level sub-stages)
    def getLastSubStages(self):
        stages = []
        for pipe_i in self.getPipelines():
            stages.extend(pipe_i.getLastStages())
        return stages

    # Return first sub-stages for each of this stages paths (Non-recursively, i.e. only returns 1st-level sub-stages)
    def getFirstSubStages(self):
        stages = []
        for pipe_i in self.getPipelines():
            stages.extend(pipe_i.getFirstStages())
        return stages
    
    # Returns next stage of the same level
    # Returns [] if last sub-stage of a sub-pipeline
    # Returns [] if last stage of the top-pipeline
    def getNextStages(self):
        return self.parent.getNextStages(self)

    # Returns True if this stage (or any of its substages) contains a microaction mapped to instr_
    def isUsedBy(self, instr_):
        uActions = self.getAllMicroactions()
        for uA_i in instr_.getUsedMicroactions():
            if uA_i in uActions:
                return True
        return False

    def getBlockingStages(self):
        blockingStages = []
        if self in self.parent.getFirstStages():
            for blockPipe_i in self.parent.blockedByPipelines:
                blockingStages.extend(blockPipe_i.getLastStages())
        return blockingStages
    
class Microaction(FrozenBase):

    def __init__(self):
        self.name = ""
        self.virtualAlias = ""
        self.inConnectors = []
        self.resources = []
        self.outConnectors = []
         
        super().__init__()

    # TODO: Outdated
    # def hasInConnector(self):
    #     return (self.inConnector is not None)
        
    def getInConnectors(self):
        return self.inConnectors

    def hasResources(self):
        return bool(self.resources)
    
    def getResources(self):
        return self.resources

    # TODO: Outdated
    # def hasOutConnector(self):
    #     return (self.outConnector is not None)
    
    def getOutConnectors(self):
        return self.outConnectors

    def assign(self, uA_):
        if type(uA_) is not Microaction:
            raise TypeError("Cannot call Microaction::assign function with input of type %s" % type(uA_))
        if self.name != "":
            raise TypeError("Virtual microaction %s has allready been assigned to %s" %(self.virtualAlias, self.name))

        self.name = uA_.name
        self.inConnectors = uA_.inConnectors
        self.resources = uA_.resources
        self.outConnectors = uA_.outConnectors
    
class Resource(FrozenBase):

    def __init__(self):
        self.name = ""
        self.virtualAlias = ""
        self.delay = 0
        self.resourceModel = None

        super().__init__()

    def assign(self, res_):
        if type(res_) is not Resource:
            raise TypeError("Cannot call Resource::assign function with input of type %s" % type(res_))
        if self.name != "":
            raise TypeError("Virtual resource %s has allready been assigned to %s" %(self.virtualAlias, self.name))

        self.name = res_.name
        self.delay = res_.delay
        self.resourceModel = res_.resourceModel

    def hasDynamicDelay(self):
        return (self.resourceModel is not None)

    def getResourceModelName(self):
        return self.resourceModel.name
        
class Connector(FrozenBase):

    def __init__(self):
        self.name = ""
        self.connectorModel = None
        self.connectorType = ""
        
        super().__init__()

    def getConnectorModel(self):
        return self.connectorModel
        
class ResourceModel(FrozenBase):

    def __init__(self):
        self.name = ""
        self.link = ""
        self.traceValues = []

        super().__init__()

    def getTraceValues(self):
        return self.traceValues
        
class ConnectorModel(FrozenBase):

    def __init__(self):
        self.name = ""
        self.link = ""
        self.inConnectors = []
        self.outConnectors = []
        self.traceValues = []

        super().__init__()

    def getTraceValues(self):
        return self.traceValues
        
class TraceValue(FrozenBase):

    def __init__(self):
        self.name = ""

        super().__init__()

class Instruction(FrozenBase):

    def __init__(self):
        self.name = ""
        self.identifier = -1 # TODO: Does it make more sense to handle instruction groups instead of each instruction individually?
        self.group = []
        self.microactions = []
        self.traceValueAssignments = []
                
        super().__init__()

    def getUsedMicroactions(self):
        return self.microactions

    def getTraceValueAssignments(self):
        return self.traceValueAssignments

    def addGroupName(self, name_):
        self.group.append(name_)
    
class TraceValueAssignment(FrozenBase):

    def __init__(self):
        self.traceValue = None
        self.description = ""

        super().__init__()

    def getTraceValue(self):
        return self.traceValue

    def getDescription(self):
        return self.description
