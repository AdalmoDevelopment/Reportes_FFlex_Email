import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mysql.connector
from datetime import datetime, timedelta
from email.mime.image import MIMEImage
import os.path
from PIL import Image 

# Obtener la ruta del directorio actual
current_directory = os.path.dirname(__file__)

    # Concatenar la ruta del directorio actual con el nombre de la imagen
image_path = os.path.join(current_directory, "image001.png")


smtp_server = 'smtp.gmail.com'
smtp_port = 587
smtp_user = 'jthomas@adalmo.com'
smtp_pass = 'delasmil2'

# Configurar la conexión a la base de datos MySQL
db_connection = mysql.connector.connect(
    host="192.168.50.206",
    user="f2afichajes",
    password="A.1977!acrelec",
    database="fichaflex"
)
cursor = db_connection.cursor(dictionary=True)

cursor.execute("""
    SELECT r.*, u.email, u.intensivo
    FROM registros_new r 
    JOIN users u ON u.nombre = r.usuario 
    WHERE (
        (u.intensivo = 'si' AND !(r.in_time != 0 AND r.out_time != 0)) 
        OR 
        (u.intensivo = 'no' AND !(r.in_time != 0 AND r.out_time != 0 AND r.pause_time != 0 AND r.restart_time != 0))
    ) 
    AND r.fecha = CURDATE() 
    AND r.usuario = 'JUAN IGNACIO THOMAS GARCIA';
""")

fichajeserroneos = cursor.fetchall()

for fichaje in fichajeserroneos:
    print(fichaje)  # Debug: Imprime los valores del fichaje para verificar

    in_color = '#9299a6'
    pause_color = '#9299a6'
    restart_color = '#9299a6'
    out_color = '#9299a6'

    email_to = fichaje['email']
    if fichaje['in_time'] == timedelta(0):
        in_color = 'red'
        fichaje['in_time'] = 'No fichada'
    if fichaje['pause_time'] == timedelta(0):
        pause_color = 'red'
        fichaje['pause_time'] = 'No fichada'
    if fichaje['restart_time'] == timedelta(0):
        restart_color = 'red'
        fichaje['restart_time'] = 'No fichada'
    if fichaje['out_time'] == timedelta(0):
        out_color = 'red'
        fichaje['out_time'] = 'No fichada'

    if fichaje['intensivo'] == 'si':
            fichaje['pause_time'] = 'Intensivo'
            fichaje['restart_time'] = 'Intensivo'
            pause_color, restart_color = '#9299a6', '#9299a6'

    # Crear tabla HTML con estilos en línea
    html = f"""
     <html>
    <body>
        <p>Estimado {fichaje['usuario']}</p>
        <p>Se han detectado uno o varios fichajes sin hacer ayer:</p>
        
        <table style="width: 100%; border-collapse: collapse;">
            <thead>
                <tr style="background-color: #374151; color: white;">
                    <th style="padding: 8px; color: #9299a6; text-align: center;">Fecha</th>
                    <th style="padding: 8px; color: #9299a6; text-align: center;"> </th>
                    <th style="padding: 8px; color: #9299a6; text-align: center;">ENTRADA JORNADA</th>
                    <th style="padding: 8px; color: #9299a6; text-align: center;">SALIDA JORNADA </th>
                    <th style="padding: 8px; color: #9299a6; text-align: center;">INICIO DESCANSO</th>
                    <th style="padding: 8px; color: #9299a6; text-align: center;">SALIDA DESCANSO</th>
                </tr>
            </thead>
            <tbody>
                <tr style="background-color: #1f2937;">
                    <td style="padding: 8px; color: #9299a6; background-color: #111827; text-align: center;">{fichaje['fecha']}</td>
                    <td style="padding: 8px; color: #9299a6; background-color: #1f2937; text-align: center; font-size:20px;">L</td>
                    <td style="padding: 8px; color: {in_color}; background-color: #111827; text-align: center;">{fichaje['in_time']}</td>
                    <td style="padding: 8px; color: {out_color}; background-color: #1f2937; text-align: center;">{fichaje['out_time']}</td>
                    <td style="padding: 8px; color: {pause_color}; background-color: #111827; text-align: center;">{fichaje['pause_time']}</td>
                    <td style="padding: 8px; color: {restart_color}; background-color: #1f2937; text-align: center;">{fichaje['restart_time']}</td>
                </tr>
            </tbody>
        </table>
        </div>
        <p>Por favor, necesitamos llevar de forma meticulosa los registros de horas.</p>
        <p>Saludos.</p>
        <img src="cid:image1" alt="imagen" style="width: 100%; max-width: 600px; display: block; margin-left: auto; margin-right: auto;"/>

    </body>
    </html>
    """

    # Crea el correo electrónico
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = email_to
    msg['Subject'] = 'Fichaje incorrecto detectado'
    msg.attach(MIMEText(html, 'html'))

# Obtener la ruta del directorio actual
    current_directory = os.path.dirname(__file__)

    # Concatenar la ruta del directorio actual con el nombre de la imagen
    image_path = os.path.join(current_directory, "image001.png")

    # Abrir la imagen
        # Abrir la imagen
    with open(image_path, 'rb') as img_file:
        img_data = img_file.read()

    # Crear un objeto MIMEImage con los datos binarios de la imagen
    image_mime = MIMEImage(img_data, name=os.path.basename(image_path))

    image_mime.add_header('Content-ID', '<image1>')

    # Adjuntar la imagen al mensaje
    msg.attach(image_mime)

    
    # Envía el correo electrónico
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, email_to, msg.as_string())
                    
    print(f"Email enviado a {email_to}")  
