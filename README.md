Fetch Commits from Azure DevOps
===============================

This project fetches commit data from an Azure DevOps repository, processes it,
and generates reports. It includes tools for creating visualizations and
exporting data, making it ideal for tracking development progress and
analyzing commit patterns over time.

Features
--------

**Fetch Commit Data**: Retrieve commits from a specified Azure DevOps repository using a Personal Access Token (PAT).

**Data Processing**: Parse and organize commit data for meaningful analysis.

**Reporting and Visualization**: Generate reports and save visualizations in the `evidences/yyyy-mm/` folder structure, with automatic subfolder categorization by file type (e.g., `.png` for images).

**Excel Export**: Export results to an Excel sheet for further analysis.


Prerequisites
-------------

Ensure you have the following installed:

`Python 3.6+`

`openpyxl`: For handling Excel files

`matplotlib`: For data visualization

You can install these dependencies via:

    pip install openpyxl matplotlib

Setup
-----

Clone the repository:

    git clone https://github.com/dflucas/fetch-commits-azure.git
    cd fetch-commits-azure

### Configure Your Token:

In `fetch_commits.py`, replace `<YOUR_TOKEN>` on line 12 with your Azure DevOps Personal Access Token (PAT).

### Run the Script:

    python generate_report.py

Folder Structure
----------------

Reports and visualizations will be saved in the `evidences/` folder with the following structure:

`evidences/yyyy-mm/png`: For image reports
`evidences/yyyy-mm/xls`: For Excel files

Usage
-----

The script can be customized to fetch commits from various projects within Azure DevOps. You can adjust project-specific configurations directly in the script or extend the functionality as needed.

Troubleshooting
---------------

**Authentication Errors**: Ensure the token is correctly set and has the necessary permissions for your Azure DevOps project.
**File/Directory Issues**: If the required folder structure isn't created, check that the script has write permissions in the directory.

License
-------

This project is licensed under the [MIT License](LICENSE).
