import useEntity from "carbure/hooks/entity"
import { Button } from "common/components/button"
import { Dialog } from "common/components/dialog"
import { Check, Cross, Download, Return } from "common/components/icons"
import { useNotify, useNotifyError } from "common/components/notifications"
import { useMutation, useQuery } from "common/hooks/async"
import { formatDate } from "common/utils/formatters"
import * as api from "elec-admin/api"
import { Trans, useTranslation } from "react-i18next"
import ChargePointsApplicationAcceptDialog from "./accept-dialog"
import { usePortal } from "common/components/portal"
import ChargePointsApplicationRejectDialog from "./reject-dialog"
import ApplicationStatus from "elec/components/charge-points/application-status"
import { ElecChargePointsApplication, ElecChargePointsApplicationStatus } from "elec/types"
export type ApplicationDialogProps = {
  application: ElecChargePointsApplication
  onClose: () => void
  companyId: number
}

export const ChargingPointsApplicationDetailsDialog = ({
  application,
  onClose,
  companyId,
}: ApplicationDialogProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()
  const notifyError = useNotifyError()
  const portal = usePortal()

  // const match = useHashMatch("transfer-certificate/:id")

  // const transferCertificateResponse = useQuery(api.getTransferCertificateDetails, {
  //   key: "transfer-certificate-details",
  //   params: [entity.id, parseInt(match?.params.id!)],
  // })
  // const transferCertificate = transferCertificateResponse.result?.data.data?.elec_transfer_certificate

  const rejectApplication = () => {
    portal((close) => (
      <ChargePointsApplicationRejectDialog
        application={application}
        companyId={companyId}
        onClose={close}
      />
    ))
  }

  const acceptApplication = () => {
    portal((close) => (
      <ChargePointsApplicationAcceptDialog
        application={application}
        companyId={companyId}
        onClose={close}
      />
    ))
  }

  return (
    <Dialog onClose={onClose}>
      <header>
        <ApplicationStatus status={application.status} big />

        <h1>{t("Inscription de points de recharge")}</h1>
      </header>

      <main>

        <section>
          <p style={{ textAlign: 'left' }}>
            <Trans
              values={{
                applicationDate: formatDate(application.application_date),
              }}
              count={application.charge_point_count}
              defaults="La demande d'inscription a été faite le <b>{{applicationDate}}</b> pour <b>{{count}} points de recharge</b>." />
          </p>

          <section>
            {/* <TextInput
              readOnly
              label={t("Date d'émission")}
              value={transferCertificate && formatDate(transferCertificate.transfer_date)}

            /> */}

            {/* <TextInput
              readOnly
              label={t("Aménageur")}
              value={transferCertificate?.supplier.name}

            />
            <TextInput
              readOnly
              label={t("Redevable")}
              value={transferCertificate?.client.name}

            />


            <TextInput
              readOnly
              label={t("Puissance cumulée (Mwh)")}
              value={transferCertificate?.energy_amount}

            /> */}

            {/* {transferCertificate?.status === ElecTransferCertificateStatus.Rejected &&
              <Alert variant="info" icon={Message}>
                {transferCertificate.comment}
              </Alert>
            } */}
          </section>


          {!entity.isAdmin && application.status === ElecChargePointsApplicationStatus.Pending && (
            <p><i>
              {t("En attente de validation de la DGEC.")}
            </i></p>
          )}
        </section>
      </main>

      <footer>

        {entity.isAdmin && application.status === ElecChargePointsApplicationStatus.Pending && (
          <>
            <Button icon={Check} label={t("Valider l'inscription")} variant="success" action={acceptApplication} />
            <Button icon={Cross} label={t("Refuser")} variant="danger" action={rejectApplication} />
          </>
        )}
        <Button icon={Return} label={t("Fermer")} action={onClose} asideX />
      </footer>

    </Dialog>
  )
}




export default ChargingPointsApplicationDetailsDialog
