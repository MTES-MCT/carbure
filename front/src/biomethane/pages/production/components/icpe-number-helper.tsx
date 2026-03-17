import { Dialog } from "common/components/dialog2"
import { NavLink } from "common/components/nav-link"
import { usePortal } from "common/components/portal"
import { Text } from "common/components/text"
import { useTranslation } from "react-i18next"

const IcpeNumberDialog = ({ onClose }: { onClose: () => void }) => {
  const { t } = useTranslation()

  return (
    <div>
      <Dialog
        onClose={onClose}
        header={<Dialog.Title>{t("N° ICPE")}</Dialog.Title>}
      >
        <Text>
          {t(
            "Code à 10 chiffres correspondant au code unique AIOT utilisé sur les applications GUN et GEREP. Ce code figure également dans votre arrêté préfectoral, vos rapports d'inspection…"
          )}
          <br />
          <br />
          {t(
            "Vous pouvez également retrouver ce code à partir de la liste publique des ICPE disponible sur le site Géorisques et en réalisant un filtre de localisation sur votre commune (il s'agit du \"Numéro d'établissement\")."
          )}{" "}
          <NavLink
            target="_blank"
            to="https://www.georisques.gouv.fr/risques/installations/donnees"
            underline
          >
            {t("Accéder au site Géorisques")}
          </NavLink>
          .
          <br />
          <br />
          {t(
            "Dans le cas où vous ne disposez pas de ce code, nous vous invitons à contacter votre interlocuteur DREAL ou DD(ETS)PP."
          )}
        </Text>
      </Dialog>
    </div>
  )
}

export const IcpeNumberHelper = () => {
  const { t } = useTranslation()
  const portal = usePortal()

  const handleClick = () => {
    portal((close) => <IcpeNumberDialog onClose={close} />)
  }

  return (
    <button onClick={handleClick} style={{ padding: 0 }} type="button">
      {t("Où trouver mon numéro ICPE ?")}
    </button>
  )
}
