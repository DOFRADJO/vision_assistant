import sys

sys.path.append("/mnt/dtamboudisk/vision_assistant")

from agents.fusion.scene import Scene, SceneObject
from agents.reasoning.scene_interpreter import SceneInterpreter

def test():
    scene = Scene()
    
    # Person
    p1 = SceneObject(
        source="yolo", source_model="people_detector", category="persons", label="person",
        confidence=0.9, bbox=[200, 100, 440, 500], backend="onnx"
    )
    
    # Sidewalk
    s1 = SceneObject(
        source="yolo", source_model="sidewalk_detector", category="sidewalks", label="sidewalk",
        confidence=0.9, bbox=[0, 400, 640, 640], backend="onnx"
    )
    
    # Food
    f1 = SceneObject(
        source="yolo", source_model="food_detector", category="food", label="avocado",
        confidence=0.9, bbox=[100, 100, 200, 200], backend="onnx"
    )
    
    scene.add("persons", p1)
    scene.add("sidewalks", s1)
    scene.add("food", f1)
    
    interpreter = SceneInterpreter()
    report = interpreter.interpret(scene)
    
    print("Report Summary:", report.summary)

if __name__ == "__main__":
    test()
