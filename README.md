# M2-ISA-R-Perf
M2-ISA-R-Perf is a code generator for the SWEvalLib plugin library of ETISS. It main objectives are:
- Generating microarchitecture specific source files for the performance estimator backend (scheduling functions + timing variables)
- Generating matching monitor description (.json) for generation of monitor and channel source files (e.g. with M2ISAR) 

M2-ISA-R-Perf uses the CorePerfDSL description language as an input format. You can find example versions in the [CorePerfDSL-Examples](https://github.com/tum-ei-eda/CorePerfDSL-Examples) repository.

## First Time Setup

### Create Workspace
Clone this repository and navigate to its top folder. (The given example uses an SSH-based link; adapt if necessary)

      $ git clone git@github.com:tum-ei-eda/M2-ISA-R-Perf.git <YOUR_WORKSPACE_NAME>
      $ cd <YOUR_WORKSPACE_NAME>

Switch to the latest release version:

      $ git fetch --tags
      $ git checkout tags/v2.0

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

Run the entire tool chain like this:

    $ python m2isar_perf/run.py <path/to/corePerfDsl/description> [-c] [-i] [-m]

- c: Generate performance estimator source files
- i: Generate documentation
- m: Generate monitor description file

Use the help option to get an overview of supported input arguments:

    $ python m2isar_perf/run.py --help

## Version

The latest release version of this repository is v2.0.

This repository does not contain any submodules.

Version v2.0 is compatible with the following external repositories:

| Repository | Version |
| ---------- | ------- |
| CorePerfDSL-Example | v2.0 |
| SoftwareEvalLib | v2.0 |
| SoftwareEval-Backends | v2.0 |
| etiss-perf-sim | v0.10 |