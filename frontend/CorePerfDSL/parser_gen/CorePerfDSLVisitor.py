# Generated from CorePerfDSL.g4 by ANTLR 4.9
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .CorePerfDSLParser import CorePerfDSLParser
else:
    from CorePerfDSLParser import CorePerfDSLParser

# This class defines a complete generic visitor for a parse tree produced by CorePerfDSLParser.

class CorePerfDSLVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by CorePerfDSLParser#description_context.
    def visitDescription_context(self, ctx:CorePerfDSLParser.Description_contextContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#corePerfModel_sec.
    def visitCorePerfModel_sec(self, ctx:CorePerfDSLParser.CorePerfModel_secContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#externModel_sec.
    def visitExternModel_sec(self, ctx:CorePerfDSLParser.ExternModel_secContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#instruction_sec.
    def visitInstruction_sec(self, ctx:CorePerfDSLParser.Instruction_secContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#connectorModel_def.
    def visitConnectorModel_def(self, ctx:CorePerfDSLParser.ConnectorModel_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#connectorModel.
    def visitConnectorModel(self, ctx:CorePerfDSLParser.ConnectorModelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#resourceModel_def.
    def visitResourceModel_def(self, ctx:CorePerfDSLParser.ResourceModel_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#resourceModel.
    def visitResourceModel(self, ctx:CorePerfDSLParser.ResourceModelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#traceValue_def.
    def visitTraceValue_def(self, ctx:CorePerfDSLParser.TraceValue_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#traceValue.
    def visitTraceValue(self, ctx:CorePerfDSLParser.TraceValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#microactionMapping_def.
    def visitMicroactionMapping_def(self, ctx:CorePerfDSLParser.MicroactionMapping_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#microactionMapping.
    def visitMicroactionMapping(self, ctx:CorePerfDSLParser.MicroactionMappingContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#instrGroup_def.
    def visitInstrGroup_def(self, ctx:CorePerfDSLParser.InstrGroup_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#instrGroup.
    def visitInstrGroup(self, ctx:CorePerfDSLParser.InstrGroupContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#corePerfModel_def.
    def visitCorePerfModel_def(self, ctx:CorePerfDSLParser.CorePerfModel_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#corePerfModel.
    def visitCorePerfModel(self, ctx:CorePerfDSLParser.CorePerfModelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#pipeline_def.
    def visitPipeline_def(self, ctx:CorePerfDSLParser.Pipeline_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#pipeline.
    def visitPipeline(self, ctx:CorePerfDSLParser.PipelineContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#stage_def.
    def visitStage_def(self, ctx:CorePerfDSLParser.Stage_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#stage.
    def visitStage(self, ctx:CorePerfDSLParser.StageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#microaction_def.
    def visitMicroaction_def(self, ctx:CorePerfDSLParser.Microaction_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#microaction_single_arg.
    def visitMicroaction_single_arg(self, ctx:CorePerfDSLParser.Microaction_single_argContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#microaction_double_arg.
    def visitMicroaction_double_arg(self, ctx:CorePerfDSLParser.Microaction_double_argContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#microaction_triple_arg.
    def visitMicroaction_triple_arg(self, ctx:CorePerfDSLParser.Microaction_triple_argContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#connector_def.
    def visitConnector_def(self, ctx:CorePerfDSLParser.Connector_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#connector.
    def visitConnector(self, ctx:CorePerfDSLParser.ConnectorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#resource_def.
    def visitResource_def(self, ctx:CorePerfDSLParser.Resource_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#resource_model.
    def visitResource_model(self, ctx:CorePerfDSLParser.Resource_modelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#resource_delay.
    def visitResource_delay(self, ctx:CorePerfDSLParser.Resource_delayContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#resource_default.
    def visitResource_default(self, ctx:CorePerfDSLParser.Resource_defaultContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#virtual_def.
    def visitVirtual_def(self, ctx:CorePerfDSLParser.Virtual_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#virtual.
    def visitVirtual(self, ctx:CorePerfDSLParser.VirtualContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#instruction_ref.
    def visitInstruction_ref(self, ctx:CorePerfDSLParser.Instruction_refContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#connector_ref.
    def visitConnector_ref(self, ctx:CorePerfDSLParser.Connector_refContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#traceValue_ref.
    def visitTraceValue_ref(self, ctx:CorePerfDSLParser.TraceValue_refContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#resourceModel_ref.
    def visitResourceModel_ref(self, ctx:CorePerfDSLParser.ResourceModel_refContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#connectorModel_ref.
    def visitConnectorModel_ref(self, ctx:CorePerfDSLParser.ConnectorModel_refContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#resource_ref.
    def visitResource_ref(self, ctx:CorePerfDSLParser.Resource_refContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#virResource_ref.
    def visitVirResource_ref(self, ctx:CorePerfDSLParser.VirResource_refContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#nonVirResource_ref.
    def visitNonVirResource_ref(self, ctx:CorePerfDSLParser.NonVirResource_refContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#resourceOrConnector_ref.
    def visitResourceOrConnector_ref(self, ctx:CorePerfDSLParser.ResourceOrConnector_refContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#microaction_ref.
    def visitMicroaction_ref(self, ctx:CorePerfDSLParser.Microaction_refContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#virMicroaction_ref.
    def visitVirMicroaction_ref(self, ctx:CorePerfDSLParser.VirMicroaction_refContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#nonVirMicroaction_ref.
    def visitNonVirMicroaction_ref(self, ctx:CorePerfDSLParser.NonVirMicroaction_refContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#instructionOrInstrGroup_ref.
    def visitInstructionOrInstrGroup_ref(self, ctx:CorePerfDSLParser.InstructionOrInstrGroup_refContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#stage_ref.
    def visitStage_ref(self, ctx:CorePerfDSLParser.Stage_refContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CorePerfDSLParser#pipeline_ref.
    def visitPipeline_ref(self, ctx:CorePerfDSLParser.Pipeline_refContext):
        return self.visitChildren(ctx)



del CorePerfDSLParser