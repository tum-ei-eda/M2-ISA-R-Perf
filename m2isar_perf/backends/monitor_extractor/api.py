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

#!/usr/bin/env python3

import argparse
import pathlib
import pickle
import sys
import json

from backends.common import dirUtils
from common import common as cf # common functions

##### API-FUNCTIONS (called by m2isar_perf/run.py) #####

def execute(model_, outDir_):

    print()
    print("-- BACKEND: MONITOR_EXTRACTOR --")
    
    for variant_i in model_.getAllVariants():
        
        # Create trace dictionary
        trace = {}
        trace["name"] = variant_i.name
        trace["core"] = variant_i.core
        trace["setId"] = "Manual"
        trace["traceValues"] = getTraceValues(variant_i)
        trace["instructions"] = getInstructions(variant_i)

        # Create a "root" dictionary for json
        json_dict = {}
        json_dict["trace"] = trace

        # Dump root dictionary to file
        outFile = dirUtils.getMonitorDirPath(outDir_, variant_i.name) / (variant_i.name + "_trace.json")
        outFile.parent.mkdir(parents=True, exist_ok=True) # Make sure that output directory exists
        with outFile.open('w') as f:
            json.dump(json_dict, f, indent=2)

##### SUPPORT FUNCTIONS #####
            
def getTraceValues(variant_):
    traceValues = []
    for trVal_i in variant_.getAllUsedTraceValues():
        traceValues.append({"name": trVal_i.name, "type": "uint64_t"})
    return traceValues

def getInstructions(variant_):
    usedTraceValues = variant_.getAllUsedTraceValues()
        
    instructions = []
    for instr_i in variant_.getAllInstructions():
        mappings = []
        for map_i in instr_i.getTraceValueAssignments():
            if map_i.getTraceValue() in usedTraceValues:
                mappings.append({"traceValue": map_i.getTraceValue().name, "description": map_i.getDescription()})
        instructions.append({"name": instr_i.name, "id": instr_i.identifier, "mappings": mappings}) 

    return instructions

##### STAND-ALONE #####

# Run this if backend is called stand-alone (i.e. this file is directly called)
if __name__ == '__main__':
    
    # Parse command line arguments
    argParser = argparse.ArgumentParser()
    argParser.add_argument("model", help="File containing the input model (generated by frontend)")
    argParser.add_argument("-o", "--output_dir", help="Path to store generated files")
    args = argParser.parse_args()

    # Load model from file
    modelFile = pathlib.Path(args.model).resolve()
    if not modelFile.is_file():
        sys.exit("FATAL: Specified model (%s) does not exist!" % modelFile)
    with modelFile.open('rb') as f:
        model = pickle.load(f) 

    outDir = cf.resolveOutDir(args.output_dir, __file__)
        
    # Call main routine of estimator_gen backend
    execute(model, outDir)
