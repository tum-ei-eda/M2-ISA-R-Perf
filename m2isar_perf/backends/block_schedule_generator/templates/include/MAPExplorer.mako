${builder_.getFileHeader()}

#ifndef ${builder_.getHeaderGuardPrefix()}_BLOCK_EXTRACTOR_H
#define ${builder_.getHeaderGuardPrefix()}_BLOCK_EXTRACTOR_H

#include "MAPExplorer.h"

#include "${builder_.getName()}_BlockSchedulingFunctions.h"

namespace ${builder_.getName()}{

class ${builder_.getName()}_MAPExplorer : public MAPExplorer{

public:
    ${builder_.getName()}_MAPExplorer() : MAPExplorer(&CV32E40P_blockDict) {};
    ~${builder_.getName()}_MAPExplorer() = default;

};

} // namespace ${builder_.getName()}

#endif // ${builder_.getHeaderGuardPrefix()}_BLOCK_EXTRACTOR_H