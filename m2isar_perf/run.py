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

# Read command line arguments
argParser = argparse.ArgumentParser()
argParser.add_argument("description", help="File containing the description of the performance model.")
argParser.add_argument("output_dir", help="Directory to store generated files")
argParser.add_argument("-d", "--dump_dir", help="Directory to dump intermediatly generated models.")
args = argParser.parse_args()

# Import appropriate frontend
if args.description.endswith('.corePerfDsl'):
    import frontends.CorePerfDSL.run as frontend
else:
    sys.exit("FATAL: Description format is not supported. Currently only supporting files of type .corePerfDsl")

# Import backend
#import backends.estimator_gen.run as backend
import backends.graph_printer.run as backend
    
# Call frontend
model = frontend.main(args.description, args.dump_dir)

backend.main(model)
