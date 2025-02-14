import cv2
import csv
from cvzone.HandTrackingModule import HandDetector
import cvzone
import time

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)
detector = HandDetector(detectionCon=0.8)

class MCQ():
    def __init__(self, data):
        self.question = data[0]
        self.choice1 = data[1]
        self.choice2 = data[2]
        self.choice3 = data[3]
        self.choice4 = data[4]
        self.answer = int(data[5])

        self.user_answer = None
    
    def update(self, cursor, bounding_boxes):
        for x, bounding_box in enumerate(bounding_boxes):
            x1, y1, x2, y2 = bounding_box
            if x1 < cursor[0] < x2 and y1 < cursor[1] < y2:
                self.user_answer = x + 1
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), cv2.FILLED)


path_csv = "./mcqs.csv"
with open(path_csv, newline="\n") as f:
    reader = csv.reader(f)
    all_data = list(reader)[1:]


# create object for each MCQ
mcq_list = []
for question in all_data:
    mcq_list.append(MCQ(question))

question_number = 0
total_questions = len(all_data)

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img, flipType=False)

    if question_number < total_questions:
        mcq = mcq_list[question_number]

        img, bounding_box = cvzone.putTextRect(img, mcq.question, [100, 100], 2, 2, offset=50, border=5)
        img, bounding_box1 = cvzone.putTextRect(img, mcq.choice1, [100, 250], 2, 2, offset=50, border=5)
        img, bounding_box2 = cvzone.putTextRect(img, mcq.choice2, [400, 250], 2, 2, offset=50, border=5)
        img, bounding_box3 = cvzone.putTextRect(img, mcq.choice3, [100, 400], 2, 2, offset=50, border=5)
        img, bounding_box4 = cvzone.putTextRect(img, mcq.choice4, [400, 400], 2, 2, offset=50, border=5)


        if hands:
            landmark_list = hands[0]['lmList']
            cursor = landmark_list[8]
            length, info = detector.findDistance(landmark_list[8], landmark_list[12])

            if length < 50:
                mcq.update(cursor, [bounding_box1, bounding_box2, bounding_box3, bounding_box4])
                print(mcq.user_answer)
                if mcq.user_answer is not None:
                    time.sleep(1)
                    question_number += 1
    else:
        score = 0
        for mcq in mcq_list:
            if mcq.answer == mcq.user_answer:
                score += 1
        score = round((score / total_questions) * 100, 2)
        img, _ = cvzone.putTextRect(img, "Quiz Completed", [250, 300], 2, 2, offset=50, border=5)
        img, _ = cvzone.putTextRect(img, f"Your Score: {score}%", [700, 300], 2, 2, offset=50, border=5)
        print(score)
    
    # draw progress bar
    bar_value = 150 + (950 // total_questions) * question_number
    cv2.rectangle(img, (150, 600), (bar_value, 625), (176, 250, 2), cv2.FILLED)
    img, _ = cvzone.putTextRect(img, f"{round((question_number / total_questions) * 100)}%", [1130, 635], 2, 2, offset=16)

    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break