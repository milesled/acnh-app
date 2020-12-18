import urllib
from PIL import Image as pil_Image

class Image:
    def __init__(self, obj, target_height):
        self.type = obj.type
        self.id = obj.id
        self.name = obj.name
        self.img_url = 'http://acnhapi.com/v1/images/{}/{}/'.format(self.type, self.id)
        # now I open the image using the link with the PIL Image class so I can find out the current
        # size and perform calculations for later access for size attributes in the <img> tag in HTML
        self.img = pil_Image.open(urllib.request.urlopen(self.img_url))
        # if the height is greater than the width, then rotate it 90 degrees
        if self.img.height > self.img.width:
            # reference for CSS styling
            self.isRotated = True
            # for calculation purposes, make sure to rotate the image
            self.img.save(self.img.rotate(90))
        else:
            self.isRotated = False
        # now resizing the image so it can fit in a grid
        # if the current height is not our target height, then we resize
        if self.img.size[1] != target_height:
            # we want all the heights to be the same
            self.height = target_height # just to stay in the same format as width
            ratio = target_height / self.img.size[1]
            # however, the width will be variable
            self.width = self.img.size[0] * ratio # !!! SAVE FOR FUTURE USE !!!
            self.img.save = (self.img.resize((int(self.width), int(self.height))))