#
# Copyright 2026 Chair of EDA, Technical University of Munich
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#	 http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import pathlib
import json

from backends.common import dirUtils

class BlockScheduleGenerator:

    def __init__(self):
        pass
        #self.templateDir = pathlib.Path(__file__).parents[0] / "templates"

    def execute(self, model_, blockList_, outDir_):

        blockListPath = pathlib.Path(blockList_).resolve()
        with blockListPath.open('r', encoding='utf-8') as f:
            self.blockDict = json.load(f)

        print()
        print("-- BACKEND: BLOCK_SCHEDULE_GENERATOR --")

        for variant_i in model_.getAllVariants():

            print(f" > Creating output directory for {variant_i.name}")
            outDir = dirUtils.getCodeDirPath(outDir_, variant_i, "block_sched")
            dirUtils.createOrReplaceDir(outDir / "src")
            dirUtils.createOrReplaceDir(outDir / "include")

            print(f" > Generating block-schedules for {variant_i.name}")
            self.__generateBlockScheduleFunctions(variant_i, outDir)

    def __generateBlockScheduleFunctions(self, variant_, outDir_):
        
        for block_i in self.blockDict["blocks"]:
            print(f"{block_i['id']}: {block_i['pc']}")