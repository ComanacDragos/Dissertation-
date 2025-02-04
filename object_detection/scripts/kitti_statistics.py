import os
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

from backend.enums import Stage, DataType, LabelType
from backend.utils import to_json, open_json
from config.kitti_object_detection.data_generator_config import KittiDataGeneratorConfig


def generate_boxes(output, stage):
    output = output
    KittiDataGeneratorConfig.BATCH_SIZE = 1  # 7481
    ds = KittiDataGeneratorConfig.build(stage)
    all_data = {}
    for i in tqdm(range(len(ds)), total=len(ds)):
        data = ds[i]
        img_name = data[DataType.IDENTIFIER][0]
        classes = data[DataType.LABEL][0][LabelType.CLASS]
        if len(classes):
            classes = [ds.labels[cls] for cls in np.argmax(classes, axis=-1)]
        boxes = ds[i][DataType.LABEL][0][LabelType.COORDINATES]
        all_data[img_name] = {
            'classes': classes,
            'boxes': boxes
        }

    to_json(all_data, output)


def labels_stats():
    root = Path(r"C:\Users\Dragos\datasets\KITTI\labels")

    classes = []
    paths = list(os.listdir(root))
    for label_name in tqdm(paths, total=len(paths)):
        with open(root / str(label_name)) as f:
            for line in f.readlines():
                tokens = line.split()

                classes.append(tokens[0])

    classes_freq = Counter(classes)
    print("CLASSES:", classes_freq.keys())
    print("Frequency:", classes_freq)


def generate_images_stats():
    output = "scripts/image_stats.json"
    KittiDataGeneratorConfig.BATCH_SIZE = 1
    ds = KittiDataGeneratorConfig.build(Stage.ALL)
    stats = {}
    for i in tqdm(range(len(ds)), total=len(ds)):
        data = ds[i]
        identifier = data[DataType.IDENTIFIER][0]
        image = data[DataType.IMAGE][0]
        stats[identifier] = {
            "shape": np.shape(image),
            "mean": float(np.mean(image)),
            "std": float(np.std(image)),
            "min": float(np.min(image)),
            "max": float(np.max(image))
        }

    to_json(stats, output)


def process_stats():
    data = open_json("scripts/image_stats.json")

    shapes = [tuple(x['shape']) for _, x in data.items()]

    print(Counter(shapes))


def plot_dist(values, title, bins):
    plt.title(title)
    plt.hist(values, bins=bins)
    plt.axvline(x=np.min(values), linestyle='--', label="min: " + str(round(np.min(values), 2)))
    plt.axvline(x=np.max(values), linestyle='--', label="max: " + str(round(np.max(values), 2)))
    plt.legend()


def box_distribution(json_path):
    data = open_json(json_path)
    boxes = np.concatenate([x['boxes'] for x in data.values() if len(x['boxes']) > 0])
    x_min, y_min, x_max, y_max = boxes[:, 0], boxes[:, 1], boxes[:, 2], boxes[:, 3]
    center_x = (x_min + x_max) / 2
    center_y = (y_min + y_max) / 2

    bins = 100
    rows = 3
    cols = 2
    # plt.figure(figsize=(10, 10))
    plt.subplot(rows, cols, 1)
    plot_dist(x_min, "x_min", bins)

    plt.subplot(rows, cols, 2)
    plot_dist(x_max, "x_max", bins)

    plt.subplot(rows, cols, 3)
    plot_dist(y_min, "y_min", bins)

    plt.subplot(rows, cols, 4)
    plot_dist(y_max, "y_max", bins)

    plt.subplot(rows, cols, 5)
    plot_dist(center_x, "center_x", bins)

    plt.subplot(rows, cols, 6)
    plot_dist(center_y, "center_y", bins)

    plt.tight_layout()

    # plt.show()
    plt.savefig(json_path.split(".")[0] + ".png")
    plt.clf()
    plt.close()


def classes_stats(root):
    paths = root.glob("*.json")
    all_data = {}
    for json_path in paths:
        data = open_json(json_path)
        classes = np.concatenate([x['classes'] for x in data.values() if len(x['classes']) > 0])
        print(json_path)
        all_data[json_path.stem] = {
            "no_images": len(data),
            "class_freq": dict(Counter(classes))
        }
    to_json(all_data, root / "statistics.json")

if __name__ == '__main__':
    # generate_images_stats()

    box_distribution("outputs/kitti/stats/kitti_all_classes_train.json")
    box_distribution("outputs/kitti/stats/kitti_all_classes_val.json")
    box_distribution("outputs/kitti/stats/kitti_2_classes_train.json")
    box_distribution("outputs/kitti/stats/kitti_2_classes_val.json")

    # generate_boxes("outputs/kitti_all_classes_train.json", Stage.TRAIN)

    # classes_stats(Path("outputs/kitti/stats"))