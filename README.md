# M2-ISA-R-Perf
M2-ISA-R-Perf is a code generator for the SWEvalLib plugin library of ETISS. It main objectives are:
- Generating microarchitecture specific source files for the performance estimator backend (scheduling functions + timing variables)
- Generating matching monitor and channel source files to provide a matching instruction trace to the performance backend.

## Requirements
M2-ISA-R-Perf is developted for python3. It uses the Trace-Generator tool as a git-submodule.

## First Time Setup

### Create Workspace
Clone this repository and navigate to its top folder. (The given example uses an SSH-based link; adapt if necessary)

      $ git clone git@github.com:tum-ei-eda/M2-ISA-R-Perf.git <YOUR_WORKSPACE_NAME>
      $ cd <YOUR_WORKSPACE_NAME>

The current release version of M2-ISA-R-Perf is v1.0. Please switch to this tag:

      $ git fetch --tags
      $ git checkout tags/v1.0

Initialize required git-submodules:

	$ git submodule update --init --recursive

### Install Python requirements
Create a virtual Python evnironment and activate it:

       $ python3 -m venv venv
       $ source venv/bin/activate

Install Python dependencies:

	$ pip install -r requirements.txt

## Usage
Always make sure to run M2-ISA-R-Perf from within the virtual Python environment:

       $ source venv/bin/activate

Run the entire tool chain like this (e.g.):

    $ python m2isar_perf/run.py uArchs/SimpleRISCV/simpleRISCV.corePerfDSL -c [-i]

Use the help option to get an overview of supported input arguments:

    $ python m2isar_perf/run.py --help
