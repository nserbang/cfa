import cv2 as cv
import numpy as np
import pytesseract as pt
from django.db.models import Q
from api.models import LostVehicle
from django.conf import settings
from api.log import *


# check or valid RC string
def has_numbers_and_characters(s):
    has_digit = False
    has_letter = False

    for char in s:
        if char.isdigit():
            has_digit = True
        elif char.isalpha():
            has_letter = True

        # Break the loop early if both conditions are met
        if has_digit and has_letter:
            break

    return has_digit and has_letter


# INPUT: Image or vehicle numbers
# OUTPUT: Vehicle number annotated input image, list of vehicle numbers detected in the image


def detectVehicleNumber(img=None, numbers=None, is_police=False):
    # cv.imshow(" Found :",img)
    ret_nums = []
    # cv.imshow("Grayscale Image", img)
    # cv.waitKey(0)
    if numbers is not None:
        log.debug(" Trying to detect vehicle number from passed value :", numbers)
        # TO DO: search num in lostVehicle. If found, return as it is
        # fetch numbers from the lostVehicle table and return it
        found = LostVehicle.objects.filter(
            Q(regNumber=numbers) | Q(chasisNumber=numbers) | Q(engineNumber=numbers)
        ).exists()
        if found:
            log.info(" Vehicle found ")
            vehicle = LostVehicle.objects.get(
                Q(regNumber=numbers) | Q(chasisNumber=numbers) | Q(engineNumber=numbers)
            )
            ret_nums.append({
                numbers: True, 
                'case_id':vehicle.caseId_id, 
                'chasis_number':vehicle.chasisNumber if is_police else '*******',
                'engineNumber':vehicle.engineNumber if is_police else '*******',
                'make':vehicle.make,
                'model':vehicle.model,
                'color':vehicle.color,
                'description': vehicle.description,
                })
        else:
            log.info(" Vehicle not found ")
            ret_nums.append({numbers: False})
    if img is not None:
        log.info(" Trying to detect vehicle number from image ")
        image_data_bytes = img.read()
        image_array = np.frombuffer(image_data_bytes, dtype=np.uint8)
        img = cv.imdecode(image_array, cv.IMREAD_COLOR)

        car = img
        cascade_file = str(settings.BASE_DIR / "api/haarcascade_number_plate.xml")

        cascade = cv.CascadeClassifier(cascade_file)
        grayCar = cv.cvtColor(car, cv.COLOR_RGB2BGR)

        npr = []
        nums = []
        numPlate = cascade.detectMultiScale(grayCar, 1.1, 4)
        for x, y, w, h in numPlate:
            cv.rectangle(
                car, (x, y), (x + w, y + h), (0, 0, 255), 5
            )  # Draw rectangle around the number plate in the original image
            npr.append(
                car[y + 20 : y + h - 10, x + 20 : x + w - 15]
            )  # strip the number plate
        # TO DO : Change tesseract_cmd for linux as required #
        pt.pytesseract.tesseract_cmd = r"/usr/bin/tesseract"
        custom_config = r"--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

        for n in npr:
            width = int(n.shape[1] * 150 / 100)
            height = int(n.shape[0] * 150 / 100)
            # print(" HELLO width :",width, "Height :",height, " Shape :",n.shape[0])
            dm = (width, height)
            # print(" NNNN : ",n)
            carTemp = cv.resize(
                n, dm, interpolation=cv.INTER_AREA
            )  # resize image for OCR

            grayLarged = cv.cvtColor(carTemp, cv.COLOR_RGB2GRAY)

            grayBlur = cv.medianBlur(grayLarged, 3)

            num = pt.image_to_string(grayBlur, config=custom_config)
            num = num.replace("\n", "").replace("\x0c", "")
            if has_numbers_and_characters(num) is True:
                rcn = LostVehicle.objects.filter(regNumber=num).exists()
                if rcn:
                    vehicle = LostVehicle.objects.get(
                        Q(regNumber=num) | Q(chasisNumber=num) | Q(engineNumber=num)
                    )
                    ret_nums.append({         
                        numbers: True, 
                        'case_id':vehicle.caseId_id, 
                        'chasis_number':vehicle.chasisNumber if is_police else '*******',
                        'engineNumber':vehicle.engineNumber if is_police else '*******',
                        'make':vehicle.make,
                        'model':vehicle.model,
                        'color':vehicle.color,
                        'description': vehicle.description,
                    })
                else:
                    ret_nums.append({rcn: False})
            # print (' NUMBER  in image : ',num)
            # nums.append(num) # get recognized numbers
    log.info(" Returning : ", ret_nums)
    return ret_nums


# cp = cv.VideoCapture(0)
def test():
    img = cv.imread("cars.jpg")
    img, nums = detectVehicleNumber(img, "1234")

    for i in nums:
        print(" Vehicle Number found ", i)

    cv.imshow(" Found :", img)

    cv.waitKey(0)

    cv.destroyAllWindows()


# test()
