import smtplib
from email.message import EmailMessage
import asyncio
import logging
from app.config import settings

logger = logging.getLogger(__name__)

async def send_email_async(to_email: str, subject: str, content: str):
    """
    Envoie un email de façon asynchrone en utilisant le threadpool natif de Python
    afin de ne pas bloquer l'Event Loop de FastAPI.
    """
    def _send():
        # Fallbacks for config, or from settings
        # On suppose que ces variables d'environnement pourraient exister
        smtp_server = getattr(settings, "SMTP_SERVER", "smtp.gmail.com")
        smtp_port = getattr(settings, "SMTP_PORT", 587)
        smtp_user = getattr(settings, "SMTP_USER", "pulse-rh@example.com")
        smtp_pass = getattr(settings, "SMTP_PASSWORD", "")

        msg = EmailMessage()
        msg.set_content(content)
        msg['Subject'] = subject
        msg['From'] = smtp_user
        msg['To'] = to_email

        try:
            # S'il n'y a pas de mot de passe configuré, on simule l'envoi en développement
            if not smtp_pass:
                logger.warning(f"[MOCK SMTP] Envoi simulé de l'email à {to_email}. Configurez SMTP_PASSWORD pour un envoi réel.")
                return

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
            logger.info(f"Email asynchrone envoyé à {to_email}")
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'email asynchrone à {to_email}: {e}")

    # Exécute la fonction bloquante dans un thread pour ne pas bloquer l'Event Loop
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, _send)
