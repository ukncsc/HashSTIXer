Copyright (c) 2016 Crown Copyright (CERT-UK)

Permission is hereby granted, free of charge, to use, copy, modify, merge, distribute and/or sub-licence the software together with any associated documentation provided that it is solely for your own internal use and subject to the following conditions:

(1) The above copyright notice and this permission notice shall be included in all copies or substantial portions of the software.

(2) THIS SOFTWARE IS PROVIDED "AS IS" WITHOUT ANY WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN ANY ACTION FOR CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# HashSTIXer

Python script to take a given file/folder and return a STIX package containing hash observables from each file.


## Features
- Calculates the following hash types:
  - MD5
  - SHA1
  - SHA256
  - SSDeep
- Takes either a single file or directory
- Adds a given indicated TTP
- Adds a given suggested COA


## Status
This script is at its initial stages and is therefore under active development.


## Setup
Before using the script you will need setup the config file with your own settings:

1. Make a copy of the `config.json.template` file and rename it to `config.json`.
2. Enter your own settings inside your `config.json` file.
  * The `coas` key defines any COAs you would like to relate to your ET object.
  * The `ttp` key defines if you want TTP objects to be built as part of the package.
  * The `stix` key defines your namespace and prefix.
  * The `ingest` key defines settings related to API ingestion.
  * The `buffer-size` key defines how much of each file is read at once.


## Usage
From a terminal/command prompt you can run the python script to get the usage statement.
```
$ python hashinator.py
[-] Please include an argument for the 'target' - a target file or directory to hash.
```

To generate a STIX hash indicator package of a single file:

```
$ python hashinator.py file.txt
```

To generate a STIX hash indicator package from a directory of files:

```
$ python hashinator.py /home/user/directory
```

## Example Output
An example output can be found in the [Example](Example-Package-8cb568f6-4744-4aae-b213-0cae2b0cbd82.xml) file.


## Dependencies
The script requires the following python modules:

- pydeep
- requests
- stix

### Installation

```
pip install -r requirements.txt
```
