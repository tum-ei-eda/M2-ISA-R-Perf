#!/usr/bin/env python3

import argparse
import pathlib
import sys
import pickle

import antlr4
from .parser_gen import CorePerfDSLLexer
from .parser_gen import CorePerfDSLParser

from .ModelGen import ModelGen

def main(description_, outdir_=None):

    # Find pathes for description and output-directory
    description = pathlib.Path(description_).resolve()
    if outdir_ is not None:
        outdir = pathlib.Path(outdir_).resolve()
    else:
        outdir = None
        
    # Create parse-tree from description file
    print("")
    print("-- Generating parser tree --")
    lexer = CorePerfDSLLexer(antlr4.FileStream(description))
    stream = antlr4.CommonTokenStream(lexer)
    parser = CorePerfDSLParser(stream)
    tree = parser.description_context()

    # Use parse tree for model-2-model transformation according to meta-model
    print("")
    print("-- Generating model --")
    modelGen = ModelGen()
    modelGen.extractInstances(tree)
    top = modelGen.buildModel()

    # If outdir is set, dump top-model to file
    if outdir is not None:
        print("")
        print("-- Storing model --")
        print("Out-directory: %s" %outdir)

        # Creating out-directory
        pathlib.Path(outdir).mkdir(parents=True, exist_ok=True)

        # Make path for out-file
        outfile_name = 'frontend.model'
        outfile = outdir / outfile_name
        print("File: %s" % outfile_name)
        if outfile.is_file():
            print("\tFile exists and will be replaced!")
            # TODO: Add possibility for user to aboard overwrite?
            
        # Dump model to file
        with outfile.open('wb') as f:
            pickle.dump(top, f)
        
    return top

# Run this if frontend is called stand-alone (i.e. this file is directly called)
if __name__ == '__main__':

    # Parse command line arguments
    argParser = argparse.ArgumentParser()
    argParser.add_argument("description", help="File containing the CorePerfDSL description.")
    argParser.add_argument("-o", "--output_dir", help="Directory to store generated model.")
    args = argParser.parse_args()
    
    main(args.description, args.output_dir)
    
