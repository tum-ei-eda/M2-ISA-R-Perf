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
import pathlib
import os

from backends.common import dirUtils

class SchedulingModelViewer:

    def __init__(self):
        self.tempDirBase = pathlib.Path(__file__).parent / "temp"

    def execute(self, model_, outDir_):

        print()
        print("-- BACKEND: SCHEDULE_VIEWER --")

        for variant_i in model_.getAllVariants():

            # Make sure output directories and temp directory exist
            print(f" > Creating output directories for {variant_i.name}")
            tempDir = (self.tempDirBase) / variant_i.name
            dirUtils.createOrReplaceDir(tempDir, suppress_warning=True)
            outDir = dirUtils.getDocDirPath(outDir_, variant_i.name)
            # Generate sub-dirs for each instr/sched.function
            for schedFunc_i in variant_i.getAllSchedulingFunctions():
                (outDir / schedFunc_i.name).mkdir(parents=True, exist_ok=True) # Do not over-write: Could delete output for structure_viewer
            
            for func_i in variant_i.getAllSchedulingFunctions():

                if func_i.name: #TODO: Check why there would be any sched.funcs without a name?
                    
                    dotGraph = graphviz.Digraph(comment=func_i.name)
                    dotGraph.attr(rankdir='TB')

                    # Make (in-)nodes for timing variables and connector models
                    with dotGraph.subgraph() as top:
                        top.attr(rank='min')
                        tVar_prev = None
                        for tvariable_i in variant_i.getAllTimingVariables():
                            top.node(self.__timingVariableIn(tvariable_i.name), label=(tvariable_i.name + " [" + str(tvariable_i.depth) + "]"), shape='box')
                            # Enforce representation of tVar nodes in order?
                            if tVar_prev is not None:
                                top.edge(self.__timingVariableIn(tVar_prev.name), self.__timingVariableIn(tvariable_i.name), style='invis') 
                            tVar_prev = tvariable_i

                        # TODO: Show all connector models, or just the onces used by this scheduling function? 
                        for conModel_i in variant_i.getAllConnectorModels():
                            top.node(self.__connectorModelIn(conModel_i.name), label=conModel_i.name, shape='box')

                    # Make (out-)nodes for timing variables and connector models
                    with dotGraph.subgraph() as bottom:
                        bottom.attr(rank='max')
                        tVar_prev = None
                        for tvariable_i in variant_i.getAllTimingVariables():
                            bottom.node(self.__timingVariableOut(tvariable_i.name), label=tvariable_i.name, shape='box')
                            # Enforce representation of tVar nodes in order?
                            if tVar_prev is not None:
                                bottom.edge(self.__timingVariableOut(tVar_prev.name), self.__timingVariableOut(tvariable_i.name), style='invis') 
                            tVar_prev = tvariable_i

                        # TODO: Show all connector models, or just the onces used by this scheduling function? 
                        for conModel_i in variant_i.getAllConnectorModels():
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
                                dotGraph.edge(self.__timingVariableIn(edge_i.getTimingVariable().name), self.__scheduleNode(node_i.name), label=("[" + str(edge_i.depth) + "]")) # Implicit "cast" to StaticEdge
                        # Connect out-edges
                        for edge_i in node_i.getAllOutEdges():
                            if edge_i.isDynamic():
                                dotGraph.edge(self.__scheduleNode(node_i.name), self.__connectorModelOut(edge_i.getConnectorModel().name), label=edge_i.name)
                            else:
                                dotGraph.edge(self.__scheduleNode(node_i.name), self.__timingVariableOut(edge_i.getTimingVariable().name))
                                
                    #dotGraph.render('graph', format='png', view=True)

                    tempFile = tempDir / (func_i.name + ".dot")
                    with tempFile.open('w') as f:
                        f.write(dotGraph.source)

                    os.chdir(tempDir)
                    os.system(f"dot -Tpdf {func_i.name}.dot -o {func_i.name}.pdf")
                    os.replace(f"{str(tempDir)}/{func_i.name}.pdf", f"{str(outDir / func_i.name)}/{func_i.name}_schedulingFunction.pdf")
                    
                    
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
