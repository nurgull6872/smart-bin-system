import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score

url = 'Smart_Bin.csv'
df = pd.read_csv(url)
df = df.dropna(subset=['Container Type', 'Recyclable fraction', 'FL_B', 'Class'])

df_model = pd.get_dummies(df, columns=['Container Type', 'Recyclable fraction'])
le_class = LabelEncoder()
df_model['Target'] = le_class.fit_transform(df['Class'])

X = df_model.drop(['Class', 'Target', 'VS', 'FL_B_3', 'FL_A_3', 'FL_B_12', 'FL_A_12'], axis=1)
y = df_model['Target']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

model_rf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
model_rf.fit(X_train_scaled, y_train)
model_lr = LogisticRegression(max_iter=1000, class_weight='balanced')
model_lr.fit(X_train_scaled, y_train)
model_knn = KNeighborsClassifier(n_neighbors=5)
model_knn.fit(X_train_scaled, y_train)

def tahmin_et():
    try:
        kutu = combo_kutu.get()
        atik = combo_atik.get()
        doluluk = float(ent_doluluk.get())

        if not 0 <= doluluk <= 100:
            messagebox.showwarning("Hata", "Doluluk oranı 0-100 arası olmalı!")
            return

        girdi = pd.DataFrame(0, index=[0], columns=X.columns)
        girdi['FL_B'] = doluluk
        col_kutu = f"Container Type_{kutu}"
        col_atik = f"Recyclable fraction_{atik}"

        if col_kutu in girdi.columns and col_atik in girdi.columns:
            girdi[col_kutu] = 1
            girdi[col_atik] = 1
        else:
            messagebox.showerror("Hata", "Geçersiz seçim!")
            return

        girdi_scaled = scaler.transform(girdi)
        
        modeller = {"Random Forest": model_rf, "Logistic Reg": model_lr, "KNN": model_knn}
        skorlar = []
        isimler = []
        
        sonuc_metni = ""
        for isim, model in modeller.items():
            y_pred = model.predict(X_test_scaled)
            acc = accuracy_score(y_test, y_pred)
            tahmin_idx = model.predict(girdi_scaled)[0]
            tahmin_sonuc = le_class.inverse_transform([tahmin_idx])[0]
            
            skorlar.append(acc)
            isimler.append(isim)
            sonuc_metni += f"{isim}: {tahmin_sonuc.upper()} (Başarı: %{acc*100:.1f})\n"

        lbl_sonuc.config(text=sonuc_metni, foreground="blue")
        
        fig.clear()
        
        ax1 = fig.add_subplot(121)
        ax1.bar(isimler, skorlar, color=['skyblue', 'lightgreen', 'salmon'])
        ax1.set_title("Model Başarımı", fontsize=10)
        ax1.set_ylim(0, 1.1)
        for i, v in enumerate(skorlar):
            ax1.text(i, v + 0.02, f"%{v*100:.1f}", ha='center', fontsize=8)

        ax2 = fig.add_subplot(122)
        sinif_dagilimi = df['Class'].value_counts()
        ax2.pie(sinif_dagilimi, labels=sinif_dagilimi.index, autopct='%1.1f%%', 
                colors=["#993030","#225c95","#006800"], startangle=140)
        ax2.set_title("Sınıf Dağılımı ", fontsize=10)

        fig.tight_layout()
        canvas.draw()

    except ValueError:
        messagebox.showerror("Hata", "Lütfen geçerli bir doluluk oranı girin!")

root = tk.Tk()
root.title("Smart Bin System")
root.geometry("800x750")

frame_input = ttk.LabelFrame(root, text=" Veri Girişi ", padding=10)
frame_input.pack(pady=10, fill="x", padx=20)

ttk.Label(frame_input, text="Kutu Tipi:").grid(row=0, column=0, sticky="w")
combo_kutu = ttk.Combobox(frame_input, values=list(df['Container Type'].unique()), state="readonly")
combo_kutu.grid(row=0, column=1, pady=5)

ttk.Label(frame_input, text="Atık Türü:").grid(row=1, column=0, sticky="w")
combo_atik = ttk.Combobox(frame_input, values=list(df['Recyclable fraction'].unique()), state="readonly")
combo_atik.grid(row=1, column=1, pady=5)

ttk.Label(frame_input, text="Doluluk Oranı (%):").grid(row=2, column=0, sticky="w")
ent_doluluk = ttk.Entry(frame_input)
ent_doluluk.grid(row=2, column=1, pady=5)

btn_tahmin = ttk.Button(frame_input, text="Karar Ver ve Analiz Et", command=tahmin_et)
btn_tahmin.grid(row=3, columnspan=2, pady=10)

lbl_sonuc = ttk.Label(root, font=("Arial", 10, "bold"))
lbl_sonuc.pack(pady=5)

fig = plt.Figure(figsize=(7, 4), dpi=100)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(pady=10, fill="both", expand=True)

root.mainloop()