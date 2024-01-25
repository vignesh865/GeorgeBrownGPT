# Project Name

## Overview

This project involves the management and processing of JSON and TXT files related to program pages, along with additional functionalities for checking null values and running a main program.

## File Structure

- **functions.py**: Contains all the functions required for processing and managing files.
- **main.py**: Requires a folder path and an ngrok base_url to execute.
- **check_for_nulls.ipynb**: A Jupyter Notebook to check for null values in JSON files, move related TXT files to a new folder, and rerun those TXT files using `main.py`.
- **metadata_programpages2023**: Contains metadata for programpages2023.
- **metadata_programpages2024**: Contains metadata for programpages2024.
- **other two ipynb notebooks**: Intermediate notebooks used for testing.


## Execution Steps

1. **functions.py**: Contains essential functions for file management and processing.

2. **main.py**:
   - Requires the following inputs:
     - Folder name (ex. programpages2023)
     - ngrok base_url
   - Execute the script to perform specific functionalities.

3. **check_for_nulls.ipynb**:
   - Check for null values in JSON files.
   - Move related TXT files to a new folder.
   - Rerun those TXT files using `main.py`.

4. **metadata_programpages2023** and **metadata_programpages2024**:
   - Contain metadata for program pages corresponding to the respective years.

5. **other_notebook_1.ipynb** and **other_notebook_2.ipynb**:
   - Intermediate notebooks used for testing purposes.

## Usage

1. Run `main.py` with the required inputs to execute the main program.

2. Use `check_for_nulls.ipynb` to check for null values, move related TXT files, and rerun the files using `main.py`.

3. Ensure that all dependencies are installed before running any scripts.

## Dependencies

- List any dependencies or libraries required for running the scripts.

## Author

[Your Name]

## License

This project is licensed under the [License Name] - see the [LICENSE.md](LICENSE.md) file for details.
