import os

from pdf2image import convert_from_path
from tqdm import tqdm

def readfiles(input_folder):
   
   pdf_files = [file for file in os.listdir(input_folder) if file.endswith(".pdf")]
       
   return(pdf_files)

def split_pdf(input_folder, 
              file_name,
              output_folder):
    
    input_pdf_path = os.path.join(input_folder, f'{file_name}.pdf')

    try:
            
            pages = convert_from_path(input_pdf_path, 90)

            for count, page in enumerate(pages):
                page.save(f'{output_folder}/{file_name}_{count}.jpg', 'JPEG')

    except Exception as e:
        
        with open(f'{output_folder}/logs.txt', 'a') as log_file:
                log_file.write(f"PDF {str(file_name)}: An error occurred - {str(e)}\n")

    except Warning as w:
         
        with open(f'{output_folder}/logs.txt', 'a') as log_file:
                log_file.write(f"PDF {str(file_name)}: An error occurred - {str(w)}\n")






def run_pdfs_split(input_folder,
                   output_folder):
     
     pdfs = readfiles(input_folder)

     pdfs = [p.removesuffix('.pdf') for p in pdfs]

     for file in tqdm(pdfs, total=len(pdfs)):
        split_pdf(input_folder = input_folder, 
                file_name = file,
                output_folder = output_folder)
     
