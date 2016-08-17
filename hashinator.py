import datetime
import hashlib
import os
import sys
from config import setting
from itertools import izip_longest

import magic
import pydeep
import requests
from cybox.common import Hash
from cybox.core import Observable
from cybox.objects.file_object import File
from stix.coa import CourseOfAction
from stix.common.kill_chains.lmco import PHASE_DELIVERY
from stix.core import STIXHeader, STIXPackage
from stix.data_marking import Marking, MarkingSpecification
from stix.extensions.marking.simple_marking import SimpleMarkingStructure
from stix.extensions.marking.tlp import TLPMarkingStructure
from stix.indicator import Indicator
from stix.ttp import TTP

SETTINGS = setting("config.json")
BUF_SIZE = SETTINGS['buffer_size']


def _construct_headers():
    headers = {
        'Content-Type': 'application/xml',
        'Accept': 'application/json'
    }
    return headers


def _inbox_package(endpoint_url, stix_package):
    data = stix_package
    headers = _construct_headers()
    response = requests.post(endpoint_url, data=data, headers=headers)

    print("HTTP status: %d %s") % (response.status_code, response.reason)
    return


def _custom_namespace(url, alias):
    try:
        from stix.utils import set_id_namespace
        namespace = {url: alias}
        set_id_namespace(namespace)
    except ImportError:
        from mixbox.namespaces import Namespace
        from stix.utils import idgen
        namespace = Namespace(url, alias, "")
        idgen.set_id_namespace(namespace)


def _marking():
    """Define the TLP marking and the inheritance."""
    marking_specification = MarkingSpecification()
    tlp = TLPMarkingStructure()
    tlp.color = SETTINGS['stix']['tlp']
    marking_specification.marking_structures.append(tlp)
    marking_specification.controlled_structure = SETTINGS[
        'stix']['controlled_structure']
    simple = SimpleMarkingStructure()
    simple.statement = SETTINGS['stix']['statement']
    marking_specification.marking_structures.append(simple)
    handling = Marking()
    handling.add_marking(marking_specification)
    return handling


def hashfile(path, targetfile):
    '''This function returns a hash from a given file.'''
    md5 = hashlib.md5()
    sha1 = hashlib.sha1()
    sha256 = hashlib.sha256()
    sha512 = hashlib.sha512()
    fullfile = path + "/" + targetfile
    with open(fullfile, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)
            sha1.update(data)
            sha256.update(data)
            sha512.update(data)
            hdict = {
                'fileformat': magic.from_file(fullfile, mime=True),
                'filename': str(targetfile),
                'filesize': os.path.getsize(fullfile),
                'md5': md5.hexdigest(),
                'sha1': sha1.hexdigest(),
                'sha256': sha256.hexdigest(),
                'sha512': sha512.hexdigest(),
                'ssdeep': pydeep.hash_file(fullfile)
            }
            return hdict


def _targetselection(target):
    '''This function returns several hashes from the given file location'''
    hashd = []
    if os.path.isfile(target):
        print("[+] File detected")
        print("[+] I am going to hash '" + str(target) + "'")
        hashd.append(hashfile("./", target))
    elif os.path.isdir(target):
        print("[+] Directory detected")
        for dirName, subdirList, fileList in os.walk(target):  # pylint:disable=unused-variable
            for f in fileList:
                print("[+] Generating hash for '" +
                      dirName + "/" + str(f) + "'")
                hashd.append(hashfile(dirName, f))
    else:
        print("[-] Target argument is not a file or a directory.")
        sys.exit(1)
    if hashd:
        return hashd
    else:
        return


def _dostix(hashes):
    '''This function creates a STIX packages containing hashes.'''
    print("[+] Creating STIX Package")
    title = SETTINGS['stix']['ind_title'] + " " + str(datetime.datetime.now())
    _custom_namespace(SETTINGS['stix']['ns'], SETTINGS['stix']['ns_prefix'])
    stix_package = STIXPackage()
    stix_package.stix_header = STIXHeader()
    stix_package.stix_header.title = title
    stix_package.stix_header.handling = _marking()
    try:
        indicator = Indicator()
        indicator.set_producer_identity(SETTINGS['stix']['producer'])
        indicator.set_produced_time(indicator.timestamp)
        indicator.set_received_time(indicator.timestamp)
        indicator.add_kill_chain_phase(PHASE_DELIVERY)
        indicator.confidence = SETTINGS['stix']['confidence']

        indicator.title = title
        indicator.add_indicator_type("File Hash Watchlist")
        indicator.description = SETTINGS['stix']['ind_desc']

        try:
            indicator.add_indicated_ttp(
                TTP(idref=SETTINGS['indicated_ttp'],
                    timestamp=indicator.timestamp))
            indicator.suggested_coas.append(
                CourseOfAction(
                    idref=SETTINGS['suggested_coa'],
                    timestamp=indicator.timestamp))
        except KeyError:
            pass

        for info in hashes:
            try:
                file_name = info['filename']
                file_object = File()
                file_object.file_name = file_name
                file_object.file_extension = "." + file_name.split('.')[-1]
                file_object.size_in_bytes = info['filesize']
                file_object.file_format = info['fileformat']
                file_object.add_hash(Hash(info['md5']))
                file_object.add_hash(Hash(info['sha1']))
                file_object.add_hash(Hash(info['sha256']))
                file_object.add_hash(Hash(info['sha512']))
                file_object.add_hash(Hash(info['ssdeep'], Hash.TYPE_SSDEEP))
                for hashobj in file_object.hashes:
                    hashobj.simple_hash_value.condition = "Equals"
                    hashobj.type_.condition = "Equals"
                file_obs = Observable(file_object)
                file_obs.title = "File: " + file_name
                indicator.add_observable(file_obs)
            except TypeError:
                pass
        stix_package.add_indicator(indicator)
        return stix_package
    except KeyError:
        pass


def _make_stix(var):
    stix = _dostix(var)
    name = stix.id_.split(':', 1)[1] + '.xml'
    if SETTINGS['debug']['debug_mode']:
        outpath = SETTINGS['debug']['stix_out']
        if not os.path.isdir(outpath):
            print("[-] " + outpath + " is not a valid directory. Please change"
                  "the 'stix_out' setting in config.json before continuing.")
            sys.exit(0)
        outfile = open(outpath + name, 'w')
        outfile.write(stix.to_xml())
        outfile.close()
        print("[+] Succesfully created " + name)
    else:
        _inbox_package(SETTINGS['ingest'][0]['endpoint'] +
                       SETTINGS['ingest'][0]['user'], stix.to_xml())
        print("[+] Succesfully ingested " + name)
    return


def _main():
    if not len(sys.argv) > 1:
        print("[-] Please include an argument for the 'target' - a target file"
              " or directory to hash.")
        sys.exit()
    hashlist = _targetselection(sys.argv[1])
    split = SETTINGS['split_level']
    if len(hashlist) > split:
        print("[+] Splitting STIX Packages")
        for i, group in enumerate(izip_longest(*(iter(hashlist),) * split)):  # pylint:disable=unused-variable
            _make_stix(list(group))
    else:
        _make_stix(hashlist)

if __name__ == '__main__':
    _main()
