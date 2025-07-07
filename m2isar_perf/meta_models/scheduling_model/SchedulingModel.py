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

from typing import List, Optional, Union

from meta_models.common.FrozenBase import FrozenBase

class SchedulingModel(FrozenBase):

    def __init__(self, name_:str):
        self.name = name_
        
        # Owned instances
        self.variants:List[Variant] = []

        super().__init__()

    def createVariant(self, name_:str) -> 'Variant':
        variant = Variant(name_, self)
        self.variants.append(variant)
        return variant

    def getAllVariants(self) -> List['Variant']:
        return self.variants
    
class Variant(FrozenBase):

    def __init__(self, name_:str, parent_:Optional['SchedulingModel']):
        self.name = name_
        self.parent = parent_
        
        # Owned instances
        self.schedulingFunctions:List[SchedulingFunction] = []
        self.timingVariables:Dict[TimingVariable] = {}
        self.externalModels:Dict[str,ExternalModel] = {}
        
        super().__init__()

    def createExternalModel(self, name_:str, link_:str, isConModel_:bool, isResModel_:bool, isConfigurable_:bool) -> 'ExternalModel':
        if name_ in self.externalModels:
            raise RuntimeError(f"ExternalModel {name_} was already created!")
        model = ExternalModel(name_, link_, isConModel_, isResModel_, isConfigurable_)
        self.externalModels[name_] = model
        return model
        
    def createTimingVariable(self, name_:str, numElements_:int=1, traced_:bool=False) -> 'TimingVariable':
        if name_ in self.timingVariables:
            raise RuntimeError(f"TimingVaribale {name_} was already created")
        var = TimingVariable(name_, numElements_, traced_)
        self.timingVariables[name_] = var
        return var
        
    def createSchedulingFunction(self, name_:str, id_:int) -> 'SchedulingFunction':
        func = SchedulingFunction(name_, id_, self)
        self.schedulingFunctions.append(func)
        return func

    def getResourceModel(self, name_:str) -> Optional['ExternalModel']:
        resModel = self.__getExternalModel(name_)
        if not resModel.isResourceModel:
            raise RuntimeError(f"{resModel.name} is not a resource model")
        return resModel

    def getConnectorModel(self, name_:str) -> Optional['ExternalModel']:
        conModel = self.__getExternalModel(name_)
        if not conModel.isConnectorModel:
            raise RuntimeError(f"{conModel.name} is not a connector model")
        return conModel
    
    def getTimingVariable(self, name_:str) -> Optional['TimingVariable']:
        if name_ in self.timingVariables:
            return self.timingVariables[name_]
        raise RuntimeError(f"TimingVariable {name_} does not exist!")

    def getAllExternalModels(self) -> List['ExternalModels']:
        return list(self.externalModels.values())
    
    def getAllResourceModels(self) -> List['ExternalModels']:
        return [x for x in self.externalModels.values() if x.isResourceModel]
        
    def getAllConnectorModels(self) -> List['ExternalModels']:
        return [x for x in self.externalModels.values() if x.isConnectorModel]
    
    def getAllTimingVariables(self) -> List['TimingVariables']:
        return list(self.timingVariables.values())

    def getAllMultiElementTimingVariables(self) -> List['TimingVariables']:
        ret = []
        for tVar_i in self.timingVariables.values():
            if tVar_i.hasMultiElements():
                ret.append(tVar_i)
        return ret

    def getAllSingleElementTimingVariables(self) -> List['TimingVariables']:
        ret = []
        for tVar_i in self.timingVariables.values():
            if not tVar_i.hasMultiElements():
                ret.append(tVar_i)
        return ret

    def getAllTracedTimingVariables(self) -> List['TimingVariables']:
        ret = []
        for tVar_i in self.getAllTimingVariables():
            if tVar_i.isTraced():
                ret.append(tVar_i)
        return ret
    
    def getAllSchedulingFunctions(self) -> List['SchedulingFunction']:
        return self.schedulingFunctions

    def getParentModel(self) -> Optional['SchedulingModel']:
        return self.parent
    
    def __getExternalModel(self, name_) -> Optional['ExternalModel']:
        if name_ not in self.externalModels:
            raise RuntimeError(f"ExternalModel {name_} does not exist!")
        return self.externalModels[name_]
    
class SchedulingFunction(FrozenBase):

    def __init__(self, name_:str, id_:int, parent_:Optional[Variant]):
        self.name = name_
        self.identifier = id_
        self.parent = parent_
        
        # Owned instances
        self.nodes:List[Node] = []
        self.inEdges:List[Edge] = []
        self.outEdges:List[Edge] = []

        # Referenced instances
        self.rootNode:Optional[Node] = None
        self.endNode:Optional[Node] = None

        super().__init__()

    def createNode(self, name_:str) -> 'Node':
        node = Node(name_, self.parent, self)
        self.nodes.append(node)
        return node

    def deleteNode(self, node_:Optional['Node']):
        self.nodes.remove(node_)

    def setRootNode(self, node_:Optional['Node']):
        self.rootNode = node_

    def setEndNode(self, node_:Optional['Node']):
        self.endNode = node_

    def getRootNode(self) -> Optional['Node']:
        return self.rootNode

    def getAllNodes(self) -> List['Node']:
        return self.nodes

class TimingVariable(FrozenBase):

    def __init__(self, name_:str, numElements_:int=1, traced_:bool=False):
        self.name = name_
        self.numElements = numElements_
        self.traced = traced_ # Observable in timing trace
        
        # TODO: Are these members still required somewhere?
        self.lastStage = False # TODO: How to handle this for V-form pipelines? Replace by isEndStage?
        self.isEndStage = False
        
        super().__init__()

    def hasMultiElements(self) -> bool:
        return (self.numElements > 1)

    def getNumElements(self) -> int:
        return self.numElements

    def isTraced(self) -> bool:
        return self.traced
    
    # TODO: Is this still required somewhere?
    def setEndStage(self):
        self.isEndStage = True
        
class ExternalModel(FrozenBase):

    def __init__(self, name_:str, link_:str, isConModel_:bool, isResModel_:bool, isConfigurable_:bool):
        self.name = name_
        self.link = link_
        self.traceValues:List[str] = []

        self.isConnectorModel = isConModel_
        self.isResourceModel = isResModel_
        self.isConfig = isConfigurable_

    def addTraceValues(self, trVal_:List[str]):
        self.traceValues.extend(trVal_)

    def getAllTraceValues(self) -> List[str]:
        return self.traceValues
        
    def isConfigurable(self) -> bool:
        return self.isConfig

class ResourceModel(ExternalModel):

    def __init__(self, name_:str, link_:str):
        
        super().__init__(name_, link_)
        
class ConnectorModel(ExternalModel):

    def __init__(self, name_:str, link_:str):
        
        super().__init__(name_, link_)
        
class Node(FrozenBase):

    def __init__(self, name_:str, parentVariant_:Optional[Variant], parent_:Optional[SchedulingFunction]):
        self.name = name_
        self.delay:int = 0
        self.parentVariant = parentVariant_
        self.parentSchedulingFunction = parent_
        
        # Referenced instances
        self.inNodes:List[Optional[Node]] = []
        self.outNodes:List[Optional[Node]] = []
        self.resourceModel:Optional[ResourceModel] = None
        self.inEdges:List[Optional[Edge]] = []
        self.outEdges:List[Optional[Edge]] = []
        
        super().__init__()

    def linkResourceModel(self, resM_:str):
        self.resourceModel = self.parentVariant.getResourceModel(resM_)
    
    def getResourceModel(self) -> Optional['ResourceModel']:
        return self.resourceModel
        
    def setDelay(self, delay_:int):
        self.delay = delay_

    def getDelay(self) -> int:
        return self.delay
        
    def hasDynamicDelay(self) -> bool:
        return (self.resourceModel is not None)

    def hasZeroDelay(self) -> bool:
        return ((self.delay == 0) and (not self.hasDynamicDelay()))
    
    def connectNode(self, node_:Optional['Node']):
        self.outNodes.append(node_)
        node_.addInNode(self)

    def disconnectNode(self, node_:Optional['Node']):
        self.outNodes.remove(node_)
        node_.removeInNode(self)
        
    def mergeNode(self, node_:Optional['Node']):

        # Check if merge is legal
        if self.parentSchedulingFunction is not node_.parentSchedulingFunction:
            raise RuntimeError(f"Trying to merge two nodes ({self.name, node_.name}) belonging to different SchedulingFunctions.")
        if self.parentVariant is not node_.parentVariant:
            raise RuntimeError(f"Trying to merge two nodes ({self.name, node_.name}) belonging to different Variants.")

        # Connect merging node (self) to in- and out-nodes of merged node (node_)
        # Ignore if in- or out-node is merging node (self)
        for in_i in node_.getAllInNodes():
            if not in_i is self:
                in_i.connectNode(self)
        for out_i in node_.getAllOutNodes():
            if not out_i is self:
                self.connectNode(out_i)

        # Copy in- and out-edges from merged node (node_)
        self.inEdges.extend(node_.getAllInEdges())
        self.outEdges.extend(node_.getAllOutEdges())
            
        # Copy resourceModel or delay from merged node ()
        if (self.resourceModel is not None) and (node_.resourceModel is not None):
            raise RuntimeError(f"Trying to merge two nodes ({self.name, node_.name}) with own ResourceModels. Unspecified behavior.")
        elif node_.resourceModel is not None:
            self.resourceModel = node_.resourceModel

        if (self.delay != 0) and (node_.delay != 0):
            raise RuntimeError(f"Trying to merge two nodes ({self.name, node_.name}) with own static delays. Unspecified behavior.")
        elif node_.delay != 0:
            self.delay = node_.delay

        # Delete merged node (node_)
        node_.delete()
            
    def delete(self):
        # Disconnect all in- and out-nodes
        for in_i in self.getAllInNodes():
            in_i.disconnectNode(self)
        for out_i in self.getAllOutNodes():
            self.disconnectNode(out_i)

        # Remove from parent SchedFunc, and delete object
        self.parentSchedulingFunction.deleteNode(self)
        del self
            
    def addInNode(self, node_:Optional['Node']):
        self.inNodes.append(node_)

    def removeInNode(self, node_:Optional['Node']):
        self.inNodes.remove(node_)
        
    def getAllInNodes(self) -> List['Node']:
        return self.inNodes

    def getAllOutNodes(self) -> List['Node']:
        return self.outNodes

    def createStaticInEdge(self, variable_:str, depth_:int=1) -> 'StaticEdge':
        edge = self.__createStaticEdge(variable_, depth_)
        self.inEdges.append(edge)
        return edge
        
    def createStaticOutEdge(self, variable_:str) -> 'StaticEdge':
        edge = self.__createStaticEdge(variable_)
        self.outEdges.append(edge)
        return edge
        
    def createDynamicInEdge(self, name_:str, model_:str) -> 'DynamicEdge':
        edge = self.__createDynamicEdge(name_, model_)
        self.inEdges.append(edge)
        return edge
        
    def createDynamicOutEdge(self, name_:str, model_:str) -> 'DynamicEdge':
        edge = self.__createDynamicEdge(name_, model_)
        self.outEdges.append(edge)
        return edge
    
    def getAllInEdges(self) -> List['Edge']:
        return self.inEdges

    def getAllOutEdges(self) -> List['Edge']:
        return self.outEdges

    def getAllInElements(self) -> List[Union['Node', 'Edge']]:
        retList = [x for x in self.getAllInNodes()]
        retList.extend(self.getAllInEdges())
        return retList

    def hasSingleInElement(self) -> bool:
        return (len(self.getAllInElements()) == 1)

    def hasMultipleInElements(self) -> bool:
        return (len(self.getAllInElements()) > 1)
    
    def __createStaticEdge(self, variable_:str, depth_:int=1) -> 'StaticEdge':
        edge = StaticEdge(depth_)
        tVar = self.parentVariant.getTimingVariable(variable_)
        if depth_ > tVar.numElements:
            raise RuntimeError(f"Depth ({depth_}) of StaticEdge to TimingVariable {variable_} exceeds depth of that TimingVariable ({tVar.numElements})")
        edge.setTimingVariable(tVar)
        return edge
        
    def __createDynamicEdge(self, name_:str, model_:str) -> 'DynamicEdge':
        edge = DynamicEdge(name_)
        edge.setConnectorModel(self.parentVariant.getConnectorModel(model_))
        return edge
    
class Edge(FrozenBase):

    # "Virtual class"
    
    def __init__(self, dynamic_):
        self.dynamic = dynamic_
        
        super().__init__()

    def isDynamic(self) -> bool:
        return self.dynamic
        
class StaticEdge(Edge):

    def __init__(self, depth_:int=1):
        self.depth = depth_

        # Referenced instances
        self.timingVariable:Optional[TimingVariable] = None
        
        super().__init__(False)

    def setTimingVariable(self, var_:Optional[TimingVariable]):
        self.timingVariable = var_

    def getTimingVariable(self) -> Optional[TimingVariable]:
        return self.timingVariable

        
class DynamicEdge(Edge):

    def __init__(self, name_:str):
        self.name = name_

        # Referenced instances
        self.connectorModel:Optional[ConnectorModel] = None
        
        super().__init__(True)

    def setConnectorModel(self, model_:Optional[ConnectorModel]):
        self.connectorModel = model_

    def getConnectorModel(self) -> Optional[ConnectorModel]:
        return self.connectorModel
