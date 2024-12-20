/*
 * Copyright 2024 Chair of EDA, Technical University of Munich
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *	 http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/********************* AUTO GENERATE FILE (create by M2-ISA-R-Perf) *********************/

#include <algorithm>
#include <cstdint>

#include "PerformanceModel.h"

#include "${variant_.name}_PerformanceModel.h"

namespace ${variant_.name}{

SchedulingFunctionSet* ${variant_.name}_SchedulingFunctionSet = new SchedulingFunctionSet("${variant_.name}_SchedulingFunctionSet");

% for schedFunc_i in variant_.getAllSchedulingFunctions():
static SchedulingFunction *schedulingFunction_${schedFunc_i.name} = new SchedulingFunction(
  ${variant_.name}_SchedulingFunctionSet,
  "${schedFunc_i.name}",
  ${schedFunc_i.identifier},
  [](PerformanceModel* perfModel_){
  ${variant_.name}_PerformanceModel* perfModel = static_cast<${variant_.name}_PerformanceModel*>(perfModel_);
  ${codeBodyDict_[schedFunc_i.name]}
  }
);

% endfor

} // namespace ${variant_.name}