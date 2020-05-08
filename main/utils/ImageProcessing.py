

import cv2

class ProcessImage:
    def process(self,image,clipLimit=25):
        new_image=image.copy()
        cv2.convertScaleAbs(image, new_image, clipLimit, 50)
        return new_image
        # lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        # l, a, b = cv2.split(lab)
        # clahe = cv2.createCLAHE(clipLimit=clipLimit, tileGridSize=(8, 8))
        # cl = clahe.apply(l)
        # limg = cv2.merge((cl, a, b))
        #
        # final = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        # return final
