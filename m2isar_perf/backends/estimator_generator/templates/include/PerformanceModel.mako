${builder_.getFileHeader()}

#ifndef ${builder_.getHeaderGuardPrefix()}_PERFORMANCE_MODEL_H
#define ${builder_.getHeaderGuardPrefix()}_PERFORMANCE_MODEL_H

#include <stdbool.h>
#include <string>
#include <cstdint>

#include "PerformanceModel.h"
#include "Channel.h"

%for model_i in variant_.getAllExternalModels():
#include "${model_i.link}"
%endfor

namespace ${variant_.name}{

extern SchedulingFunctionSet* ${variant_.name}_SchedulingFunctionSet;

class ${variant_.name}_PerformanceModel : public PerformanceModel
{
public:

  ${variant_.name}_PerformanceModel() : PerformanceModel("${variant_.name}", ${variant_.name}_SchedulingFunctionSet)
    % for tVar_i in variant_.getAllMultiElementTimingVariables():
    ,${tVar_i.name}(${tVar_i.getNumElements()},0)
    %endfor
    % for model_i in variant_.getAllExternalModels():
    ,${model_i.name}(this)
    %endfor
  {};

  // Entrance-point "timing variable" (only used for info-stream)
  uint64_t entrancePoint = 0;

  %if variant_.getAllSingleElementTimingVariables():
  // Single-Element Timing Variables
  %endif
  %for tVar_i in variant_.getAllSingleElementTimingVariables():
  uint64_t ${tVar_i.name} = 0;
  %endfor

  %if variant_.getAllMultiElementTimingVariables():
  // Multi-Element Timing Variables
  %endif
  %for tVar_i in variant_.getAllMultiElementTimingVariables():
  MultiElementTimingVariable ${tVar_i.name};
  %endfor	 

  %if variant_.getAllExternalModels():
  // External Resource Models
  %endif
  %for model_i in variant_.getAllExternalModels():
  ${builder_.getModelClassName(model_i)} ${model_i.name};
  %endfor

  virtual void connectChannel(Channel*);
  virtual uint64_t getCycleCount(void);
  virtual std::string getPipelineStream(void);
  virtual std::string getPrintHeader(void);

};

} // namespace ${variant_.name}

#endif // ${builder_.getHeaderGuardPrefix()}_PERFORMANCE_MODEL_H