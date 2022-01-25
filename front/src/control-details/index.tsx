import { useNavigate, useLocation, useParams } from "react-router-dom"
import { useTranslation } from "react-i18next"
import * as api from "./api"
import { useQuery } from "common-v2/hooks/async"
import { useStatus } from "controls/components/status"
import useEntity from "carbure/hooks/entity"
import { LoaderOverlay } from "common-v2/components/scaffold"
import Dialog from "common-v2/components/dialog"
import Button from "common-v2/components/button"
import { Alarm, Return } from "common-v2/components/icons"
import LotForm, { useLotForm } from "lot-add/components/lot-form"
import LotTag from "transactions/components/lots/lot-tag"
import Comments from "lot-details/components/comments"
import {
  BlockingAnomalies,
  separateAnomalies,
} from "lot-details/components/anomalies"
import { getLotChanges, LotHistory } from "lot-details/components/history"
import { isExpiring } from "common-v2/utils/deadline"
import Alert from "common-v2/components/alert"
import NavigationButtons from "lot-details/components/navigation"
import LotTraceability, {
  hasTraceability,
} from "lot-details/components/lot-traceability"
import { WarningAnomalies } from "./components/warnings"
import { invalidate } from "common-v2/hooks/invalidate"

export interface LotDetailsProps {
  neighbors: number[]
}

export const LotDetails = ({ neighbors }: LotDetailsProps) => {
  const { t } = useTranslation()

  const navigate = useNavigate()
  const location = useLocation()

  const entity = useEntity()
  const status = useStatus()
  const params = useParams<"id">()

  const lot = useQuery(api.getLotDetails, {
    key: "control-details",
    params: [entity.id, parseInt(params.id!)],
  })

  const lotData = lot.result?.data.data
  const creator = lotData?.lot.added_by
  const comments = lotData?.comments ?? []
  const changes = getLotChanges(lotData?.updates)
  const [errors, warnings] = separateAnomalies(lotData?.errors ?? [])

  const form = useLotForm(lotData?.lot, errors)

  const expiring = isExpiring(lotData?.lot)

  const closeDialog = () => {
    invalidate("controls")
    navigate({
      pathname: `../${status}`,
      search: location.search,
    })
  }

  return (
    <Dialog onClose={closeDialog}>
      <header>
        {lotData && <LotTag big lot={lotData.lot} />}
        <h1>
          {t("Détails du lot")} #{lotData?.lot.carbure_id || lotData?.lot.id}
          {" · "}
          {creator?.name ?? "N/A"}
        </h1>

        {expiring && (
          <Alert
            icon={Alarm}
            variant="warning"
            label={t("À valider avant la fin du mois")}
          />
        )}
      </header>

      <main>
        <section>
          <LotForm readOnly form={form} />
        </section>

        {errors.length > 0 && (
          <section>
            <BlockingAnomalies anomalies={errors} />
          </section>
        )}

        {warnings.length > 0 && (
          <section>
            <WarningAnomalies lot={lotData!.lot} anomalies={warnings} />
          </section>
        )}

        {lotData && comments.length > 0 && (
          <section>
            <Comments readOnly lot={lotData?.lot} comments={comments} />
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
        <NavigationButtons neighbors={neighbors} root={`../${status}`} />
        <Button icon={Return} label={t("Retour")} action={closeDialog} />
      </footer>

      {lot.loading && <LoaderOverlay />}
    </Dialog>
  )
}

export default LotDetails
