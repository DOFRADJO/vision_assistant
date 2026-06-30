# Référence enrichie du code
Ce document liste les fichiers source du projet par ordre alphabétique et décrit les responsabilités et le comportement de chaque fonction et classe.

## agents/__init__.py

- Description du module : Agent orchestration package for Vision Assistant.

## agents/coordinator/__init__.py

- Description du module : Coordinator agent package for orchestrating the Vision Assistant pipeline.

## agents/coordinator/coordinator.py

- Description du module : Coordinator agent orchestrating the multi-agent pipeline.

- Classe `Coordinator` (ligne 23) : Classe de type Coordinator.
  - Méthode `__init__(self, config, model_loader)` (ligne 24) : Initialise. gère des cas conditionnels; met à jour des variables internes; appelle ConversationManager, DecisionEngine, SpeechAgent, SpeechPlanner, TrackingAgent, VisionAgent, VisionAssistantConfig, modèle, scène.
  - Méthode `initialize(self)` (ligne 44) : Initialise. gère des cas conditionnels; met à jour des variables internes; appelle _log_startup, info, keys, modèle, sorted, warning.
  - Méthode `_log_startup(self, loaded_models)` (ligne 54) : Enregistre startup. parcourt des collections; gère des cas conditionnels; met à jour des variables internes; appelle info.
  - Méthode `process_frame(self, frame)` (ligne 71) : Traite une trame complète : inférence, fusion, suivi, interprétation et planification vocale. parcourt des collections; gère des cas conditionnels; gère des exceptions; met à jour des variables internes; retourne un résultat; appelle append, copy, decide, get, has_changed, info, interpret, items, perf_counter, plan, predict, scène, should_announce, should_speak, speak, summary, to_dict, track, update.

## agents/coordinator/registry.py

- Description du module : Registry for registering detector models and runtime state.

- Classe `RegisteredModel` (ligne 9) : Classe de type RegisteredModel.

- Classe `ModelRegistry` (ligne 15) : Gère un registre de model.
  - Méthode `__init__(self)` (ligne 16) : Initialise. met à jour des variables internes.
  - Méthode `register(self, model)` (ligne 19) : Enregistre. met à jour des variables internes.
  - Méthode `list_models(self)` (ligne 22) : Liste models. retourne un résultat; appelle values.
  - Méthode `get(self, name)` (ligne 25) : Récupère. retourne un résultat; appelle get.

## agents/fusion/__init__.py

- Description du module : Fusion agent package for building a unified scene from raw detections.

## agents/fusion/fusion_agent.py

- Description du module : Fusion agent for merging raw detector outputs into a single scene.

- Classe `FusionAgent` (ligne 13) : Combine raw detector outputs into a single scene representation.
  - Méthode `__init__(self, scene_builder)` (ligne 16) : Initialise. gère des cas conditionnels; met à jour des variables internes; appelle scène.
  - Méthode `fuse(self, raw_predictions)` (ligne 19) : Fusionne. retourne un résultat; appelle scène.

## agents/fusion/labels.py

- Description du module : Registry for model labels found under the workspace `models/` directory.

- Classe `LabelsRegistry` (ligne 12) : Gère un registre de labels.
  - Méthode `__init__(self, models_dir)` (ligne 15) : Initialise. met à jour des variables internes; appelle _load.
  - Méthode `get_instance(cls, models_dir)` (ligne 22) : Récupère instance. gère des cas conditionnels; met à jour des variables internes; retourne un résultat; appelle label.
  - Méthode `_load(self)` (ligne 27) : Charge. lit ou écrit des données; parcourt des collections; gère des cas conditionnels; utilise un gestionnaire de contexte; gère des exceptions; met à jour des variables internes; retourne un résultat; appelle add, isdir, isfile, join, listdir, lower, open, readlines, strip.
  - Méthode `has_label(self, label)` (ligne 49) : Vérifie qu’un label existe dans le registre de labels. gère des cas conditionnels; retourne un résultat; appelle lower.
  - Méthode `labels_for_model(self, model_name)` (ligne 52) : Récupère les labels associés à un modèle. retourne un résultat; appelle get.

## agents/fusion/scene.py

- Description du module : Scene and object models for unified detection fusion.

- Classe `SceneObject` (ligne 10) : A single detected object enriched for scene understanding.
  - Méthode `__post_init__(self)` (ligne 27) : Fonction `__post_init__` du module. gère des cas conditionnels; met à jour des variables internes.

- Classe `Scene` (ligne 38) : A unified scene representation consumed by reasoning and speech planning.
  - Méthode `add(self, bucket, obj)` (ligne 56) : Ajoute. gère des cas conditionnels; appelle append, getattr, hasattr, setdefault.
  - Méthode `remove(self, obj, bucket)` (ligne 63) : Supprime. gère des cas conditionnels; met à jour des variables internes; appelle _find_bucket_for, get, getattr, hasattr, remove.
  - Méthode `get(self, bucket)` (ligne 78) : Récupère. gère des cas conditionnels; retourne un résultat; appelle get, getattr, hasattr.
  - Méthode `count(self, bucket)` (ligne 83) : Compte. gère des cas conditionnels; retourne un résultat; appelle get.
  - Méthode `summary(self)` (ligne 88) : Retourne un résumé. met à jour des variables internes; retourne un résultat; appelle items, update.
  - Méthode `to_dict(self)` (ligne 107) : Convertit l’objet en dictionnaire pour sérialisation ou rapport. met à jour des variables internes; retourne un résultat; appelle asdict, items, summary.
  - Méthode `_find_bucket_for(self, obj)` (ligne 130) : Fonction `_find_bucket_for` du module. parcourt des collections; gère des cas conditionnels; retourne un résultat; appelle getattr, hasattr, items, summary.

## agents/fusion/scene_builder.py

- Description du module : Scene Builder for turning raw model outputs into a unified Scene.

- Fonction `_normalize_text(value)` (ligne 74) : Normalise text. gère des cas conditionnels; retourne un résultat; appelle lower, strip.

- Fonction `_bucket_for(source, label, category_map)` (ligne 78) : Classe for. parcourt des collections; gère des cas conditionnels; met à jour des variables internes; retourne un résultat; appelle _normalize_text, endswith, items.

- Fonction `_normalize_bbox(value)` (ligne 101) : Normalise bbox. gère des cas conditionnels; gère des exceptions; met à jour des variables internes; retourne un résultat; appelle all, get, isinstance.

- Classe `SceneBuilder` (ligne 124) : Build a unified scene from raw model outputs.
  - Méthode `__init__(self, category_map)` (ligne 127) : Initialise. gère des cas conditionnels; met à jour des variables internes.
  - Méthode `build_scene(self, raw_predictions)` (ligne 130) : Construit une scène unifiée à partir des prédictions brutes des modèles. travaille sur la représentation de la scène; parcourt des collections; gère des cas conditionnels; met à jour des variables internes; retourne un résultat; appelle _bucket_for, add, boîte de délimitation, debug, get, isinstance, items, modèle, scène, setdefault, time.
  - Méthode `_iou(first, second)` (ligne 157) : Fonction `_iou` du module. gère des cas conditionnels; met à jour des variables internes; retourne un résultat.
  - Méthode `_remove_cross_model_duplicates(self, scene, threshold)` (ligne 168) : Keep the strongest overlapping detection produced by two models.
  - Méthode `summarize(self, raw_predictions)` (ligne 187) : Retourne un résumé simplifié de l’état actuel de la scène. retourne un résultat; appelle scène, summary.

## agents/memory/__init__.py

- Description du module : Memory agent package for deduplicating spoken announcements.

## agents/memory/history.py

- Description du module : module Python du projet.

## agents/memory/memory_agent.py

- Description du module : Memory agent for de-duplication, cooldowns, and history.

- Classe `MemoryAgent` (ligne 11) : Agent responsable de la logique memory.
  - Méthode `__init__(self, config)` (ligne 12) : Initialise. gère des cas conditionnels; met à jour des variables internes; appelle VisionAssistantConfig, deque.
  - Méthode `should_emit(self, message)` (ligne 18) : Détermine si un message vocal doit être émis en appliquant des règles de cooldown et de priorité. gère des cas conditionnels; met à jour des variables internes; retourne un résultat; appelle append, get, time.
  - Méthode `get_history(self)` (ligne 53) : Récupère l’historique des messages ou événements enregistrés. retourne un résultat.

## agents/navigation/navigation_agent.py

- Description du module : module Python du projet.

## agents/reasoning/__init__.py

- Description du module : Reasoning agent for rule-based analysis of visual predictions.

## agents/reasoning/conversation_manager.py

- Description du module : Conversation Manager — stabilises vocal announcements.

- Classe `CountBucket` (ligne 36) : Coarse quantisation of an object count.
  - Méthode `from_count(n)` (ligne 43) : Quantifie un compte d’objets en bucket NONE/ONE/MULTIPLE. gère des cas conditionnels; retourne un résultat.

- Classe `AnnouncementDecision` (ligne 56) : Result of :py:meth:`ConversationManager.should_announce`.

- Classe `ConversationManager` (ligne 98) : Gate that decides whether a scene report warrants a new announcement.
  - Méthode `__init__(self, min_announce_interval)` (ligne 109) : Initialise. met à jour des variables internes.
  - Méthode `should_announce(self, scene_report)` (ligne 124) : Decide whether *scene_report* deserves a new vocal announcement.
  - Méthode `announced_buckets(self)` (ligne 204) : Read-only view of the last announced bucket per category.
  - Méthode `last_announce_time(self)` (ligne 209) : Fonction `last_announce_time` du module. gère l’émission vocale; retourne un résultat.
  - Méthode `reset(self)` (ligne 212) : Reset all internal state.
  - Méthode `_compute_buckets(scene_report)` (ligne 222) : Extract per-category counts from the scene report and quantise them.

## agents/reasoning/danger_rules.py

- Description du module : Scene analysis rules for the reasoning agent.

- Fonction `_make_event(event_type, message, priority, details)` (ligne 9) : Fonction `_make_event` du module. gère des cas conditionnels; retourne un résultat.

- Fonction `_add_event(events, event_type, message, priority, details)` (ligne 19) : Ajoute event. gère des cas conditionnels; retourne un résultat; appelle any, append, get, événement.

- Fonction `build_risk_profile(target, confidence, bbox)` (ligne 25) : Construit risk profile. gère des cas conditionnels; retourne un résultat; appelle _build_risk_profile_from_detections, isinstance, scène.

- Fonction `_build_risk_profile_from_detections(detections, confidence, bbox)` (ligne 31) : Construit risk profile from detections. parcourt des collections; gère des cas conditionnels; met à jour des variables internes; retourne un résultat; appelle get, lower, événement.

- Fonction `_build_risk_profile_from_scene(scene)` (ligne 50) : Construit risk profile from scene. travaille sur la représentation de la scène; gère des cas conditionnels; met à jour des variables internes; retourne un résultat; appelle any, événement.

## agents/reasoning/decision_engine.py

- Description du module : Decision engine that chooses a single action from a SceneReport.

- Classe `Decision` (ligne 15) : Classe de type Decision.

- Classe `DecisionEngine` (ligne 23) : Choose a single Decision from a SceneReport.
  - Méthode `__init__(self, priority_map, ttl_map, time_fn)` (ligne 68) : Initialise. gère des cas conditionnels; met à jour des variables internes; appelle update.
  - Méthode `decide(self, report)` (ligne 82) : Fonction `decide` du module. parcourt des collections; gère des cas conditionnels; met à jour des variables internes; retourne un résultat; appelle Decision, _time, get, getattr.
  - Méthode `reset(self)` (ligne 134) : Reset the internal state (useful for tests).

## agents/reasoning/priority_agent.py

- Description du module : Priority agent for selecting the most relevant events.

- Classe `PriorityAgent` (ligne 7) : Choose the highest-value events from a larger list.
  - Méthode `__init__(self, max_events)` (ligne 10) : Initialise. met à jour des variables internes.
  - Méthode `select_top_events(self, events)` (ligne 13) : Fonction `select_top_events` du module. met à jour des variables internes; retourne un résultat; appelle get, sorted.

## agents/reasoning/priority_manager.py

- Description du module : Priority ranking for reasoning messages.

- Fonction `sort_messages(messages)` (ligne 7) : Fonction `sort_messages` du module. retourne un résultat; appelle get, sorted.

## agents/reasoning/reasoning_agent.py

- Description du module : Reasoning agent converting a fused scene into prioritized events.

- Classe `ReasoningAgent` (ligne 15) : Agent responsable de la logique reasoning.
  - Méthode `__init__(self, config)` (ligne 16) : Initialise. gère des cas conditionnels; met à jour des variables internes; appelle VisionAssistantConfig, priorité.
  - Méthode `analyze_scene(self, scene)` (ligne 20) : Analyse scene. travaille sur la représentation de la scène; met à jour des variables internes; retourne un résultat; appelle build_risk_profile.

## agents/reasoning/scene_interpreter.py

- Description du module : Scene interpreter for producing a high-level scene report.

- Fonction `get_spatial_context(obj, frame_width, frame_height)` (ligne 12) : Computes a natural language description of the object's position and distance using invariable adverbs.

- Fonction `build_natural_summary(scene, matched_rules)` (ligne 38) : Construit natural summary. parcourt des collections; gère des cas conditionnels; met à jour des variables internes; retourne un résultat; appelle append, get, get_spatial_context, join.

- Classe `SceneReport` (ligne 119) : Classe de type SceneReport.
  - Méthode `to_dict(self)` (ligne 127) : Convertit l’objet en dictionnaire pour sérialisation ou rapport. retourne un résultat.

- Classe `SceneInterpreter` (ligne 138) : Convert a fused scene into a structured scene report.
  - Méthode `interpret(self, scene)` (ligne 141) : Interprète une scène pour générer un rapport de situation. parcourt des collections; gère des cas conditionnels; met à jour des variables internes; retourne un résultat; appelle _highest_danger_level, _merge_unique, _norm, add, build_natural_summary, choose_important_objects, get, get_instance, getattr, label, lower, modèle, scène, select_applicable_rules, sorted, strip, update, événement.
  - Méthode `_default_report(self, scene)` (ligne 219) : Fonction `_default_report` du module. met à jour des variables internes; retourne un résultat; appelle scène.
  - Méthode `_highest_danger_level(self, rules)` (ligne 230) : Fonction `_highest_danger_level` du module. gère des cas conditionnels; met à jour des variables internes; retourne un résultat; appelle upper.
  - Méthode `_merge_unique(items)` (ligne 241) : Fonction `_merge_unique` du module. parcourt des collections; gère des cas conditionnels; met à jour des variables internes; retourne un résultat; appelle add, append.

## agents/reasoning/scene_memory.py

- Description du module : Scene memory for tracking recent scene state and emitting only important changes.

- Classe `SceneMemoryObject` (ligne 15) : Classe de type SceneMemoryObject.

- Classe `SceneMemory` (ligne 26) : Track recent scene state and report only meaningful scene changes.
  - Méthode `__init__(self, cooldown_seconds)` (ligne 29) : Initialise. met à jour des variables internes.
  - Méthode `update(self, scene)` (ligne 38) : Update memory from a fused scene representation.
  - Méthode `get_new_events(self)` (ligne 134) : Return only the events generated by the most recent scene update.
  - Méthode `has_changed(self)` (ligne 138) : Return True only when the scene contains a meaningful change.
  - Méthode `should_speak(self, text)` (ligne 142) : Return True only if text has not been spoken within the cooldown window.
  - Méthode `_extract_scene_objects(self, scene)` (ligne 156) : Fonction `_extract_scene_objects` du module. travaille sur la représentation de la scène; parcourt des collections; gère des cas conditionnels; met à jour des variables internes; retourne un résultat; appelle extend, isinstance, values.
  - Méthode `_scene_bounds(self, objects)` (ligne 169) : Fonction `_scene_bounds` du module. travaille sur la représentation de la scène; gère des cas conditionnels; met à jour des variables internes; retourne un résultat.
  - Méthode `_compute_key(self, obj, bounds)` (ligne 178) : Fonction `_compute_key` du module. gère des cas conditionnels; met à jour des variables internes; retourne un résultat; appelle _approximate_position, lower.
  - Méthode `_approximate_position(self, bbox, bounds)` (ligne 192) : Fonction `_approximate_position` du module. gère des cas conditionnels; met à jour des variables internes; retourne un résultat.
  - Méthode `_appearance_message(self, obj)` (ligne 217) : Fonction `_appearance_message` du module. met à jour des variables internes; retourne un résultat; appelle endswith, label.
  - Méthode `_disappearance_message(self, obj)` (ligne 222) : Fonction `_disappearance_message` du module. met à jour des variables internes; retourne un résultat; appelle capitalize, label.
  - Méthode `_singular_label(self, label)` (ligne 226) : Fonction `_singular_label` du module. gère des cas conditionnels; met à jour des variables internes; retourne un résultat; appelle lower, strip.
  - Méthode `_plural_label(self, label)` (ligne 240) : Fonction `_plural_label` du module. gère des cas conditionnels; met à jour des variables internes; retourne un résultat; appelle endswith, lower, strip.

## agents/reasoning/scene_rules.py

- Description du module : Business rules for interpreting a visual scene.

- Classe `SceneRule` (ligne 13) : Classe de type SceneRule.

- Fonction `_normalize_label(value)` (ligne 25) : Normalise label. gère des cas conditionnels; retourne un résultat; appelle lower, strip.

- Fonction `has_label(scene, label)` (ligne 29) : Vérifie qu’un label existe dans le registre de labels. gère des cas conditionnels; met à jour des variables internes; retourne un résultat; appelle any, label.

- Fonction `has_any_label(scene, labels)` (ligne 34) : Vérifie any label. retourne un résultat; appelle any, label.

- Fonction `count_category(scene, category)` (ligne 38) : Compte category. gère des cas conditionnels; retourne un résultat; appelle getattr, hasattr.

- Fonction `category_is_approaching(scene, category)` (ligne 44) : Fonction `category_is_approaching` du module. retourne un résultat; appelle any, bool, get.

- Fonction `important_objects(scene, labels, categories)` (ligne 48) : Fonction `important_objects` du module. parcourt des collections; gère des cas conditionnels; met à jour des variables internes; retourne un résultat; appelle append, label.

- Fonction `select_applicable_rules(scene)` (ligne 222) : Fonction `select_applicable_rules` du module. retourne un résultat; appelle condition.

- Fonction `choose_important_objects(scene, rules, limit)` (ligne 226) : Fonction `choose_important_objects` du module. parcourt des collections; gère des cas conditionnels; met à jour des variables internes; retourne un résultat; appelle extend, important_objects, values.

## agents/speech/__init__.py

- Description du module : Speech agent package for audio feedback.

## agents/speech/speech_agent.py

- Description du module : Speech agent with prioritized queue and non-blocking output.

- Classe `SpeechAgent` (ligne 19) : Agent responsable de la logique speech.
  - Méthode `__init__(self, config)` (ligne 20) : Initialise. gère des cas conditionnels; met à jour des variables internes; appelle Lock, Thread, VisionAssistantConfig, _initialize_engine, priorité, start, événement.
  - Méthode `_initialize_engine(self)` (ligne 31) : Initialise engine. gère des cas conditionnels; gère des exceptions; met à jour des variables internes; appelle getProperty, init, setProperty, warning.
  - Méthode `_run(self)` (ligne 44) : Exécute. gère des exceptions; met à jour des variables internes; appelle _speak, get, is_set, task_done.
  - Méthode `_speak(self, message)` (ligne 55) : Fait parler. gère l’émission vocale; gère des cas conditionnels; utilise un gestionnaire de contexte; appelle info, runAndWait, say.
  - Méthode `speak(self, message, priority)` (ligne 63) : Émet un message vocal. gère l’émission vocale; gère des cas conditionnels; met à jour des variables internes; retourne un résultat; appelle put, qsize, warning.
  - Méthode `stop(self)` (ligne 82) : Arrête. appelle join.

## agents/speech/speech_planner.py

- Description du module : Speech planner for translating events into natural spoken phrases.

- Classe `SpeechPlanner` (ligne 7) : Prepare natural language phrases from a scene report.
  - Méthode `plan(self, decision)` (ligne 9) : Create speech plan from a single Decision.
  - Méthode `_format_message(self, event)` (ligne 30) : Fonction `_format_message` du module. gère des cas conditionnels; met à jour des variables internes; retourne un résultat; appelle get, lower, strip.

## agents/speech/tts.py

- Description du module : module Python du projet.

## agents/tracking/__init__.py

- Description du module : Tracking agent package for maintaining identity across frames.

## agents/tracking/tracking_agent.py

- Description du module : Tracking agent for assigning stable IDs to scene objects.

- Classe `TrackingAgent` (ligne 13) : Assign tracking identifiers to fused scene objects.
  - Méthode `__init__(self, tracker_type, iou_threshold, max_age, min_hits)` (ligne 16) : Initialise. met à jour des variables internes; appelle Tracker.
  - Méthode `track(self, scene)` (ligne 30) : Suit des objets dans la scène entre les images. applique le suivi d’objets; parcourt des collections; gère des cas conditionnels; met à jour des variables internes; retourne un résultat; appelle debug, get, update, zip.

## agents/vision/__init__.py

- Description du module : Vision agent package for model management and prediction.

## agents/vision/model_loader.py

- Description du module : Real model loader for ONNX and PyTorch detectors.

- Fonction `normalize_category(name)` (ligne 25) : Normalize a detector directory name to a consistent category key.

- Classe `ModelInfo` (ligne 48) : Model metadata and runtime artifacts.

- Classe `ModelLoader` (ligne 63) : Load and manage multiple detector models for VisionAgent.
  - Méthode `__init__(self, models_dir)` (ligne 66) : Initialise. gère des cas conditionnels; met à jour des variables internes; appelle Path, _detect_torch, get_config.
  - Méthode `_detect_torch(self)` (ligne 74) : Détecte torch. gère des exceptions; retourne un résultat; appelle debug.
  - Méthode `load_all_models(self)` (ligne 82) : Discover and load all available real detectors from the models directory.
  - Méthode `refresh_models(self)` (ligne 99) : Reload the detector configuration if the model files have changed.
  - Méthode `_discover_model_names(self)` (ligne 109) : Fonction `_discover_model_names` du module. gère des cas conditionnels; retourne un résultat; appelle exists, is_dir, iterdir.
  - Méthode `_build_snapshot(self)` (ligne 114) : Construit snapshot. parcourt des collections; gère des cas conditionnels; met à jour des variables internes; retourne un résultat; appelle exists, is_dir, iterdir, stat.
  - Méthode `_read_labels(self, folder)` (ligne 127) : Fonction `_read_labels` du module. gère des cas conditionnels; met à jour des variables internes; retourne un résultat; appelle safe_read_text, splitlines, strip.
  - Méthode `_read_metadata(self, folder)` (ligne 134) : Fonction `_read_metadata` du module. gère des cas conditionnels; gère des exceptions; met à jour des variables internes; retourne un résultat; appelle exists, loads, safe_read_text, warning.
  - Méthode `_is_real_model(self, folder)` (ligne 147) : Teste si real model. gère des cas conditionnels; met à jour des variables internes; retourne un résultat; appelle any, exists, stat.
  - Méthode `load_model(self, name)` (ligne 152) : Load a single real model by directory name.
  - Méthode `_initialize_real_detector(self, model_info)` (ligne 177) : Initialise real detector. gère des cas conditionnels; met à jour des variables internes; retourne un résultat; appelle _load_onnx_session, error, info, label, modèle, warning.
  - Méthode `_load_onnx_session(self, path)` (ligne 203) : Charge onnx session. gère des exceptions; retourne un résultat; appelle InferenceSession, warning.
  - Méthode `_read_onnx_labels(self, session)` (ligne 211) : Read Ultralytics class names embedded in an ONNX graph.
  - Méthode `_extract_metadata_input_size(self, metadata)` (ligne 224) : Fonction `_extract_metadata_input_size` du module. gère des cas conditionnels; gère des exceptions; met à jour des variables internes; retourne un résultat; appelle get, isinstance.
  - Méthode `_input_size_from_onnx_shape(self, input_shape)` (ligne 237) : Fonction `_input_size_from_onnx_shape` du module. gère des cas conditionnels; gère des exceptions; met à jour des variables internes; retourne un résultat; appelle isinstance.
  - Méthode `_resolve_onnx_input_size(self, model_info)` (ligne 249) : Fonction `_resolve_onnx_input_size` du module. gère des cas conditionnels; gère des exceptions; met à jour des variables internes; retourne un résultat; appelle _input_size_from_onnx_shape, get_inputs, info, métadonnées, warning.
  - Méthode `_load_torch_model(self, path)` (ligne 286) : Charge torch model. lit ou écrit des données; gère des cas conditionnels; gère des exceptions; met à jour des variables internes; retourne un résultat; appelle eval, load, warning.
  - Méthode `_prepare_image(self, image, target_shape)` (ligne 296) : Fonction `_prepare_image` du module. gère des cas conditionnels; gère des exceptions; met à jour des variables internes; retourne un résultat; appelle LetterBox, RuntimeError, astype, cvtColor, letterbox, transpose.
  - Méthode `_decode_label(self, label, labels)` (ligne 310) : Fonction `_decode_label` du module. gère des cas conditionnels; retourne un résultat; appelle isinstance.
  - Méthode `_log_tensor_summary(self, raw, name)` (ligne 318) : Enregistre tensor summary. parcourt des collections; gère des cas conditionnels; met à jour des variables internes; retourne un résultat; appelle asarray, debug, enumerate, isinstance, reshape, tolist.
  - Méthode `_parse_raw_predictions(self, raw, image_shape, model_shape)` (ligne 343) : Fonction `_parse_raw_predictions` du module. parcourt des collections; gère des cas conditionnels; gère des exceptions; met à jour des variables internes; retourne un résultat; appelle append, asarray, enumerate, from_numpy, hasattr, isinstance, item, non_max_suppression, scale_boxes, tolist, unsqueeze, warning.
  - Méthode `_predict_onnx(self, model_info, image)` (ligne 397) : Fonction `_predict_onnx` du module. gère des cas conditionnels; gère des exceptions; met à jour des variables internes; retourne un résultat; appelle _log_tensor_summary, _prepare_image, _resolve_onnx_input_size, exception, get_inputs, isinstance, prédiction, run.
  - Méthode `_predict_torch(self, model_info, image)` (ligne 412) : Fonction `_predict_torch` du module. gère des cas conditionnels; utilise un gestionnaire de contexte; gère des exceptions; met à jour des variables internes; retourne un résultat; appelle _prepare_image, cpu, exception, from_numpy, hasattr, isinstance, iter, modèle, next, no_grad, numpy, parameters, prédiction.
  - Méthode `predict(self, name, image)` (ligne 433) : Predict with a named detector and return normalized detections.
  - Méthode `predict_all(self, image)` (ligne 453) : Run prediction on every loaded detector and return categorized results.
  - Méthode `_normalize_prediction(self, item, model_info)` (ligne 494) : Normalise prediction. gère des cas conditionnels; met à jour des variables internes; retourne un résultat; appelle get, isinstance, label, setdefault.

## agents/vision/model_loader_backup.py

- Description du module : BACKUP - This is a reference of what the cleaned model_loader.

## agents/vision/vision_agent.py

- Description du module : Vision agent responsible for loading models and producing raw detections.

- Classe `VisionAgent` (ligne 16) : Agent responsable de la logique vision.
  - Méthode `__init__(self, model_loader, config)` (ligne 17) : Initialise. gère des cas conditionnels; met à jour des variables internes; appelle VisionAssistantConfig, modèle.
  - Méthode `load_models(self)` (ligne 22) : Charge les modèles de détection disponibles. appelle modèle.
  - Méthode `predict(self, image, frame_id)` (ligne 25) : Exécute l’inférence sur une image ou une trame. parcourt des collections; gère des cas conditionnels; met à jour des variables internes; retourne un résultat; appelle append, get, items, predict_all, setdefault, time.

## app/api/__init__.py

- Description du module : FastAPI application package for Vision Assistant.

## app/api/main.py

- Description du module : FastAPI endpoints for Vision Assistant.

- Classe `ImagePredictRequest` (ligne 29) : Classe de type ImagePredictRequest.

- Classe `VideoPredictRequest` (ligne 33) : Classe de type VideoPredictRequest.

- Classe `SpeakRequest` (ligne 39) : Classe de type SpeakRequest.

- Fonction `startup()` (ligne 44) : Fonction `startup` du module. met à jour des variables internes; appelle Coordinator, initialize, modèle, événement.

- Fonction `status(request)` (ligne 55) : Fonction `status` du module. met à jour des variables internes; retourne un résultat; appelle get, keys, sorted.

- Fonction `models(request)` (ligne 68) : Fonction `models` du module. retourne un résultat; appelle get, items.

- Fonction `history(request)` (ligne 82) : Fonction `history` du module. met à jour des variables internes; retourne un résultat; appelle get, values, événement.

- Fonction `config_endpoint(request)` (ligne 91) : Configure endpoint. met à jour des variables internes; retourne un résultat; appelle get.

- Fonction `predict_image(request, payload)` (ligne 120) : Fonction `predict_image` du module. gère des cas conditionnels; gère des exceptions; met à jour des variables internes; retourne un résultat; appelle HTTPException, ValueError, b64decode, exception, frombuffer, imdecode, post, process_frame.

- Fonction `predict_video(request, payload)` (ligne 136) : Fonction `predict_video` du module. lit ou écrit des données; gère des cas conditionnels; gère des exceptions; met à jour des variables internes; retourne un résultat; appelle HTTPException, Path, VideoCapture, isOpened, is_absolute, is_file, post, process_frame, read, release.

- Fonction `reload_models(request)` (ligne 178) : Fonction `reload_models` du module. retourne un résultat; appelle keys, modèle, post, sorted.

- Fonction `speak(request, payload)` (ligne 184) : Émet un message vocal. gère l’émission vocale; met à jour des variables internes; retourne un résultat; appelle post, speak.

- Fonction `frame(request)` (ligne 190) : Fonction `frame` du module. gère des cas conditionnels; met à jour des variables internes; retourne un résultat; appelle HTTPException, get.

## app/desktop/__init__.py

- Description du module : Desktop user interface package for Vision Assistant.

## app/desktop/desktop_app.py

- Description du module : Desktop OpenCV application for live vision assistant output.

- Classe `DesktopApp` (ligne 19) : Classe de type DesktopApp.
  - Méthode `__init__(self, config)` (ligne 20) : Initialise. gère des cas conditionnels; met à jour des variables internes; appelle CameraManager, Coordinator, configure_logging, get_config, info, initialize, keys, sorted.
  - Méthode `run(self)` (ligne 35) : Exécute. lit ou écrit des données; gère des cas conditionnels; met à jour des variables internes; appelle RuntimeError, destroyAllWindows, get, imshow, info, open, ord, process_frame, prédiction, putText, read, release, waitKey.

## app/mobile/.eslintrc.js

- Description du module : fichier js du projet.

- Aucun symbole fonctionnel détecté ou analyse manuelle nécessaire.

## app/mobile/.prettierrc.js

- Description du module : fichier js du projet.

- Aucun symbole fonctionnel détecté ou analyse manuelle nécessaire.

## app/mobile/App.tsx

- Description du module : Sample React Native App

- Fonction `Section` (ligne 32) : Fonction `Section` du module.
- Fonction `App` (ligne 58) : Fonction `App` du module.

## app/mobile/__tests__/App.test.tsx

- Description du module : @format

- Aucun symbole fonctionnel détecté ou analyse manuelle nécessaire.

## app/mobile/babel.config.js

- Description du module : fichier js du projet.

- Aucun symbole fonctionnel détecté ou analyse manuelle nécessaire.

## app/mobile/index.js

- Description du module : @format

- Aucun symbole fonctionnel détecté ou analyse manuelle nécessaire.

## app/mobile/jest.config.js

- Description du module : fichier js du projet.

- Aucun symbole fonctionnel détecté ou analyse manuelle nécessaire.

## app/mobile/metro.config.js

- Description du module : fichier js du projet.

- Aucun symbole fonctionnel détecté ou analyse manuelle nécessaire.

## app/mobile/src/App.tsx

- Description du module : fichier tsx du projet.

- Fonction `copyModelFromAssets` (ligne 14) : Fonction `copyModelFromAssets` du module.

## app/mobile/src/agents/MemoryAgent.ts

- Description du module : fichier ts du projet.

- Aucun symbole fonctionnel détecté ou analyse manuelle nécessaire.

## app/mobile/src/agents/ReasoningAgent.ts

- Description du module : fichier ts du projet.

- Aucun symbole fonctionnel détecté ou analyse manuelle nécessaire.

## app/mobile/src/components/BoundingBoxOverlay.tsx

- Description du module : fichier tsx du projet.

- Aucun symbole fonctionnel détecté ou analyse manuelle nécessaire.

## app/mobile/src/utils/YoloPostProcess.ts

- Description du module : fichier ts du projet.

- Fonction `calculateIoU` (ligne 4) : Helper for Intersection Over Union (IoU) calculation
- Fonction `parseYoloOutput` (ligne 17) : Fonction `parseYoloOutput` du module.

## config.py

- Description du module : Central configuration for Vision Assistant.

- Classe `CameraConfig` (ligne 10) : Classe de type CameraConfig.

- Classe `SpeechConfig` (ligne 22) : Classe de type SpeechConfig.

- Classe `MemoryConfig` (ligne 32) : Classe de type MemoryConfig.

- Classe `TrackingConfig` (ligne 39) : Classe de type TrackingConfig.

- Classe `ModelConfig` (ligne 48) : Classe de type ModelConfig.

- Classe `ApiConfig` (ligne 59) : Classe de type ApiConfig.

- Classe `PathsConfig` (ligne 66) : Classe de type PathsConfig.

- Classe `LoggingConfig` (ligne 77) : Classe de type LoggingConfig.

- Classe `VisionAssistantConfig` (ligne 84) : Classe de type VisionAssistantConfig.

- Fonction `get_config()` (ligne 103) : Récupère config. gère des cas conditionnels; met à jour des variables internes; retourne un résultat; appelle VisionAssistantConfig.

## core/__init__.py

- Description du module : Core utilities and camera subsystem for Vision Assistant.

## core/camera.py

- Description du module : Camera manager for live video, files, and IP streams.

- Classe `CameraManager` (ligne 10) : Gère la logique de camera.
  - Méthode `__init__(self, source_type, device_index, video_path, ip_camera_url)` (ligne 11) : Initialise. met à jour des variables internes.
  - Méthode `open(self)` (ligne 18) : Fonction `open` du module. gère des cas conditionnels; met à jour des variables internes; retourne un résultat; appelle VideoCapture, bool, isOpened, resolve_source.
  - Méthode `resolve_source(self)` (ligne 24) : Fonction `resolve_source` du module. gère des cas conditionnels; retourne un résultat.
  - Méthode `read(self)` (ligne 33) : Fonction `read` du module. lit ou écrit des données; gère des cas conditionnels; met à jour des variables internes; retourne un résultat; appelle open, read.
  - Méthode `release(self)` (ligne 43) : Fonction `release` du module. gère des cas conditionnels; met à jour des variables internes; appelle release.

- Classe `CameraSource` (ligne 49) : Backward-compatible camera wrapper used by older clients and tests.
  - Méthode `__init__(self, config)` (ligne 52) : Initialise. met à jour des variables internes; appelle __init__, super.
  - Méthode `_resolve_source(self)` (ligne 61) : Fonction `_resolve_source` du module. retourne un résultat; appelle resolve_source.

## core/distance_estimator.py

- Description du module : module Python du projet.

## core/logger.py

- Description du module : Professional logging setup for Vision Assistant.

- Fonction `configure_logging(config)` (ligne 12) : Fonction `configure_logging` du module. gère des cas conditionnels; met à jour des variables internes; retourne un résultat; appelle Formatter, Path, RotatingFileHandler, StreamHandler, VisionAssistantConfig, addHandler, clear, getLogger, getattr, mkdir, setFormatter, setLevel, upper.

## core/object_counter.py

- Description du module : module Python du projet.

## core/scene_analyzer.py

- Description du module : module Python du projet.

## core/tracker.py

- Description du module : Tracking utilities with IoU fallback and optional ByteTrack support.

- Classe `Track` (ligne 11) : Classe de type Track.

- Classe `Tracker` (ligne 21) : Classe de type Tracker.
  - Méthode `__init__(self, tracker_type, iou_threshold, max_age, min_hits)` (ligne 22) : Initialise. met à jour des variables internes.
  - Méthode `_compute_iou(self, box_a, box_b)` (ligne 37) : Fonction `_compute_iou` du module. gère des cas conditionnels; met à jour des variables internes; retourne un résultat.
  - Méthode `update(self, detections)` (ligne 50) : Met à jour. parcourt des collections; gère des cas conditionnels; gère des exceptions; met à jour des variables internes; retourne un résultat; appelle Track, add, append, get, intersection over union, lower, métadonnées, pop, strip, tuple, update.
  - Méthode `_motion_metadata(previous, current)` (ligne 117) : Fonction `_motion_metadata` du module. gère des cas conditionnels; met à jour des variables internes; retourne un résultat; appelle abs, round.

## core/utils.py

- Description du module : Shared utilities for Vision Assistant.

- Fonction `ensure_directory(path)` (ligne 15) : Fonction `ensure_directory` du module. retourne un résultat; appelle mkdir.

- Fonction `safe_read_text(path)` (ligne 20) : Fonction `safe_read_text` du module. gère des exceptions; retourne un résultat; appelle read_text, strip.

- Fonction `serialize_json(payload)` (ligne 27) : Fonction `serialize_json` du module. retourne un résultat; appelle dumps.

- Fonction `normalize_bbox(raw_bbox, frame_shape)` (ligne 31) : Normalise bbox. met à jour des variables internes; retourne un résultat; appelle get.

- Fonction `draw_predictions(image, detections)` (ligne 44) : Fonction `draw_predictions` du module. parcourt des collections; gère des cas conditionnels; met à jour des variables internes; retourne un résultat; appelle copy, get, isinstance, putText, rectangle.

## run.py

- Description du module : Entry point for Vision Assistant desktop execution.

- Fonction `main()` (ligne 7) : Fonction `main` du module. met à jour des variables internes; appelle DesktopApp, run.

## scripts/debug_model.py

- Description du module : Debug the ONNX detector pipeline and save annotated output for inspection.

- Fonction `parse_args()` (ligne 14) : Fonction `parse_args` du module. met à jour des variables internes; retourne un résultat; appelle ArgumentParser, add_argument, parse_args.

- Fonction `main()` (ligne 31) : Fonction `main` du module. gère des cas conditionnels; met à jour des variables internes; retourne un résultat; appelle Path, basicConfig, draw_bounding_boxes, ensure_directory, error, exists, imread, imwrite, info, iter, keys, modèle, next, parse_args, predict, serialize_json, write_text.

## scripts/integrate_model.py

- Description du module : Integrate a student-trained detector into the platform.

- Fonction `validate_files(model_dir)` (ligne 18) : Fonction `validate_files` du module. met à jour des variables internes; retourne un résultat; appelle exists.

- Fonction `integrate_model(model_path, destination_dir, report_path)` (ligne 24) : Fonction `integrate_model` du module. parcourt des collections; gère des cas conditionnels; met à jour des variables internes; retourne un résultat; appelle FileNotFoundError, copy2, isoformat, mkdir, serialize_json, utcnow, validate_files, write_text.

- Fonction `main()` (ligne 42) : Fonction `main` du module. met à jour des variables internes; appelle ArgumentParser, Path, add_argument, get_config, modèle, parse_args, print, resolve, serialize_json, strftime, utcnow.

## setup.py

- Description du module : module Python du projet.

## test_fallback.py

- Description du module : module Python du projet.

- Fonction `test()` (ligne 9) : Fonction `test` du module. met à jour des variables internes; appelle DecisionEngine, add, decide, interpret, print, scène.

## test_interpreter.py

- Description du module : module Python du projet.

- Fonction `test()` (ligne 10) : Fonction `test` du module. met à jour des variables internes; appelle add, interpret, print, scène.

## test_nlg.py

- Description du module : module Python du projet.

- Fonction `test()` (ligne 9) : Fonction `test` du module. met à jour des variables internes; appelle add, interpret, print, scène.

## test_nlg2.py

- Description du module : module Python du projet.

- Fonction `test()` (ligne 8) : Fonction `test` du module. met à jour des variables internes; appelle add, interpret, print, scène.

## tests/integration/test_pipeline.py

- Description du module : module Python du projet.

- Fonction `test_coordinator_process_frame()` (ligne 7) : Fonction `test_coordinator_process_frame` du module. gère des cas conditionnels; met à jour des variables internes; appelle Coordinator, get_config, initialize, process_frame, zeros.

## tests/test_conversation_manager.py

- Description du module : Unit tests for ConversationManager.

- Classe `FakeReport` (ligne 26) : Classe de type FakeReport.

- Fonction `make_report(persons, vehicles, obstacles, food, sidewalks, events)` (ligne 35) : Build a minimal fake report with controllable category counts.

- Classe `TestCountBucket` (ligne 58) : Classe de type TestCountBucket.
  - Méthode `test_from_count_zero(self)` (ligne 59) : Test from count zero. gère des cas conditionnels; appelle from_count.
  - Méthode `test_from_count_one(self)` (ligne 62) : Test from count one. gère des cas conditionnels; appelle from_count.
  - Méthode `test_from_count_many(self)` (ligne 65) : Test from count many. gère des cas conditionnels; appelle from_count.
  - Méthode `test_from_count_negative(self)` (ligne 70) : Test from count negative. gère des cas conditionnels; appelle from_count.

- Classe `TestStabilisation` (ligne 74) : Core test suite: minor count fluctuations must NOT trigger announcements.
  - Méthode `test_no_change_means_no_announce(self)` (ligne 77) : Empty scene stays empty → no announcement.
  - Méthode `test_none_to_one_triggers(self)` (ligne 85) : 0 persons → 1 person = bucket change NONE→ONE.
  - Méthode `test_one_to_multiple_triggers(self)` (ligne 93) : 1 person → 3 persons = bucket change ONE→MULTIPLE.
  - Méthode `test_multiple_to_none_triggers(self)` (ligne 103) : 5 persons → 0 = MULTIPLE→NONE.
  - Méthode `test_jitter_within_multiple_is_suppressed(self)` (ligne 111) : 4→5→4→6→5 persons all stay in MULTIPLE — no new announcement.
  - Méthode `test_jitter_within_one_is_suppressed(self)` (ligne 122) : 1→1→1 stays ONE — only the first transition is announced.

- Classe `TestCriticalBypass` (ligne 131) : Critical events must always be allowed through, regardless of bucket state.
  - Méthode `test_vehicle_approaching_always_passes(self)` (ligne 134) : Fonction `test_vehicle_approaching_always_passes` du module. gère des cas conditionnels; met à jour des variables internes; appelle ConversationManager, make_report, should_announce.
  - Méthode `test_person_approaching_always_passes(self)` (ligne 142) : Fonction `test_person_approaching_always_passes` du module. met à jour des variables internes; appelle ConversationManager, make_report, should_announce.

- Classe `TestCooldown` (ligne 151) : The minimum announcement interval must be respected for non-critical events.
  - Méthode `test_cooldown_blocks_rapid_changes(self)` (ligne 154) : Fonction `test_cooldown_blocks_rapid_changes` du module. gère des cas conditionnels; met à jour des variables internes; appelle ConversationManager, make_report, should_announce.
  - Méthode `test_cooldown_expires(self)` (ligne 164) : Fonction `test_cooldown_expires` du module. met à jour des variables internes; appelle ConversationManager, make_report, should_announce, sleep.

- Classe `TestReset` (ligne 172) : Classe de type TestReset.
  - Méthode `test_reset_clears_state(self)` (ligne 173) : Fonction `test_reset_clears_state` du module. gère des cas conditionnels; met à jour des variables internes; appelle ConversationManager, all, make_report, reset, should_announce, values.

- Classe `TestMultipleCategories` (ligne 182) : Changes in different categories are tracked independently.
  - Méthode `test_persons_and_vehicles_independent(self)` (ligne 185) : Fonction `test_persons_and_vehicles_independent` du module. gère des cas conditionnels; met à jour des variables internes; appelle ConversationManager, make_report, should_announce.

## tests/test_integration.py

- Description du module : Integration Tests for Model Integration System.

- Fonction `temp_training_dir()` (ligne 47) : Create temporary training directory structure.

- Fonction `temp_models_dir()` (ligne 55) : Create temporary models directory.

- Fonction `temp_reports_dir()` (ligne 63) : Create temporary reports directory.

- Fonction `create_test_model_dir(base_dir, model_name, valid, include_files, metadata_dict, labels)` (ligne 70) : Create a test model directory with files.

- Classe `TestModelMetadata` (ligne 133) : Tests for ModelMetadata dataclass.
  - Méthode `test_valid_metadata(self)` (ligne 136) : Test creating valid metadata.
  - Méthode `test_missing_required_field(self)` (ligne 152) : Test metadata with missing required field.
  - Méthode `test_invalid_input_size(self)` (ligne 162) : Test metadata with invalid input_size.
  - Méthode `test_optional_fields(self)` (ligne 175) : Test metadata with optional fields.

- Classe `TestModelValidator` (ligne 196) : Tests for ModelValidator class.
  - Méthode `test_valid_model(self, temp_training_dir)` (ligne 199) : Test validation of valid model.
  - Méthode `test_missing_file(self, temp_training_dir)` (ligne 210) : Test validation with missing required file.
  - Méthode `test_empty_labels(self, temp_training_dir)` (ligne 221) : Test validation with empty labels.
  - Méthode `test_duplicate_labels(self, temp_training_dir)` (ligne 237) : Test validation with duplicate labels.
  - Méthode `test_malformed_metadata(self, temp_training_dir)` (ligne 252) : Test validation with malformed metadata.
  - Méthode `test_model_name_mismatch(self, temp_training_dir)` (ligne 263) : Test validation with model_name mismatch.

- Classe `TestModelInstaller` (ligne 290) : Tests for ModelInstaller class.
  - Méthode `test_install_model(self, temp_training_dir, temp_models_dir)` (ligne 293) : Test successful model installation.
  - Méthode `test_dry_run_installation(self, temp_training_dir, temp_models_dir)` (ligne 308) : Test dry-run installation.
  - Méthode `test_install_existing_model_without_overwrite(self, temp_training_dir, temp_models_dir)` (ligne 319) : Test installation of existing model without overwrite.
  - Méthode `test_install_with_overwrite(self, temp_training_dir, temp_models_dir)` (ligne 335) : Test installation with overwrite.

- Classe `TestIntegrationResult` (ligne 360) : Tests for IntegrationResult dataclass.
  - Méthode `test_result_serialization(self)` (ligne 363) : Test converting result to dictionary.

- Classe `TestReportGenerator` (ligne 389) : Tests for ReportGenerator class.
  - Méthode `test_generate_model_report(self, temp_reports_dir)` (ligne 392) : Test generating report for single model.
  - Méthode `test_generate_batch_report(self, temp_reports_dir)` (ligne 421) : Test generating batch report.

- Classe `TestBatchOperations` (ligne 459) : Tests for batch discovery and integration.
  - Méthode `test_discover_models(self, temp_training_dir)` (ligne 462) : Test model discovery.
  - Méthode `test_skip_template_directory(self, temp_training_dir)` (ligne 478) : Test that template directory is skipped.

- Classe `TestFullIntegration` (ligne 496) : End-to-end integration tests.
  - Méthode `test_full_workflow(self, temp_training_dir, temp_models_dir, temp_reports_dir)` (ligne 499) : Test complete integration workflow.
  - Méthode `test_integration_with_missing_files(self, temp_training_dir, temp_models_dir, temp_reports_dir)` (ligne 520) : Test integration with missing required files.

- Classe `TestEdgeCases` (ligne 544) : Tests for edge cases and error conditions.
  - Méthode `test_very_long_label(self, temp_training_dir)` (ligne 547) : Test validation of very long label names.
  - Méthode `test_special_characters_in_labels(self, temp_training_dir)` (ligne 561) : Test labels with special characters.
  - Méthode `test_unicode_labels(self, temp_training_dir)` (ligne 576) : Test labels with unicode characters.

- Classe `TestPerformance` (ligne 596) : Performance-related tests.
  - Méthode `test_large_labels_file(self, temp_training_dir)` (ligne 599) : Test validation of large labels file.

## tests/unit/test_camera_source.py

- Description du module : Unit tests for camera source resolution and configuration.

- Fonction `test_camera_source_resolves_laptop()` (ligne 8) : Fonction `test_camera_source_resolves_laptop` du module. gère des cas conditionnels; met à jour des variables internes; appelle AppConfig, CameraSource, _resolve_source, type.

- Fonction `test_camera_source_resolves_video_file(tmp_path)` (ligne 14) : Fonction `test_camera_source_resolves_video_file` du module. gère des cas conditionnels; met à jour des variables internes; appelle AppConfig, CameraSource, _resolve_source, type.

## tests/unit/test_config.py

- Description du module : Unit tests for Vision Assistant configuration.

- Fonction `test_get_config_paths()` (ligne 5) : Fonction `test_get_config_paths` du module. gère des cas conditionnels; met à jour des variables internes; appelle get_config.

## tests/unit/test_decision_engine.py

- Description du module : Unit tests for DecisionEngine behavior.

- Classe `TimeMock` (ligne 8) : Classe de type TimeMock.
  - Méthode `__init__(self, start)` (ligne 9) : Initialise. met à jour des variables internes.
  - Méthode `time(self)` (ligne 12) : Fonction `time` du module. retourne un résultat.
  - Méthode `advance(self, seconds)` (ligne 15) : Fonction `advance` du module. met à jour des variables internes.

- Classe `TestDecisionEngine` (ligne 19) : Classe de type TestDecisionEngine.
  - Méthode `setUp(self)` (ligne 20) : Définit up. met à jour des variables internes; appelle DecisionEngine, TimeMock.
  - Méthode `test_empty_scene_ignored(self)` (ligne 24) : Fonction `test_empty_scene_ignored` du module. travaille sur la représentation de la scène; met à jour des variables internes; appelle assertEqual, decide, scène.
  - Méthode `test_single_person_speak(self)` (ligne 29) : Fonction `test_single_person_speak` du module. gère l’émission vocale; met à jour des variables internes; appelle assertEqual, decide, scène.
  - Méthode `test_repetition_ignored_within_ttl(self)` (ligne 35) : Fonction `test_repetition_ignored_within_ttl` du module. met à jour des variables internes; appelle assertEqual, decide, scène.
  - Méthode `test_ttl_expiry_allows_repeat(self)` (ligne 43) : Fonction `test_ttl_expiry_allows_repeat` du module. met à jour des variables internes; appelle advance, assertEqual, decide, scène.
  - Méthode `test_higher_priority_replaces(self)` (ligne 52) : Fonction `test_higher_priority_replaces` du module. met à jour des variables internes; appelle assertEqual, decide, scène.
  - Méthode `test_merge_person_and_door(self)` (ligne 63) : Fonction `test_merge_person_and_door` du module. met à jour des variables internes; appelle assertEqual, decide, scène.
  - Méthode `test_red_light_vs_crosswalk(self)` (ligne 69) : Fonction `test_red_light_vs_crosswalk` du module. met à jour des variables internes; appelle assertEqual, decide, scène.

## tests/unit/test_memory_agent.py

- Description du module : Unit tests for memory agent deduplication.

- Fonction `test_memory_prevents_duplicate_messages()` (ligne 5) : Fonction `test_memory_prevents_duplicate_messages` du module. gère des cas conditionnels; met à jour des variables internes; appelle MemoryAgent, message.

- Fonction `test_memory_allows_high_priority_repeat()` (ligne 14) : Fonction `test_memory_allows_high_priority_repeat` du module. gère des cas conditionnels; met à jour des variables internes; appelle MemoryAgent, message.

## tests/unit/test_model_loader.py

- Description du module : Unit tests for model loader behavior.

- Fonction `test_fake_model_loader_creates_detectors(tmp_path)` (ligne 12) : Fonction `test_fake_model_loader_creates_detectors` du module. met à jour des variables internes; appelle isinstance, mkdir, modèle, predict_all, zeros.

- Fonction `test_registers_model_directory(tmp_path)` (ligne 22) : Fonction `test_registers_model_directory` du module. gère des cas conditionnels; met à jour des variables internes; appelle mkdir, modèle, write_text.

- Fonction `test_model_loader_refreshes_when_model_appears(tmp_path)` (ligne 32) : Fonction `test_model_loader_refreshes_when_model_appears` du module. gère des cas conditionnels; met à jour des variables internes; appelle mkdir, modèle, write_text.

- Fonction `test_parse_yolo_matrix_output(tmp_path)` (ligne 45) : Fonction `test_parse_yolo_matrix_output` du module. gère des cas conditionnels; met à jour des variables internes; appelle array, modèle, prédiction.

- Fonction `_make_dummy_onnx_session(shape)` (ligne 59) : Fonction `_make_dummy_onnx_session` du module. met à jour des variables internes; retourne un résultat; appelle DummyInput, DummySession.

- Classe `LogCaptureHandler` (ligne 75) : Classe de type LogCaptureHandler.
  - Méthode `__init__(self)` (ligne 76) : Initialise. met à jour des variables internes; appelle __init__, super.
  - Méthode `emit(self, record)` (ligne 80) : Fonction `emit` du module. appelle append.

- Fonction `_capture_log_messages(logger_name, level, callback)` (ligne 84) : Fonction `_capture_log_messages` du module. gère des exceptions; met à jour des variables internes; retourne un résultat; appelle LogCaptureHandler, addHandler, callback, getLogger, join, message, removeHandler, setLevel.

- Classe `TestModelLoaderInputSize` (ligne 98) : Classe de type TestModelLoaderInputSize.
  - Méthode `test_resolves_fixed_onnx_input_shape(self)` (ligne 99) : Fonction `test_resolves_fixed_onnx_input_shape` du module. utilise un gestionnaire de contexte; met à jour des variables internes; appelle Path, TemporaryDirectory, _make_dummy_onnx_session, _resolve_onnx_input_size, assertEqual, assertIn, message, mkdir, modèle.
  - Méthode `test_resolves_dynamic_onnx_input_shape_with_metadata(self)` (ligne 121) : Fonction `test_resolves_dynamic_onnx_input_shape_with_metadata` du module. utilise un gestionnaire de contexte; met à jour des variables internes; appelle Path, TemporaryDirectory, _make_dummy_onnx_session, _resolve_onnx_input_size, assertEqual, assertIn, message, mkdir, modèle.
  - Méthode `test_resolves_dynamic_onnx_input_shape_without_metadata_uses_camera_config(self)` (ligne 143) : Fonction `test_resolves_dynamic_onnx_input_shape_without_metadata_uses_camera_config` du module. utilise un gestionnaire de contexte; met à jour des variables internes; appelle Path, TemporaryDirectory, _make_dummy_onnx_session, _resolve_onnx_input_size, assertEqual, assertIn, message, mkdir, modèle.

- Fonction `test_parse_yolo_channel_first_output(tmp_path)` (ligne 168) : Fonction `test_parse_yolo_channel_first_output` du module. gère des cas conditionnels; met à jour des variables internes; appelle array, modèle, prédiction.

## tests/unit/test_reasoning.py

- Description du module : module Python du projet.

- Fonction `test_reasoning_agent_returns_messages()` (ligne 5) : Fonction `test_reasoning_agent_returns_messages` du module. met à jour des variables internes; appelle ReasoningAgent, get_config, scène.

## tests/unit/test_reasoning_agent.py

- Description du module : Unit tests for reasoning rules.

- Fonction `test_reasoning_emergency_priority()` (ligne 5) : Fonction `test_reasoning_emergency_priority` du module. gère des cas conditionnels; met à jour des variables internes; appelle ReasoningAgent, analyze, lower.

- Fonction `test_reasoning_no_detections()` (ligne 14) : Fonction `test_reasoning_no_detections` du module. gère des cas conditionnels; met à jour des variables internes; appelle ReasoningAgent, analyze, lower.

## tests/unit/test_scene_builder.py

- Description du module : Unit tests for the scene builder and scene model.

- Classe `TestSceneBuilder` (ligne 7) : Construit ou assemble test scene.
  - Méthode `test_constructs_scene_from_raw_predictions(self)` (ligne 8) : Fonction `test_constructs_scene_from_raw_predictions` du module. travaille sur la représentation de la scène; met à jour des variables internes; appelle assertAlmostEqual, assertEqual, assertIsInstance, count, get, scène, summary, to_dict.

## tests/unit/test_scene_interpreter.py

- Description du module : Unit tests for scene interpretation and report generation.

- Classe `TestSceneInterpreter` (ligne 8) : Classe de type TestSceneInterpreter.
  - Méthode `setUp(self)` (ligne 9) : Définit up. met à jour des variables internes; appelle scène.
  - Méthode `test_single_person_summary(self)` (ligne 12) : Fonction `test_single_person_summary` du module. met à jour des variables internes; appelle assertEqual, assertIn, interpret, scène.
  - Méthode `test_vehicle_crosswalk_summary(self)` (ligne 25) : Fonction `test_vehicle_crosswalk_summary` du module. met à jour des variables internes; appelle assertEqual, assertIn, get, interpret, scène.
  - Méthode `test_wet_floor_summary(self)` (ligne 42) : Fonction `test_wet_floor_summary` du module. met à jour des variables internes; appelle assertEqual, assertIn, interpret, scène.
  - Méthode `test_multiple_objects_generate_events(self)` (ligne 54) : Fonction `test_multiple_objects_generate_events` du module. met à jour des variables internes; appelle assertIn, interpret, scène.
  - Méthode `_build_scene(self, predictions)` (ligne 69) : Construit scene. travaille sur la représentation de la scène; parcourt des collections; met à jour des variables internes; retourne un résultat; appelle add, get, scène.

- Classe `TestSceneReport` (ligne 88) : Classe de type TestSceneReport.
  - Méthode `test_scene_report_to_dict(self)` (ligne 89) : Fonction `test_scene_report_to_dict` du module. travaille sur la représentation de la scène; met à jour des variables internes; appelle assertEqual, scène, to_dict.

## tests/unit/test_speech_agent.py

- Description du module : Unit tests for SpeechAgent behavior.

- Fonction `test_speech_agent_returns_backend_info()` (ligne 5) : Fonction `test_speech_agent_returns_backend_info` du module. gère des cas conditionnels; met à jour des variables internes; appelle SpeechAgent, get, isinstance, speak.

- Fonction `test_speech_agent_high_priority_interrupts_queue()` (ligne 13) : Fonction `test_speech_agent_high_priority_interrupts_queue` du module. gère des cas conditionnels; met à jour des variables internes; appelle SpeechAgent, get, speak.

## tests/unit/test_tracker_motion.py

- Description du module : Tests for stable IDs and temporal approach estimation.

- Fonction `_person(bbox)` (ligne 6) : Fonction `_person` du module. retourne un résultat.

- Fonction `test_tracker_keeps_id_and_updates_motion()` (ligne 10) : Fonction `test_tracker_keeps_id_and_updates_motion` du module. applique le suivi d’objets; gère des cas conditionnels; met à jour des variables internes; appelle Tracker, _person, update.

- Fonction `test_approach_requires_several_consistent_frames()` (ligne 20) : Fonction `test_approach_requires_several_consistent_frames` du module. gère des cas conditionnels; met à jour des variables internes; appelle Tracker, _person, get, update.

- Fonction `test_tracker_never_matches_different_labels()` (ligne 31) : Fonction `test_tracker_never_matches_different_labels` du module. applique le suivi d’objets; gère des cas conditionnels; met à jour des variables internes; appelle Tracker, _person, update.

## tests/unit/test_utils.py

- Description du module : Unit tests for core utility functions.

- Fonction `test_ensure_directory(tmp_path)` (ligne 7) : Fonction `test_ensure_directory` du module. met à jour des variables internes; appelle ensure_directory, exists, is_dir.

- Fonction `test_normalize_bbox(tmp_path)` (ligne 14) : Fonction `test_normalize_bbox` du module. gère des cas conditionnels; met à jour des variables internes; appelle boîte de délimitation.

## tests/unit/test_vision_agent.py

- Description du module : Unit tests for VisionAgent behavior.

- Fonction `test_vision_agent_returns_category_keys(tmp_path)` (ligne 9) : Fonction `test_vision_agent_returns_category_keys` du module. gère des cas conditionnels; met à jour des variables internes; appelle VisionAgent, isinstance, mkdir, modèle, predict, zeros.
