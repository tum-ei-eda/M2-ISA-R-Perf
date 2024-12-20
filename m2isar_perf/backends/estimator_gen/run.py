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
import sys
import pickle

from backends.metaMathModel.ModelTransformer import ModelTransformer
from .CodeGenerator import CodeGenerator
from backends import utils as backendUtils
from common import common as cf # common functions

def main(model_, outDir_):

    print(">> HELLO FROM THE BACKEND <<")
    print()

    print("Creating output directories")
    outDirDict = {}
    for corePerfModel_i in model_.getAllCorePerfModels():
        dirPath = backendUtils.getCodeDirPath(outDir_, corePerfModel_i.name) / "perf_model"
        outDirDict[corePerfModel_i.name] = dirPath
        backendUtils.createOrReplaceDir(dirPath / "src")
        backendUtils.createOrReplaceDir(dirPath / "include")
    
    print("Generating Math-Model")
    transformer = ModelTransformer()
    mathModel = transformer.transform(model_)
    print()
    
    print("Generating code for estimator")
    curDir = pathlib.Path(__file__).parents[0]
    CodeGenerator(curDir / "templates", outDirDict).generateEstimator(mathModel)
        
    
# Run this if backend is called stand-alone (i.e. this file is directly called)
if __name__ == '__main__':

    # TODO: Move loading of file to backends-common folder? Common for all backends? Might have different arguments?
    
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

    # Resolve outDir
    outDir = cf.resolveOutDir(args.output_dir, __file__)
        
    # Call main routine of estimator_gen backend
    main(model, outDir)
