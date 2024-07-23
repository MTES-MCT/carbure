import { useNavigate, useLocation } from "react-router-dom"
import { useTranslation } from "react-i18next"
import pickApi from "../api"
import { useQuery } from "common/hooks/async"
import useEntity from "carbure/hooks/entity"
import { LoaderOverlay } from "common/components/scaffold"
import Dialog from "common/components/dialog"
import { Alarm } from "common/components/icons"
import LotForm, { useLotForm } from "lot-add/components/lot-form"
import LotTag from "transactions/components/lots/lot-tag"
import Comments from "transaction-details/components/lots/comments"
import {
  BlockingAnomalies,
  separateAnomalies,
} from "transaction-details/components/lots/anomalies"
import {
  getLotChanges,
  LotHistory,
} from "transaction-details/components/lots/history"
import { isExpiring } from "transactions/utils/deadline"
import Alert from "common/components/alert"
import NavigationButtons from "transaction-details/components/lots/navigation"
import LotTraceability, {
  hasTraceability,
} from "transaction-details/components/lots/lot-traceability"
import { WarningAnomalies } from "./warnings"
import { AlertOneButton } from "controls/actions/alert"
import ControlComments from "./control-comments"
import { formatDate } from "common/utils/formatters"
import Score from "transaction-details/components/score"
import { SetOneConformityButton } from "controls/actions/set-conformity"
import Portal from "common/components/portal"
import { useHashMatch } from "common/components/hash-route"

export interface LotDetailsProps {
  neighbors: number[]
}

export const LotDetails = ({ neighbors }: LotDetailsProps) => {
  const { t } = useTranslation()

  const navigate = useNavigate()
  const location = useLocation()

  const entity = useEntity()
  const match = useHashMatch("lot/:id")

  const api = pickApi(entity)

  const lot = useQuery(api.getLotDetails, {
    key: "control-details",
    params: [entity.id, parseInt(match?.params.id || "")],
  })

  const lotData = lot.result?.data.data
  const creator = lotData?.lot.added_by
  const comments = lotData?.comments ?? []
  const controlComments = lotData?.control_comments ?? []
  const changes = getLotChanges(lotData?.updates)
  const [errors, warnings] = separateAnomalies(lotData?.errors ?? [])

  const form = useLotForm(lotData?.lot, errors)

  const expiring = isExpiring(lotData?.lot)

  const closeDialog = () => {
    navigate({ search: location.search, hash: "#" })
  }

  return (
    <Portal onClose={closeDialog}>
      <Dialog onClose={closeDialog}>
        <header>
          {lotData && <Score big lot={lotData.lot} details={lotData.score} />}
          {lotData && <LotTag big lot={lotData.lot} />}
          <h1>
            {t("Lot")} #{lotData?.lot.carbure_id || lotData?.lot.id}
            {" · "}
            {creator?.name ?? "N/A"}
            {" · "}
            {lotData && formatDate(lotData.lot.created_at)}
          </h1>

          {expiring && (
            <Alert
              icon={Alarm}
              variant="warning"
              label={t("À valider avant la fin du mois")}
              style={{ marginLeft: "auto" }}
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

          {lotData && (
            <section>
              <ControlComments lot={lotData?.lot} comments={controlComments} />
            </section>
          )}

          {hasTraceability(lotData) && (
            <section>
              <LotTraceability
                details={lotData}
                parentLotRoot="../lots"
                parentStockRoot="../stocks"
                childLotRoot="../lots"
                childStockRoot="../stocks"
              />
            </section>
          )}

          {changes.length > 0 && (
            <section>
              <LotHistory changes={changes} />
            </section>
          )}
        </main>

        <footer>
          {lotData && <AlertOneButton lot={lotData.lot} />}
          {lotData && entity.isAuditor && (
            <SetOneConformityButton lot={lotData.lot} />
          )}
          <NavigationButtons neighbors={neighbors} closeAction={closeDialog} />
        </footer>

        {lot.loading && <LoaderOverlay />}
      </Dialog>
    </Portal>
  )
}

export default LotDetails
