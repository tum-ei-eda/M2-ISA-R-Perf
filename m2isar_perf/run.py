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

from meta_models.scheduling_model.SchedulingTransformer import SchedulingTransformer

from backends.schedule_viewer.SchedulingModelViewer import SchedulingModelViewer

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

# Import appropriate frontend
if args.description.endswith('.corePerfDsl'):
    import frontends.corePerfDsl.api as frontend
else:
    sys.exit("FATAL: Description format is not supported. Currently only supporting files of type .corePerfDsl")

# Import backends
backends = []
if args.code_gen:
    #import backends.estimator_gen.run as backend_estimator_gen
    #backends.append(backend_estimator_gen)
    print("\nNOTE: Backend currently not supported! Try again later...")
if args.monitor_description:
    import backends.monitor_extractor.api as backend_monitor_extractor
    backends.append(backend_monitor_extractor)
if args.info_print:
    import backends.structure_viewer.api as backend_structure_viewer
    backends.append(backend_structure_viewer)
    #print("\nNOTE: Backend currently not supported! Try again later...")
    
# Call frontend
model = frontend.execute(args.description, args.dump_dir)

# TEST SchedulingTransformer
transformer = SchedulingTransformer()
sModel = transformer.transform(model)

viewer = SchedulingModelViewer()
viewer.execute(sModel, outDir)


# Call all selected backends
for backend_i in backends:
    backend_i.execute(model, outDir)
