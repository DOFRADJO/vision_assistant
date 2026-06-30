"""Coordinator agent orchestrating the multi-agent pipeline."""
from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

from agents.fusion.scene_builder import SceneBuilder
from agents.reasoning.scene_interpreter import SceneInterpreter
from agents.reasoning.conversation_manager import ConversationManager
from agents.reasoning.decision_engine import DecisionEngine
from agents.reasoning.scene_memory import SceneMemory
from agents.speech.speech_agent import SpeechAgent
from agents.speech.speech_planner import SpeechPlanner
from agents.tracking.tracking_agent import TrackingAgent
from agents.vision.vision_agent import VisionAgent
from agents.vision.model_loader import ModelLoader
from config import VisionAssistantConfig

logger = logging.getLogger(__name__)


class Coordinator:
    def __init__(self, config: Optional[VisionAssistantConfig] = None, model_loader: Optional[ModelLoader] = None) -> None:
        self.config = config or VisionAssistantConfig()
        self.model_loader = model_loader or ModelLoader(self.config.paths.models_dir)
        self.vision_agent = VisionAgent(model_loader=self.model_loader, config=self.config)
        self.scene_builder = SceneBuilder()
        self.scene_interpreter = SceneInterpreter()
        self.decision_engine = DecisionEngine()
        self.tracking_agent = TrackingAgent(
            tracker_type=self.config.tracking.tracker_type,
            iou_threshold=self.config.tracking.iou_threshold,
            max_age=self.config.tracking.max_age,
            min_hits=self.config.tracking.min_hits,
        )
        self.scene_memory = SceneMemory()
        self.conversation_manager = ConversationManager(min_announce_interval=3.0)
        self.speech_planner = SpeechPlanner()
        self.speech_agent = SpeechAgent(config=self.config)
        self.last_result: Dict[str, Any] = {}
        self.frame_count = 0

    def initialize(self) -> None:
        if not self.model_loader.detectors:
            self.vision_agent.load_models()
        loaded_models = sorted(self.model_loader.detectors.keys())
        self._log_startup(loaded_models)
        if loaded_models:
            logger.info("Loaded %d models for inference", len(loaded_models))
        else:
            logger.warning("No models were loaded. Check models directory: %s", self.model_loader.models_dir)

    def _log_startup(self, loaded_models: List[str]) -> None:
        camera_name = "Laptop Camera" if self.config.camera.source_type == "webcam" else self.config.camera.source_type
        logger.info("%s", "=" * 40)
        logger.info("Vision Assistant")
        logger.info("%s", "=" * 40)
        logger.info("Camera : %s", camera_name)
        logger.info("Resolution : %sx%s", self.config.camera.resize_width, self.config.camera.resize_height)
        logger.info("FPS : %s", self.config.camera.fps)
        logger.info("%s", "=" * 40)
        logger.info("Loading Models")
        logger.info("%s", "=" * 40)
        for model_name in loaded_models:
            logger.info("✓ %s", model_name)
        logger.info("Total Models : %d", len(loaded_models))
        logger.info("%s", "=" * 40)
        logger.info("Ready")

    def process_frame(self, frame: Any) -> Dict[str, Any]:
        frame_start = time.perf_counter()
        self.frame_count += 1

        original_detectors = self.model_loader.detectors.copy()
        try:
            if self.frame_count % 2 != 0:
                # Modèles critiques (frames impaires)
                active_models = {'obstacle_detector', 'people_detector', 'people_tracking'}
            elif self.frame_count % 4 == 0:
                # Modèles extérieurs (frames paires divisibles par 4)
                active_models = {'cross_traffic_detector', 'traffic_detector', 'sidewalk_detector'}
            else:
                # Modèles intérieurs (les autres frames paires)
                active_models = {'electronic_detector', 'food_detector', 'wall_switch_detection'}
                
            self.model_loader.detectors = {k: v for k, v in original_detectors.items() if k in active_models}
            vision_output = self.vision_agent.predict(frame, frame_id=self.frame_count)
        finally:
            self.model_loader.detectors = original_detectors

        vision_time = time.perf_counter() - frame_start

        scene = self.scene_builder.build_scene(vision_output.get("raw_predictions", {}))
        fusion_time = time.perf_counter() - frame_start - vision_time

        tracked_scene = self.tracking_agent.track(scene)
        tracking_time = time.perf_counter() - frame_start - vision_time - fusion_time

        self.scene_memory.update(tracked_scene)
        report = self.scene_interpreter.interpret(tracked_scene)
        reasoning_time = time.perf_counter() - frame_start - vision_time - fusion_time - tracking_time

        # Attach the scene summary so ConversationManager can read real counts.
        report.scene_summary = {k: v for k, v in tracked_scene.summary().items()}

        # --- ConversationManager gate ---
        announce_decision = self.conversation_manager.should_announce(report)

        filtered: List[Dict[str, Any]] = []
        if announce_decision.allowed:
            decision = self.decision_engine.decide(report)
            planned = self.speech_planner.plan(decision)
            for message in planned:
                if self.scene_memory.should_speak(str(message.get("message", ""))):
                    filtered.append(message)
            for message in filtered:
                self.speech_agent.speak(message["message"], priority=message.get("priority", 1))
        else:
            decision = self.decision_engine.decide(report)  # keep state advancing
            planned = []

        speech_time = time.perf_counter() - frame_start - vision_time - fusion_time - tracking_time - reasoning_time
        elapsed = time.perf_counter() - frame_start
        fps = 1.0 / max(elapsed, 1e-6)

        summary = tracked_scene.summary()
        logger.info(
            "Frame : %d | Inference : %.0f ms | FPS : %.2f | Scene : %s | Changed : %s | Events : %s | Spoken : %s",
            self.frame_count,
            vision_time * 1000.0,
            fps,
            {k: v for k, v in summary.items() if v > 0},
            self.scene_memory.has_changed(),
            report.events,
            [message.get("message") for message in filtered],
        )

        result = {
            "status": "ok",
            "frame": self.frame_count,
            "timestamp": vision_output.get("timestamp"),
            "detections": vision_output.get("detections", []),
            "scene": summary,
            "tracked_scene": tracked_scene.to_dict(),
            "scene_report": report.to_dict(),
            "decision": decision.__dict__ if decision is not None else {},
            "events": report.events,
            "recommendations": report.recommendations,
            "planned": planned,
            "spoken": filtered,
            "scene_changed": self.scene_memory.has_changed(),
            "fps": fps,
        }
        self.last_result = result
        return result
