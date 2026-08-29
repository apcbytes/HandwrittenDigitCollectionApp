# Session 5 (Optional) — Close the Loop: Train a Model on Your Own Data

**Goal:** Load the class's collected `data/labels.xlsx` + `data/images/`
dataset and train a simple classifier, showing learners their own
handwriting becoming training data for a real model.

**Duration:** ~60-90 min

**Prerequisite:** Sessions 1-4 complete, class has collected enough
samples (ideally combine everyone's `data/` folders into one shared
folder first — see note below).

---

## 0. Combine everyone's data (~10 min, instructor-led)

Since Session storage is local per-learner, gather everyone's
`data/images/*.png` into one shared folder and concatenate their
`labels.xlsx` files:

```python
import pandas as pd
import glob

all_logs = [pd.read_excel(f) for f in glob.glob("submissions/*/labels.xlsx")]
combined = pd.concat(all_logs, ignore_index=True)
combined.to_excel("combined_labels.xlsx", index=False)
print(f"Total samples: {len(combined)}")
print(combined["label"].value_counts().sort_index())
```

Discuss: is the class's data balanced across digits 0-9? (Probably
close, since the app enforces the guided sequence — a nice payoff from
the Session 4 design choice.)

## 1. Vibe-code first (~15 min)

Prompt:

> "Load a folder of 28x28 grayscale PNGs and a matching Excel file
> with filename/label columns, build a train/test split, and train a
> simple scikit-learn classifier to predict the digit."

## 2. Read & break it down (~10 min)

- Which classifier did it pick? (Likely `LogisticRegression`,
  `SVC`, or a small `MLPClassifier` — all reasonable for a tiny dataset.)
- How did it flatten the 28x28 images into feature vectors? (Should be
  `.reshape(-1, 784)` or similar — connect this back to Session 3's
  pipeline output shape.)
- Did it hold out a test set, or evaluate on training data? (Common
  vibe-coding gap — flag if missing.)

## 3. Hand-code the core concept (~25 min)

```python
import numpy as np
import pandas as pd
from PIL import Image
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix

df = pd.read_excel("combined_labels.xlsx")

X = []
y = []
for _, row in df.iterrows():
    img = Image.open(f"combined_images/{row['image_filename']}")
    X.append(np.array(img).flatten() / 255.0)   # normalize to 0-1
    y.append(row["label"])

X = np.array(X)
y = np.array(y)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

preds = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, preds))
print(confusion_matrix(y_test, preds))
```

**Discuss:**
- Why normalize pixel values to 0-1 (`/255.0`)? (Most ML models train
  better/faster on small, consistent-scale inputs.)
- Why `stratify=y` in the split? (With only ~10 samples per digit per
  learner, a random split could accidentally put all "7"s in the test
  set — stratify keeps class balance in both splits.)
- Look at the confusion matrix together — which digits does the model
  confuse most? (Often 4/9, 3/8, 1/7 — good discussion of why these
  are visually similar.)

## 4. Reconcile & test (~15 min)

- Report class accuracy — with a small, single-class dataset this will
  likely be modest (60-85%), which is itself the lesson: **small,
  narrow datasets don't generalize well** — real MNIST has 70,000
  samples from hundreds of different writers for a reason.
- Optional: have each learner test the model on a *freshly drawn*
  digit (not in the training set) via the HDCA app's preprocessing
  pipeline, and see if it predicts correctly.

## Closing discussion

- What would you need to do to make this model actually good?
  (More samples, more writers, more variation in style, possibly a
  CNN instead of logistic regression.)
- Tie back to the real MNIST dataset's scale and diversity as the
  reason it became a benchmark.

## Checkpoint

- [ ] Combined dataset loads correctly (images match labels)
- [ ] Train/test split and stratification is understood, not just copy-pasted
- [ ] Group can read a confusion matrix and identify commonly confused digit pairs
- [ ] At least one learner tests the model on a live, freshly-drawn digit
