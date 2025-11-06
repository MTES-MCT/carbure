import useEntity from "common/hooks/entity"
import { Dialog } from "common/components/dialog2"
import { useHashMatch } from "common/components/hash-route"
import Portal from "common/components/portal"
import { Box, LoaderOverlay } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import { useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router"
import { getProvisionCertificateDetails } from "../../api"
import { TextInput } from "common/components/inputs2"
import { formatUnit } from "common/utils/formatters"
import { ExtendedUnit } from "common/types"
import { getSourceLabel } from "../../utils"

export const ProvisionCertificateDetails = () => {
  const { t } = useTranslation()

  const navigate = useNavigate()
  const location = useLocation()
  const match = useHashMatch("provision-certificate/:id")

  const entity = useEntity()

  const provisionResponse = useQuery(getProvisionCertificateDetails, {
    key: "provision-certificate-details",
    params: [entity.id, parseInt(match?.params.id ?? "")],
  })

  const provisionCert = provisionResponse.result?.data

  const closeDialog = () => {
    navigate({ search: location.search, hash: "#" })
  }

  return (
    <Portal onClose={closeDialog}>
      <Dialog
        onClose={closeDialog}
        header={
          <Dialog.Title>
            {t("Certificat de fourniture n°")}
            {provisionCert?.id ?? "..."}
          </Dialog.Title>
        }
        footer={<></>}
      >
        <Box>
          <TextInput
            readOnly
            label={t("Aménageur")}
            value={provisionCert?.cpo.name}
          />
          <TextInput
            readOnly
            label={t("Trimestre")}
            value={t("T{{quarter}} {{year}}", {
              quarter: provisionCert?.quarter,
              year: provisionCert?.year,
            })}
          />
          <TextInput
            readOnly
            label={t("Unité d'exploitation")}
            value={provisionCert?.operating_unit}
          />
          <TextInput
            readOnly
            label={t("Source")}
            value={getSourceLabel(provisionCert?.source)}
          />
          <TextInput
            readOnly
            label={t("Énergie fournie initialement")}
            value={formatUnit(
              provisionCert?.energy_amount ?? 0,
              ExtendedUnit.MWh
            )}
          />
          <TextInput
            readOnly
            label={t("Énergie disponible pour cession")}
            value={formatUnit(
              provisionCert?.remaining_energy_amount ?? 0,
              ExtendedUnit.MWh
            )}
          />
        </Box>

        {provisionResponse.loading && <LoaderOverlay />}
      </Dialog>
    </Portal>
  )
}

export default ProvisionCertificateDetails
