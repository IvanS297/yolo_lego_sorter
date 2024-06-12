from ultralytics import YOLO

MODEL = "src/models/for training/yolov8n.pt"
DATA_YAML = "src/configs/train_conf.yaml"
BATCH_SIZE = 2
IMG_SIZE = 640
EPOCHS = 100
WORKERS_NUM = 1

model = YOLO(MODEL)

model.train(data=DATA_YAML, batch=BATCH_SIZE, imgsz=IMG_SIZE, epochs=EPOCHS, workers=WORKERS_NUM)