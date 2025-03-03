import useEntity from "carbure/hooks/entity"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import { Check, Cross, Message, Return } from "common/components/icons"
import { TextInput } from "common/components/input"
import { formatDate } from "common/utils/formatters"
import { useTranslation } from "react-i18next"
import TransferCertificateTag from "./tag"
import TransferCertificateTiruertTag from "./tiruert-tag"
import { ElecCancelTransferButton } from "./cancel"
import { RejectTransfer } from "./reject"
import Portal, { usePortal } from "common/components/portal"
import { AcceptTransfer } from "./accept"
import Alert from "common/components/alert"
import { useLocation, useNavigate } from "react-router-dom"
import { useHashMatch } from "common/components/hash-route"
import { useQuery } from "common/hooks/async"
import * as apiOperator from "../../api-operator"
import * as apiCPO from "elec/api-cpo"
import { ElecTransferCertificateStatus } from "elec/types-cpo"
import { RoleEnum } from "api-schema"
export interface ElecTransferDetailsDialogProps {
  displayCpo?: boolean
  tiruert?: boolean
}
export const ElecTransferDetailsDialog = ({
  displayCpo,
  tiruert,
}: ElecTransferDetailsDialogProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const portal = usePortal()
  const navigate = useNavigate()
  const location = useLocation()
  const match = useHashMatch("transfer-certificate/:id")

  const api = displayCpo ? apiCPO : apiOperator

  const transferCertificateResponse = useQuery(
    api.getTransferCertificateDetails,
    {
      key: "transfer-certificate-details",
      params: [entity.id, parseInt(match?.params.id || "")],
    }
  )
  const transferCertificate =
    transferCertificateResponse.result?.data.data?.elec_transfer_certificate

  const showRejectModal = () => {
    portal((close) => (
      <RejectTransfer
        transferCertificate={transferCertificate}
        onClose={close}
        onRejected={closeDialog}
      />
    ))
  }

  const showAcceptModal = async () => {
    portal((close) => (
      <AcceptTransfer
        transferCertificate={transferCertificate}
        tiruertChoice={
          transferCertificate?.status === ElecTransferCertificateStatus.Pending
        }
        onClose={close}
        onAccepted={closeDialog}
      />
    ))
  }

  const closeDialog = () => {
    navigate({ search: location.search, hash: "#" })
  }

  return (
    <Portal onClose={closeDialog}>
      <Dialog onClose={closeDialog}>
        <header>
          {!tiruert && transferCertificate && (
            <TransferCertificateTag status={transferCertificate.status} big />
          )}
          {tiruert && transferCertificate && (
            <TransferCertificateTiruertTag
              used_in_tiruert={transferCertificate.used_in_tiruert}
              big
            />
          )}
          <h1>
            {t("Certificat de cession n°{{id}}", {
              id: transferCertificate?.certificate_id || "...",
            })}
          </h1>
        </header>

        <main>
          <section
            style={{
              display: "grid",
              gridTemplateColumns: tiruert ? "1fr 1fr" : "1fr",
              gap: "1rem",
            }}
          >
            <TextInput
              readOnly
              label={t("Date d'émission")}
              value={
                transferCertificate &&
                formatDate(transferCertificate.transfer_date)
              }
            />

            {tiruert && (
              <TextInput
                readOnly
                label={t("MWh")}
                value={transferCertificate?.energy_amount + " MWh"}
              />
            )}

            <TextInput
              readOnly
              label={t("Aménageur")}
              value={transferCertificate?.supplier.name}
            />

            <TextInput
              readOnly
              label={t("Redevable")}
              value={transferCertificate?.client.name}
            />

            {!tiruert && (
              <TextInput
                readOnly
                label={t("MWh")}
                value={transferCertificate?.energy_amount + " MWh"}
              />
            )}

            {tiruert && (
              <TextInput
                readOnly
                label={t("Déclaration TIRUERT")}
                value={transferCertificate?.used_in_tiruert ? "Oui" : "Non"}
              />
            )}

            {tiruert && (
              <TextInput
                readOnly
                label={t("Date de déclaration TIRUERT")}
                value={formatDate(
                  transferCertificate?.consumption_date || null
                )}
              />
            )}

            {transferCertificate?.status ===
              ElecTransferCertificateStatus.Accepted &&
              entity.id === transferCertificate?.client.id && (
                <Alert
                  variant="info"
                  icon={Message}
                  style={{ gridColumn: "span 2" }}
                >
                  {t(
                    "L'identifiant est à reporter sur le certificat d'acquisition à intégrer dans votre comptabilité matière pour le compte des douanes."
                  )}
                </Alert>
              )}
            {transferCertificate?.status ===
              ElecTransferCertificateStatus.Rejected && (
              <Alert
                variant="info"
                icon={Message}
                style={{ gridColumn: "span 2" }}
              >
                {transferCertificate.comment}
              </Alert>
            )}
          </section>
        </main>

        <footer>
          {(transferCertificate?.client.id === entity.id || true) && (
            <>
              {!entity.hasRights(RoleEnum.Auditor, RoleEnum.ReadOnly) &&
                transferCertificate &&
                (transferCertificate?.status ===
                  ElecTransferCertificateStatus.Pending ||
                  !transferCertificate?.used_in_tiruert) && (
                  <Button
                    icon={Check}
                    label={t(
                      transferCertificate.status ===
                        ElecTransferCertificateStatus.Pending
                        ? "Accepter"
                        : "Déclarer"
                    )}
                    variant="success"
                    action={showAcceptModal}
                  />
                )}

              {transferCertificate?.status ===
                ElecTransferCertificateStatus.Pending && (
                <Button
                  icon={Cross}
                  label={t("Refuser")}
                  variant="danger"
                  action={showRejectModal}
                />
              )}
            </>
          )}
          {entity.id === transferCertificate?.supplier.id &&
            transferCertificate?.status !==
              ElecTransferCertificateStatus.Accepted && (
              <ElecCancelTransferButton
                transferCertificate={transferCertificate}
                onClose={closeDialog}
              />
            )}
          <Button icon={Return} label={t("Retour")} action={closeDialog} />
        </footer>
      </Dialog>
    </Portal>
  )
}

export default ElecTransferDetailsDialog
