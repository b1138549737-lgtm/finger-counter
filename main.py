"""
手指识别 - 调用摄像头实时识别伸出的手指数量
使用 OpenCV + MediaPipe HandLandmarker (新版 API)
"""

import os
import time
import urllib.request

import cv2
import mediapipe as mp

# ── 模型文件 ──────────────────────────────────────────────
MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
)
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "hand_landmarker.task")


def _ensure_model():
    """若模型文件不存在则自动下载。"""
    if os.path.exists(MODEL_PATH):
        return
    os.makedirs(MODEL_DIR, exist_ok=True)
    print(f"正在下载模型 hand_landmarker.task ...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    print("模型下载完成。")


def count_fingers(hand_landmarks, handedness_label):
    """
    根据 21 个关键点判断伸出了几根手指。

    规则:
      - 拇指 (索引 4):  右手时指尖 x > 指根 x 为伸直, 左手反之
      - 其余四指 (8/12/16/20):  指尖 y < 指根 y (图像中位置更高) 为伸直
    """
    lm = hand_landmarks
    cnt = 0

    # 拇指
    if handedness_label == "Right":
        if lm[4].x > lm[3].x:
            cnt += 1
    else:
        if lm[4].x < lm[3].x:
            cnt += 1

    # 食指・中指・无名指・小指
    for tip, pip in ((8, 6), (12, 10), (16, 14), (20, 18)):
        if lm[tip].y < lm[pip].y:
            cnt += 1

    return cnt


def main():
    _ensure_model()

    # ── MediaPipe HandLandmarker 初始化 ──────────────────
    VisionRunningMode = mp.tasks.vision.RunningMode
    HandLandmarker = mp.tasks.vision.HandLandmarker
    HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
    BaseOptions = mp.tasks.BaseOptions

    options = HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=VisionRunningMode.VIDEO,
        num_hands=1,
        min_hand_detection_confidence=0.7,
        min_tracking_confidence=0.5,
    )
    detector = HandLandmarker.create_from_options(options)

    # ── 打开摄像头 ──────────────────────────────────────
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("错误: 无法打开摄像头")
        detector.close()
        return

    print("按 'q' 键退出程序")

    start_time = time.perf_counter_ns()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("错误: 无法读取摄像头画面")
            break

        # 镜像翻转（镜子效果）
        frame = cv2.flip(frame, 1)

        # 构建 MediaPipe Image（OpenCV BGR → RGB）
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        # 推断（VIDEO 模式要求递增的时间戳，单位 ms）
        timestamp_ms = (time.perf_counter_ns() - start_time) // 1_000_000
        result = detector.detect_for_video(mp_image, timestamp_ms)

        # 顶部提示文字
        cv2.putText(
            frame,
            "Press 'q' to quit",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (200, 200, 200),
            1,
        )

        h, w, _ = frame.shape

        # ── 处理检测结果 ──────────────────────────────
        if result.hand_landmarks and result.handedness:
            for hand_lms, hand_cats in zip(result.hand_landmarks, result.handedness):
                # 画骨架
                mp.tasks.vision.drawing_utils.draw_landmarks(
                    frame,
                    hand_lms,
                    mp.tasks.vision.HandLandmarksConnections.HAND_CONNECTIONS,
                    mp.tasks.vision.drawing_styles.get_default_hand_landmarks_style(),
                    mp.tasks.vision.drawing_styles.get_default_hand_connections_style(),
                )

                # 手指计数
                label = hand_cats[0].category_name  # "Left" / "Right"
                fingers = count_fingers(hand_lms, label)

                # 手腕坐标（用作文字锚点）
                cx = int(hand_lms[0].x * w)
                cy = int(hand_lms[0].y * h)

                cv2.putText(
                    frame,
                    f"Fingers: {fingers}",
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
    detector.close()


if __name__ == "__main__":
    main()
