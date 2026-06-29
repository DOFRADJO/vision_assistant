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

### Critère de classification

| Classe | Critère (hauteur bbox relative) |
|--------|--------------------------------|
| `close_person` | hauteur bbox > 30% de l'image |
| `far_person` | hauteur bbox ≤ 30% de l'image |

---

## 📁 Structure du dossier

```
training/distance_detector/
├── README.md                        ← Ce fichier
├── data.yaml                        ← Configuration du dataset
├── distance_detector_colab.ipynb    ← Notebook d'entraînement (Google Colab)
├── export.py                        ← Script d'export ONNX (local)
└── predict.py                       ← Script d'inférence / test
```

---

## 🗂️ Dataset

Le dataset utilisé provient de **Roboflow Universe** (person detection).  
Il est téléchargé automatiquement dans le notebook Colab.

Les annotations YOLO d'origine (classe `person`) sont **re-labellisées automatiquement** en `close_person` / `far_person` selon la taille de la bounding box.

Format des annotations YOLO :
```
<class_id> <x_center> <y_center> <width> <height>
```

Exemple :
```
0 0.45 0.60 0.30 0.55   ← close_person
1 0.80 0.30 0.08 0.15   ← far_person
```

---

## 🚀 Entraînement (Google Colab)

L'entraînement se fait entièrement sur **Google Colab** (GPU T4 gratuit).

1. Ouvrir `distance_detector_colab.ipynb` dans Google Colab
2. Activer le GPU : **Runtime → Changer le type d'exécution → GPU**
3. Coller son snippet Roboflow dans la cellule 3
4. Exécuter toutes les cellules dans l'ordre
5. Le notebook télécharge automatiquement `best.pt` et `best.onnx`

---

## 📦 Export ONNX (local)

Si tu veux exporter en local après entraînement :

```bash
pip install ultralytics
python export.py --weights path/to/best.pt
```

---

## 🔍 Test / Inférence

```bash
pip install ultralytics opencv-python

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
- **Roboflow** (dataset)
- **Google Colab** (entraînement)
