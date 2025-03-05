# 
# Copyright 2024 Chair of EDA, Technical University of Munich
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

from datetime import datetime

from meta_models.scheduling_model.SchedulingModel import DynamicEdge
from meta_models.scheduling_model.SchedulingModel import StaticEdge
from meta_models.scheduling_model.SchedulingModel import Node

class CodeBuilder:

    def __init__(self, variant_):
        self.variant = variant_

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
        return ("SWEVAL_BACKENDS_" + self.variant.name.upper())

    def getModelType(self, link_):
        # Assumption: Model type has same name as header-file. E.g.: link:"models/Register.h" -> type:Register
        fileName = link_.split('/').pop()
        return fileName.split('.h')[0]

    def getTimingVariableCnt(self, tVar_):
        if tVar_.hasMultiElements():
            return tVar_.name + ".get(1)" # TODO: Check if this matches the final definition of the get function
        return tVar_.name
    
    def getNodeStr(self, node_):
        return ("n_" + node_.name)

    def getNodeMaxStr(self, node_):
        return ("n_" + node_.name + "_max")

    def getSingleInElement(self, node_):
        if not node_.hasSingleInElement():
            raise RuntimeError(f"Node {node_.name} has either more than a single input element or no input element!")
        return node_.getAllInElements()[0]
        
    def getInElementStr(self, element_):
        if isinstance(element_, Node):
            return self.getNodeStr(element_)
        elif isinstance(element_, StaticEdge):
            tVar = element_.getTimingVariable()
            if tVar.hasMultiElements():
                return(f"perfModel->{tVar.name}.get({element_.depth})")
            else:
                return(f"perfModel->{tVar.name}")
            #return ("perfModel->" + element_.getTimingVariable().name + ".get()") # TODO: Adjust for get-call to timing variable with depth
        elif isinstance(element_, DynamicEdge):
            return ("perfModel->" + element_.getConnectorModel().name + ".get" + element_.name + "()")
        raise RuntimeError(f"Provided element ({element_}) cannot be identified")

    def getOutEdgeStr(self, edge_, node_):
        if isinstance(edge_, StaticEdge):
            tVar = edge_.getTimingVariable()
            if tVar.hasMultiElements():
                return (f"perfModel->{tVar.name}.set({self.getNodeStr(node_)})")
            else:
                return(f"perfModel->{tVar.name} = {self.getNodeStr(node_)}")
            #return ("perfModel->" + edge_.getTimingVariable().name + ".set(" + self.getNodeStr(node_) + ")")
        elif isinstance(edge_, DynamicEdge):
            return ("perfModel->" + edge_.getConnectorModel().name + ".set" + edge_.name + "(" + self.getNodeStr(node_) + ")")
        raise RuntimeError(f"Provided edge ({edge_}) cannot be identified")
        
    def getNodeDelay(self, node_):
        if node_.hasDynamicDelay():
            return ("perfModel->" + node_.getResourceModel().name + ".getDelay()")
        else:
            return str(node_.getDelay())
