import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import neighbors
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score

# ==========================================
# 1. ЗАВАНТАЖЕННЯ ВЛАСНОГО НАБОРУ ДАНИХ
# ==========================================
print("--- [1] Завантаження даних (train.csv) ---")
try:
    # Використовуємо dataset, зібраний у Завданні 1
    data = pd.read_csv('train.csv')
    data = data.dropna()
    print(f"Всього записів: {len(data)}")
except FileNotFoundError:
    print("Помилка: файл train.csv не знайдено.")
    exit()

# ==========================================
# 2. ПЕРЕДОБРОБКА (PREPROCESSING)
# ==========================================
print("\n--- [2] Кодування та Масштабування ---")

# Кодуємо текстові поля в числа
data['Registrar_code'] = data['Registrar'].astype('category').cat.codes
data['Country_code'] = data['Country'].astype('category').cat.codes
data['Protocol_code'] = data['Protocol'].astype('category').cat.codes
data['Class_code'] = data['Class'].astype('category').cat.codes

# Визначаємо, який код відповідає класу 'phishing'
class_labels = dict(enumerate(data['Class'].astype('category').cat.categories))
print(f"Мітки класів: {class_labels}")

# Формуємо набір ознак
feature_cols = ['Registrar_code', 'Lifetime', 'Country_code', 'Protocol_code']
if 'Has_SSL' in data.columns:
    feature_cols.append('Has_SSL')

X = data[feature_cols].values
y = data['Class_code'].values

# Масштабування (обов'язково для KNN)
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

# ==========================================
# 3. НАВЧАННЯ ТА БАЗОВА ОЦІНКА (Hold-out)
# ==========================================
print("\n--- [3] Базова оцінка (Train/Test Split) ---")
# Це потрібно для побудови матриці помилок (FP/FN)
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.3, random_state=42, stratify=y
)

knn = neighbors.KNeighborsClassifier(n_neighbors=5)
knn.fit(X_train, y_train)
y_pred = knn.predict(X_test)

# Обчислення метрик помилок
tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()

print(f">> МАТРИЦЯ ПОМИЛОК (на 30% даних):")
print(f"True Positives (Вірно фішинг):  {tp}")
print(f"True Negatives (Вірно безпечні): {tn}")
print(f"False Positives (Помилка - Тривога): {fp}")
print(f"False Negatives (Помилка - Пропуск): {fn}")

# ==========================================
# 4. ПЕРЕХРЕСНА ПЕРЕВІРКА (Cross-Validation)
# ==========================================
print("\n--- [4] Перехресна перевірка (Cross-Validation) ---")
# Розбиваємо дані на 10 частин (folds)
k_folds = 10
cv = StratifiedKFold(n_splits=k_folds, shuffle=True, random_state=42)

# Оцінюємо точність (Accuracy) для кожного з 10 прогонів
scores = cross_val_score(knn, X_scaled, y, scoring='accuracy', cv=cv)

print(f"Результати {k_folds} перевірок: {scores}")
print(f"Середня точність (Mean Accuracy): {np.mean(scores):.4f}")
print(f"Стандартне відхилення (Std Dev): {np.std(scores):.4f}")

# ==========================================
# 5. ВІЗУАЛІЗАЦІЯ РЕЗУЛЬТАТІВ CV
# ==========================================
plt.figure(figsize=(8, 5))
plt.plot(range(1, k_folds + 1), scores, marker='o', linestyle='-', color='b')
plt.title(f'Результати Cross-Validation (k={k_folds})')
plt.xlabel('Номер ітерації (Fold)')
plt.ylabel('Точність (Accuracy)')
plt.ylim(0.5, 1.05)
plt.grid(True)
plt.axhline(y=np.mean(scores), color='r', linestyle='--', label=f'Середнє: {np.mean(scores):.2f}')
plt.legend()
plt.savefig('cv_results.png')
print("\nГрафік стабільності моделі збережено як 'cv_results.png'")
plt.show()