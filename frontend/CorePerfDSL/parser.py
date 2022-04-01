#!/usr/bin/env python3

import argparse
import pathlib
import sys

import antlr4
from parser_gen import CorePerfDSLLexer
from parser_gen import CorePerfDSLParser

from Extractor import Extractor
from GraphRewriter import GraphRewriter

# TODO: Helper/debug function. Remove
def print_instr_list(instr_list):

    for instr in instr_list:
        print(instr.name, end='')
        print(": ", end='')
        for uA in instr.microactions:
            print("%s, " % uA.name, end='')
        print("")

# TODO: Helper/debug function. Remove
def print_pipeline(model):

    pipeline = model.pipeline
    
    header_str = ""
    pipeline_str = []
    pipeline_num = []

    for st in pipeline.stages:
        header_str += '{0: <14}'.format(st.name) + '{0: >14}'.format("  |")

        stage_str = []
        stage_num = 0

        for uA in st.microactions:
            new_str = ""
            if(uA.inConnector is not None):
                in_str = uA.inConnector.name
            else:
                in_str = " [ ] "
            new_str += '{0: <5}'.format(in_str)
            new_str += " -> "
            if(uA.resource is not None):
                r_str = uA.resource.name
            else:
                r_str = "  [  ]  "
            new_str += '{0: <8}'.format(r_str)
            new_str += " -> "
            if(uA.outConnector is not None):
                out_str = uA.outConnector.name
            else:
                out_str = " [ ] "
            new_str += '{0: <5}'.format(out_str)
            stage_str.append(new_str)
            stage_num += 1

        pipeline_str.append(stage_str)
        pipeline_num.append(stage_num)

    print("--------------------------------------------------------------------------------------------------------------------------------------------")
    print("Model: %s" % model.name)
    print("Pipeline: %s" % pipeline.name)
    print(header_str)
    finished = False
    cnt = 0
    while not finished:
        finished = True
        for i,st in enumerate(pipeline_str):
            if(cnt < pipeline_num[i]):
                finished = False
                print(st[cnt], "|", end='')
            else:
                print('{0: >28}'.format("|"), end='')
        print("")
        cnt += 1
    print("--------------------------------------------------------------------------------------------------------------------------------------------")
               
def main():

    # Import command line arguments
    argParser = argparse.ArgumentParser()
    argParser.add_argument("top_level", help="The top-level CorePerfDSL file.")
    args = argParser.parse_args()

    # Find top-level file (abs path)
    abs_top_level = pathlib.Path(args.top_level).resolve()

    print("")
    print("-- Generating parser tree --")
    lexer = CorePerfDSLLexer(antlr4.FileStream(abs_top_level))
    stream = antlr4.CommonTokenStream(lexer)
    parser = CorePerfDSLParser(stream)
    tree = parser.description_context()

    print("")
    print("-- Extracting hierachical description --")

    extractor = Extractor()
    description = extractor.extract(tree)

    print("")
    print("-- Rewriting graph --")

    rewriter = GraphRewriter(description)
    rewriter.mapInstructions()    
    rewriter.extractModelTrees()
    
    print_instr_list(rewriter.modelTrees[0].instructionSet)
    print_instr_list(rewriter.modelTrees[1].instructionSet)
    
    #rewriter = GraphRewriter(description)
    #rewriter.generateInstrList()
    #
    #rewriter.extractModelTrees()
    
    #print_instr_list(description.instructionList)
    #                 
    ##print_pipeline(model_0)
    #print("")
    #print("")
    #print_instr_list(model_1.instrList)
    ##print_pipeline(model_1)
    
if __name__ == '__main__':
    main()
