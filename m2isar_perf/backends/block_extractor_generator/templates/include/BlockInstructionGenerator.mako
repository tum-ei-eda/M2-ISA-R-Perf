${builder_.getFileHeader()}

#ifndef ${builder_.getHeaderGuardPrefix()}_BLOCK_INSTRUCTION_GENERATOR_H
#define ${builder_.getHeaderGuardPrefix()}_BLOCK_INSTRUCTION_GENERATOR_H

#include "BlockInstructionGenerator.h"

#include "${builder_.getName()}_Channel.h"

#include <sstream>

namespace ${builder_.getName()}{

% for instr_i in instructions_:
class BlockInstruction_${instr_i.name} : public BlockInstruction{

public:
    BlockInstruction_${instr_i.name}(Channel* channel_, uint64_t instrCnt_): BlockInstruction(channel_, instrCnt_) {
        ${builder_.getName()}_Channel* channel = static_cast<${builder_.getName()}_Channel*>(channel_);
        % for trVal_i in builder_.getUsedTraceValues(instr_i):
        ${trVal_i} = channel->${trVal_i}[instrCnt_];
        % endfor
        % if builder_.isBranchInstr(instr_i):
        isBranch = true;
        % endif
    };
    ~BlockInstruction_${instr_i.name}() = default;

    std::string getJsonStr(std::string offset_){
        std::stringstream ret_strs;
        ret_strs << offset_ << "{\n";
        ret_strs << offset_ << "\t\"typeId\": " << typeId;
        % for (key_i, val_i) in builder_.getTraceValuePairs(instr_i):
        ret_strs << offset_ << "\t\"${key_i}\": " << ${val_i};
        % endfor
        ret_strs << "\n" << offset_ << "}";
        return ret_strs.str();
    };

private:
    % for trVal_i in builder_.getUsedTraceValues(instr_i):
    uint64_t ${trVal_i};
    % endfor

};

% endfor

class ${builder_.getName()}_BlockInstructionGenerator : public BlockInstructionGenerator{

public:
    ${builder_.getName()}_BlockInstructionGenerator(){
        % for instr_i in instructions_:
        ctorMap[${instr_i.identifier}] = [](Channel* channel_, uint64_t instrCnt_){ return std::make_unique<BlockInstruction_${instr_i.name}>(channel_, instrCnt_); };
        % endfor
    };
    ~${builder_.getName()}_BlockInstructionGenerator() = default;

};

} // namespace ${builder_.getName()}

#endif // ${builder_.getHeaderGuardPrefix()}_BLOCK_INSTRUCTION_GENERATOR_H