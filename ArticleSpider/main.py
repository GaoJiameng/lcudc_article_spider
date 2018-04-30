#  _*_  coding: utf-8  _*_
___auther___ =  'Ryan'

from scrapy.cmdline import execute

import sys
import os


sys.path.append(os.path.dirname(os.path.abspath(__file__)))
execute(["scrapy", "crawl", "lcudc"])