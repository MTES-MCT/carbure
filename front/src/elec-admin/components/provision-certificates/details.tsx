import useEntity from "carbure/hooks/entity"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import { useHashMatch } from "common/components/hash-route"
import { Return } from "common/components/icons"
import { TextInput } from "common/components/input"
import Portal from "common/components/portal"
import { useQuery } from "common/hooks/async"
import { useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import * as api from "../../api"
import { formatNumber } from "common/utils/formatters"

export const ElecAdminProvisionDetailsDialog = () => {
  const { t } = useTranslation()
  const entity = useEntity()
  const navigate = useNavigate()
  const location = useLocation()
  const match = useHashMatch("provision-certificate/:id")

  const provisionCertificateResponse = useQuery(
    api.getProvisionCertificateDetails,
    {
      key: "provision-certificate-details",
      params: [entity.id, parseInt(match?.params.id || "")],
    }
  )
  const provisionCertificate =
    provisionCertificateResponse.result?.data.data?.elec_provision_certificate

  const closeDialog = () => {
    navigate({ search: location.search, hash: "#" })
  }

  return (
    <Portal onClose={closeDialog}>
      <Dialog onClose={closeDialog}>
        <header>
          <h1>
            {t("Certificat de fourniture T{{quarter}} {{year}}", {
              quarter: provisionCertificate?.quarter || "-",
              year: provisionCertificate?.year || "-",
            })}
          </h1>
        </header>

        <main>
          <section>
            <TextInput
              readOnly
              label={t("Aménageur")}
              value={provisionCertificate?.cpo.name}
            />

            <TextInput
              readOnly
              label={t("Trimestre")}
              value={t("T{{quarter}} {{year}}", {
                quarter: provisionCertificate?.quarter,
                year: provisionCertificate?.year,
              })}
            />

            <TextInput
              readOnly
              label={t("Unité d'exploitation")}
              value={provisionCertificate?.operating_unit}
            />

            <TextInput
              readOnly
              label={t("Type de courant")}
              value={provisionCertificate?.current_type}
            />
            <TextInput
              readOnly
              label={t("MWh")}
              value={
                "+ " +
                formatNumber(provisionCertificate?.energy_amount || 0, 3) +
                " MWh"
              }
            />
          </section>
        </main>

        <footer>
          <Button icon={Return} label={t("Retour")} action={closeDialog} />
        </footer>
      </Dialog>
    </Portal>
  )
}

export default ElecAdminProvisionDetailsDialog
