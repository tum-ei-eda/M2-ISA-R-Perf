${builder_.getFileHeader()}

#include "${builder_.getName()}_BlockSchedulingFunctions.h"

#include <array>

namespace ${builder_.getName()}{

% for blk_i in blocks_:
extern const MAP_Explorer::Block block_${blk_i.id};
% endfor

const std::array<const MAP_Explorer::Block*, ${len(blocks_)}> ${builder_.getName()}_blocks{{
    %for blk_i in blocks_:
    &block_${blk_i.id}${"" if loop.last else ","}
    %endfor
}};

const ${builder_.getName()}_BlockDictionary ${builder_.getName()}_blockDict{${builder_.getName()}_blocks};

} // namespace ${builder_.getName()}