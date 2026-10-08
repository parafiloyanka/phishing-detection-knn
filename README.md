# Phishing Detection using KNN 🎣🤖

Проєкт з машинного навчання для виявлення фішингових веб-ресурсів. Утиліта аналізує параметри доменів та класифікує їх на безпечні (`benign`) або фішингові (`phishing`) за допомогою алгоритму **K-Nearest Neighbors (KNN)**.

## ⚙️ Етапи обробки даних (Pipeline)
1. **Feature Engineering:** Конвертація категоріальних текстових ознак (Registrar, Country, Protocol) у числові коди (`cat.codes`).
2. **Масштабування (MinMax Scaling):** Нормалізація значень для коректного розрахунку відстаней в алгоритмі KNN.
3. **Класифікація:** Навчання моделі з гіперпараметром $k=5$.
4. **Оцінка ефективності:** Формування Confusion Matrix (TP, TN, FP, FN) та розрахунок загальної точності (Accuracy).
5. **Візуалізація:** Генерація 2D-графіка (`result_plot.png`) розподілу класів за ознаками `Lifetime` та `Protocol`.

## 🚀 Встановлення та запуск (macOS / Linux)

Для роботи скрипта потрібні зовнішні бібліотеки для Data Science.

1. Клонуйте репозиторій:
   ```bash
   git clone [https://github.com/ВАШ_ЛОГІН/phishing-detection-knn.git](https://github.com/ВАШ_ЛОГІН/phishing-detection-knn.git)
   cd phishing-detection-knn
