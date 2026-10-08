import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn import neighbors
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

# ==========================================
# 1. ЗАВАНТАЖЕННЯ ДАНИХ
# ==========================================
print("--- [1] Завантаження наборів даних ---")
try:
    data_train = pd.read_csv('train.csv')
    data_test = pd.read_csv('test.csv')

    # Видаляємо пусті значення, якщо вони є
    data_train = data_train.dropna()
    data_test = data_test.dropna()

    # Запам'ятовуємо розмір тренувальної вибірки для подальшого розділення
    TRAIN_COUNT = len(data_train)
    print(f"Записів у train.csv: {TRAIN_COUNT}")
    print(f"Записів у test.csv: {len(data_test)}")

    # Об'єднуємо дані для коректного кодування (Encoding)
    data = pd.concat([data_train, data_test], ignore_index=True)

except FileNotFoundError:
    print("Помилка: Файли train.csv або test.csv не знайдені.")
    exit()

# ==========================================
# 2. ПЕРЕДОБРОБКА (Feature Engineering)
# ==========================================
print("\n--- [2] Кодування та Масштабування ---")

# Перетворення текстових полів у категорії, а потім у коди
# Це відповідає методиці з Лекції 8
data['Registrar'] = data['Registrar'].astype('category')
data['Country'] = data['Country'].astype('category')
data['Protocol'] = data['Protocol'].astype('category')
data['Class'] = data['Class'].astype('category')

data['Registrar_code'] = data['Registrar'].cat.codes
data['Country_code'] = data['Country'].cat.codes
data['Protocol_code'] = data['Protocol'].cat.codes
data['Class_code'] = data['Class'].cat.codes

# Вибір ознак для навчання (Features)
# Використовуємо 4 ознаки: Код реєстратора, Час життя, Код країни, Код протоколу
# (Якщо у вас є колонка Has_SSL, її також можна додати)
features_list = ['Registrar_code', 'Lifetime', 'Country_code', 'Protocol_code']
X_raw = data[features_list].values
y = data['Class_code'].values

# Масштабування (Scaling) - обов'язково для KNN
scaler = MinMaxScaler()
X = scaler.fit_transform(X_raw)

# Розділяємо назад на train та test
X_train = X[:TRAIN_COUNT]
y_train = y[:TRAIN_COUNT]

X_test = X[TRAIN_COUNT:]
y_test = y[TRAIN_COUNT:]

print("Дані успішно підготовлені.")

# ==========================================
# 3. НАВЧАННЯ МОДЕЛІ
# ==========================================
print("\n--- [3] Навчання моделі KNN ---")
k = 5
knn = neighbors.KNeighborsClassifier(n_neighbors=k)
knn.fit(X_train, y_train)
print(f"Модель навчена з k={k}")

# ==========================================
# 4. ОЦІНКА РЕЗУЛЬТАТІВ
# ==========================================
print("\n--- [4] Результати класифікації ---")

# Прогнозування
y_pred = knn.predict(X_test)

# Розрахунок метрик
accuracy = accuracy_score(y_test, y_pred)
conf_matrix = confusion_matrix(y_test, y_pred)
tn, fp, fn, tp = conf_matrix.ravel()

# Визначення назв класів (0 і 1)
class_labels = data['Class'].cat.categories
print(f"Класи: {dict(enumerate(class_labels))}")

print(f"\nТочність (Accuracy): {accuracy:.2%}")
print("-" * 30)
print(f"TP (True Positive - Фішинг вірно):  {tp}")
print(f"TN (True Negative - Безпечні вірно): {tn}")
print(f"FP (False Positive - Помилкова тривога): {fp}")
print(f"FN (False Negative - Пропущена загроза): {fn}")
print("-" * 30)

# Детальний звіт
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=class_labels))

# ==========================================
# 5. ВІЗУАЛІЗАЦІЯ
# ==========================================
print("\n--- [5] Побудова графіка ---")
plt.figure(figsize=(10, 6))

# Будуємо графік на основі ВІДОМИХ міток (y), щоб побачити реальний розподіл
# Використовуємо оригінальні (немасштабовані) дані для наочності Lifetime
lifetime_idx = 1  # Індекс колонки Lifetime у X_raw
protocol_idx = 3  # Індекс колонки Protocol_code у X_raw

# Розділяємо індекси класів
idx_phishing = np.where(y == 1)  # Припускаємо 1 = phishing
idx_benign = np.where(y == 0)  # Припускаємо 0 = benign

# Якщо коди навпаки, перевіряємо це
if class_labels[0] == 'phishing':
    idx_phishing = np.where(y == 0)
    idx_benign = np.where(y == 1)

plt.scatter(X_raw[idx_benign, lifetime_idx], X_raw[idx_benign, protocol_idx],
            c='blue', label='Benign', alpha=0.6, s=100, edgecolors='k')
plt.scatter(X_raw[idx_phishing, lifetime_idx], X_raw[idx_phishing, protocol_idx],
            c='red', label='Phishing', alpha=0.6, s=100, edgecolors='k')

plt.title('Розподіл URL: Час життя vs Протокол')
plt.xlabel('Час життя домену (днів)')
plt.ylabel('Протокол')
plt.legend()
plt.grid(True, linestyle='--')

plt.savefig('result_plot.png')
print("Графік збережено як 'result_plot.png'")
plt.show()