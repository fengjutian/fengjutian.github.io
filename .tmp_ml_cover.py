# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0, r".agents\skills\blog-post-publishing\scripts")
import covers

OUT = os.path.abspath(r"assets\img\blog")
print(covers.build("mainline", OUT))
