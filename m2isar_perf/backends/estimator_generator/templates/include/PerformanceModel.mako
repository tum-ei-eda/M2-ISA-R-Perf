${builder_.getFileHeader()}

#ifndef ${builder_.getHeaderGuardPrefix()}_PERFORMANCE_MODEL_H
#define ${builder_.getHeaderGuardPrefix()}_PERFORMANCE_MODEL_H

#include <stdbool.h>
#include <string>
#include <cstdint>

#include "PerformanceModel.h"
#include "Channel.h"

% for resM_i in variant_.getAllResourceModels():
#include "${resM_i.link}"
%endfor
% for conM_i in variant_.getAllConnectorModels():
#include "${conM_i.link}"
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
    % for resM_i in variant_.getAllResourceModels():
    ,${resM_i.name}(this)
    %endfor
    % for conM_i in variant_.getAllConnectorModels():
    ,${conM_i.name}(this)
    %endfor
  {};

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

  %if variant_.getAllResourceModels():
  // External Resource Models
  %endif
  %for resM_i in variant_.getAllResourceModels():
  ${builder_.getModelType(resM_i.link)} ${resM_i.name};
  %endfor

  %if variant_.getAllConnectorModels():
  // External Connector Models
  %endif
  %for conM_i in variant_.getAllConnectorModels():
  ${builder_.getModelType(conM_i.link)} ${conM_i.name};
  %endfor

  virtual void connectChannel(Channel*);
  virtual uint64_t getCycleCount(void);
  virtual std::string getPipelineStream(void);
  virtual std::string getPrintHeader(void);

};

} // namespace ${variant_.name}

#endif // ${builder_.getHeaderGuardPrefix()}_PERFORMANCE_MODEL_H