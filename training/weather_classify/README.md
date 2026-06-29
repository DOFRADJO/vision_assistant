# 🌦️ Weather Detector — MobileNetV2

**Projet AIA-4 : Agent Intelligent et Computer Vision**  
Étudiant : TSAYO DINEL  
Modèle : `weather_detector` — Classification des conditions météorologiques

---

## 🎯 Classes détectées

| Classe | Description |
|--------|-------------|
| `cloudy` | Ciel nuageux |
| `rain` | Pluie |
| `shine` | Soleil / ciel dégagé |
| `sunrise` | Lever de soleil |

## 📦 Livrables

| Fichier | Description |
|---------|-------------|
| `best.pt` | Poids PyTorch MobileNetV2 |
| `best.onnx` | Export ONNX (opset 12) |
| `labels.txt` | Liste des classes |
| `metadata.json` | Métadonnées du modèle |

## 📤 Format de sortie JSON

```json
{
  "model": "weather_detector",
  "detections": [
    {"label": "rain", "confidence": 0.94, "bbox": []}
  ]
}
```

## 🗂️ Dataset

**Multi-class Weather Dataset (MWD)**  
Source : https://data.mendeley.com/datasets/4drtyfjtfy/1  
4 classes : `cloudy`, `rain`, `shine`, `sunrise`

## 🚀 Utilisation

```bash
# Entraînement
python train.py

# Export ONNX
python export.py

# Inférence
python predict.py --image chemin/vers/image.jpg
```

## 🏗️ Architecture

- **Modèle** : MobileNetV2 (Transfer Learning — pré-entraîné ImageNet)
- **Framework** : PyTorch + TorchVision
- **Entrée** : Image RGB 224×224
- **Sortie** : Classe météo + confidence
