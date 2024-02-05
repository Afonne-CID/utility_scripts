# Email_N_Phone
Email_N_Phone extracts email address and phone numbers from any PDF file.

It's implemented in a way that makes bulk extraction EASY, FAST and SIMPLE.

## Getting Started
To get started using `Email_N_Phone`, make sure you have python installed on your machine.

Once you have python installed, `fork` this repository and `git clone https://github.com/Afonne-CID/email_phone_extractor.git` into your local.

Now, create a virtual environment.

    pip install virtualenv #Installs virtualenv
    virtualenv env #The name of the environment to be created

Then:

```
    pip install -r requirements

```

Now to start extracting, load the folders that have the pdf files into this path `C:/Users/CID/Desktop/pdf_files/` on your computer.

You'll need to create this path or change the path in the code to your preferred location.

The structure of the folders that contain the pdf files should be like:

```

   - folder
    - pdf_file1.pdf
    - pdf_file2.pdf
    ...
   ...

```

## Run

```

    python.py pdf_extractor.py <required_target_pdfs_path/> <opional_absolute_path_to_extract_file_to/>

```

Enjoy.