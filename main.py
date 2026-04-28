"""
手指识别 - 调用摄像头实时识别伸出的手指数量
使用 OpenCV + MediaPipe Hands
"""

import cv2
import mediapipe as mp


def count_fingers(hand_landmarks, handedness):
    """
    根据手部关键点判断伸出了几根手指。

    手指判定规则:
      - 拇指 (landmark 4): 对于右手, 指尖x > 指根x 为伸直;
                           对于左手, 指尖x < 指根x 为伸直
      - 其余四指 (landmark 8/12/16/20): 指尖y < 指根y (图像中位置更高) 为伸直
    """
    lm = hand_landmarks.landmark
    finger_count = 0

    # 拇指: 根据左右手判断
    hand_label = handedness.classification[0].label  # "Left" 或 "Right"
    if hand_label == "Right":
        if lm[4].x > lm[3].x:
            finger_count += 1
    else:
        if lm[4].x < lm[3].x:
            finger_count += 1

    # 食指 (8-6), 中指 (12-10), 无名指 (16-14), 小指 (20-18)
    for tip, pip in [(8, 6), (12, 10), (16, 14), (20, 18)]:
        if lm[tip].y < lm[pip].y:
            finger_count += 1

    return finger_count


def main():
    # MediaPipe 初始化
    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils
    mp_draw_styles = mp.solutions.drawing_styles
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5,
    )

    # 打开摄像头
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("错误: 无法打开摄像头")
        return

    print("按 'q' 键退出程序")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("错误: 无法读取摄像头画面")
            break

        # 镜像翻转（让画面像镜子一样自然）
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        # 显示提示文字
        cv2.putText(
            frame,
            "Press 'q' to quit",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (200, 200, 200),
            1,
        )

        if result.multi_hand_landmarks and result.multi_handedness:
            for hand_landmarks, handedness in zip(
                result.multi_hand_landmarks, result.multi_handedness
            ):
                # 绘制手部骨架
                mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_draw_styles.get_default_hand_landmarks_style(),
                    mp_draw_styles.get_default_hand_connections_style(),
                )

                # 计算手指数量
                fingers = count_fingers(hand_landmarks, handedness)

                # 获取手腕位置作为文字锚点
                h, w, _ = frame.shape
                wrist = hand_landmarks.landmark[0]
                cx, cy = int(wrist.x * w), int(wrist.y * h)

                # 在手腕上方显示手指数量
                label = f"Fingers: {fingers}"
                cv2.putText(
                    frame,
                    label,
                    (cx - 40, cy - 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (0, 255, 0),
                    2,
                )

        cv2.imshow("Finger Counter", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    hands.close()


if __name__ == "__main__":
    main()
