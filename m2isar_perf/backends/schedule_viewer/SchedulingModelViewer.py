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

import graphviz

class SchedulingModelViewer:

    def __init__(self):
        pass

    def execute(self, model_, outDir_):

        print()
        print("-- BACKEND: SCHEDULE_VIEWER --")

        
        for var_i in model_.getAllVariants():
                
            for func_i in var_i.getAllSchedulingFunctions():
                if func_i.name == 'div':
                    
                    dotGraph = graphviz.Digraph(comment=func_i.name)
                    dotGraph.attr(rankdir='TB')

                    # Make (in-)nodes for timing variables and connector models
                    with dotGraph.subgraph() as top:
                        top.attr(rank='min')
                        tVar_prev = None
                        for tVar_i in var_i.getAllTimingVariables():
                            top.node(self.__timingVariableIn(tVar_i.name), label=tVar_i.name, shape='box')
                            # Enforce representation of tVar nodes in order?
                            if tVar_prev is not None:
                                top.edge(self.__timingVariableIn(tVar_prev.name), self.__timingVariableIn(tVar_i.name), style='invis') 
                            tVar_prev = tVar_i

                        # TODO: Show all connector models, or just the onces used by this scheduling function? 
                        for conModel_i in var_i.getAllConnectorModels():
                            top.node(self.__connectorModelIn(conModel_i.name), label=conModel_i.name, shape='box')

                    # Make (out-)nodes for timing variables and connector models
                    with dotGraph.subgraph() as bottom:
                        bottom.attr(rank='max')
                        tVar_prev = None
                        for tVar_i in var_i.getAllTimingVariables():
                            bottom.node(self.__timingVariableOut(tVar_i.name), label=tVar_i.name, shape='box')
                            # Enforce representation of tVar nodes in order?
                            if tVar_prev is not None:
                                bottom.edge(self.__timingVariableOut(tVar_prev.name), self.__timingVariableOut(tVar_i.name), style='invis') 
                            tVar_prev = tVar_i

                        # TODO: Show all connector models, or just the onces used by this scheduling function? 
                        for conModel_i in var_i.getAllConnectorModels():
                            bottom.node(self.__connectorModelOut(conModel_i.name), label=conModel_i.name, shape='box')
                            
                    # Make nodes for scheduling function nodes
                    for node_i in func_i.getAllNodes():
                        dotGraph.node(self.__scheduleNode(node_i.name), label=node_i.name, shape='ellipse')
                        # Connect resource model
                        if node_i.hasDynamicDelay():
                            resModelName = node_i.getResourceModel().name
                            dotGraph.node(self.__resourceModel(resModelName), label=resModelName, shape='box')
                            dotGraph.edge(self.__resourceModel(resModelName), self.__scheduleNode(node_i.name))
                        # Connect to previous nodes
                        for prevNode_i in node_i.getAllInNodes():
                            dotGraph.edge(self.__scheduleNode(prevNode_i.name), self.__scheduleNode(node_i.name))
                        # Connect in-edges
                        for edge_i in node_i.getAllInEdges():
                            if edge_i.isDynamic():
                                dotGraph.edge(self.__connectorModelIn(edge_i.getConnectorModel().name), self.__scheduleNode(node_i.name), label=edge_i.name)
                            else:
                                dotGraph.edge(self.__timingVariableIn(edge_i.getTimingVariable().name), self.__scheduleNode(node_i.name))
                        # Connect out-edges
                        for edge_i in node_i.getAllOutEdges():
                            if edge_i.isDynamic():
                                dotGraph.edge(self.__scheduleNode(node_i.name), self.__connectorModelOut(edge_i.getConnectorModel().name), label=edge_i.name)
                            else:
                                dotGraph.edge(self.__scheduleNode(node_i.name), self.__timingVariableOut(edge_i.getTimingVariable().name))
                                
                    dotGraph.render('graph', format='png', view=True)

    def __timingVariableIn(self, name_):
        return ("tvi_" + name_)

    def __timingVariableOut(self, name_):
        return ("tvo_" + name_)

    def __scheduleNode(self, name_):
        return ("n_" + name_)

    def __connectorModelIn(self, name_):
        return ("cmi_" + name_)

    def __connectorModelOut(self, name_):
        return ("cmo_" + name_)

    def __resourceModel(self, name_):
        return ("rm_" + name_)
