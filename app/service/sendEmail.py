import os
from email.message import EmailMessage
from smtplib import SMTP, SMTPException

EXPO_EMAIL = os.getenv("EXPO_EMAIL", "")
EXPO_APP_PASSWORD = os.getenv("EXPO_APP_PASSWORD", "")
EXPO_FRONT_URL = os.getenv("EXPO_FRONT_URL", "")
HOST_SMTP = "smtp-mail.outlook.com"
PORTA_SMTP = 587

def send_login_token_email(
    user_email: str,
    user_name: str,
    token: str,
) -> bool:
    if not EXPO_EMAIL:
        raise RuntimeError("EXPO_EMAIL não configurado")
    
    if not EXPO_APP_PASSWORD:
        raise RuntimeError("EXPO_APP_PASSWORD não configurado")
    
    if not EXPO_FRONT_URL:
        raise RuntimeError("EXPO_FRONT_URL não configurado")
    
    try:
        assunto = "Bem-vindo a ExpoTech!"

        corpo_email = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; background-color: #f4f4f4; font-family: Arial, sans-serif;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #f4f4f4;">
        <tr>
            <td align="center" style="padding: 20px 0;">
                <table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td align="center" style="padding: 30px 20px 20px 20px;">
                            <h2 style="margin: 0; color: #001489; font-size: 24px;">Olá, {user_name}!</h2>
                        </td>
                    </tr>
                    
                    <tr>
                        <td align="center" style="padding: 0 20px 20px 20px;">
                            <p style="margin: 0; color: #555; font-size: 16px; line-height: 1.6;">
                                Bem-vindo à ExpoTech! Clique no botão abaixo para realizar seu primeiro acesso:
                            </p>
                        </td>
                    </tr>
                    
                    <tr>
                        <td align="center" style="padding: 20px;">
                            <table role="presentation" cellpadding="0" cellspacing="0" border="0">
                                <tr>
                                    <td align="center" style="background-color: #001489; border-radius: 5px;">
                                        <a href="{token}" style="display: block; padding: 15px 40px; color: #ffffff; text-decoration: none; font-size: 16px; font-weight: bold; border-radius: 5px;">
                                            Acessar Plataforma
                                        </a>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <tr>
                        <td align="center" style="padding: 20px; border-top: 1px solid #eee;">
                            <p style="margin: 0; color: #999; font-size: 12px;">
                                Se você não solicitou este acesso, ignore este email.
                            </p>
                        </td>
                    </tr>
                    
                    <tr>
                        <td align="center" style="padding: 20px;">
                            <p style="margin: 0; color: #666; font-size: 14px;">
                                Atenciosamente,<br>
                                <strong style="color: #001489;">Equipe ExpoTech</strong>
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""

        msg = EmailMessage()
        msg["Subject"] = assunto
        msg["From"] = EXPO_EMAIL
        msg["To"] = user_email
        msg.add_alternative(corpo_email, subtype="html", charset="utf-8")

        with SMTP(host=HOST_SMTP, port=PORTA_SMTP, timeout=30) as smtp:
            smtp.starttls()
            smtp.login(EXPO_EMAIL, EXPO_APP_PASSWORD)
            smtp.send_message(msg)
    except SMTPException as e:
        raise RuntimeError(f"Erro ao enviar email: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Erro ao enviar email: {type(e).__name__}: {str(e)}")
        