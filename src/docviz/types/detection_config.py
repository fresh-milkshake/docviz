from dataclasses import dataclass


@dataclass
class DetectionConfig:
    """
    Configuration for detection.
    
    Attributes:
        imagesize (int): The size of the image to detect.
        confidence (float): The confidence threshold for the detection.
        device (str): The device to use for the detection.
    """

    imagesize: int
    confidence: float
    device: str
