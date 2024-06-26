import cv2
import mediapipe as mp
import numpy as np
from PIL import ImageFont, ImageDraw, Image

cam = cv2.VideoCapture(0)
mppose = mp.solutions.pose
mpdraw = mp.solutions.drawing_utils
poses = mppose.Pose()

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

def main():
    stage = "start"
    feedback = ""
    score = 0
    frame_count = 0
    smooth_window_size = 10
    knee_angles = []
    hip_angles = []
    ankle_positions = []
    waist_positions = []

    while True:
        ret, frame = cam.read()
        if not ret:
            print("讀取錯誤")
            break
        frame = cv2.flip(frame, 1)
        rgbframe = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        poseoutput = poses.process(rgbframe)
        preview = frame.copy()

        if poseoutput.pose_landmarks:
            mpdraw.draw_landmarks(preview, poseoutput.pose_landmarks, mppose.POSE_CONNECTIONS)
            landmarks = poseoutput.pose_landmarks.landmark

            # 計算膝蓋角度（大腿和小腿之間的角度）
            knee_angle = calc_angles(
                [landmarks[mppose.PoseLandmark.LEFT_HIP].x, landmarks[mppose.PoseLandmark.LEFT_HIP].y],
                [landmarks[mppose.PoseLandmark.LEFT_KNEE].x, landmarks[mppose.PoseLandmark.LEFT_KNEE].y],
                [landmarks[mppose.PoseLandmark.LEFT_ANKLE].x, landmarks[mppose.PoseLandmark.LEFT_ANKLE].y])

            # 計算臀部角度（上半身和大腿之間的角度）
            hip_angle = calc_angles(
                [landmarks[mppose.PoseLandmark.LEFT_SHOULDER].x, landmarks[mppose.PoseLandmark.LEFT_SHOULDER].y],
                [landmarks[mppose.PoseLandmark.LEFT_HIP].x, landmarks[mppose.PoseLandmark.LEFT_HIP].y],
                [landmarks[mppose.PoseLandmark.LEFT_KNEE].x, landmarks[mppose.PoseLandmark.LEFT_KNEE].y])

            # 計算踝部位置
            ankle_position = landmarks[mppose.PoseLandmark.LEFT_ANKLE].y

            # 計算腰部位置
            waist_position = landmarks[mppose.PoseLandmark.LEFT_SHOULDER].x

            knee_angles.append(knee_angle)
            hip_angles.append(hip_angle)
            ankle_positions.append(ankle_position)
            waist_positions.append(waist_position)

            if len(knee_angles) > smooth_window_size:
                knee_angles.pop(0)
                hip_angles.pop(0)
                ankle_positions.pop(0)
                waist_positions.pop(0)

            avg_knee_angle = np.mean(knee_angles)
            avg_hip_angle = np.mean(hip_angles)
            avg_ankle_position = np.mean(ankle_positions)
            avg_waist_position = np.mean(waist_positions)

            preview = put_text_chinese(preview, f"跨欄", (10, 10), 30, (0, 255, 0))
            
            frame_count += 1
            if frame_count >= smooth_window_size:
                if stage == "start":
                    if avg_knee_angle < 90 and avg_hip_angle < 90:
                        stage = "cross"
                        score = 0
                        feedback = "動作開始"

                elif stage == "cross":
                    if avg_knee_angle > 160 and avg_hip_angle > 160:
                        if abs(avg_waist_position - avg_ankle_position) < 20:  # 髖、膝、踝保持一直線
                            score = 3
                            feedback = "髖、膝、踝保持一直線，腰椎無移動"
                        elif abs(avg_waist_position - avg_ankle_position) < 40:  # 髖、膝、踝未保持一直線，腰椎移動
                            score = 2
                            feedback = "髖、膝、踝未保持一直線，腰椎有移動"
                        else:  # 腳與欄架發生接觸或未能保持平衡
                            score = 1
                            feedback = "腳與欄架發生接觸或未能保持平衡"
                        stage = "end"

                elif stage == "end":
                    if avg_knee_angle < 90 and avg_hip_angle < 90:
                        stage = "start"
                        score = 0
                        feedback = ""

        # 在視窗中顯示分數和反饋
        if stage == "cross":
            preview = put_text_chinese(preview, f"分數: {score} 分", (10, 50), 30, (0, 255, 0))
            preview = put_text_chinese(preview, f"反饋: {feedback}", (10, 90), 30, (0, 255, 0))

        cv2.imshow('frame', preview)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
