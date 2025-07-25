${builder_.getFileHeader()}

#include "${variant_.name}_PerformanceModel.h"

#include <stdbool.h>
#include <string>
#include <sstream>
#include <algorithm>

#include "Channel.h"

#include "${variant_.name}_Channel.h"

% for model_i in variant_.getAllExternalModels():
#include "${model_i.link}"
%endfor

namespace ${variant_.name}{

void ${variant_.name}_PerformanceModel::connectChannel(Channel* channel_)
{
  ${variant_.name}_Channel* channel = static_cast<${variant_.name}_Channel*>(channel_);

  % for model_i in variant_.getAllExternalModels():
  % for trVal_i in model_i.getAllTraceValues():
  ${model_i.name}.${trVal_i}_ptr = channel->${trVal_i};
  %endfor

  %endfor
}

uint64_t ${variant_.name}_PerformanceModel::getCycleCount(void)
{
  <% firstIt = True %>
  return std::max({
  %for var_i in variant_.getAllTimingVariables():
  %if firstIt:
    ${builder_.getTimingVariableCnt(var_i)} <% firstIt = False %>
  %else:
    ,${builder_.getTimingVariableCnt(var_i)}
  %endif
  %endfor
  });
}

std::string ${variant_.name}_PerformanceModel::getPipelineStream(void)
{
  std::stringstream ret_strs;
  ret_strs << entrancePoint;
  %for var_i in variant_.getAllTracedTimingVariables():
  ret_strs << "," << ${builder_.getTimingVariableCnt(var_i)};
  %endfor
  %for mod_i in variant_.getExternalModelsWithInfoTrace():
  ret_strs << "," << ${mod_i.name}.getInfoStream();
  %endfor
  ret_strs << std::endl;
  return ret_strs.str();
}

std::string ${variant_.name}_PerformanceModel::getPrintHeader(void)
{
  std::stringstream ret_strs;
  ret_strs << "Enter";
  %for var_i in variant_.getAllTracedTimingVariables():
  ret_strs << "," << "${var_i.name}";
  %endfor
  %for mod_i in variant_.getExternalModelsWithInfoTrace():
  ret_strs << "," << ${mod_i.name}.getInfoHeader();
  %endfor
  ret_strs << std::endl;
  return ret_strs.str();
}

} // namespace ${variant_.name}