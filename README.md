# tlmCleaner
![Version 0.8.0](https://img.shields.io/badge/version-0.8.0-blue?style=plastic)
![Language Python 3.12-1](https://img.shields.io/badge/python-3.12.1-orange?style=plastic&logo=python)

Remove duplicated packets from spacecraft telemtry comparing the Source Sequence Count and filter the packets by APID (Application Process IDentifier).

## Installing

You can install tlmCleaner in two different ways:

> [!NOTE]
> The installation using pip will be available soon

2. cloning the repository:

```console
git clone https://github.com/RomoloPoliti-INAF/tlmCleaner.git
cd tlmCleaner
python3 -m pip install -U .
```

3. directly from GitHub

```console
python3 -m pip install -U git+https://github.com/RomoloPoliti-INAF/tlmCleaner.git
```

## Usage

The standard usage is:

```console
Usage: tlmCleaner [OPTIONS] FILENAME   

Options:

 --output     -o  FILE     Output file
 --apids      -a  FILE     APID list
 --summarize  -s           Show packets information by APID
 --logFile    -l  LOGFILE  Name and location of the Log file
 --debug      -d           Enable 👉 debug mode 👈
 --verbose    -v           Enable 👉 verbose mode 👈 
 --version    -V           Show the version and exit.
 --help       -h           Show this message and exit.  
```

##  Example
For clean a telemetry file called *COM_Packets.xml* and filter the APID of the reports can use the syntax:

```console
tlmCleaner -a apid_Janus_Com.yml -sv COM_Packets.xml
````

where the file *apid_Janus_Com.yml* has the information reported [here](#com-report)

## APID Configuration examples

### BepiColombo SIMBIO-SYS

```yaml
apid801:
  apid: 801
  name: Telecommand
apid804:
  apid: 804
  name: Housekeeping
apid807:
  apid: 807
  name: Event_Report
apid809:
  apid: 809
  name: Memory_Management
apid828:
  apid: 828
  name: HRIC_Low_Priority
apid844:
  apid: 844
  name: STC_Low_Priority
apid860:
  apid: 860
  name: VIHI_Low_Priority
apid876:
  apid: 876
  name: HRIC_High_Priority
apid892:
  apid: 892
  name: STC_High_Priority
apid908:
  apid: 908
  name: VIHI_High_Priority
```

### JUICE JANUS
#### COM Report

```yaml
apid643:
  apid: 643
  name: COM_Report
```
