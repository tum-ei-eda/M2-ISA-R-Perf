# 
#  Copyright 2026 Chair of EDA, Technical University of Munich
# 
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
# 
# 	 http://www.apache.org/licenses/LICENSE-2.0
# 
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

from .MatrixModel import MatrixModel, DynamicElement
from meta_models.scheduling_model.SchedulingModel import SchedulingModel

import networkx as nx
from itertools import product

class MatrixTransformer:

    def __init__(self):
        pass

    def transform(self, schedulingModel_:SchedulingModel):
        matrixModel = MatrixModel(schedulingModel_.name)

        for schedVar_i in schedulingModel_.getAllVariants():
            matrixVar = matrixModel.createVariant(schedVar_i.name)

            # TODO: Hack to create resource-groups. Need to get this information from SchedModel / CorePerfDSL
            for rMod_i in schedVar_i.getAllResourceModels():
                rGroup = matrixVar.createResourceGroup(rMod_i.name.upper())
                
                if rMod_i.name == "iCache":

                    iCacheConfigs = [
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 5, 'NUM_WAYS': 4, 'NUM_ROWS': 256}, # Default
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 5, 'NUM_WAYS': 2, 'NUM_ROWS': 512},
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 5, 'NUM_WAYS': 1, 'NUM_ROWS': 1024},
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 5, 'NUM_WAYS': 8, 'NUM_ROWS': 128},
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 5, 'NUM_WAYS': 16, 'NUM_ROWS': 64},
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 5, 'NUM_WAYS': 32, 'NUM_ROWS': 32},

                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 4, 'NUM_WAYS': 4, 'NUM_ROWS': 128}, # Faster memory, 1/2 cache
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 4, 'NUM_WAYS': 2, 'NUM_ROWS': 256},
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 4, 'NUM_WAYS': 1, 'NUM_ROWS': 512},
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 4, 'NUM_WAYS': 8, 'NUM_ROWS': 64},
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 4, 'NUM_WAYS': 16, 'NUM_ROWS': 32},

                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 6, 'NUM_WAYS': 4, 'NUM_ROWS': 512}, # Slower memory, 2x cache
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 6, 'NUM_WAYS': 2, 'NUM_ROWS': 1024},
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 6, 'NUM_WAYS': 1, 'NUM_ROWS': 2048},
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 6, 'NUM_WAYS': 8, 'NUM_ROWS': 256},
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 6, 'NUM_WAYS': 16, 'NUM_ROWS': 128}
                    ]

                    n = 4 # max: 4
                    for i in range(2**n):
                        mod = rGroup.createResourceModel((rMod_i.name + "_" + str(i)), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
                        mod.addConfig(iCacheConfigs[i])

#                    mod = rGroup.createResourceModel((rMod_i.name + "_1"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 5}) # Default
#                    mod = rGroup.createResourceModel((rMod_i.name + "_2"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 5, 'NUM_WAYS': 8, 'NUM_ROWS': 128})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_3"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 5, 'NUM_WAYS': 2, 'NUM_ROWS': 512})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_4"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 5, 'NUM_WAYS': 1, 'NUM_ROWS': 1024})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_5"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 5, 'NUM_WAYS': 16, 'NUM_ROWS': 64})
#                    
#                    mod = rGroup.createResourceModel((rMod_i.name + "_6"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 4})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_7"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 4, 'NUM_WAYS': 4, 'NUM_ROWS': 128})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_8"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 4, 'NUM_WAYS': 8, 'NUM_ROWS': 64})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_9"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 4, 'NUM_WAYS': 16, 'NUM_ROWS': 32})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_10"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 4, 'NUM_WAYS': 2, 'NUM_ROWS': 256})
#
#                    mod = rGroup.createResourceModel((rMod_i.name + "_11"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 4, 'NUM_WAYS': 1, 'NUM_ROWS': 512})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_12"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 4, 'NUM_WAYS': 32, 'NUM_ROWS': 16})
#
#
#                    mod = rGroup.createResourceModel((rMod_i.name + "_13"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 6})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_14"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 6, 'NUM_WAYS': 4, 'NUM_ROWS': 512})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_15"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 6, 'NUM_WAYS': 8, 'NUM_ROWS': 256})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_16"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 6, 'NUM_WAYS': 16, 'NUM_ROWS': 128})

#                    mod = rGroup.createResourceModel((rMod_i.name + "_17"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 6, 'NUM_WAYS': 2, 'NUM_ROWS': 1024})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_18"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 6, 'NUM_WAYS': 1, 'NUM_ROWS': 2048})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_19"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 6, 'NUM_WAYS': 16, 'NUM_ROWS': 256})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_20"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 6, 'NUM_WAYS': 32, 'NUM_ROWS': 64})
#
#                    mod = rGroup.createResourceModel((rMod_i.name + "_21"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 5, 'NUM_WAYS': 4, 'NUM_ROWS': 128})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_22"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 5, 'NUM_WAYS': 4, 'NUM_ROWS': 512})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_23"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 5, 'NUM_WAYS': 4, 'NUM_ROWS': 1024})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_24"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 5, 'NUM_WAYS': 4, 'NUM_ROWS': 64})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_25"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 5, 'NUM_WAYS': 4, 'NUM_ROWS': 32})
#
#                    mod = rGroup.createResourceModel((rMod_i.name + "_26"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 3, 'NUM_WAYS': 4, 'NUM_ROWS': 128})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_27"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 3, 'NUM_WAYS': 4, 'NUM_ROWS': 512})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_28"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 3, 'NUM_WAYS': 4, 'NUM_ROWS': 1024})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_29"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 3, 'NUM_WAYS': 4, 'NUM_ROWS': 64})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_30"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 3, 'NUM_WAYS': 4, 'NUM_ROWS': 32})
#
#                    mod = rGroup.createResourceModel((rMod_i.name + "_31"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 3, 'NUM_WAYS': 8, 'NUM_ROWS': 128})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_32"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 3, 'NUM_WAYS': 8, 'NUM_ROWS': 512})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_33"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 3, 'NUM_WAYS': 8, 'NUM_ROWS': 1024})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_34"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 3, 'NUM_WAYS': 8, 'NUM_ROWS': 64})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_35"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 3, 'NUM_WAYS': 8, 'NUM_ROWS': 32})
#
#                    mod = rGroup.createResourceModel((rMod_i.name + "_36"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 3, 'NUM_WAYS': 2, 'NUM_ROWS': 128})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_37"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 3, 'NUM_WAYS': 2, 'NUM_ROWS': 512})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_38"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 3, 'NUM_WAYS': 2, 'NUM_ROWS': 1024})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_39"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 3, 'NUM_WAYS': 2, 'NUM_ROWS': 64})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_40"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 3, 'NUM_WAYS': 2, 'NUM_ROWS': 32})
#
#                    mod = rGroup.createResourceModel((rMod_i.name + "_41"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 3, 'NUM_WAYS': 1, 'NUM_ROWS': 128})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_42"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 3, 'NUM_WAYS': 1, 'NUM_ROWS': 512})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_43"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 3, 'NUM_WAYS': 1, 'NUM_ROWS': 1024})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_44"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 3, 'NUM_WAYS': 1, 'NUM_ROWS': 64})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_45"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 3, 'NUM_WAYS': 1, 'NUM_ROWS': 32})
#
#                    mod = rGroup.createResourceModel((rMod_i.name + "_46"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 2, 'NUM_WAYS': 4, 'NUM_ROWS': 128})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_47"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 2, 'NUM_WAYS': 4, 'NUM_ROWS': 512})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_48"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 2, 'NUM_WAYS': 4, 'NUM_ROWS': 1024})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_49"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 2, 'NUM_WAYS': 4, 'NUM_ROWS': 64})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_50"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 2, 'NUM_WAYS': 4, 'NUM_ROWS': 32})
#
#                    mod = rGroup.createResourceModel((rMod_i.name + "_51"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 2, 'NUM_WAYS': 8, 'NUM_ROWS': 128})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_52"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 2, 'NUM_WAYS': 8, 'NUM_ROWS': 512})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_53"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 2, 'NUM_WAYS': 8, 'NUM_ROWS': 1024})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_54"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 2, 'NUM_WAYS': 8, 'NUM_ROWS': 64})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_55"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 2, 'NUM_WAYS': 8, 'NUM_ROWS': 32})
#
#                    mod = rGroup.createResourceModel((rMod_i.name + "_56"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 2, 'NUM_WAYS': 2, 'NUM_ROWS': 128})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_57"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 2, 'NUM_WAYS': 2, 'NUM_ROWS': 512})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_58"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 2, 'NUM_WAYS': 2, 'NUM_ROWS': 1024})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_59"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 2, 'NUM_WAYS': 2, 'NUM_ROWS': 64})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_60"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 2, 'NUM_WAYS': 2, 'NUM_ROWS': 32})
#
#                    mod = rGroup.createResourceModel((rMod_i.name + "_61"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 2, 'NUM_WAYS': 1, 'NUM_ROWS': 128})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_62"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 2, 'NUM_WAYS': 1, 'NUM_ROWS': 512})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_63"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 2, 'NUM_WAYS': 1, 'NUM_ROWS': 1024})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_64"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 2, 'NUM_WAYS': 1, 'NUM_ROWS': 64})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_65"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 2, 'NUM_WAYS': 1, 'NUM_ROWS': 32})
#
#
#
#                    mod = rGroup.createResourceModel((rMod_i.name + "_66"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 7, 'NUM_WAYS': 4, 'NUM_ROWS': 128})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_67"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 7, 'NUM_WAYS': 4, 'NUM_ROWS': 512})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_68"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 7, 'NUM_WAYS': 4, 'NUM_ROWS': 1024})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_69"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 7, 'NUM_WAYS': 4, 'NUM_ROWS': 64})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_70"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 7, 'NUM_WAYS': 4, 'NUM_ROWS': 32})
#
#                    mod = rGroup.createResourceModel((rMod_i.name + "_71"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 7, 'NUM_WAYS': 8, 'NUM_ROWS': 128})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_72"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 7, 'NUM_WAYS': 8, 'NUM_ROWS': 512})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_73"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 7, 'NUM_WAYS': 8, 'NUM_ROWS': 1024})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_74"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 7, 'NUM_WAYS': 8, 'NUM_ROWS': 64})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_75"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 7, 'NUM_WAYS': 8, 'NUM_ROWS': 32})
#
#                    mod = rGroup.createResourceModel((rMod_i.name + "_76"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 7, 'NUM_WAYS': 2, 'NUM_ROWS': 128})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_77"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 7, 'NUM_WAYS': 2, 'NUM_ROWS': 512})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_78"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 7, 'NUM_WAYS': 2, 'NUM_ROWS': 1024})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_79"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 7, 'NUM_WAYS': 2, 'NUM_ROWS': 64})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_80"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 7, 'NUM_WAYS': 2, 'NUM_ROWS': 32})
#
#                    mod = rGroup.createResourceModel((rMod_i.name + "_81"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 7, 'NUM_WAYS': 1, 'NUM_ROWS': 128})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_82"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 7, 'NUM_WAYS': 1, 'NUM_ROWS': 512})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_83"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 7, 'NUM_WAYS': 1, 'NUM_ROWS': 1024})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_84"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 7, 'NUM_WAYS': 1, 'NUM_ROWS': 64})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_85"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 7, 'NUM_WAYS': 1, 'NUM_ROWS': 32})
#
#
#
#                    mod = rGroup.createResourceModel((rMod_i.name + "_86"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 8, 'NUM_WAYS': 4, 'NUM_ROWS': 128})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_87"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 8, 'NUM_WAYS': 4, 'NUM_ROWS': 512})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_88"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 8, 'NUM_WAYS': 4, 'NUM_ROWS': 1024})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_89"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 8, 'NUM_WAYS': 4, 'NUM_ROWS': 64})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_90"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 8, 'NUM_WAYS': 4, 'NUM_ROWS': 32})
#
#                    mod = rGroup.createResourceModel((rMod_i.name + "_91"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 8, 'NUM_WAYS': 8, 'NUM_ROWS': 128})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_92"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 8, 'NUM_WAYS': 8, 'NUM_ROWS': 512})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_93"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 8, 'NUM_WAYS': 8, 'NUM_ROWS': 1024})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_94"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 8, 'NUM_WAYS': 8, 'NUM_ROWS': 64})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_95"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 8, 'NUM_WAYS': 8, 'NUM_ROWS': 32})
#
#                    mod = rGroup.createResourceModel((rMod_i.name + "_96"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 8, 'NUM_WAYS': 2, 'NUM_ROWS': 128})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_97"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 8, 'NUM_WAYS': 2, 'NUM_ROWS': 512})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_98"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 8, 'NUM_WAYS': 2, 'NUM_ROWS': 1024})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_99"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 8, 'NUM_WAYS': 2, 'NUM_ROWS': 64})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_100"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 8, 'NUM_WAYS': 2, 'NUM_ROWS': 32})
#
#                    mod = rGroup.createResourceModel((rMod_i.name + "_101"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 8, 'NUM_WAYS': 1, 'NUM_ROWS': 128})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_102"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 8, 'NUM_WAYS': 1, 'NUM_ROWS': 512})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_103"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 8, 'NUM_WAYS': 1, 'NUM_ROWS': 1024})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_104"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 8, 'NUM_WAYS': 1, 'NUM_ROWS': 64})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_105"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 8, 'NUM_WAYS': 1, 'NUM_ROWS': 32})
#
#
#                    mod = rGroup.createResourceModel((rMod_i.name + "_106"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 9, 'NUM_WAYS': 4, 'NUM_ROWS': 128})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_107"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 9, 'NUM_WAYS': 4, 'NUM_ROWS': 512})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_108"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 9, 'NUM_WAYS': 4, 'NUM_ROWS': 1024})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_109"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 9, 'NUM_WAYS': 4, 'NUM_ROWS': 64})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_110"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 9, 'NUM_WAYS': 4, 'NUM_ROWS': 32})
#
#                    mod = rGroup.createResourceModel((rMod_i.name + "_111"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 9, 'NUM_WAYS': 8, 'NUM_ROWS': 128})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_112"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 9, 'NUM_WAYS': 8, 'NUM_ROWS': 512})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_113"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 9, 'NUM_WAYS': 8, 'NUM_ROWS': 1024})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_114"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 9, 'NUM_WAYS': 8, 'NUM_ROWS': 64})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_115"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 9, 'NUM_WAYS': 8, 'NUM_ROWS': 32})
#
#                    mod = rGroup.createResourceModel((rMod_i.name + "_116"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 9, 'NUM_WAYS': 2, 'NUM_ROWS': 128})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_117"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 9, 'NUM_WAYS': 2, 'NUM_ROWS': 512})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_118"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 9, 'NUM_WAYS': 2, 'NUM_ROWS': 1024})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_119"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 9, 'NUM_WAYS': 2, 'NUM_ROWS': 64})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_120"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 9, 'NUM_WAYS': 2, 'NUM_ROWS': 32})
#
#                    mod = rGroup.createResourceModel((rMod_i.name + "_121"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 9, 'NUM_WAYS': 1, 'NUM_ROWS': 128})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_122"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 9, 'NUM_WAYS': 1, 'NUM_ROWS': 512})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_123"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 9, 'NUM_WAYS': 1, 'NUM_ROWS': 1024})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_124"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 9, 'NUM_WAYS': 1, 'NUM_ROWS': 64})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_125"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 9, 'NUM_WAYS': 1, 'NUM_ROWS': 32})
#
#
#                    mod = rGroup.createResourceModel((rMod_i.name + "_126"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 10, 'NUM_WAYS': 4, 'NUM_ROWS': 128})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_127"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 10, 'NUM_WAYS': 4, 'NUM_ROWS': 512})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_128"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 10, 'NUM_WAYS': 4, 'NUM_ROWS': 1024})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_129"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 10, 'NUM_WAYS': 4, 'NUM_ROWS': 64})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_130"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 10, 'NUM_WAYS': 4, 'NUM_ROWS': 32})
#
#                    mod = rGroup.createResourceModel((rMod_i.name + "_131"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 10, 'NUM_WAYS': 8, 'NUM_ROWS': 128})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_132"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 10, 'NUM_WAYS': 8, 'NUM_ROWS': 512})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_133"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 10, 'NUM_WAYS': 8, 'NUM_ROWS': 1024})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_134"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 10, 'NUM_WAYS': 8, 'NUM_ROWS': 64})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_135"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 10, 'NUM_WAYS': 8, 'NUM_ROWS': 32})
#
#                    mod = rGroup.createResourceModel((rMod_i.name + "_136"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 10, 'NUM_WAYS': 2, 'NUM_ROWS': 128})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_137"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 10, 'NUM_WAYS': 2, 'NUM_ROWS': 512})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_138"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 10, 'NUM_WAYS': 2, 'NUM_ROWS': 1024})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_139"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 10, 'NUM_WAYS': 2, 'NUM_ROWS': 64})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_140"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 10, 'NUM_WAYS': 2, 'NUM_ROWS': 32})
#
#                    mod = rGroup.createResourceModel((rMod_i.name + "_141"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 10, 'NUM_WAYS': 1, 'NUM_ROWS': 128})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_142"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 10, 'NUM_WAYS': 1, 'NUM_ROWS': 512})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_143"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 10, 'NUM_WAYS': 1, 'NUM_ROWS': 1024})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_144"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 10, 'NUM_WAYS': 1, 'NUM_ROWS': 64})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_145"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 10, 'NUM_WAYS': 1, 'NUM_ROWS': 32})
#
#
#
#
#                    mod = rGroup.createResourceModel((rMod_i.name + "_146"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 11, 'NUM_WAYS': 4, 'NUM_ROWS': 128})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_147"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 11, 'NUM_WAYS': 4, 'NUM_ROWS': 512})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_148"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 11, 'NUM_WAYS': 4, 'NUM_ROWS': 1024})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_149"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 11, 'NUM_WAYS': 4, 'NUM_ROWS': 64})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_150"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 11, 'NUM_WAYS': 4, 'NUM_ROWS': 32})
#
#                    mod = rGroup.createResourceModel((rMod_i.name + "_151"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 11, 'NUM_WAYS': 8, 'NUM_ROWS': 128})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_152"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 11, 'NUM_WAYS': 8, 'NUM_ROWS': 512})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_153"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 11, 'NUM_WAYS': 8, 'NUM_ROWS': 1024})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_154"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 11, 'NUM_WAYS': 8, 'NUM_ROWS': 64})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_155"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 11, 'NUM_WAYS': 8, 'NUM_ROWS': 32})
#
#                    mod = rGroup.createResourceModel((rMod_i.name + "_156"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 11, 'NUM_WAYS': 2, 'NUM_ROWS': 128})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_157"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 11, 'NUM_WAYS': 2, 'NUM_ROWS': 512})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_158"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 11, 'NUM_WAYS': 2, 'NUM_ROWS': 1024})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_159"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 11, 'NUM_WAYS': 2, 'NUM_ROWS': 64})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_160"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 11, 'NUM_WAYS': 2, 'NUM_ROWS': 32})
#
#                    mod = rGroup.createResourceModel((rMod_i.name + "_161"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 11, 'NUM_WAYS': 1, 'NUM_ROWS': 128})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_162"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 11, 'NUM_WAYS': 1, 'NUM_ROWS': 512})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_163"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 11, 'NUM_WAYS': 1, 'NUM_ROWS': 1024})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_164"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 11, 'NUM_WAYS': 1, 'NUM_ROWS': 64})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_165"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 11, 'NUM_WAYS': 1, 'NUM_ROWS': 32})
#
#
#
#                    mod = rGroup.createResourceModel((rMod_i.name + "_166"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 12, 'NUM_WAYS': 4, 'NUM_ROWS': 128})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_167"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 12, 'NUM_WAYS': 4, 'NUM_ROWS': 512})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_168"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 12, 'NUM_WAYS': 4, 'NUM_ROWS': 1024})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_169"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 12, 'NUM_WAYS': 4, 'NUM_ROWS': 64})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_170"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 12, 'NUM_WAYS': 4, 'NUM_ROWS': 32})
#
#                    mod = rGroup.createResourceModel((rMod_i.name + "_171"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 12, 'NUM_WAYS': 8, 'NUM_ROWS': 128})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_172"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 12, 'NUM_WAYS': 8, 'NUM_ROWS': 512})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_173"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 12, 'NUM_WAYS': 8, 'NUM_ROWS': 1024})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_174"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 12, 'NUM_WAYS': 8, 'NUM_ROWS': 64})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_175"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 12, 'NUM_WAYS': 8, 'NUM_ROWS': 32})
#
#                    mod = rGroup.createResourceModel((rMod_i.name + "_176"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 12, 'NUM_WAYS': 2, 'NUM_ROWS': 128})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_177"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 12, 'NUM_WAYS': 2, 'NUM_ROWS': 512})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_178"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 12, 'NUM_WAYS': 2, 'NUM_ROWS': 1024})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_179"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 12, 'NUM_WAYS': 2, 'NUM_ROWS': 64})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_180"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 12, 'NUM_WAYS': 2, 'NUM_ROWS': 32})
#
#                    mod = rGroup.createResourceModel((rMod_i.name + "_181"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 12, 'NUM_WAYS': 1, 'NUM_ROWS': 128})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_182"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 12, 'NUM_WAYS': 1, 'NUM_ROWS': 512})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_183"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 12, 'NUM_WAYS': 1, 'NUM_ROWS': 1024})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_184"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 12, 'NUM_WAYS': 1, 'NUM_ROWS': 64})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_185"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 12, 'NUM_WAYS': 1, 'NUM_ROWS': 32})
#
#
#                    mod = rGroup.createResourceModel((rMod_i.name + "_186"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 13, 'NUM_WAYS': 4, 'NUM_ROWS': 128})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_187"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 13, 'NUM_WAYS': 4, 'NUM_ROWS': 512})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_188"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 13, 'NUM_WAYS': 4, 'NUM_ROWS': 1024})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_189"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 13, 'NUM_WAYS': 4, 'NUM_ROWS': 64})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_190"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 13, 'NUM_WAYS': 4, 'NUM_ROWS': 32})
#
#                    mod = rGroup.createResourceModel((rMod_i.name + "_191"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 13, 'NUM_WAYS': 8, 'NUM_ROWS': 128})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_192"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 13, 'NUM_WAYS': 8, 'NUM_ROWS': 512})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_193"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 13, 'NUM_WAYS': 8, 'NUM_ROWS': 1024})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_194"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 13, 'NUM_WAYS': 8, 'NUM_ROWS': 64})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_195"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 13, 'NUM_WAYS': 8, 'NUM_ROWS': 32})
#
#                    mod = rGroup.createResourceModel((rMod_i.name + "_196"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 13, 'NUM_WAYS': 2, 'NUM_ROWS': 128})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_197"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 13, 'NUM_WAYS': 2, 'NUM_ROWS': 512})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_198"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 13, 'NUM_WAYS': 2, 'NUM_ROWS': 1024})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_199"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 13, 'NUM_WAYS': 2, 'NUM_ROWS': 64})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_200"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 13, 'NUM_WAYS': 2, 'NUM_ROWS': 32})
#
#                    mod = rGroup.createResourceModel((rMod_i.name + "_201"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 13, 'NUM_WAYS': 1, 'NUM_ROWS': 128})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_202"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 13, 'NUM_WAYS': 1, 'NUM_ROWS': 512})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_203"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 13, 'NUM_WAYS': 1, 'NUM_ROWS': 1024})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_204"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 13, 'NUM_WAYS': 1, 'NUM_ROWS': 64})
#                    mod = rGroup.createResourceModel((rMod_i.name + "_205"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 13, 'NUM_WAYS': 1, 'NUM_ROWS': 32})
#
#                    #mod = rGroup.createResourceModel((rMod_i.name + "_3"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    #mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 3})
#                    #mod = rGroup.createResourceModel((rMod_i.name + "_4"), "map_models/ICacheModel.h", rMod_i.getAllTraceValues())
#                    #mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 1})
#
                elif rMod_i.name == "dCache":
                    
                    dCacheConfigs = [
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 5, 'NUM_WAYS': 4, 'NUM_ROWS': 256}, # Default
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 5, 'NUM_WAYS': 2, 'NUM_ROWS': 512},
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 5, 'NUM_WAYS': 1, 'NUM_ROWS': 1024},
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 5, 'NUM_WAYS': 8, 'NUM_ROWS': 128},
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 5, 'NUM_WAYS': 16, 'NUM_ROWS': 64},
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 5, 'NUM_WAYS': 32, 'NUM_ROWS': 32},

                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 4, 'NUM_WAYS': 4, 'NUM_ROWS': 128}, # Faster memory, 1/2 cache
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 4, 'NUM_WAYS': 2, 'NUM_ROWS': 256},
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 4, 'NUM_WAYS': 1, 'NUM_ROWS': 512},
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 4, 'NUM_WAYS': 8, 'NUM_ROWS': 64},
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 4, 'NUM_WAYS': 16, 'NUM_ROWS': 32},

                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 6, 'NUM_WAYS': 4, 'NUM_ROWS': 512}, # Slower memory, 2x cache
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 6, 'NUM_WAYS': 2, 'NUM_ROWS': 1024},
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 6, 'NUM_WAYS': 1, 'NUM_ROWS': 2048},
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 6, 'NUM_WAYS': 8, 'NUM_ROWS': 256},
                        {'CACHE_DELAY': 1, 'MEMORY_DELAY': 6, 'NUM_WAYS': 16, 'NUM_ROWS': 128}
                    ]

                    n = 4 # max: 4
                    for i in range(2**n):
                        mod = rGroup.createResourceModel((rMod_i.name + "_" + str(i)), "map_models/DCacheModel.h", rMod_i.getAllTraceValues())
                        mod.addConfig(dCacheConfigs[i])
                    
                    
                    
                    #mod = rGroup.createResourceModel((rMod_i.name + "_1"), "map_models/DCacheModel.h", rMod_i.getAllTraceValues())
                    #mod.addConfig({'CACHE_DELAY': 1, 'MEMORY_DELAY': 5}) # Default

                elif rMod_i.name == "divider":
                    rGroup.createResourceModel(rMod_i.name, "map_models/Divider_CV32E40P.h", rMod_i.getAllTraceValues())
                elif rMod_i.name == "divider_u":
                    rGroup.createResourceModel(rMod_i.name, "map_models/DividerUnsigned_CV32E40P.h", rMod_i.getAllTraceValues())
                else:
                    print(f"WARNING: Currently no idea how to handle resource-model {rMod_i.name}...EXPAND HACK!")

            # TODO: Hack to create branch-group
            brGroup = matrixVar.createBranchGroup()
            
            branchConfig = [
                {'NUM_PAGES': 2, 'NUM_ROWS': 64}, # Default
                {'NUM_PAGES': 4, 'NUM_ROWS': 32},
                {'NUM_PAGES': 2, 'NUM_ROWS': 128}, # Increased size
                {'NUM_PAGES': 4, 'NUM_ROWS': 64},
                {'NUM_PAGES': 2, 'NUM_ROWS': 32}, # Decreased size
                {'NUM_PAGES': 4, 'NUM_ROWS': 16},
            ]

            n = 0 # max: 3
            for i in range(2**n):
                if i == 0:
                    brGroup.createBranchModel("branch_ant", "map_models/Branch_ant.h", ["pc", "brTarget"]) # always non-taken
                elif i == 1:
                    brGroup.createBranchModel("branch_fnt_bt", "map_models/Branch_fnt_bt.h", ["pc", "brTarget"]) # forward: non-taken, backward: taken
                else:
                    j = i-2
                    mod = brGroup.createBranchModel("branch_2sat_" + str(j), "map_models/Branch_2sat.h", ["pc", "brTarget"]) # Dynamic 2-sat.
                    mod.addConfig(branchConfig[j])

            #brGroup.createBranchModel("branch_ant", "map_models/Branch_ant.h", ["pc", "brTarget"])
            ##brGroup.createBranchModel("branch_fnt_bt", "map_models/Branch_fnt_bt.h", ["pc", "brTarget"])
            ##mod = brGroup.createBranchModel("branch_2sat_1", "map_models/Branch_2sat.h", ["pc", "brTarget"])
            ##mod.addConfig({'NUM_PAGES': 2, 'NUM_ROWS': 64})
            ##mod = brGroup.createBranchModel("branch_2sat_2", "map_models/Branch_2sat.h", ["pc", "brTarget"])
            ##mod.addConfig({'NUM_PAGES': 4, 'NUM_ROWS': 32})

            # Create combinations for all involved models
            for brMod_i in matrixVar.getBranchGroup().getAllModels():
                for resModComb_i in product(*(g.getAllModels() for g in matrixVar.getAllResourceGroups())):
                    matrixVar.createCombination(brMod_i, resModComb_i)


            for timingVar_i in schedVar_i.getAllTimingVariables():
                matrixVar.addTimingVariable(timingVar_i.name, timingVar_i.numElements)

            # TODO: Need to get this information from the model
            matrixVar.addRegisterSet([("Xa", "rs1"), ("Xb", "rs2")], [("Xd", "rd")], 32)
            matrixVar.addBranchSet(["Pc"], ["Pc_p", "Pc_np"])

            for schedFunc_i in schedVar_i.getAllSchedulingFunctions():

                #skipInstr = False # TODO: This should be removed as soon as we can cover all features (e.g. dynamic delays)

                instr = matrixVar.createInstruction(schedFunc_i.name, schedFunc_i.identifier)

                # Generate Scheduling-Graph (networkx)
                schedGraph = nx.DiGraph()
                openNodes = [schedFunc_i.getRootNode()]
                while openNodes:
                    curNode = openNodes.pop(0)

                    if curNode.hasDynamicDelay():

                        # TODO: Hack to find a resource-group
                        resModel = curNode.getResourceModel()

                        weight = DynamicElement(instr.createDynamicDelay(resModel.name.upper()))
                    else:
                        weight = curNode.getDelay()

#                    if curNode.hasDynamicDelay():
#                        print(f"{schedVar_i.name}::{schedFunc_i.name}::{curNode.name} has dynamic delay. I cannot handle that yet!")
#                        skipInstr = True
#                        break
#                    delay = curNode.getDelay()

                    for inEdge_i in curNode.getAllInEdges():
                        inVar = matrixVar.getInVariable(self.__getEdgeName(inEdge_i))
                        schedGraph.add_edge(inVar.getGraphName(), curNode.name, weight=0)

                    for outNode_i in curNode.getAllOutNodes():
                        if outNode_i not in openNodes:
                            openNodes.append(outNode_i)
                        schedGraph.add_edge(curNode.name, outNode_i.name, weight=weight)

                    for outEdge_i in curNode.getAllOutEdges():
                        outVar = matrixVar.getOutVariable(self.__getEdgeName(outEdge_i))
                        schedGraph.add_edge(curNode.name, outVar.getGraphName(), weight=weight)

                #if skipInstr:
                #    continue
                
                # Calculate longest path between all out- and in-variable pairs to create the compressed Instr-Matrix
                cInstrMatrix = instr.getCompressedInstructionMatrix()
                for outVar_i in matrixVar.getAllOutVariables():
                    
                    if outVar_i.getGraphName() not in schedGraph:                        
                        cInstrMatrix.addDefaultRow(outVar_i)
                        continue
                    
                    for inVar_i in matrixVar.getAllInVariables():
                        
                        if inVar_i.getGraphName() not in schedGraph:
                            cInstrMatrix.addElement(inVar_i, outVar_i, -1)
                            continue
                        
                        paths = list(nx.all_simple_paths(schedGraph, inVar_i.getGraphName(), outVar_i.getGraphName()))

                        if not paths:
                            cInstrMatrix.addElement(inVar_i, outVar_i, -1)
                            continue

                        maxWeight = -1
                        for path_i in paths:
                            weight = self.__getPathWeight(schedGraph, path_i)
                            if maxWeight == -1:
                                maxWeight = weight
                            else:
                                if isinstance(maxWeight, DynamicElement):
                                    #maxWeight = maxWeight.compare(weight)
                                    maxWeight.max(weight)
                                else:
                                    if isinstance(weight, DynamicElement):
                                        maxWeight = DynamicElement(maxWeight)
                                        #maxWeight = maxWeight.compare(weight)
                                        maxWeight.max(weight)
                                    else:
                                        maxWeight = max(maxWeight, weight)                            

                        cInstrMatrix.addElement(inVar_i, outVar_i, maxWeight)

        return matrixModel

    def __getPathWeight(self, schedGraph_, path_):
        weight = 0
        for i, j in zip(path_[:-1], path_[1:]):
            w = schedGraph_[i][j]["weight"]
            if isinstance(weight, DynamicElement):
                weight.add(w)
            else:
                if isinstance(w, DynamicElement):
                    weight = DynamicElement(weight)
                    weight.add(w)
                else:
                    weight += w
        return weight

    def __getEdgeName(self, edge_):
        if not edge_.isDynamic():
            if edge_.depth > 1:
                raise RuntimeError(f"Edge-depth is {edge_.depth} (>1). I cannot handle this yet!")
        return edge_.name if edge_.isDynamic() else edge_.getTimingVariable().name