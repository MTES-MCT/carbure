import { useNavigate, useLocation, useParams } from "react-router-dom"
import { useTranslation } from "react-i18next"
import * as api from "./api"
import { CorrectionStatus, Lot, LotStatus } from "transactions-v2/types"
import { useQuery, useMutation } from "common-v2/hooks/async"
import { useNotify } from "common-v2/components/notifications"
import { useStatus } from "transactions-v2/components/status"
import useEntity from "carbure/hooks/entity"
import { LoaderOverlay } from "common-v2/components/scaffold"
import Dialog from "common-v2/components/dialog"
import Button from "common-v2/components/button"
import { Alarm, Return, Save } from "common-v2/components/icons"
import LotForm from "lot-add/components/lot-form"
import LotTag from "transactions-v2/components/lots/lot-tag"
import Comments from "./components/comments"
import {
  BlockingAnomalies,
  separateAnomalies,
  WarningAnomalies,
} from "./components/anomalies"
import { getLotChanges, LotHistory } from "./components/history"
import { isExpiring } from "common-v2/utils/deadline"
import Alert from "common-v2/components/alert"
import NavigationButtons from "./components/navigation"
import LotActions from "./components/actions"
import { Entity } from "carbure/types"
import LotTraceability, { hasTraceability } from "./components/lot-traceability"

export interface LotDetailsProps {
  neighbors: number[]
}

export const LotDetails = ({ neighbors }: LotDetailsProps) => {
  const { t } = useTranslation()
  const notify = useNotify()

  const navigate = useNavigate()
  const location = useLocation()

  const entity = useEntity()
  const status = useStatus()
  const params = useParams<"id">()

  const lot = useQuery(api.getLotDetails, {
    key: "lot-details",
    params: [entity.id, parseInt(params.id!)],
  })

  const updateLot = useMutation(api.updateLot, {
    invalidates: ["lots", "lot-details", "snapshot"],

    onSuccess: () => {
      notify(t("Le lot a bien été mis à jour"), { variant: "success" })
    },

    onError: () => {
      notify(t("La mise à jour du lot a échoué"), { variant: "danger" })
    },
  })

  const lotData = lot.result?.data.data
  const comments = lotData?.comments ?? []
  const changes = getLotChanges(lotData?.updates)
  const [errors, warnings] = separateAnomalies(lotData?.errors ?? [])

  const editable = isEditable(lotData?.lot, entity)
  const expiring = isExpiring(lotData?.lot)

  const closeDialog = () =>
    navigate({
      pathname: `../${status}`,
      search: location.search,
    })

  return (
    <Dialog onClose={closeDialog}>
      <header>
        {lotData && <LotTag big lot={lotData.lot} />}
        <h1>
          {t("Détails du lot")} #{lotData?.lot.carbure_id || lotData?.lot.id}
        </h1>
      </header>

      <main>
        <section>
          <LotForm
            readOnly={!editable}
            lot={lotData?.lot}
            errors={errors}
            onSubmit={(form) => updateLot.execute(entity.id, form!)}
          />
        </section>

        {errors.length > 0 && (
          <section>
            <BlockingAnomalies anomalies={errors} />
          </section>
        )}

        {warnings.length > 0 && (
          <section>
            <WarningAnomalies anomalies={warnings} />
          </section>
        )}

        {lotData && comments.length > 0 && (
          <section>
            <Comments lot={lotData?.lot} comments={comments} />
          </section>
        )}

        {hasTraceability(lotData) && (
          <section>
            <LotTraceability details={lotData} />
          </section>
        )}

        {changes.length > 0 && (
          <section>
            <LotHistory changes={changes} />
          </section>
        )}
      </main>

      <footer>
        {editable && (
          <Button
            loading={updateLot.loading}
            variant="primary"
            icon={Save}
            submit="lot-form"
            label={t("Sauvegarder")}
          />
        )}

        {lotData && <LotActions lot={lotData.lot} />}

        {expiring && (
          <Alert
            icon={Alarm}
            variant="warning"
            label={t("À valider avant la fin du mois")}
          />
        )}

        <NavigationButtons neighbors={neighbors} root={`../${status}`} />
        <Button icon={Return} label={t("Retour")} action={closeDialog} />
      </footer>

      {lot.loading && <LoaderOverlay />}
    </Dialog>
  )
}

function isEditable(lot: Lot | undefined, entity: Entity) {
  if (lot === undefined) return false

  const isSupplier = lot.carbure_supplier?.id === entity.id

  return (
    [LotStatus.Draft, LotStatus.Rejected].includes(lot.lot_status) ||
    (isSupplier && lot.correction_status === CorrectionStatus.InCorrection)
  )
}

export default LotDetails
