from os import environ

from core.models import Entity, UserRights


# Email sent to all admins of the entity when a user requests access to the entity
def get_request_access_email_default(entity: Entity, user_email: str, comment: str):
    validation_url = f"{environ.get('BASE_URL')}/org/{entity.id}/settings/users"
    email_subject = "Carbure - Demande d'accès"
    message = """
    Bonjour,
    Un utilisateur vient de faire une demande d'accès à CarbuRe.
    Vous pouvez valider ou refuser cette demande depuis la page d'administration de votre société : %s.

    Utilisateur: %s
    Société: %s
    Commentaire: %s
    """ % (
        validation_url,
        user_email,
        entity.name,
        comment,
    )

    # get all user admins for the entity
    admins = entity.get_admin_users_emails()
    recipient_list = list(admins)
    recipient_list.append("carbure@beta.gouv.fr")

    return recipient_list, email_subject, message


# When a user requests access to a biomethane producer, send an email to the DREAL du département du producteur
def get_request_access_email_biomethane_producer(entity: Entity, user_email: str, comment: str):
    """
    Returns (recipient_list, email_subject, message) to notify the DREAL of the department.
    If no EXTERNAL_ADMIN entity manages this department, falls back to the default behavior.
    """
    external_admins = entity.get_managing_external_admins()
    if not external_admins:
        return get_request_access_email_default(entity, user_email, comment)

    email_subject = "Carbure - Demande d'accès"
    message = f"""
    Bonjour,
    Un utilisateur vient de faire une demande d'accès à CarbuRe.
    Vous pouvez valider ou refuser cette demande depuis la page Sociétés de votre DREAL :.

    1 - Allez sur la page 'Sociétés'.
    2 - Selectionnez la société %s.
    3 - Vérifiez que l'utilisateur est bien autorisé à accéder à la société'.
    4 - Dans la liste des utilisateurs, cliquez sur l'icone de validation pour valider la demande.

    Utilisateur: {user_email}
    Société: {entity.name}
    Commentaire: {comment}
    """

    # Get all admins of the external admins that are not user admins, or super users
    admins = []
    for admin_entity in external_admins:
        admins.extend(admin_entity.get_users_emails(user__is_staff=False, user__is_superuser=False, role=UserRights.ADMIN))
    recipient_list = list(dict.fromkeys(admins))

    recipient_list.append("carbure@beta.gouv.fr")

    return recipient_list, email_subject, message
