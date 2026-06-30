# Vision Assistant — Référence Complète du Code

## Table des matières
1. [Fichiers racine](#fichiers-racine)
2. [agents/coordinator/](#agentscoordinator)
3. [agents/fusion/](#agentsfusion)
4. [agents/memory/](#agentsmemory)
5. [agents/reasoning/](#agentsreasoning)
6. [agents/speech/](#agentsspeech)
7. [agents/tracking/](#agentstracking)
8. [agents/vision/](#agentsvision)
9. [app/api/](#appapi)
10. [app/desktop/](#appdesktop)
11. [app/mobile/](#appmobile)
12. [core/](#core)
13. [scripts/](#scripts)
14. [training/](#training)
15. [tests/](#tests)

---

## Fichiers racine

### `config.py`
Configuration centrale de l'application. Contient toutes les constantes regroupées en dataclasses.

| Classe | Rôle |
|---|---|
| `CameraConfig` | Source vidéo, résolution (640×480), FPS |
| `SpeechConfig` | Backend TTS, langue (fr), débit, volume |
| `MemoryConfig` | Timeout anti-répétition (3s), historique max |
| `TrackingConfig` | Type de tracker (IoU), seuils de matching |
| `ModelConfig` | Backend ONNX/PyTorch, seuil de confiance (0.25), workers (4) |
| `ApiConfig` | Hôte et port du serveur FastAPI |
| `PathsConfig` | Chemins vers models/, datasets/, exports/, logs/ |
| `LoggingConfig` | Niveau de log, rotation des fichiers |
| `VisionAssistantConfig` | Agrège toutes les configs ci-dessus |

| Fonction | Rôle |
|---|---|
| `get_config()` | Singleton — retourne l'instance unique de VisionAssistantConfig |

### `run.py`
Point d'entrée du pipeline desktop. Instancie `DesktopApp` et appelle `app.run()`.

| Fonction | Rôle |
|---|---|
| `main()` | Configure le logging, crée DesktopApp, lance la boucle vidéo |

### `setup.py`
Fichier vide — placeholder pour un futur packaging pip.

---

## agents/coordinator/

### `coordinator.py`
Chef d'orchestre du pipeline multi-agent. Reçoit une frame, la distribue aux agents, collecte les résultats.

| Fonction | Rôle |
|---|---|
| `__init__()` | Instancie tous les agents (Vision, Tracking, Reasoning, Speech, ConversationManager) |
| `initialize()` | Charge les modèles ONNX, affiche le résumé de démarrage |
| `_log_startup()` | Affiche dans les logs la liste des modèles chargés et la config caméra |
| `process_frame(frame)` | **Pipeline principal** : Time-Slicing → Vision → SceneBuilder → Tracking → SceneMemory → Interpreter → ConversationManager → DecisionEngine → SpeechPlanner → SpeechAgent |

### `registry.py`
Registre simple des modèles chargés.

| Classe | Rôle |
|---|---|
| `RegisteredModel` | Dataclass contenant le nom et les métadonnées d'un modèle |
| `ModelRegistry` | Dictionnaire de modèles enregistrés |

| Fonction | Rôle |
|---|---|
| `register(name, model)` | Ajoute un modèle au registre |
| `list_models()` | Retourne la liste des noms enregistrés |
| `get(name)` | Récupère un modèle par son nom |

---

## agents/fusion/

### `scene.py`
Structures de données centrales du système.

| Classe | Rôle |
|---|---|
| `SceneObject` | Un objet détecté avec label, bbox, confiance, catégorie, tracking_id, et métadonnées calculées (width, height, center) |
| `Scene` | Conteneur unifié de tous les objets détectés, organisés par catégorie (persons, vehicles, food, etc.) |

| Fonction (Scene) | Rôle |
|---|---|
| `add(bucket, obj)` | Ajoute un objet dans la catégorie appropriée + dans all_objects |
| `remove(obj)` | Retire un objet d'une catégorie |
| `get(bucket)` | Retourne la liste des objets d'une catégorie |
| `count(bucket)` | Compte les objets d'une catégorie (ou tous si None) |
| `summary()` | Retourne un dict {catégorie: nombre} pour toutes les catégories |
| `to_dict()` | Sérialise la scène complète en dictionnaire JSON |

### `scene_builder.py`
Construit une Scene unifiée à partir des sorties brutes des détecteurs.

| Classe | Rôle |
|---|---|
| `SceneBuilder` | Transforme les prédictions brutes multi-modèles en un objet Scene cohérent |

| Fonction | Rôle |
|---|---|
| `_normalize_text(text)` | Normalise un label en minuscules sans espaces superflus |
| `_bucket_for(label)` | Détermine dans quelle catégorie (persons, vehicles, food…) classer un label |
| `_normalize_bbox(bbox, shape)` | Convertit une bbox en coordonnées normalisées |
| `build_scene(raw_predictions)` | **Méthode principale** — itère les prédictions de tous les modèles, crée les SceneObjects, déduplique, retourne une Scene |
| `_iou(box1, box2)` | Calcule l'Intersection over Union entre deux bboxes |
| `_remove_cross_model_duplicates(scene)` | Supprime les doublons quand deux modèles détectent le même objet |
| `summarize(scene)` | Résumé texte de la scène pour le debug |

### `fusion_agent.py`
Agent de fusion haut-niveau (wrapper léger autour de SceneBuilder).

| Fonction | Rôle |
|---|---|
| `fuse(raw_predictions)` | Appelle SceneBuilder.build_scene() et retourne la Scene |

### `labels.py`
Registre centralisé de tous les labels connus par les modèles.

| Classe | Rôle |
|---|---|
| `LabelsRegistry` | Singleton qui charge et indexe les labels depuis les fichiers labels.txt de chaque modèle |

| Fonction | Rôle |
|---|---|
| `get_instance()` | Retourne l'instance singleton |
| `_load()` | Parcourt models/ et charge tous les labels.txt |
| `has_label(label)` | Vérifie si un label est connu |
| `labels_for_model(model_name)` | Retourne les labels d'un modèle spécifique |

---

## agents/memory/

### `memory_agent.py`
Agent de mémoire pour éviter les répétitions vocales.

| Fonction | Rôle |
|---|---|
| `__init__(timeout)` | Initialise avec un timeout de déduplication |
| `should_emit(event)` | Retourne True si l'événement n'a pas été émis récemment |
| `get_history()` | Retourne l'historique des événements récents |

### `history.py`
Fichier vide — placeholder pour un futur historique persistant.

---

## agents/reasoning/

### `scene_rules.py`
Catalogue de toutes les règles métier pour interpréter une scène visuelle.

| Classe | Rôle |
|---|---|
| `SceneRule` | Dataclass décrivant une règle : condition (lambda), summary, danger_level, priority, events, recommendations |

| Fonction | Rôle |
|---|---|
| `_normalize_label(value)` | Met un label en minuscules nettoyé |
| `has_label(scene, label)` | Vérifie si un label est présent dans la scène |
| `has_any_label(scene, labels)` | Vérifie si au moins un label d'une liste est présent |
| `count_category(scene, category)` | Compte les objets d'une catégorie dans la scène |
| `category_is_approaching(scene, cat)` | Vérifie si un objet d'une catégorie a la métadonnée "approaching" |
| `important_objects(scene, labels, cats)` | Retourne les objets correspondant aux labels/catégories importants |
| `select_applicable_rules(scene)` | Retourne toutes les règles dont la condition est vraie pour la scène |
| `choose_important_objects(scene, rules)` | Sélectionne les objets les plus pertinents selon les règles matchées |

**Règles définies** : vehicle_approaching, person_approaching, wet_floor, traffic_light_red, green_light_crosswalk, dog_with_person, person_at_door, vehicle_at_crosswalk, stairs_present, single_person, multiple_persons, vehicle_present, crosswalk_present, sidewalk_present, food_present.

### `scene_interpreter.py`
Moteur de Génération de Langage Naturel (NLG). Transforme une Scene en un SceneReport avec une phrase française grammaticalement correcte.

| Classe | Rôle |
|---|---|
| `SceneReport` | Résultat structuré : summary (phrase), danger_level, priority, events, recommendations, important_objects |
| `SceneInterpreter` | Classe principale qui orchestre l'interprétation |

| Fonction | Rôle |
|---|---|
| `get_spatial_context(obj)` | Calcule la position (gauche/droite/centre) et la distance (très près/moyenne/au loin) d'un objet via la géométrie de sa bbox |
| `build_natural_summary(scene, rules)` | **Cœur du NLG** — construit dynamiquement une phrase française fluide en analysant les comptages, les approches, et les catégories mineures |
| `interpret(scene)` | Méthode principale : applique les règles, génère le summary, collecte les events, retourne un SceneReport |
| `_default_report()` | Retourne un SceneReport par défaut quand rien n'est détecté |
| `_highest_danger_level(rules)` | Détermine le niveau de danger le plus élevé parmi les règles matchées |
| `_merge_unique(items)` | Déduplique une liste de recommandations |

### `decision_engine.py`
Moteur de décision qui choisit si une annonce vocale doit être émise.

| Classe | Rôle |
|---|---|
| `Decision` | Résultat : priority, action (SPEAK/IGNORE), message, reason, danger_level |
| `DecisionEngine` | Applique un système de priorités et de TTL (Time-To-Live) anti-spam |

| Fonction | Rôle |
|---|---|
| `__init__(priority_map, ttl_map)` | Initialise les tables de priorités et de TTL par type d'événement |
| `decide(report)` | Analyse les events du SceneReport, choisit le plus prioritaire, vérifie le TTL, retourne SPEAK ou IGNORE |
| `reset()` | Remet l'état interne à zéro |

### `conversation_manager.py`
Stabilisateur d'annonces vocales. Empêche les variations mineures de comptage de provoquer des annonces répétées.

| Classe | Rôle |
|---|---|
| `CountBucket` | Enum : NONE (0), ONE (1), MULTIPLE (≥2) |
| `AnnouncementDecision` | Résultat : allowed (bool), reason (str), changed_categories |
| `ConversationManager` | Gate qui quantise les comptages en buckets et n'autorise les annonces que lors de transitions significatives |

| Fonction | Rôle |
|---|---|
| `from_count(n)` | Convertit un entier en bucket (NONE/ONE/MULTIPLE) |
| `should_announce(report)` | **API principale** — retourne True uniquement si un bucket a changé OU si un événement critique est détecté |
| `reset()` | Remet tous les buckets à NONE |
| `_compute_buckets(report)` | Extrait les comptages par catégorie depuis le scene_summary et les quantise |

### `scene_memory.py`
Mémoire de la scène pour détecter les apparitions/disparitions d'objets.

| Classe | Rôle |
|---|---|
| `SceneMemoryObject` | Objet mémorisé avec id, label, bbox, position, timestamps |
| `SceneMemory` | Suit l'évolution de la scène frame par frame |

| Fonction | Rôle |
|---|---|
| `update(scene)` | Met à jour la mémoire avec la scène courante, génère les événements d'apparition/disparition |
| `get_new_events()` | Retourne les événements générés par la dernière mise à jour |
| `has_changed()` | True si la scène a changé de manière significative |
| `should_speak(text)` | Anti-spam : True si le texte n'a pas été prononcé dans la fenêtre de cooldown |
| `_compute_key(obj)` | Calcule une clé unique par objet (tracking_id ou grille spatiale) |
| `_approximate_position(bbox)` | Retourne une position textuelle (haut/bas, gauche/droite) |
| `_appearance_message(obj)` | Génère "Nouveau X détecté à Y" |
| `_disappearance_message(obj)` | Génère "X disparu" |
| `_singular_label(label)` | Convertit un label en singulier français |
| `_plural_label(label)` | Convertit un label en pluriel français |

### `danger_rules.py`
Règles de risque héritées (utilisées par ReasoningAgent).

| Fonction | Rôle |
|---|---|
| `_make_event(type, msg, prio)` | Crée un dictionnaire d'événement structuré |
| `_add_event(events, type, msg, prio)` | Ajoute un événement à la liste |
| `build_risk_profile(data)` | Dispatche vers le bon constructeur selon le type de données |
| `_build_risk_profile_from_detections()` | Analyse une liste de détections brutes |
| `_build_risk_profile_from_scene()` | Analyse une Scene fusionnée |

### `reasoning_agent.py`
Agent de raisonnement haut-niveau (wrapper).

| Fonction | Rôle |
|---|---|
| `analyze_scene(predictions)` | Appelle build_risk_profile() et retourne les événements |

### `priority_agent.py`
Agent de tri par priorité.

| Fonction | Rôle |
|---|---|
| `select_top_events(events, limit)` | Trie les événements par priorité et retourne les N premiers |

### `priority_manager.py`
Utilitaire de tri.

| Fonction | Rôle |
|---|---|
| `sort_messages(messages)` | Trie une liste de messages par priorité décroissante |

---

## agents/speech/

### `speech_agent.py`
Agent de synthèse vocale (TTS). Gère une file d'attente et un thread dédié pour la lecture audio.

| Fonction | Rôle |
|---|---|
| `__init__(config)` | Initialise le moteur TTS (pyttsx3) dans un thread séparé |
| `_initialize_engine()` | Configure pyttsx3 avec la langue, le débit et le volume |
| `_run()` | Boucle du thread TTS — consomme la file d'attente |
| `_speak(text)` | Prononce un texte via le moteur TTS |
| `speak(text, priority)` | Ajoute un message à la file (avec gestion de priorité) |
| `stop()` | Arrête proprement le thread TTS |

### `speech_planner.py`
Traduit une Decision en plan de parole.

| Fonction | Rôle |
|---|---|
| `plan(decision)` | Si decision.action == "SPEAK", retourne [{message, priority, label}]. Sinon [] |
| `_format_message(event)` | Formate un événement brut en phrase (fallback anglais, non utilisé dans le pipeline actuel) |

### `tts.py`
Fichier vide — placeholder pour un futur moteur TTS alternatif.

---

## agents/tracking/

### `tracking_agent.py`
Agent de suivi temporel des objets entre frames.

| Classe | Rôle |
|---|---|
| `TrackingAgent` | Assigne des tracking_id persistants aux objets de la scène grâce au Tracker IoU |

| Fonction | Rôle |
|---|---|
| `__init__(tracker_type, iou_threshold, max_age, min_hits)` | Initialise le tracker avec les paramètres de matching |
| `track(scene)` | Reçoit une Scene, applique le tracking IoU, enrichit les objets avec tracking_id et métadonnées de mouvement (approaching), retourne la scène enrichie |

---

## agents/vision/

### `model_loader.py`
Chargeur et gestionnaire de tous les modèles YOLO (ONNX et PyTorch).

| Classe | Rôle |
|---|---|
| `ModelInfo` | Métadonnées d'un modèle : nom, catégorie, chemins, labels, session ONNX |
| `ModelLoader` | Découvre, charge, et exécute les modèles depuis le dossier models/ |

| Fonction | Rôle |
|---|---|
| `normalize_category(name)` | Convertit un nom de dossier en clé de catégorie (people_detector → people) |
| `load_all_models()` | Découvre et charge tous les modèles du dossier models/ |
| `refresh_models()` | Recharge si les fichiers modèles ont changé |
| `load_model(name)` | Charge un seul modèle par nom de dossier |
| `_initialize_real_detector()` | Initialise la session ONNX ou le modèle PyTorch |
| `_load_onnx_session(path)` | Crée une session ONNX Runtime |
| `_read_onnx_labels(session)` | Lit les noms de classes embarqués dans les métadonnées ONNX |
| `_resolve_onnx_input_size()` | Détermine la taille d'entrée (depuis ONNX, metadata.json, ou config) |
| `_prepare_image(image, shape)` | Redimensionne et normalise une image pour l'inférence (LetterBox) |
| `_parse_raw_predictions()` | Décode les tenseurs ONNX bruts en détections {label, bbox, confidence} via NMS |
| `_predict_onnx(model, image)` | Exécute l'inférence ONNX sur une image |
| `_predict_torch(model, image)` | Exécute l'inférence PyTorch sur une image |
| `predict(name, image)` | Prédit avec un détecteur nommé, retourne les détections normalisées |
| `predict_all(image)` | Exécute TOUS les détecteurs (en parallèle selon max_workers) |
| `_normalize_prediction()` | Décode le label, normalise la bbox |

### `vision_agent.py`
Agent de vision haut-niveau.

| Fonction | Rôle |
|---|---|
| `__init__(model_loader, config)` | Reçoit le ModelLoader partagé |
| `load_models()` | Appelle model_loader.load_all_models() |
| `predict(frame, frame_id)` | Appelle model_loader.predict_all(frame) et retourne les résultats structurés |

### `model_loader_backup.py`
Sauvegarde de l'ancien model_loader (non utilisé en production).

---

## app/api/

### `main.py`
Serveur REST FastAPI pour exposer le pipeline en HTTP.

| Endpoint | Rôle |
|---|---|
| `GET /status` | État du système (modèles chargés, FPS, etc.) |
| `GET /models` | Liste des modèles disponibles |
| `GET /history` | Historique des événements récents |
| `GET /config` | Configuration active |
| `POST /predict/image` | Envoie une image, reçoit les détections |
| `POST /predict/video` | Traite une vidéo frame par frame |
| `POST /reload` | Recharge les modèles à chaud |
| `POST /speak` | Déclenche manuellement une annonce vocale |
| `GET /frame` | Retourne la dernière frame traitée |

---

## app/desktop/

### `desktop_app.py`
Application de bureau avec fenêtre OpenCV.

| Fonction | Rôle |
|---|---|
| `__init__(config)` | Instancie le Coordinator et le CameraManager |
| `run()` | Boucle principale : capture frame → process_frame → affichage OpenCV → touche 'q' pour quitter |

---

## app/mobile/

### `index.js`
Point d'entrée React Native. Enregistre le composant `App`.

### `App.tsx` (racine)
Template React Native par défaut (non utilisé, remplacé par src/App.tsx).

### `src/App.tsx`
Application mobile principale. Utilise react-native-vision-camera pour capturer les frames, exécute les modèles ONNX via onnxruntime-react-native, et génère les annonces via react-native-tts.

### `src/agents/ReasoningAgent.ts`
Version TypeScript du moteur de raisonnement pour le mobile.

| Interface | Rôle |
|---|---|
| `Detection` | {label, confidence, bbox} — une détection YOLO |

### `src/agents/MemoryAgent.ts`
Mémoire anti-répétition pour le mobile (équivalent de SceneMemory).

### `src/components/BoundingBoxOverlay.tsx`
Composant React Native qui dessine les bounding boxes sur l'écran.

### `src/utils/YoloPostProcess.ts`
Post-processing des sorties YOLO (NMS, décodage) côté mobile.

---

## core/

### `camera.py`
Gestion de la source vidéo (webcam, fichier vidéo, caméra IP).

| Classe | Rôle |
|---|---|
| `CameraManager` | Gère l'ouverture, la lecture et la libération d'une source vidéo OpenCV |
| `CameraSource` | Wrapper rétrocompatible pour les anciens clients |

| Fonction | Rôle |
|---|---|
| `open()` | Ouvre la source vidéo configurée |
| `resolve_source()` | Résout le type de source (webcam index, chemin fichier, URL IP) |
| `read()` | Lit une frame, la redimensionne si nécessaire |
| `release()` | Libère la ressource vidéo |

### `tracker.py`
Tracker IoU pour le suivi temporel des objets.

| Classe | Rôle |
|---|---|
| `Track` | Un objet suivi avec ID, bbox, âge, nombre de hits |
| `Tracker` | Associe les détections courantes aux tracks existants via IoU |

| Fonction | Rôle |
|---|---|
| `_compute_iou(box1, box2)` | Calcule l'IoU entre deux bounding boxes |
| `update(detections)` | Met à jour les tracks avec les nouvelles détections (association hongroise simplifiée) |
| `_motion_metadata(track)` | Calcule si un objet s'approche (bbox qui grandit = approaching) |

### `utils.py`
Utilitaires partagés.

| Fonction | Rôle |
|---|---|
| `ensure_directory(path)` | Crée un dossier s'il n'existe pas |
| `safe_read_text(path)` | Lit un fichier texte sans lever d'exception |
| `serialize_json(data)` | Sérialise en JSON avec gestion des types numpy |
| `normalize_bbox(bbox, shape)` | Normalise une bbox en coordonnées relatives [0,1] |
| `draw_predictions(frame, preds)` | Dessine les bounding boxes sur une image OpenCV |

### `logger.py`
Configuration du système de logging.

| Fonction | Rôle |
|---|---|
| `configure_logging(config)` | Configure le format, le niveau, et la rotation des logs |

### Fichiers vides (placeholders)
- `distance_estimator.py` — futur estimateur de distance par profondeur
- `object_counter.py` — futur compteur d'objets avancé
- `scene_analyzer.py` — futur analyseur de scène haut-niveau

---

## scripts/

### `debug_model.py`
Outil CLI pour debugger un modèle ONNX individuellement.

| Fonction | Rôle |
|---|---|
| `parse_args()` | Parse les arguments CLI (chemin modèle, image) |
| `main()` | Charge un modèle, exécute l'inférence, affiche les résultats |

### `integrate_model.py`
Outil CLI pour intégrer un nouveau modèle dans le projet.

| Fonction | Rôle |
|---|---|
| `validate_files(path)` | Vérifie que best.onnx et labels.txt existent |
| `integrate_model(src, dest)` | Copie les fichiers du modèle dans models/ |
| `main()` | Parse les arguments et lance l'intégration |

---

## training/

### `model_template/`
Template réutilisable pour entraîner un nouveau détecteur YOLO.

| Fichier | Rôle |
|---|---|
| `train.py` | Script d'entraînement YOLO (ultralytics) avec data.yaml |
| `predict.py` | Script de prédiction/test sur des images |
| `export.py` | Script d'export du modèle .pt vers .onnx |

### `obstacle_detector/` et `people_detector/`
Dossiers de modèles entraînés. Contiennent `best.onnx`, `best.pt`, `labels.txt`, `metadata.json`. Les scripts .py sont vides (l'entraînement a été fait manuellement).

---

## tests/

| Fichier | Ce qu'il teste |
|---|---|
| `test_conversation_manager.py` | ConversationManager : buckets, stabilisation, bypass critique, cooldown |
| `test_integration.py` | Pipeline de bout en bout |
| `integration/test_pipeline.py` | Pipeline complet avec modèles réels |
| `unit/test_camera_source.py` | CameraSource et CameraManager |
| `unit/test_config.py` | Chargement de VisionAssistantConfig |
| `unit/test_decision_engine.py` | DecisionEngine : priorités, TTL, SPEAK/IGNORE |
| `unit/test_memory_agent.py` | MemoryAgent : déduplication |
| `unit/test_model_loader.py` | ModelLoader : chargement ONNX, prédiction |
| `unit/test_reasoning_agent.py` | ReasoningAgent : analyse de scène |
| `unit/test_reasoning.py` | Règles de danger |
| `unit/test_scene_builder.py` | SceneBuilder : fusion, déduplication |
| `unit/test_scene_interpreter.py` | SceneInterpreter : NLG, règles |
| `unit/test_speech_agent.py` | SpeechAgent : file d'attente TTS |
| `unit/test_tracker_motion.py` | Tracker : IoU, mouvement, approaching |
| `unit/test_utils.py` | Fonctions utilitaires |
| `unit/test_vision_agent.py` | VisionAgent : predict() |

---

## Pipeline complet (ordre d'exécution)

```
1. run.py → DesktopApp.run()
2.   CameraManager.read() → frame
3.   Coordinator.process_frame(frame)
4.     Time-Slicing (filtre les modèles selon frame_count)
5.     VisionAgent.predict() → ModelLoader.predict_all()
6.       9 modèles ONNX en parallèle (max_workers=4)
7.     SceneBuilder.build_scene() → Scene
8.     TrackingAgent.track() → Scene enrichie (tracking_id, approaching)
9.     SceneMemory.update() → événements apparition/disparition
10.    SceneInterpreter.interpret() → SceneReport (NLG français)
11.    ConversationManager.should_announce() → True/False
12.    DecisionEngine.decide() → Decision (SPEAK/IGNORE)
13.    SpeechPlanner.plan() → [{message, priority}]
14.    SceneMemory.should_speak() → anti-spam
15.    SpeechAgent.speak() → pyttsx3 TTS
16.  OpenCV affichage + bounding boxes
```
