# 🎯 People Tracking - Mouvement et Tracking Personnes

**Projet** : AIA-4 -- Agent Intelligent et Computer Vision  
**Auteur** : MEZAGO WILFRIED AYMAR  
**Encadrant** : M. TINKU Claude  
**Année académique** : 2025–2026

---

## Description

Ce module assure la **détection et le suivi des personnes** dans un flux vidéo en temps réel.
Il constitue le composant `people_tracking` du système Vision Assistant.

Le modèle détecte les personnes présentes dans une scène, leur attribue un identifiant
de suivi persistant entre les frames, estime leur direction de mouvement et signale
lorsqu'une personne s'approche de la caméra.

---

## Livrables

| Fichier | Description |
|---|---|
| `best.pt` | Poids PyTorch du meilleur modèle (22.5 Mo) |
| `best.onnx` | Modèle exporté ONNX pour déploiement mobile (44.7 Mo) |
| `labels.txt` | Liste des classes détectées |
| `metadata.json` | Métadonnées et métriques du modèle |


---

## Modèle

| Paramètre | Valeur |
|---|---|
| Architecture | YOLOv8s |
| Dataset | COCO 2017 (classe `person`) |
| Taille d'entrée | 640 × 640 px |
| Tracker | ByteTrack (centroïde) |
| Format d'export | ONNX opset 12 |

---

## Métriques

| Métrique | Valeur |
|---|---|
| mAP@0.5 | 0.6597 |
| mAP@0.5:0.95 | 0.3930 |
| Précision | 0.7402 |
| Rappel | 0.5874 |

---

## Contrat d'interface

Ce module respecte le contrat d'interface commun à tous les modèles du projet.

```json
{
  "model": "motion_tracker",
  "detections": [
    {
      "label": "person",
      "confidence": 0.92,
      "bbox": [120, 85, 230, 470],
      "track_id": 1,
      "movement_direction": "left",
      "approaching": false
    }
  ]
}
```

### Champs étendus spécifiques à ce module

| Champ | Type | Description |
|---|---|---|
| `track_id` | int | Identifiant unique de la personne entre les frames |
| `movement_direction` | string | Direction estimée : `left`, `right`, `up`, `down`, `stationary` |
| `approaching` | bool | `true` si la personne s'approche de la caméra |

---

## Utilisation

### Inférence avec le modèle PyTorch

```bash
python inference.py --source video.mp4 --weights best.pt --show
```

### Inférence avec le modèle ONNX

```bash
python inference.py --source video.mp4 --weights best.onnx --onnx
```

### Webcam en temps réel

```bash
python inference.py --source 0 --weights best.pt --show
```

### Export ONNX depuis best.pt

```bash
python export_onnx.py --weights best.pt --imgsz 640 --opset 12
```

---

## Entraînement


Étapes principales :
1. Installation des dépendances
2. Chargement du dataset COCO (classe `person`)
3. Configuration des hyperparamètres
4. Entraînement YOLOv8s avec augmentations
5. Évaluation sur le jeu de validation
6. Export ONNX
7. Validation du modèle exporté

---

## Dépendances

```bash
pip install ultralytics onnx onnxruntime opencv-python
```

---

## Structure du dossier

```
training/people_tracking/
├── best.pt
├── best.onnx
├── labels.txt
├── metadata.json
└── README.md
```