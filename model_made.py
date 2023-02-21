import torch
import torchvision
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor


def create_model(num_classes):
    # load Faster RCNN pre-trained model
    model = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=True)

    # get the number of input features
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    # define a new head for the detector with required number of classes
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)
    return model

def create_model_2(weights, classes):
    device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
    # load the model and the trained weights
    model2 = create_model(num_classes=classes).to(device)
    model2.load_state_dict(torch.load(
        weights, map_location=device
    ))
    return model2