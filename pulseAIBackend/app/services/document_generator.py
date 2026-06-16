import os
import uuid
import logging
from io import BytesIO
from datetime import datetime
from jinja2 import Environment, DictLoader
from xhtml2pdf import pisa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.domain import DocumentType, DocumentTemplate, BaseTemplate

logger = logging.getLogger(__name__)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class DocumentGenerator:
    """Outils de génération de documents administratifs dynamiques basés sur Jinja2."""

    async def create_pdf_bytes(self, db: AsyncSession, doc_type_code: str, context: dict, custom_fields: dict = None) -> tuple[str, bytes]:
        logger.info(f"Démarrage de la génération pour le type: {doc_type_code}")
        
        if custom_fields is None:
            custom_fields = {}
            
        # Récupérer le type de document
        type_query = select(DocumentType).filter(DocumentType.code == doc_type_code)
        doc_type = (await db.execute(type_query)).scalar_one_or_none()
        
        if not doc_type:
            raise ValueError(f"Type de document introuvable: {doc_type_code}")

        # Récupérer le template actif pour ce type
        template_query = select(DocumentTemplate).options(selectinload(DocumentTemplate.base_template)).filter(
            DocumentTemplate.document_type_id == doc_type.id,
            DocumentTemplate.is_active == True
        )
        active_template = (await db.execute(template_query)).scalar_one_or_none()
        
        if not active_template:
            raise ValueError(f"Aucun template actif trouvé pour le type: {doc_type_code}")
            
        base_template = active_template.base_template
        if not base_template:
            raise ValueError(f"Le template '{active_template.name}' n'est lié à aucun base template.")

        # Charger les templates dans Jinja2 dynamiquement
        templates_dict = {
            "base.html": base_template.html_content,
            f"{doc_type_code}.html": active_template.html_content
        }
        
        env = Environment(loader=DictLoader(templates_dict))
        
        try:
            template = env.get_template(f"{doc_type_code}.html")
        except Exception as e:
            logger.error(f"Erreur lors de la compilation du template Jinja2: {e}")
            raise ValueError(f"Erreur de compilation Jinja2: {str(e)}")
            
        # Fetch assets and add to context
        from app.models.domain import TemplateAsset
        asset_result = await db.execute(select(TemplateAsset))
        assets_list = asset_result.scalars().all()
        assets_dict = {a.key: a.value for a in assets_list}
        context["assets"] = assets_dict

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
            logger.error(f"Erreur lors du rendu Jinja2 pour {doc_type_code}: {e}")
            raise ValueError(f"Erreur de rendu HTML: {str(e)}")

        # 2. Conversion en PDF avec xhtml2pdf
        filename = f"{doc_type_code}_{uuid.uuid4().hex[:8]}.pdf"
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

    async def create(self, db: AsyncSession, doc_type_code: str, context: dict, custom_fields: dict = None) -> str:
        filename, pdf_bytes = await self.create_pdf_bytes(db=db, doc_type_code=doc_type_code, context=context, custom_fields=custom_fields)
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as pdf_file:
            pdf_file.write(pdf_bytes)
        return file_path

document_generator = DocumentGenerator()
