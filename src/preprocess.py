import os
import tempfile
from PIL import Image

from datasets import load_dataset
from transformers import (
    AutoImageProcessor,
    set_seed,
)
from gcs_utils import get_gcs_fs, gcs_uri


def main():
    set_seed(42)
    print("Running preprocess.py")

    # -------------------------
    # 0) Fast dev run toggles
    # -------------------------
    FAST_DEV_RUN = os.getenv("FAST_DEV_RUN", "1").lower() in {"1", "true", "yes"}
    TRAIN_SAMPLES = int(os.getenv("TRAIN_SAMPLES", "200"))
    EVAL_SAMPLES = int(os.getenv("EVAL_SAMPLES", "200"))

    if FAST_DEV_RUN:
        print("Fast dev run enabled")
    else:
        print("Full run enabled")

    # -------------------------
    # 1) Data & preprocessing
    # -------------------------
    print("Loading Food101 dataset...")
    ds = load_dataset("ethz/food101")
    id2label = {i: c for i, c in enumerate(ds["train"].features["label"].names)}
    label2id = {c: i for i, c in id2label.items()}

    # Small subsample for quick local test, or use the full splits
    if FAST_DEV_RUN:
        train_ds = ds["train"].shuffle(seed=42).select(range(min(TRAIN_SAMPLES, len(ds["train"]))))
        eval_ds = ds["validation"].shuffle(seed=42).select(range(min(EVAL_SAMPLES, len(ds["validation"]))))
    else:
        train_ds = ds["train"]
        eval_ds = ds["validation"]

    model_ckpt = "google/vit-base-patch16-224-in21k"
    processor = AutoImageProcessor.from_pretrained(model_ckpt)

    def _materialize(dataset, desc):
        original_columns = dataset.column_names

        def _batch_transform(batch):
            images = []
            for img in batch["image"]:
                if hasattr(img, "convert"):
                    images.append(img.convert("RGB"))
                else:
                    images.append(Image.open(img).convert("RGB"))
            inputs = processor(images=images, return_tensors="np")
            inputs["labels"] = batch["label"]
            return inputs

        print(f"Applying transforms for {desc} split...")
        return dataset.map(
            _batch_transform,
            batched=True,
            batch_size=64,
            remove_columns=original_columns,
            desc=f"{desc}__materialize_transforms",
        )

    train_ds = _materialize(train_ds, "train")
    eval_ds = _materialize(eval_ds, "eval")

    # -------------------------
    # 2) Save processed datasets (with transforms applied)
    # -------------------------
    fs = get_gcs_fs()
    train_uri = gcs_uri("train")
    eval_uri = gcs_uri("eval")
    metadata_uri = gcs_uri("metadata.json")

    print(f"Saving processed datasets to {gcs_uri()} ...")
    for uri in (train_uri, eval_uri):
        if fs.exists(uri):
            print(f"Clearing existing dataset at {uri}")
            fs.rm(uri, recursive=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        local_train = os.path.join(tmpdir, "train")
        local_eval = os.path.join(tmpdir, "eval")

        print("Serializing transformed datasets locally before upload...")
        train_ds.save_to_disk(local_train)
        eval_ds.save_to_disk(local_eval)

        print(f"Uploading train split to {train_uri}")
        fs.put(local_train, train_uri, recursive=True)
        print(f"Uploading eval split to {eval_uri}")
        fs.put(local_eval, eval_uri, recursive=True)

    # Save metadata for training script
    metadata = {
        "id2label": id2label,
        "label2id": label2id,
        "model_ckpt": model_ckpt,
        "fast_dev_run": FAST_DEV_RUN,
        "train_samples": len(train_ds),
        "eval_samples": len(eval_ds)
    }

    import json
    with fs.open(metadata_uri, "w") as f:
        json.dump(metadata, f)

    print(
        "Preprocessing complete! "
        f"Saved {len(train_ds)} train and {len(eval_ds)} eval samples to {gcs_uri()}."
    )


if __name__ == "__main__":
    main()