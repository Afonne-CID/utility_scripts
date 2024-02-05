# IcsToXlsx Converter

Converts iCalender file into a spreadsheet

## Configuration
- Setup a virtual environment.

**P.S**: You want to always do this for every of your Python project.

There are many ways to achieve this. Personally I use `virtualenv` or just 	`venv`.

So, one way you can setup virtual environment:

```
python -m venv env
```

`env` in `python -m venv env` can be anything else, but "env" is commonly used.

After that, activate the environment. I do `source env/Scripts/activate` on my Windows machine, and `source venv/bin/activate` on my Linux.

It should be something similar on MacOS too.

- Install requirement libraries
```
pip install -r requirements.txt
```

This command installs the required library for the program.

Ensure to install after an environment is already active.

## Usage
An example use:
```
python converter.py /dir/file_to_convert.ics /path/converted_file.xlsx
```

**Note**:
- The output file name is optional as it defaults to `output.xlsx` in the current directory.
- If you do provide an output name, you can choose to, or not add the `.xlsx` extension. E.g: Both `expected_filename.xlsx` and `expected_filename` are valid output file names.
- Relative file paths are supported, but the target file has to be in the current/relative path.
- In the case of an absolute path, spaces within filenames (file to be converted as well as in output file name) are also supported.

## Author
CID [X/Twitter](https://tweeter.com/cee_eye_d)