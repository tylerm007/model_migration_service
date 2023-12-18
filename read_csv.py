import csv
import os

def append_content(content: str, project_directory: str):
    file_name = f"{project_directory}"
    with open(file_name, "a") as expose_services_file:
        expose_services_file.write(content)
        
def get_os_url(url: str) -> str:
    """ idiotic fix for windows (\ --> \\\\) """
    return url.replace('\\', '\\\\')

def main():
    #read_and_write("NOTES_DATA_TABLE","NOTES_DATA_TABLE.sql")
    read_and_write("SHIPMENTS_DATA_TABLE","SHIPMENTS_DATA_.sql")
    
def convert_row(row: any) -> str:
    ret = "("
    sep =""
    for r in row:
        r = r.replace("\n"," ", 20)
        r = r.replace("'","", 20)
        ret += f"{sep}{r}" if r.isnumeric() else f"{sep}'{r}'"
        sep = ","
    ret += "),\n"
    return ret
    
def read_and_write(source_csv, target_file):
    print(f"Read {source_csv}.csv")
    content = ""
    header = ""
    with open(f'./{source_csv}.csv') as fileObject:
        reader_obj = csv.reader(fileObject)
        for i, row in enumerate(reader_obj):
            if i> 0:
                content += convert_row(row)
            else:
                row = str(row).replace("'","", 100)
                row = row.replace("[","")
                row = row.replace("]","")
                header = f"insert into {source_csv} ({row}) values \n"
    append_content(header, f"./{target_file}.SQL")
    append_content(content, f"./{target_file}.SQL")
    
    
    
    
if __name__ == "__main__":
    main()