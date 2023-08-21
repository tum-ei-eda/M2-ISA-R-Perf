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

import pathlib
import json

class Translator:

    def __init__(self, tempDir_):
        self.tempDirBase = tempDir_

    def createTraceDescriptions(self, model_):

        for corePerfModel_i in model_.getAllCorePerfModels():

            # Create trace dictionary
            trace = {}
            trace["name"] = corePerfModel_i.name
            trace["setId"] = "Manual"
            trace["traceValues"] = self.__getTraceValues(corePerfModel_i)
            trace["instructions"] = self.__getInstructions(corePerfModel_i)

            # Create a "root" dictionary for json
            json_dict = {}
            json_dict["trace"] = trace

            # Dump root dictionary to file
            outFile = self.tempDirBase / corePerfModel_i.name / "trace.json"
            with outFile.open('w') as f:
                json.dump(json_dict, f, indent=2)
        

    def __getTraceValues(self, corePerfModel_):
        traceValues = []
        for trVal_i in corePerfModel_.getAllUsedTraceValues():
            traceValues.append({"name": trVal_i.name, "type": "uint64_t"})
        return traceValues

    def __getInstructions(self, corePerfModel_):
        usedTraceValues = corePerfModel_.getAllUsedTraceValues()
        
        instructions = []
        for instr_i in corePerfModel_.getAllInstructions():
            mappings = []
            for map_i in instr_i.getTraceValueAssignments():
                if map_i.getTraceValue() in usedTraceValues:
                    mappings.append({"traceValue": map_i.getTraceValue().name, "description": map_i.getDescription()})
            instructions.append({"name": instr_i.name, "id": instr_i.identifier, "mappings": mappings}) 

        return instructions

        
