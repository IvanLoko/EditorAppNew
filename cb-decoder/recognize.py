import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
import math
import argparse

modelDetector = "./frozen_east_text_detection.pb"
modelRecognition = "./crnn.onnx"

############ Utility functions ############

def fourPointsTransform(frame, vertices):
    vertices = np.asarray(vertices)
    outputSize = (100, 32)
    targetVertices = np.array([
        [0, outputSize[1] - 1],
        [0, 0],
        [outputSize[0] - 1, 0],
        [outputSize[0] - 1, outputSize[1] - 1]], dtype="float32")

    rotationMatrix = cv.getPerspectiveTransform(vertices, targetVertices)
    result = cv.warpPerspective(frame, rotationMatrix, outputSize)
    return result

# correct solution:
def softmax(x):
    """Compute softmax values for each sets of scores in x."""
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum(axis=0) # only difference

def decodeText(scores):
    text = ""
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyz"
    # first = False

    for i in range(scores.shape[0]):
        #c = np.argmax(scores[i][0])
        
        sm = softmax(scores[i][0])
        s = np.argmax(sm)
        c = s

        # if s != 0 and sm[s] < 0.8:
        #     s1, sm1 = s, sm[s]
        #     sm[s1] = 0

        #     s2 = np.argmax(sm)
        #     if first:
        #         if s1 <= 10:
        #             c = s1
        #         else:
        #             c = s2
        #     else:
        #         if s1 > 10:
        #             c = s1
        #         else:
        #             c = s2

        # first = True

        if c != 0:
            text += alphabet[c - 1]
        else:
            text += '-'

    # adjacent same letters as well as background text must be removed to get the final output
    char_list = []
    for i in range(len(text)):
        if text[i] != '-' and (not (i > 0 and text[i] == text[i - 1])):
            char_list.append(text[i])
    return ''.join(char_list)


def decodeBoundingBoxes(scores, geometry, scoreThresh):
    detections = []
    confidences = []

    ############ CHECK DIMENSIONS AND SHAPES OF geometry AND scores ############
    assert len(scores.shape) == 4, "Incorrect dimensions of scores"
    assert len(geometry.shape) == 4, "Incorrect dimensions of geometry"
    assert scores.shape[0] == 1, "Invalid dimensions of scores"
    assert geometry.shape[0] == 1, "Invalid dimensions of geometry"
    assert scores.shape[1] == 1, "Invalid dimensions of scores"
    assert geometry.shape[1] == 5, "Invalid dimensions of geometry"
    assert scores.shape[2] == geometry.shape[2], "Invalid dimensions of scores and geometry"
    assert scores.shape[3] == geometry.shape[3], "Invalid dimensions of scores and geometry"
    height = scores.shape[2]
    width = scores.shape[3]
    for y in range(0, height):

        # Extract data from scores
        scoresData = scores[0][0][y]
        x0_data = geometry[0][0][y]
        x1_data = geometry[0][1][y]
        x2_data = geometry[0][2][y]
        x3_data = geometry[0][3][y]
        anglesData = geometry[0][4][y]
        for x in range(0, width):
            score = scoresData[x]

            # If score is lower than threshold score, move to next x
            if (score < scoreThresh):
                continue

            # Calculate offset
            offsetX = x * 4.0
            offsetY = y * 4.0
            angle = anglesData[x]

            # Calculate cos and sin of angle
            cosA = math.cos(angle)
            sinA = math.sin(angle)
            h = x0_data[x] + x2_data[x]
            w = x1_data[x] + x3_data[x]

            # Calculate offset
            offset = ([offsetX + cosA * x1_data[x] + sinA * x2_data[x], offsetY - sinA * x1_data[x] + cosA * x2_data[x]])

            # Find points for rectangle
            p1 = (-sinA * h + offset[0], -cosA * h + offset[1])
            p3 = (-cosA * w + offset[0], sinA * w + offset[1])
            center = (0.5 * (p1[0] + p3[0]), 0.5 * (p1[1] + p3[1]))
            detections.append((center, (w, h), -1 * angle * 180.0 / math.pi))
            confidences.append(float(score))

    # Return detections and confidences
    return [detections, confidences]

# Load network
detector = cv.dnn.readNet(modelDetector)
recognizer = cv.dnn.readNet(modelRecognition)

def recognize(frame, cropped_out=None, \
    confThreshold=0.5, nmsThreshold=0.4, \
    inpWidth=320, inpHeight=320, \
    marginX = 10, marginY = 10):

    outNames = []
    outNames.append("feature_fusion/Conv_7/Sigmoid")
    outNames.append("feature_fusion/concat_3")

    # The EAST text requires that your input image dimensions be multiples of 32, 
    # so if you choose to adjust your --width and --height values, make sure they are multiples of 32!
    
    # Get frame height and width
    height_ = frame.shape[0]
    width_ = frame.shape[1]

    rW = width_ / float(inpWidth)
    rH = height_ / float(inpHeight)

    # Create a 4D blob from frame.
    blob = cv.dnn.blobFromImage(frame, 1.0, (inpWidth, inpHeight), (123.68, 116.78, 103.94), True, False)

    # Run the detection model
    detector.setInput(blob)

    outs = detector.forward(outNames)

    # Get scores and geometry
    scores = outs[0]
    geometry = outs[1]
    [boxes, confidences] = decodeBoundingBoxes(scores, geometry, confThreshold)

    # Apply NMS
    wordsRecognized = []

    indices = cv.dnn.NMSBoxesRotated(boxes, confidences, confThreshold, nmsThreshold)
    for i in indices:
        # get 4 corners of the rotated rect
        vertices = cv.boxPoints(boxes[i])
        # scale the bounding box coordinates based on the respective ratios
        for j in range(4):
            vertices[j][0] *= rW
            vertices[j][1] *= rH

        # get cropped image using perspective transform
        cropped = fourPointsTransform(frame, vertices)
        cropped = cv.cvtColor(cropped, cv.COLOR_BGR2GRAY)

        if cropped_out is not None:
            cropped_out.append(cropped)

        # Create a 4D blob from cropped image
        blob = cv.dnn.blobFromImage(cropped, size=(100, 32), mean=127.5, scalefactor=1 / 127.5)
        recognizer.setInput(blob)

        # Run the recognition model
        result = recognizer.forward()

        # decode the result into text
        wordRecognized = decodeText(result)

        wordInfo = {
            "word": wordRecognized, 
            "p": [
                (int(vertices[1][0]), int(vertices[1][1])),
                (int(vertices[2][0]), int(vertices[2][1])),
                (int(vertices[3][0]), int(vertices[3][1])),
                (int(vertices[0][0]), int(vertices[0][1]))
            ]
        }

        p = wordInfo["p"]
        maxP = (max(map(lambda x: x[0], p)) + marginX, max(map(lambda x: x[1], p)) + marginY)
        minP = (min(map(lambda x: x[0], p)), min(map(lambda x: x[1], p)))

        wordInfo["rect"] = (minP, maxP)

        wordsRecognized.append(wordInfo)

        # cv.putText(frame, wordRecognized, (int(vertices[1][0]), int(vertices[1][1])), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0))

        # for j in range(4):
        #     p1 = (int(vertices[j][0]), int(vertices[j][1]))
        #     p2 = (int(vertices[(j + 1) % 4][0]), int(vertices[(j + 1) % 4][1]))
        #     cv.line(frame, p1, p2, (0, 255, 0), 1)

    return wordsRecognized


if __name__ == "__main__":
    file = "demo-1"
    # img = cv.imread(f"./cb/{file}.jpg")
    img = cv.imread("./elems/13-1.png")

    wordsRecognized = recognize(img)
    info = wordsRecognized[0]

    print(info)
    cv.putText(img, info["word"], info["p"][0], cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0))
    # for j in range(4):
    #     p1 = info["p"][j]
    #     p2 = info["p"][(j + 1) % 4]
    #     cv.line(img, p1, p2, (0, 255, 0), 1)

    p1, p2 = info["rect"]
    cv.rectangle(img,p1,p2,(0,255,0),2)

    plt.imshow(img)
    plt.show()