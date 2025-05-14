import streamlit as st
import pandas as pd
import glob
import os
import re
import matplotlib.pyplot as plt

from data_utils import load_all_vhi_data, area_names_ua, toggle_ascending

# --- Стани ---
if 'selected_index' not in st.session_state:
    st.session_state.selected_index = 'VHI'
if 'selected_area' not in st.session_state:
    st.session_state.selected_area = 'Київська'
if 'week_range' not in st.session_state:
    st.session_state.week_range = (1, 52)
if 'year_range' not in st.session_state:
    st.session_state.year_range = (2000, 2024)
if 'ascending_order' not in st.session_state:
    st.session_state.ascending_order = False
if 'descending_order' not in st.session_state:
    st.session_state.descending_order = False

# --- Завантаження даних ---
df = load_all_vhi_data("vhi_data")
df = df[df['year'] <= 2024]  # Фільтрація даних, якщо є майбутні роки

# --- Інтерфейс ---
st.title("Аналіз індексів рослинності VHI/VCI/TCI по Україні 🌾")

col1, col2 = st.columns([1, 2])

with col1:
    index = st.selectbox("Оберіть індекс", options=['VCI', 'TCI', 'VHI'])
    area = st.selectbox("Оберіть область", options=list(area_names_ua.values()))

    week_range = st.slider("Інтервал тижнів", 1, 52, st.session_state.week_range)
    year_range = st.slider("Інтервал років", 1981, 2024, st.session_state.year_range)

    # Checkbox для сортування
    st.checkbox("Сортувати за зростанням", key="ascending_order", on_change=toggle_ascending)
    st.checkbox("Сортувати за спаданням", key="descending_order", on_change=toggle_ascending)

    # Скидання фільтрів
    if st.button("Скинути фільтри"):
        st.session_state.selected_index = 'VHI'
        st.session_state.selected_area = 'Київська'
        st.session_state.week_range = (1, 52)
        st.session_state.year_range = (2000, 2024)
        st.session_state.ascending_order = False
        st.session_state.descending_order = False
        st.experimental_rerun()

with col2:
    # Фільтрація
    inv_area_dict = {v: k for k, v in area_names_ua.items()}
    area_id = inv_area_dict[area]

    filtered = df[
        (df['province_id'] == area_id) &
        (df['week'].between(*week_range)) &
        (df['year'].between(*year_range))
    ][['year', 'week', index, 'province_id']]

    # Сортування
    if st.session_state.ascending_order and not st.session_state.descending_order:
        filtered = filtered.sort_values(by=index, ascending=True)
    elif st.session_state.descending_order and not st.session_state.ascending_order:
        filtered = filtered.sort_values(by=index, ascending=False)

    # Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Таблиця", "📈 Графік", "📉 Порівняння"])

    with tab1:
        st.dataframe(filtered)

    with tab2:
        fig, ax = plt.subplots()
        ax.plot(filtered['year'].astype(str) + '-' + filtered['week'].astype(str), filtered[index])
        ax.set_title(f"{index} у {area}")
        ax.set_ylabel(index)
        ax.set_xlabel("Рік-тиждень")
        ax.tick_params(axis='x', rotation=45)
        st.pyplot(fig)

    with tab3:
        comparison_df = df[
            (df['week'].between(*week_range)) &
            (df['year'].between(*year_range))
        ].groupby(['province_id'])[index].mean().reset_index()
        comparison_df['Область'] = comparison_df['province_id'].map(area_names_ua)

        fig2, ax2 = plt.subplots(figsize=(10, 6))
        ax2.bar(comparison_df['Область'], comparison_df[index])
        ax2.set_title(f"Середній {index} по всіх областях ({year_range[0]}–{year_range[1]})")
        ax2.tick_params(axis='x', rotation=90)
        st.pyplot(fig2)
