# Resume-Parser
It can fetch name,gmail,phone,skills from your resume that you have stored in Google Drive
- make sure you have installed python 3
- from ctypes.wintypes import tagRECT
  from django.shortcuts import render,redirect
  from django.http import HttpResponse

  from urllib import response
  from . import Google
  #importing libraries to download media from Google drive
  import io
  import os
  from googleapiclient.http import MediaIoBaseDownload
  import pandas as pd

  from resume_parser import resumeparse
  import pytesseract
  import cv2  #open cv library
  import re
  from fpdf import FPDF
  import shutil
  from django.contrib import messages
  import glob
 
 these libraries are being used for this app,make sure everything is installed.
 
 -Run python3 manage.py runserver(for ubuntu)
 
 -Now this app will run on 8000 port of your localhost
