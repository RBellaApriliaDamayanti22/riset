import streamlit as st
import mysql.connector
from st_supabase_connection import SupabaseConnection

def damerau_levenshtein_distance(str1, str2):
    # Matriks untuk menyimpan jarak Damerau-Levenshtein
    d = [[0] * (len(str2) + 1) for _ in range(len(str1) + 1)]

    # Inisialisasi baris pertama dan kolom pertama
    for i in range(len(str1) + 1):
        d[i][0] = i
    for j in range(len(str2) + 1):
        d[0][j] = j

    # Mengisi matriks berdasarkan operasi penyisipan, penghapusan, penggantian, dan transposisi
    for i in range(1, len(str1) + 1):
        for j in range(1, len(str2) + 1):
            cost = 0 if str1[i - 1] == str2[j - 1] else 1
            d[i][j] = min(
                d[i - 1][j] + 1,  # Operasi penghapusan
                d[i][j - 1] + 1,  # Operasi penyisipan
                d[i - 1][j - 1] + cost,  # Operasi penggantian
            )

            # Operasi transposisi
            if (
                i > 1
                and j > 1
                and str1[i - 1] == str2[j - 2]
                and str1[i - 2] == str2[j - 1]
            ):
                d[i][j] = min(d[i][j], d[i - 2][j - 2] + cost)

    return d[len(str1)][len(str2)]


import re
def remove_tanda_baca(text):
    text = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)"," ",text).split())
    return text

def check_spell(sentence):
    # mydb = mysql.connector.connect(
    #         host="localhost",
    #         user="root",
    #         password="",
    #         # database="skripsi"
    #         database="koreksi_ejaan",
    #     )


    # mycursor = mydb.cursor()

    # mycursor.execute("SELECT Unique_Words FROM kamus_berita_pariwisata")

    # kamus = mycursor.fetchall()
    # mycursor.close()
    # Initialize connection.
    # conn = st.connection("spelling_correction",type=SupabaseConnection)
    st_supabase = st.experimental_connection(
        name="spelling_correction",
        type=SupabaseConnection,
        ttl=None,
        url="https://vnhstgzurrpktwoavsrq.supabase.co", # not needed if provided as a streamlit secret
        key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZuaHN0Z3p1cnJwa3R3b2F2c3JxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDIyNzQ5NTksImV4cCI6MjAxNzg1MDk1OX0.tnVEfSXiqERs9gVvScp5o2b8ToOrtiZy2v7Jn-mewgU", # not needed if provided as a streamlit secret
    )
    
    # Perform query.
    # rows = conn.query("data", table="data", ttl="10m").execute()
    rows = st_supabase.query("data", table="data", ttl=0).execute()
    
    # kamus = [word[0] for word in kamus]
    kamus = rows.data
    tokenize = sentence.split()

    kamus = [kamus[idx] for idx in range(len(kamus))]

    st.write("kamus",kamus)

    result = "Mungkin yang anda maksud: "
    listDis = {}
    count = 0
    for token in tokenize:
        token = token.lower()
        min_dis = float("inf")
        correctWord = token
        if token in kamus:
            correctWord = token
            min_dis = 0
        else:
            for term in kamus:
                term = term.lower()
                dis = damerau_levenshtein_distance(token, term)
                if dis < min_dis:
                    min_dis = dis
                    correctWord = term
        listDis[correctWord] = min_dis
        result += correctWord + " "
    st.write(result)
    # st.write("DLD Result:")
    # ind = 0
    # for key, value in listDis.items():
    #     st.write(f"({tokenize[ind]} , {key}) = {value}")
    #     ind += 1


st.title("Spelling Correction")
user_input = st.text_input("Input:")
if st.button("Search"):
    if user_input == "":
        st.warning("Input kosong! Silakan masukkan Kata.")
    else:
        check_spell(user_input)
