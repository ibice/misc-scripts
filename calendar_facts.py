#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Inspired by a xkcd strip (https://xkcd.com/1930/)
# Text and behaviour was specified by them. I just implemented it with py

from random import randint

struct =  \
    [   "Did you know that ",
        [   ["the ", ["fall ", "spring "], "equinox "],
            ["the ", ["winter ", "summer "], ["solstice ", "olympics "]],
            ["the ", ["earliest ", "latest "], ["sunrise ", "sunset "]],
            ["daylight ", ["savings ", "saving "], "time "],
            ["leap ", ["day ", "year "]],
            ["easter "],
            ["the ", ["harvest ", "super ", "blood "], "moon "],
            ["toyota truck month "],
            ["shark week "]],
        [   ["happens ", ["earlier ", "later ", "at the wrong time "], "every year "],
            ["drifts out of the sync with the ", ["sun ", "moon ", "zodiac ", [["gregorian ", "mayan ", "lunar ", "iphone "], "calendar "], ["atomic clock in colorado "]]],
            ["might ", ["not happen ", "happen twice "], "this year "]],
        "because of ",
        [   ["time zone legislation in ", ["indiana", "arizona", "russia"]],
            ["a decree by the pope in the 1500s"],
            [["precession ", "liberation ", "nutation ", "libation ", "eccentricity ", "obiquity "], "of the ", ["moon", "sun", "earth's axis", "equator", "prime meridian", [["international date ", "Mason-Dixon "], "line"]]],
            ["magnetic field reversal"],
            ["an arbitrary decision by ", ["Benjamin Franklin", "Isaac Newton", "FDR"]]],
        "? ",
        "Apparently ",
        [   ["it causes a predictable increase in car accidents"],
            ["that's why we have leap seconds"],
            ["scientists are really bored"],
            ["it was even more extreme during the ", ["bronze age", "ice age", "crecateous", "1990s"]],
            ["there's a proposal to fix it, but it ", ["will never happen", "actually makes things worse", "is stalled in congress", "might be unconstitutional"]],
            ["it's getting worse and no one knows why"]],
        "."]

def process (node, level, sentence):

    if type(node) == str:
        return node

    if type(node) == list and len(node) == 1 and type(node[0]) == str:
        return node[0]

    if level % 2 == 1:
        # combinational level
        sentence += process(node[randint(0, len(node) - 1)], level + 1, "")
        return sentence
    else:
        # sequential level
        for subnode in node:
            sentence += process(subnode, level + 1, "")
        return sentence

print(process(struct, 0, ""))
