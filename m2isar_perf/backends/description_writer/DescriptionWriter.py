# 
# Copyright 2025 Chair of EDA, Technical University of Munich
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
from mako.template import Template

from .CorePerfDslBuilder import CorePerfDslBuilder

class DescriptionWriter:

    def __init__(self):
        self.templateDir_corePerfDsl = pathlib.Path(__file__).parents[0] / "templates/corePerfDsl"

    def execute(self, structModel_, outDir_, fileName_):

        retStr = ""

        ### Architectur e###
        arch_template = Template(filename = str(self.templateDir_corePerfDsl) + "/Architecture.mako")
        retStr += arch_template.render(**{"model_": structModel_})

        ### Microactions ###

        connectorDict = {} # Dict. of all unique conenctors in this model

        resourceDict = {} # Dict. of all unique resources in this model
        virtualResources = [] # List of all virtual microactions
        
        microactionDict = {} # Dict. of all unique microactions in this model
        virtualMicroactions = [] # List of all virtual microactions

        for var_i in structModel_.getAllVariants():
            for uAction_i in var_i.getAllMicroactions():

                # Identify unique connectors
                for con_i in (uAction_i.getInConnectors() + uAction_i.getOutConnectors()):
                    if con_i.name not in connectorDict:
                        connectorDict[con_i.name] = con_i

                # Identify unique resources and virtual resources
                for res_i in uAction_i.getResources():
                    if res_i.name not in resourceDict:
                        resourceDict[res_i.name] = res_i
                    if res_i.isVirtual():
                        virAlias = res_i.getVirtualAlias()
                        if virAlias not in virtualResources:
                            virtualResources.appen(virAlias)
                
                # Identify unique microactions and virtual microactions
                if uAction_i.name not in microactionDict:
                    microactionDict[uAction_i.name] = uAction_i
                if uAction_i.isVirtual():
                    virAlias = uAction_i.getVirtualAlias()
                    if virAlias not in virtualMicroactions:
                        virtualMicroactions.append(virAlias)
                                            
        microaction_template = Template(filename = str(self.templateDir_corePerfDsl) + "/Microactions.mako")
        retStr += microaction_template.render(**{'connectorDict_': connectorDict,
                                                 'resourceDict_': resourceDict,
                                                 'virtualResources_': virtualResources,
                                                 'microactionDict_': microactionDict,
                                                 'virtualMicroactions_': virtualMicroactions,
                                                 'builder_': CorePerfDslBuilder()
        })

        ### Stages & Pipelines ###
        
        stageDict = {} # Dict. of all unique stages in this model
        pipelineDict = {} # Dict. of all unique pipelines in this model

        for var_i in structModel_.getAllVariants():
            for pipe_i in var_i.getAllPipelines():
                if pipe_i.name not in pipelineDict:
                    pipelineDict[pipe_i.name] = pipe_i
            for st_i in var_i.getAllStages():
                if st_i.name not in stageDict:
                    stageDict[st_i.name] = st_i

        pipeline_template = Template(filename = str(self.templateDir_corePerfDsl) + "/Pipelines.mako")
        retStr += pipeline_template.render(**{'stageDict_': stageDict,
                                              'pipelineDict_': pipelineDict,
                                              'builder_': CorePerfDslBuilder()
        })

        ### Models ###

        modelDict = {} # Dict. of all unique external models in this structural model

        for var_i in structModel_.getAllVariants():
            for mod_i in var_i.getAllModels():
                if mod_i.name not in modelDict:
                    modelDict[mod_i.name] = mod_i

        model_template = Template(filename = str(self.templateDir_corePerfDsl) + "/Models.mako")
        retStr += model_template.render(**{'traceValues_': structModel_.getAllTraceValues(),
                                           'modelDict_': modelDict,
                                           'builder_': CorePerfDslBuilder()
        })
            

        ### Instructions ###

        microactionMappingDict = {} # Dict. mapping instructions (key) to list of microactions

        for instr_i in structModel_.getAllInstructions():
            microactionMappingDict[instr_i] = []

        for uAction_i in microactionDict.values():
            for instr_i in microactionMappingDict:
                if uAction_i.isUsedByInstr(instr_i):
                    microactionMappingDict[instr_i].append(uAction_i)
        
        mapping_template = Template(filename = str(self.templateDir_corePerfDsl) + "/Mappings.mako")
        retStr += mapping_template.render(**{'instructions_': structModel_.getAllInstructions(),
                                             'microactionMappingDict_': microactionMappingDict,
                                             'builder_': CorePerfDslBuilder()
        })


        ### Variants ###

        variant_template = Template(filename = str(self.templateDir_corePerfDsl) + "/Variants.mako")
        retStr += variant_template.render(**{'variants_': structModel_.getAllVariants(),
                                             'builder_': CorePerfDslBuilder()
        })
        
        # Generate CorePerfDSL file
        outFile = pathlib.Path(outDir_).resolve() / (fileName_ + ".corePerfDsl")
        with outFile.open('w') as f:
            f.write(retStr)
        
