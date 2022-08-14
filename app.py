from flask import Flask, redirect, render_template, request, url_for
import psycopg2
from Model.Album import Album
from Model.Kullanici import Kullanici 
from Model.Sarki import Sarki 
from Model.Sanatci import Sanatci 
from Model.Grup import Grup 
from Model.Solo import Solo
from Model.Degerlendirme import Degerlendirme


aktif_kullanici = None

def connect():
    #db baglantisi
    connection = psycopg2.connect("dbname=MusicReviewerVT user=postgres password=1234")
    print("Database baglantisi kuruldu")
    return connection
    
def closeConnection(connection):
    connection.close()
    print("Database baglantisi bitirildi")

#SQL SORGUSU FONKSIYONLARI

#Kullanici adi kontrolu
def checkNickname(input_nickname):
    existNickname = False
    connection = connect()
    cursor = connection.cursor()
    
    #nickname ile kayitli kullanici var mi sorgusu
    cursor.execute("SELECT nickname FROM KULLANICI WHERE nickname = (%s)", [input_nickname])
    kullanici = cursor.fetchall()

    #nickname ile kayitli kullanici varsa true 
    if(len(kullanici)>0):
        existNickname = True
        print("Kullanici adi bulundu: ", input_nickname)
    else:
        print("Kullanici adi bulunamadi: ", input_nickname)
    connection.commit()
    cursor.close()
    closeConnection(connection)
    return existNickname

#Sifre adi kontrolu
def checkPassword(input_password):
    existPassword = False
    connection = connect()
    cursor = connection.cursor()
    
    #password ile kayitli kullanici var mi sorgusu
    cursor.execute("SELECT sifre FROM KULLANICI WHERE sifre = (%s)", [input_password])
    kullanici = cursor.fetchall()

    #password ile kayitli kullanici varsa true 
    if(len(kullanici)>0):
        existPassword = True
        print("Kullanici adi bulundu: ", input_password)
    else:
        print("Kullanici adi bulunamadi: ", input_password)
    connection.commit()
    cursor.close()
    closeConnection(connection)
    return existPassword

#Kullanici tablosuna yeni Kullanici ekleme
def createUser(kullanici):
    connection = connect()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO KULLANICI VALUES (%s, %s, %s, %s, %s)", (kullanici.nickname, kullanici.kullanici_ismi, kullanici.kullanici_soyismi, kullanici.mail_adresi, kullanici.sifre))
    print("Kullanici oluturuldu. Nickname: ", kullanici.nickname)
    connection.commit()
    cursor.close()
    closeConnection(connection)

#DB'de tutulan albumlerin listesini doner
def getAlbums():
    connection = connect()
    cursor = connection.cursor()
    albums = []
    cursor.execute("SELECT * FROM ALBUM")

    album = cursor.fetchall()
    for a in album:
        current_album = Album(a[0],a[1],a[2],a[3])
        albums.append(current_album)

    connection.commit()
    cursor.close()
    closeConnection(connection)

    return albums

#album id'si verilen albumu doner doner
def getAlbum(id):
    connection = connect()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM ALBUM WHERE (%s) = album_id", [id])

    album = cursor.fetchall()
    current_album = Album(album[0][0],album[0][1],album[0][2],album[0][3])
    connection.commit()
    cursor.close()
    closeConnection(connection)

    return current_album

#Album'den Albumdeki tum sarkilari getirir
def getSarkilar(album):
    connection = connect()
    cursor = connection.cursor()
    sarkilar = []
    cursor.execute("SELECT * FROM SARKI WHERE (%s) = album_id", [album.album_id])

    sarki = cursor.fetchall()
    for s in sarki:
        current_sarki = Sarki(s[0],s[1],s[2],s[3],s[4],s[5])
        sarkilar.append(current_sarki)

    connection.commit()
    cursor.close()
    closeConnection(connection)

    return sarkilar

#Sarkinin ait oldugu sanatciyi doner
def getSanatci(sanatci_id):
    connection = connect()
    cursor = connection.cursor()
    sanatcilar = []

    #sanatci grup da olsa solo da olsa SANATCI gerekli bilgileri daha sonra elde etmek icin sorgu ile getirilir ve listeye eklenir
    cursor.execute("SELECT * FROM SANATCI WHERE (%s) = sanatci_id", [sanatci_id])
    sanatci = cursor.fetchall()
    sanatcilar.append(Sanatci(sanatci[0][0],sanatci[0][1]))
    cursor.close()

    #eger sanatci bir grupsa, grubun uyeleri(SANATCI) sql sorgulari ile getirilir ve sanatcilar listesine eklenir
    cursor = connection.cursor()
    #sanatci grup mu
    cursor.execute("SELECT * FROM GRUP WHERE (%s) = sanatci_id", [sanatcilar[0].sanatci_id])
    current_grup = cursor.fetchall()
    cursor.close()
    if(len(current_grup) > 0):
        grup = Grup(current_grup[0][0],current_grup[0][1],current_grup[0][2])
        #sanatci bir gruptur, uyeleri de sanatcilar listesine eklenmelidir
        cursor = connection.cursor()
        #uye iliskisi uzerinden grubun solo sanatcilari bulunur
        cursor.execute("SELECT solo_id FROM UYE WHERE (%s) = grup_id", [grup.grup_id])
        sololar = []
        solo = cursor.fetchall()
        for s in solo:
            current_solo = s[0]
            sololar.append(current_solo)

        cursor.close()
    
        #solodan sanatcilara ulasilarak listeye eklenir
        for i in range(0,len(sololar)):
            cursor = connection.cursor()
            cursor.execute("SELECT S.sanatci_id, S.sanatci_ismi FROM SANATCI S, SOLO SOL WHERE (%s) = SOL.solo_id AND SOL.sanatci_id = S.sanatci_id", [sololar[i]])
            sanatci = cursor.fetchall()
            sanatcilar.append(Sanatci(sanatci[0][0],sanatci[0][1]))
            cursor.close()

    connection.commit()
    closeConnection(connection)
    return sanatcilar

#Sarki_id sine gore ilgili sarkinin bilgilerini vt den getirit
def getSarkiBilgileri(sarki_id):
    connection = connect()
    cursor = connection.cursor()
    sarki_bilgileri = [] #sarki_ismi, sanatci_ismi, tur, sure
    
    cursor.execute("SELECT SAR.sarki_ismi, SAN.sanatci_ismi, SAR.tur, SAR.sure FROM SARKI SAR, SANATCI SAN WHERE SAN.sanatci_id = SAR.sanatci_id AND SAR.sarki_id = (%s)", [sarki_id])
    bilgiler = cursor.fetchall()
    sarki_bilgileri = [bilgiler[0][0],bilgiler[0][1],bilgiler[0][2],bilgiler[0][3]]

    connection.commit()
    cursor.close()
    closeConnection(connection)

    return sarki_bilgileri

#Sarki_id sine gore ilgili sarkinin veri tabanindaki degerlendirmelerini getirir
def getDegerlendirmeler(sarki_id):
    connection = connect()
    cursor = connection.cursor()
    
    cursor.execute("SELECT * FROM DEGERLENDIRME WHERE sarki_id = (%s)", [sarki_id])
    degerlendirmeler = []
    degerlendirme = cursor.fetchall()
    for d in degerlendirme:
        degerlendirmeler.append(Degerlendirme(d[0],d[1],d[2],d[3],d[4],d[5]))

    connection.commit()
    cursor.close()
    closeConnection(connection)

    return degerlendirmeler

#Sarki_id sine gore ilgili sarkinin veri tabanindaki degerlendirmelerini getirir
def getAllDegerlendirmeler():
    connection = connect()
    cursor = connection.cursor()
    
    cursor.execute("SELECT * FROM DEGERLENDIRME")
    degerlendirmeler = []
    degerlendirme = cursor.fetchall()
    for d in degerlendirme:
        degerlendirmeler.append(Degerlendirme(d[0],d[1],d[2],d[3],d[4],d[5]))

    connection.commit()
    cursor.close()
    closeConnection(connection)

    return degerlendirmeler

#Veri tabanına degerlendirme ekleme 
def createDegerlendirme(degerlendirme):
    print('*** Deg: ',degerlendirme.degerlendirme_id,degerlendirme.yorum, degerlendirme.puan, degerlendirme.sarki_id, degerlendirme.album_id, degerlendirme.nickname)
    connection = connect()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO DEGERLENDIRME VALUES(%s, %s, %s, %s, %s, %s)", (degerlendirme.degerlendirme_id,degerlendirme.yorum, int(degerlendirme.puan), degerlendirme.sarki_id, degerlendirme.album_id, degerlendirme.nickname))
    print("Degerlendirme oluturuldu. id: ", degerlendirme.degerlendirme_id)
    connection.commit()
    cursor.close()
    closeConnection(connection)

def getAlbumID(sarki_id):
    connection = connect()
    cursor = connection.cursor()
    
    cursor.execute("SELECT album_id FROM SARKI  WHERE sarki_id = (%s)", [sarki_id])
    album_id = cursor.fetchall()

    connection.commit()
    cursor.close()
    closeConnection(connection)

    return album_id[0][0]

app = Flask(__name__)

#pages
@app.route("/", methods=['GET'])
def home():
    global aktif_kullanici
    aktif_kullanici = None
    albumler = getAlbums()
    return render_template("index.html",album_listesi = albumler, len = len(albumler))

@app.route("/register", methods=['GET','POST'])
def register():
    error_message = ""
    if request.method == 'POST':
        #kullanici bilgileri gecerli ise kayıt etme
        kullanici = Kullanici(request.form.get('nickname'),request.form.get('firstname'),request.form.get('lastname'),request.form.get('email'),request.form.get('password'))
        
        #kullanici bilgilerinin gecerlilik kontrolu
        if(len(kullanici.nickname) > 30  or  len(kullanici.nickname) < 5):
            #gecersiz kullanici adi
            error_message="Invalid"
            print("gecersiz kullanici adi: ", kullanici.nickname)

        elif(len(kullanici.kullanici_ismi) > 30):
            #gecersiz firstname
            error_message="Invalid"
            print("gecersiz firstname: ", kullanici.kullanici_ismi)
        
        elif(len(kullanici.kullanici_soyismi) > 30):
            #gecersiz lastname
            error_message="Invalid"
            print("gecersiz lastname: ", kullanici.kullanici_soyismi)
        
        elif(len(kullanici.mail_adresi) > 30  or  len(kullanici.mail_adresi) < 5):
            #gecersiz email
            error_message="Invalid"
            print("gecersiz email: ", kullanici.mail_adresi)

        elif(len(kullanici.sifre) > 15  or  len(kullanici.sifre) < 5):
            #gecersiz password
            error_message="Invalid"
            print("gecersiz password: ", kullanici.sifre)
        else:
            print("gecerli kullanici: ", kullanici.nickname)
            createUser(kullanici)
            return redirect(url_for('login'))
    
    return render_template("Register.html",message = error_message)

@app.route("/login", methods=['GET','POST'])
def login():
    global aktif_kullanici
    error_message = ""
    if request.method == 'POST':
        #kullanicinin submit ettigi bilgileri alma
        curr_nickname = request.form.get('nickname')
        password = request.form.get('password')
        print(curr_nickname)
        print(password)
        #bilgilerin dogrulugunu sorgulama
        nickname_control = checkNickname(curr_nickname)
        password_control = checkPassword(password)

        #bilgiler dogru ise kullanicinin giris islemi gerceklesir
        if(nickname_control and password_control):
            aktif_kullanici = curr_nickname
            return redirect(url_for('homeAfterLogin'))

        #bilgiler dogru degil ise
        else:
            error_message = "Incorrect"
   
    return render_template("Login.html",message = error_message)

@app.route("/homePage", methods=['GET'])
def homeAfterLogin():
    albumler = getAlbums()
    return render_template("indexAfterLogin.html",album_listesi = albumler, len = len(albumler))

@app.route("/album/<string:album_id>", methods=['GET'])
def albumPage(album_id):
    global aktif_kullanici
    current_album = getAlbum(album_id)
    sarkilar = getSarkilar(current_album)
    sanatcilar = []
    sanatcilar= getSanatci(sarkilar[0].sanatci_id)
    
    #kullanici giris yapmis mi kontrol edilir
    if(aktif_kullanici == None):
        aktif_kullanici_var = False
    else:
        aktif_kullanici_var = True

    print("aktif kullanici albumPage: ", aktif_kullanici_var)
    return render_template("album.html",sarki_listesi = sarkilar, len_sarki = len(sarkilar), album = current_album, sanatci = sanatcilar, len_sanatci = len(sanatcilar),giris_yapilmis = aktif_kullanici_var)

@app.route("/sarki/<string:sarki_id>", methods=['GET'])
def sarkiPage(sarki_id):

    comment = request.values.get('comment')
    stars = request.values.get('stars')
    
    global aktif_kullanici

    #kullanici giris yapmis mi kontrol edilir
    if(aktif_kullanici == None):
        aktif_kullanici_var = False
    else:
        aktif_kullanici_var = True

    #veri tabanindan ilgili sarki ile ilgili ekrana basilmasi istenilen bilgiler getirilir
    sb = getSarkiBilgileri(sarki_id)

    #veri tabanindan ilgili sarki ile ilgiliveri tabanindan ilgili sarki ile ilgili kullanici degerlendirmeleri getirilir
    kullanici_degerlendirmeleri = getDegerlendirmeler(sarki_id)
    for d in kullanici_degerlendirmeleri:
        print('kullanici degerlendirmeleri: ',d.yorum)

    album_id = getAlbumID(sarki_id)

    if(aktif_kullanici_var):
        comment_message = 'Please type your comment'
        #giris yapilmissa girilen comment mesajini ve puani veri tabanina kayit eder
        if(not comment == None and not stars == None):
            degerlendirmeler = getAllDegerlendirmeler()
            last_degerlendirme_id = degerlendirmeler[len(degerlendirmeler)-1].degerlendirme_id
            degerlendirme_id = int(last_degerlendirme_id)+1
            degerlendirme = Degerlendirme(str(degerlendirme_id),comment, int(stars), sarki_id,album_id,aktif_kullanici)
            createDegerlendirme(degerlendirme)
            url_str = '/sarki/',sarki_id
            return redirect(url_for('sarkiPage' ,sarki_id=sarki_id))

    else :
        comment_message = 'Please log in before typing your comment'

    print("aktif kullanici sarkiPage: ", aktif_kullanici_var)
    return render_template("music.html",giris_yapilmis = aktif_kullanici_var, sarki_bilgileri = sb, degerlendirmeler = kullanici_degerlendirmeleri, album_id = album_id , sarki_id = sarki_id, message = comment_message)

if __name__ == "__main__":
    app.run(debug=True)