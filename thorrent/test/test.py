#!/usr/bin/python
# -*- coding: utf-8 -*-
import string, logging
html_title = 'Молодые и Голодные (1 сезон: 1-2 серии из 10) / Young and Hungry / 2014 / ЛМ (OK!Prod) / HDTVRip'
if "сезон" in html_title: # If season is present in title
    p = html_title.find("сезон")
    p2 = html_title[0:p-1].find(" (")

    print(html_title[p2+2:p-1])
