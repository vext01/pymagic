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

"""
peek at the next line and attach mime info to node if present
"""
def attach_mime(f, node, raw_lines):

    line = f.readline()
    if len(line) == 0:
        return

    if (line.startswith("!:mime")):
        flds = line.strip().split("\t")
        flds = [ x for x in flds if len(x) != 0 ]
        node.mime = flds[1]
        raw_lines.append(line.strip())
    else:
        f.seek(-len(line), 1)

"""
parse magic file making a tree
"""
def parse(f, last_node, raw_lines):

    ignore = True
    raw_line = None

    # keep reading until a useful line shows up
    while (ignore):
        raw_line = f.readline()
        if len(raw_line) == 0:
            return raw_lines

        line = raw_line.strip()

        # blank lines/comments
        if len(line) == 0 or line.startswith("#"):
            continue
        break

    if line.startswith("!:mime"):
        print("Unexpected mime");
        sys.exit(1)

    # get level
    lvl = 1
    while(line[0] == ">"):
        lvl += 1
        line = line[1:]

    new_node = None
    flds = line.split("\t")
    flds = [ x for x in flds if len(x) != 0]
    try:
        new_node = node(lvl, flds[3])
    except(IndexError):
        new_node = node(lvl, "")

    # if we hit the next 1 level line, then end of this test
    if last_node.parent != None and lvl == 1:
        f.seek(-len(raw_line), 1)
        return raw_lines

    raw_lines.append(raw_line.strip())
    attach_mime(f, new_node, raw_lines)

    if (new_node.level == last_node.level):
        last_node.parent.children.append(new_node)
        new_node.parent = last_node.parent
        parse(f, new_node, raw_lines)

    elif new_node.level == last_node.level + 1:
        last_node.children.append(new_node)
        new_node.parent = last_node
        parse(f, new_node, raw_lines)

    elif new_node.level < last_node.level:

        # HAESBERT PLEASE CHECK THIS LOGIC
        new_parent = last_node
        for up in range (0, last_node.level - new_node.level + 1):
            new_parent = new_parent.parent
        new_node.parent = new_parent

        new_parent.children.append(new_node)
        parse(f, new_node, raw_lines)

    else:
        print("should never happen")
        print("new_lvl = %d :: parent_lvl = %d" % (new_node.level,
            parent_node.level))
        sys.exit(1)

    return raw_lines

"""
TEST --------------------------------------------------------------
"""

magic = None
if (len(sys.argv) == 1):
    magic = open("/etc/magic", "r")
else:
    magic = open(sys.argv[1], "r")

while(True):
    root = node(0, "<root>")
    raw_lines = parse(magic, root, [])

    if len(raw_lines) == 0:
        sys.exit(0)

    print("\nTHESE LINES:")
    for i in raw_lines:
        print(i)
    print("\n")

    print("BECAME:")
    root.dump(0)

    print("\nHit enter for the next root branch")
    raw_input()
    print("-------------------------------\n")
