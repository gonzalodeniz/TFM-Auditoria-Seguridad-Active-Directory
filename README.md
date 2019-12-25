# TFM - AWDP: Auditoría de Active Directory de Windows
El objetivo de este proyecto de fin de máster es el desarrollo una colección de herramientas útiles para realizar enumeración de sistemas, primer paso en un pentest, y para auditar sistemas principalmente en entornos Windows y en servidores con Active Directory.

Esta colección de herramientas está categorizada en tres grupos: Auditoría de Active Directory de Windows, enumeración de redes Windows y enumeración de un equipo local. 

El proyecto se desarrolla totalmente en el lenguaje Python 2.7 y en un entorno de desarrollo Debian GNU/Linux junto con el IDE PyCharm Community. Se elige Python para desarrollar las herramientas porque sin lugar a dudas es el lenguaje de referencia en el mundo de la seguridad informática. Además de la facilidad para ser escrito, cuenta también con un elevado número de librerías de todo tipo, algo que facilita bastante el desarrollo de las herramientas.

Las herramientas que se desarrollan son:

•	awdp_ad_users.py		Auditoría de cuentas de usuarios de un Active Directory
•	awdp_ad_computers.py	Auditoría de cuentas de dispositivos de un Active Directory
•	awdp_ad_groups.py		Auditoría de grupos de un Active Directory
•	awdp_ad_smb.py		Enumeración de recursos compartidos
•	awdp_ad_smb_mon.py		Monitorización de recursos compartidos
•	awdp_stolen_mail.py		Busca si una cuenta de correo ha sido comprometido o robado.
•	awdp_win_attack_dict.py	Auditoría de claves débiles de cuentas de usuarios
•	awdp_ipublic.py		Devuelve IP pública de una red.
•	awdp_nmap.py			Descubrimiento de redes.
•	awdp_services.py		Enumeración de servicios en equipo remoto.
•	awdp_file_metadata.py	Enumeración de metadatos de documentos.

Por último, se comprueba estas herramientas en una red compuesta por los servidores Windows Server 2016 y 2003 y los clientes Windows 10, y Windows XP. 
