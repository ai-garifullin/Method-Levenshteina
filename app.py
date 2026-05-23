import streamlit as st
# Внедрение хирургического CSS для выравнивания и центрирования сетки 8х8
st.markdown("""
    <style>
    /* 1. Центрируем и сжимаем весь горизонтальный блок матрицы */
    div[data-testid="stHorizontalBlock"]:has(div[data-testid="stCheckbox"]) {
        max-width: 260px !important; /* Жесткая ширина всей сетки */
        margin: 0 auto 20px auto !important; /* Центрирование на странице */
        gap: 0px !important; /* Полностью убираем горизонтальные зазоры между колонками */
    }
    
    /* 2. Убираем отступы у колонок */
    div[data-testid="stHorizontalBlock"]:has(div[data-testid="stCheckbox"]) div[data-testid="column"] {
        padding: 0 !important;
        margin: 0 !important;
    }

    /* 3. ГЛАВНОЕ: Убираем скрытый вертикальный зазор (gap) между строками внутри колонок */
    div[data-testid="stHorizontalBlock"]:has(div[data-testid="stCheckbox"]) div[data-testid="stVerticalBlock"] {
        gap: 0px !important; /* Схлопывает строки вплотную друг к другу */
    }

    /* 4. Настройка самих чекбоксов для создания идеальных квадратных ячеек */
    div[data-testid="stCheckbox"] {
        margin: 0 !important;
        padding: 0 !important;
        height: 32px !important; /* Фиксированная высота ячейки */
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }

    /* 5. Ужимаем внутренние контейнеры клика */
    div[data-testid="stCheckbox"] > label {
        margin: 0 !important;
        padding: 0 !important;
        min-height: 0 !important;
    }
    
    /* Вырезаем пустые текстовые контейнеры подписей */
    div[data-testid="stCheckbox"] [data-testid="stWidgetLabel"] {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# 1. Полная база эталонов для всех 33 букв русского алфавита (размерность 8х8)
LETTER_TEMPLATES = {
    "А": [6, 2, 2, 4, 4, 2, 2, 6],
    "Б": [8, 3, 3, 3, 3, 3, 2, 0],
    "В": [8, 3, 3, 3, 3, 3, 6, 0],
    "Г": [8, 1, 1, 1, 1, 1, 1, 1],
    "Д": [2, 2, 6, 2, 2, 6, 2, 2],
    "Е": [8, 3, 3, 3, 3, 3, 3, 3],
    "Ё": [8, 4, 4, 3, 3, 4, 4, 3],
    "Ж": [6, 1, 2, 8, 8, 2, 1, 6],
    "З": [2, 2, 3, 3, 3, 3, 6, 0],
    "И": [8, 1, 1, 2, 2, 1, 1, 8],
    "Й": [8, 2, 1, 2, 2, 1, 2, 8],
    "К": [8, 1, 2, 2, 2, 2, 2, 4],
    "Л": [2, 2, 2, 4, 4, 2, 2, 8],
    "М": [8, 2, 2, 4, 4, 2, 2, 8],
    "Н": [8, 1, 1, 1, 1, 1, 1, 8],
    "О": [2, 4, 4, 2, 2, 4, 4, 2],
    "П": [8, 1, 1, 1, 1, 1, 1, 8],
    "Р": [8, 2, 2, 2, 2, 2, 2, 0],
    "С": [6, 2, 2, 2, 2, 2, 2, 2],
    "Т": [1, 1, 1, 8, 8, 1, 1, 1],
    "У": [4, 2, 2, 2, 8, 4, 0, 0],
    "Ф": [2, 2, 6, 8, 8, 6, 2, 2],
    "Х": [4, 2, 2, 2, 2, 2, 2, 4],
    "Ц": [8, 1, 1, 1, 1, 1, 8, 2],
    "Ч": [4, 1, 1, 1, 8, 8, 0, 0],
    "Ш": [8, 1, 1, 8, 1, 1, 8, 1],
    "Щ": [8, 1, 1, 8, 1, 1, 8, 3],
    "Ъ": [2, 8, 2, 2, 4, 2, 0, 0],
    "Ы": [8, 2, 2, 4, 0, 0, 8, 0],
    "Ь": [8, 2, 2, 4, 2, 0, 0, 0],
    "Э": [2, 2, 3, 3, 3, 3, 5, 0],
    "Ю": [8, 1, 1, 4, 2, 2, 4, 0],
    "Я": [4, 2, 2, 4, 8, 0, 0, 0]
}

def trim_zeros(vector):
    """
    Алгоритмическая нормализация положения:
    удаляет пустые столбцы (нули) в начале и в конце вектора признаков
    """
    start = 0
    while start < len(vector) and vector[start] == 0:
        start += 1
    end = len(vector)
    while end > start and vector[end - 1] == 0:
        end -= 1
    return vector[start:end] if start < end else [0]

def compute_levenshtein_distance(X, Y):
    """
    Вычисление редакционного расстояния между списками X и Y
    методом динамического программирования
    """
    l = len(X)
    k = len(Y)
    
    # Инициализация матрицы совокупных стоимостей D значениями бесконечности
    D = [[float('inf')] * (k + 1) for _ in range(l + 1)]
    
    # Начальное условие: D(1, 1) = 2 * rho(1, 1)
    rho_1_1 = abs(X[0] - Y[0])
    D[1][1] = 2 * rho_1_1
    
    # Пошаговое заполнение матрицы D
    for i in range(1, l + 1):
        for j in range(1, k + 1):
            if i == 1 and j == 1:
                continue
                
            # Локальное расстояние между текущими элементами
            rho = abs(X[i - 1] - Y[j - 1])
            
            # Стоимость трех операций трансформации
            cost_replace = D[i - 1][j - 1] + 2 * rho  # Замена
            cost_insert = D[i][j - 1] + rho           # Вставка
            cost_delete = D[i - 1][j] + rho           # Удаление
            
            D[i][j] = min(cost_replace, cost_insert, cost_delete)
            
    return D[l][k]

# 2. Оформление графического интерфейса Streamlit
st.set_page_config(page_title="Распознавание символов", layout="centered")
st.title("🔠 Структурное распознавание букв русского алфавита")
st.write("Отметьте клетки на матрице 8x8, чтобы сформировать контур буквы:")

# Инициализация состояния матрицы в сессии Streamlit
if "matrix" not in st.session_state:
    st.session_state.matrix = [[False] * 8 for _ in range(8)]

# Функция очистки рабочего поля
def clear_matrix():
    st.session_state.matrix = [[False] * 8 for _ in range(8)]
    for row_idx in range(8):
        for col_idx in range(8):
            cb_key = f"cb_{row_idx}_{col_idx}"
            st.session_state[cb_key] = False

# Стандартная отрисовка сетки 8х8 через колонки Streamlit
grid_columns = st.columns(8)
for col_idx in range(8):
    with grid_columns[col_idx]:
        for row_idx in range(8):
            cb_key = f"cb_{row_idx}_{col_idx}"
            st.session_state.matrix[row_idx][col_idx] = st.checkbox(
                "", 
                value=st.session_state.matrix[row_idx][col_idx], 
                key=cb_key,
                label_visibility="collapsed"
            )

st.write("---")
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    recognize_clicked = st.button("🔍 Распознать символ", type="primary", use_container_width=True)
with col_btn2:
    st.button("🗑️ Очистить поле", on_click=clear_matrix, use_container_width=True)

# 3. Математический анализ и вывод результатов
if recognize_clicked:
    # Поколоночное сканирование и сбор сырого вектора X
    X = []
    for col_idx in range(8):
        black_pixels_count = sum(1 for row_idx in range(8) if st.session_state.matrix[row_idx][col_idx])
        X.append(black_pixels_count)
        
    st.subheader("📊 Результаты анализа структуры")
    st.info(f"Сформированный числовой список (сырой вектор X): `{X}`")
    
    # Тримминг пустых краев у входного вектора
    X_trimmed = trim_zeros(X)
    st.info(f"Вектор после удаления пустых краев (X_trimmed): `{X_trimmed}`")
    
    best_letter = None
    min_delta = float('inf')
    results_table = []
    
    # Сравнение со всеми 33 эталонами
    for letter, Y in LETTER_TEMPLATES.items():
        # Тримминг пустых краев у текущего шаблона
        Y_trimmed = trim_zeros(Y)
        
        # Расчет расстояния Левенштейна по усеченным значащим векторам
        D_val = compute_levenshtein_distance(X_trimmed, Y_trimmed)
        
        # Нормализация на длину значащих долей
        delta = round(D_val / (len(X_trimmed) + len(Y_trimmed)), 3)
        
        results_table.append({
            "Буква": letter, 
            "Вектор эталона": str(Y), 
            "Усеченный вектор": str(Y_trimmed), 
            "Метрика ошибки (δ)": delta
        })
        
        if delta < min_delta:
            min_delta = delta
            best_letter = letter
            
    # Вывод сводной таблицы результатов
    st.write("### Таблица сравнения с алфавитом:")
    st.table(results_table)
    
    # Финальный вердикт системы
    st.success(f"### Решение системы: распознана буква «{best_letter}» с коэффициентом ошибки {min_delta}")