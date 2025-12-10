import json
import os
import shutil
import sys
from pathlib import Path

import numpy as np

import torch
from datasets import load_from_disk
from transformers import (
    AutoImageProcessor,
    AutoModelForImageClassification,
    TrainingArguments,
    Trainer,
    DefaultDataCollator,
    set_seed,
)
import evaluate
import wandb

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gcs_utils import get_gcs_fs, gcs_uri


def main():
    set_seed(42)
    print("Running train/train.py")

    # -------------------------
    # 1) Load processed data from shared volume
    # -------------------------
    fs = get_gcs_fs()
    train_uri = gcs_uri("train")
    eval_uri = gcs_uri("eval")
    metadata_uri = gcs_uri("metadata.json")

    cache_root = Path(os.getenv("LOCAL_DATA_CACHE", "/tmp/nutrisnap-data"))
    cache_root.mkdir(parents=True, exist_ok=True)

    def _sync_split(remote_uri: str, split_name: str):
        local_path = cache_root / split_name
        if local_path.exists():
            shutil.rmtree(local_path)
        print(f"Syncing {remote_uri} -> {local_path}")
        fs.get(remote_uri, str(local_path), recursive=True)
        return load_from_disk(str(local_path))

    print(f"Loading processed datasets from {gcs_uri()} ...")
    train_ds = _sync_split(train_uri, "train")
    eval_ds = _sync_split(eval_uri, "eval")

    # Load metadata
    with fs.open(metadata_uri, "r") as f:
        metadata = json.load(f)
    
    id2label = {int(k): v for k, v in metadata["id2label"].items()}
    label2id = {k: int(v) for k, v in metadata["label2id"].items()}
    model_ckpt = metadata["model_ckpt"]
    FAST_DEV_RUN = metadata["fast_dev_run"]
    
    print(f"Loaded {metadata['train_samples']} train and {metadata['eval_samples']} eval samples")

    # Load processor and set dataset format for Trainer
    processor = AutoImageProcessor.from_pretrained(model_ckpt)

    columns = ["pixel_values", "labels"]
    train_ds.set_format(type="torch", columns=columns)
    eval_ds.set_format(type="torch", columns=columns)

    # -------------------------
    # 2) Model
    # -------------------------
    print("Loading model...")
    model = AutoModelForImageClassification.from_pretrained(
        model_ckpt,
        num_labels=len(id2label),
        id2label=id2label,
        label2id=label2id,
    )

    # -------------------------
    # 3) Metrics
    # -------------------------
    acc = evaluate.load("accuracy")
    acc5 = evaluate.load("accuracy")

    def compute_metrics(p):
        # p.predictions can be (loss, logits) or logits
        logits = p.predictions[0] if isinstance(p.predictions, (tuple, list)) else p.predictions
        y_true = p.label_ids

        # top-1
        y_pred = np.argmax(logits, axis=1)
        top1 = float((y_pred == y_true).mean())

        # top-5: check if the true label is among the top-5 logits
        # (argsort descending then take first 5)
        top5_idx = np.argsort(-logits, axis=1)[:, :5]
        top5 = float(np.any(top5_idx == y_true[:, None], axis=1).mean())

        return {"top1": top1, "top5": top5}

    # -------------------------
    # 4) TrainingArguments
    # -------------------------
    # Auto device: CUDA if available; otherwise use MPS on Apple; else CPU
    use_cuda = torch.cuda.is_available()
    use_mps = (not use_cuda) and torch.backends.mps.is_available()

    # Light defaults for quick run; bump for full training
    args = TrainingArguments(
        output_dir="./output/food101-vit",
        per_device_train_batch_size=4,
        per_device_eval_batch_size=8,
        gradient_accumulation_steps=1,
        learning_rate=5e-5,
        num_train_epochs=1 if FAST_DEV_RUN else 3,
        weight_decay=0.0,
        logging_steps=10,
        remove_unused_columns=False,
        fp16=use_cuda,              # mixed precision on CUDA
        no_cuda=not use_cuda,       # False if CUDA, True otherwise
        dataloader_num_workers=0,   # adjust as needed
    )

    # Data collator handles stacking of already processed pixel_values/labels
    data_collator = DefaultDataCollator()

    # -------------------------
    # 5) W&B (minimal setup)
    # -------------------------
    wandb.init(
        project="NutriSnap",
        name="vit-base-ft" + ("-fast" if FAST_DEV_RUN else "-full"),
        mode=os.getenv("WANDB_MODE", "online"),
        config={
            "fast_dev_run": FAST_DEV_RUN,
            "train_samples": len(train_ds),
            "eval_samples": len(eval_ds),
            "model_ckpt": model_ckpt,
        },
    )

    # -------------------------
    # 6) Train
    # -------------------------
    print("Starting training...")
    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_ds,
        eval_dataset=eval_ds,
        tokenizer=processor,          # so it's saved with the trainer
        data_collator=data_collator,
        compute_metrics=compute_metrics,
    )

    trainer.train()

    # -------------------------
    # 7) Final eval + save
    # -------------------------
    print("Final evaluation...")
    metrics = trainer.evaluate()
    wandb.log(metrics)

    save_dir = "./food101-vit-model"
    model.save_pretrained(save_dir)
    processor.save_pretrained(save_dir)

    artifact = wandb.Artifact(
        name="food101-vit-model",
        type="model",
        description="ViT fine-tuned on Food101",
        metadata={"model_ckpt": model_ckpt, "num_labels": len(id2label)},
    )
    artifact.add_dir(save_dir)
    wandb.log_artifact(artifact)
    wandb.run.summary.update(metrics)
    wandb.finish()
    
    print("Training complete!")


if __name__ == "__main__":
    main()