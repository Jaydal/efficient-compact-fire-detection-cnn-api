import cv2
import torch
from models import shufflenetv2
from models import nasnet_mobile_onfire

##

from inference_ff import data_transform,read_img, run_model_img

##

def predict_fire(image_path,model_name):
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    
    if model_name == "shufflenetonfire":
        model = shufflenetv2.shufflenet_v2_x0_5(
            pretrained=False, layers=[
                4, 8, 4], output_channels=[
                24, 48, 96, 192, 64], num_classes=1)
        w_path = './weights/shufflenet_ff.pt'
        model.load_state_dict(torch.load(w_path, map_location=device))
    elif model_name == "nasnetonfire":
        model = nasnet_mobile_onfire.nasnetamobile(num_classes=1, pretrained=False)
        w_path = './weights/nasnet_ff.pt'
        model.load_state_dict(torch.load(w_path, map_location=device))
    
    np_transforms = data_transform(model_name)
    
    model.eval()
    model.to(device)
    frame = cv2.imread(image_path)
    small_frame = read_img(frame, np_transforms)
    
    return run_model_img(0, small_frame, model).item()