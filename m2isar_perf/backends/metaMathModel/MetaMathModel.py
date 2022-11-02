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

class MetaMathModel_base:
    __isFrozen = False

    def __setattr__(self, key, value):
        if self.__isFrozen and not hasattr(self, key):
            raise TypeError("Attempting to add new attribute to frozen class %r" %self)
        object.__setattr__(self, key, value)

    def __init__(self):
        self.__isFrozen = True

    def __getFromDict(self, name_, dict_):
        try:
            ret = dict_[name_]
        except KeyError:
            raise TypeError("%s: Cannot get %s from %s. Instance does not exist" %(self.name, name_, dict_))
        return ret
        
class MathModel(MetaMathModel_base):

    def __init__(self):
        self.corePerfModels = []
        
        super().__init__()

    def addCorePerfModel(self, corePerfMod_):
        self.corePerfModels.append(corePerfMod_)

    def getAllCorePerfModels(self):
        return self.corePerfModels
        
class CorePerfModel(MetaMathModel_base):

    def __init__(self, name_):
        self.name = name_
        self.pipeline = None
        self.connectorModels = {}
        self.resourceModels = {}
        self.instructions = {}

        super().__init__()

    # API functions
    
    def addConnectorModel(self, conMod_):
        self.connectorModels[conMod_.name] = conMod_

    def getConnectorModel(self, name_):
        return super()._MetaMathModel_base__getFromDict(name_, self.connectorModels)

    def getAllConnectorModels(self):
        return self.connectorModels.values()
    
    def addResourceModel(self, resMod_):
        self.resourceModels[resMod_.name] = resMod_

    def getResourceModel(self, name_):
        return super()._MetaMathModel_base__getFromDict(name_, self.resourceModels)

    def getAllResourceModels(self):
        return self.resourceModels.values()
    
    def getPipeline(self):
        return self.pipeline
    
    def getStage(self, name_):
        if self.pipeline is None:
            raise TypeError("Cannot call MetaMathModel.CorePerfModel.getStage before a pipeline has been assigned to the model (%s)" % self.name)
        return self.pipeline.getStage(name_)

    def getAllStages(self):
        if self.pipeline is None:
            raise TypeError("Cannot call MetaMathModel.CorePerfModel.getAllStages before a pipeline has been assigned to the model (%s)" % self.name)
        return self.pipeline.getAllStages()

    def addInstruction(self, instr_):
        self.instructions[instr_.name] = instr_
    
    def getInstructionDict(self):
        return self.instructions
    
class Pipeline(MetaMathModel_base):

    def __init__(self, name_):
        self.name = name_
        self.stages = {}

        super().__init__()

    # API Functions
        
    def addStage(self, st_):
        self.stages[st_.name] = st_

    def getStage(self):
        return super()._MetaMathModel_base__getFromDict(name_, self.stages)

    def getAllStages(self):
        return list(self.stages.values())
    
class Stage(MetaMathModel_base):

    def __init__(self, name_):
        self.name = name_

        super().__init__()
        
class ResourceModel(MetaMathModel_base):

    def __init__(self, name_, link_):
        self.name = name_
        self.link = link_
        self.traceValues = [] # TODO: Currently only a list of names, i.e. not pointing to traceValue objects
        
        super().__init__()

class ConnectorModel(MetaMathModel_base):

    def __init__(self, name_, link_):
        self.name = name_
        self.link = link_
        self.traceValues = [] # TODO: Currently only a list of names, i.e. not pointing to traceValue objects

        super().__init__()
        
class Instruction(MetaMathModel_base):

    def __init__(self, name_):
        self.name = name_
        self.timeFunction = None
        self.identifier = -1 # TODO: Does it make more sense to handle instruction groups instead of each instruction individually?

        super().__init__()

    def setTimeFunction(self, timeFunc_):
        self.timeFunction = timeFunc_
        
    def getTimeFunction(self):
        return self.timeFunction
        
class TimeFunction(MetaMathModel_base):

    def __init__(self, endNode_):
        self.endNode = endNode_

        super().__init__()

    def getEndNode(self):
        return self.endNode

    def forAllNodes(self, fuTuple_):
        self.__iterateNodes_recursive(self.endNode, [], fuTuple_)

    def __iterateNodes_recursive(self, node_, coveredNodes_, fuTuple_):

        if node_.getId() not in coveredNodes_:

            # Unpack function tuple
            func, funcDict = fuTuple_
            
            # Call previous node(s)
            if node_.hasMultipleInputs():
                for prev in node_.getPrev():
                    self.__iterateNodes_recursive(prev, coveredNodes_, (func, funcDict))
            else:
                if node_.getPrev() is not None:
                    self.__iterateNodes_recursive(node_.getPrev(), coveredNodes_, (func, funcDict))

            # Execute
            func(node_, funcDict)
            
            # Add node to list of coveredNodes
            coveredNodes_.append(node_.getId())
                    
class Node_base(MetaMathModel_base):

    def __init__(self):
        self.__in = None
        self.__out = [] # The inNode that represents a stage, i.e. the point when all microactions of that state get activated, need multiple outs. No harm in letting all nodes have them?
        self.id = -1
        
        super().__init__()

    def connect(self, inNode_):
        self.__in = inNode_
        inNode_._Node_base__out.append(self)

    def getPrev(self):
        return self.__in

    def setId(self, id_):
        self.id = id_

    def getId(self):
        return self.id

    def getIdStr(self):
        return ("n_" + str(self.id))

    def hasMultipleInputs(self):
        return False

    def hasName(self):
        return False

    def isAddNode(self):
        return False

    def isMaxNode(self):
        return False

    def isInNode(self):
        return False

    def isOutNode(self):
        return False
    
class IONode_base(Node_base):

    def __init__(self, name_, model_):
        self.name = name_
        self.model = model_

        super().__init__()

    def hasName(self):
        return True

    def getModel(self):
        return self.model
    
class MultiInNode_base(Node_base):

    def __init__(self):
        self.__in = []

        super().__init__()

    def connect(self, inNode_):
        self.__in.append(inNode_)
        inNode_._Node_base__out.append(self)

    def getPrev(self):
        return self.__in

    def hasMultipleInputs(self):
        return True
    
class SimpleNode(Node_base):

    def __init__(self):
        super().__init__()

    # This function disconnects the node (self) from following nodes (self.__out)
    # and connects the newNode_ instead.
    # NOTE: Inputs to this node (self) are not reconnected
    def replace(self, newNode_):
        for n in self._Node_base__out:
            if isinstance(n, MultiInNode_base):
                n._MultiInNode_base__in.remove(self)
                n.connect(newNode_)
            else:
                n.connect(newNode_)
                
class InNode(IONode_base):

    def __init__(self, name_, model_):
        super().__init__(name_, model_)

    def connect(self, inNode_):
        raise TypeError("Cannot connect a node to %s (%s) of type InNode" % (self.name, self.id))

    def isInNode(self):
        return True
    
class OutNode(IONode_base):

    def __init__(self, name_, model_):
        super().__init__(name_, model_)

    def isOutNode(self):
        return True
        
class AddNode(Node_base):

    # TODO: Add a name attribute to match with resource?
    
    def __init__(self, delay_=0, model_=None):
        if model_ is not None and type(model_) is not ResourceModel:
            raise TypeError("Cannot create an AddNode. Provided model is not of type ResourceModel but %s" %(type(model_)))
        if delay_!=0 and model_ is not None:
            raise TypeError("Cannot create an AddNode with static (%s) and dynamic (%s) delay" %(delay_, model_.name))
        elif delay_==0 and model_ is None:
            delay_ = 1

        self.delay = delay_
        self.model = model_

        super().__init__()

    def isAddNode(self):
        return True

    def hasModel(self):
        return (self.model is not None)
    
    def getModel(self):
        return self.model

    def getDelay(self):
        return self.delay
        
class MaxNode(MultiInNode_base):

    def __init__(self):
        super().__init__()

    def isMaxNode(self):
        return True
