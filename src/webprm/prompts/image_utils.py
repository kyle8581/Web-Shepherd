import base64
import io
from PIL import Image


def image_to_base64_url(image: str | Image.Image):
    if isinstance(image, str):
        with open(image, "rb") as f:
            image = f.read()
    elif isinstance(image, Image.Image):
        if image.mode in ("RGBA", "LA"):
            image = image.convert("RGB")
        with io.BytesIO() as buffer:
            image.save(buffer, format="PNG")
            image = buffer.getvalue()
    else:
        raise ValueError(f"Invalid image type: {type(image)}")
    
    return "data:image/png;base64," + base64.b64encode(image).decode("utf-8")