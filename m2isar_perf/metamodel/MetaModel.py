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

class MetaModel_base:
    __isFrozen = False

    def __setattr__(self, key, value):
        if self.__isFrozen and not hasattr(self, key):
            raise TypeError("Attempting to add new attribute to frozen class %r" %self)
        object.__setattr__(self, key, value)

    def __init__(self):
        self.__isFrozen = True

class TopModel(MetaModel_base):

    def __init__(self):
        self.corePerfModels = []

        super().__init__()
        
class CorePerfModel(MetaModel_base):

    def __init__(self):
        self.name = ""
        self.pipeline = None
        self.resourceAssignments = [] #TODO: Part of meta-model? No longer needed after Builder?
        self.microactionAssignments = [] #TODO: Part of meta-model? No longer needed after Builder?
        self.connectorModels = []
        self.resourceModels = []
        self.instructions = []

        super().__init__()

    def getAllStages(self):

        if self.pipeline is None:
            raise TypeError("Cannot call MetaModel.CorePerfModel.getAllStages before a pipeline has been assigned!")

        stages = []
        for st in self.pipeline.stages:
            stages.append(st)

        return stages

    def getAllMicroactions(self):

        microactions = []
        for st in self.getAllStages():
            for uA in st.microactions:
                microactions.append(uA)

        return microactions

    def getAllConnectorModels(self):
        return self.connectorModels
        
    def getAllResourceModels(self):
        return self.resourceModels
        
    def getAllInstructions(self):
        return self.instructions
    
    def getPipelineUsageDict(self):
        pipelineUsageDict = {}
        
        for instr in self.instructions:
            pipelineUsage = {}
   
            for st in self.getAllStages():
                usedMicroactions = []
                for uA in st.microactions:
                    if uA in instr.microactions:
                        usedMicroactions.append(uA)

                pipelineUsage[st.name] = usedMicroactions

            pipelineUsageDict[instr.name] = pipelineUsage
        return pipelineUsageDict                
        
class Pipeline(MetaModel_base):

    def __init__(self):
        self.name = ""
        self.stages = []

        super().__init__()
        
class Stage(MetaModel_base):

    def __init__(self):
        self.name = ""
        self.microactions = []

        super().__init__()
        
class Microaction(MetaModel_base):

    def __init__(self):
        self.name = ""
        self.virtualAlias = ""
        self.inConnector = None
        self.resource = None
        self.outConnector = None
         
        super().__init__()

class Resource(MetaModel_base):

    def __init__(self):
        self.name = ""
        self.virtualAlias = ""
        self.delay = 0
        self.resourceModel = None

        super().__init__()
        
class Connector(MetaModel_base):

    def __init__(self):
        self.name = ""
        self.connectorModel = None
        self.connectorType = ""

        super().__init__()
        
class ResourceModel(MetaModel_base):

    def __init__(self):
        self.name = ""
        self.link = ""
        self.traceValues = []

        super().__init__()
        
class ConnectorModel(MetaModel_base):

    def __init__(self):
        self.name = ""
        self.link = ""
        self.inConnectors = []
        self.outConnectors = []
        self.traceValues = []

        super().__init__()
        
# TODO: What is the purpose of this class!?
class TraceValue(MetaModel_base):

    def __init__(self):
        self.name = ""

        super().__init__()

class Instruction(MetaModel_base):

    def __init__(self):
        self.name = ""
        self.group = ""
        self.microactions = []
        self.traceValueAssignments = []
        
        super().__init__()
