${builder_.getFileHeader()}

#include "InstructionSchedulingFunctions.h"

#include <array>
#include <algorithm>
#include <cstdint>

namespace ${builder_.getName()}{

% for instr_i in instructions_:
static void instr_${instr_i.name}_fn(uint64_t* vec_, uint8_t* d_, uint64_t rs1_, uint64_t rs2_, uint64_t rd_){
    ${instr_i.code}
}

const MAP_Explorer::Instruction instr_${instr_i.name}{
    ${instr_i.typeId},
    ${str(instr_i.isBranch).lower()},
    instr_${instr_i.name}_fn
};

% endfor

const std::array<const MAP_Explorer::Instruction*, ${len(instructions_)}> ${builder_.getName()}_instructions{{
    % for instr_i in instructions_:
    &instr_${instr_i.name}${"" if loop.last else ","}
    % endfor
}};

extern const MAP_Explorer::InstructionDictionary ${builder_.getName()}_instrDict{${builder_.getName()}_instructions.data(), ${builder_.getName()}_instructions.size()};

} // namespace ${builder_.getName()}