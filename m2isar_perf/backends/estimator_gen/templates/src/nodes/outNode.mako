uint64_t ${node_.getIdStr()};
perfModel->${node_.getModel().name}.set${node_.name}(${node_.getPrev().getIdStr()});
${node_.getIdStr()} = ${node_.getPrev().getIdStr()};