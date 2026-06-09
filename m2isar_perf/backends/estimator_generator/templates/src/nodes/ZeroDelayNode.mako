// ${node_.name}
uint64_t ${builder_.getNodeStr(node_)};
${builder_.getNodeStr(node_)} = std::max({\
% for in_i in node_.getAllInElements():
${builder_.getInElementStr(in_i)}${"" if loop.last else ","}\
%endfor
});
% for outEdge_i in node_.getAllOutEdges():
${builder_.getOutEdgeStr(outEdge_i, node_)};
%endfor