// ${node_.name}
uint64_t ${builder_.getNodeStr(node_)};
${builder_.getNodeStr(node_)} = std::max({\
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
% for outEdge_i in node_.getAllOutEdges():
${builder_.getOutEdgeStr(outEdge_i, node_)};
%endfor