# Branche finalisation — integration NAVIS

## Contenu de cette branche

- **Pipeline multi-agents Python** (`agents/`, `run.py`) : 13 detecteurs specialises + coordinateur
- **App Flutter NAVIS** (`mobile/`) : application produit hors ligne (voix, camera, demo)
- **Prototype React Native** (`app/mobile/`) : ancien prototype, conserve pour reference
- **Modeles** : non versionnes (voir `docs/MODELS_SETUP.md`)

## Architecture multi-agents (cours Agent IA)

```
Camera / Video
    → Coordinator (time-slicing des 13 modeles)
    → VisionAgent (inference ONNX parallele)
    → SceneBuilder (fusion)
    → TrackingAgent
    → SceneInterpreter + ConversationManager
    → DecisionEngine → SpeechPlanner → SpeechAgent
```

| Agent / module | Role |
|----------------|------|
| **Coordinator** | Orchestre la boucle frame, active 3-6 modeles par frame |
| **VisionAgent** | Charge et execute les detecteurs ONNX |
| **SceneBuilder** | Fusionne les detections en scene unifiee |
| **TrackingAgent** | IDs stables (IoU tracker) |
| **SceneInterpreter** | Regles metier, danger, position |
| **ConversationManager** | Anti-spam vocal |
| **DecisionEngine** | Priorise les annonces |
| **SpeechAgent** | TTS / console |

## 13 detecteurs (1 etudiant / specialite)

| Detecteur | Domaine |
|-----------|---------|
| people_detector | Personnes |
| people_tracking | Suivi personnes |
| obstacle_detector | Obstacles |
| distance_detector | Estimation distance |
| traffic_detector | Trafic |
| cross_traffic_detector | Traversée |
| sidewalk_detector | Trottoir |
| detection_portes | Portes |
| furniture_detector | Mobilier |
| electronic_detector | Appareils |
| food_detector | Nourriture |
| animal_detector | Animaux |
| wall_switch_detection | Interrupteurs |
| bag_detector | Sacs (present, pas encore dans time-slice) |

## Modele global (18 classes COCO)

`mobile/assets/models/navis_18classes.onnx` — utilise par l'app Flutter en attendant l'integration des 13 agents.

## Prochaine etape : integration

1. Exposer le pipeline Python via API (`app/api/main.py`) ou FFI
2. Remplacer / completer `YoloDetector` Flutter par appels aux 13 modeles
3. Porter la logique `SceneInterpreter` Python vers Dart ou appeler l'API locale
