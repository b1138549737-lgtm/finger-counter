# Finger Counter

> Real-time finger counting using webcam + MediaPipe HandLandmarker.

Detect how many fingers a person is holding up via webcam, powered by MediaPipe's 21-point hand landmark model. Works in real time with OpenCV display.

**English · [中文文档](#项目简介)**

---

## Features

- Real-time webcam capture with mirror display
- 21-point hand skeleton overlay
- Accurate finger counting (0–5) for one hand
- Auto-downloads the ML model on first run
- Press `q` to exit

## Requirements

- Python >= 3.9
- A webcam

Dependencies (`requirements.txt`):

```
opencv-python>=4.8.0
mediapipe>=0.10.0
```

## Quick Start

```bash
pip install -r requirements.txt
python main.py
```

The first run automatically downloads a 7.5MB model file.

## How It Works

### Hand Landmarks

MediaPipe HandLandmarker provides 21 keypoint coordinates per hand:

```
 0: Wrist
 4: Thumb tip
 8: Index finger tip
12: Middle finger tip
16: Ring finger tip
20: Pinky tip
```

### Finger Counting Logic

| Finger | Rule |
|--------|------|
| Thumb | Compare tip(4) and IP(3) **x coordinates** — thumb moves sideways; direction depends on left/right hand |
| Index | tip(8).y < PIP(6).y |
| Middle | tip(12).y < PIP(10).y |
| Ring | tip(16).y < PIP(14).y |
| Pinky | tip(20).y < PIP(18).y |

> In image coordinates, y-axis points downward, so **tip.y < PIP.y** means the fingertip is higher (extended).

### Tech Stack

- **OpenCV** — camera capture and image display
- **MediaPipe HandLandmarker** — hand keypoint detection (new `mp.tasks.vision` API)
- **MediaPipe hand_landmarker.task** — pretrained model (auto-downloaded)

### Directory Structure

```
finger-counter/
├── main.py              # Main program
├── requirements.txt     # Python dependencies
├── models/              # Model file (auto-downloaded, gitignored)
│   └── hand_landmarker.task
├── .gitignore
└── README.md
```

---

<br>

---

# 项目简介

调用电脑摄像头实时检测画面中的人手，通过 MediaPipe 的 21 个手部关键点定位每根手指的位置，精确判断伸出了几根手指，并在画面中实时显示。

## 效果预览

运行后弹出摄像头窗口，画面会镜像翻转（镜子效果）：
- 手部绘制绿色关键点和骨架连线
- 手腕上方实时显示 `Fingers: N`
- 按 `q` 键退出

## 环境要求

- Python >= 3.9
- 摄像头

依赖项（`requirements.txt`）：
```
opencv-python>=4.8.0
mediapipe>=0.10.0
```

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 运行（首次会自动下载 7.5MB 的模型文件）
python main.py
```

## 技术原理

### 手部关键点检测

MediaPipe HandLandmarker 提供 21 个关键点坐标：

```
 0: 手腕
 4: 拇指指尖
 8: 食指指尖
12: 中指指尖
16: 无名指指尖
20: 小指指尖
```

### 手指伸直判定规则

| 手指 | 判定方式 |
|------|----------|
| 拇指 | 根据左右手，比较指尖(4)与指根(3)的 **x 坐标**（拇指横向运动） |
| 食指 | 指尖(8).y < 指根(6).y |
| 中指 | 指尖(12).y < 指根(10).y |
| 无名指 | 指尖(16).y < 指根(14).y |
| 小指 | 指尖(20).y < 指根(18).y |

> 图像坐标系中 y 轴向下，因此 **指尖 y < 指根 y** 表示指尖位置更高（伸直状态）。

### 技术栈

- **OpenCV** — 摄像头捕获与图像显示
- **MediaPipe HandLandmarker** — 手部关键点检测（新版 `mp.tasks.vision` API）
- **MediaPipe hand_landmarker.task** — 预训练模型（首次运行自动下载）

## 目录结构

```
finger-counter/
├── main.py              # 主程序
├── requirements.txt     # Python 依赖
├── models/              # 模型文件（自动下载，已 gitignore）
│   └── hand_landmarker.task
├── .gitignore
└── README.md
```

## License

MIT
