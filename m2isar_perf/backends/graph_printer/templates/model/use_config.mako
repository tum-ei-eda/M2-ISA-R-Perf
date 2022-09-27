<%!
## TODO: Get rid of this long path here!! Need something relative?
from backends.graph_printer.utils import str2latexCmd
%>

% for uA in microactionList:
% if uA in usedMicroactionList:
\newcommand\${str2latexCmd(uA.name)}Fill{gray}
% else:
\newcommand\${str2latexCmd(uA.name)}Fill{white}
% endif
% endfor