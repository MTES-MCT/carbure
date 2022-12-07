import { useEffect, useMemo } from "react"
import { useNavigate, useLocation } from "react-router-dom"
import { useTranslation } from "react-i18next"
import * as api from "../../api"
import { useMatomo } from "matomo"
import {
  CorrectionStatus,
  DeliveryType,
  Lot,
  LotStatus,
} from "transactions/types"
import { useQuery, useMutation } from "common/hooks/async"
import { useNotify } from "common/components/notifications"
import useEntity from "carbure/hooks/entity"
import { layout, LoaderOverlay } from "common/components/scaffold"
import Dialog from "common/components/dialog"
import Button from "common/components/button"
import { Alarm, Return, Save } from "common/components/icons"
import LotForm, { hasChange, useLotForm } from "lot-add/components/lot-form"
import LotTag from "transactions/components/lots/lot-tag"
import Comments from "./comments"
import {
  BlockingAnomalies,
  separateAnomalies,
  WarningAnomalies,
} from "./anomalies"
import { getLotChanges, LotHistory } from "./history"
import { isExpiring } from "transactions/utils/deadline"
import Alert from "common/components/alert"
import NavigationButtons from "./navigation"
import LotActions from "./actions"
import { Entity, UserRole } from "carbure/types"
import LotTraceability, { hasTraceability } from "./lot-traceability"
import { invalidate } from "common/hooks/invalidate"
import { formatDate } from "common/utils/formatters"
import Score from "../score"
import Portal from "common/components/portal"
import Flags from "flags.json"
import { useHashMatch } from "common/components/hash-route"
import useScrollToRef from "common/hooks/scroll-to-ref"

export interface LotDetailsProps {
  neighbors: number[]
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
    params: [entity.id, parseInt(match?.params.id!)],
  })

  const updateLot = useMutation(api.updateLot, {
    invalidates: ["lots", "lot-details", "snapshot", "year", "lot-summary"],

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

  const editable = isEditable(lotData?.lot, entity)
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
    disabledFieldsInCorrection()
  }, [lotData])

  const disabledFieldsInCorrection = () => {
    if (lotData?.lot.correction_status === CorrectionStatus.InCorrection) {
      if (
        [DeliveryType.Trading, DeliveryType.Processing].includes(
          lotData?.lot.delivery_type
        )
      ) {
        form.setDisabledFieldsGroup(["batch", "production", "emissions"])
      }
    }
  }

  return (
    <Portal onClose={closeDialog}>
      <Dialog onClose={closeDialog}>
        <header>
          {Flags.scoring && lotData && (
            <Score big lot={lotData.lot} details={lotData.score} />
          )}
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
            <LotActions lot={lotData.lot} canSave={canSave} />
          )}

          <NavigationButtons neighbors={neighbors} closeAction={closeDialog} />
        </footer>

        {lot.loading && <LoaderOverlay />}
      </Dialog>
    </Portal>
  )
}

function isEditable(lot: Lot | undefined, entity: Entity) {
  if (lot === undefined) return false

  const isCreator = lot.added_by?.id === entity.id
  return (
    [LotStatus.Draft, LotStatus.Rejected].includes(lot.lot_status) ||
    (isCreator && lot.correction_status === CorrectionStatus.InCorrection)
  )
}

export default LotDetails
