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

from datetime import datetime

class CodeBuilder:

    def __init__(self, variant_):
        self.variant = variant_

    def getName(self):
        return self.variant.name
    
    def setObservedTraceValues(self, trVals_):
        self.observedTraceValues = trVals_

    def setBranchInstrList(self, list_):
        self.branchInstrList = list_

    def setPcTraceValue(self, pc_):
        self.pc = pc_

    def getPcTraceValue(self):
        return self.pc

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
    
    def getUsedTraceValues(self, instr_):
        ret = []
        for trVal_i in self.observedTraceValues:
            if trVal_i in self.__getObservableTraceValues(instr_):
                ret.append(trVal_i)
        return ret

    def getTraceValuePairs(self, instr_):
        retList = []
        usedTrvals = self.getUsedTraceValues(instr_)
        for obsTrVal_i in self.observedTraceValues:
            if obsTrVal_i in usedTrvals:
                retList.append((obsTrVal_i, obsTrVal_i))
            else:
                retList.append((obsTrVal_i, "\"null\""))
        return retList
    
    def isBranchInstr(self, instr_):
        if instr_.identifier in self.branchInstrList:
            return True
        return False
    
    def __getObservableTraceValues(self, instr_):
        return [x.getTraceValue().name for x in instr_.getTraceValueAssignments()]

