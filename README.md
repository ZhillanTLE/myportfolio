### Developer's Identity
Name : Zhillan Baniaksa

NPM : 2506637174

Class : PBP KKI

**live:** https://zhillan-baniaksa-myportfolio.pws.cs.ui.ac.id

**updated**: 04/10/2026

do run Local Setup for grading measures:
### Local Setup
```
git clone https://github.com/ZhillanTLE/myportfolio.git
cd myportfolio
python -m venv env && source env/bin/activate
pip install -r requirements.txt
python manage.py runserver
```

### Reflection 6
1. 
    REST (Representational State Transfer) adalah gaya arsitektur perangkat lunak (architectural style) yang diperkenalkan oleh Roy Fielding dalam disertasi doktoralnya (2000). REST memanfaatkan protokol stateless—umumnya HTTP dimana komunikasi antar komponen berpusat pada manipulasi resource yang diidentifikasi melalui URI (Uniform Resource Identifier) menggunakan representasi standar (seperti JSON, XML, atau HTML).
2. 
    Serializer di DRF sangat penting. Ia bekerja seperti penerjemah dua arah. Ia mengubah data Django yang rumit—misalnya QuerySet atau model instance menjadi data sederhana yang bisa langsung diubah ke JSON (serialization). Di sisi lain, ia juga mengambil JSON dari klien dan mengembalikannya menjadi objek model Python yang sah (deserialization). Mengapa Serializer lebih baik daripada membuat kamus manual lewat JsonResponse? Karena Serializer punya validasi otomatis yang lengkap. Ia juga membersihkan dan menyaring data masuk, mendukung relasi bertingkat nested atau hyperlinked relationships dan menangani error secara standar, misalnya 400 Bad Request. Selain itu, Serializer langsung terhubung ke fungsi mutasi data seperti save(), create(), update(), sehingga tidak perlu menulis logika pengecekan manual yang mudah salah dan susah dipelihara.
3. 
    Autentikasi adalah cara memverifikasi siapa seseorang. Ini memastikan bahwa orang yang masuk benar-benar dirinya. Sementara itu, otorisasi adalah proses mengecek apa saja yang boleh dilakukan oleh pengguna tersebut di suatu sumber daya. Misalnya, apa yang bisa dia lakukan atau akses.

    Pemeriksaan hak akses harus dilakukan di sisi server, bukan di klien. Karena di sisi klien, semua bisa diubah atau dimanipulasi. Misalnya, jika tombol dihilangkan dari tampilan, itu hanya tampak kosmetik. Orang bisa melihatnya lewat fitur Inspect Element di browser. Atau bahkan mengakses langsung via perintah API menggunakan cURL atau Postman.
4. 
    Permintaan yang mengubah data seperti POST, PUT, PATCH, atau DELETE tetap memerlukan token CSRF ketika menggunakan SessionAuthentication. Ini karena browser secara otomatis menyertakan cookie sesi setiap kali melakukan permintaan ke situs yang berbeda. Artinya, jika ada situs jahat yang menyerang, mereka bisa memanfaatkan ini untuk melakukan tindakan yang tidak diinginkan atas nama pengguna yang sedang aktif. Itu sebabnya token CSRF dibutuhkan—untuk mencegah serangan seperti itu.

#### Reflecting on AI Usage
Used Claude Code to find me why my 'python manage.py check" shows an error on tutorial 01. This was necessary since my eyes couldn't find which references was left out when i changed /myportfolio to /portfolio.

A full prompt record in [docs/ai-log.md](docs/ai-log.md).

I still believe while AI would do my Individual Assignment way faster, that is not the purpose of this course: for me (and everyone else) to learn even alongside AI help.

