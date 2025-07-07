grammar CorePerfDSL;
top : (corePerfModel_sec
    | externModel_sec
    | instruction_sec
    )* EOF
;

corePerfModel_sec : virtual_def | connector_def | resource_def | microaction_def | stage_def | pipeline_def | variant_def | architecture_def;
externModel_sec : traceValue_def | connectorModel_def | resourceModel_def | model_def ;
instruction_sec : instrGroup_def | microactionMapping_def | traceValueMapping_def ;

//////////////////////////// CONNECTOR_MODEL ////////////////////////////
// NOTE: Replaced by generic MODEL. Kept for backwards compatibility

connectorModel_def : 'ConnectorModel' (connectorModel | '{' connectorModel (',' connectorModel)* '}');

connectorModel : name=ID '(' (
	      'trace' ':' (traceVals+=traceValue_ref | '{' traceVals+=traceValue_ref (',' traceVals+=traceValue_ref)* '}')
	      | 'link' ':' link=STRING
	      | 'connectorIn' ':' (inCons+=connector_ref | '{' inCons+=connector_ref (',' inCons+=connector_ref)* '}')
	      | 'connectorOut' ':' (outCons+=connector_ref | '{' outCons+=connector_ref (',' outCons+=connector_ref)* '}')
	      )* ')'
;

//////////////////////////// RESOURCE_MODEL ////////////////////////////
// NOTE: Replaced by generic MODEL. Kept for backwards compatibility

resourceModel_def : 'ResourceModel' (resourceModel | '{' resourceModel (',' resourceModel)* '}') ;

resourceModel : name=ID '(' (
	      'trace' ':' (traceVals+=traceValue_ref | '{' traceVals+=traceValue_ref (',' traceVals+=traceValue_ref)* '}')
	      | 'link' ':' link=STRING
	      )* ')'
;

//////////////////////////// MODEL ////////////////////////////
// NOTE: Generic MODEL replaced RESOURCE_MODEL and CONNECTOR_MODEL

model_def : 'Model' (model | model_list);

model_list : '{' model (',' model)* '}';

model : name=ID 
('[' attributes+=model_attr (',' attributes+=model_attr)* ']')? // Optional list of attributes
'(' (
      'link' ':' link=STRING
      | 'trace' ':' (traceVals+=traceValue_ref | '{' traceVals+=traceValue_ref (',' traceVals+=traceValue_ref)* '}')
      | 'connectorIn' ':' (inCons+=connector_ref | '{' inCons+=connector_ref (',' inCons+=connector_ref)* '}')
      | 'connectorOut' ':' (outCons+=connector_ref | '{' outCons+=connector_ref (',' outCons+=connector_ref)* '}')
)* ')'
;

model_attr : 'config' ;

//////////////////////////// TRACE_VALUE_MAPPING ////////////////////////////

traceValueMapping_def : 'TraceValueMapping' (traceValueMapping | '{' traceValueMapping (',' traceValueMapping)* '}') ;

traceValueMapping : instr=instructionOrInstrGroup_ref ':' ( trValAssign+=traceValue_assign | '{' trValAssign+=traceValue_assign (',' trValAssign+=traceValue_assign)* '}' );

//////////////////////////// TRACE_VALUE ////////////////////////////

traceValue_def : 'TraceValue' (traceValue | '{' traceValue (',' traceValue)* '}');

traceValue : name=ID ;

//////////////////////////// MICROACTION_MAPPING ////////////////////////////

microactionMapping_def : 'MicroactionMapping' (microactionMapping | '{' microactionMapping (',' microactionMapping)* '}' );

microactionMapping : instr=instructionOrInstrGroup_ref ':' (microactions+=microaction_ref | '{' microactions+=microaction_ref (',' microactions+=microaction_ref)* '}');

//////////////////////////// INSTRUCTION_GROUP ////////////////////////////

instrGroup_def : 'InstrGroup' (instrGroup | '{' instrGroup (',' instrGroup)* '}');

instrGroup : name=ID '(' instructions+=(ID|KEYWORD_REST) (',' instructions+=(ID|KEYWORD_REST))* ')';

//////////////////////////// ARCHITECTURE ////////////////////////////

architecture_def : 'Architecture' architecture;

architecture : '(' (
	     'name' ':' name=STRING
	     | 'isa' ':' isa=STRING
	     )* ')'
;

//////////////////////////// VARIANT ////////////////////////////

variant_def : 'Variant' (variant | variant_list);

variant_list : '{' variant (',' variant)* '}';

variant : name=ID '(' (
	      'use' 'Pipeline' ':' use_pipeline=pipeline_ref
	      | 'use' 'ConnectorModel' ':' (conModels+=model_ref | '{' conModels+=model_ref (',' conModels+=model_ref)* '}')
	      | 'assign' 'Resource' ':' (resAssigns+=resource_assign | '{' resAssigns+=resource_assign (',' resAssigns+=resource_assign)* '}')
	      | 'assign' 'Microaction' ':' (uActionAssigns+=microaction_assign | '{' uActionAssigns+=microaction_assign (',' uActionAssigns+=microaction_assign)* '}')
	      )* ')'
;

//////////////////////////// PIPELINE ////////////////////////////

pipeline_def : 'Pipeline' (pipeline |  pipeline_list);

pipeline_list : '{' pipeline (',' pipeline)* '}';

pipeline : name=ID // Pipeline name
('[' attribute=pipeline_attr ']')? // Attributes (optional)
'(' (sequentialComponentList=pipeline_sequential | parallelComponentList=pipeline_parallel) ')'; // Concatination of components (stages and/or (sub-)pipelines)

pipeline_sequential : components+=stageOrPipeline_ref ('->' components+=stageOrPipeline_ref)* ;

pipeline_parallel : components+=stageOrPipeline_ref '|' components+=stageOrPipeline_ref ('|' components+=stageOrPipeline_ref)* ;

pipeline_attr : 'blocks' ':' (blockPipelines+=pipeline_ref | '{' blockPipelines+=pipeline_ref (',' blockPipelines+=pipeline_ref)* '}');

//////////////////////////// STAGE ////////////////////////////

stage_def : 'Stage' (stage | stage_list);

stage_list : '{' stage (',' stage)* '}';

stage : name=ID // Stage name
('[' attributes+=stage_attr (',' attributes+=stage_attr)* ']')? // Optional list of attributes
'(' paths+=microactionOrPipeline_ref (',' paths+=microactionOrPipeline_ref)* ')';// List of microactions and/or (sub-)pipelines (required)

stage_attr : 'capacity' ':' capacity=INT
	   | 'output-buffer' ;

//////////////////////////// MICROACTION ////////////////////////////

microaction_def : 'Microaction' (microaction | '{' microaction (',' microaction)* '}');

microaction_list : '{' microaction (',' microaction)* '}';

microaction : name=ID '(' (
	    comps_1=microactionComponent
	    | comps_1=microactionComponent '->' comps_2=microactionComponent
	    | comps_1=microactionComponent '->' comps_2=microactionComponent '->' comps_3=microactionComponent
	    ) ')'
;

microactionComponent : ( singleComponent=resourceOrConnector_ref | multipleComponents=microactionComponent_list ) ;

microactionComponent_list : '{' refs+=resourceOrConnector_ref (',' refs+=resourceOrConnector_ref)* '}' ;

//////////////////////////// CONNECTOR ////////////////////////////

connector_def : 'Connector' (connector | '{' connector (',' connector)* '}');

connector : name=ID;

//////////////////////////// RESOURCE ////////////////////////////

resource_def : 'Resource' (resource | '{' resource_list '}');

resource_list : resource (',' resource)*;

resource : name=ID // Resource name
('(' (res_model=model_ref | delay=INT) ')')? ; // Delay specification (optional)

//////////////////////////// VIRTUAL ////////////////////////////

virtual_def: 'virtual' (type_='Resource' | type_='Microaction') (virtuals+=ID | '{' virtuals+=ID (',' virtuals+=ID)* '}');

//////////////////////////// ASSIGNMENTS ////////////////////////////

resource_assign: vir_res=resource_ref '=' nvir_res=resource_ref;

microaction_assign: vir_uA=microaction_ref '=' nvir_uA=microaction_ref;

traceValue_assign: trVal=traceValue_ref '=' description=STRING;

//////////////////////////// REFERENCES ////////////////////////////

connector_ref : name=ID ;

traceValue_ref : name=ID ; 

resourceModel_ref : name=ID ;

connectorModel_ref : name=ID ;

model_ref : name=ID;

resource_ref : name=ID ;

resourceOrConnector_ref : name=ID ;

microaction_ref : name=ID ;

//instruction_ref : name=(ID|KEYWORD_REST);

instructionOrInstrGroup_ref : name=(ID|KEYWORD_ALL) ;

stage_ref : name=ID ;

pipeline_ref : name=ID ;

microactionOrPipeline_ref : name=ID ;

stageOrPipeline_ref : name=ID ;

//////////////////////////// LEXER RULES ////////////////////////////

ID : [a-zA-Z] [a-zA-Z0-9_.]*  ;
INT : [0-9][0-9]* ;
STRING : '"' (~[\r\n"] | '\\"')* '"';

KEYWORD_ALL  : '[ALL]' ;
KEYWORD_REST : '[?]' ;

ML_COMMENT: '/*' .*? '*/' -> skip;
SL_COMMENT: '//' ~('\n'|'\r')* ('\r'? '\n')? -> skip;
WS: [ \t\r\n]+ -> skip;