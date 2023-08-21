/*
 * Copyright 2022 Chair of EDA, Technical University of Munich
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

#include "${corePerfModel_.name}_PerformanceModel.h"

InstructionModelSet* ${corePerfModel_.name}_InstrModelSet = new InstructionModelSet("${corePerfModel_.name}_InstrModelSet");

% for instr_i in corePerfModel_.getInstructionDict().values():
static InstructionModel *instrModel_${instr_i.name.replace('.','_')} = new InstructionModel(
  ${corePerfModel_.name}_InstrModelSet,
  "${instr_i.name}",
  ${instr_i.identifier},
  [](PerformanceModel* perfModel_){
  ${corePerfModel_.name}_PerformanceModel* perfModel = static_cast<${corePerfModel_.name}_PerformanceModel*>(perfModel_);
  % for line_i in codeArrayDict_[instr_i.name]:
  ${line_i}
  % endfor
  }
);

%endfor
