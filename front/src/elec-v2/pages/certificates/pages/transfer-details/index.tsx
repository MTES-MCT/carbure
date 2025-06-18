import useEntity from "common/hooks/entity"
import { Dialog } from "common/components/dialog2"
import { useHashMatch } from "common/components/hash-route"
import Portal from "common/components/portal"
import { Box, LoaderOverlay } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import { useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import { getTransferCertificateDetails } from "../../api"
import { TextInput } from "common/components/inputs2"
import { formatDate, formatUnit } from "common/utils/formatters"
import { ExtendedUnit } from "common/types"
import TicketTag from "saf/components/tickets/tag"
import { AcceptTransferCertificate } from "../../components/accept-transfer-certificate"
import { RejectTransferCertificate } from "../../components/reject-transfer-certificate"
import { TransferCertificateStatus } from "../../types"

export const TransferCertificateDetails = () => {
  const { t } = useTranslation()

  const navigate = useNavigate()
  const location = useLocation()
  const match = useHashMatch("transfer-certificate/:id")
  const transferID = parseInt(match?.params.id ?? "")

  const entity = useEntity()

  const transferResponse = useQuery(getTransferCertificateDetails, {
    key: "transfer-certificate-details",
    params: [entity.id, transferID],
  })

  const transferCert = transferResponse.result?.data
  const isPending = transferCert?.status === TransferCertificateStatus.PENDING

  function closeDialog() {
    navigate({ search: location.search, hash: "#" })
  }

  return (
    <Portal onClose={closeDialog}>
      <Dialog
        onClose={closeDialog}
        header={
          <Dialog.Title>
            <TicketTag status={transferCert?.status} />
            {t("Certificat de cession n°")}
            {transferCert?.certificate_id ?? "..."}
          </Dialog.Title>
        }
        footer={
          <>
            {entity.isOperator && isPending && (
              <>
                <RejectTransferCertificate id={transferID} />
                <AcceptTransferCertificate id={transferID} />
              </>
            )}
          </>
        }
      >
        <Box>
          <TextInput
            readOnly
            label={t("Aménageur")}
            value={transferCert?.supplier.name}
          />
          <TextInput
            readOnly
            label={t("Redevable")}
            value={transferCert?.client.name}
          />
          <TextInput
            readOnly
            label={t("Date d'émission")}
            value={formatDate(transferCert?.transfer_date ?? null)}
          />
          {!entity.isCPO && (
            <TextInput
              readOnly
              label={t("Date de déclaration TIRUERT")}
              value={formatDate(transferCert?.consumption_date ?? null)}
            />
          )}
          <TextInput
            readOnly
            label={t("Énergie transférée")}
            value={formatUnit(
              transferCert?.energy_amount ?? 0,
              ExtendedUnit.MWh
            )}
          />
        </Box>

        {transferResponse.loading && <LoaderOverlay />}
      </Dialog>
    </Portal>
  )
}

export default TransferCertificateDetails
