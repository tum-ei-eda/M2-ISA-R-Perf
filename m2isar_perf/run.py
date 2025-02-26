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

from common import common as cf

from frontends.corePerfDsl import api as Frontend # TODO: Change from API to Class format 

from meta_models.scheduling_model.SchedulingTransformer import SchedulingTransformer

from backends.monitor_extractor import api as backend_monitor_extractor # TODO: Change from API to Class format 
from backends.schedule_viewer.SchedulingModelViewer import SchedulingModelViewer
from backends.estimator_generator.EstimatorGenerator import EstimatorGenerator

# Read command line arguments
argParser = argparse.ArgumentParser()
argParser.add_argument("description", help="File containing the description of the performance model.")
argParser.add_argument("-o", "--output_dir", help="Directory to store generated files")
argParser.add_argument("-c", "--code_gen", action="store_true", help="Generate estimator code")
argParser.add_argument("-m", "--monitor_description", action="store_true", help="Generate monitor description")
argParser.add_argument("-i", "--info_print", action="store_true", help="Generate info/debug/doc prints")
argParser.add_argument("-d", "--dump_dir", help="Directory to dump intermediatly generated models.")
args = argParser.parse_args()

# Resolve outDir
outDir = cf.resolveOutDir(args.output_dir, __file__, 1)

# Call frontend to generate structural-model
if args.description.endswith('.corePerfDsl'):
    structModel = Frontend.execute(args.description, args.dump_dir)
else:
    sys.exit("FATAL: Description format is not supported. Currently only supporting files of type .corePerfDsl")

# Call model transformer (structural -> scheduling model) if applicable
if args.code_gen or args.info_print:
    schedModel = SchedulingTransformer().transform(structModel)
    #transformer = SchedulingTransformer()
    #schedModel = transformer.transform(structModel)

# Call applicable backends
if args.monitor_description:
    backend_monitor_extractor.execute(structModel, outDir)
if args.code_gen:
    print("WARNING: Code-generator backend currently disabled!")
    
    # EstimatorGenerator().execute(schedModel, outDir)
    # #generator = EstimatorGenerator()
    # #generator.execute(schedModel, outDir)
if args.info_print :
    print("WARNING: SchedulingViewer backend currently disabled!")
    
    SchedulingModelViewer().execute(schedModel, outDir)
    #viewer = SchedulingViewer()
    #viewer.execute(schedModel, outDir)
