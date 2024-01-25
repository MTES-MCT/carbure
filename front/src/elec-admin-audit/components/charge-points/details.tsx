import useEntity from "carbure/hooks/entity"
import { Button, MailTo } from "common/components/button"
import { Dialog } from "common/components/dialog"
import { Check, Cross, Download, Return, Send } from "common/components/icons"
import { useNotify, useNotifyError } from "common/components/notifications"
import Portal, { usePortal } from "common/components/portal"
import { formatDate, formatNumber } from "common/utils/formatters"
import { elecChargePointApplication1, elecChargePointApplication4 } from "elec/__test__/data"
import ApplicationStatus from "elec/components/charge-points/application-status"
import { ElecChargePointsApplicationStatus } from "elec/types"
import { Trans, useTranslation } from "react-i18next"
import ChargePointsApplicationAcceptDialog from "./accept-dialog"
import ChargePointsApplicationRejectDialog from "./reject-dialog"
import { useLocation, useNavigate } from "react-router-dom"
import { useHashMatch } from "common/components/hash-route"
import { useMutation, useQuery } from "common/hooks/async"
import * as api from "../../api"
import { TextInput } from "common/components/input"
import Form from "common/components/form"
import Alert from "common/components/alert"

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
    key: "audit-charge-points-application-details",
    params: [entity.id, parseInt(match?.params.id!)],
  })
  // const chargePointApplication = chargePointApplicationResponse.result?.data.data?.elec_transfer_certificate
  const chargePointApplication = elecChargePointApplication1 // TEST with data

  const startChargePointsApplicationAuditResponse = useMutation(api.startChargePointsApplicationAudit, {
    invalidates: ["audit-charge-points-application-details"],
    onSuccess() {
      notify(t("L'audit de l'inscription des {{count}} points de recharge a bien été initié.", { count: chargePointApplication.charge_point_count }), { variant: "success" })
    },
    onError(err) {
      notifyError(err, t("Impossible d'initier l'audit de l'inscription des points de recharge"))
    },
  })

  const closeDialog = () => {
    navigate({ search: location.search, hash: "#" })
  }




  const startAudit = () => {
    startChargePointsApplicationAuditResponse.execute(entity.id, chargePointApplication.id)
  }

  const showEmailDialog = () => {
    portal((close) => <MailToDialog onClose={() => { close(); }} />)

  }

  const downloadSample = () => {
    api.downloadChargePointsSample(entity.id, chargePointApplication.id)
  }

  const acceptApplication = (force: boolean = false) => {
    portal((close) => (
      <ChargePointsApplicationAcceptDialog
        application={chargePointApplication}
        onClose={close}
        forceValidation={force}
      />
    ))
  }

  const rejectApplication = (force: boolean = false) => {
    portal((close) => (
      <ChargePointsApplicationRejectDialog
        application={chargePointApplication}
        onClose={close}
        forceRejection={force}

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
          {chargePointApplication.status === ElecChargePointsApplicationStatus.AuditInProgress && (

            <section>
              <Alert variant="info" >
                <p>
                  <Send />
                  <Trans>
                    Action requise par l’administrateur pour poursuivre l’audit de l’inscription des points de recharge :
                  </Trans>
                </p>
                <ul>
                  <li><Trans>Joindre le fichier téléchargé comportant l'échantillon des points de recharge à auditer</Trans></li>
                  <li><Trans>Transmettre cet e-mail à l'aménageur</Trans></li>
                </ul>

              </Alert>
            </section>
          )}
        </main>

        <footer>

          {chargePointApplication.status === ElecChargePointsApplicationStatus.Pending && (
            <>
              <Button icon={Send} label={t("Commencer l'audit")} variant="primary" action={startAudit} />
              <Button icon={Check} label={t("Valider sans auditer")} variant="success" action={() => acceptApplication(true)} />
              <Button icon={Cross} label={t("Refuser sans auditer")} variant="danger" action={() => rejectApplication(true)} />
            </>
          )}

          {chargePointApplication.status === ElecChargePointsApplicationStatus.AuditInProgress && (
            <>

              <Button icon={Download} label={t("Télécharger l’échantillon")} variant="secondary" action={downloadSample} />
              <Button icon={Send} label={t("Générer l’email")} variant="secondary" action={showEmailDialog} />
              <Button icon={Check} label={t("Valide")} variant="success" action={acceptApplication} />
              <Button icon={Cross} label={t("Refuser")} variant="danger" action={rejectApplication} />
            </>
          )}
          <Button icon={Return} label={t("Fermer")} action={closeDialog} asideX />
        </footer>

      </Dialog>
    </Portal >
  )
}



export const MailToDialog = ({
  onClose,
}: { onClose: () => void }) => {
  const { t } = useTranslation()
  const entity = useEntity()

  const bodyMessage = `Mesdames%2C%20Messieurs%2C%0D%0A%0D%0AJe%20vous%20faire%20parvenir%20le%20dossier%20de%20demande%20de%20reconnaissance%20au%20Double%20Comptage%20pour%20notre%20soci%C3%A9t%C3%A9.%0D%0AJ'ai%20joint%20%20%3A%0D%0A-%20le%20fichier%20Excel%20apr%C3%A8s%20validation%20avec%20la%20plateforme%20CarbuRe%0D%0A%0D%0ABien%20cordialement`

  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>{t("Envoi de la demande d'audit")}</h1>
      </header>

      <main>
        <section>
          <p style={{ textAlign: 'left' }}>
            {t("Transmettre cet e-mail à l’aménageur")}
          </p>

          <MailTo user="carbure" host="beta.gouv.fr"
            subject={`[CarbuRe - Double comptage] Demande de ${entity.name}`}
            body={bodyMessage}
          >
            <Trans>Génerer l'email à envoyer</Trans>
          </MailTo>

        </section>
      </main>

      <footer>
        <Button icon={Return} label={t("Fermer")} action={onClose} asideX />
      </footer>

    </Dialog>
  )
}



export default ChargingPointsApplicationDetailsDialog
