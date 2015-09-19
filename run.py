#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
 
"""Convenience wrapper for running thorrent directly from source tree."""
 
 
from thorrent.thorrent import main

if __name__ == "__main__":
    main(sys.argv[1:])