<%!
## TODO: Get rid of this long path here!! Need something relative?
from backends.graph_printer.utils import str2latex
from backends.graph_printer.utils import inConNodeName
from backends.graph_printer.utils import outConNodeName
from backends.graph_printer.utils import resNodeName
from backends.graph_printer.utils import inConLinkNodeName
from backends.graph_printer.utils import outConLinkNodeName
from backends.graph_printer.utils import elementTitle
%>

<%
uAList = stage.getUsedMicroactions()
%>

\renewcommand\connectorLinkSpace{\minStep + (${numConnectorLinks}*\minStep)}

\node[stage, right = \connectorLinkSpace of \placeRef] (${stage.name}) {};
\node[minimum height = \stageTitleHeight, below] (${elementTitle(stage)}) at (${stage.name}.north) {\tiny ${str2latex(stage.name)}};

\renewcommand\placeRef{${elementTitle(stage)}.south}

<% inCon_i = 0 %>
<% outCon_i = 0 %>
%for uA in uAList:
\input{../microactions/${uA.name}.tex}
\renewcommand\placeRef{${uA.name}}

%if uA.getInConnector() is not None:
<% inCon_i += 1 %>
\renewcommand\connectorLinkOffset{\connectorLinkOffsetBase + ${inCon_i}*\minStep}
\coordinate[left = \connectorLinkOffset of ${inConNodeName(uA)}] (${inConLinkNodeName(uA)}) {};
\draw[-stealth] (${inConLinkNodeName(uA)}) -- (${inConNodeName(uA)});
%endif

%if uA.getOutConnector() is not None:
<% outCon_i += 1 %>
\renewcommand\connectorLinkOffset{\connectorLinkOffsetBase + ${outCon_i}*\minStep}
\coordinate[right = \connectorLinkOffset of ${outConNodeName(uA)}] (${outConLinkNodeName(uA)}) {};
\draw (${outConNodeName(uA)}) -- (${outConLinkNodeName(uA)});
%endif

%endfor


\renewcommand\placeRef{${stage.name}.south}
%for conMod in connectorModelList:
\input{../connectorModels/${conMod.name}.tex}
\let\oldConnectorModelOffset\connectorModelOffset
\renewcommand\connectorModelOffset{\oldConnectorModelOffset + \connectorModelHeight + \minStep}
%endfor
      
