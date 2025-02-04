import os
import tempfile

import cv2
import pytest

from img_extraction.extraction_utility import extract_bboxes_from_image_folder
from img_extraction.image_extractor import ImageExtractor
from utility.config_utils import read_yaml

MODEL_CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                 "..", "config", "image_extractor_config.yml"))


def check_model_available():
    if not os.path.exists(MODEL_CONFIG_PATH):
        pytest.skip("Config not available")
    config = read_yaml(MODEL_CONFIG_PATH)
    image_extractor_config = config["Extraction"]["ImageExtractor"]

    if not os.path.exists(image_extractor_config["model_path"]):
        pytest.skip(f"Model not available at {image_extractor_config['model_path']}")

    if not os.path.exists(image_extractor_config["cfg_pickle_path"]):
        pytest.skip(f"Config not available at {image_extractor_config['cfg_pickle_path']}")


class TestImageExtraction:
    def setup_class(self):
        check_model_available()
        config = read_yaml(MODEL_CONFIG_PATH)
        self.image_extractor = ImageExtractor(config["Extraction"]["ImageExtractor"])

        self.test_data_path = os.path.join(os.path.dirname(__file__), "test_data")

        self.test_data_input_dir = os.path.join(self.test_data_path, "test_images")

    def test_image_extraction(self):
        for file in os.listdir(self.test_data_input_dir):
            if file.endswith(".png"):
                image_path = os.path.join(self.test_data_input_dir, file)
                n_bboxes = int(file.split("_")[1].split(".")[0])
                image = cv2.imread(image_path)
                bboxes = self.image_extractor(image)
                assert len(bboxes) == n_bboxes

    def test_folder_extraction(self):
        # with tempdir
        with tempfile.TemporaryDirectory() as tempdir:
            test_config = {"InputDir": self.test_data_input_dir,
                           "OutputDir": tempdir,
                           }
            extract_bboxes_from_image_folder(test_config, image_extractor=self.image_extractor)
            assert len(os.listdir(tempdir)) == 4
