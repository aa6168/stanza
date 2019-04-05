# stanza

Create stanza file for users from SQLite database

This project uses a small Python script to create stanza files for setting quotas per user in the relevant GPFS filesets. Users, filesets and quotas are stored in a SQLite database.

# WARNING:
This project is created for demonstration purposes ONLY.  It serves no practical use and could potentially damage files in your filesystem. You are strongly advised NOT to use it. We DON’T accept any liability from any damage caused by its use.

# Use:
To test the script, Python 3.5 or greater is required. The SQLite database file must be in the same local directory where the script is executed. The executing user must have write permissions in the local directory. The output file will be created if it does not exist. If the output file exists, it will be overwritten and all previous data in the output file will be LOST. The Python script will NOT work with any other SQLite database file.
