import { useRoutes } from "common/hooks/routes"
import { EmptyState } from "common/molecules/empty-state"
import { useH2Permissions } from "h2/hooks/use-h2-permissions"
import { useTranslation } from "react-i18next"

export const EmptyCertificates = () => {
  const { t } = useTranslation()
  const { canAccessAdmin } = useH2Permissions()
  const { HYDROGEN } = useRoutes()

  if (canAccessAdmin) {
    return (
      <EmptyState
        title={t("Aucun certificat d'hydrogène disponible")}
        description={t(
          "Validez les lots d'hydrogène pour visualiser les certificats."
        )}
      />
    )
  }

  return (
    <EmptyState
      title={t("Aucun certificat d'hydrogène disponible")}
      description={t(
        "Une fois vos lots d'hydrogène validés par l'administration, vous pourrez retrouver vos certificats ici."
      )}
      buttonProps={{
        children: t("Ajouter un lot d'hydrogène"),
        iconId: "ri-add-line",
        linkProps: {
          to: HYDROGEN().LOTS,
        },
      }}
    />
  )
}
