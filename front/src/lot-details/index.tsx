import { useNavigate, useLocation, useParams } from "react-router-dom"
import { useTranslation } from "react-i18next"
import * as api from "./api"
import { CorrectionStatus, Lot, LotStatus } from "transactions-v2/types"
import { useQuery } from "common-v2/hooks/async"
import { useStatus } from "transactions-v2/components/status"
import useEntity from "carbure/hooks/entity"
import { LoaderOverlay } from "common-v2/components/scaffold"
import Dialog from "common-v2/components/dialog"
import Button from "common-v2/components/button"
import { Return, Save } from "common-v2/components/icons"
import LotForm from "lot-add/components/lot-form"
import LotTag from "transactions-v2/components/lots/lot-tag"
import Comments from "./components/comments"
import {
  BlockingAnomalies,
  separateAnomalies,
  WarningAnomalies,
} from "./components/anomalies"
import { getLotUpdates, History } from "./components/history"

export const LotDetails = () => {
  const { t } = useTranslation()

  const navigate = useNavigate()
  const location = useLocation()

  const entity = useEntity()
  const status = useStatus()
  const params = useParams<"id">()

  const lot = useQuery(api.getLotDetails, {
    key: "lot-details",
    params: [entity.id, parseInt(params.id!)],
  })

  const lotData = lot.result?.data.data
  const editable = isEditable(lotData?.lot)
  const comments = lotData?.comments ?? []
  const updates = getLotUpdates(lotData?.updates)
  const [errors, warnings] = separateAnomalies(lotData?.errors ?? [])

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
            onSubmit={(form) => console.log(form)}
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

        {comments.length > 0 && (
          <section>
            <Comments comments={comments} />
          </section>
        )}

        {updates.length > 0 && (
          <section>
            <History updates={updates} />
          </section>
        )}
      </main>

      <footer>
        {editable && (
          <Button
            variant="primary"
            icon={Save}
            submit="lot-form"
            label={t("Sauvegarder")}
          />
        )}
        <Button asideX icon={Return} label={t("Retour")} action={closeDialog} />
      </footer>

      {lot.loading && <LoaderOverlay />}
    </Dialog>
  )
}

function isEditable(lot: Lot | undefined) {
  if (lot === undefined) return false

  return (
    [LotStatus.Draft, LotStatus.Rejected].includes(lot.lot_status) ||
    lot.correction_status === CorrectionStatus.InCorrection
  )
}

export default LotDetails
