import sys

sys.path.append("/mnt/dtamboudisk/vision_assistant")

from agents.fusion.scene import Scene, SceneObject
from agents.reasoning.scene_interpreter import SceneInterpreter
from agents.reasoning.decision_engine import DecisionEngine

def test():
    scene = Scene()
    # Add a random object that has NO rule (e.g. wall_switch)
    switch = SceneObject(
        source="yolo",
        source_model="wall_switch_detection",
        category="objects",
        label="wall_switch",
        confidence=0.9,
        bbox=[400, 100, 640, 500],
        backend="onnx"
    )
    scene.add("objects", switch)
    
    interpreter = SceneInterpreter()
    report = interpreter.interpret(scene)
    
    engine = DecisionEngine()
    decision = engine.decide(report)
    
    print("Report Summary:", report.summary)
    print("Decision Message:", decision.message)
    print("Decision Action:", decision.action)

if __name__ == "__main__":
    test()
