import requests
from nltk.tokenize import RegexpTokenizer
from bs4 import BeautifulSoup
import smtplib, time, os, datetime, pytz
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# para evitar llenar el log del container con las alertas
requests.packages.urllib3.disable_warnings()

import nltk.data
nltk.data.path.append("nltk_data")
tokenizer = nltk.data.load("tokenizers/punkt/PY3/punkt/spanish.pickle")

# Para ir guardando las noticias
def capturas(wordSel, link):
  agregar = 1
  if os.path.exists('capturas.txt'):
    with open('capturas.txt', 'r') as f:
      agregar = 0 if link in f.read() else 1
  with open('capturas.txt', 'a') as f:
    if agregar == 1:
      f.write(f'{datetime.datetime.now(pytz.timezone("America/Asuncion")).strftime("%d/%m/%Y %H:%M:%S")} - {wordSel} - <a href="{link}">{link}</a>\n')

dictTranslate = {225: 97, 233: 101, 237: 105, 243: 111, 250: 117, 46: 32}
beforeLink = ''
beforeLinkUh = ''
beforeLinkLN = ''

if datetime.datetime.now(pytz.timezone("America/Asuncion")).strftime("%H") in('08', '09', '10', '11'):
  horaUltReporte = '08'
elif datetime.datetime.now(pytz.timezone("America/Asuncion")).strftime("%H") in('12', '13', '14', '15'):
  horaUltReporte = '12'
else:
  horaUltReporte = '16'

while True:
    # Se obtiene la noticia
    headers = {
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36 Edg/95.0.1020.53"
    }
    url = "https://www.abc.com.py/nacionales"
    response = requests.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(response.text, features="lxml")
    article = soup.find(class_='article-list one-item big-item')
    link = 'https://www.abc.com.py' + [a['href'] for a in article.select('a[href]')][0]
    intro = article.find('p')

    # aquí se revisa si la intro contiene alguna de las palabras claves (cargar todo sin acentos y en minúsculas)
    wordsBase = ['narcotrafico', 'tenencia de drogas', 'incautacion de drogas', 'lavado de dinero',
    'microtrafico', 'extorsion', 'sextorsion', 'cohecho pasivo', 'usura', 'corrupcion', 'sicariato',
    'sicarios', 'trata de personas', 'trafico de armas', 'portacion de armas sin autorizacion',
    'contrabando', 'incautacion de productos de contrabando', 'lesion de confianza',
    'asociacion criminal', 'produccion de documentos no autenticos', 'estafa', 'criptomonedas', 'terrorismo'
    'trafico de drogas', 'bitcoin', 'usurero', 'produccion de documentos falsos', 'enriquecimiento ilicito', 'criptoactivos']

    words = list() + wordsBase
    reportar = 'NO'
    while len(words) > 0:
        word = words.pop()
        if f" {word} " in f" {intro.text.lower().translate(dictTranslate)} ":
            reportar = 'SI'
            wordSel = word

    # cuando el link de la noticia actual es diferente al anterior, acumula en el archivo
    if link != beforeLink and reportar == 'SI':
        capturas(wordSel, link)

    # log
    with open("log.txt", 'a') as log:
      log.write(f'{datetime.datetime.now(pytz.timezone("America/Asuncion")).strftime("%d/%m/%Y %H:%M:%S")} - {link}\n')


    # Ultima Hora
    urlUh = 'https://www.ultimahora.com/nacionales'
    linkUh = BeautifulSoup(requests.get(urlUh, headers=headers, verify=False).text, features='lxml').find(class_='PageList-items-item').find(class_='Link')['href']
    introUh = BeautifulSoup(requests.get(linkUh, headers=headers, verify=False).text, features='lxml').find(class_='ArticlePage-lede-content')

    words = list() + wordsBase
    reportar = 'NO'
    while len(words) > 0:
        word = words.pop()
        for i in introUh.select('h2'):
            if word in ' '.join([str(item) for item in RegexpTokenizer(r'\w+').tokenize(i.text.lower().translate(dictTranslate))]):
                reportar = 'SI'
                wordSel = word

    # cuando el link de la noticia actual es diferente al anterior, acumula en el archivo
    if linkUh != beforeLinkUh and reportar == 'SI':
        capturas(wordSel, linkUh)

    # log
    with open("log.txt", 'a') as log:
      log.write(f'{datetime.datetime.now(pytz.timezone("America/Asuncion")).strftime("%d/%m/%Y %H:%M:%S")} - {linkUh}\n')


    # La Nacion
    urlLN = 'https://www.lanacion.com.py/category/pais/'
    linkLN = 'https://www.lanacion.com.py' + [a['href'] for a in BeautifulSoup(requests.get(urlLN, headers=headers, verify=False).text, features='lxml').find(class_='cln ccp ccp-1 card-1').find(class_='tc').select('a[href]')][0]
    introLN = BeautifulSoup(requests.get(linkLN, headers=headers, verify=False).text, features='lxml').find(class_='sec-m container').find(class_='caption')

    words = list() + wordsBase
    reportar = 'NO'
    while len(words) > 0:
        word = words.pop()
        if f" {word} " in f" {introLN.text.lower().translate(dictTranslate)} ":
            reportar = 'SI'
            wordSel = word

    # cuando el link de la noticia actual es diferente al anterior, acumula en el archivo
    if linkLN != beforeLinkLN and reportar == 'SI':
        capturas(wordSel, linkLN)

    # log
    with open("log.txt", 'a') as log:
      log.write(f'{datetime.datetime.now(pytz.timezone("America/Asuncion")).strftime("%d/%m/%Y %H:%M:%S")} - {linkLN}\n')


    # cuando sea una de las horas de corte y exista capturas.txt, remite el email
    if os.path.exists('capturas.txt') \
       and datetime.datetime.now(pytz.timezone("America/Asuncion")).strftime("%H") in('08', '12', '16') \
       and datetime.datetime.now(pytz.timezone("America/Asuncion")).strftime("%H") != horaUltReporte:
        # lectura de capturas.txt
        with open('capturas.txt', 'r') as f:
            contenido = f.read().replace('\n', '</br>')

        # variables para MIME
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Prensa negativa"
        msg['From'] = "cognos@visionbanco.com"
        msg['To'] = "cumplimiento@visionbanco.com"
        msg['Cc'] = "admdatos@visionbanco.com"

        # crea el html que se inserta como mensaje
        html = f"""\
        <html>
          <head></head>
          <body>
            Las noticias capturadas son:</br></br>
            <p>{contenido}</p>
            <p>Ciencia de Datos (infradw02)</p>
          </body>
        </html>
        """

        # asigna el html como mensaje
        part2 = MIMEText(html, 'html')
        msg.attach(part2)

        # remite el email
        s = smtplib.SMTP('10.18.1.36', 25)
        s.sendmail('cognos@visionbanco.com', ['cumplimiento@visionbanco.com', 'admdatos@visionbanco.com'], msg.as_string())
        s.quit()

        # elimina captura.txt
        os.remove('capturas.txt')
        os.remove('log.txt')

        # hora del ultimo reporte
        horaUltReporte = datetime.datetime.now(pytz.timezone("America/Asuncion")).strftime("%H")

    beforeLink = link
    beforeLinkUh = linkUh
    beforeLinkLN = linkLN
    time.sleep(60)