import Alert from "common/components/alert"
import Button from "common/components/button"
import { Download, Edit } from "common/components/icons"
import ChargePointsSampleMap from "elec-audit-admin/components/sample/sample-map"
import { ElecAuditorApplicationDetails } from "elec-auditor/types"
import { Trans, useTranslation } from "react-i18next"


const DownloadSampleSection = ({ application, header, onDownloadSample }: {
  application: ElecAuditorApplicationDetails,
  header: JSX.Element,
  onDownloadSample: () => void
}) => {
  const { t } = useTranslation()

  return <>
    <main>
      {header}
      {application?.sample ? (
        <section>
          <ChargePointsSampleMap chargePoints={application?.sample?.charge_points} />
        </section>
      ) : <p><Trans>Le fichier CSV listant l'intégralité des points de recharge à auditer vous a été envoyé par email par l'aménageur.</Trans></p>
      }
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
      <Button icon={Download} label={t("Télécharger les points à auditer")} variant="primary" action={onDownloadSample} />

    </footer>
  </>
}

export default DownloadSampleSection