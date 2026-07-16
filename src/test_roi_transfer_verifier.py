from __future__ import annotations

import cv2
import numpy as np

from src.roi_transfer_verifier import measure_occupancy


def test_occupancy_increases_when_item_enters_tray():
    reference = np.full((200, 300, 3), (80, 120, 150), dtype=np.uint8)
    current = reference.copy()
    cv2.rectangle(current, (100, 70), (210, 140), (220, 30, 40), -1)
    polygon = np.asarray([[20, 20], [280, 20], [280, 180], [20, 180]], dtype=np.int32)

    empty, _, empty_components = measure_occupancy(reference, reference, polygon)
    occupied, _, occupied_components = measure_occupancy(reference, current, polygon)

    assert empty == 0
    assert empty_components == []
    assert occupied > 0.1
    assert occupied_components[0] > 7000
