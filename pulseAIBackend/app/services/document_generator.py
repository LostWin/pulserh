import os
import uuid
import logging
from io import BytesIO
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa


logger = logging.getLogger(__name__)

UPLOAD_DIR = "uploads"
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")

os.makedirs(UPLOAD_DIR, exist_ok=True)

class DocumentGenerator:
    """Outils de génération de documents administratifs basés sur Jinja2."""
    
    def __init__(self):
        # Configuration de l'environnement Jinja2
        if os.path.exists(TEMPLATE_DIR):
            self.env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        else:
            self.env = None
            logger.warning(f"Le dossier de templates n'existe pas : {TEMPLATE_DIR}")

    def create_pdf_bytes(self, doc_type: str, context: dict, custom_fields: dict = None) -> tuple[str, bytes]:
        """
        Méthode principale de génération de document.
        Charge le template Jinja2 correspondant à `doc_type`,
        injecte le `context` et génère le fichier PDF en mémoire.
        """
        logger.info(f"Démarrage de la génération pour le type: {doc_type}")
        
        if custom_fields is None:
            custom_fields = {}
            
        template_name = f"{doc_type}.html"
        
        try:
            template = self.env.get_template(template_name)
            logger.info(f"Template {template_name} chargé avec succès.")
        except Exception as e:
            logger.error(f"Erreur lors du chargement du template {template_name}: {e}")
            # Fallback
            try:
                template = self.env.get_template("attestation_travail.html")
                doc_type = "attestation_travail"
            except Exception as e2:
                raise ValueError(f"Impossible de charger le template de fallback: {e2}")

        # Ajout de variables globales utiles au template
        template_vars = {
            **context,
            "custom_fields": custom_fields,
            "date": datetime.now().strftime("%d/%m/%Y")
        }
        
        # 1. Rendu HTML
        try:
            html_out = template.render(template_vars)
        except Exception as e:
            logger.error(f"Erreur lors du rendu Jinja2 pour {doc_type}: {e}")
            raise

        # 2. Conversion en PDF avec xhtml2pdf
        filename = f"{doc_type}_{uuid.uuid4().hex[:8]}.pdf"
        try:
            pdf_buffer = BytesIO()
            pisa_status = pisa.CreatePDF(
                src=html_out,
                dest=pdf_buffer
            )
                
            if pisa_status.err:
                logger.error(f"Erreur lors de la création du PDF {filename}: {pisa_status.err}")
                raise Exception("Erreur de conversion PDF")

            logger.info("Document PDF généré avec succès : %s", filename)
            return filename, pdf_buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Exception critique lors de l'écriture du PDF: {e}")
            raise

    def create(self, doc_type: str, context: dict, custom_fields: dict = None) -> str:
        filename, pdf_bytes = self.create_pdf_bytes(doc_type=doc_type, context=context, custom_fields=custom_fields)
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as pdf_file:
            pdf_file.write(pdf_bytes)
        return file_path

# Singleton global pour utiliser dans l'API et le RAG
document_generator = DocumentGenerator()
