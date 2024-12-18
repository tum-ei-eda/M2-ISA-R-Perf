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

class FrozenBase:
    __isFrozen = False

    def __setattr__(self, key, value):
        if self.__isFrozen and not hasattr(self, key):
            raise TypeError("Attempting to add new attribute to frozen class %r" %self)
        object.__setattr__(self, key, value)

    def __init__(self):
        self.__isFrozen = True
