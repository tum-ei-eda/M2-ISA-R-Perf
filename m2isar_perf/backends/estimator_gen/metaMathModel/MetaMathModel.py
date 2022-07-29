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
        
    def addResourceModel(self, resMod_):
        self.resourceModels[resMod_.name] = resMod_

    def getResourceModel(self, name_):
        return super()._MetaMathModel_base__getFromDict(name_, self.resourceModels)

    def getStage(self, name_):
        if self.pipeline is None:
            raise TypeError("Cannot call MetaMathModel.CorePerfModel.getStage before a pipeline has been assigned to the model (%s)" % self.name)
        return self.pipeline.getStage(name_)

    def getAllStages(self):
        if self.pipeline is None:
            raise TypeError("Cannot call MetaMathModel.CorePerfModel.getAllStages before a pipeline has been assigned to the model (%s)" % self.name)
        return self.pipeline.getAllStages()
        
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
        self.traceValues = [] # TODO: Required? Currently not implemented, i.e not copied from frontend
        
        super().__init__()

class ConnectorModel(MetaMathModel_base):

    def __init__(self, name_, link_):
        self.name = name_
        self.link = link_
        self.traceValues = [] # TODO: Required? Currently not implemented, i.e not copied from frontend

        super().__init__()
        
class Instruction(MetaMathModel_base):

    def __init__(self, name_):
        self.name = name_
        self.timeFunction = None

        super().__init__()

class TimeFunction(MetaMathModel_base):

    def __init__(self, endNode_):
        self.endNode = endNode_

        super().__init__()
        
# TODO: What goes here? For the moment, develop meta model buttom up

class Node_base(MetaMathModel_base):

    def __init__(self):
        self.__in = None
        self.__out = [] # The inNode that represents a stage, i.e. the point when all microactions of that state get activated, need multiple outs. No harm in letting all nodes have them?
        
        super().__init__()

    def connect(self, inNode_):
        self.__in = inNode_
        inNode_._Node_base__out.append(self)

    def getPrev(self):
        return self.__in

class MultiInNode_base(Node_base):

    def __init__(self):
        self.__in = []

        super().__init__()

    def connect(self, inNode_):
        self.__in.append(inNode_)
        inNode_._Node_base__out.append(self)

    def getPrev(self):
        return self.__in
    
class SimpleNode(Node_base):

    def __init__(self, id_):
        self.id = id_

        super().__init__()

    # TODO: EVER USED? REMOVE?
    # This function disconnects the node (self) from following nodes (self.__out)
    # and connects the newNode_ instead.
    # Note: Inputs to this node (self) are not reconnected
    def replace(self, newNode_):
        for n in self._Node_base__out:
            if isinstance(n, MultiInNode_base):
                n._MultiInNode_base__in.remove(self)
                n.connect(newNode_)
            else:
                n.connect(newNode_)
        
class InNode(SimpleNode):

    def __init__(self, name_, model_, id_):
        self.name = name_
        self.model = model_

        super().__init__(id_)

    def connect(self, inNode_):
        raise TypeError("Cannot connect a node to %s (%s) of type InNode" % (self.name, self.id))
        
class OutNode(SimpleNode):

    def __init__(self, name_, model_, id_):
        self.name = name_
        self.model = model_

        super().__init__(id_)
        
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

class MaxNode(MultiInNode_base):

    def __init__(self):
        super().__init__()
