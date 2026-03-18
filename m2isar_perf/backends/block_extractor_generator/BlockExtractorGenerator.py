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

from mako.template import Template
import pathlib

from .CodeBuilder import CodeBuilder
from backends.common import dirUtils

class BlockExtractorGenerator:

    def __init__(self):
        self.templateDir = pathlib.Path(__file__).parents[0] / "templates"

    def execute(self, model_, outDir_):

        print()
        print("-- BACKEND: BLOCK_EXTRACTOR_GENERATOR --")

        for variant_i in model_.getAllVariants():

            print(f" > Creating output directory for {variant_i.name}")
            outDir = dirUtils.getCodeDirPath(outDir_, variant_i, "block_extractor")
            #dirUtils.createOrReplaceDir(outDir / "src")
            dirUtils.createOrReplaceDir(outDir / "include")

            self.builder = CodeBuilder(variant_i)

            # TODO: Need to get this information from the model!
            self.builder.setPcTraceValue("pc")
            self.builder.setObservedTraceValues(["rs1", "rs2", "rd"])
            self.builder.setBranchInstrList([43, 44, 45, 46, 47, 48, 49, 50, 52, 53])

            self.__generateBlockExtractor(outDir)
            self.__generateBlockInstructionGenerator(model_.getAllInstructions(), outDir)

            #print(f" > Generating estimator for {variant_i.name}")
            #self.builder = Builder(variant_i)
            #self.__generatePerformanceModel(variant_i, outDir)
            #self.__generateSchedulingFunctions(variant_i, outDir)

        #for instr_i in model_.getAllInstructions():
        #    print(f"{instr_i.name}: ", end="")
        #    for trVal_i in [x.getTraceValue() for x in instr_i.getTraceValueAssignments()]:
        #        print(f"{trVal_i.name}, ", end="")
        #    print() 

    def __generateBlockExtractor(self, outDir_):

        template_header = Template(filename = str(self.templateDir) + "/include/BlockExtractor.mako")
        code_header = template_header.render(**{"builder_": self.builder})
        outFile_header = outDir_ / "include"/ (self.builder.getName() + "_BlockExtractor.h")
        with outFile_header.open('w') as f:
            f.write(code_header)

    def __generateBlockInstructionGenerator(self, instructions_, outDir_):

        template_header = Template(filename = str(self.templateDir) + "/include/BlockInstructionGenerator.mako")
        code_header = template_header.render(**{"instructions_": instructions_,"builder_": self.builder})
        outFile_header = outDir_ / "include"/ (self.builder.getName() + "_BlockInstructionGenerator.h")
        with outFile_header.open('w') as f:
            f.write(code_header)
