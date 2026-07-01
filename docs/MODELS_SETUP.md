# Installation des modeles (hors Git)

Les poids ONNX / PyTorch ne sont **pas versionnes** (fichiers trop lourds).
Chaque membre de l'equipe doit disposer des modeles en local.

## Detecteurs specialises (13 agents vision)

Copier ou exporter les modeles dans `models/<detecteur>/` :

```
models/
  animal_detector/best.onnx
  bag_detector/best.onnx
  cross_traffic_detector/best.onnx
  detection_portes/best.onnx
  distance_detector/best.onnx
  electronic_detector/best.onnx
  food_detector/best.onnx
  furniture_detector/best.onnx
  obstacle_detector/best.onnx
  people_detector/best.onnx      # requis par le coordinateur
  people_tracking/best.onnx
  sidewalk_detector/best.onnx
  traffic_detector/best.onnx
  wall_switch_detection/best.onnx
```

Chaque dossier doit aussi contenir `labels.txt` et `metadata.json` (deja dans le depot).

Source : dossiers `training/<detecteur>/` apres entrainement, ou partage equipe (Drive, release GitHub).

## Modele global NAVIS (18 classes COCO)

Pour l'application Flutter (`mobile/`) :

```
mobile/assets/models/navis_18classes.onnx
```

Source : export depuis le pipeline ML global du projet NAVIS.

## Video de demonstration Flutter

```
mobile/assets/videos/demo.mp4
```

Copier depuis le dossier NAVIS d'origine ou partage equipe (~23 Mo).

## Verification

```bash
python scripts/debug_model.py
cd mobile && flutter pub get && flutter run
```
