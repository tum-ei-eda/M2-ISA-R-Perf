\newcommand\minStep{0.2cm}

\newcommand\connectorSize{1cm}
\newcommand\connectorOffset{1.75cm}

\newcommand\resourceHeight{\connectorSize}
\newcommand\resourceWidth{2cm}

\newcommand\microactionWidth{2*(\minStep + \connectorSize + \connectorOffset)}
\newcommand\microactionHeight{1.55cm}

\newcommand\stageWidth{\microactionWidth + 2*(\minStep)}
\newcommand\stageTitleHeight{1cm}
\newcommand\stageHeight{\stageTitleHeight + \minStep + ${maxNumMicroactions}*(\minStep + \microactionHeight)}

\newcommand\pipelineWidth{\minStep + ${numStages}*(\stageWidth + \minStep) + ${numConnectorLinks}*\minStep}
\newcommand\pipelineTitleHeight{1cm}
\newcommand\pipelineHeight{2*\pipelineTitleHeight + \stageHeight}

\newcommand\connectorModelWidth{4cm}
\newcommand\connectorModelHeight{1.55cm}

\newcommand\coreWidth{\pipelineWidth + 2*\minStep}
\newcommand\coreTitleHeight{1cm}
\newcommand\coreHeight{\coreTitleHeight + \pipelineHeight + ${numConnectorModels}*(\connectorModelHeight + \minStep) + \minStep}

%% NOTE: Following commands are overwritten by other files
\newcommand\placeRef{(0,0)}
\newcommand\connectorModelOffset{\pipelineTitleHeight + \minStep}
\newcommand\connectorLinkSpace{\minStep}	
\newcommand\connectorLinkOffsetBase{2*\minStep}
\newcommand\connectorLinkOffset{\connectorLinkOffsetBase}

\tikzstyle{resource} = [draw,
minimum width = \resourceWidth,
minimum height = \resourceHeight
]

\tikzstyle{connector} = [draw,
circle,
minimum size = \connectorSize
]

\tikzstyle{microaction} = [draw,
minimum width = \microactionWidth,
minimum height = \microactionHeight
]

\tikzstyle{stage} = [draw,
minimum width = \stageWidth,
minimum height = \stageHeight
]

\tikzstyle{pipeline} = [draw,
minimum width = \pipelineWidth,
minimum height = \pipelineHeight
]

\tikzstyle{connectorModel} = [draw,
minimum width = \connectorModelWidth,
minimum height = \connectorModelHeight
]

\tikzstyle{core} = [draw,
minimum width = \coreWidth,
minimum height = \coreHeight
]