int ${node_.getIdStr()};
${node_.getIdStr()} = std::max({\
<% firstIt = True %>\
% for prev in node_.getPrev():
% if firstIt:
${prev.getIdStr()}\
<% firstIt = False%>\
% else:
, ${prev.getIdStr()}\
%endif
%endfor
});