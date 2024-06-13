import os
import threading
from logging import getLogger, basicConfig, DEBUG, INFO, FileHandler, StreamHandler

import cv2
from ultralytics import YOLO

import image_actions
import serial_control
import steppers

logger = getLogger()
FORMAT = '%(asctime)s : %(name)s : %(levelname)s : %(message)s'
file_handler = FileHandler('src/logs/data.log')
console = StreamHandler()
console.setLevel(INFO)
basicConfig(level=DEBUG, format=FORMAT, handlers=[file_handler])

MODEL_PATH = "src/model/lego_model.pt"
model = YOLO(model=MODEL_PATH)

PHOTO_COUNTER = 0
IMG_WIDTH = 400
IMG_HEIGHT = 460
DIV_NUM = 0
thread_list = []

capture = cv2.VideoCapture(0)

Stepper_mover = steppers.Move_Stepper()
Stepper_rotater = steppers.Rotate_Stepper(mover=Stepper_mover)
serial_control.init()


def main_loop():
    photo_counter = 0
    while True:
        success, img = capture.read()
        img = img[DIV_NUM:IMG_HEIGHT, DIV_NUM:IMG_WIDTH]
        img = image_actions.img_to_binary(input_img=img)
        resized_image = image_actions.resize_img(input_img=img)
        cv2.imshow("", resized_image)
        k = cv2.waitKey(1) & 0xFF
        if serial_control.detect_state:
            cv2.imwrite("img.png", resized_image)
            photo_counter += 1
            logger.info(f"Снимок №{photo_counter}")
            results = model("img.png")
            for result in results:
                class_ids = result.boxes.cls
                class_names = [model.names[int(cls_id)] for cls_id in class_ids]
                if len(class_names) != 1:
                    class_names = "(no_detections)"
                Stepper_rotater.rotate(data=str(class_names))
            os.remove("img.png")
        serial_control.detect_state = False
        if k == ord("q"):
            break


def start_threads(static_thread_list):
    for thread_name in static_thread_list:
        thread_name.start()


thread_serial = threading.Thread(target=serial_control.onRead)
main_thread = threading.Thread(target=main_loop)
thread_list.append(main_thread)
thread_list.append(thread_serial)

if __name__ == "__main__":
    logger.info("Start service")
    try:
        start_threads(static_thread_list=thread_list)
    except OSError:
        logger.critical("Can't Start Threads")
    else:
        logger.info("YOLO and cv2 start")
    finally:
        main_thread.join()
        thread_serial.join()
        logger.info("Stop service")
        capture.release()
        cv2.destroyAllWindows()
        serial_control.ClosePort()
