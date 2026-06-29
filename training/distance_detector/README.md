# 📏 Distance Detector

**Auteur** : MBIDA NGUELE Paul Loïc  
**Projet** : Vision Assistant — ENSPY ANI-IA  
**Module** : `distance_detector`  

---

## 🎯 Mission

Ce module détecte les **personnes** dans une scène et estime si elles sont **proches** ou **éloignées** de la caméra.

Cette information est critique pour un assistant de malvoyants : une personne qui approche rapidement représente un danger potentiel.

---

## 🏷️ Classes détectées

| ID | Label | Description |
|----|-------|-------------|
| 0 | `close_person` | Personne proche (grande bounding box) |
| 1 | `far_person` | Personne éloignée (petite bounding box) |

---

## 📁 Structure du dossier

```
training/distance_detector/
├── README.md       ← Ce fichier
├── data.yaml       ← Configuration du dataset
├── train.py        ← Script d'entraînement
├── export.py       ← Script d'export ONNX
└── predict.py      ← Script d'inférence / test
```

---

## ⚙️ Installation

```bash
pip install ultralytics opencv-python
```

---

## 🗂️ Préparer le dataset

Organiser le dataset comme suit :

```
dataset/
├── images/
│   ├── train/     ← images d'entraînement (.jpg / .png)
│   └── val/       ← images de validation
└── labels/
    ├── train/     ← annotations YOLO (.txt)
    └── val/
```

### Format des annotations YOLO

Chaque fichier `.txt` correspond à une image :

```
<class_id> <x_center> <y_center> <width> <height>
```

Exemple :
```
0 0.45 0.60 0.30 0.55   ← close_person
1 0.80 0.30 0.08 0.15   ← far_person
```

### Critère de classification distance

| Classe | Critère (hauteur bbox relative) |
|--------|--------------------------------|
| `close_person` | hauteur bbox > 30% de l'image |
| `far_person` | hauteur bbox ≤ 30% de l'image |

---

## 🚀 Entraînement

```bash
python train.py
```

Les poids entraînés seront disponibles dans :
```
runs/detect/distance_detector/weights/best.pt
```

---

## 📦 Export ONNX

```bash
python export.py
```

Les livrables sont automatiquement copiés dans `models/distance_detector/`.

---

## 🔍 Test / Inférence

```bash
# Sur une image
python predict.py --source image.jpg

# Sur une vidéo avec affichage visuel
python predict.py --source video.mp4 --show

# Sur la webcam
python predict.py --source 0 --show
```

---

## 📤 Format de sortie (contrat d'interface)

```json
{
  "model": "distance_detector",
  "detections": [
    {
      "label": "close_person",
      "confidence": 0.91,
      "bbox": [120, 85, 230, 470]
    },
    {
      "label": "far_person",
      "confidence": 0.87,
      "bbox": [360, 80, 510, 470]
    }
  ]
}
```

---

## 🔧 Technologies

- **YOLOv8n** (Ultralytics)
- **PyTorch**
- **ONNX**
- **OpenCV**
