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

# This class provides convenience functions to the latex templates

class PrintHelper:

    def __init__(self):
        pass

    def str2latex(self, str_):
        return str_.replace("_", "\_")

    def str2latexCmd(self, str_):
        return str_.replace("_", "")

    def inConNodeName(self, uA_):
        return self.microactionElementNodeName(uA_, "inCon")

    def outConNodeName(self, uA_):
        return self.microactionElementNodeName(uA_, "outCon")

    def resNodeName(self, uA_):
        return self.microactionElementNodeName(uA_, "res")

    def microactionElementNodeName(self, uA_, type_):
        if type_ == "inCon":
            element = uA_.getInConnector()
        elif type_ == "outCon":
            element = uA_.getOutConnector()
        elif type_ == "res":
            element = uA_.getResource()
        else:
            raise TypeError("Cannot call function microactionElementNodeName with type %s" % type_)
        
        if element is not None:
            return uA_.name + "_" + element.name
        else:
            raise TypeError("Error when calling microactionElementNodeName. Element of type %s does not exist" % type_)

    def inConLinkNodeName(self, uA_):
        return self.conLinkNodeName(uA_, "inCon")

    def outConLinkNodeName(self, uA_):
        return self.conLinkNodeName(uA_, "outCon")

    def conLinkNodeName(self, uA_, type_):
        if type_ == "inCon":
            conNodeName = self.microactionElementNodeName(uA_, "inCon")
        elif type_ == "outCon":
            conNodeName = self.microactionElementNodeName(uA_, "outCon")
        else:
            raise TypeError("Cannot call function conLinkNodeName with type %s" % type_)

        return conNodeName + "_link"

    def conModOutputNodeName(self, conMod_, i_):
        return conMod_.name + "_out_" + str(i_)

    def conModInputNodeName(self, conMod_, i_):
        return conMod_.name + "_in_" + str(i_)

    def elementTitle(self, e_):
        return e_.name + "_title"
