# User

The frontend is supposed to be called from a root script.
To run the frontend stand-alone call the following from the m2isar_perf directory:
`python3 -m frontends.CorePerfDSL.run <path/to/the/CorePerfDSL/file>`

# Developer

## Setup
Useful aliases:
```
alias antlr4='java -Xmx500M -cp "/usr/local/lib/antlr-4.9-complete.jar:$CLASSPATH" org.antlr.v4.Tool'
alias javabuild ='javac -cp "/usr/local/lib/antlr-4.9-complete.jar:$CLASSPATH" *.java'
alias grun='java -Xmx500M -cp "/usr/local/lib/antlr-4.9-complete.jar:$CLASSPATH" org.antlr.v4.gui.TestRig'
```

## Build new grammar
`antlr4 -o parser_gen -listener -visitor -Dlanguage=Python3 CorePerfDSL.g4`

## View parser tree
```
antlr4 -o . -lib . -no-listener -no-visitor CorePerfDSL.g4
javabuild
grun CorePerfDSL description_context -gui ../../uArchs/SimpleRISCV/simpleRISCV.corePerfDSL
```

