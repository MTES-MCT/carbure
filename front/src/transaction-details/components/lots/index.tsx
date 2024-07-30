import { AxiosError } from "axios"
import useEntity from "carbure/hooks/entity"
import { Entity, UserRole } from "carbure/types"
import Alert from "common/components/alert"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import { useHashMatch } from "common/components/hash-route"
import { Alarm, Save } from "common/components/icons"
import { useNotify } from "common/components/notifications"
import Portal from "common/components/portal"
import { LoaderOverlay } from "common/components/scaffold"
import { useMutation, useQuery } from "common/hooks/async"
import useScrollToRef from "common/hooks/scroll-to-ref"
import { formatDate } from "common/utils/formatters"
import LotForm, { hasChange, useLotForm } from "lot-add/components/lot-form"
import { useMatomo } from "matomo"
import { useEffect, useMemo } from "react"
import { useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import LotTag from "transactions/components/lots/lot-tag"
import { CorrectionStatus, LotStatus } from "transactions/types"
import { isExpiring } from "transactions/utils/deadline"
import * as api from "../../api"
import Score from "../score"
import LotActions from "./actions"
import {
  BlockingAnomalies,
  separateAnomalies,
  WarningAnomalies,
} from "./anomalies"
import Comments from "./comments"
import { getLotChanges, LotHistory } from "./history"
import LotTraceability, { hasTraceability } from "./lot-traceability"
import NavigationButtons from "./navigation"
import { LotDetails as LotData } from "transaction-details/types"

export interface LotDetailsProps {
  neighbors?: number[]
}

export const LotDetails = ({ neighbors }: LotDetailsProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const matomo = useMatomo()

  const navigate = useNavigate()
  const location = useLocation()

  const entity = useEntity()
  const match = useHashMatch("lot/:id")

  const lot = useQuery(api.getLotDetails, {
    key: "lot-details",
    params: [entity.id, parseInt(match?.params.id || "")],
  })

  const updateLot = useMutation(api.updateLot, {
    invalidates: ["lots", "lot-details", "snapshot", "years", "lot-summary"],

    onSuccess: () => {
      notify(t("Le lot a bien été mis à jour"), { variant: "success" })
    },

    onError: () => {
      notify(t("La mise à jour du lot a échoué"), { variant: "danger" })
    },
  })

  const lotData = lot.result?.data.data
  const certificates = lotData?.certificates
  const creator = lotData?.lot.added_by
  const comments = lotData?.comments ?? []
  const changes = getLotChanges(lotData?.updates)
  const [errors, warnings] = separateAnomalies(lotData?.errors ?? [])
  const { refToScroll } = useScrollToRef(errors.length > 0)

  const form = useLotForm(lotData?.lot, errors, certificates)

  const editable = isEditable(lotData, entity)
  const hasEditRights = entity.hasRights(UserRole.Admin, UserRole.ReadWrite)
  const expiring = isExpiring(lotData?.lot)

  const canSave = useMemo(
    () => hasChange(form.value, lotData?.lot, entity),
    [form.value, lotData?.lot, entity]
  )

  const closeDialog = () => {
    navigate({ search: location.search, hash: "#" })
  }

  useEffect(() => {
    if (lotData) {
      form.setDisabledFields(lotData.disabled_fields)
    } else {
      form.setDisabledFields([])
    }
  }, [lotData])

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
            <LotForm
              form={form}
              readOnly={!editable || !hasEditRights}
              onSubmit={(form) => {
                matomo.push(["trackEvent", "lots-details", "save-lot-changes"])
                updateLot.execute(entity.id, form!)
              }}
            />
          </section>

          {errors.length > 0 && (
            <section ref={refToScroll}>
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
              <Comments
                readOnly={!editable}
                lot={lotData?.lot}
                comments={comments}
              />
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
          {editable && hasEditRights && (
            <Button
              loading={updateLot.loading}
              disabled={canSave}
              variant="primary"
              icon={Save}
              submit="lot-form"
              label={t("Sauvegarder")}
            />
          )}

          {lotData && hasEditRights && (
            <LotActions
              lot={lotData.lot}
              canSave={canSave}
              hasParentStock={!!lotData.has_parent_stock}
            />
          )}
          {neighbors && (
            <NavigationButtons
              neighbors={neighbors}
              closeAction={closeDialog}
            />
          )}
        </footer>

        {lot.loading && <LoaderOverlay />}
      </Dialog>
    </Portal>
  )
}

function isEditable(lotData: LotData | undefined, entity: Entity) {
  if (lotData === undefined) return false
  if (lotData.is_read_only) return false
  if (lotData.lot.added_by.id !== entity.id) return false // entity not owner

  const isDraft = lotData.lot.lot_status === LotStatus.Draft
  const isRejected = lotData.lot.lot_status === LotStatus.Rejected
  const isCorrection = lotData.lot.correction_status === CorrectionStatus.InCorrection // prettier-ignore

  return isDraft || isRejected || isCorrection
}

export default LotDetails
