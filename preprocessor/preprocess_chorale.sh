#!/bin/bash
#
# Preprocess a Bach chorale for ingestion by the Python humpy module.
# Specficially, we need to get the beat information prepended.

# Get the soprano part.
beat $1 > /tmp/$$beat
semits -tx $1 > /tmp/$$semits
dur -x $1 > /tmp/$$durs
extract -i '*Isoprn' $1 > /tmp/$$sop
extract -i '*Isoprn' /tmp/$$durs > /tmp/$$durs2
extract -i '*Isoprn' /tmp/$$semits > /tmp/$$semits2
assemble /tmp/$$beat /tmp/$$sop /tmp/$$semits2 /tmp/$$durs2

rm /tmp/$$*
