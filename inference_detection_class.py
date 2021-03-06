# https://colab.research.google.com/github/tensorflow/hub/blob/master/examples/colab/tf2_object_detection.ipynb#scrollTo=oi28cqGGFWnY
import os
import pathlib

import matplotlib
import matplotlib.pyplot as plt

import io
import scipy.misc
import numpy as np
from six import BytesIO
from PIL import Image, ImageDraw, ImageFont
from six.moves.urllib.request import urlopen

import tensorflow as tf
import tensorflow_hub as hub

from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils
from object_detection.utils import ops as utils_ops

from PIL import Image
from dataclasses import dataclass

@dataclass
class inferenceDectection():
    """Gets what is in the image and saves bounding boxes around items
    example:

    from inference_detection_class import inferenceDectection
    my_inference = inferenceDectection()
    my_dict = my_inference.classifyImage("/home/mycode/steven/keyboard.jpg")

    my_inference.saveToImage(file_path="/home/mycode/steven/keyboard/inference_detection")
    my_inference.showImage()
    """

    model_name: str = "CenterNet HourGlass104 Keypoints 512x512"
    min_threshold: float = .30

    def __post_init__(self):
        tf.get_logger().setLevel('INFO')
        PATH_TO_LABELS = './models/research/object_detection/data/mscoco_label_map.pbtxt'
        self.category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)

        ALL_MODELS = {
            'CenterNet HourGlass104 512x512' : 'https://tfhub.dev/tensorflow/centernet/hourglass_512x512/1',
            'CenterNet HourGlass104 Keypoints 512x512' : 'https://tfhub.dev/tensorflow/centernet/hourglass_512x512_kpts/1',
            'CenterNet HourGlass104 1024x1024' : 'https://tfhub.dev/tensorflow/centernet/hourglass_1024x1024/1',
            'CenterNet HourGlass104 Keypoints 1024x1024' : 'https://tfhub.dev/tensorflow/centernet/hourglass_1024x1024_kpts/1',
            'CenterNet Resnet50 V1 FPN 512x512' : 'https://tfhub.dev/tensorflow/centernet/resnet50v1_fpn_512x512/1',
            'CenterNet Resnet50 V1 FPN Keypoints 512x512' : 'https://tfhub.dev/tensorflow/centernet/resnet50v1_fpn_512x512_kpts/1',
            'CenterNet Resnet101 V1 FPN 512x512' : 'https://tfhub.dev/tensorflow/centernet/resnet101v1_fpn_512x512/1',
            'CenterNet Resnet50 V2 512x512' : 'https://tfhub.dev/tensorflow/centernet/resnet50v2_512x512/1',
            'CenterNet Resnet50 V2 Keypoints 512x512' : 'https://tfhub.dev/tensorflow/centernet/resnet50v2_512x512_kpts/1',
            'EfficientDet D0 512x512' : 'https://tfhub.dev/tensorflow/efficientdet/d0/1',
            'EfficientDet D1 640x640' : 'https://tfhub.dev/tensorflow/efficientdet/d1/1',
            'EfficientDet D2 768x768' : 'https://tfhub.dev/tensorflow/efficientdet/d2/1',
            'EfficientDet D3 896x896' : 'https://tfhub.dev/tensorflow/efficientdet/d3/1',
            'EfficientDet D4 1024x1024' : 'https://tfhub.dev/tensorflow/efficientdet/d4/1',
            'EfficientDet D5 1280x1280' : 'https://tfhub.dev/tensorflow/efficientdet/d5/1',
            'EfficientDet D6 1280x1280' : 'https://tfhub.dev/tensorflow/efficientdet/d6/1',
            'EfficientDet D7 1536x1536' : 'https://tfhub.dev/tensorflow/efficientdet/d7/1',
            'SSD MobileNet v2 320x320' : 'https://tfhub.dev/tensorflow/ssd_mobilenet_v2/2',
            'SSD MobileNet V1 FPN 640x640' : 'https://tfhub.dev/tensorflow/ssd_mobilenet_v1/fpn_640x640/1',
            'SSD MobileNet V2 FPNLite 320x320' : 'https://tfhub.dev/tensorflow/ssd_mobilenet_v2/fpnlite_320x320/1',
            'SSD MobileNet V2 FPNLite 640x640' : 'https://tfhub.dev/tensorflow/ssd_mobilenet_v2/fpnlite_640x640/1',
            'SSD ResNet50 V1 FPN 640x640 (RetinaNet50)' : 'https://tfhub.dev/tensorflow/retinanet/resnet50_v1_fpn_640x640/1',
            'SSD ResNet50 V1 FPN 1024x1024 (RetinaNet50)' : 'https://tfhub.dev/tensorflow/retinanet/resnet50_v1_fpn_1024x1024/1',
            'SSD ResNet101 V1 FPN 640x640 (RetinaNet101)' : 'https://tfhub.dev/tensorflow/retinanet/resnet101_v1_fpn_640x640/1',
            'SSD ResNet101 V1 FPN 1024x1024 (RetinaNet101)' : 'https://tfhub.dev/tensorflow/retinanet/resnet101_v1_fpn_1024x1024/1',
            'SSD ResNet152 V1 FPN 640x640 (RetinaNet152)' : 'https://tfhub.dev/tensorflow/retinanet/resnet152_v1_fpn_640x640/1',
            'SSD ResNet152 V1 FPN 1024x1024 (RetinaNet152)' : 'https://tfhub.dev/tensorflow/retinanet/resnet152_v1_fpn_1024x1024/1',
            'Faster R-CNN ResNet50 V1 640x640' : 'https://tfhub.dev/tensorflow/faster_rcnn/resnet50_v1_640x640/1',
            'Faster R-CNN ResNet50 V1 1024x1024' : 'https://tfhub.dev/tensorflow/faster_rcnn/resnet50_v1_1024x1024/1',
            'Faster R-CNN ResNet50 V1 800x1333' : 'https://tfhub.dev/tensorflow/faster_rcnn/resnet50_v1_800x1333/1',
            'Faster R-CNN ResNet101 V1 640x640' : 'https://tfhub.dev/tensorflow/faster_rcnn/resnet101_v1_640x640/1',
            'Faster R-CNN ResNet101 V1 1024x1024' : 'https://tfhub.dev/tensorflow/faster_rcnn/resnet101_v1_1024x1024/1',
            'Faster R-CNN ResNet101 V1 800x1333' : 'https://tfhub.dev/tensorflow/faster_rcnn/resnet101_v1_800x1333/1',
            'Faster R-CNN ResNet152 V1 640x640' : 'https://tfhub.dev/tensorflow/faster_rcnn/resnet152_v1_640x640/1',
            'Faster R-CNN ResNet152 V1 1024x1024' : 'https://tfhub.dev/tensorflow/faster_rcnn/resnet152_v1_1024x1024/1',
            'Faster R-CNN ResNet152 V1 800x1333' : 'https://tfhub.dev/tensorflow/faster_rcnn/resnet152_v1_800x1333/1',
            'Faster R-CNN Inception ResNet V2 640x640' : 'https://tfhub.dev/tensorflow/faster_rcnn/inception_resnet_v2_640x640/1',
            'Faster R-CNN Inception ResNet V2 1024x1024' : 'https://tfhub.dev/tensorflow/faster_rcnn/inception_resnet_v2_1024x1024/1',
            'Mask R-CNN Inception ResNet V2 1024x1024' : 'https://tfhub.dev/tensorflow/mask_rcnn/inception_resnet_v2_1024x1024/1'
            }

        model_handle = ALL_MODELS[self.model_name]
        print('loading model...')
        self.hub_model = hub.load(model_handle)
        print('model loaded!')


    def classifyImage(self, image_path):
        """Classify the Image

        Args:
            image_path (str): Full path to the image, can be url or local path

        Returns:
            dict: What was classified and anything over the threshold.
        """
        flip_image_horizontally = False
        convert_image_to_grayscale = False

        self.image_np = self.load_image_into_numpy_array(image_path)

        # Flip horizontally
        if(flip_image_horizontally):
            self.image_np[0] = np.fliplr(self.image_np[0]).copy()

        # Convert image to grayscale
        if(convert_image_to_grayscale):
            self.image_np[0] = np.tile(
                np.mean(self.image_np[0], 2, keepdims=True), (1, 1, 3)).astype(np.uint8)

        # running inference
        self.results = self.hub_model(self.image_np)
        self.result = {key:value.numpy() for key,value in self.results.items()}

        # Save results in a workable dict
        results_dict = {}
        for s_detect in self.result['detection_classes']:
            for my_i, my_detect in enumerate(s_detect):
                detection_score = self.result['detection_scores'][0][my_i]
                item_found = self.category_index[my_detect]['name']
                # Skip if threshold is too low
                if self.min_threshold > detection_score:
                    continue
                # Save new value to dictionary
                if results_dict.get(item_found) == None:
                    new_list = [detection_score]
                else:
                    new_list.append(detection_score)
                results_dict[item_found] = new_list
        print(f"Found in Image: {results_dict}")
        return results_dict



    def saveToImage(self, file_path=os.getcwd(), file_name="inf_image.png"):
        # VISUALIZE THE self.resultS
        COCO17_HUMAN_POSE_KEYPOINTS = [
            (0, 1),
            (0, 2),
            (1, 3),
            (2, 4),
            (0, 5),
            (0, 6),
            (5, 7),
            (7, 9),
            (6, 8),
            (8, 10),
            (5, 6),
            (5, 11),
            (6, 12),
            (11, 12),
            (11, 13),
            (13, 15),
            (12, 14),
            (14, 16)
            ]
        label_id_offset = 0
        self.image_np_with_detections = self.image_np.copy()

        # Use keypoints if available in detections
        keypoints, keypoint_scores = None, None
        if 'detection_keypoints' in self.result:
            keypoints = self.result['detection_keypoints'][0]
            keypoint_scores = self.result['detection_keypoint_scores'][0]

        viz_utils.visualize_boxes_and_labels_on_image_array(
            self.image_np_with_detections[0],
            self.result['detection_boxes'][0],
            (self.result['detection_classes'][0] + label_id_offset).astype(int),
            self.result['detection_scores'][0],
            self.category_index,
            use_normalized_coordinates=True,
            max_boxes_to_draw=200,
            min_score_thresh=self.min_threshold,
            agnostic_mode=False,
            keypoints=keypoints,
            keypoint_scores=keypoint_scores,
            keypoint_edges=COCO17_HUMAN_POSE_KEYPOINTS
            )

        local_path = file_path
        self.my_file = os.path.join(local_path, file_name)
        plt.figure(figsize=(24,32))
        plt.imshow(self.image_np_with_detections[0])
        plt.savefig(self.my_file)
        print(f"File saved to {self.my_file}")

    def showImage(self):
        img_PIL = Image.open(self.my_file)
        img_PIL.show()


    def load_image_into_numpy_array(self, path):
        """Load an image from file into a numpy array.

        Puts image into numpy array to feed into tensorflow graph.
        Note that by convention we put it into a numpy array with shape
        (height, width, channels), where channels=3 for RGB.

        Args:
            path: the file path to the image

        Returns:
            uint8 numpy array with shape (img_height, img_width, 3)
        """
        image = None
        if(path.startswith('http')):
            response = urlopen(path)
            image_data = response.read()
            image_data = BytesIO(image_data)
            image = Image.open(image_data)
        else:
            image_data = tf.io.gfile.GFile(path, 'rb').read()
            image = Image.open(BytesIO(image_data))

        (im_width, im_height) = image.size
        return np.array(image.getdata()).reshape(
            (1, im_height, im_width, 3)).astype(np.uint8)

