import zipfile
import os

def zip_directory(directory, zip_file):
    """
    Compresses the specified directory into a zip file.

    :param directory: Path to the directory to be compressed.
    :param zip_file: Path to the output zip file.
    """
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, directory))

if __name__ == "__main__":
    directory_to_zip = r'<abolute path to file goes here>'
    output_zip_file = r'<absolute path including file name goes here'

    zip_directory(directory_to_zip, output_zip_file)
    print(f"Directory '{directory_to_zip}' zipped successfully to '{output_zip_file}'.")

