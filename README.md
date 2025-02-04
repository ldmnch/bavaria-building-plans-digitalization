# Bavaria Building Plans Digitalization

This project by GreenDIA aims to create a dataset regarding land use in Germany. As a comprehensive dataset of land use in Germany is not available, this project seeks to fill that gap by extracting data from local land use plans and regional sources in Bavaria, Germany.

## Installation

Follow these instructions to install and set up the project.

## Folder Structure

An overview of the folder structure and files:

```
bavaria-building-plans-digitalization/
├── src/                        # Source files
│   ├── pdfs_to_text                    # Extracting text from PDFs
│   ├── processing_data                 # Data processing
│   ├── textual_features                # Extracting textual features
│   ├── llm_extraction.py # Main pipeline run file 
├── data/                       # Data files
│   ├── raw/                    # Raw data files
│   ├── proc/                   # Processed data files
│   ├── final/                  # Final data files
├── README.md                   # Project documentation
├── requirements.txt            # List of dependencies, has to be updated 
```

## Running the Project from VM

1. Connect to the VM using the provided IP address and credentials:

```sh
ssh -i C:\Path\to\PEM\Key greendia-user@IP_Address
```

2. Activate environment    `bp_digitalization`.

```sh
source bp_digitalization/bin/activate
```

3. Create a screen session to keep the code running in the background:

```sh
screen
```

If there is already a screen session running (check with `screen -ls`), reattach to it:

```sh
screen -r
```

4. To detach from the screen session, press `Ctrl + A` then `D`.
