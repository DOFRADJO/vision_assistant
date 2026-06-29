# Architecture du Vision Assistant

Ce document décrit le flux de données et les responsabilités des composants principaux du projet Vision Assistant.

## Vue d’ensemble du flux

1. Initialisation
   - `config.py` fournit la configuration globale.
   - `core/logger.py` configure la journalisation.
   - `ModelLoader` charge les détecteurs depuis `models/`.
   - `VisionAgent`, `Coordinator`, `SpeechAgent`, `MemoryAgent`, et `ReasoningAgent` sont instanciés.

2. Acquisition de la trame
   - `core.camera.CameraSource` ouvre la source vidéo configurée.
   - les trames sont capturées en boucle.
   - chaque image est redimensionnée via `core.utils.preprocess_frame()`.

3. Inférence multi-modèles
   - chaque détecteur chargé est exécuté sur la trame.
   - les modèles peuvent être :
     - ONNX (`best.onnx`),
     - PyTorch (`best.pt`),
     - détecteur factice si aucun modèle réel n’est présent.
   - `VisionAgent` centralise les résultats.

4. Normalisation des prédictions
   - chaque prédiction est convertie en JSON uniforme :
     - `label`,
     - `confidence`,
     - `bbox`,
     - `source`.
   - les boîtes de délimitation sont normalisées par `core.utils.normalize_bbox()`.

5. Raisonnement
   - `ReasoningAgent` reçoit les prédictions groupées par catégorie.
   - il applique des règles de priorité et des règles de danger.
   - il retourne :
     - un message utilisateur,
     - un niveau de priorité,
     - un drapeau d’alerte si nécessaire.

6. Mémoire et sortie
   - `MemoryAgent` empêche la répétition d’un même message pendant la période définie.
   - `SpeechAgent` diffuse le message choisi.
   - le `Coordinator` conserve le dernier résultat pour l’API et l’interface.

## Composants principaux

### `config.py`

Contient la configuration globale, regroupée en dataclasses :

- `PathConfig`
- `LoggingConfig`
- `ModelConfig`
- `SpeechConfig`
- `MemoryConfig`
- `CameraConfig`
- `AppConfig`

### `core/logger.py`

Configure la journalisation :

- console colorée,
- fichiers de log rotatifs dans `exports/logs/`,
- log d’erreurs dédié,
- log de performance.

### `core/camera.py`

Gère la source vidéo :

- webcam locale (`usb`, `laptop`),
- fichier vidéo (`video_file`),
- flux IP (`ip_camera`).

### `agents/vision/model_loader.py`

Découvre et charge les modèles :

- scanne `models/` pour les sous-dossiers,
- lit `labels.txt` et `metadata.json`,
- charge ONNX/PyTorch si disponible,
- crée un détecteur factice si aucun modèle réel n’est présent.

### `agents/vision/vision_agent.py`

Orchestre l’exécution des détecteurs et normalise les outputs.

### `agents/reasoning/reasoning_agent.py`

Applique des règles métier pour transformer les prédictions visuelles en décisions.

### `agents/memory/memory_agent.py`

Garde les messages récents et évite les annonces répétées.

### `agents/speech/speech_agent.py`

Expose un backend vocal abstrait pour console ou synthèse vocale.

### `agents/coordinator/coordinator.py`

Point central du pipeline :

- initialise les agents,
- exécute la capture, l’inférence, le raisonnement et la parole,
- gère les erreurs,
- journalise les performances.

## Flux d’exécution détaillé

### Mode desktop

1. L’utilisateur lance `python run.py --mode desktop`.
2. Le `Coordinator` est initialisé.
3. `CameraSource` ouvre la caméra.
4. Pour chaque trame :
   - le `VisionAgent` prédit les objets détectés,
   - les résultats sont envoyés au `ReasoningAgent`,
   - le `MemoryAgent` filtre les messages,
   - le `SpeechAgent` lit le message,
   - l’image annotée est affichée.

### Mode API

1. L’utilisateur lance `uvicorn app.api.main:app --reload`.
2. Le serveur FastAPI initialise les mêmes composants.
3. Les clients peuvent :
   - consulter l’état (`/status`),
   - récupérer la liste des modèles (`/models`),
   - envoyer une image pour prédiction (`/predict`),
   - demander la lecture d’un message (`/speak`),
   - récupérer le dernier résultat traité (`/frame`).

## Gestion des modèles

### Détecteurs réels

Le chargeur de modèles recherche :

- `best.onnx`
- `best.pt`

Si un modèle réel est présent, il est chargé.

### Détecteurs factices

Si aucun modèle réel n’est disponible, le système instancie un détecteur factice pour permettre le fonctionnement du pipeline sans modèles entraînés.

## Résilience et extensibilité

- les imports OpenCV sont optionnels,
- le pipeline peut fonctionner avec des détecteurs factices,
- la configuration est centralisée,
- de nouvelles règles de raisonnement peuvent être ajoutées sans modifier le pipeline principal,
- de nouveaux backends de voix peuvent être ajoutés via `SpeechAgent`.

## Conseils d’utilisation

- commencez avec le mode desktop pour vérifier que la capture fonctionne,
- utilisez la console si OpenCV n’est pas installé,
- ajoutez progressivement des modèles dans `models/`,
- surveillez `exports/logs/` pour diagnostiquer les problèmes.
