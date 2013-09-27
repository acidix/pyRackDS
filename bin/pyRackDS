#!/usr/bin/env python -B

import ipaddress
import sys
import os
import inspect
import argparse
from threading import Thread
from Queue import Queue
from Cheetah.Template import Template

rackpath = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../python/lib/racktables")))
confpath = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../conf")))
sys.path.insert(0, rackpath)
sys.path.insert(0, confpath)
from client import *
from config import __config__

global rtHosts
global rtNetworks
global rtTags
global allNetworks
global allHosts
global allTags
global rtPool
rtPool = Queue()


class hostDetailAdder(Thread):
    """Extends host object information. Extends the threading.Thread
        module to be invoked in parallel.

    """

    def __init__(self, objectID):
        """Initialize the hostDetailAdder object.

        :param objectID: Object ID for which to collect information

        """
        super(hostDetailAdder, self).__init__()
        self._objectID = objectID

        rtPoolItem = rtPool.get()
        self._rtObjectDetail = rtPoolItem.get_object(objectID)
        rtPool.put(rtPoolItem)

    def run(self):
        """Start Thread of type hostDetailAdder.

        """
        self._network = self.getObjectNetworkDetails()
        self._tags = self.getObjectTagDetails()

    def getObjectNetworkDetails(self):
        """Get network tree for the given object.

        :returns: Dictionary with information about network ports

        """
        rtHostNetworkInfo = queryDict(self._rtObjectDetail["ports"],
            ( "id", "iif_name", "name", "l2address", "label" ))

        for key in [key for key in rtHostNetworkInfo]:
            targetkey = rtHostNetworkInfo[key]["name"]
            rtHostNetworkInfo[targetkey] = rtHostNetworkInfo.pop(key)

        for rtHostInfoIPv4 in self._rtObjectDetail["ipv4"].values():
            if rtHostInfoIPv4["osif"] not in rtHostNetworkInfo:
                return

            rtHostNetworkInfo[rtHostInfoIPv4["osif"]]["ip"] = ipaddress.ip_address(rtHostInfoIPv4["addrinfo"]["ip"])

        return rtHostNetworkInfo

    def getObjectTagDetails(self):
        """Get tag tree for the given object.

        :returns: Dictionary with tag information for the given object

        """
        rtHostTagInfo = {}
        rtHostTagInfoTemp = {}

        rtHostTagInfoTemp["other_tags"] = filter(lambda etag:
            not etag["parent_id"],
            self._rtObjectDetail["etags"].values() )

        for special_tag in __config__["tags"]["special_tags"]:
            parent = filter(lambda itag: itag["tag"] == special_tag,
                self._rtObjectDetail["itags"].values() )

            if len(parent) == 0 or len(parent) > 1:
                continue

            rtHostTagInfoTemp[special_tag] = filter(lambda etag:
                etag["parent_id"] == parent[0]["id"],
                    self._rtObjectDetail["etags"].values() )

        for tag_group in rtHostTagInfoTemp.keys():
            rtHostTagInfo[tag_group] = []
            [rtHostTagInfo[tag_group].append(x["tag"]) for x in rtHostTagInfoTemp[tag_group]]

        return rtHostTagInfo


class networkDetailAdder(Thread):
    """Adds details to the network tree. Extends the threading.Thread
        module to be invoked in parallel.

    """

    def __init__(self, objectID):
        """Initialize networkDetailAdder object.

        :param objectID: Object ID (network)

        """
        super(networkDetailAdder, self).__init__()
        self._objectID = objectID

    def run(self):
        """Start Thread of type networkDetailAdder.

        """
        self._network = ipaddress.ip_network(allNetworks[self._objectID]["ip"] + "/" + allNetworks[self._objectID]["mask"])
        self._hosts = self.getNetworkDetails()
        self._dottedMask = calcDottedNetmask(int(allNetworks[self._objectID]["mask"]))

    def getNetworkDetails(self):
        """Return detail information for the given network ID

        :returns: Dictionary with information pulled from RackTables

        """
        hostsInNet = []

        for host in allHosts.values():
            networkAddr = filter(lambda network: "ip" in network
                and ipaddress.ip_address(network["ip"]) in self._network,
                host["network"].values())

            if len(networkAddr) == 0:
                continue

            hostsInNet.append(networkAddr[0])

        return hostsInNet


class templateRunner(Thread):
    """Run cheetah templating engine for the given definition file

    """

    def __init__(self, templateFile, definitionFile):
        """Initialize object of type templateRunner

        :param templateFile: Path to template
        :param definitionFile: Path to definitino

        """
        super(templateRunner, self).__init__()
        self._templateFile = templateFile
        self._definitionFile = definitionFile
        self._definition = __import__(self._definitionFile.replace(".py"
            , "")).definition

    def run(self):
        """Start Thread of type templateRunner

        """
        burstMode = self._definition.get("burst", "none").lower()

        trigger = {   "none"    : self.runNoBurst,
                      "hosts"   : self.runHostBurst,
                      "networks": self.runNetworkBurst,
                      "tags"    : self.runTagBurst,
                      "tftp"    : self.runTftpBurst
                  }

        trigger[burstMode]()

    def runNoBurst(self):
        """Run template with bursting mode: none

        """
        renderedTemplate = Template( file = self._templateFile,
            searchList = [ {"allHosts" : allHosts},
                {"allNetworks" : allNetworks},
                {"allTags" : allTags} ] )
        if not "filename" in self._definition:
            self._definition["filename"] = os.path.basename(self._templateFile).split('.')[0]
        outfile = open(self._definition["outputdir"] +
            self._definition["filename"] +
            self._definition["extension"], "w")
        outfile.write(str(renderedTemplate))
        outfile.close()

    def runHostBurst(self):
        """Run template with bursting mode: host

        This loops through all entries in the allHosts object and runs
        the template with the host dictionary.

        """
        for host in allHosts.values():
            renderedTemplate = Template( file = self._templateFile,
                searchList = [ {"host" : host} ] )
            self._definition["filename"] = os.path.basename(self._templateFile).split('.')[0]
            outfile = open(self._definition["outputdir"] +
                host["name"] +
                self._definition["extension"], "w")
            outfile.write(str(renderedTemplate))
            outfile.close()

    def runNetworkBurst(self):
        """Run template with bursting mode: network

        This loops through all entries in the allNetworks object and
        runs the template with the network dictionary.

        """
        for network in allNetworks.values():
            renderedTemplate = Template( file = self._templateFile,
                searchList = [ {"network" : network} ] )
            outfile = open(self._definition["outputdir"] +
                network["name"] +
                self._definition["extension"], "w")
            outfile.write(str(renderedTemplate))
            outfile.close()

    def runTagBurst(self):
        """Run template with bursting mode: tag

        This loops through all entries in the allTags object and runs
        the template with the tag dictionary.

        """
        for tagidx, tag in allTags:
            renderedTemplate = Template( file = self._templateFile,
                searchList = [ {"tag" : tag} ] )
            outfile = open(self._definition["outputdir"] +
                tag["name"] +
                self._definition["extension"], "w")
            outfile.write(str(renderedTemplate))
            outfile.close()

    def runTftpBurst(self):
        """Run template with bursting mode: tftp

        This loops through all entries in the network part of each
        allHosts object and runs the template if either the netboot
        tag is set on the parent object or restrict_tftp is false
        in the global configuration.

        """

        def writeTftpFile(host):
            """Writes the tftp output file.

            :param host: Dictionary with host information.

            """
            for iface in host["network"].values():
                if not iface["mac"]:
                    continue
                renderedTemplate = Template( file = self._templateFile, searchList = [ {"iface" : iface},
                        {"host" : host} ] )
                outfile = open(outputdir +
                    iface["mac"].lower().replace(":", "-"), "w")
                outfile.write(str(renderedTemplate))
                outfile.close

        for host in allHosts.values():
            if __config__["tftp"]["netboot_tag"] in host["tags"]["other_tags"]:
                writeTftpFile(host)
            if not __config__["tftp"]["restrict_tftp"]:
                writeTftpFile(host)


def calcDottedNetmask(mask):
    """ Helper function to calculate a dotted netmask

    :param mask: Netmask in cidr notation
    :returns: Netmask in dot-decimal notation

    """
    bits = 0
    for i in xrange(32-mask,32):
        bits |= (1 << i)
    return "%d.%d.%d.%d" % ((bits & 0xff000000) >> 24,
        (bits & 0xff0000) >> 16, (bits & 0xff00) >> 8 , (bits & 0xff))


def queryDict(data, wanted):
    """Return a subset of leafs in a dictionary. Example:

    mydict {
        "member 1": {
            "attribute 1": "value 1",
            "attribute 2": "value 2"
        }
    }

    querydict(mydict, ("attribute 1")) will return:

    mydict {
        "member 1": {
            "attribute 1": "value 1",
        }
    }


    :param data: Source dictionary
    :param wanted: Child leafs to be returned
    :returns: Dictionary with selected leaf entries

    """
    result = {}
    for k, v in data.items():
        v2 = { k2:v[k2] for k2 in wanted if k2 in v }
        if v2:
            result[k] = v2
    return result


def createRtWorker(QueueObj, items=5):
    """Create workers of type RacktablesClient

    :param QueueObj: Object queue to add the worker to
    :param items: Number of items to add to the queue

    """
    def createWorker(QueueObj):
        rtClient = RacktablesClient(__config__["racktables"]["apiurl"],
            __config__["racktables"]["username"],
            __config__["racktables"]["password"])
        QueueObj.put(rtClient)

    threads = []
    for x in range(0,items):
        logging.debug("Adding RT worker %s" % str(x))
        thread = Thread(target=createWorker, args=(QueueObj,))
        threads.append(thread)

    for t in threads:
        t.start()

    for t in threads:
        t.join()


def initRtTrees():
    """Initalizes the global Racktables trees rtHosts, rtNetworks and
        rtTags

    """
    global rtHosts, rtNetworks, rtTags
    rtPoolItem = rtPool.get()

    rtHosts = rtPoolItem.get_objects()
    rtNetworks = rtPoolItem.get_ipv4space()
    rtTags = rtPoolItem.get_tags(True)

    rtPool.put(rtPoolItem)


def addObjectDetails():
    """Adds details to the allHosts tree by invoking hostDetailAdder
        for each leaf of allHosts.

    """
    threads = []
    for host in allHosts.values():
        thread = hostDetailAdder(host["id"])
        threads.append(thread)

    for t in threads:
        t.start()

    for t in threads:
        t.join()
        allHosts[t._objectID]["network"] = t._network
        allHosts[t._objectID]["tags"] = t._tags


def addNetworkDetails():
    """Adds details to the allNetworks tree by invoking
        networkDetailAdder for each leaf of the allNetworks tree.

    """
    threads = []
    for net in allNetworks.values():
        thread = networkDetailAdder(net["id"])
        threads.append(thread)

    for t in threads:
        t.start()

    for t in threads:
        t.join()
        allNetworks[t._objectID]["hosts"] = t._hosts
        allNetworks[t._objectID]["dottedMask"] = t._dottedMask
        allNetworks[t._objectID]["network"] = t._network


def getTags(tagDict):
    """Builds the allTags tree from the tagDict parameter.

    :param tagDict: Source dictionary containing tags (fed from
        Racktables)
    :returns: Dictionary containing a hierarchical tag tree.

    """
    retDict = queryDict(tagDict, ( "id", "is_assignable", "parent_id", "tag" ) )

    for idx in [idx for idx in tagDict]:
        if tagDict[idx]["kidc"] == "0":
            continue
        retDict[idx]["kids"] = getTags(tagDict[idx]["kids"])

    for idx in [idx for idx in tagDict]:
        retDict[tagDict[idx]["tag"]] = retDict.pop(idx)

    return retDict


def runTemplates(_templatedir, _definitiondir):
    """Runs all templates in the definitions folder by invoking
        templateRunner on each file found.

    :param _templatedir: Directory to scan for templates
    :param _definitinodir: Directory to scan for definitions
    :returns: Dictionary with information pulled from RackTables

    """
    sys.path.insert(0, _definitiondir)
    threads = []
    for _definition in os.listdir(_definitiondir):
        template = _templatedir + "/" + _definition.replace(".py", ".tmpl")
        thread = templateRunner(template, _definition)
        threads.append(thread)

    [t.start() for t in threads]
    [t.join() for t in threads]

def runSingleTemplate(_templatedir, _definitiondir, _template):
    sys.path.insert(0, _definitiondir)
    template = _templatedir + "/" + _template + ".tmpl"
    definition = _template + ".py"
    thread = templateRunner(template, definition)
    thread.start()
    thread.join()


def main():
    """Main function
    """
    global allNetworks,allHosts, allTags

    parser = argparse.ArgumentParser(prog="pyRackDS")
    parser.add_argument('-v', '--verbose',action="store_true",
                        help="Increase output verbosity.")
    parser.add_argument('-a', '--all',action="store_true",
                        help="Run all templates (default).")
    parser.add_argument('-H', '--host',action="store_true",
                        help="Output host tree.")
    parser.add_argument('-N', '--network',action="store_true",
                        help="Output network tree.")
    parser.add_argument('-T', '--tag',action="store_true",
                        help="Output tag tree.")
    parser.add_argument('-t', '--template',type=str,
                        help="Only process this template.")
    args = parser.parse_args()

    _templatedir = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../templates.d")))
    _definitiondir = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../definitions.d")))

    createRtWorker(rtPool, __config__["racktables"]["worker"])

    initRtTrees()

    allNetworks = queryDict(rtNetworks, ( "id", "ip", "mask", "name", "comment" ) )
    allHosts = queryDict(rtHosts, ( "id", "name", "dname", "label", "objtype_id", "comment") )
    allTags = getTags(rtTags)

    addObjectDetails()
    addNetworkDetails()

    if args.host:
        pprint.pprint(allHosts)
        sys.exit(0)
    if args.network:
        pprint.pprint(allNetworks)
        sys.exit(0)
    if args.tag:
        pprint.pprint(allTags)
        sys.exit(0)
    if args.template:
        for _template in args.template.split(","):
            runSingleTemplate(_templatedir, _definitiondir, _template)
        sys.exit(0)

    runTemplates(_templatedir, _definitiondir)


if __name__ == "__main__":
    main()

