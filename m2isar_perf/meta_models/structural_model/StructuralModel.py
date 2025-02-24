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

    def getAllStages(self):
        if self.pipeline is None:
            raise TypeError("Cannot call MetaModel.CorePerfModel.getAllStages before a pipeline has been assigned!")
        return self.pipeline.getAllStages()
        
        #stages = []
        #for st in self.pipeline.stages:
        #    stages.append(st)
        #
        #return stages

    def getAllMicroactions(self):
        return self.pipeline.getAllMicroactions()
        
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
        self.components = [] # Stages and/or sub-pipelines
        self.isParallel = False
        self.blockPipelines = [] # List of pipelines blocked by THIS pipeline
        
        super().__init__()

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
            
    def getFirstStage(self):
        return self.components[0]

    def isLastStage(self, stage_):
        return stage_ == self.components[-1]

    def getLastStage(self):
        return self.components[-1]
    
    def getNextStage(self, stage_):
        retStage = None
        found = False
        for st_i in self.components:
            if stage_ == st_i: # found current stage
                found = True
                continue
            if found == True:
                retStage = st_i
                break
        return retStage
    
class Stage(FrozenBase):

    def __init__(self):
        self.name = ""
        self.paths = [] # List of parallel microactions and/or sub-pipelines in stage
        self.capacity = 0
        self.hasOutputBuffer = False
        
        super().__init__()

    def getUsedMicroactions(self): # TODO: Is this still used somewhere? Replace with getMicroactions?
        return self.microactions

    # Return microactions directly in this stage (not in sub-stages)
    def getMicroactions(self):
        return [p for p in self.paths if type(p) is Microaction]

    # Return all microactions in this stage and all its substages
    def getAllMicroactions(self):
        uActions = self.getMicroactions()
        for path_i in self.paths:
            if type(path_i) is Pipeline:
                uActions.extend(path_i.getAllMicroactions())
        return uActions
                    
    def getAllPathes(self):
        return self.paths
        
class Microaction(FrozenBase):

    def __init__(self):
        self.name = ""
        self.virtualAlias = ""
        self.inConnector = None
        self.resource = None
        self.outConnector = None
         
        super().__init__()

    def hasInConnector(self):
        return (self.inConnector is not None)
        
    def getInConnector(self):
        return self.inConnector

    def hasResource(self):
        return (self.resource is not None)
    
    def getResource(self):
        return self.resource

    def hasOutConnector(self):
        return (self.outConnector is not None)
    
    def getOutConnector(self):
        return self.outConnector

    def assign(self, uA_):
        if type(uA_) is not Microaction:
            raise TypeError("Cannot call Microaction::assign function with input of type %s" % type(uA_))
        if self.name != "":
            raise TypeError("Virtual microaction %s has allready been assigned to %s" %(self.virtualAlias, self.name))

        self.name = uA_.name
        self.inConnector = uA_.inConnector
        self.resource = uA_.resource
        self.outConnector = uA_.outConnector
    
class Resource(FrozenBase):

    def __init__(self):
        self.name = ""
        self.virtualAlias = ""
        self.delay = 0
        self.resourceModel = None
        self.capacity = 0

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
