import sys
import pandas as pd
from icalendar import Calendar
import recurring_ical_events
import datetime


def process_filenames(filenames):
    '''Processes filenames with spaces
    '''
    result = []
    current_filename = ""

    for filename in filenames:
        # current_filename will only be valid if it has an extension
        combined_filename = current_filename + filename
        if '.' in combined_filename:
            # If it has a single extension, consider it complete
            result.append(combined_filename)
            current_filename = ""
        else:
            current_filename = f'{combined_filename} '

    if current_filename:
        result.append(current_filename)

    return result


def remove_timezone(dt):
    '''Remove timezone information from a datetime object.'''
    return dt.replace(tzinfo=None)

def ics_to_excel(ics_file_path, excel_file_path):
    '''Converts iCalender file to spreadsheet'''
    with open(ics_file_path, 'rb') as file:
        calendar = Calendar.from_ical(file.read())

    events = recurring_ical_events.of(calendar).between(datetime.datetime.now() - datetime.timedelta(days=1), datetime.datetime.now() + datetime.timedelta(days=365))

    event_list = []

    for event in events:
        event_summary = str(event.get('summary'))
        event_start = remove_timezone(event.get('dtstart').dt)
        event_end = remove_timezone(event.get('dtend').dt)
        event_description = str(event.get('description'))
        event_location = str(event.get('location'))

        event_data = {
            'Summary': event_summary,
            'Start': event_start,
            'End': event_end,
            'Description': event_description,
            'Location': event_location
        }
        event_list.append(event_data)

    df = pd.DataFrame(event_list)
    df.to_excel(excel_file_path, index=False)


# Execution
if __name__ == "__main__":

    file_to_convert = None
    output_filename = 'output.xlsx'

    cli_inputs = process_filenames(sys.argv)
    print(cli_inputs)

    if len(cli_inputs) < 2:
        print('''Please provide `.ics`* path and optionally, an expected output name (defaults to `output.xlsx`).
            E.g: `python converter.py /dir/file_to_convert.ics converted_file.xlsx`
            ''')
    else:
        
        file_to_convert = cli_inputs[1]
        if len(cli_inputs[1:]) >= 2:

            input_filename = cli_inputs[2]
            input_filename_parts = input_filename.split('.')
            
            if len(input_filename_parts) > 1:
                input_filename_parts[-1] = 'xlsx'
                input_filename = '.'.join(input_filename_parts)
            else:
                input_filename += '.xlsx'

            output_filename = input_filename

        ics_to_excel(ics_file_path=file_to_convert, excel_file_path=output_filename)

    print(f'Your file was successfully converted -> {output_filename}')
