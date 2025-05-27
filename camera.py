import cv2
from PIL import Image
import re
import pyocr
import pyocr.builders
import time
import sys


def is_window_visible(winname):
    try:
        ret = cv2.getWindowProperty(winname, cv2.WND_PROP_VISIBLE)
        if ret == -1:
            raise False
        return bool(ret)
    except cv2.error:
        return False


def test_pyocr(e):
    pyocr.tesseract.TESSERACT_CMD = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
    tools = pyocr.get_available_tools()
    if len(tools) == 0:
        print("No OCR tool found")
        sys.exit(1)
    tool = tools[0]

    capture = cv2.VideoCapture(0)
    width = capture.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
    print(f"元の解像度: {width}x{height}")
    if height > width:
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, 720)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1280)
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, 720)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1280)
    else:
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    width = capture.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
    print(f"実際の解像度: {width}x{height}")

    if height > width:
        center_x, center_y = int(width // 2), int(height // 3)
        roi_size_x = int(width // 1.2)
        roi_size_y = roi_size_x // 4
    else:
        center_x, center_y = int(width // 2), int(height // 2)
        roi_size_x = int(width // 2)
        roi_size_y = roi_size_x // 4

    roi_default = (
        (center_x - roi_size_x // 2, center_y - roi_size_y // 2),
        (center_x + roi_size_x // 2, center_y + roi_size_y // 2),
    )
    roi_detect = roi_default
    detect_isbn = ""
    detect_count = 0
    missing_count = 0
    detect = False

    while True:
        ret, frame = capture.read()
        if not ret:
            break

        processed = frame[
            roi_detect[0][1] : roi_detect[1][1], roi_detect[0][0] : roi_detect[1][0]
        ]

        cv2.rectangle(frame, roi_detect[0], roi_detect[1], (0, 255, 0), 2)
        cv2.rectangle(frame, roi_default[0], roi_default[1], (255, 0, 0), 2)

        if detect:
            detect = False
            time.sleep(3)

        processed = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)

        txt = tool.image_to_string(
            Image.fromarray(processed),
            lang="jpn+eng",
            builder=pyocr.builders.WordBoxBuilder(tesseract_layout=6),
        )

        position = None
        for box in txt:
            m = re.search(r"([-\.0-9 ]{9,17})", box.content)
            if not m:
                continue
            t = m.group(1).translate(
                str.maketrans({"-": None, ".": None, "}": "1", "{": "1"})
            )
            if t[0:3] != "978":
                continue
            position = box.position
            cv2.rectangle(processed, position[0], position[1], (255, 0, 0), 1)

            print("text:", box.content)
            if len(t) != 13:
                continue
            if detect_isbn == t:
                detect_count += 1
            else:
                detect_isbn = t
                detect_count = 1
            print("isbn:", t, "count:", detect_count, "position:", position)
            if detect_count > 2:
                size, _ = cv2.getTextSize(detect_isbn, cv2.FONT_HERSHEY_SIMPLEX, 1, 4)
                scale = width / size[0]
                cv2.putText(
                    frame,
                    detect_isbn,
                    (roi_detect[0][0], roi_detect[0][1]),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    scale,
                    (0, 0, 0),
                    8,
                )
                cv2.putText(
                    frame,
                    detect_isbn,
                    (roi_detect[0][0], roi_detect[0][1]),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    scale,
                    (255, 255, 255),
                    2,
                )
                print("発見されたISBN:", detect_isbn)
                if e:
                    e(detect_isbn)
                roi_detect = roi_default
                missing_count = 0
                detect_count = 0
                detect_isbn = ""
                detect = True
                break

        if position:
            width = position[1][0] - position[0][0]
            height = position[1][1] - position[0][1]
            center_x = roi_detect[0][0] + position[0][0] + width // 2
            center_y = roi_detect[0][1] + position[0][1] + height // 2
            width = int(width * 1.5)
            height = int(height * 2)
            roi_detect = (
                (center_x - width // 2, center_y - height // 2),
                (center_x + width // 2, center_y + height // 2),
            )
        elif (missing_count := missing_count + 1) > 5:
            roi_detect = roi_default
            missing_count = 0

        cv2.imshow("Capture", frame)

        if cv2.waitKey(1) & 0xFF == ord("q") or not is_window_visible("Capture"):
            capture.release()
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    test_pyocr(None)
