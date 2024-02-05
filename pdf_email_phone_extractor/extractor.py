import os
import re
import PyPDF2
import sys
import shutil


def pdf_extractor():

    email_regex = re.compile(r'[\w.+-]+@[\w-]+\.[\w.-]{3}')
    phone_regex = re.compile (r'([-\.\s]??\d{3}[-\.\s]??\d{3}[-\.\s]??\d{5}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{5}|\d{3}[-\.\s]??\d{5})')
    
    target_file_path = sys.argv[1]

    pdf_files = list_of_files(target_file_path)
    keys = pdf_files.keys()

    for key in keys:
        print(key + '...')
        for pdf_file in pdf_files[key]:
            try:
                with open(pdf_file, 'rb') as pdf_obj:
                    pdf_reader = PyPDF2.PdfFileReader(pdf_obj)
                    
                    pdf_obj = ''
                    count = pdf_reader.numPages
                    for i in range(count):
                        pdf_obj += str(pdf_reader.getPage(i).extractText())
                        
                    phone = str(phone_regex.findall(pdf_obj))\
                            .replace('[', '').replace(']', '')\
                            .replace(' ', '')\
                            .strip("'")\
                            .replace(',', ' ')\

                    email = str(email_regex.findall(pdf_obj))\
                            .replace('[', '')\
                            .replace(']', '')\
                            .strip("'")

                    with open(sys.argv[2] + key + '.txt', 'a+', encoding="utf-8") as extracts:
                        details = '{}, {}\n'.format(phone.strip("'") if len(phone) > 0 else '', email if len(email) > 0 else '')
                        contact = details.strip("'")
                        extracts.write(contact.strip("'"))
            except Exception as e:
                pass

    empty_folder(target_file_path)

    print('Action was successful')
    return


def list_of_files(path_of_the_directory):

    pdf_files = {}
    for state_name in os.listdir(path_of_the_directory):
        state = []
        for file_name in os.listdir(path_of_the_directory + state_name):
            f = os.path.join(path_of_the_directory, state_name + '/' + file_name)
            if os.path.isfile(f):
                state.append(f)
        pdf_files[state_name] = state

    return pdf_files


def empty_folder(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

pdf_extractor()
