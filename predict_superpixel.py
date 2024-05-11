import os
import uuid
import cv2
import torch
from models import shufflenetv2
from models import nasnet_mobile_onfire

##

from inference_superpixel import data_transform,process_sp

##

def predict_fire_sp(image_path,model_name):
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    
    if model_name == "shufflenetonfire":
        model = shufflenetv2.shufflenet_v2_x0_5(
            pretrained=False, layers=[
                4, 8, 4], output_channels=[
                24, 48, 96, 192, 64], num_classes=1)
        w_path = './weights/shufflenet_sp.pt'
        model.load_state_dict(torch.load(w_path, map_location=device))
    elif model_name == "nasnetonfire":
        model = nasnet_mobile_onfire.nasnetamobile(num_classes=1, pretrained=False)
        w_path = './weights/nasnet_sp.pt'
        model.load_state_dict(torch.load(w_path, map_location=device))
    
    np_transforms = data_transform(model_name)
    
    model.eval()
    model.to(device)
    
    frame = cv2.imread(image_path)
    
    height, width, _ = frame.shape
    small_frame = cv2.resize(frame, (224, 224), cv2.INTER_AREA)
    
    prediction = process_sp(0, small_frame, np_transforms, model)        
    small_frame = cv2.resize(small_frame, (width, height), cv2.INTER_AREA)

    unique_filename = 'output_'+str(uuid.uuid4()) + '.png'
    cv2.imwrite(f'./static/uploads/{unique_filename}', small_frame)
    
    
    return prediction.item()