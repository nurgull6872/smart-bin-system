import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, precision_score, f1_score, recall_score

# veri setimi yükledim
url='Smart_Bin.csv'
df = pd.read_csv(url)

# veri setimden belirlediğim sutunlarda özellikle de pivot tablo kullandığım sütunlarda eksik değer varsa yok ettim
df = df.dropna(subset=[
    'Container Type',
    'Recyclable fraction',
    'FL_B',
    'Class'
])

# oluşturduğum pivot tabloda hangi konteyner türü hangi atık türünde toplanmadan önce ne kadar doluluk oranına ulaştığını
# görmeyi isteyerek ayarladım
# satırlar: konteyner tipi, sütunlar: atık türü, değer: ortalama fl_b
pivot_sonuc = df.pivot_table(
    index='Container Type',
    columns='Recyclable fraction',
    values='FL_B',
    aggfunc='mean'
).round(1)

print(" PİVOT TABLO ANALİZİ \n")
print(pivot_sonuc)

print("Not: Bu tablo toplanmadan önceki değerleri her bir kontenyer tipi ve atık türü için gösterir.")

# veri ön işleme adımlarımdan biri olan bu satırlarda 
# önemli olarak belrilediğim sutunların kategorik olanlarını sayısala çevirdim
# ilk olarak modelime sayısal değer verebilmek için container type ve recyclable fraction için
# onehotencoding kullandım çünkü bu değerler sıralı olmadığı için.
df_model = pd.get_dummies(df, columns=['Container Type', 'Recyclable fraction'])

# tahmin edeceğim değer yani emptyn non emptying değerini ise label encoding kullanarak
# sayısala çevirdim çünkü sütunumun iki farklı değeri olabilir 0 ve 1 gibi.
le_class = LabelEncoder()
df_model['Target'] = le_class.fit_transform(df['Class'])

# modelimin girmesini istemediğim değerleri sildim böylece modelimin hata payını azalttım
X = df_model.drop(['Class', 'Target', 'VS','FL_B_3', 'FL_A_3', 'FL_B_12', 'FL_A_12'], axis=1)
y = df_model['Target']

# verimi test ve train olarak ayırdım %20 test %80 train
X_train, X_test, y_train, y_test = train_test_split(
    X, 
    y,
    test_size=0.2,
    random_state=42,
)

scaler = StandardScaler()
# doluluk_orani oranı diğer girilen bilgilerden yani labelencoder ile yaptığım 0 1  gibi değerlerden
# fazla olacağı için model gereksiz şekilde doluluğa önem verip modelimi yanıltabilirdi 
# bunu önlemek için yaptım.
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# sırasıyla karşılaştırmak istediğim modelleri kurdum
model_rf = RandomForestClassifier(n_estimators=100, random_state=42)
model_rf.fit(X_train_scaled, y_train)

model_lr = LogisticRegression(max_iter=1000)
model_lr.fit(X_train_scaled, y_train)

model_knn = KNeighborsClassifier(n_neighbors=5)
model_knn.fit(X_train_scaled, y_train)

print("\n SİSTEMİMİZE HOŞ GELDİNİZ")
print("\n İStenen değerleri girin ve kararınızı alın")



#hata çıkarsa program çökmesin diye try except bloğuna aldım
try:
    # kullanıcı değer girerken kutu tiplerini görebilsin ve yanlış değer girmesin diye
    kutu_listesi = df['Container Type'].unique()
    atik_listesi = df['Recyclable fraction'].unique()
    print(f"Sistemdeki Kutular: {', '.join(kutu_listesi)}")
    print(f"Atık Türleri    : {', '.join(atik_listesi)}")

    kutu_tipi = input("Kutu tipini girin: ").strip()
    atik_tipi = input("Atık türünü girin: ").strip()
    doluluk_orani = float(input("Doluluk oranını (%) girin: "))

    # kullanıcıdan aldığım değerlerin dorğuluğunu kontrol ediyorum
    if not 0 <= doluluk_orani <= 100:
        raise ValueError("doluluk oranı 0–100 aralığında olmalıdır")

    # kullanıcıdan da hem atık türü hem kutu tipi aldığım için
    #kullanıcıdan gelen verileri de makinenin anlayacağı forma sokmam gerekiyor
    #bunun için yine kategorik olan bilgileri sayısala çevirdim ve devamında da modelin 
    # anlayabilmesi için bir dataframe yapısı oluşturdum
    
    # bu yapıyı kullanıcı değer girdikten sonra önceki yapımla aynı şekilde oluşsun diye yaptım
    #burada model için zaten kullandığım x verileri ile içi full 0dan oluşan bir dataframe tasarladım böylece kulalnıcı 
    #değer girdiğinde bu yapıya uygun şekilde gelecek ve yapı bozulmayacak
    girdi = pd.DataFrame(0, index=[0], columns=X.columns)
    girdi['FL_B'] = doluluk_orani
    
    #kullanıcın girdiği tip ile yeni bir sütun ismi oluşturdum
    col_kutu = f"Container Type_{kutu_tipi}"
    col_atik = f"Recyclable fraction_{atik_tipi}"
    
    # burada ise yine onehotencoding gereği kullanıcının seçtiği kısmı 1 yaptım ve böylece kullanıcın seçtiği 
    # tip türü onehot encodingde ilgili sütunda 1 yapıldı ve seçim yapıldı.
    if col_kutu in girdi.columns and col_atik in girdi.columns:
        girdi[col_kutu] = 1
        girdi[col_atik] = 1
    else:
        raise ValueError("Hatalı kutu tipi veya atık türü girişi\n NOT: Lütfen listedeki isimleri tam yazın.")

    girdi_scaled = scaler.transform(girdi)
    # üstte yaptığım gibi sayısal değerimi ölçeklendirdim

    modeller = {
        "Random Forest": model_rf,
        "Logistic Reg": model_lr,
        "KNN ": model_knn
    }
     # terminal için küçük bir tablo oluşturdum
    print(f"{'Algoritma':25} | {'Accuracy':10} | {'Precision':10} | {'Recall':10} | {'F1-Skor':10}")
    print("-" * 80)

    en_iyi_skor = -1
    en_iyi_model_adi = ""
    en_iyi_tahmin = ""

    for isim, model in modeller.items():
       model_tahmin_index = model.predict(girdi_scaled)[0]
       tahmin_deger = le_class.inverse_transform([model_tahmin_index])[0].upper()
       y_pred = model.predict(X_test_scaled)

       # her bi sınıflandırma algoritmam için sınıflandırma metriklerini kullandım ve 
       # busayede hangi modelim daha verimli görebildim
       acc_deger = accuracy_score(y_test, y_pred)
       prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
       recall_deger = recall_score(y_test, y_pred, average='weighted', zero_division=0)
       f1_deger = f1_score(y_test, y_pred, average='weighted', zero_division=0)
       # hesaplama sonucumda birden fazla sınıf olduğu için sonuçları tek bir değerde toplayıp döndürdüm
    
       print(f"{isim:22} | %{acc_deger*100:<8.1f} | {prec:<10.2f} | {recall_deger:<10.2f} | {f1_deger:<10.2f}")

       if acc_deger > en_iyi_skor:
         en_iyi_skor = acc_deger
         en_iyi_model_adi = isim
         en_iyi_tahmin = tahmin_deger

   
    print("SİSTEM KARARI")

    print(f"Kullanılan En Başarılı Model: {en_iyi_model_adi} (Acc: %{en_iyi_skor*100:.1f})")
    print(f"Tahmin Edilen Toplama Kararı   : {en_iyi_tahmin}")

except Exception as e:
  print(f"\nHata! İşlem tamamlanamadı: {e}")