// ${node_.name}
uint64_t ${builder_.getNodeStr(node_)};
uint64_t ${builder_.getNodeMaxStr(node_)};
${builder_.getNodeMaxStr(node_)} = std::max({\
<% firstIt = True %>\
% for in_i in node_.getAllInElements():
% if firstIt:
${builder_.getInElementStr(in_i)}\
<% firstIt = False %>\
% else:
, ${builder_.getInElementStr(in_i)}\
%endif
%endfor
});
${builder_.getNodeStr(node_)} = ${builder_.getNodeMaxStr(node_)} + ${builder_.getNodeDelay(node_)};
% for outEdge_i in node_.getAllOutEdges():
${builder_.getOutEdgeStr(outEdge_i, node_)};
%endfor