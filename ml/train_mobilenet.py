import argparse, json
from pathlib import Path
import tensorflow as tf

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data-dir", required=True)
    p.add_argument("--epochs", type=int, default=10)
    p.add_argument("--batch-size", type=int, default=32)
    args = p.parse_args()
    data = Path(args.data_dir)
    if not data.exists(): raise SystemExit(f"Dataset not found: {data}")
    train = tf.keras.utils.image_dataset_from_directory(
        data, validation_split=0.2, subset="training", seed=42,
        image_size=(224, 224), batch_size=args.batch_size)
    val = tf.keras.utils.image_dataset_from_directory(
        data, validation_split=0.2, subset="validation", seed=42,
        image_size=(224, 224), batch_size=args.batch_size)
    Path("models").mkdir(exist_ok=True)
    Path("models/class_names.json").write_text(json.dumps(train.class_names, ensure_ascii=False, indent=2), encoding="utf-8")
    autotune = tf.data.AUTOTUNE
    train = train.cache().shuffle(1000).prefetch(autotune)
    val = val.cache().prefetch(autotune)
    augment = tf.keras.Sequential([
        tf.keras.layers.RandomFlip("horizontal"),
        tf.keras.layers.RandomRotation(0.08),
        tf.keras.layers.RandomZoom(0.1)])
    base = tf.keras.applications.MobileNetV3Small(
        input_shape=(224, 224, 3), include_top=False, weights="imagenet",
        include_preprocessing=True)
    base.trainable = False
    inputs = tf.keras.Input((224, 224, 3))
    x = augment(inputs)
    x = base(x, training=False)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dropout(0.25)(x)
    outputs = tf.keras.layers.Dense(len(train.class_names), activation="softmax")(x)
    model = tf.keras.Model(inputs, outputs)
    model.compile(optimizer=tf.keras.optimizers.Adam(1e-3),
                  loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    model.fit(train, validation_data=val, epochs=args.epochs)
    model.save("models/disease_model.keras")
    print("Saved models/disease_model.keras")
    print("Classes:", train.class_names)
    print("Build a separate field-image test set before claiming real-world accuracy.")

if __name__ == "__main__": main()
