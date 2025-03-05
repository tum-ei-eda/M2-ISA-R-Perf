# 
# Copyright 2025 Chair of EDA, Technical University of Munich
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

class StructuralModelViewer:

    def __init__(self):
        self.tempDirBase = pathlib.Path(__file__).parent / "temp"

    def execute(self, model_, outDir_):

        print()
        print("-- BACKEND: STRUCTURAL_MODEL_VIEWER --")

        # # Make sure output directories and temp directory exist
        # print(f" > Creating output directories for {variant_i.name}")
        # tempDir = (self.tempDirBase) / variant_i.name
        # dirUtils.createOrReplaceDir(tempDir, suppress_warning=True)
        # outDir = dirUtils.getDocDirPath(outDir_, variant_i.name)
        # # Generate sub-dirs for each instr/sched.function
        # for schedFunc_i in variant_i.getAllSchedulingFunctions():
        #     (outDir / schedFunc_i.name).mkdir(parents=True, exist_ok=True) # Do not over-write: Could delete output of schedule_viewer

        dotGraph = graphviz.Digraph("TEST")

        with dotGraph.subgraph(name="top1") as c:
            c.attr(style="filled", label="TopNode1", color="lightblue")
            c.node("A1", "A1")
            c.node("A2", "A2")

        with dotGraph.subgraph(name="top2") as c:
            c.attr(style="filled", label="TopNode2", color="lightgreen")
            c.node("B1", "B1")
            c.node("B2", "B2")

        dotGraph.edge("A1","B1")
        dotGraph.edge("A2","B2")
        
        dotGraph.render('test', format='png', view=True)
