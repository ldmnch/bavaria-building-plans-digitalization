import os
from random import sample

import cv2
import pandas as pd
from loguru import logger
from tqdm import tqdm

from features.image_extraction.image_extractor import ImageExtractor
from features.image_extraction.image_preprocessor import ImagePreprocessor
from features.image_extraction.preprocessing_utility import pdf2image_dir
from utility.config_utils import get_source_path, get_project_root_path

SRC_DIR = get_source_path()
ROOT_DIR = get_project_root_path()


def preprocess_pdf_folder(preprocess_config: dict, file_names_to_convert: list = None):
    """Preprocesses all pdf files in a directory and saves the images to another directory.

    Reads the config/preprocessing_config.yml file and uses the ImagePreprocessor class to preprocess the images.
    The images are saved to the output directory with the same filename as the input pdf and an index.

    Args:
        preprocess_config (dict): Preprocessing config dictionary. Needs to contain the following keys:
            InputDir (str): Path to the input directory.
            OutputDir (str): Path to the output directory.
            OutputFormat (str): Output format of the images e.g. "png".
            FirstPageOnly (bool): Whether to only extract the first page of the pdf.

            ImagePreprocessorConfig (dict): ImagePreprocessor config dictionary. Needs to contain the following keys:
                grey_scale (bool): Whether to convert the image to grey scale.
                remove_noise (bool): Whether to remove noise from the image.
                thresholding (bool): Whether to apply thresholding to the image.
                dilate (bool): Whether to apply dilation to the image.
                erode (bool): Whether to apply erosion to the image.
                opening (bool): Whether to apply opening to the image.
                canny (bool): Whether to apply canny edge detection to the image.
                deskew (bool): Whether to deskew the image.
                unsharp_masking (bool): Whether to apply unsharp masking to the image.
                rotate (bool): Whether to rotate the image.
            file_names_to_convert (list, optional): List of filenames to convert. Defaults to None.
    """

    img_preprocessor = ImagePreprocessor(preprocess_config["ImagePreprocessorConfig"])
    pdf2image_dir(pdf_dir=os.path.join(ROOT_DIR, preprocess_config["InputDir"]),
                  image_dir=os.path.join(ROOT_DIR, preprocess_config["OutputDir"]),
                  preprocessor=img_preprocessor,
                  file_ending=preprocess_config["OutputFormat"],
                  first_page_only=preprocess_config["FirstPageOnly"],
                  src_dir=SRC_DIR,
                  file_names_to_convert=file_names_to_convert)


def extract_bboxes_from_image_folder(extraction_config: dict,
                                     debug=False,
                                     image_extractor: "ImageExtractor" = None
                                     ):
    """Extracts all images from a folder and saves them to another folder.

    Reads the config/image_extractor_config.yml file and uses the ImageExtractor class to extract the images.
    The images are saved to the output directory with the same filename as the input image and an index.

    Args:
        extraction_config (dict): Extraction config dictionary. Needs to contain the following keys:
            InputDir (str): Path to the input directory.
            OutputDir (str): Path to the output directory.
            ImageExtractor (dict): ImageExtractor config dictionary. Needs to contain the following keys:
                cfg_pickle_path (str): Path to the config pickle file.
                model_path (str): Path to the model.
                threshold (float): Threshold for the model.
                device (str): Device to use e.g. "cpu" or "cuda".
        debug (bool, optional): Whether to visualize the bounding boxes. Defaults to False.
        image_extractor (ImageExtractor, optional): ImageExtractor object. Defaults to None.
    """
    if not image_extractor:
        # initialize image extractor
        extraction_config["ImageExtractor"]["cfg_pickle_path"] = os.path.join(ROOT_DIR,
                                                                              extraction_config["ImageExtractor"][
                                                                                  "cfg_pickle_path"])
        extraction_config["ImageExtractor"]["model_path"] = os.path.join(ROOT_DIR,
                                                                         extraction_config["ImageExtractor"][
                                                                             "model_path"])
        image_extractor = ImageExtractor(extraction_config["ImageExtractor"])

    img_dir = os.path.join(ROOT_DIR, extraction_config["InputDir"])
    output_dir = os.path.join(ROOT_DIR, extraction_config["OutputDir"])
    file_names = os.listdir(img_dir) if not debug else sample(os.listdir(img_dir), 10)
    for image_filename in tqdm(file_names):
        logger.debug(f"Extracting bboxes from {image_filename}")
        filename_without_ending = image_filename.split(".")[0]
        if debug:
            image_extractor.visualize(os.path.join(img_dir, image_filename))
        try:
            bboxes = image_extractor.cut_all_bboxes(os.path.join(img_dir, image_filename))
            logger.debug(f"Found {len(bboxes)} bboxes in {image_filename}")
            for index, bbox in enumerate(bboxes):
                save_path = os.path.join(output_dir, f"{filename_without_ending}_img{index}.png")
                if not os.path.exists(save_path):
                    cv2.imwrite(save_path, bbox)
        except Exception as e:
            logger.error(f"Error extracting bboxes from {image_filename}: {e}")


def parse_category_df_for_img_extraction(categories_csv_path):
    df = pd.read_csv(categories_csv_path, sep=',', index_col=0)
    # only keep filename and document category
    categories_df = df[['filename', 'document_category']]
    # keep all rows where document category is 'is a BP'
    categories_df = categories_df[categories_df['document_category'] == 'is a BP']
    # drop document category column
    categories_df = categories_df.drop(columns=['document_category'])
    return categories_df['filename']


def _match_img_file_with_pdf_file(config: dict):
    """Matches the image files with the pdf files.

    Args:
        output_dir (str): Path to the output directory.

    Returns:
        img_filenames (list): List of image filenames.
        pdf_filenames (list): List of pdf filenames.
        """
    output_dir = os.path.join(ROOT_DIR, config["OutputDir"])
    img_filenames, pdf_filenames = [], []
    for img_filename in os.listdir(output_dir):
        # only consider png files
        if not img_filename.endswith(".png"):
            continue
        # filename is structured as follows: <filename>_<page_number>_img<img_number>.png
        # we want to extract the filename and page number
        filename_split = img_filename.split("_")
        filename = filename_split[0]
        page_number = filename_split[1]
        if "img" in page_number:
            pdf_page = filename + ".pdf"
        else:
            # combine filename and page number to get the original pdf page
            pdf_page = filename + "_" + page_number + ".pdf"
        # append to list
        img_filenames.append(img_filename)
        pdf_filenames.append(pdf_page)
    return img_filenames, pdf_filenames
