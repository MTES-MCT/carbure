import useEntity from "carbure/hooks/entity"
import { Button } from "common/components/button"
import { Dialog } from "common/components/dialog"
import { Check, Cross, Return } from "common/components/icons"
import { useNotify, useNotifyError } from "common/components/notifications"
import Portal, { usePortal } from "common/components/portal"
import { formatDate, formatNumber } from "common/utils/formatters"
import { elecChargePointApplication1 } from "elec/__test__/data"
import ApplicationStatus from "elec/components/charge-points/application-status"
import { ElecChargePointsApplicationStatus } from "elec/types"
import { Trans, useTranslation } from "react-i18next"
import ChargePointsApplicationAcceptDialog from "./accept-dialog"
import ChargePointsApplicationRejectDialog from "./reject-dialog"
import { useLocation, useNavigate } from "react-router-dom"
import { useHashMatch } from "common/components/hash-route"
import { useQuery } from "common/hooks/async"
import * as api from "../../api"
import { TextInput } from "common/components/input"
import Form from "common/components/form"

export const ChargingPointsApplicationDetailsDialog = () => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()
  const notifyError = useNotifyError()
  const portal = usePortal()
  const navigate = useNavigate()
  const location = useLocation()

  const match = useHashMatch("application/:id")

  const chargePointApplicationResponse = useQuery(api.getChargePointsApplicationDetails, {
    key: "transfer-certificate-details",
    params: [entity.id, parseInt(match?.params.id!)],
  })
  // const chargePointApplication = chargePointApplicationResponse.result?.data.data?.elec_transfer_certificate
  const chargePointApplication = elecChargePointApplication1 // TEST with data


  const closeDialog = () => {
    navigate({ search: location.search, hash: "#" })
  }

  const rejectApplication = () => {
    portal((close) => (
      <ChargePointsApplicationRejectDialog
        application={chargePointApplication}
        onClose={close}
      />
    ))
  }

  const acceptApplication = () => {
    portal((close) => (
      <ChargePointsApplicationAcceptDialog
        application={chargePointApplication}
        onClose={close}
      />
    ))
  }

  return (
    <Portal onClose={closeDialog}>
      <Dialog onClose={closeDialog} >
        <header>
          <ApplicationStatus status={chargePointApplication.status} big />

          <h1>{t("Inscription de points de recharge")}</h1>
        </header>

        <main>

          <section>
            {/* <TextInput
                readOnly
                label={t("Date d'émission")}
                value={chargePointApplication && formatDate(transferCertificate.transfer_date)}

              />  */}
            <Form
              id="lot-form"
              variant="columns"

            >

              <TextInput
                readOnly
                label={t("Date de la demande")}
                value={formatDate(chargePointApplication.application_date)}
              />

              <TextInput
                readOnly
                label={t("Aménageur")}
                value={chargePointApplication?.cpo.name}

              />

              <TextInput
                readOnly
                label={t("Puissance cumulée (kW)")}
                value={formatNumber(Math.round(chargePointApplication.power_total))}

              />

              <TextInput
                readOnly
                label={t("Points de recharge")}
                value={formatNumber(chargePointApplication.charge_point_count)}
              />


            </Form>

            {/* 

              {/* {transferCertificate?.status === ElecTransferCertificateStatus.Rejected &&
              <Alert variant="info" icon={Message}>
                {transferCertificate.comment}
              </Alert>
            } */}
          </section>

          <section>
            {!entity.isAdmin && chargePointApplication.status === ElecChargePointsApplicationStatus.Pending && (
              <p><i>
                {t("En attente de validation de la DGEC.")}
              </i></p>
            )}
          </section>
        </main>

        <footer>
          {/* 
          {entity.isAdmin && chargePointApplication.status === ElecChargePointsApplicationStatus.Pending && (
            <>
              <Button icon={Check} label={t("Valider l'inscription")} variant="success" action={acceptApplication} />
              <Button icon={Cross} label={t("Refuser")} variant="danger" action={rejectApplication} />
            </>
          )} */}
          <Button icon={Return} label={t("Fermer")} action={closeDialog} asideX />
        </footer>

      </Dialog>
    </Portal >
  )
}




export default ChargingPointsApplicationDetailsDialog
