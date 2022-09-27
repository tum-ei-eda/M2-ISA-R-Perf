grammar CorePerfDSL;
description_context : (corePerfModel_sec
		    | externModel_sec
		    | instruction_sec
		    )* EOF
;

corePerfModel_sec : virtual_def | connector_def | resource_def | microaction_def | stage_def | pipeline_def | corePerfModel_def ;
externModel_sec : traceValue_def | connectorModel_def | resourceModel_def ;
instruction_sec : instrGroup_def | microactionMapping_def | traceValueMapping_def ;

//////////////////////////// CONNECTOR_MODEL ////////////////////////////

connectorModel_def : 'ConnectorModel' (connectorModel | '{' connectorModel (',' connectorModel)* '}');

connectorModel : name=ID '(' (
	      'trace' ':' (traceVals+=traceValue_ref | '{' traceVals+=traceValue_ref (',' traceVals+=traceValue_ref)* '}')
	      | 'link' ':' link=FILE
	      | 'connectorIn' ':' (inCons+=connector_ref | '{' inCons+=connector_ref (',' inCons+=connector_ref)* '}')
	      | 'connectorOut' ':' (outCons+=connector_ref | '{' outCons+=connector_ref (',' outCons+=connector_ref)* '}')
	      )* ')'
;

//////////////////////////// RESOURCE_MODEL ////////////////////////////

resourceModel_def : 'ResourceModel' (resourceModel | '{' resourceModel (',' resourceModel)* '}') ;

resourceModel : name=ID '(' (
	      'trace' ':' (traceVals+=traceValue_ref | '{' traceVals+=traceValue_ref (',' traceVals+=traceValue_ref)* '}')
	      | 'link' ':' link=FILE
	      )* ')'
;

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

//instrGroup : name=ID '(' instructions+=ID (',' instructions+=ID)* ')';
instrGroup : name=ID '(' instructions+=(ID|KEYWORD_REST) (',' instructions+=(ID|KEYWORD_REST))* ')';

//////////////////////////// CORE_PERFORMANCE_MODEL ////////////////////////////

corePerfModel_def : 'CorePerfModel' (corePerfModel | '{' corePerfModel (',' corePerfModel)* '}');

corePerfModel : name=ID '(' (
	      'use' 'Pipeline' ':' use_pipeline=pipeline_ref
	      | 'use' 'ConnectorModel' ':' (conModels+=connectorModel_ref | '{' conModels+=connectorModel_ref (',' conModels+=connectorModel_ref)* '}')
	      | 'assign' 'Resource' ':' (resAssigns+=resource_assign | '{' resAssigns+=resource_assign (',' resAssigns+=resource_assign)* '}')
	      | 'assign' 'Microaction' ':' (uActionAssigns+=microaction_assign | '{' uActionAssigns+=microaction_assign (',' uActionAssigns+=microaction_assign)* '}')
	      )* ')'
;

//////////////////////////// PIPELINE ////////////////////////////

pipeline_def : 'Pipeline' (pipeline | '{' pipeline (',' pipeline)* '}');

pipeline : name=ID '(' stages+=stage_ref ('->' stages+=stage_ref)* ')';

//////////////////////////// STAGE ////////////////////////////

stage_def : 'Stage' (stage | '{' stage (',' stage)* '}');

stage : name=ID '(' microactions+=microaction_ref (',' microactions+=microaction_ref)* ')';

//////////////////////////// MICROACTION ////////////////////////////

microaction_def : 'Microaction' (microaction | '{' microaction (',' microaction)* '}');

microaction : name=ID '(' (
	    refs+=resourceOrConnector_ref
	    | refs+=resourceOrConnector_ref '->' refs+=resourceOrConnector_ref
	    | refs+=resourceOrConnector_ref '->' refs+=resourceOrConnector_ref '->' refs+=resourceOrConnector_ref
	    ) ')'
;

//////////////////////////// CONNECTOR ////////////////////////////

connector_def : 'Connector' (connector | '{' connector (',' connector)* '}');

connector : name=ID;

//////////////////////////// RESOURCE ////////////////////////////

resource_def : 'Resource' (resource | '{' resource (',' resource)* '}');

resource : 
    name=ID '(' res_model=resourceModel_ref ')' # resource_model
    | name=ID '(' delay=INT ')' # resource_delay
    | name=ID # resource_default
;

//////////////////////////// VIRTUAL ////////////////////////////

virtual_def: 'virtual' (type_='Resource' | type_='Microaction') (virtuals+=ID | '{' virtuals+=ID (',' virtuals+=ID)* '}');

//////////////////////////// ASSIGNMENTS ////////////////////////////

resource_assign: vir_res=resource_ref '=' nvir_res=resource_ref;

microaction_assign: vir_uA=microaction_ref '=' nvir_uA=microaction_ref;

traceValue_assign: trVal=traceValue_ref '=' '"' description=ID '"';

//////////////////////////// REFERENCES ////////////////////////////

connector_ref : name=ID ;

traceValue_ref : name=ID ; 

resourceModel_ref : name=ID ;

connectorModel_ref : name=ID ;

resource_ref : name=ID ;

resourceOrConnector_ref : name=ID ;

microaction_ref : name=ID ;

//instruction_ref : name=(ID|KEYWORD_REST);

instructionOrInstrGroup_ref : name=(ID|KEYWORD_ALL) ;

stage_ref : name=ID ;

pipeline_ref : name=ID ;

//////////////////////////// LEXER RULES ////////////////////////////

ID : [a-zA-Z] [a-zA-Z0-9_]*  ;
INT : [0-9][0-9]* ;
FILE : [a-zA-Z] [a-zA-Z0-9_./]*  ;

KEYWORD_ALL  : '[ALL]' ;
KEYWORD_REST : '[?]' ;

ML_COMMENT: '/*' .*? '*/' -> skip;
SL_COMMENT: '//' ~('\n'|'\r')* ('\r'? '\n')? -> skip;
WS: [ \t\r\n]+ -> skip;