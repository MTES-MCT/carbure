import useEntity from "carbure/hooks/entity"
import { EntityPreview } from "carbure/types"
import Alert from "common/components/alert"
import { Button } from "common/components/button"
import { Dialog } from "common/components/dialog"
import Form from "common/components/form"
import { useHashMatch } from "common/components/hash-route"
import { Check, Cross, Download, Return, Send } from "common/components/icons"
import { TextInput } from "common/components/input"
import { useNotify, useNotifyError } from "common/components/notifications"
import Portal, { usePortal } from "common/components/portal"
import { LoaderOverlay } from "common/components/scaffold"
import { useMutation, useQuery } from "common/hooks/async"
import { formatDate, formatNumber } from "common/utils/formatters"
import ApplicationStatus from "elec/components/application-status"
import { ElecAuditApplicationStatus } from "elec/types"
import { Trans, useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import * as api from "../../api"
import MeterReadingsApplicationAcceptDialog from "./accept-dialog"
import MeterReadingsApplicationRejectDialog from "./reject-dialog"
import ApplicationSummary from "./details-application-summary"

export const MeterReadingsApplicationDetailsDialog = () => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()
  const notifyError = useNotifyError()
  const portal = usePortal()
  const navigate = useNavigate()
  const location = useLocation()
  const match = useHashMatch("application/:id")

  const meterReadingsApplicationResponse = useQuery(api.getMeterReadingsApplicationDetails, {
    key: "audit-meter-readings-application-details",
    params: [entity.id, parseInt(match?.params.id!)],
  })
  const meterReadingsApplication = meterReadingsApplicationResponse.result?.data.data
  // const meterReadingsApplication = elecMeterReadingApplication1Details // TEST with data


  const startMeterReadingsApplicationAuditResponse = useMutation(api.startMeterReadingsApplicationAudit, {
    invalidates: ["audit-meter-readings-application-details", "audit-meter-readings-applications"],
    onSuccess() {
      notify(t("L'audit des relevés des {{count}} points de recharge a bien été initié.", { count: meterReadingsApplication?.charge_point_count }), { variant: "success" })
    },
    onError(err) {
      notifyError(err, t("Impossible d'initier l'audit des relevés des points de recharge"))
    },
  })

  const closeDialog = () => {
    navigate({ search: location.search, hash: "#" })
  }

  const startAudit = () => {
    if (!meterReadingsApplication) return
    startMeterReadingsApplicationAuditResponse.execute(entity.id, meterReadingsApplication.id)
  }

  const acceptApplication = (force: boolean = false) => {
    if (!meterReadingsApplication) return
    portal((close) => (
      <MeterReadingsApplicationAcceptDialog
        application={meterReadingsApplication}
        onClose={close}
        forceValidation={force}
        onValidated={closeDialog}
      />
    ))
  }

  const rejectApplication = (force: boolean = false) => {
    if (!meterReadingsApplication) return
    portal((close) => (
      <MeterReadingsApplicationRejectDialog
        application={meterReadingsApplication}
        onClose={close}
        forceRejection={force}
        onRejected={closeDialog}

      />
    ))
  }

  const downloadSample = async () => {
    if (!meterReadingsApplication) return
    return api.downloadMeterReadingsApplication(entity.id, meterReadingsApplication.id, true)
  }

  return (
    <Portal onClose={closeDialog}>
      <Dialog onClose={closeDialog} >
        <header>
          <ApplicationStatus status={meterReadingsApplication?.status} big />

          <h1>{t("Relevés T{{quarter}} {{year}} - {{cpo}}", {
            quarter: meterReadingsApplication?.quarter,
            year: meterReadingsApplication?.year,
            cpo: meterReadingsApplication?.cpo.name
          })}</h1>

        </header>

        <main>

          <section>
            <ApplicationSummary application={meterReadingsApplication} />
          </section>

          <section>
            {!entity.isAdmin && meterReadingsApplication?.status === ElecAuditApplicationStatus.Pending && (
              <p><i>
                {t("En attente de validation de la DGEC.")}
              </i></p>
            )}
          </section>
          {meterReadingsApplication?.status === ElecAuditApplicationStatus.AuditInProgress && (

            <section>
              <Alert variant="info" style={{ flexDirection: "column" }} >
                <p>
                  <Send />
                  <Trans>
                    Action requise par l'administrateur pour poursuivre l'audit de ces relevés trimestriels :
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

          {meterReadingsApplication?.status === ElecAuditApplicationStatus.Pending && (
            <>
              <Button icon={Check} label={t("Valider sans auditer")} variant="success" action={() => acceptApplication(true)} />
              <Button icon={Cross} label={t("Refuser sans auditer")} variant="danger" action={() => rejectApplication(true)} />
            </>
          )}

          {meterReadingsApplication?.status === ElecAuditApplicationStatus.AuditInProgress && (
            <>
              <MailtoButton cpo={meterReadingsApplication.cpo} quarter={meterReadingsApplication.quarter} year={meterReadingsApplication.year} emailContacts={meterReadingsApplication.email_contacts} />
              <Button icon={Download} label={t("Télécharger l'échantillon")} variant="secondary" action={downloadSample} />
              <Button icon={Check} label={t("Valide")} variant="success" action={acceptApplication} />
              <Button icon={Cross} label={t("Refuser")} variant="danger" action={rejectApplication} />
            </>
          )}
          <Button icon={Return} label={t("Fermer")} action={closeDialog} asideX />
        </footer>
        {meterReadingsApplicationResponse.loading && <LoaderOverlay />}
      </Dialog>
    </Portal >
  )
}


const MailtoButton = ({ cpo, quarter, year, emailContacts }: { cpo: EntityPreview, quarter: number, year: number, emailContacts: string[] }) => {
  const { t } = useTranslation()
  const subject = `[CarbuRe - Audit Elec] Demande d'audit ${cpo.name}`
  const bodyIntro = `Bonjour%20${cpo.name}%0D%0A%0D%0A%0D%0AAfin%20de%20valider%20votre%20relev%C3%A9s%20trimestriels%20T${quarter}%20${year}%2C%20un%20audit%20doit%20%C3%AAtre%20men%C3%A9%20sur%20les%20points%20de%20recharge%20s%C3%A9lectionn%C3%A9s%20ci-joints..%0D%0A%0D%0A%0D%0AL'inspecteur%20doit%20remplir%20le%20tableau%20en%20respectant%20le%20format%20suivant%20%3A%0D%0A%0D%0A%0D%0A`
  const bodyContent = `-%20Infrastructure%20de%20recharge%20install%C3%A9e%20%C3%A0%20la%20localisation%20renseign%C3%A9e%20%3A%0D%0Al'inspecteur%20confirme%20avoir%20trouv%C3%A9%20le%20point%20de%20recharge%20%C3%A0%20la%20localisation%20indiqu%C3%A9e.%20%C3%89crire%20%22OUI%22%20ou%20%22NON%22%20et%20passer%20aux%20%C3%A9tapes%20suivantes%20si%20l'infrastructure%20a%20%C3%A9t%C3%A9%20localis%C3%A9e%20%3B%0D%0A%0D%0A-%20Identifiant%20renseign%C3%A9%20visible%20%C3%A0%20proximit%C3%A9%20imm%C3%A9diate%20de%20l'infrastructure%20%3A%0D%0Al'inspecteur%20pr%C3%A9cise%20si%20l'identifiant%20renseign%C3%A9%20est%20visible%20sur%20ou%20a%20proximit%C3%A9%20imm%C3%A9diate%20du%20point%20de%20recharge.%20La%20non%20visibilit%C3%A9%20de%20cet%20identifiant%20ne%20doit%20pas%20faire%20obstacle%20%C3%A0%20la%20suite%20du%20contr%C3%B4le%20si%20l'inspecteur%20est%20en%20mesure%20d'identifier%20les%20points%20de%20recharge%20par%20d'autres%20moyens%20(indication%20de%20l'am%C3%A9nageur%2Fde%20l'op%C3%A9rateur%20par%20exemple).%20%C3%89crire%20%22OUI%22%20ou%20%22NON%22%20%3B%0D%0A%0D%0A-%20Point%20de%20contr%C3%B4le%20type%20de%20courant%20%3A%0D%0Al'inspecteur%20v%C3%A9rifie%20le%20type%20de%20courant%20d%C3%A9livr%C3%A9%20par%20le%20point%20de%20recharge%20(%C3%A0%20partir%20du%20connecteur)%20et%20l'indique%20en%20%C3%A9crivant%20%22CC%22%20ou%20%22CA%22%20%3B%0D%0A%0D%0A-%20Num%C3%A9ro%20du%20certificat%20d'examen%20du%20type%20si%20diff%C3%A9rent%20%3A%0D%0Al'inspecteur%20v%C3%A9rifie%20la%20correspondance%20entre%20le%20certificat%20d'examen%20du%20type%20d%C3%A9clar%C3%A9%20par%20le%20demandeur%20(rappel%C3%A9%20dans%20la%20colonne%20%22no_mid%22)%20et%20celui%20du%20compteur%20install%C3%A9%20dans%20le%20point%20de%20recharge.%20Il%20laisse%20la%20case%20vide%20en%20cas%20de%20correspondance%20ou%20indique%20le%20num%C3%A9ro%20du%20compteur%20install%C3%A9%20si%20une%20diff%C3%A9rence%20est%20constat%C3%A9e%20%3B%0D%0A%0D%0A-%20Date%20du%20relev%C3%A9%20par%20l'intervenant%20%3A%0D%0Ala%20date%20de%20passage%20de%20l'inspecteur%20au%20format%20JJ%2FMM%2FAAAA%20%3B%0D%0AEnergie%20active%20totale%20relev%C3%A9e%20%3A%20le%20relev%C3%A9%20en%20kWh%2C%20au%20format%20XXXX%2CXX%20%3B%0D%0ALimite%20dans%20la%20mission%20de%20contr%C3%B4le%20%3A%20champ%20libre%20permettant%20d'indiquer%20tout%20circonstance%20ayant%20fait%20obstacle%20%C3%A0%20la%20mission%20de%20contr%C3%B4le.%0D%0A%0D%0A`
  const bodyOutro = `Veuillez%20transmettre%20ce%20fichier%20%C3%A0%20votre%20auditeur%20officiel.%20Celui-ci%20pourra%20renvoyer%20le%20r%C3%A9sultat%20de%20cet%20audit%20%C3%A0%20l'adresse%20suivante%20%3A%0D%0A%0D%0Avalorisation-recharge%40developpement-durable.fr%0D%0A%0D%0A%0D%0AMerci%20de%20votre%20compr%C3%A9hension%2C%0D%0A%0D%0ABien%20%C3%A0%20vous%2C%0D%0A%0D%0AL'%C3%A9quipe%20CarbuRe`

  const mailto = `mailto:${emailContacts.join(',')}?subject=${encodeURIComponent(subject)}&body=${bodyIntro + bodyContent + bodyOutro}`

  return <Button icon={Send} label={t("Générer l'email")} variant="secondary" href={mailto} />

}



export default MeterReadingsApplicationDetailsDialog
