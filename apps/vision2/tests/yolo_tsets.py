from pathlib import Path

from ultralytics import YOLO

OUTPUT_DIR = Path(__file__).parent / "output"


def main() -> None:
    model = YOLO("yolov8n.pt")
    results = model.predict(
        source="https://ultralytics.com/images/bus.jpg",
        save=True,
        project=str(OUTPUT_DIR),
        name="hello_world",
        exist_ok=True,
    )

    for result in results:
        print(f"감지된 객체 수: {len(result.boxes)}")
        for box in result.boxes:
            class_name = result.names[int(box.cls)]
            confidence = float(box.conf)
            print(f"- {class_name}: {confidence:.2%}")


if __name__ == "__main__":
    main()
