import shutil
from pathlib import Path

from ultralytics import YOLO

DATASET_YAML = "data.yaml"
BASE_MODEL = "yolov8n.pt" # nano 
EPOCHS = 30                 
IMG_SIZE = 320              
BATCH_SIZE = 8                
PATIENCE = 10 # early stopping 
RUN_NAME = "train"
DEVICE = "cpu"                 
WORKERS = 2                     

def main():
    model = YOLO(BASE_MODEL)

    train_results = model.train(
        data=DATASET_YAML,
        epochs=EPOCHS,
        imgsz=IMG_SIZE,
        batch=BATCH_SIZE,
        patience=PATIENCE,
        device=DEVICE,
        workers=WORKERS,
        project="runs",
        name=RUN_NAME,
        # Augmentations adaptées au contexte piéton/rue :
        # - pas de flip vertical (un feu à l'envers n'a pas de sens)
        # - rotation légère seulement (caméra piéton rarement très inclinée)
        # - hsv_v modéré : conditions de luminosité variables (jour/nuit/ombre)
        flipud=0.0,
        fliplr=0.5,
        degrees=5.0,
        translate=0.1,
        scale=0.4,
        hsv_h=0.015,
        hsv_s=0.5,
        hsv_v=0.3,
    )

    metrics = model.val(data=DATASET_YAML, project="runs", name=f"{RUN_NAME}_val")
    print("\n=== Résultats de validation ===")
    print(f"mAP50     : {metrics.box.map50:.4f}")
    print(f"mAP50-95  : {metrics.box.map:.4f}")
    print(f"Precision : {metrics.box.mp:.4f}")
    print(f"Recall    : {metrics.box.mr:.4f}")

    run_save_dir = Path(model.trainer.save_dir)
    best_pt_source = run_save_dir / "weights" / "best.pt"
    best_pt_dest = Path("best.pt")
    shutil.copy2(best_pt_source, best_pt_dest)
    print(f"\nbest.pt copié vers : {best_pt_dest.resolve()}")
    print("Lance maintenant : python export.py")


if __name__ == "__main__":
    main()