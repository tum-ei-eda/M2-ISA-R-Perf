${builder_.getFileHeader()}

#include "BlockSchedulingFunctions.h"

#include <algorithm>

namespace ${builder_.getName()}{

% for blk_i in blocks_:

extern const MAP_Explorer::Block block_${blk_i.id}{
    ${blk_i.id},
    ${blk_i.startPc},
    ${blk_i.endPc},
    [](uint64_t* vec_, uint64_t* d_){
        ${blk_i.code}
    }};

% endfor

} // namespace ${builder_.getName()}