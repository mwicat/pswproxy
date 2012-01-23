import Image

def resize(im, ratio):
    w, h = im.size
    w, h = w * ratio, h * ratio
    w = int(round(w))
    h = int(round(h))
    im = im.resize((w, h), Image.ANTIALIAS)
    return im
