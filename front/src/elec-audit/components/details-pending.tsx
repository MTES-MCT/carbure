import useEntity from "carbure/hooks/entity"
import Alert from "common/components/alert"
import Button from "common/components/button"
import { Dialog } from "common/components/dialog"
import { Divider } from "common/components/divider"
import { useHashMatch } from "common/components/hash-route"
import { Download, Edit, Send } from "common/components/icons"
import Portal from "common/components/portal"
import { LoaderOverlay } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import ChargePointsSampleMap from "elec-audit-admin/components/sample/sample-map"
import * as api from "elec-audit/api"
import ApplicationStatus from "elec/components/application-status"
import { Trans, useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import ApplicationSummary from "./details-application-summary"
import { ElecChargePointsApplication, ElecMeterReadingsApplication } from "elec/types"
import { ElecAuditApplicationDetails } from "elec-audit/types"


interface ElecAuditDetailsPendingProps {
  audit: ElecAuditApplicationDetails
}
export const ElecAuditDetailsPending = ({
  audit
}: ElecAuditDetailsPendingProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const navigate = useNavigate()
  const location = useLocation()
  const match = useHashMatch("application/:id")



  // const closeDialog = () => {
  //   navigate({ search: location.search, hash: "#" })
  // }


  // const downloadSample = async () => {
  //   return api.downloadChargePointsSample(entity.id, application!.id)
  // }

  return (
    <>

      {/* <main>
        <section>
          <ApplicationSummary application={application} />
        </section>
        <Divider />
        {chargePointApplication?.sample ? (
          <section>
            <ChargePointsSampleMap chargePoints={chargePointApplication?.sample?.charge_points} />
            <Button icon={Download} label={t("Télécharger les points à auditer")} variant="secondary" action={downloadSample} style={{ width: "min-content" }} />
          </section>
        ) : <p><Trans>Le fichier CSV listant l'intégralité des points de recharge à auditer vous a été envoyé par email par l'aménageur.</Trans></p>}

        <section>

          <Alert icon={Edit} variant="info" label={t("Précision sur les champs du tableau à remplir :")} >
            <p>
              <strong><Trans>Infrastructure de recharge installée à la localisation renseignée :</Trans></strong>
              <Trans>l'inspecteur confirme avoir trouvé le point de recharge à la localisation indiquée. Écrire "OUI" ou "NON" et passer aux étapes suivantes si l'infrastructure a été localisée ;</Trans>
            </p>

            <p>
              <strong><Trans>Identifiant renseigné visible à proximité immédiate de l'infrastructure :</Trans></strong>
              <Trans>l'inspecteur précise si l'identifiant renseigné est visible sur ou a proximité immédiate du point de recharge. La non visibilité de cet identifiant ne doit pas faire obstacle à la suite du contrôle si l'inspecteur est en mesure d'identifier les points de recharge par d'autres moyens (indication de l'aménageur/de l'opérateur par exemple). Écrire "OUI" ou "NON" ;</Trans>
            </p>

            <p>
              <strong><Trans>Point de contrôle type de courant :</Trans></strong>
              <Trans>l'inspecteur vérifie le type de courant délivré par le point de recharge (à partir du connecteur) et l'indique en écrivant "CC" ou "CA" </Trans>
            </p>

            <p>
              <strong><Trans>Numéro du certificat d'examen du type si différent :</Trans></strong>
              <Trans>l'inspecteur vérifie la correspondance entre le certificat d'examen du type déclaré par le demandeur (rappelé dans la colonne "no_mid") et celui du compteur installé dans le point de recharge. Il laisse la case vide en cas de correspondance ou indique le numéro du compteur installé si une différence est constatée ;</Trans>
            </p>

            <p>
              <strong><Trans>Date du relevé par l'intervenant :</Trans></strong>
              <Trans>la date de passage de l'inspecteur au format JJ/MM/AAAA ;</Trans>
            </p>
            <p>
              <strong><Trans>Énergie active totale relevée :</Trans></strong>
              <Trans>le relevé en kWh, au format XXXX,XX ;</Trans>
            </p>
            <p>
              <strong><Trans>Limite dans la mission de contrôle :</Trans></strong>
              <Trans>champ libre permettant d'indiquer tout circonstance ayant fait obstacle à la mission de contrôle.</Trans>
            </p>
          </Alert>
        </section>
      </main>

      <footer>
        <MailtoButton cpoName={chargePointApplication?.cpo.name} auditorName={entity?.name} chargePointCount={chargePointApplication?.charge_point_count} />
      </footer> */}
    </>
  )
}


interface MailtoButtonProps {
  cpoName?: string
  auditorName?: string
  chargePointCount?: number

}



export default ElecAuditDetailsPendingProps
