import PyPDF2
import os

def readfiles(input_folder):
   
   pdf_files = [file for file in os.listdir(input_folder) if file.endswith(".pdf")]
       
   return(pdf_files)

def split_pdf(input_folder, 
              file_name,
              output_folder):
    
    input_pdf_path = os.path.join(input_folder, f'{file_name}.pdf')

    try:
    
            with open(input_pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)

                for page_num in range(len(pdf_reader.pages)):
                    pdf_writer = PyPDF2.PdfWriter()
                    pdf_writer.add_page(pdf_reader.pages[page_num])

                    output_pdf_path = f"{output_folder}/{file_name}_{page_num + 1}.pdf"

                    with open(output_pdf_path, 'wb') as output_file:
                        pdf_writer.write(output_file)

    except PyPDF2.errors.PdfReadError as e:
        
        with open(f'{output_folder}/logs.txt', 'a') as log_file:
                log_file.write(f"PDF {str(file_name)}: An error occurred - {str(e)}\n")


def run_pdfs_split(input_folder,
                   output_folder):
     
     pdfs = readfiles(input_folder)

     pdfs = [p.removesuffix('.pdf') for p in pdfs]

     for file in pdfs:
        split_pdf(input_folder = input_folder, 
                file_name = file,
                output_folder = output_folder)
     
