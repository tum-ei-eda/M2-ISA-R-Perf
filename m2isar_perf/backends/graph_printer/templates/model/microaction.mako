<%!
## TODO: Get rid of this long path here!! Need something relative?
from backends.graph_printer.utils import str2latex
from backends.graph_printer.utils import str2latexCmd
from backends.graph_printer.utils import inConNodeName
from backends.graph_printer.utils import outConNodeName
from backends.graph_printer.utils import resNodeName
%>

<%
res = microaction.getResource()
inCon = microaction.getInConnector()
outCon = microaction.getOutConnector()

res_exists = res is not None
inCon_exists = inCon is not None
outCon_exists = outCon is not None

if res_exists:
   resNodeName_str = resNodeName(microaction)

if inCon_exists:
   inConNodeName_str = microaction.name + "_" + inCon.name

if outCon_exists:
   outConNodeName_str = microaction.name + "_" + outCon.name
   
%>

\node[microaction, below = \minStep of \placeRef, fill = \${str2latexCmd(microaction.name)}Fill] (${microaction.name}) {};
\node[above] at (${microaction.name}.south) {\tiny ${str2latex(microaction.name)}};
 
% if res_exists:
\node[resource](${resNodeName_str}) at (${microaction.name}.center) {\tiny ${str2latex(res.name)}};
% endif

% if inCon_exists:
\node[connector, left = \connectorOffset of ${microaction.name}.center] (${inConNodeName_str}) {\tiny ${str2latex(inCon.name)}};
% endif

% if inCon_exists and res_exists:
\draw[-stealth] (${inConNodeName_str}) -- (${resNodeName_str});
% endif

% if outCon_exists:
\node[connector, right = \connectorOffset of ${microaction.name}.center] (${outConNodeName_str}) {\tiny ${str2latex(outCon.name)}};
\draw[-stealth] (${resNodeName_str}) -- (${outConNodeName_str});
% endif
 
