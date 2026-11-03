import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
MAPS = os.path.dirname(ROOT)
V18 = os.path.join(MAPS, 'Pokemon Arena v1.8.w3x')
PKL = os.path.join(MAPS, 'PKLegendsv3.2.w3x')
EXTRACTED = os.path.join(ROOT, 'extracted_v1.8')
