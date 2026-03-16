#computer vision
import torch
import torchvision.transforms as T
from torchvision.models import resnet18, ResNet18_Weights
from PIL import Image
import numpy as np

# Device
device = "cuda" if torch.cuda.is_available() else "cpu"

# Load model (NO WARNINGS)
weights = ResNet18_Weights.DEFAULT
model = resnet18(weights=weights)
model.fc = torch.nn.Identity()
model.eval().to(device)

# Transform
transform = T.Compose([
    T.Resize((224,224)),
    T.ToTensor(),
    T.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


def extract_visual_stress(image_path):
    img = Image.open(image_path).convert("RGB")
    x = transform(img).unsqueeze(0).to(device)

    with torch.no_grad():
        features = model(x).squeeze().cpu().numpy()

    # L2 norm → visual intensity
    raw_score = np.linalg.norm(features)

    # Normalize to 0–1 range
    visual_stress = min(raw_score / 1500, 1.0)

    return visual_stress
