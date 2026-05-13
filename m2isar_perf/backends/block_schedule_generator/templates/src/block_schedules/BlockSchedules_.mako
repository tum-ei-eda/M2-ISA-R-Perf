${builder_.getFileHeader()}

#include "BlockSchedulingFunctions.h"

#include <algorithm>

namespace ${builder_.getName()}{

% for blk_i in blocks_:
static void block_${blk_i.id}_fn(uint64_t* vec_, uint8_t* d_){
    ${blk_i.code}
}

extern const MAP_Explorer::Block block_${blk_i.id}{
    ${blk_i.id},
    ${blk_i.startPc},
    ${blk_i.endPc},
    block_${blk_i.id}_fn
    };

% endfor

} // namespace ${builder_.getName()}