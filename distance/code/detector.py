"""
Ultra-fast YOLOv5 ONNX inference engine using ONNX Runtime (CPU).
Eliminates PyTorch overhead and dependency issues completely.
Compatible with standalone PyInstaller executables and direct Python execution.
"""

import cv2
import numpy as np
import onnxruntime as ort
import os
import sys

class FastYoloDetector:
    def __init__(self, model_path="code/models/best.onnx"):
        # Resolve path for PyInstaller bundle or direct execution
        if not os.path.exists(model_path):
            base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            candidates = [
                os.path.join(base_dir, "code", "models", "best.onnx"),
                os.path.join(base_dir, "models", "best.onnx"),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "best.onnx"),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "code", "models", "best.onnx"),
                os.path.join(base_dir, "code", "yolo5", "best.onnx"),
                model_path
            ]
            for cand in candidates:
                if os.path.exists(cand):
                    model_path = cand
                    break
                
        # Configure optimized ONNX session
        opts = ort.SessionOptions()
        opts.intra_op_num_threads = 2
        opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        
        self.session = ort.InferenceSession(model_path, sess_options=opts, providers=['CPUExecutionProvider'])
        
    def detect(self, img_bgr, conf_thresh=0.25, nms_thresh=0.45):
        h, w = img_bgr.shape[:2]
        resized = cv2.resize(img_bgr, (480, 480))
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        inp = (rgb.astype(np.float32) / 255.0).transpose(2, 0, 1)[None, ...]
        
        out = self.session.run(None, {'images': inp})[0][0] # (14175, 8)
        
        obj_conf = out[:, 4]
        cls_scores = out[:, 5:]
        cls_ids = np.argmax(cls_scores, axis=1)
        cls_conf = np.max(cls_scores, axis=1) * obj_conf
        
        mask = cls_conf > conf_thresh
        filtered_boxes = out[mask]
        filtered_classes = cls_ids[mask]
        filtered_scores = cls_conf[mask]
        
        boxes_for_nms = []
        for b in filtered_boxes:
            cx, cy, bw, bh = b[:4]
            x = int((cx - bw / 2) * (w / 480.0))
            y = int((cy - bh / 2) * (h / 480.0))
            boxes_for_nms.append([x, y, int(bw * w / 480.0), int(bh * h / 480.0)])
            
        indices = cv2.dnn.NMSBoxes(boxes_for_nms, filtered_scores.tolist(), score_threshold=conf_thresh, nms_threshold=nms_thresh)
        
        tank_pos = None
        marker_pos = None
        tank_conf = 0.0
        marker_conf = 0.0
        
        for idx in indices:
            cls = int(filtered_classes[idx])
            score = float(filtered_scores[idx])
            bx, by, bw, bh = boxes_for_nms[idx]
            cx = bx + bw / 2.0
            cy = by + bh / 2.0
            
            # Class 0 or 1: player tank icon
            if (cls == 0 or cls == 1) and tank_pos is None:
                tank_pos = (cx, cy)
                tank_conf = score
            # Class 2: yellow squad marker
            elif cls == 2 and marker_pos is None:
                marker_pos = (cx, cy)
                marker_conf = score
                
        return tank_pos, marker_pos, tank_conf, marker_conf
