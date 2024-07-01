import cv2
import mediapipe as mp
import numpy as np
from PIL import ImageFont, ImageDraw, Image
import mysql.connector
from datetime import datetime
import sys
import math

user_account = sys.argv[1]
exercise_type = sys.argv[2]

# 初始化攝像頭和MediaPipe Pose
cam = cv2.VideoCapture(0)
mppose = mp.solutions.pose
mp_hands = mp.solutions.hands
mpdraw = mp.solutions.drawing_utils
poses = mppose.Pose()
hands = mp_hands.Hands(model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5)

def calc_angles(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - \
              np.arctan2(a[1] - b[1], a[0] - b[0])

    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180:
        angle = 360 - angle

    return angle

def put_text_chinese(image, text, position, font_size, color):
    pil_img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    font = ImageFont.truetype("simsun.ttc", font_size, encoding="utf-8")
    draw.text(position, text, font=font, fill=color)
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

def vector_2d_angle(v1, v2):
    v1_x = v1[0]
    v1_y = v1[1]
    v2_x = v2[0]
    v2_y = v2[1]
    try:
        angle_ = math.degrees(math.acos((v1_x * v2_x + v1_y * v2_y) / (((v1_x ** 2 + v1_y ** 2) ** 0.5) * ((v2_x ** 2 + v2_y ** 2) ** 0.5))))
    except:
        angle_ = 180
    return angle_

def hand_angle(hand_):
    angle_list = []
    # thumb 大拇指角度
    angle_ = vector_2d_angle(
        ((int(hand_[0][0]) - int(hand_[2][0])), (int(hand_[0][1]) - int(hand_[2][1]))),
        ((int(hand_[3][0]) - int(hand_[4][0])), (int(hand_[3][1]) - int(hand_[4][1])))
    )
    angle_list.append(angle_)
    # index 食指角度
    angle_ = vector_2d_angle(
        ((int(hand_[0][0]) - int(hand_[6][0])), (int(hand_[0][1]) - int(hand_[6][1]))),
        ((int(hand_[7][0]) - int(hand_[8][0])), (int(hand_[7][1]) - int(hand_[8][1])))
    )
    angle_list.append(angle_)
    # middle 中指角度
    angle_ = vector_2d_angle(
        ((int(hand_[0][0]) - int(hand_[10][0])), (int(hand_[0][1]) - int(hand_[10][1]))),
        ((int(hand_[11][0]) - int(hand_[12][0])), (int(hand_[11][1]) - int(hand_[12][1])))
    )
    angle_list.append(angle_)
    # ring 無名指角度
    angle_ = vector_2d_angle(
        ((int(hand_[0][0]) - int(hand_[14][0])), (int(hand_[0][1]) - int(hand_[14][1]))),
        ((int(hand_[15][0]) - int(hand_[16][0])), (int(hand_[15][1]) - int(hand_[16][1])))
    )
    angle_list.append(angle_)
    # pink 小拇指角度
    angle_ = vector_2d_angle(
        ((int(hand_[0][0]) - int(hand_[18][0])), (int(hand_[0][1]) - int(hand_[18][1]))),
        ((int(hand_[19][0]) - int(hand_[20][0])), (int(hand_[19][1]) - int(hand_[20][1])))
    )
    angle_list.append(angle_)
    return angle_list

def hand_pos(finger_angle):
    f1 = finger_angle[0]
    f2 = finger_angle[1]
    f3 = finger_angle[2]
    f4 = finger_angle[3]
    f5 = finger_angle[4]

    if f1 >= 50 and f2 < 50 and f3 >= 50 and f4 >= 50 and f5 >= 50:
        return '1'
    elif f1 >= 50 and f2 < 50 and f3 < 50 and f4 >= 50 and f5 >= 50:
        return '2'
    else:
        return ''

def main():
    stage = "up"
    feedback = ""
    score = 0
    frame_count = 0
    smooth_window_size = 10
    hip_knee_angles = []
    shoulder_hip_knee_angles = []
    hip_positions_y = []
    knee_positions_y = []
    heel_positions_y = []
    foot_positions_y = []
    wrist_positions = []
    scores = []
    user_wants_to_continue = True

    # 设置窗口名称和大小
    cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('frame', 1280, 720)


    while user_wants_to_continue:
        ret, frame = cam.read()
        if not ret:
            print("讀取錯誤")
            break
        frame = cv2.flip(frame, 1)
        rgbframe = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        poseoutput = poses.process(rgbframe)
        handsoutput = hands.process(rgbframe)
        preview = frame.copy()

        if poseoutput.pose_landmarks:
            mpdraw.draw_landmarks(preview, poseoutput.pose_landmarks, mppose.POSE_CONNECTIONS)
            landmarks = poseoutput.pose_landmarks.landmark

            # 計算膝蓋角度（大腿和小腿之間的角度）
            hip_knee_angle = calc_angles(
                [landmarks[mppose.PoseLandmark.LEFT_HIP].x, landmarks[mppose.PoseLandmark.LEFT_HIP].y],
                [landmarks[mppose.PoseLandmark.LEFT_KNEE].x, landmarks[mppose.PoseLandmark.LEFT_KNEE].y],
                [landmarks[mppose.PoseLandmark.LEFT_ANKLE].x, landmarks[mppose.PoseLandmark.LEFT_ANKLE].y])

            # 計算臀部角度（上半身和大腿之間的角度）
            shoulder_hip_knee_angle = calc_angles(
                [landmarks[mppose.PoseLandmark.LEFT_SHOULDER].x, landmarks[mppose.PoseLandmark.LEFT_SHOULDER].y],
                [landmarks[mppose.PoseLandmark.LEFT_HIP].x, landmarks[mppose.PoseLandmark.LEFT_HIP].y],
                [landmarks[mppose.PoseLandmark.LEFT_KNEE].x, landmarks[mppose.PoseLandmark.LEFT_KNEE].y])

            # 計算臀部和膝蓋位置
            hip_position_y = landmarks[mppose.PoseLandmark.LEFT_HIP].y
            knee_position_y = landmarks[mppose.PoseLandmark.LEFT_KNEE].y

            # 計算腳跟位置
            heel_position_y = landmarks[mppose.PoseLandmark.LEFT_HEEL].y
            # 計算腳尖位置
            foot_position_y = landmarks[mppose.PoseLandmark.LEFT_FOOT_INDEX].y

            # 計算左手腕和右手腕的位置
            left_wrist = [landmarks[mppose.PoseLandmark.LEFT_WRIST].x, landmarks[mppose.PoseLandmark.LEFT_WRIST].y]
            right_wrist = [landmarks[mppose.PoseLandmark.RIGHT_WRIST].x, landmarks[mppose.PoseLandmark.RIGHT_WRIST].y]
            wrist_positions.append((left_wrist, right_wrist))

            hip_knee_angles.append(hip_knee_angle)
            shoulder_hip_knee_angles.append(shoulder_hip_knee_angle)
            hip_positions_y.append(hip_position_y)
            knee_positions_y.append(knee_position_y)
            heel_positions_y.append(heel_position_y)
            foot_positions_y.append(foot_position_y)

            if len(hip_knee_angles) > smooth_window_size:
                hip_knee_angles.pop(0)
                shoulder_hip_knee_angles.pop(0)
                hip_positions_y.pop(0)
                knee_positions_y.pop(0)
                heel_positions_y.pop(0)
                foot_positions_y.pop(0)
                wrist_positions.pop(0)

            avg_hip_knee_angle = np.mean(hip_knee_angles)
            avg_shoulder_hip_knee_angle = np.mean(shoulder_hip_knee_angles)
            avg_hip_position_y = np.mean(hip_positions_y)
            avg_knee_position_y = np.mean(knee_positions_y)
            avg_heel_position_y = np.mean(heel_positions_y)
            avg_foot_position_y = np.mean(foot_positions_y)
            avg_left_wrist = np.mean([pos[0] for pos in wrist_positions], axis=0)
            avg_right_wrist = np.mean([pos[1] for pos in wrist_positions], axis=0)

            frame_count += 1
            if frame_count >= smooth_window_size:
                if stage == "up" and avg_hip_knee_angle < 160:
                    wrist_y_diff = abs(avg_left_wrist[1] - avg_right_wrist[1])
                    if wrist_y_diff < 0.05 and avg_left_wrist[1] < landmarks[mppose.PoseLandmark.LEFT_SHOULDER].y and avg_right_wrist[1] < landmarks[mppose.PoseLandmark.RIGHT_SHOULDER].y:
                        #臀低於等於膝蓋
                        if avg_hip_position_y >= avg_knee_position_y :
                            if 80 < avg_shoulder_hip_knee_angle < 100 : #身體垂直
                                if abs(avg_shoulder_hip_knee_angle - avg_hip_knee_angle) < 10: #軀幹與脛骨平行
                                    if avg_heel_position_y < avg_foot_position_y: #腳跟抬起
                                        score = 2
                                        stage = "down"
                                        feedback = "腳跟離地，但動作標準"
                                    else:                           #腳跟沒抬起
                                        score = 3
                                        stage = "down"
                                        feedback = "標準深蹲"
                                else:                                                          #軀幹與脛骨不平行
                                    if avg_heel_position_y < avg_foot_position_y: #腳跟抬起
                                        score = 1
                                        stage = "down"
                                        feedback = "臀低於等於膝蓋且身體垂直，但軀幹與脛骨不平行、腳跟抬起"
                                    else :                          #腳跟沒抬起
                                        score = 1
                                        stage = "down"
                                        feedback = "臀低於等於膝蓋且身體垂直、腳跟沒抬起，但軀幹與脛骨不平行"
                            else:                                       #身體不垂直
                                if abs(avg_shoulder_hip_knee_angle - avg_hip_knee_angle) < 10: #軀幹與脛骨平行
                                    if avg_heel_position_y < avg_foot_position_y: #腳跟抬起
                                        score = 1
                                        stage = "down"
                                        feedback = "臀低於等於膝蓋且軀幹與脛骨平行，但身體不垂直、腳跟抬起"
                                    else:                           #腳跟沒抬起
                                        score = 1
                                        stage = "down"
                                        feedback = "臀低於等於膝蓋且軀幹與脛骨平行、腳跟沒抬起，但身體不垂直"
                                else:                                                          #軀幹與脛骨不平行
                                    if avg_heel_position_y < avg_foot_position_y: #腳跟抬起
                                        score = 1
                                        stage = "down"
                                        feedback = "臀低於等於膝蓋，但軀幹與脛骨不平行、腳跟抬起、身體不垂直"
                                    else :                          #腳跟沒抬起
                                        score = 1
                                        stage = "down"
                                        feedback = "臀低於等於膝蓋且腳跟沒抬起，但軀幹與脛骨不平行、身體不垂直"

                        #臀高於膝
                        elif avg_hip_position_y < avg_knee_position_y: 
                            score = 1
                            if 80 < avg_shoulder_hip_knee_angle < 100 :  #身體垂直
                                if abs(avg_shoulder_hip_knee_angle - avg_hip_knee_angle) < 10: #軀幹與脛骨平行
                                    if avg_heel_position_y < avg_foot_position_y:   #腳跟抬起
                                        feedback = "身體垂直且軀幹與脛骨平行，但腳跟抬起、臀高於膝"
                                        stage = "down"
                                    else:                            #腳跟沒抬起
                                        feedback = "身體垂直且軀幹與脛骨平行、腳跟沒抬起，但臀高於膝"
                                        stage = "down"
                                else:                                                          #軀幹與脛骨不平行
                                    if avg_heel_position_y < avg_foot_position_y:  #腳跟抬起
                                        feedback = "身體垂直，但軀幹與脛骨不平行、腳跟抬起且臀高於膝"
                                        stage = "down"
                                    else:                            #腳跟沒抬起
                                        feedback = "腳跟沒抬起且身體垂直，但是軀幹與脛骨不平行、臀高於膝"
                                        stage = "down"
                            else:                                       #身體不垂直
                                if abs(avg_shoulder_hip_knee_angle - avg_hip_knee_angle) < 10: #軀幹與脛骨平行
                                    if avg_heel_position_y < avg_foot_position_y: #腳跟抬起
                                        feedback = "軀幹與脛骨平行，但身體不垂直、腳跟抬起且臀高於膝"
                                        stage = "down"
                                    else:                           #腳跟沒抬起
                                        feedback = "軀幹與脛骨平行且腳跟沒抬起，但身體不垂直且臀高於膝"
                                        stage = "down"
                                else:                                                          #軀幹與脛骨不平行
                                    if avg_heel_position_y < avg_foot_position_y: #腳跟抬起
                                        feedback = "都不符合標準"
                                        stage = "down"
                                    else :                          #腳跟沒抬起
                                        feedback = "腳跟沒抬起，但軀幹與脛骨不平行、身體不垂直且臀高於膝"
                                        stage = "down"
                    

        # 在視窗中顯示分數和反饋
        if stage == "down":
            preview = put_text_chinese(preview, f"分數: {score} 分", (10, 40), 20, (0, 255, 0))
            preview = put_text_chinese(preview, f"反饋: {feedback}", (10, 80), 20, (0, 255, 0))
            scores.append(score)  # 添加分數到列表
            
            if handsoutput.multi_hand_landmarks:
                for hand_landmarks in handsoutput.multi_hand_landmarks:
                    finger_points = []
                    for i in hand_landmarks.landmark:
                        x = i.x * preview.shape[1]
                        y = i.y * preview.shape[0]
                        finger_points.append((x, y))
                    if finger_points:
                        finger_angle = hand_angle(finger_points)
                        gesture = hand_pos(finger_angle)
                        cv2.putText(preview, gesture, (30, 120), cv2.FONT_HERSHEY_SIMPLEX, 5, (255, 255, 255), 10, cv2.LINE_AA)
                        if gesture == '1':
                            user_wants_to_continue = True
                            stage = "up"
                        elif gesture == '2':
                            user_wants_to_continue = False

                        preview = put_text_chinese(preview, "是否繼續？是（1）否（2）", (10, 120), 20, (0, 255, 0))
                        cv2.imshow('frame', preview)
                        cv2.waitKey(200)

                        if not user_wants_to_continue:
                            break
            

        cv2.imshow('frame', preview)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

    
    # 將分數、賬戶、訓練類型和時間存入資料表
    connection = mysql.connector.connect(
        host='127.0.0.1', port=3306, user='root', password='', database='vfc')
    cursor = connection.cursor()
    insert_query = "INSERT INTO exercise_scores (user_account, exercise_type, score, exercise_time,feedback) VALUES (%s, %s, %s, %s,%s)"
    if scores:  # 確保 scores 列表不為空
        last_score = scores[-1]
        exercise_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(insert_query, (user_account, exercise_type, last_score, exercise_time,feedback))
    connection.commit()
    cursor.close()
    connection.close()

if __name__ == '__main__':
    main()

