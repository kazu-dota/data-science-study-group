"""Appendix：音声認識。"""

from course_content.builder import code, markdown


TITLE = "Appendix：手元で動かす音声認識"
SUMMARY = "合成した音の波形から周波数特徴を作り、低音・中音・高音を分類します。"

CELLS = [
    markdown("## 音は時間ごとの振幅\n\n今回は録音の代わりに、NumPyで周波数の異なる音を作ります。"),
    code(
        """
        import matplotlib.pyplot as plt
        import numpy as np
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.metrics import ConfusionMatrixDisplay, accuracy_score
        from sklearn.model_selection import train_test_split

        rng = np.random.default_rng(42)
        sample_rate = 8_000
        duration = 0.25
        time = np.arange(int(sample_rate * duration)) / sample_rate

        def make_tone(frequency, noise=0.15):
            phase = rng.uniform(0, 2 * np.pi)
            signal = np.sin(2 * np.pi * frequency * time + phase)
            return signal + rng.normal(0, noise, size=time.size)
        """
    ),
    markdown("## 波形と周波数を見る\n\nFFTは波形を、周波数ごとの強さへ変換します。"),
    code(
        """
        sample_wave = make_tone(440)
        spectrum = np.abs(np.fft.rfft(sample_wave))
        frequencies = np.fft.rfftfreq(sample_wave.size, d=1 / sample_rate)

        fig, axes = plt.subplots(1, 2, figsize=(10, 3))
        axes[0].plot(time[:400], sample_wave[:400])
        axes[0].set(title="波形", xlabel="秒", ylabel="振幅")
        axes[1].plot(frequencies, spectrum)
        axes[1].set(xlim=(0, 1_000), title="周波数成分", xlabel="Hz", ylabel="強さ")
        plt.tight_layout()
        """
    ),
    markdown("## 学習データを作る\n\n220Hzを低音、440Hzを中音、880Hzを高音として、少し周波数とノイズを変えた例を作ります。"),
    code(
        """
        examples = []
        labels = []
        classes = {"低音": 220, "中音": 440, "高音": 880}

        for label, base_frequency in classes.items():
            for _ in range(40):
                frequency = base_frequency + rng.normal(0, base_frequency * 0.04)
                wave = make_tone(frequency)
                fft_features = np.abs(np.fft.rfft(wave))[:300]
                examples.append(fft_features)
                labels.append(label)

        X = np.asarray(examples)
        y = np.asarray(labels)
        print("特徴量:", X.shape, "正解:", y.shape)
        """
    ),
    markdown("## 音の種類を分類する"),
    code(
        """
        X_train, X_valid, y_train, y_valid = train_test_split(
            X, y, test_size=0.25, random_state=42, stratify=y
        )
        model = RandomForestClassifier(n_estimators=200, random_state=42)
        model.fit(X_train, y_train)
        prediction = model.predict(X_valid)
        print("accuracy:", round(accuracy_score(y_valid, prediction), 3))
        ConfusionMatrixDisplay.from_predictions(y_valid, prediction, cmap="Blues")
        """
    ),
    markdown("## 新しい音を予測する\n\n周波数を変えて、予測される音の種類を確認します。"),
    code(
        """
        new_frequency = 500
        new_wave = make_tone(new_frequency)
        new_features = np.abs(np.fft.rfft(new_wave))[:300].reshape(1, -1)
        print(new_frequency, "Hzの予測:", model.predict(new_features)[0])
        print("確率:", dict(zip(model.classes_, model.predict_proba(new_features)[0].round(3), strict=True)))
        """
    ),
    markdown("## 試してみる\n\n`new_frequency`を300、600、750などへ変え、境界付近で確率がどう変わるか見てください。"),
]
