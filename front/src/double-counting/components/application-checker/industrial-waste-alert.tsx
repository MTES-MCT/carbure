import { Trans, useTranslation } from "react-i18next"
import { Notice } from "common/components/notice"
import { Button } from "common/components/button2"

export const DechetIndustrielAlert = () => {
  const { t } = useTranslation()

  return (
    <Notice
      variant="info"
      icon="ri-error-warning-line"
      title={t("Spécificité Déchets industriels")}
    >
      <p style={{ marginTop: "var(--spacing-xs)" }}>
        <Trans>
          Une demande concernant des déchets industriels doit être accompagnée
          du questionnaire de processus de validation pour ces matières
          premières
        </Trans>{" "}
        <Button
          customPriority="link"
          linkProps={{
            href: "https://www.ecologie.gouv.fr/sites/default/files/Processus%20de%20validation%20de%20mati%C3%A8res%20premi%C3%A8res.pdf",
          }}
        >
          <Trans>disponible ici</Trans>
        </Button>
        .{" " + t("Merci de déposer ce fichier") + " "}
        {t("dans l'onglet Fichiers") + "."}
      </p>
    </Notice>
  )
}
