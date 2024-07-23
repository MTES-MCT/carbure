import useEntity from "carbure/hooks/entity"
import Alert from "common/components/alert"
import Button, { ButtonVariant, ExternalLink } from "common/components/button"
import { AlertTriangle, Send } from "common/components/icons"
import { Trans, useTranslation } from "react-i18next"

export const DechetIndustrielAlert = ({
	mailToIsButton = false,
}: {
	mailToIsButton?: boolean
}) => {
	return (
		<Alert
			// style={{ flexDirection: "column" }}
			variant="warning"
			icon={AlertTriangle}
		>
			<p>
				<strong>
					<Trans>Spécifité "Déchets industriels"</Trans>
				</strong>{" "}
				<br />
				<Trans>
					Une demande concernant des déchets industriels doit être accompagnée
					du questionnaire de processus de validation pour ces matières
					premières
				</Trans>{" "}
				<ExternalLink
					href={
						"https://www.ecologie.gouv.fr/sites/default/files/Processus%20de%20validation%20de%20mati%C3%A8res%20premi%C3%A8res.pdf"
					}
				>
					<Trans>disponible ici</Trans>
				</ExternalLink>
				.
				<br />
				<Trans>
					Merci de nous le joindre par email avant de nous envoyer votre
					demande.
				</Trans>
				<br />
				<MailtoButton variant={mailToIsButton ? "secondary" : "link"} />
			</p>
		</Alert>
	)
}

const MailtoButton = ({
	variant = "secondary",
}: {
	variant?: ButtonVariant
}) => {
	const { t } = useTranslation()
	const entity = useEntity()

	const bodyMessage = `Mesdames%2C%20Messieurs%2C%0D%0A%0D%0A%E2%80%A8Je%20vais%20vous%20envoyer%20le%20dossier%20de%20demande%20de%20reconnaissance%20au%20Double%20Comptage%20pour%20notre%20soci%C3%A9t%C3%A9.%0D%0A%0D%0AEtant%20donn%C3%A9%20que%20notre%20demande%20concerne%20des%20d%C3%A9chets%20industriels%2C%20Je%20vous%20joint%20%3A%E2%80%A8%0D%0A-%20le%20questionnaire%20de%20processus%20de%20validation%20des%20mati%C3%A8res%20premieres%20rempli%20pour%20les%20d%C3%A9chets%20industriels%20mentionn%C3%A9s.%E2%80%A8%E2%80%A8%0D%0A%0D%0ABien%20cordialement%0D`

	const subject = `[CarbuRe - Double comptage] Demande de ${entity.name}`

	const mailto = `mailto:carbure@beta.gouv.fr?subject=${encodeURIComponent(subject)}&body=${bodyMessage}}`

	return (
		<Button
			icon={variant != "link" ? Send : undefined}
			label={t("Envoyer le formulaire par email")}
			variant={variant}
			href={mailto}
		/>
	)
}
