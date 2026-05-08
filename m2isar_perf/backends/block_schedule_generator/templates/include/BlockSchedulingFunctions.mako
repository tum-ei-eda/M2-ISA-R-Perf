${builder_.getFileHeader()}

#ifndef ${builder_.getHeaderGuardPrefix()}_BLOCK_SCHEDULING_FUNCTIONS_H
#define ${builder_.getHeaderGuardPrefix()}_BLOCK_SCHEDULING_FUNCTIONS_H

#include "BlockSchedulingFunctions.h"

namespace ${builder_.getName()}{

extern const MAP_Explorer::BlockDictionary ${builder_.getName()}_blockDict;

} // namespace ${builder_.getName()}

#endif // ${builder_.getHeaderGuardPrefix()}_BLOCK_SCHEDULING_FUNCTIONS_H