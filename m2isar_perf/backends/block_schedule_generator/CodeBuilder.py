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

from datetime import datetime

from meta_models.scheduling_model.SchedulingModel import DynamicEdge
from meta_models.scheduling_model.SchedulingModel import StaticEdge
from meta_models.scheduling_model.SchedulingModel import Node

class CodeBuilder:

    def __init__(self, variant_):
        self.variant = variant_
        self.delayCnt = 0

    def getName(self):
        return self.variant.name

    def getFileHeader(self):
        retStr = "/*\n"
        retStr += f"* Copyright {datetime.today().year} Chair of EDA, Technical University of Munich\n"
        retStr += "*\n"
        retStr += "* Licensed under the Apache License, Version 2.0 (the \"License\");\n"
        retStr += "* you may not use this file except in compliance with the License.\n"
        retStr += "* You may obtain a copy of the License at\n"
        retStr += "*\n"
        retStr += "*	 http://www.apache.org/licenses/LICENSE-2.0\n"
        retStr += "*\n"
        retStr += "* Unless required by applicable law or agreed to in writing, software\n"
        retStr += "* distributed under the License is distributed on an \"AS IS\" BASIS,\n"
        retStr += "* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\n"
        retStr += "* See the License for the specific language governing permissions and\n"
        retStr += "* limitations under the License.\n"
        retStr += "*/\n"
        retStr += "\n"
        retStr += "/********************* AUTO GENERATE FILE (create by M2-ISA-R-Perf) *********************/\n"
        return retStr
    
    def getHeaderGuardPrefix(self):
        return ("SWEVAL_BACKENDS_" + self.getName().upper())
    
    def getResourceGroupClassName(self, resGr_):
        return (self.getName() + "_" + resGr_.name + "_ResourceGroup")
    
    def getResourceGroupName(self, resGr_):
        return ("resGroup_" + resGr_.name)
    
    def getBranchGroupClassName(self):
        return (self.getName() + "_BranchGroup")
    
    def getChannelClassName(self):
        return (self.getName() + "_Channel")
    
    # TODO: This is very hacky and not consistent with generation of PerformanceSimulator.... Find a better way
    #def getModelClassName(self, mod_):
    #    retStr = mod_.link.replace('.h','')
    #    retStr = retStr.replace('/','::')
    #    return retStr
    def getModelClassName(self, mod_):
        return self.getModelNamespace(mod_) + self.getModelClass(mod_)
    
    def getModelConfigName(self, mod_):
        return self.getModelNamespace(mod_) + self.getModelClass(mod_) + "_Config"

    def getModelNamespace(self, mod_):
        split = mod_.link.split('/')
        retStr = ""
        if len(split) > 1:
            for split_i in split[:-1]:
                retStr += split_i + "::"
        return retStr
    
    def getModelClass(self, mod_):
        split = mod_.link.replace('.h','').split('/')
        return split[-1]

    ## Helper function to write nodes for Instruction-Scheduling functions
    
    def getNodeStr(self, node_):
        return ("n_" + node_.name)

    def getNodeMaxStr(self, node_):
        return ("n_" + node_.name + "_max")

    def getNodeDelay(self, node_):
        if node_.hasDynamicDelay():
            ret = f"d_{self.delayCnt}"
            self.delayCnt += 1
            return ret
        else:
            return (str(node_.getDelay()))

    def resetDelayCnt(self):
        self.delayCnt = 0

    def getInElementStr(self, elem_):
        if isinstance(elem_, Node):
            return self.getNodeStr(elem_)
        elif isinstance(elem_, StaticEdge):
            tVar = elem_.getTimingVariable()
            if tVar.hasMultiElements():
                return self.getUnrolledStr(tVar.name, elem_.depth)
                #return(f"{tVar.name}__{elem_.depth}")
            else:
                return(f"{tVar.name}")
        elif isinstance(elem_, DynamicEdge):
            return elem_.name
        raise RuntimeError(f"Provided element ({elem_}) cannot be identified")

    def getOutEdgeStr(self, edge_, node_):
        if isinstance(edge_, StaticEdge):
            tVar = edge_.getTimingVariable()
            if tVar.hasMultiElements():
                return (f"{tVar.name}__{edge_.depth} = {self.getNodeStr(node_)}")
            else:
                return(f"{tVar.name} = {self.getNodeStr(node_)}")
        elif isinstance(edge_, DynamicEdge):
            return (f"uint64_t {edge_.name} = {self.getNodeStr(node_)}")
        raise RuntimeError(f"Provided edge ({edge_}) cannot be identified")
    
    def getUnrolledStr(self, name_:str, depth_:int):
        return f"{name_}__{depth_}"