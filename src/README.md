# Bavaria Building Plans Digitalization

This project from GreenDIA and aims to create dataset regarding land use in Germany. As comprehensive dataset of land use in Germany is not available, this project aims to create a dataset that can be used for further analysis and research. The dataset is extracted from local landuse plans and regional from Bavaria in Germany.

## Installation

Instructions on how to install and set up the project.

## Folder Structure

A brief description of the folder structure and files:

```
bavaria-building-plans-digitalization/
├── src/                # Source files
│   ├── geodata_bayern_scraping         # Scraping of Geodata Bayern
│   ├── geoservices_bayern_scraping        # Scraping of Geoservices
│   ├── pdfs_to_text      # Extracting text from PDFs
│   ├── processing_data        # Data processing
│   ├── textual_features        # Extracting textual features from text
│   ├── visualizations        # Visualizing data
├── data/               # Data files
│   ├── raw/            # Raw data files
│   ├── proc/       # Processed data files
│   ├── final/       # Final data files
├── dictionaries/              # Dictionaries for keyword search
│   ├── keyword_name_of_keyword_search.json   
├── README.md           # Project documentation
├── requirements.txt    # List of dependencies
```

## Running the Project from VM

1. Connect to the VM using the provided IP address and credentials.

ssh -i C:\Path to PEM Key greendia-user@IP Address

2a. Create a screen session to keep code running in the background.

screen 

2b. If there is a screen session running already (check with screen -ls), reattach to it.

screen -r

3. Ctrl + A then D to detach. 

