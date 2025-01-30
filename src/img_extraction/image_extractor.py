import os
import pickle

import cv2
import numpy as np
from detectron2.engine import DefaultPredictor
from detectron2.utils.visualizer import Visualizer

from utility.config_utils import get_project_root_path

ROOT_DIR = get_project_root_path()

def _get_image(image):
    if isinstance(image, str):
        image = cv2.imread(image)
    return image


class ImageExtractor:
    """Cuts all bounding boxes from an image."""

    def __init__(self, config: dict):
        """Initializes the image extractor.

        Args:
            config (dict): Config dictionary. Needs to contain the following keys:
                cfg_pickle_path (str): Path to the config pickle file.
                model_path (str): Path to the model.
                threshold (float): Threshold for the model.
                device (str): Device to use e.g. "cpu" or "cuda".
        """
        # load config from the pickle file
        config_path = os.path.abspath(os.path.join(ROOT_DIR, config["cfg_pickle_path"]))
        with open(config_path, 'rb') as f:
            self.cfg = pickle.load(f)

        self.cfg.MODEL.WEIGHTS = os.path.join(config["model_path"])  # path to the trained model
        self.cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = config["threshold"]  # threshold whether to keep a prediction
        self.cfg.MODEL.DEVICE = config["device"]
        self.predictor = DefaultPredictor(self.cfg)

    def __call__(self, image: "np.ndarray | str") -> "list":
        """Extracts the bounding boxes coordinates from an image.

        Args:
            image (np.array |  str) : Image as numpy array, CV2 format. Or image path.

        Returns:
            list: List of bounding box coordinates. [x, y, w, h]
        """
        image = _get_image(image)

        outputs = self.predict(image)
        return outputs["instances"].pred_boxes.tensor

    def predict(self, image: "np.array | str") -> "dict":
        """Predicts the bounding boxes of an image.

        Uses the detectron2 predictor to predict the bounding boxes of an image.

        Args:
            image (np.array |  str) : Image as numpy array, CV2 format. Or image path.

        Returns:
            dict: Dictionary containing the bounding boxes. The output is in detectron2 format
             https://detectron2.readthedocs.io/tutorials/models.html#model-output-format
        """
        image = _get_image(image)
        outputs = self.predictor(image)
        return outputs

    def visualize(self, image: "np.array | str"):
        """
        Visualizes the bounding boxes contained an image of a pdf.

        Args:
            image (np.array |  str) : Image as numpy array, CV2 format. Or image path.

        """
        image = _get_image(image)
        outputs = self.predict(image)
        v = Visualizer(image[:, :, ::-1],  # BGR -> RGB
                       scale=0.5,
                       )
        out = v.draw_instance_predictions(outputs["instances"])
        # get the image from the output
        img = out.get_image()[:, :, ::-1]
        cv2.imshow("test", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def cut_all_bboxes(self, image: "np.array | str") -> "list":
        """Cuts all bounding boxes from an image.

        Args:
            image (np.array |  str) : Image as numpy array, CV2 format. Or image path.

        Returns:
            bboxes list[np.array]: List of the images inside the located bounding boxes.
        """

        image = _get_image(image)
        bboxes_coordinates = self(image)
        return [slice_bbox_from_image(image, bbox) for bbox in bboxes_coordinates]


def slice_bbox_from_image(img: "np.array", bbox: list, padding: int = 10) -> "np.array":
    """ Slice a bounding box from an image.

    Args:
        img (np.array): Image as numpy array. CV2 format.
        bbox (list): Bounding box as list of coordinates.
        padding (int, optional): Padding around the bounding box. Defaults to 10.

    Returns:
        np.array: Bounding box as numpy array.
    """
    bbox = [int(x) for x in bbox]  # int for slicing
    x, y, w, h = bbox
    # check if padded coords are in image
    if x - padding < 0 or y - padding < 0 or x + w + padding > img.shape[1] or y + h + padding > img.shape[0]:
        # return without padding
        return img[y:y + h, x:x + w]
    img_bbox = img[y - padding:y + h + padding, x - padding:x + w + padding]
    return img_bbox
