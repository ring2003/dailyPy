#!/usr/bin/env python
#--------------------------------------------------------
# A toy script of python3 filesystem & asyncio library
#--------------------------------------------------------
# Read 'publics.list' to filter out all symlink entries,
# And add to a missing list, if it doesn't exist in currrent symlink list．
#
import os
import asyncio

@asyncio.coroutine
def islink(en, cb, wcb):
    if os.path.islink(en):
        cb.send( (en, wcb) )

@asyncio.coroutine
def isInSymlinkList(en):
    print("Initializing resolver corouting.")
    allLinks = dict()
    with open("symlinks.list", 'r') as fh:
        for row in fh:
            rr = row.rstrip()
            com = rr.split(',')
            link = com[-1]
            target = com[1]
            allLinks[link] = target
    while True:
        query , cb = (yield)
        resolve(allLinks, query, cb)

def resolve(allLinks, link, cb):
    exists = allLinks.get(link)
    if exists is None:
        target = os.path.realpath(link)
        if target is None:
            pass
        else:
            print("%s -> %s" % (link, target))
            cb.send( (link, target) )
            while True:
                parent = os.path.dirname(target)
                if parent == "/":
                    break
                else:
                    if os.path.islink(parent):
                        resolve(allLinks, parent)
                    target = parent

@asyncio.coroutine
def saveAddtionalSymlink(cb):
    print("Initializing saver coroutine.")
    dumpTo = 'missing_sym.list'
    if os.path.exists(dumpTo):
        os.remove(dumpTo)
    missingFh = open(dumpTo,'a')
    while True:
        link , target = (yield)
        missingFh.write("%s,%s\n" % (link,target))
        missingFh.flush()
    missingFh.close()

cb = isInSymlinkList(None)
wcb = saveAddtionalSymlink(None)
cb.send(None)
wcb.send(None)
tasks = list()
with open("publics.list",'r') as fh:
    for row in fh:
        rr = row.rstrip()
        tasks.append(asyncio.ensure_future(islink(rr, cb, wcb)))
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.gather(*tasks))
loop.close()

