// ${node_.name}
uint64_t ${builder_.getNodeStr(node_)};
${builder_.getNodeStr(node_)} = ${builder_.getInElementStr(node_.getAllInElements()[0])} + ${builder_.getNodeDelay(node_)};
% for outEdge_i in node_.getAllOutEdges():
${builder_.getOutEdgeStr(outEdge_i, node_)};
%endfor