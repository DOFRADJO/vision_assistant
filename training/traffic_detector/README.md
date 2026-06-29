# crosswalk_traffic_light_detector

Module du projet collectif **Agent Intelligent de Vision Assistée pour Personnes Malvoyantes**.

Détecte les passages piétons et les feux (véhicules + piétons), avec leur
état (rouge / jaune / vert), à partir d'une image. Basé sur YOLOv8n
(transfer learning depuis les poids pré-entraînés COCO).

## Contrat de sortie

Identique à celui de tous les autres modèles du projet (`people_detector`,
`vehicle_detector`, `food_detector`, etc.) :

```json
{
    "model": "crosswalk_traffic_light_detector",
    "detections": [
        {
            "label": "pedestrian_signal_red",
            "confidence": 0.91,
            "bbox": [120, 85, 230, 470]
        }
    ]
}
```

## Classes détectées

| id | label                      |
|----|----------------------------|
| 0  | crosswalk                  |
| 1  | traffic_light_red          |
| 2  | traffic_light_yellow       |
| 3  | traffic_light_green        |
| 4  | pedestrian_signal_red      |

## Structure du dossier

```
crosswalk_traffic_light_detector/
├── README.md
├── data.yaml          # config du dataset (chemins + classes)
├── train.py           # entraînement (transfer learning YOLOv8n)
├── export.py           # génère best.onnx, labels.txt, metadata.json
├── predict.py           # inférence -> JSON conforme au contrat
├── best.pt              # généré par train.py
├── best.onnx             # généré par export.py
├── labels.txt             # généré par export.py
└── metadata.json           # généré par export.py
```

## Installation

```bash
pip install ultralytics onnx onnxruntime pyyaml pillow numpy
```

## Dataset

Télécharger un dataset au format YOLOv8 depuis Roboflow Universe (chercher
un dataset combinant passages piétons + feux avec état, ou fusionner
plusieurs sources). Placer les données dans :

```
data/
├── train/images/  + train/labels/
├── valid/images/  + valid/labels/
└── test/images/   + test/labels/   (optionnel)
```

Adapter `data.yaml` si les noms de classes du dataset téléchargé diffèrent
de ceux listés ci-dessus.

## Utilisation

```bash
# 1. Entraînement (produit best.pt)
python train.py

# 2. Export des livrables (produit best.onnx, labels.txt, metadata.json)
python export.py

# 3. Test d'inférence sur une image
python predict.py chemin/vers/image.jpg
```

## Livrables finaux

- `best.pt` — poids PyTorch
- `best.onnx` — export ONNX (exécution mobile / cross-platform)
- `labels.txt` — une classe par ligne
- `metadata.json` — description du modèle et du contrat de sortie

Ce module ne touche à aucun autre dossier `training/<autre_modele>/`.