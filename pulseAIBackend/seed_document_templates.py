import asyncio
import uuid
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.domain import DocumentType, BaseTemplate, DocumentTemplate

# Templates HTML pour les différents types
ATTESTATION_TRAVAIL_HTML = """
<div class="document-content">
    <h1>Attestation de Travail</h1>
    <p>Nous soussignés, <strong>PULSE RH</strong>, certifions par la présente que :</p>
    <p>Monsieur/Madame <strong>{{ employee.first_name }} {{ employee.last_name }}</strong></p>
    <p>Est employé(e) au sein de notre entreprise depuis le <strong>{{ employee.hire_date }}</strong>.</p>
    <p>Il/Elle occupe actuellement le poste de <strong>{{ job.title }}</strong> au sein du département <strong>{{ employee.department_name }}</strong>.</p>
    <p>Type de contrat actuel : <strong>{{ contract.type }}</strong></p>
    <br><br>
    <p>Cette attestation est délivrée pour servir et valoir ce que de droit.</p>
    <br><br>
    <p class="signature" style="text-align: right; margin-top: 50px;">
        Fait pour valoir ce que de droit,<br>
        La Direction des Ressources Humaines
    </p>
</div>
"""

CERTIFICAT_SALAIRE_HTML = """
<div class="document-content">
    <h1>Certificat de Salaire</h1>
    <p>Nous soussignés, <strong>PULSE RH</strong>, certifions par la présente que :</p>
    <p>Monsieur/Madame <strong>{{ employee.first_name }} {{ employee.last_name }}</strong></p>
    <p>Employé(e) au sein de notre entreprise en tant que <strong>{{ job.title }}</strong> (Contrat: {{ contract.type }}),</p>
    <p>Perçoit une rémunération annuelle brute s'élevant à :</p>
    <h2 style="text-align: center; color: #1F524B; margin: 30px 0;">{{ salary_formatted }} €</h2>
    <p>Soit une rémunération mensuelle brute de base de <strong>{{ monthly_salary_formatted }} €</strong>.</p>
    <br><br>
    <p>Ce certificat est délivré à la demande de l'intéressé(e) pour servir et valoir ce que de droit.</p>
    <br><br>
    <p class="signature" style="text-align: right; margin-top: 50px;">
        Fait pour valoir ce que de droit,<br>
        La Direction des Ressources Humaines
    </p>
</div>
"""

AUTORISATION_TELETRAVAIL_HTML = """
<div class="document-content">
    <h1>Autorisation de Télétravail</h1>
    <p>La présente atteste que :</p>
    <p>Monsieur/Madame <strong>{{ employee.first_name }} {{ employee.last_name }}</strong></p>
    <p>Occupant le poste de <strong>{{ job.title }}</strong>,</p>
    <p>Bénéficie d'un accord de télétravail conformément à la charte de l'entreprise.</p>
    <p>Il/Elle est autorisé(e) à exercer ses fonctions en télétravail régulier, à raison de <strong>2 jours par semaine</strong>, dans le respect de ses obligations contractuelles et horaires de travail.</p>
    <p>Son manager direct, <strong>{% if manager %}{{ manager.first_name }} {{ manager.last_name }}{% else %}Non défini{% endif %}</strong>, a validé ces modalités.</p>
    <br><br>
    <p class="signature" style="text-align: right; margin-top: 50px;">
        Fait pour valoir ce que de droit,<br>
        La Direction des Ressources Humaines
    </p>
</div>
"""

DOCUMENT_TYPES = [
    {
        "code": "attestation_travail",
        "name": "Attestation de Travail",
        "allowed_roles": ["collaborator", "hr", "admin", "manager", "director"],
        "responsible_role": "hr",
        "required_variables": ["employee", "job", "contract"],
        "html_content": ATTESTATION_TRAVAIL_HTML
    },
    {
        "code": "certificat_salaire",
        "name": "Certificat de Salaire",
        "allowed_roles": ["collaborator", "hr", "admin"],
        "responsible_role": "hr",
        "required_variables": ["employee", "job", "salary_formatted", "monthly_salary_formatted", "contract"],
        "html_content": CERTIFICAT_SALAIRE_HTML
    },
    {
        "code": "autorisation_teletravail",
        "name": "Autorisation de Télétravail",
        "allowed_roles": ["collaborator", "hr", "admin", "manager", "director"],
        "responsible_role": "manager",
        "required_variables": ["employee", "job", "manager"],
        "html_content": AUTORISATION_TELETRAVAIL_HTML
    }
]

async def seed_documents():
    async with AsyncSessionLocal() as session:
        # Trouver ou créer le template de base
        result = await session.execute(select(BaseTemplate).filter(BaseTemplate.name == "Template Entreprise (Standard)"))
        base_template = result.scalars().first()
        
        if not base_template:
            print("Template de base introuvable. Veuillez d'abord exécuter le script de création du template de base.")
            # Si absent, on prend le premier
            result = await session.execute(select(BaseTemplate))
            base_template = result.scalars().first()
            if not base_template:
                print("Aucun template de base trouvé dans la base de données. Abandon.")
                return

        for doc_type_data in DOCUMENT_TYPES:
            # Upsert DocumentType
            result = await session.execute(select(DocumentType).filter(DocumentType.code == doc_type_data["code"]))
            doc_type = result.scalars().first()
            
            if not doc_type:
                print(f"Création du type de document : {doc_type_data['name']} ({doc_type_data['code']})")
                doc_type = DocumentType(
                    id=str(uuid.uuid4()),
                    name=doc_type_data["name"],
                    code=doc_type_data["code"],
                    allowed_roles=doc_type_data["allowed_roles"],
                    responsible_role=doc_type_data["responsible_role"],
                    required_variables=doc_type_data["required_variables"]
                )
                session.add(doc_type)
                await session.flush()
            else:
                print(f"Mise à jour du type de document : {doc_type_data['name']} ({doc_type_data['code']})")
                doc_type.name = doc_type_data["name"]
                doc_type.allowed_roles = doc_type_data["allowed_roles"]
                doc_type.responsible_role = doc_type_data["responsible_role"]
                doc_type.required_variables = doc_type_data["required_variables"]

            # Upsert DocumentTemplate
            result = await session.execute(select(DocumentTemplate).filter(DocumentTemplate.document_type_id == doc_type.id))
            doc_template = result.scalars().first()
            
            if not doc_template:
                print(f"Création du template actif pour : {doc_type_data['name']}")
                doc_template = DocumentTemplate(
                    id=str(uuid.uuid4()),
                    name=f"Modèle standard - {doc_type_data['name']}",
                    document_type_id=doc_type.id,
                    base_template_id=base_template.id,
                    html_content=doc_type_data["html_content"],
                    is_active=True
                )
                session.add(doc_template)
            else:
                print(f"Mise à jour du template actif pour : {doc_type_data['name']}")
                doc_template.name = f"Modèle standard - {doc_type_data['name']}"
                doc_template.html_content = doc_type_data["html_content"]
                doc_template.is_active = True
                doc_template.base_template_id = base_template.id

        await session.commit()
        print("\nSeed terminé avec succès ! Les types de documents et leurs templates actifs ont été générés.")

if __name__ == "__main__":
    asyncio.run(seed_documents())
