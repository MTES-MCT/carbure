import { useMemo } from "react"
import { useNavigate, useLocation, useParams } from "react-router-dom"
import { useTranslation } from "react-i18next"
import * as api from "../../api"
import { useMatomo } from "matomo"
import { CorrectionStatus, Lot, LotStatus } from "transactions/types"
import { useQuery, useMutation } from "common-v2/hooks/async"
import { useNotify } from "common-v2/components/notifications"
import { useStatus } from "transactions/components/status"
import useEntity from "carbure/hooks/entity"
import { LoaderOverlay } from "common-v2/components/scaffold"
import Dialog from "common-v2/components/dialog"
import Button from "common-v2/components/button"
import { Alarm, Return, Save } from "common-v2/components/icons"
import LotForm, { hasChange, useLotForm } from "lot-add/components/lot-form"
import LotTag from "transactions/components/lots/lot-tag"
import Comments from "./comments"
import {
  BlockingAnomalies,
  separateAnomalies,
  WarningAnomalies,
} from "./anomalies"
import { getLotChanges, LotHistory } from "./history"
import { isExpiring } from "common-v2/utils/deadline"
import Alert from "common-v2/components/alert"
import NavigationButtons from "./navigation"
import LotActions from "./actions"
import { Entity, UserRole } from "carbure/types"
import LotTraceability, { hasTraceability } from "./lot-traceability"
import { invalidate } from "common-v2/hooks/invalidate"
import { useCategory } from "transactions/components/category"

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
  const status = useStatus()
  const category = useCategory()
  const params = useParams<"id">()

  const lot = useQuery(api.getLotDetails, {
    key: "lot-details",
    params: [entity.id, parseInt(params.id!)],
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

  const form = useLotForm(lotData?.lot, errors, certificates)

  const editable = isEditable(lotData?.lot, entity)
  const hasEditRights = entity.hasRights(UserRole.Admin, UserRole.ReadWrite)
  const expiring = isExpiring(lotData?.lot)

  const canSave = useMemo(
    () => hasChange(form.value, lotData?.lot),
    [form.value, lotData?.lot]
  )

  const closeDialog = () => {
    invalidate("lots")
    navigate({
      pathname: `../${status}/${category}`,
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

        <NavigationButtons
          neighbors={neighbors}
          root={`../${status}/${category}`}
        />

        <Button icon={Return} label={t("Retour")} action={closeDialog} />
      </footer>

      {lot.loading && <LoaderOverlay />}
    </Dialog>
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