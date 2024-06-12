import cv2
from configparser import ConfigParser

action_params_config_data = 'src/configs/img_action.conf'
action_params_config = ConfigParser()
action_params_config.read(action_params_config_data)

scale_percent = int(action_params_config['img_action_parameters']['scale_percent'])
thresh = int(action_params_config['img_action_parameters']['thresh'])
bright = int(action_params_config['img_action_parameters']['bright'])
a = int(action_params_config['img_action_parameters']['a'])
b = int(action_params_config['img_action_parameters']['b'])


def resize_img(input_img):
    width = int(input_img.shape[1] * scale_percent / 100)
    height = int(input_img.shape[0] * scale_percent / 100)
    dimension = (width, height)
    resize_image = cv2.resize(input_img, dimension, interpolation=cv2.INTER_AREA)
    return resize_image


def img_to_gray(input_img):
    input_img = cv2.cvtColor(input_img, cv2.COLOR_BGR2GRAY)
    se = cv2.getStructuringElement(cv2.MORPH_RECT, (a, b))
    bg = cv2.morphologyEx(input_img, cv2.MORPH_DILATE, se)
    out_gray = cv2.divide(input_img, bg, scale=255)
    return out_gray


def img_to_binary(input_img):
    gray = img_to_gray(input_img=input_img)
    out_binary = cv2.threshold(gray, thresh, bright, cv2.THRESH_OTSU)[1]
    return out_binary