${builder_.getFileHeader()}

#ifndef ${builder_.getHeaderGuardPrefix()}_INSTRUCTION_SCHEDULING_FUNCTIONS_H
#define ${builder_.getHeaderGuardPrefix()}_INSTRUCTION_SCHEDULING_FUNCTIONS_H

#include "InstructionSchedulingFunctions.h"

namespace ${builder_.getName()}{

extern const MAP_Explorer::InstructionDictionary ${builder_.getName()}_instrDict;

} // namespace ${builder_.getName()}

#endif // ${builder_.getHeaderGuardPrefix()}_INSTRUCTION_SCHEDULING_FUNCTIONS_H