#!/usr/bin/python
#
# unstk - Extract parts of HP1820 STK firmware images.
#
# Based on https://mail.python.org/pipermail/python-list/2014-April/670688.html
#

from struct import unpack
from sys import argv

def dump_image(index, data):
    filenames = [ 'kernel.xz', 'initramfs.cpio.xz', 'activate.sh', 'application.tar.gz', 'signature.txt' ]
    if index < len(filenames):
        filename = filenames[index]
    else:
        filename = "dump-%d.bin" % index
    print("[%d] %s: %d bytes" % (index, filename, len(data)))
    with open(filename, 'wb') as f:
        f.write(data)

with open(argv[1], "rb") as f:
    # skip STK header
    f.read(88)
    f.read(28)

    (ih_magic, ih_hcrc, ih_time, ih_size, ih_load, ih_ep, ih_dcrc, 
     ih_os, ih_arch, ih_type, ih_comp, ih_name) \
        = unpack("!IIIIIIIBBBB32s",f.read(64))

    print("magic=%08x type=%d size=%d name='%s'" % (ih_magic, ih_type, ih_size, ih_name))

    if ih_type == 4:
        # multi-file: read image lengths from data
        imagesizes = []
        while 1:
            size, = unpack("!I",f.read(4))
            if size == 0:
                break
            imagesizes.append(size)
    else:
        # single-file
        imagesizes = [ih_size]

    index = 0
    for size in imagesizes:
        dump_image(index, f.read(size))
        index += 1
        if size & 3:
            f.read(4 - size & 3)

    extradata = f.read() 
    if extradata:
        dump_image(index, extradata)
