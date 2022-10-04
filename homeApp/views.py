from ctypes.wintypes import tagRECT
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



from selenium import webdriver  #To close a tab


# Create your views here.

def loadFirstPage(request):
    return render(request,'firstpage.html')

def create_gapi_instance():
    CLIENT_SECRET_FILE = 'client_secret.json'
    API_NAME= 'drive'
    API_VERSION= 'v3'
    SCOPES = ['https://www.googleapis.com/auth/drive']
    service = Google.Create_Service(CLIENT_SECRET_FILE,API_NAME,API_VERSION,SCOPES)
    #Here service is a Google drive service instance
    return service

def root_files(request):
    service=create_gapi_instance()
    query= "'root' in parents"  

    response=service.files().list(q=query).execute()
    files=response.get('files')
    nextPageToken=response.get('nextPageToken')

    while nextPageToken:
        response=service.files().list(q=query).execute()
        files.extend(response.get('files'))
        nextPageToken=response.get('nextPageToken')

    df=pd.DataFrame(files)
    df=df[df['mimeType']=='application/vnd.google-apps.folder']

    global all_folders
    all_folders=zip(list(df['id']),list(df['name']))
    
    return render(request,'rootfolder.html',{'all_folders':all_folders})

def download_files(file_id,file_name):
    service=create_gapi_instance()

    request=service.files().get_media(fileId=file_id)

    fh= io.BytesIO()
    downloader = MediaIoBaseDownload(fd=fh, request=request)
    done = False

    while not done:
        status,done = downloader.next_chunk()
    fh.seek(0)

    with open(os.path.join('./Resumes',file_name) ,'wb') as f:
        f.write(fh.read())
        f.close()


def files_inside_folder(request,folder_id):
    try:
            service=create_gapi_instance()
            query= f"'{folder_id}' in parents"  #"'root' in parents" (For root drive)  


            response=service.files().list(q=query).execute()
            files=response.get('files')
            nextPageToken=response.get('nextPageToken')

            while nextPageToken:
                esponse=service.files().list(q=query).execute()
                files.extend(response.get('files'))
                nextPageToken=response.get('nextPageToken')
                

            df=pd.DataFrame(files)
            all_files=list(df['id'])
            print(df)

            counter=1
            for file_id in all_files:
                file_name='document'+str(counter)+'.pdf'
                if ((df[df['id']==file_id]['mimeType']).get(key = counter-1)) == 'application/pdf':
                    download_files(file_id,file_name)
                    counter += 1
                elif ((df[df['id']==file_id]['mimeType']).get(key = counter-1)) == 'image/jpeg':
                    file_name='document'+str(counter)+'.jpeg'
                    download_files(file_id,file_name)
                    counter += 1   
                    image_to_pdf(file_name) 
            

                #########    Resume Parsing   ###############
            name=[]
            phone=[]
            email=[]
            skills=[]

            for i in range(1,len(df)+1):
                document_name='document'+str(i)+'.pdf'
                data = resumeparse.read_file('./Resumes/'+document_name)
                name.append(data['name'])
                phone.append(data['phone'])
                email.append(data['email'])
                skills.append(data['skills'])
            table = zip(name,phone,email,skills)

            
            return render(request,'output.html',{'table':table})
    except:
        #messages.info(request, 'Your password has been changed successfully!')
        return render(request,'notfound.html')



def signout(request):
    os.remove("./token_drive_v3.pickle")

    location='./Resumes/'
    for file in os.listdir(location):
        os.unlink(location+file)
        
    return redirect('/')

def image_to_pdf(file_name):
    img=cv2.imread('./Resumes/'+file_name)

    resume_text=pytesseract.image_to_string(img)
    pdf=FPDF()
    pdf.add_page()
    pdf.add_font("Arial", "", "arial.ttf", uni=True)
    pdf.set_font("Arial", style='' , size=30) 
    pdf.cell(200, 10, txt = resume_text ,ln = 1, align = 'C')
    pdf_name=file_name[ :-4]+'pdf'
    pdf.output(pdf_name)

    src_path = pdf_name
    dst_path = "Resumes/"+pdf_name
    shutil.move(src_path, dst_path) 

    
