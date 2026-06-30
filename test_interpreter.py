import sys
import os

# Add root to python path
sys.path.append("/mnt/dtamboudisk/vision_assistant")

from agents.fusion.scene import Scene, SceneObject
from agents.reasoning.scene_interpreter import SceneInterpreter

def test():
    scene = Scene()
    # Create a person object (close, right)
    # [x1, y1, x2, y2]
    # width = x2-x1, height = y2-y1
    # area = 400 * 400 = 160,000 / (640*640=409600) = 0.39 (medium/close)
    # cx = 400 + 400/2 = 600 (> 640*2/3 = 426) -> droite
    person = SceneObject(
        source="yolo",
        source_model="people_detector",
        category="persons",
        label="person",
        confidence=0.9,
        bbox=[400, 100, 640, 500],
        backend="onnx"
    )
    scene.add("persons", person)
    
    interpreter = SceneInterpreter()
    report = interpreter.interpret(scene)
    print("Report Summary:", report.summary)
    print("Report Events:", report.events)

if __name__ == "__main__":
    test()
