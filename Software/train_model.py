"""
========================================================
 AIRPEN – CNN Training Script
========================================================
 Trains a CNN on EMNIST for handwriting recognition.
 Usage: python train_model.py
 Saves model to models/airpen_cnn.keras
========================================================
"""

import os
import numpy as np


def main():
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers

    print("=" * 60)
    print(" AIRPEN – CNN Model Training")
    print("=" * 60)

    IMG_SIZE = 28
    EPOCHS = 15
    BATCH_SIZE = 128
    MODEL_DIR = "models"
    MODEL_PATH = os.path.join(MODEL_DIR, "airpen_cnn.h5")
    os.makedirs(MODEL_DIR, exist_ok=True)

    # ── Load Dataset ──
    print("\n[1/5] Loading MNIST dataset (Digits 0-9)...")
    (x_train, y_train), (x_test, y_test) = keras.datasets.mnist.load_data()
    num_classes = 10

    print(f"    Train: {len(x_train)}, Test: {len(x_test)}, Classes: {num_classes}")

    # ── Preprocess ──
    print("\n[2/5] Preprocessing...")
    x_train = np.array([img.T for img in x_train]).astype("float32") / 255.0
    x_test = np.array([img.T for img in x_test]).astype("float32") / 255.0
    x_train = x_train.reshape(-1, IMG_SIZE, IMG_SIZE, 1)
    x_test = x_test.reshape(-1, IMG_SIZE, IMG_SIZE, 1)

    # ── Build Model ──
    print("\n[3/5] Building CNN...")
    aug = keras.Sequential([
        layers.RandomRotation(factor=0.05),
        layers.RandomTranslation(height_factor=0.05, width_factor=0.05),
        layers.RandomZoom(height_factor=0.05),
    ])

    model = keras.Sequential([
        layers.Input(shape=(IMG_SIZE, IMG_SIZE, 1)),
        aug,
        layers.Conv2D(32, 3, activation="relu", padding="same"),
        layers.BatchNormalization(),
        layers.Conv2D(32, 3, activation="relu", padding="same"),
        layers.BatchNormalization(),
        layers.MaxPooling2D(2),
        layers.Dropout(0.25),
        layers.Conv2D(64, 3, activation="relu", padding="same"),
        layers.BatchNormalization(),
        layers.Conv2D(64, 3, activation="relu", padding="same"),
        layers.BatchNormalization(),
        layers.MaxPooling2D(2),
        layers.Dropout(0.25),
        layers.Flatten(),
        layers.Dense(256, activation="relu"),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(num_classes, activation="softmax"),
    ])

    model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    model.summary()

    # ── Train ──
    print(f"\n[4/5] Training ({EPOCHS} epochs)...")
    callbacks = [
        keras.callbacks.EarlyStopping(monitor="val_accuracy", patience=3, restore_best_weights=True),
        keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=2),
    ]
    model.fit(x_train, y_train, epochs=EPOCHS, batch_size=BATCH_SIZE,
              validation_data=(x_test, y_test), callbacks=callbacks, verbose=1)

    # ── Save ──
    print("\n[5/5] Saving...")
    loss, acc = model.evaluate(x_test, y_test, verbose=0)
    print(f"    Test Accuracy: {acc*100:.2f}%")
    model.save(MODEL_PATH)
    print(f"    Model saved to: {MODEL_PATH}")


if __name__ == "__main__":
    main()
