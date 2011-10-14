#!/usr/bin/env python2.7

import sys

class node:
    """ Represents a node in the n-ary tree we are building """

    def __init__(self, level, descr):
        """ make a new node """
        self.children = []
        self.level = level # -1 for root
        self.mime = None
        self.parent = None
        self.descr = descr

    def dump(self, level):
        """ dump a node and it's subtree to stdout """

        # indent
        sys.stdout.write("%s" % ("    " * level))
        print(self)

        # print kids
        for i in self.children:
            i.dump(level+1)

        # sanity check
        if (level != self.level):
            print("failed sanity check")
            sys.exit(1)

    def __str__(self):
        """ string representation of a single node """
        return "* [%s] (mime=%s, level=%d)" % \
                (self.descr, self.mime, self.level)

def next_useful_line(f):
    """ get next non-blank, non-comment line """
    while(True):
        line = f.readline()

        if (len(line) == 0):
            raise EOFError

        if len(line.strip()) == 0 or line.startswith("#") :
            continue

        return (line)

def attach_mime(f, node):
    """ peek at the next line and attach mime info to node if present """
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

def parse(f, root_node):
    """ parse magic file making a tree """
    ignore = True
    raw_line = None

    last_node = root_node

    # keep reading until a useful line shows up
    while (True):

        try:
            raw_line = next_useful_line(f)
        except EOFError:
            return # we are done

        line = raw_line.strip()

        if line.startswith("!:mime"):
            print("Unexpected mime");
            sys.exit(1)

        # get level
        lvl = 0
        while(line[0] == ">"):
            lvl += 1
            line = line[1:]

        # construct the new node
        new_node = None
        flds = line.split(None, 3)
        flds = [ x for x in flds if len(x) != 0]
        try:
            new_node = node(lvl, flds[3])
        except(IndexError):
            new_node = node(lvl, "")

        # attach mime iff a mime line follows
        attach_mime(f, new_node)

        # decide where to insert the new node
        insert_at = None
        if (new_node.level == last_node.level):
            # new node is on the same level as the last node's parent
            # new parent becomes the last node's parent's parent
            # (lol)
            insert_at = last_node.parent

        elif new_node.level == last_node.level + 1:
            # new node on next level deep as last
            # last node becomes new parent
            insert_at = last_node

        elif new_node.level < last_node.level:
            # new node is further up the tree
            # go up the difference in levels to find the new parent
            insert_at = last_node.parent
            for up in range (0, last_node.level - new_node.level):
                insert_at = insert_at.parent
        else:
            # if the new node has a level greater than 2 more than the last
            # node, something went wrong.
            print("should never happen")
            print("new_lvl = %d :: last_lvl = %d" % (new_node.level,
                last_node.level))
            sys.exit(1)

        insert_at.children.append(new_node)
        new_node.parent = insert_at
        last_node = new_node

if (__name__ == "__main__"):
    magic = None
    if (len(sys.argv) == 1):
        magic = open("magic", "r")
    else:
        magic = open(sys.argv[1], "r")

    root = node(-1, "<root>")
    parse(magic, root)
    root.dump(-1)
