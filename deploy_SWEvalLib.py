# 
# Copyright 2023 Chair of EDA, Technical University of Munich
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
import sys
import pathlib
import shutil

## PATH DEFINITIONS ##
SWEVAL_MONITOR_VARIANTS_PATH = "libs/monitors/variants/"
SWEVAL_BACKENDS_VARIANTS_PATH = "libs/backends/variants/"

## SUPPORT FUNCTIONS ##

def checkDir_ERROR(dir_):
    if not dir_.is_dir():
        raise RuntimeError("Path \"" + str(dir_) + "\" does not exist!")

def copyList(list_, sourceDir_, targetDir_):
    for file_i in list_:
        print(" > Copy: " + file_i + "... ", end='')
        shutil.copyfile((sourceDir_ / file_i), (targetDir_ / file_i))
        print("Done.")

def createCMakeList(dir_, lib_, cppList_):
    cmake_file = dir_ / "CMakeLists.txt"
    with cmake_file.open('w') as f:
        f.write("TARGET_SOURCES(" + lib_.upper() + " PRIVATE\n")
        for file_i in cppList_:
            f.write("\tsrc/" + str(file_i) + "\n")
        f.write(")\n\n")
        f.write("TARGET_INCLUDE_DIRECTORIES(" + lib_.upper() + " PRIVATE\n")
        f.write("\tinclude\n")
        f.write(")")
    
## MAIN ROUTINE ##
    
argParser = argparse.ArgumentParser()
argParser.add_argument("path", help="Path to target SWEvalLib")
argParser.add_argument("-mod", "--model", help="Name of the model to deploy")
argParser.add_argument("-src", "--source", help="Path to source folder containing the files for deployment")
args = argParser.parse_args()

if args.model is None:
    sys.exit("FATAL: Did not specify any model to deploy")
else:
    modelName = args.model

# List of file names
monitor_h = modelName + "_Monitor.h"
monitor_cpp = modelName + "_Monitor.cpp"
instrMonitors_cpp = modelName + "_InstructionMonitors.cpp"

channel_h = modelName + "_Channel.h"
channel_cpp = modelName + "_Channel.cpp"
perfModel_h = modelName + "_PerformanceModel.h"
perfModel_cpp = modelName + "_PerformanceModel.cpp"
instrModels_cpp = modelName + "_InstructionModels.cpp"
instrPrinters_cpp = modelName + "_InstructionPrinters.cpp"
printer_h = modelName + "_Printer.h"
printer_cpp = modelName + "_Printer.cpp"

# Check that source files exist
if args.source is not None:
    sourcePath = pathlib.Path(args.source).resolve()
else:
    sourcePath = pathlib.Path(__file__).resolve().parent / "out"
checkDir_ERROR(sourcePath)
    
sourcePathDict = {}
for obj_i in ["monitor", "channel", "printer", "model"]:
    obj_path = sourcePath / (modelName + "/" + obj_i)
    checkDir_ERROR(obj_path)
    sourcePathDict[obj_i] = {"include" : obj_path / "include", "src" : obj_path / "src"}

# Check that target files exist
monitorVar_path = pathlib.Path(args.path + SWEVAL_MONITOR_VARIANTS_PATH).resolve()
checkDir_ERROR(monitorVar_path)
monitorModel_path = monitorVar_path / modelName
monitorInc_path = monitorModel_path / "include"
monitorSrc_path = monitorModel_path / "src"
if not monitorModel_path.is_dir():
    print("Creating directory: \"" + str(monitorModel_path) + "\"")
    monitorModel_path.mkdir()
    createCMakeList(monitorModel_path, "SWEVAL_MONITORS_LIB", [monitor_cpp, instrMonitors_cpp])

backendVar_path = pathlib.Path(args.path + SWEVAL_BACKENDS_VARIANTS_PATH).resolve()
checkDir_ERROR(backendVar_path)
backendModel_path = backendVar_path / modelName
backendInc_path = backendModel_path / "include"
backendSrc_path = backendModel_path / "src"
if not backendModel_path.is_dir():
    print("Creating directory: \"" + str(backendModel_path) + "\"")
    backendModel_path.mkdir()
    createCMakeList(backendModel_path, "SWEVAL_BACKENDS_LIB", [channel_cpp, instrModels_cpp, perfModel_cpp, instrPrinters_cpp, printer_cpp])

    
# Deploy model
    
print("")
print("Deploying monitor...")
copyList([monitor_h], sourcePathDict["monitor"]["include"], monitorInc_path)
copyList([monitor_cpp, instrMonitors_cpp], sourcePathDict["monitor"]["src"], monitorSrc_path)

print("")
print("Deploying channel...")
copyList([channel_h], sourcePathDict["channel"]["include"], backendInc_path)
copyList([channel_cpp], sourcePathDict["channel"]["src"], backendSrc_path)

print("")
print("Deploying printer...")
copyList([printer_h], sourcePathDict["printer"]["include"], backendInc_path)
copyList([printer_cpp, instrPrinters_cpp], sourcePathDict["printer"]["src"], backendSrc_path)

print("")
print("Deploying performance model...")
copyList([perfModel_h], sourcePathDict["model"]["include"], backendInc_path)
copyList([perfModel_cpp, instrModels_cpp], sourcePathDict["model"]["src"], backendSrc_path)
