"""Appendix：自然言語処理。"""

from course_content.builder import code, markdown


TITLE = "Appendix：手元で動かす自然言語処理"
SUMMARY = "日本語の短文を数値へ変換し、肯定的・否定的な文を分類します。"

CELLS = [
    markdown("## 文章を数値へ変える\n\nモデルは文字列を直接扱えません。TF-IDFで、文字の並びが各文にどれくらい特徴的かを数値にします。"),
    code(
        """
        import numpy as np
        import pandas as pd
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import accuracy_score
        from sklearn.model_selection import train_test_split
        from sklearn.pipeline import make_pipeline

        positive = [
            "結果が分かりやすくて助かった", "操作が簡単で使いやすい", "予測が当たり満足した",
            "説明が丁寧で理解できた", "処理が速くて快適だった", "グラフが見やすく便利だ",
            "期待した結果が得られた", "エラーをすぐ直せて良かった", "手順どおりに動いた",
            "試していて楽しかった", "分析の続きが楽しみだ", "この方法をまた使いたい",
            "比較が簡単にできた", "出力の意味がよく分かった", "少ないコードで予測できた",
        ]
        negative = [
            "結果が分かりにくく困った", "操作が複雑で使いにくい", "予測が外れて不満だ",
            "説明が難しく理解できない", "処理が遅くて待たされた", "グラフが見づらく不便だ",
            "期待した結果が得られない", "エラーの原因が分からなかった", "手順どおりに動かない",
            "試していて疲れた", "分析を続けたくない", "この方法はもう使いたくない",
            "比較に手間がかかった", "出力の意味が分からない", "コードが長くて混乱した",
        ]
        texts = positive + negative
        labels = np.array([1] * len(positive) + [0] * len(negative))
        """
    ),
    markdown("## 学習用と検証用に分ける\n\n日本語の単語分割ツールを使わず、2〜4文字の並びを特徴にします。"),
    code(
        """
        X_train, X_valid, y_train, y_valid = train_test_split(
            texts, labels, test_size=0.3, random_state=42, stratify=labels
        )
        model = make_pipeline(
            TfidfVectorizer(analyzer="char", ngram_range=(2, 4)),
            LogisticRegression(max_iter=1000),
        )
        model.fit(X_train, y_train)
        prediction = model.predict(X_valid)
        print("accuracy:", round(accuracy_score(y_valid, prediction), 3))
        pd.DataFrame({"文章": X_valid, "正解": y_valid, "予測": prediction})
        """
    ),
    markdown("## 新しい文章を分類する"),
    code(
        """
        new_texts = [
            "初めてでも簡単に動かせて楽しい",
            "説明が複雑で何をすればよいか分からない",
            "結果は出たが少し時間がかかった",
        ]
        probabilities = model.predict_proba(new_texts)[:, 1]
        pd.DataFrame({"文章": new_texts, "肯定的な確率": probabilities}).round(3)
        """
    ),
    markdown("## モデルが見ている文字列\n\n肯定的と判断する方向へ強く働いた文字の並びを表示します。"),
    code(
        """
        vectorizer = model.named_steps["tfidfvectorizer"]
        classifier = model.named_steps["logisticregression"]
        names = vectorizer.get_feature_names_out()
        top_indices = np.argsort(classifier.coef_[0])[-12:][::-1]
        pd.DataFrame({"文字の並び": names[top_indices], "係数": classifier.coef_[0, top_indices]}).round(3)
        """
    ),
    markdown("## 試してみる\n\n`new_texts`へ自分の文を追加してください。学習例が少ないため、もっともらしく外す場合がある点も確認します。"),
]
