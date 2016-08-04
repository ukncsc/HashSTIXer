import hashlib
import os
import sys

BUF_SIZE = 65536


def hashfile(path, file):
    '''This function returns a hash from a given file.'''
    md5 = hashlib.md5()
    sha1 = hashlib.sha1()
    sha256 = hashlib.sha256()
    fullfile = path + "/" + file
    with open(fullfile, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)
            sha1.update(data)
            sha256.update(data)
            hdict = {'filename': str(file), 'md5': md5.hexdigest(
            ), 'sha1': sha1.hexdigest(), 'sha256': sha256.hexdigest()}
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
        for file in os.listdir(target):
            print("[+] I am going to hash '" + str(file) + "'")
            hashd.append(hashfile(target, file))
    if hashd:
        return hashd
    else:
        return


def main():
    print(_targetselection(sys.argv[1]))


if __name__ == '__main__':
    main()
