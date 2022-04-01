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

class Instance:
     
    def __init__(self, name_, virtual_=False):
        self.name = name_
        self.virtual = virtual_

    def isVirtual(self):
        return self.virtual

    def replaceVirtual(self, rep_):
        if self.isVirtual:
            self.__dict__ = rep_.__dict__.copy()

class InstanceListIterator:

    def __init__(self, parent_):
        self.index = 0
        self.parent = parent_
        
    def __next__(self):
        if self.index < len(self.parent.instances):
            result = self.parent.instances[self.index]
            self.index += 1
            return result
        raise StopIteration
        
class InstanceList:

    globalNameList=[]
    
    def __init__(self):
        self.instances = []
        
    def __iter__(self):
        return InstanceListIterator(self)
        
    def add(self, inst):
        if(inst.name in InstanceList.globalNameList):
            print("ERROR: Cannot add instance %s. Name already assigned." % inst.name)
        else:
            self.instances.append(inst)
            InstanceList.globalNameList.append(inst.name)

    def exists(self, name_):
        for inst in self.instances:
            if inst.name == name_:
                return True
        return False
    
    def get(self, name_):
        for inst in self.instances:
            if inst.name == name_:
                return inst
        return UndefinedInstance(name_)

    def getList(self): # TODO: Remove
        return self.instances
    
    def delete(self, name_):
        inst = self.get(name_)
        if inst is not None:
            self.instances.remove(inst)
            del inst
        
class ConnectorInstance(Instance):
    pass

class TraceValueInstance(Instance):
    pass

class ResourceModelInstance(Instance):

    def __init__(self, name_):
        super().__init__(name_)
        self.link = ""
        self.traceVals = []

class ConnectorModelInstance(Instance):

    def __init__(self, name_):
        super().__init__(name_)
        self.link = ""
        self.traceVals = []
        self.inCons = []
        self.outCons = []
        
class ResourceInstance(Instance):
    
    def __init__(self, name_, virtual_=False):
        super().__init__(name_, virtual_)
        self.dynamic_delay = False
        self.delay = 0
        self.model = None
         
class MicroactionInstance(Instance):
    
    def __init__(self, name_, virtual_=False):
        super().__init__(name_, virtual_)
        self.inConnector = None
        self.resource = None
        self.outConnector = None

class StageInstance(Instance):
    
    def __init__(self, name_):
        super().__init__(name_)
        self.microactions = []

class PipelineInstance(Instance):
    
    def __init__(self, name_):
        super().__init__(name_)
        self.stages = []

class CorePerfModelInstance(Instance):

    def __init__(self, name_):
        super().__init__(name_)
        self.pipeline = None
        self.connectorModels = []
        self.resourceAssignments = []
        self.microactionAssignments = []

class InstrGroupInstance(Instance):

    def __init__(self, name_):
        super().__init__(name_)
        self.instructions = []

class MicroactionMappingInstance(Instance):

    def __init__(self, name_):
        super().__init__(name_)
        self.microactions = []
        self.singleInstr = True
        self.instr = None
        self.instrGr = None

class InstructionInstance(Instance):

    def __init__(self, name_):
        super().__init__(name_)
        self.microactions = []

class UndefinedInstance(Instance):
    pass
