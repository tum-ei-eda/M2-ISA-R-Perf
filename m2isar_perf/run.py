#!/usr/bin/env python3

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

import argparse
import pathlib
import pickle
import sys
import time

from common import common as cf

from frontends.corePerfDsl import api as Frontend # TODO: Change from API to Class format 

from meta_models.scheduling_model.SchedulingTransformer import SchedulingTransformer
from meta_models.matrix_model.MatrixTransformer import MatrixTransformer

from backends.monitor_extractor import api as backend_monitor_extractor # TODO: Change from API to Class format 
#from backends.structure_viewer.StructuralModelViewer import StructuralModelViewer
from backends.schedule_viewer.SchedulingModelViewer import SchedulingModelViewer
from backends.estimator_generator.EstimatorGenerator import EstimatorGenerator
from backends.block_extractor_generator.BlockExtractorGenerator import BlockExtractorGenerator
from backends.block_schedule_generator.BlockScheduleGenerator import BlockScheduleGenerator


# Read command line arguments
startTime = time.time()
argParser = argparse.ArgumentParser()
argParser.add_argument("description", help="File containing the description of the performance model.")
argParser.add_argument("-o", "--output_dir", help="Directory to store generated files")
argParser.add_argument("-c", "--code_gen", action="store_true", help="Generate estimator code")
argParser.add_argument("-m", "--monitor_description", action="store_true", help="Generate monitor description")
argParser.add_argument("-i", "--info_print", action="store_true", help="Generate info/debug/doc prints")

argParser.add_argument("-e", "--block_ext", action="store_true", help="Generate block extractor")
argParser.add_argument("-b", "--block_gen", help="Generate block-scheduling-functions")

argParser.add_argument("-d", "--dump_dir", help="Directory to dump intermediatly generated models.")

argParser.add_argument("-t1", "--test_1", help="Num. of I\$ variants")
argParser.add_argument("-t2", "--test_2", help="Num. of D\$ variants")
argParser.add_argument("-t3", "--test_3", help="Num. of Br.Pred variants")

args = argParser.parse_args()

# Resolve outDir
outDir = cf.resolveOutDir(args.output_dir, __file__, 1)

# Call frontend to generate structural-model
if args.description.endswith('.corePerfDsl'):
    structModel = Frontend.execute(args.description, args.dump_dir)
else:
    sys.exit("FATAL: Description format is not supported. Currently only supporting files of type .corePerfDsl")

# Call model transformers if applicable
if args.code_gen or args.info_print or (args.block_gen is not None):
    schedModel = SchedulingTransformer().transform(structModel)
    if args.block_gen is not None:
        if (args.test_1 is not None) and (args.test_2 is not None) and (args.test_3 is not None):
            matrixModel = MatrixTransformer(args.test_1, args.test_2, args.test_3).transform(schedModel)
        else:
            matrixModel = MatrixTransformer().transform(schedModel)
            transTime = time.time()
            print(f"Time spend on parsing and model transformation: {float(transTime-startTime)}s")

# Call applicable backends
if args.monitor_description:
    backend_monitor_extractor.execute(structModel, outDir)
if args.code_gen:
    EstimatorGenerator().execute(schedModel, outDir)
if args.block_ext:
    BlockExtractorGenerator().execute(structModel, outDir)
if args.block_gen is not None:
    gen = BlockScheduleGenerator()
    
    gen.execute(matrixModel, schedModel, args.block_gen, outDir)
    gen.getInfo()
    
    #BlockScheduleGenerator().execute(matrixModel, args.block_gen, outDir)
if args.info_print :
    #StructuralModelViewer().execute(structModel, outDir)
    SchedulingModelViewer().execute(schedModel, outDir)

# Calculate run-time
endTime = time.time()
print(f"Total execution time M2ISAR-Perf: {float(endTime-startTime)}s")


