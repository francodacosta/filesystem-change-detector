# Filesystem Change Detector
This tool will keep a record of a file checksum.

It will report if the checksum changes or if files where added or deleted to a folder

## Why?
I needed a tool to check if a folder has tampered files or if files where added/deleted

This would help me to be aware of potential attacks to wordpress installations

I could not find a ready tool, so FCD was created

## Cli parameters
### -- init
Creates a new database

### --db _path_
path to the database file to use

### --add _path_
adds a file to the database, it will automatically compute the checksum and add/replace the entry in the db

### --add-folder _path_
will recursively add all files in the folder to the database

### --remove _path_
will remove the file from the database, this file will no longer be checked

### --list
lists all files and checksums present in the database

### --check-all
will check all files in the database, it will report errors if the checksum has changed or the file was deleted

### --check-folder _path_
will compare all files in the folder with the file list in the database, it will report errors if a file was added or removed to the folder and also if there is a checksum mismatch

### --ignore _path_
the file/folder will be ignored, can be used multiple times
