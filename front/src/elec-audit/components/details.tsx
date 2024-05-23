import useEntity from "carbure/hooks/entity"
import { Dialog } from "common/components/dialog"
import { useHashMatch } from "common/components/hash-route"
import Portal, { usePortal } from "common/components/portal"
import { LoaderOverlay } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import ApplicationStatus from "elec/components/application-status"
import { ElecAuditApplicationStatus } from "elec/types"
import { Trans, useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import * as api from "elec-audit/api"
import { Divider } from "common/components/divider"
import SampleSummary from "elec-audit-admin/components/charge-points/details-sample-summary"
import ChargePointsSampleMap from "elec-audit-admin/components/charge-points/sample-map"
import Button from "common/components/button"
import { Download, Edit } from "common/components/icons"
import ApplicationSummary from "./details-application-summary"
import Alert from "common/components/alert"



export const ChargingPointsApplicationDetailsDialog = () => {
  const { t } = useTranslation()
  const entity = useEntity()
  const portal = usePortal()
  const navigate = useNavigate()
  const location = useLocation()
  const match = useHashMatch("application/:id")

  const chargePointApplicationResponse = useQuery(api.getChargePointsApplicationDetails, {
    key: "audit-charge-points-application-details",
    params: [entity.id, parseInt(match?.params.id!)],
  })
  const chargePointApplication = chargePointApplicationResponse.result?.data.data


  const closeDialog = () => {
    navigate({ search: location.search, hash: "#" })
  }


  const downloadSample = async () => {
    return api.downloadChargePointsSample(entity.id, chargePointApplication!.id)
  }

  return (
    <Portal onClose={closeDialog}>
      <Dialog onClose={closeDialog} >
        <header>
          <ApplicationStatus status={chargePointApplication?.status} big />
          <h1>{t("Inscription de points de recharge")}</h1>
        </header>

        <main>
          <section>
            <ApplicationSummary application={chargePointApplication} />
          </section>
          <Divider />
          {chargePointApplication?.sample && (
            <section>
              <ChargePointsSampleMap chargePoints={chargePointApplication?.sample?.charge_points} />
            </section>
          )}
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
          <Button icon={Download} label={t("Télécharger les points à auditer")} variant="secondary" action={downloadSample} style={{ width: "min-content" }} />
        </footer>
        {chargePointApplicationResponse.loading && <LoaderOverlay />}
      </Dialog>
    </Portal >
  )
}




export default ChargingPointsApplicationDetailsDialog
