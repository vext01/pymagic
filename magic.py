#!/usr/bin/env python2.7

import sys

class node:
    def __init__(self, level, descr):
        self.children = []
        self.level = level
        self.mime = None
        self.parent = None
        self.descr = descr

    def dump(self, level):

        # sanity check
        if (level != self.level):
            print("failed sanity check")
            sys.exit(1)

        sys.stdout.write("%s" % ("\t" * level))
        print(self)
        for i in self.children:
            i.dump(level+1)

    def __str__(self):
        return "* [%s] (mime=%s)" % (self.descr, self.mime)

# get next non-blank, non-comment line
def next_useful_line(f):
    while(True):
        line = f.readline()

        if (len(line) == 0):
            raise EOFError

        if len(line.strip()) == 0 or line.startswith("#") :
            continue

        return (line)

"""
peek at the next line and attach mime info to node if present
"""
def attach_mime(f, node):

    try:
        line = next_useful_line(f)
    except EOFError:
        return

    if (line.startswith("!:mime")):
        flds = line.strip().split(None, 1)
        flds = [ x for x in flds if len(x) != 0 ]
        node.mime = flds[1]
    else:
        f.seek(-len(line), 1)

"""
parse magic file making a tree
"""
def parse(f, parent_node, limit):

    ignore = True
    raw_line = None

    # keep reading until a useful line shows up
    while (True and limit > 0):

        limit -= 1 #XXX

        try:
            raw_line = next_useful_line(f)
        except EOFError:
            return # we are done

        line = raw_line.strip()
        print(line)

        if line.startswith("!:mime"):
            print("Unexpected mime");
            sys.exit(1)

        # get level
        lvl = 1
        while(line[0] == ">"):
            lvl += 1
            line = line[1:]

        new_node = None
        flds = line.split(None, 3)
        flds = [ x for x in flds if len(x) != 0]
        try:
            new_node = node(lvl, flds[3])
        except(IndexError):
            new_node = node(lvl, "")

        attach_mime(f, new_node)

        # XXX separate parent_node from last_node
        if (new_node.level == parent_node.level + 1):
            pass
            # parent_node does not change
        elif new_node.level == parent_node.level:
            parent_node = parent_node.parent
        elif new_node.level < parent_node.level:
            for up in range (0, parent_node.level - new_node.level + 1):
                parent_node = parent_node.parent
        else:
            print("should never happen")
            print("new_lvl = %d :: parent_lvl = %d" % (new_node.level,
                parent_node.level))
            # XXX some bad magic causes this. Hmmm
            sys.exit(1)

        new_node.parent = parent_node
        parent_node.children.append(new_node)
        parent_node = new_node

"""
TEST --------------------------------------------------------------
"""

magic = None
if (len(sys.argv) == 1):
    magic = open("/etc/magic", "r")
else:
    magic = open(sys.argv[1], "r")

sys.stdout.write("How many lines to parse (or hot enter for whole file: ")
lim = raw_input()
if len(lim.strip()) == 0:
    lim = 99999999999
else:
    lim = int(lim)

root = node(0, "<root>")
parse(magic, root, lim)
root.dump(0)
