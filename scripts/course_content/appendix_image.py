"""Appendix：画像認識。"""

from course_content.builder import code, markdown


TITLE = "Appendix：手元で動かす画像認識"
SUMMARY = "scikit-learn付属の手書き数字画像を分類します。データのダウンロードは不要です。"

CELLS = [
    markdown("## 画像も数値の集まり\n\n8×8画素の明るさを64個の数値としてモデルへ渡し、0〜9の数字を予測します。"),
    code(
        """
        import matplotlib.pyplot as plt
        from sklearn.datasets import load_digits
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import ConfusionMatrixDisplay, accuracy_score
        from sklearn.model_selection import train_test_split
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler

        digits = load_digits()
        print("画像配列:", digits.images.shape)
        print("モデルへ渡す表:", digits.data.shape)
        """
    ),
    markdown("## 画像を見る"),
    code(
        """
        fig, axes = plt.subplots(2, 5, figsize=(8, 4))
        for index, axis in enumerate(axes.ravel()):
            axis.imshow(digits.images[index], cmap="gray_r")
            axis.set_title(f"正解: {digits.target[index]}")
            axis.axis("off")
        plt.tight_layout()
        """
    ),
    markdown("## 学習用と検証用に分ける\n\n画像を平らな64列の表として扱います。"),
    code(
        """
        X_train, X_valid, y_train, y_valid = train_test_split(
            digits.data, digits.target, test_size=0.25, random_state=42, stratify=digits.target
        )
        model = make_pipeline(
            StandardScaler(),
            LogisticRegression(max_iter=2000),
        )
        model.fit(X_train, y_train)
        prediction = model.predict(X_valid)
        print("accuracy:", round(accuracy_score(y_valid, prediction), 3))
        """
    ),
    markdown("## 間違え方を見る\n\n混同行列で、どの数字同士を間違えたか確認します。"),
    code(
        """
        ConfusionMatrixDisplay.from_predictions(y_valid, prediction, cmap="Blues")
        plt.title("手書き数字の混同行列")
        """
    ),
    markdown("## 1枚を予測する"),
    code(
        """
        sample_index = 12
        sample = X_valid[sample_index].reshape(8, 8)
        predicted_number = model.predict(X_valid[[sample_index]])[0]
        probabilities = model.predict_proba(X_valid[[sample_index]])[0]

        plt.imshow(sample, cmap="gray_r")
        plt.title(f"予測={predicted_number}, 確率={probabilities.max():.1%}, 正解={y_valid[sample_index]}")
        plt.axis("off")
        """
    ),
    markdown("## 試してみる\n\n`sample_index`を変更し、確率が低い画像や間違えた画像を探してください。"),
]
