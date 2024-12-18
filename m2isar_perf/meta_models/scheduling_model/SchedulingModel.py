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

from typing import List, Optional

from meta_models.common.FrozenBase import FrozenBase

class SchedulingModel(FrozenBase):

    def __init__(self):

        # Owned instances
        self.variants:List[Variant] = []

        super().__init__()

    def createVariant(self, name_:str) -> 'Variant':
        variant = Variant(name_)
        self.variants.append(variant)
        return variant

    def getAllVariants(self) -> List['Variant']:
        return self.variants
    
class Variant(FrozenBase):

    def __init__(self, name_:str):
        self.name = name_

        # Owned instances
        self.schedulingFunctions:List[SchedulingFunction] = []
        self.timingVariables:Dict[TimingVariable] = {}
        self.resourceModels:Dict[str,ResourceModel] = {}
        self.connectorModels:Dict[ConnectorModel] = {}

        super().__init__()

    def createResourceModel(self, name_:str, link_:str) -> 'ResourceModel':
        if name_ in self.resourceModels:
            raise RuntimeError(f"ResourceModel {name_} was already created!")
        model = ResourceModel(name_, link_)
        self.resourceModels[name_] = model
        return model
    
    def createConnectorModel(self, name_:str, link_:str) -> 'ConnectorModel':
        if name_ in self.connectorModels:
            raise RuntimeError(f"ConenctorModel {name_} was already created!")
        model = ConnectorModel(name_, link_)
        self.connectorModels[name_] = model
        return model
        
    def createTimingVariable(self, name_:str) -> 'TimingVariable':
        if name_ in self.timingVariables:
            raise RuntimeError(f"TimingVaribale {name_} was already created")
        var = TimingVariable(name_)
        self.timingVariables[name_] = var
        return var

    def createSchedulingFunction(self, name_:str, id_:int) -> 'SchedulingFunction':
        func = SchedulingFunction(name_, id_, self)
        self.schedulingFunctions.append(func)
        return func

    def getResourceModel(self, name_:str) -> Optional['ResourceModel']:
        if name_ not in self.resourceModels:
            raise RuntimeError(f"ResourceModel {name_} does not exist!")
        return self.resourceModels[name_]

    def getConnectorModel(self, name_:str) -> Optional['ConnectorModel']:
        if name_ not in self.connectorModels:
            raise RuntimeError(f"ConnectorModel {name_} does not exist!")
        return self.connectorModels[name_]
    
    def getTimingVariable(self, name_:str) -> Optional['TimingVariable']:
        if name_ not in self.timingVariables:
            raise RuntimeError(f"TimingVariable {name_} does not exist!")
        return self.timingVariables[name_]
    
    def getAllConnectorModels(self) -> List['ConnectorModel']:
        return list(self.connectorModels.values())

    def getAllTimingVariables(self) -> List['TimingVariables']:
        return list(self.timingVariables.values())

    def getAllSchedulingFunctions(self) -> List['SchedulingFunction']:
        return self.schedulingFunctions
    
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
        node = Node(name_, self.parent)
        self.nodes.append(node)
        return node

    def setRootNode(self, node_:Optional['Node']):
        self.rootNode = node_

    def setEndNode(self, node_:Optional['Node']):
        self.endNode = node_

    def getAllNodes(self) -> List['Node']:
        return self.nodes

    #def createStaticInEdge(self, node_:Optional['Node'], variable_:str, depth_:int=1) -> 'StaticEdge':
    #    edge = StaticEdge(depth_)
    #    self.inEdges.append(edge)
    #    node_.setInEdge(edge)
    #    edge.setTimingVariable(self.parent.getTimingVariable(variable_))
    #    return edge
    
class TimingVariable(FrozenBase):

    def __init__(self, name_:str, depth_:int=1):
        self.name = name_
        self.depth = depth_

        super().__init__()

class ExternalModel(FrozenBase):

    # "Virtual class"
    
    def __init__(self, name_:str, link_:str):
        self.name = name_
        self.link = link_
        self.traceValues:List[str] = []

    def addTraceValues(self, trVal_:List[str]):
        self.traceValues.extend(trVal_)
        
class ResourceModel(ExternalModel):

    def __init__(self, name_:str, link_:str):
        
        super().__init__(name_, link_)
        
class ConnectorModel(ExternalModel):

    def __init__(self, name_:str, link_:str):
        
        super().__init__(name_, link_)
        
class Node(FrozenBase):

    def __init__(self, name_:str, parentVariant_:Optional[Variant]):
        self.name = name_
        self.delay:int = 0
        self.dynamicDelay:bool = False
        self.parentVariant = parentVariant_

        
        # Referenced instances
        self.inNodes:List[Optional[Node]] = []
        self.outNodes:List[Optional[Node]] = []
        self.resourceModel:Optional[ResourceModel] = None
        self.inEdges:List[Optional[Edge]] = []
        self.outEdges:List[Optional[Edge]] = []
        
        super().__init__()

    def setResourceModel(self, resM_:Optional['ResourceModel']):
        self.resourceModel = resM_

    def getResourceModel(self) -> Optional['ResourceModel']:
        return self.resourceModel
        
    def setDelay(self, delay_:int):
        self.delay = delay_

    def hasDynamicDelay(self) -> bool:
        return (self.resourceModel is not None)
        
    def connectNode(self, node_:Optional['Node']):
        self.outNodes.append(node_)
        node_.addInNode(self)

    def addInNode(self, node_:Optional['Node']):
        self.inNodes.append(node_)

    def getAllInNodes(self) -> List['Node']:
        return self.inNodes

    #def setInEdge(self, edge_:Optional['Edge']):
    #    self.inEdges.append(edge_)

    def createStaticInEdge(self, variable_:str, depth_:int=1) -> 'StaticEdge':
        #edge = StaticEdge(depth_)
        #self.inEdges.append(edge)
        #edge.setTimingVariable(self.parentVariant.getTimingVariable(variable_))
        #return edge
        edge = self.__createStaticEdge(variable_, depth_)
        self.inEdges.append(edge)
        return edge
        
    def createStaticOutEdge(self, variable_:str) -> 'StaticEdge':
        #edge = StaticEdge()
        #self.outEdges.append(edge)
        #edge.setTimingVariable(self.parentVariant.getTimingVariable(variable_))
        #return edge
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
    
    def getAllInEdges(self) -> List['Edges']:
        return self.inEdges

    def getAllOutEdges(self) -> List['Edges']:
        return self.outEdges

    def __createStaticEdge(self, variable_:str, depth_:int=1) -> 'StaticEdge':
        edge = StaticEdge(depth_)
        edge.setTimingVariable(self.parentVariant.getTimingVariable(variable_))
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
