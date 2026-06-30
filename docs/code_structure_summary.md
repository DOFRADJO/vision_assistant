# Sommaire du code par dossier
Ce document présente la structure du code source du projet, classée par dossier principal.

Chaque fichier est décrit brièvement à partir de sa docstring ou de son rôle apparent.

## agents

- `__init__.py` : Agent orchestration package for Vision Assistant.
### agents/coordinator

- `__init__.py` : Coordinator agent package for orchestrating the Vision Assistant pipeline.
- `coordinator.py` : Coordinator agent orchestrating the multi-agent pipeline.
- `registry.py` : Registry for registering detector models and runtime state.

### agents/fusion

- `__init__.py` : Fusion agent package for building a unified scene from raw detections.
- `fusion_agent.py` : Fusion agent for merging raw detector outputs into a single scene.
- `labels.py` : Registry for model labels found under the workspace `models/` directory.
- `scene.py` : Scene and object models for unified detection fusion.
- `scene_builder.py` : Scene Builder for turning raw model outputs into a unified Scene.

### agents/memory

- `__init__.py` : Memory agent package for deduplicating spoken announcements.
- `history.py` : Fichier history.py du projet.
- `memory_agent.py` : Memory agent for de-duplication, cooldowns, and history.

### agents/navigation

- `navigation_agent.py` : Fichier navigation_agent.py du projet.

### agents/reasoning

- `__init__.py` : Reasoning agent for rule-based analysis of visual predictions.
- `conversation_manager.py` : Conversation Manager — stabilises vocal announcements.
- `danger_rules.py` : Scene analysis rules for the reasoning agent.
- `decision_engine.py` : Decision engine that chooses a single action from a SceneReport.
- `priority_agent.py` : Priority agent for selecting the most relevant events.
- `priority_manager.py` : Priority ranking for reasoning messages.
- `reasoning_agent.py` : Reasoning agent converting a fused scene into prioritized events.
- `scene_interpreter.py` : Scene interpreter for producing a high-level scene report.
- `scene_memory.py` : Scene memory for tracking recent scene state and emitting only important changes.
- `scene_rules.py` : Business rules for interpreting a visual scene.

### agents/speech

- `__init__.py` : Speech agent package for audio feedback.
- `speech_agent.py` : Speech agent with prioritized queue and non-blocking output.
- `speech_planner.py` : Speech planner for translating events into natural spoken phrases.
- `tts.py` : Fichier tts.py du projet.

### agents/tracking

- `__init__.py` : Tracking agent package for maintaining identity across frames.
- `tracking_agent.py` : Tracking agent for assigning stable IDs to scene objects.

### agents/vision

- `__init__.py` : Vision agent package for model management and prediction.
- `model_loader.py` : Real model loader for ONNX and PyTorch detectors.
- `model_loader_backup.py` : BACKUP - This is a reference of what the cleaned model_loader.
- `vision_agent.py` : Vision agent responsible for loading models and producing raw detections.


## app

### app/api

- `__init__.py` : FastAPI application package for Vision Assistant.
- `main.py` : FastAPI endpoints for Vision Assistant.

### app/desktop

- `__init__.py` : Desktop user interface package for Vision Assistant.
- `desktop_app.py` : Desktop OpenCV application for live vision assistant output.

### app/mobile

- `.eslintrc.js` : Fichier .eslintrc.js du projet.
- `.prettierrc.js` : Fichier .prettierrc.js du projet.
- `App.tsx` : Fichier App.tsx du projet.
- `babel.config.js` : Fichier babel.config.js du projet.
- `index.js` : Fichier index.js du projet.
- `jest.config.js` : Fichier jest.config.js du projet.
- `metro.config.js` : Fichier metro.config.js du projet.

### app/mobile/__tests__

- `App.test.tsx` : Fichier App.test.tsx du projet.

### app/mobile/src

- `App.tsx` : Fichier App.tsx du projet.

### app/mobile/src/agents

- `MemoryAgent.ts` : Fichier MemoryAgent.ts du projet.
- `ReasoningAgent.ts` : Fichier ReasoningAgent.ts du projet.

### app/mobile/src/components

- `BoundingBoxOverlay.tsx` : Fichier BoundingBoxOverlay.tsx du projet.

### app/mobile/src/utils

- `YoloPostProcess.ts` : Fichier YoloPostProcess.ts du projet.


## core

- `__init__.py` : Core utilities and camera subsystem for Vision Assistant.
- `camera.py` : Camera manager for live video, files, and IP streams.
- `distance_estimator.py` : Fichier distance_estimator.py du projet.
- `logger.py` : Professional logging setup for Vision Assistant.
- `object_counter.py` : Fichier object_counter.py du projet.
- `scene_analyzer.py` : Fichier scene_analyzer.py du projet.
- `tracker.py` : Tracking utilities with IoU fallback and optional ByteTrack support.
- `utils.py` : Shared utilities for Vision Assistant.

## racine

- `config.py` : Central configuration for Vision Assistant.
- `run.py` : Entry point for Vision Assistant desktop execution.
- `setup.py` : Fichier setup.py du projet.
- `test_fallback.py` : Fichier test_fallback.py du projet.
- `test_interpreter.py` : Fichier test_interpreter.py du projet.
- `test_nlg.py` : Fichier test_nlg.py du projet.
- `test_nlg2.py` : Fichier test_nlg2.py du projet.

## scripts

- `debug_model.py` : Debug the ONNX detector pipeline and save annotated output for inspection.
- `integrate_model.py` : Integrate a student-trained detector into the platform.

## tests

- `test_conversation_manager.py` : Unit tests for ConversationManager.
- `test_integration.py` : Integration Tests for Model Integration System.
### tests/integration

- `test_pipeline.py` : Fichier test_pipeline.py du projet.

### tests/unit

- `test_camera_source.py` : Unit tests for camera source resolution and configuration.
- `test_config.py` : Unit tests for Vision Assistant configuration.
- `test_decision_engine.py` : Unit tests for DecisionEngine behavior.
- `test_memory_agent.py` : Unit tests for memory agent deduplication.
- `test_model_loader.py` : Unit tests for model loader behavior.
- `test_reasoning.py` : Fichier test_reasoning.py du projet.
- `test_reasoning_agent.py` : Unit tests for reasoning rules.
- `test_scene_builder.py` : Unit tests for the scene builder and scene model.
- `test_scene_interpreter.py` : Unit tests for scene interpretation and report generation.
- `test_speech_agent.py` : Unit tests for SpeechAgent behavior.
- `test_tracker_motion.py` : Tests for stable IDs and temporal approach estimation.
- `test_utils.py` : Unit tests for core utility functions.
- `test_vision_agent.py` : Unit tests for VisionAgent behavior.

