import cv2 as cv
import numpy as np
import pytesseract as pt

# INPUT: Image or vehicle numbers
# OUTPUT: Vehicle number annotated input image, list of vehicle numbers detected in the image

def detectVehicleNumber(img = None, numbers = None):  
    #cv.imshow(" Found :",img)

    #cv.waitKey(0)
    if numbers is not None:
        # TO DO: search num in lostVehicle. If found, return as it is
        # fetch numbers from the lostVehicle table and return it
        found = None
        return None, found
    if img is not None:
        car = img
        cascade = cv.CascadeClassifier('haarcascade_number_plate.xml')

        grayCar = cv.cvtColor(car,cv.COLOR_RGB2BGR)

        numPlate = cascade.detectMultiScale(grayCar,1.1,4)
        print( " Plate :",numPlate)
        npr = []
        nums = []
        for x,y,w,h in numPlate:
            cv.rectangle(car, (x,y), (x+w,y+h), (0,0,255), 5) # Draw rectangle around the number plate in the original image
            npr.append(car[y+20:y+h-10 ,x+20:x+w-15]) # strip the number plate
        # TO DO : Change tesseract_cmd for linux as required #
        pt.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
        custom_config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    
        for n in npr:
            width = int(n.shape[1]*150/100) 
            height = int(n.shape[0]*150/100)
            print(" HELLO width :",width, "Height :",height, " Shape :",n.shape[0])
            dm = (width,height) 
            #print(" NNNN : ",n)
            carTemp = cv.resize(n,dm,interpolation=cv.INTER_AREA) # resize image for OCR

            grayLarged = cv.cvtColor(carTemp,cv.COLOR_RGB2GRAY)

            grayBlur = cv.medianBlur(grayLarged,3)

            num = pt.image_to_string(grayBlur, config=custom_config)
            print (' NUMBER : ',num)
            nums.append(num) # get recognized numbers

        #dm = (size,size)
        #car = cv.resize(car,dm,interpolation=cv.INTER_AREA)
        ret_nums = []
        for num in nums:
            # for each num, check this value in LostVehicle table
            # TO DO: search num in lostVehicle. If found, return as it is 
            found = None # fill this with value returned from lostVehicle table
            if found is not None:
                ret_nums.append(found)
            return None,found  # image is null
        return car, ret_nums



#cp = cv.VideoCapture(0)
def test () :
    img =  cv.imread("cars.jpg")
    img, nums= detectVehicleNumber(img)

    for i in nums:
        print(" Vehicle Number found ",i)

    cv.imshow(" Found :",img)

    cv.waitKey(0)

    cv.destroyAllWindows()

#test()
