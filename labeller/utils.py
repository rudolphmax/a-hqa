from __future__ import annotations

import csv
from pathlib import Path
from typing import TYPE_CHECKING

import cv2
import numpy as np
from PIL import Image

if TYPE_CHECKING:
  from streamlit.delta_generator import DeltaGenerator
  from PIL.Image import Image as ImageType


# Create a csv file for storing labels
def prepare_label_csv(cols: list[str]) -> None:
  p = Path("data/validation_labels.csv")

  with p.open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(cols)

def preprocess_image(img: ImageType) -> tuple[ImageType, ImageType, ImageType]:
  width, height = img.size
  dpi = img.info.get("dpi", (72, 72))

  # Load image
  image_vert_lines = cv2.cvtColor(np.array(img.copy()), cv2.COLOR_RGB2BGR)
  image_hor_lines = cv2.cvtColor(np.array(img.copy()), cv2.COLOR_RGB2BGR)

  line_offset = (0.5 / 2.54) * dpi[0]

  line_x = 0
  while line_x < width:
    cv2.line(image_vert_lines, (int(line_x), 0), (int(line_x), height), (255, 0, 0), 2)
    line_x += line_offset

  line_y = 0
  while line_y < height:
    cv2.line(image_hor_lines, (0, int(line_y)), (width, int(line_y)), (255, 0, 0), 2)
    line_y += line_offset

  return img, Image.fromarray(image_vert_lines), Image.fromarray(image_hor_lines)
