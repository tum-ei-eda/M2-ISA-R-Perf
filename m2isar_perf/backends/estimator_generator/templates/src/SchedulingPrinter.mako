${builder_.getFileHeader()}

#include <sstream>
#include <string>
#include <cstdint>


#include "${variant_.name}_PerformanceModel.h"

namespace ${variant_.name}{

SchedulingPrinterSet* ${variant_.name}_SchedulingPrinterSet = new SchedulingPrinterSet("${variant_.name}_SchedulingPrinterSet");

% for schedFunc_i in variant_.getAllSchedulingFunctions():
static SchedulingPrinter *schedulingPrinter_${schedFunc_i.name} = new SchedulingPrinter(
  ${variant_.name}_SchedulingPrinterSet,
  "${schedFunc_i.name}",
  ${schedFunc_i.identifier},
  [](PerformanceModel* pm_) -> std::string{
    auto* pm = static_cast<${variant_.name}_PerformanceModel*>(pm_);
    std::stringstream ss;
    // TODO: printing rule (entrancePoint, stages, branch pred, ...)
    ss << pm->entrancePoint;
    <%
    allTrVal = variant_.getAllTracedTimingVariables()
    traced_names = set([tv.name for tv in schedFunc_i.getTracedTimingVariables()])
    %>
    % for tv in allTrVal:
    %   if tv.name in traced_names:
    ss << "," << pm->${tv.name};
    %   else:
    ss << ",";  // empty for ${tv.name}
    %   endif
    % endfor
    %for mod_i in variant_.getExternalModelsWithInfoTrace():
    ss << "," << pm->${mod_i.name}.getInfoStream();
    %endfor
    ss << "\n";
    return ss.str();
});

% endfor

} // namespace ${variant_.name}