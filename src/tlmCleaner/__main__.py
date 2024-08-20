#!/usr/bin/env python3
#
# tlmClean
# Version 0.8.0
#
# History:
# [2024-01-06] [Version 0.8.0] - Stand alone version
# [2023-12-05] [Version 0.7.0] - introduced the customize log class
# [2023-10-09] [Version 0.6.0] - integration with version 2.1.0
#                              - switch to rich-click
# [2022-04-06] [Version 0.5.0] integration with version 2.0.0
# [2021-01-05] [V.0.4.0] move to Python 3


import xml.etree.ElementTree as ET
from pathlib import Path
from shutil import rmtree

import rich_click as click
from MyCommonLib import (CONTEXT_SETTINGS, FMODE, MSG, Vers, progEpilog,
                         progresSet, read_yaml)
from rich.panel import Panel
from rich.progress import Progress
from rich.table import Table
from SCOS.SCOS import *

from tlmCleaner.configure import conf

# from progress.bar import Bar

__version__ = Vers((0, 9, 0, 'f', 1)).full()

click.rich_click.USE_RICH_MARKUP = True
click.rich_click.FOOTER_TEXT = progEpilog
click.rich_click.HEADER_TEXT = f"Telemetry Cleaner, version [blue]{
    __version__}[/blue]"

# Panel color Setup
class COLOR:
    console = 'dodger_blue3'
    error = 'red'
    panel = 'yellow'


def do_it(ctx, param, value):
    """Callback for the creation of a folder.
    If it exists and is not empty it will be deleted and recreated
    """
    value = Path(value)
    if value.exists():
        is_full = bool({_ for _ in value.rglob('*')})
        if is_full:
            rmtree(value)
            value.mkdir()
    else:
        value.mkdir(parents=True)
    return value

def mkTmpFolder(tp=None):
    message = "Creating the folder"
    if tp is None:

        conf.log.info(f"{message} {conf.tmp}", verbosity=2)
        conf.tmp.mkdir(parents=True, exist_ok=True)
    else:
        conf.log.info(
            f"{message} {conf.tmp.joinpath(tp).as_posix()}", verbosity=2)
        do_it(None, None, conf.tmp.joinpath(tp))


class ApidList:
    def __init__(self,apidList:dict, pt) -> None:
        for item in apidList:
            setattr(self, item, apid(apidList[item]['name'], apidList[item]['apid'], pt))
        # self.apid801 = apid("Telecommand", 801, pt)
        # self.apid804 = apid("Housekeeping", 804, pt)
        # self.apid807 = apid("Event_Report", 807, pt)
        # self.apid809 = apid("Memory_Management", 809, pt)
        # self.apid828 = apid("HRIC_Low_Priority", 828, pt)
        # self.apid876 = apid("HRIC_High_Priority", 876, pt)
        # self.apid844 = apid("STC_Low_Priority", 844, pt)
        # self.apid892 = apid("STC_High_Priority", 892, pt)
        # self.apid860 = apid("VIHI_Low_Priority", 860, pt)
        # self.apid908 = apid("VIHI_High_Priority", 908, pt)

    def check(self, pk, id):
        name = f"apid{pk.TMPH.PUSAPID}"
        if not name in self.__dict__:
            # if the APID is not in the list, the packet is not saved
            return False
        retVal = getattr(self, f"apid{pk.TMPH.PUSAPID}").check(pk, id)
        return retVal
        # ck.check(pk,id)

    def summarize(self):
        for k in self.__dict__:
            if k.startswith("apid"):
                getattr(self, k).summarize()

    def kill(self):
        for k in self.__dict__:
            if k.startswith("apid"):
                getattr(self, k).kill()


class apid():
    def __init__(self, name, apid, pt):
        self.lastSSC = None
        self.lastSCET = None
        self.listSSC = []
        self.listXMLid = []
        self.XMLidTotal = []
        self.flag = []
        self.name = name
        self.apid = apid
        self.outpath = pt
        if not Path(self.outpath).exists():
            mkTmpFolder(tp=self.outpath)
        self.fileid = open(self.outpath.joinpath(self.fname()), FMODE.WRITE)
        self.fileid.write("FillingTime,SSC,XMLCount\n")

    def kill(self):
        self.fileid.close()
        if len(self.listSSC) == 0:
            self.outpath.joinpath(self.fname()).unlink()
        del self

    def check(self, pk, id):
        self.XMLidTotal.append(id)
        if (self.lastSSC == None) or (self.lastSSC != pk.TMPH.PUSSSC):
            self.lastSSC = pk.TMPH.PUSSSC
            self.lastSCET = pk.CPH.FilingTime
            self.listSSC.append(pk.TMPH.PUSSSC)
            self.listXMLid.append(id)
            self.fileid.write("{},{},{}\n".format(
                pk.CPH.FilingTime, pk.TMPH.PUSSSC, id))
            return True

    def summarize(self):
        table = Table.grid()
        table.add_column(style='green')
        table.add_column()
        table.add_column()
        table.add_row("APID", "   ", f"{self.apid}")
        table.add_row("Name", "   ", f"{self.name}")
        if len(self.listSSC) != 0:
            table.add_row("Total Packets", "   ", f"{len(self.XMLidTotal)}")
            table.add_row("Saved Packets", "   ", f"{len(self.listSSC)}")
            table.add_row("Output File", "   ", f"{self.fname()}")
        else:
            table.add_row("No data found", "   ", "")
        conf.console.print(Panel(table, title=self.name.replace(
            '_', ' '), border_style=COLOR.panel, expand=False))

    def fname(self):
        return self.name+'.csv'

    def pprint(self):
        return


def tlmClean(fileName: Path, output: str = None, apidList:dict=None, extern: Path = None,
             summarize: bool = False):

    # if not log:
    #     log = logInit(logFile, 'SIMBIO-SYS clean', logging.INFO, FMODE.WRITE)
    # if debug:
    #     log.setLevel(logging.DEBUG)
    conf.log.info("Start tlmClean")
    if not fileName.exists():
        conf.log.critical("The file {fileName} not exists")
        raise SystemExit(1)


    conf.log.info(f"Reading the input file ({fileName})", verbosity=1)

    myDoc = ET.parse(fileName)
    root = myDoc.getroot()
    ET._namespace_map['http://edds.egos.esa/model'] = 'ns2'
    if extern == None:
        extern = Path("./tmp/clean").expanduser()
        if not extern.exists():
            extern.mkdir(parents=True)
    if conf.debug:
        conf.console.print(f"{MSG.DEBUG}External Path: {extern}")
    top = ET.Element("{http://edds.egos.esa/model}ResponsePart")
    outRoot = ET.ElementTree(top)
    child1 = ET.SubElement(top, 'Response')
    child2 = ET.SubElement(child1, 'PktRawResponse')
    ap = ApidList(apidList,extern)
    with Progress(*progresSet, console=conf.console) as progr:

        taskClean = progr.add_task("Processing Packets: ", total=len(
            myDoc.findall('.//PktRawResponseElement')))
        for packet in root.iter('PktRawResponseElement'):
            p1 = SCOS(packet[0].text)
            if ap.check(p1, packet.attrib['packetID']):
                child2.append(packet)
            progr.update(taskClean, advance=1)

    if output == None:
        temp = Path(fileName)
        output = f"{temp.parent}/{temp.stem}_cl{temp.suffix}"

    
    conf.log.info(f"Writing the output file {output}", verbosity=1)

    outRoot.write(output, encoding='utf-8', xml_declaration=True)

    if summarize:
        ap.summarize()
    ap.kill()
    conf.log.info("End tlmClean", verbosity=1)
    return output


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('fileName')
@click.option('-o', '--output', metavar='FILE', help="Output file", default="output.xml")
@click.option('-a', '--apids', metavar='FILE', help="APID list", default='apids.yml')
@click.option('-s', '--summarize', is_flag=True, help="Show packets information by APID", default=False)
# @click.option('-c', '--config', metavar='FILE', help='Use a specific configuration file', default=None)
@click.option('-l', '--logFile', 'logFile', metavar="LOGFILE", help="Name and location of the Log file", default=None)
@click.option('-d', '--debug', is_flag=True,
              help="Enable :point_right: [yellow]debug mode[/yellow] :point_left:", default=False)
@click.option('-v', '--verbose', count=True, metavar="", help="Enable :point_right: [yellow]verbose mode[/yellow] :point_left:", default=0)
@click.version_option(__version__, '-V', '--version')
def action(filename: Path, output: str, apids:Path,  summarize: bool,  logFile: Path, debug: bool = False, verbose: int = 0):
    """Telemetry Filter"""
    fileName = Path(filename)
    
    
    if type(logFile) is str:
        logFile = Path(logFile).expanduser()
    output = Path(output).expanduser()
    conf._logger = 'TLMClean'
    if logFile is not None:
        conf.setLog(logFile)
    conf.start_log()
    if isinstance(apids, str):
        apids = Path(apids)
    if not apids.exists():
        conf.log.critical(f"The file {apids} not exists")
        exit(1)
    else:
       apidList=read_yaml(apids)
    
    # Code block used to read the configuration file. Actually disabled
    # if config is not None:
    #     if type(config) is str:
    #         config = Path(config).expanduser()
    #     ret = conf.read_file_base(config)
    conf.debug = debug
    conf.verbose = verbose
    tlmClean(fileName, output, apidList, summarize=summarize)

    pass


if __name__ == "__main__":
    action()
