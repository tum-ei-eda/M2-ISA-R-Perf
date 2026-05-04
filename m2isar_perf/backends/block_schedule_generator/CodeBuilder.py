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

class CodeBuilder:

    def __init__(self, variant_):
        self.variant = variant_

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