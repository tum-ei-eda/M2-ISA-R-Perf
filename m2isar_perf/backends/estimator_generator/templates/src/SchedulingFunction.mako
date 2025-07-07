${builder_.getFileHeader()}

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
  // Dump Entrance point for info print (tracing)
  perfModel->entrancePoint = n_Enter;
  }
);

% endfor

} // namespace ${variant_.name}