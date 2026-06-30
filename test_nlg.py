import sys

sys.path.append("/mnt/dtamboudisk/vision_assistant")

from agents.fusion.scene import Scene, SceneObject
from agents.reasoning.scene_interpreter import SceneInterpreter
from agents.reasoning.decision_engine import DecisionEngine

def test():
    scene = Scene()
    
    # Person 1 (Center, medium distance)
    p1 = SceneObject(
        source="yolo", source_model="people_detector", category="persons", label="person",
        confidence=0.9, bbox=[200, 100, 440, 500], backend="onnx"
    )
    
    # Person 2 (Right, very close, approaching)
    p2 = SceneObject(
        source="yolo", source_model="people_detector", category="persons", label="person",
        confidence=0.9, bbox=[450, 100, 640, 640], backend="onnx"
    )
    p2.metadata["approaching"] = True
    
    scene.add("persons", p1)
    scene.add("persons", p2)
    
    interpreter = SceneInterpreter()
    report = interpreter.interpret(scene)
    
    print("Report Summary:", report.summary)

if __name__ == "__main__":
    test()
