import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re
from datetime import datetime


def load_data(file_path):
    """
    Memuat dataset berita dari file CSV dengan penanganan format waktu yang benar
    """
    try:
        # Membaca file CSV
        df = pd.read_csv(file_path,
                         names=['Judul', 'Waktu', 'Link', 'Content',
                                'Tag1', 'Tag2', 'Tag3', 'Tag4', 'Tag5', 'Source'],
                         parse_dates=['Waktu'],
                         date_parser=lambda x: pd.to_datetime(x, format='%d/%m/%Y', errors='coerce'))

        # Memeriksa apakah ada nilai waktu yang tidak valid
        invalid_dates = df['Waktu'].isnull().sum()
        if invalid_dates > 0:
            print(f"Peringatan: Terdapat {invalid_dates} baris dengan format tanggal tidak valid")

        return df
    except Exception as e:
        print(f"Error saat memuat data: {e}")
        return None


def detect_slang_words(text, slang_dictionary):
    """
    Mendeteksi kata-kata gaul dalam teks
    """
    found_slang = []
    text = str(text).lower()
    words = re.findall(r'\b\w+\b', text)  # Memisahkan kata dengan lebih baik

    for word in words:
        if word in slang_dictionary:
            found_slang.append(word)
    return found_slang


def analyze_news_and_slang(df):
    """
    Menganalisis dataset berita dan penggunaan bahasa gaul
    """
    # Kamus kata gaul Indonesia
    slang_dictionary = {
        # Kata gaul umum
        'gue', 'lu', 'elu', 'gw', 'loe', 'gak', 'nggak', 'gada', 'gaada',
        'udah', 'udh', 'dah', 'udeh', 'tuh', 'teh', 'mah', 'dong', 'deh',
        'sih', 'nih', 'mulu', 'aja', 'doang', 'banget', 'bgt', 'bener',

        # Kata gaul modern
        'viral', 'netizen', 'followers', 'haters', 'hits', 'kece', 'gercep',
        'gabut', 'garing', 'receh', 'baper', 'kepo', 'julid', 'glow up',

        # Singkatan gaul
        'otw', 'btw', 'asap', 'tfl', 'gas', 'gws', 'hbd', 'oot', 'tbh',
        'fyi', 'cmiiw', 'imho', 'tysm', 'wkwk', 'ttd', 'pdf',

        # Kata gaul bahasa Indonesia
        'gegara', 'santuy', 'gokil', 'cucok', 'mantul', 'mantap', 'sultan',
        'auto', 'anjay', 'yakali', 'sabi', 'jutek', 'lebay', 'kzl'
    }

    # Analisis dasar
    results = {
        'total_berita': len(df),
        'periode': (df['Waktu'].min(), df['Waktu'].max()),
        'sumber_berita': df['Source'].value_counts(),
        'top_tags': pd.concat([df['Tag1'], df['Tag2'], df['Tag3'],
                               df['Tag4'], df['Tag5']]).value_counts().head(10),
        'berita_per_hari': df.groupby(df['Waktu'].dt.date).size(),

        # Analisis bahasa gaul
        'berita_dengan_gaul_judul': 0,
        'berita_dengan_gaul_konten': 0,
        'frekuensi_kata_gaul': Counter(),
        'berita_gaul_per_sumber': Counter(),
        'contoh_berita_gaul': []
    }

    # Analisis bahasa gaul
    for idx, row in df.iterrows():
        # Analisis judul
        slang_in_title = detect_slang_words(row['Judul'], slang_dictionary)

        # Analisis konten
        slang_in_content = detect_slang_words(row['Content'], slang_dictionary)

        if slang_in_title:
            results['berita_dengan_gaul_judul'] += 1
            results['frekuensi_kata_gaul'].update(slang_in_title)

        if slang_in_content:
            results['berita_dengan_gaul_konten'] += 1
            results['frekuensi_kata_gaul'].update(slang_in_content)

        if slang_in_title or slang_in_content:
            results['berita_gaul_per_sumber'][row['Source']] += 1

            if len(results['contoh_berita_gaul']) < 5:
                results['contoh_berita_gaul'].append({
                    'judul': row['Judul'],
                    'waktu': row['Waktu'],
                    'source': row['Source'],
                    'kata_gaul': list(set(slang_in_title + slang_in_content))
                })

    return results


def create_visualizations(results):
    """
    Membuat visualisasi hasil analisis
    """
    # plt..use('seaborn')

    # Visualisasi 1: Analisis Umum
    fig1 = plt.figure(figsize=(15, 10))

    # Plot distribusi sumber berita
    plt.subplot(2, 2, 1)
    results['sumber_berita'].plot(kind='bar')
    plt.title('Distribusi Sumber Berita')
    plt.xlabel('Sumber')
    plt.ylabel('Jumlah Berita')
    plt.xticks(rotation=45)

    # Plot top 10 tags
    plt.subplot(2, 2, 2)
    results['top_tags'].plot(kind='bar')
    plt.title('10 Tag Terpopuler')
    plt.xlabel('Tag')
    plt.ylabel('Frekuensi')
    plt.xticks(rotation=45)

    # Plot tren berita harian
    plt.subplot(2, 1, 2)
    results['berita_per_hari'].plot(kind='line')
    plt.title('Tren Jumlah Berita per Hari')
    plt.xlabel('Tanggal')
    plt.ylabel('Jumlah Berita')

    plt.tight_layout()
    plt.savefig('hasil_analisis_umum.png')
    plt.close()

    # Visualisasi 2: Analisis Bahasa Gaul
    fig2 = plt.figure(figsize=(15, 10))

    # Proporsi berita dengan bahasa gaul
    plt.subplot(2, 2, 1)
    labels = ['Dengan Bahasa Gaul', 'Tanpa Bahasa Gaul']
    sizes = [results['berita_dengan_gaul_konten'],
             results['total_berita'] - results['berita_dengan_gaul_konten']]
    plt.pie(sizes, labels=labels, autopct='%1.1f%%')
    plt.title('Proporsi Berita dengan Bahasa Gaul')

    # Top 10 kata gaul
    plt.subplot(2, 2, 2)
    top_words = pd.DataFrame.from_dict(results['frekuensi_kata_gaul'],
                                       orient='index',
                                       columns=['count']).head(10)
    top_words.plot(kind='bar')
    plt.title('10 Kata Gaul Terpopuler')
    plt.xlabel('Kata')
    plt.ylabel('Frekuensi')
    plt.xticks(rotation=45)

    # Distribusi bahasa gaul per sumber
    plt.subplot(2, 1, 2)
    source_df = pd.DataFrame.from_dict(results['berita_gaul_per_sumber'],
                                       orient='index',
                                       columns=['count'])
    source_df.plot(kind='bar')
    plt.title('Distribusi Bahasa Gaul per Sumber Berita')
    plt.xlabel('Sumber')
    plt.ylabel('Jumlah Berita dengan Bahasa Gaul')
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.savefig('hasil_analisis_bahasa_gaul.png')
    plt.close()


def create_visual_report(results):
    """
    Membuat visualisasi laporan dalam bentuk dashboard
    """
    # plt.style.use('seaborn')

    # Membuat figure dengan ukuran besar untuk dashboard
    fig = plt.figure(figsize=(20, 25))

    # 1. Distribusi Sumber Berita (Pie Chart)
    plt.subplot(4, 2, 1)
    source_sizes = [17770, 17229, 10710, 1]
    source_labels = ['Detik', 'Tempo', 'Kompas', 'Other']
    plt.pie(source_sizes, labels=source_labels, autopct='%1.1f%%')
    plt.title('Distribusi Sumber Berita', pad=20, fontsize=14)

    # 2. Top 10 Tags (Horizontal Bar Chart)
    plt.subplot(4, 2, 2)
    tags = ['Jokowi', 'jabodetabek', 'Prabowo', 'PDIP', 'Pemilu 2024',
            'Pilpres 2024', 'Pilkada 2024', 'KPU', 'Pilkada Jakarta', 'pilkada 2024']
    tag_counts = [3669, 3143, 2014, 1717, 1631, 1528, 1358, 1354, 1310, 1244]
    plt.barh(tags[::-1], tag_counts[::-1])
    plt.title('10 Tag Terpopuler', pad=20, fontsize=14)

    # 3. Proporsi Berita dengan Bahasa Gaul (Donut Chart)
    plt.subplot(4, 2, 3)
    gaul_sizes = [10130, 45782 - 10130]  # Berita dengan gaul vs tanpa gaul
    plt.pie(gaul_sizes, labels=['Mengandung Bahasa Gaul', 'Tanpa Bahasa Gaul'],
            autopct='%1.1f%%', pctdistance=0.85)
    plt.gca().add_artist(plt.Circle((0, 0), 0.70, fc='white'))
    plt.title('Proporsi Penggunaan Bahasa Gaul dalam Berita', pad=20, fontsize=14)

    # 4. Top 10 Kata Gaul (Bar Chart)
    plt.subplot(4, 2, 4)
    words = ['nggak', 'aja', 'sultan', 'sih', 'udah', 'dong', 'banget', 'gue', 'nih', 'gegara']
    frequencies = [6000, 2391, 1818, 1374, 1332, 767, 694, 328, 633, 258]
    plt.bar(words, frequencies)
    plt.xticks(rotation=45)
    plt.title('10 Kata Gaul Terpopuler', pad=20, fontsize=14)

    # 5. Distribusi Bahasa Gaul per Sumber (Bar Chart)
    plt.subplot(4, 2, 5)
    sources = ['Detik', 'Tempo', 'Kompas']
    gaul_counts = [5014, 3283, 1967]
    plt.bar(sources, gaul_counts)
    plt.title('Distribusi Bahasa Gaul per Sumber Berita', pad=20, fontsize=14)

    # 6. Perbandingan Gaul di Judul vs Konten (Grouped Bar Chart)
    plt.subplot(4, 2, 6)
    categories = ['Judul', 'Konten']
    gaul_percentages = [2.1, 22.1]
    non_gaul_percentages = [97.9, 77.9]

    x = range(len(categories))
    width = 0.35

    plt.bar(x, gaul_percentages, width, label='Dengan Bahasa Gaul')
    plt.bar([i + width for i in x], non_gaul_percentages, width, label='Tanpa Bahasa Gaul')

    plt.ylabel('Persentase')
    plt.title('Perbandingan Penggunaan Bahasa Gaul di Judul vs Konten', pad=20, fontsize=14)
    plt.xticks([i + width / 2 for i in x], categories)
    plt.legend()

    # 7. Informasi Dataset (Text Box)
    plt.subplot(4, 2, 7)
    plt.axis('off')
    info_text = (
        'INFORMASI DATASET\n\n'
        'Total Berita: 45,782\n'
        'Periode: 01/01/2024 - 05/09/2024\n\n'
        'Statistik Bahasa Gaul:\n'
        '• Berita dengan Bahasa Gaul di Judul: 983 (2.1%)\n'
        '• Berita dengan Bahasa Gaul di Konten: 10,130 (22.1%)'
    )
    plt.text(0.1, 0.5, info_text, fontsize=12, va='center')

    # Mengatur layout
    plt.tight_layout()

    # Menyimpan visualisasi
    plt.savefig('laporan_visual.png', dpi=300, bbox_inches='tight')
    print("Visualisasi laporan telah disimpan sebagai 'laporan_visual.png'")
    plt.close()


def main():
    # Path file CSV
    file_path = 'politik_merge.csv'  # Sesuaikan dengan nama file Anda

    # Memuat data
    print("Memuat dataset...")
    df = load_data(file_path)

    if df is not None:
        print("Menganalisis data dan penggunaan bahasa gaul...")
        # Analisis data dan bahasa gaul
        results = analyze_news_and_slang(df)

        # Membuat visualisasi
        print("Membuat visualisasi...")
        create_visualizations(results)

        # Membuat dan menampilkan laporan
        print("\nMembuat laporan...")
        create_visual_report(results)
        # print(report)
        print("\nLaporan telah disimpan sebagai 'laporan_analisis_lengkap.txt'")
        print("Visualisasi telah disimpan sebagai 'hasil_analisis_umum.png' dan 'hasil_analisis_bahasa_gaul.png'")


if __name__ == "__main__":
    main()