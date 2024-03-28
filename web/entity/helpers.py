from core.models import UserRights, UserRightsRequests


def enable_entity(entity):

    # get entity admin
    right_request = UserRightsRequests.objects.get(entity=entity, role=UserRightsRequests.ADMIN, status="PENDING")
    admin = right_request.user
    # valid admin rights request
    right_request.status = "ACCEPTED"
    right_request.save()

    # create user right
    UserRights.objects.update_or_create(
        entity=right_request.entity,
        user=right_request.user,
        defaults={"role": right_request.role, "expiration_date": right_request.expiration_date},
    )


# send email to user
# subject = "[CarbuRe] Demande d'inscription de société enregistrée"
# subject = subject if CarbureEnv.is_prod else "STAGING " + subject
# recipient_list = [admin.email] if CarbureEnv.is_prod else ["carbure@beta.gouv.fr"]
# text_message = f"""
# Bonjour,

# Votre demande d'inscription pour la société {entity.name} a été validée par l'administration.
# Vous pouvez désormais vous connectez dans votre espace en tant qu'administrateur.

# Pour plus d'information veuillez consulter notre guide d'utilisation : https://carbure-1.gitbook.io/faq/affichage/traduction

# Bien cordialement,
# L'équipe CarbuRe
# """

# send_mail(
#     subject="[CarbuRe] Demande d'inscription de société validée",
#     message=text_message,
#     from_email=settings.DEFAULT_FROM_EMAIL,
#     recipient_list=recipient_list,
#     fail_silently=False,
# )
