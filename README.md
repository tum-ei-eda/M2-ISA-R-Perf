# User

## First time setup
- Create virtual Python environment: `python3 -m venv venv`
- Activate the virtual envirinment: `source venv/bin/activate`
- Install Python dependencies: `pip install -r requirements.txt`

## Usage
- Make sure that the virtual Python environment is activated (`source venv/bin/activate`)
- Run the entire tool-chain:
  ```
  cd m2isar_perf/
  python3 run.py ../uArchs/SimpleRISCV/simpleRISCV.corePerfDSL ./SimpleRISCV -c -i
  ```
- Run help to get overview of supported input arguments:
  ```
  cd m2isar_perf/
  python3 run.py --help
  ```