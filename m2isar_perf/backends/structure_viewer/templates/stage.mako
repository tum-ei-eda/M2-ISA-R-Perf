<%!
## TODO: Get rid of this long path here!! Need something relative?
from backends.structure_viewer.templates.templateUtils import str2latex
from backends.structure_viewer.templates.templateUtils import inConNodeName
from backends.structure_viewer.templates.templateUtils import outConNodeName
from backends.structure_viewer.templates.templateUtils import resNodeName
from backends.structure_viewer.templates.templateUtils import inConLinkNodeName
from backends.structure_viewer.templates.templateUtils import outConLinkNodeName
from backends.structure_viewer.templates.templateUtils import elementTitle
%>

<%
uAList = stage.getUsedMicroactions()
%>

\renewcommand\connectorLinkSpace{\minStep + (${numConnectorLinks}*\minStep)}

\node[stage, right = \connectorLinkSpace of \placeRef] (${stage.name}) {};
\node[minimum height = \stageTitleHeight, below] (${printHelper_.elementTitle(stage)}) at (${stage.name}.north) {\tiny ${printHelper_.str2latex(stage.name)}};

\renewcommand\placeRef{${printHelper_.elementTitle(stage)}.south}

<% inCon_i = 0 %>
<% outCon_i = 0 %>
%for uA in uAList:
\input{../microactions/${uA.name}.tex}
\renewcommand\placeRef{${uA.name}}

%if uA.getInConnector() is not None:
<% inCon_i += 1 %>
\renewcommand\connectorLinkOffset{\connectorLinkOffsetBase + ${inCon_i}*\minStep}
\coordinate[left = \connectorLinkOffset of ${printHelper_.inConNodeName(uA)}] (${printHelper_.inConLinkNodeName(uA)}) {};
\draw[-stealth] (${printHelper_.inConLinkNodeName(uA)}) -- (${printHelper_.inConNodeName(uA)});
%endif

%if uA.getOutConnector() is not None:
<% outCon_i += 1 %>
\renewcommand\connectorLinkOffset{\connectorLinkOffsetBase + ${outCon_i}*\minStep}
\coordinate[right = \connectorLinkOffset of ${printHelper_.outConNodeName(uA)}] (${printHelper_.outConLinkNodeName(uA)}) {};
\draw (${printHelper_.outConNodeName(uA)}) -- (${printHelper_.outConLinkNodeName(uA)});
%endif

%endfor


\renewcommand\placeRef{${stage.name}.south}
%for conMod in connectorModelList:
\input{../connectorModels/${conMod.name}.tex}
\let\oldConnectorModelOffset\connectorModelOffset
\renewcommand\connectorModelOffset{\oldConnectorModelOffset + \connectorModelHeight + \minStep}
%endfor
      
