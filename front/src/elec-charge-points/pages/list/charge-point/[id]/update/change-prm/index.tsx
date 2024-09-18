import Button from "common/components/button"
import Dialog from "common/components/dialog"
import Form, { useForm } from "common/components/form"
import { Plus } from "common/components/icons"
import { DateInput, TextInput } from "common/components/input"
import { PortalInstance, usePortal } from "common/components/portal"
import { ChargePoint } from "elec-charge-points/types"
import { useTranslation } from "react-i18next"
import { ChangeMeasureReferencePointQuery } from "../types"
import { AcceptChangeMeasureReferencePoint } from "./accept-change-prm"

const FORM_ID = "change-measure-reference-point"

type ChangeMeasureReferencePointProps = {
  onClose: PortalInstance["close"]
  charge_point_id: ChargePoint["id"]
}

export const ChangeMeasureReferencePoint = ({
  onClose,
  charge_point_id,
}: ChangeMeasureReferencePointProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  const { value, bind } = useForm<ChangeMeasureReferencePointQuery>({
    measure_date: "",
    measure_reference_point_id: "",
    charge_point_id,
  })

  const openAcceptChangeMeasureReferencePoint = () =>
    portal((close) => (
      <AcceptChangeMeasureReferencePoint
        onClose={close}
        onMeasureReferencePointChanged={() => onClose()}
        data={value}
      />
    ))

  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>{t("Déclarer un changement de PRM")}</h1>
      </header>
      <main>
        <section>
          <Form id={FORM_ID} onSubmit={openAcceptChangeMeasureReferencePoint}>
            <DateInput
              label={t("Date d'installation")}
              required
              {...bind("measure_date")}
            />
            <TextInput
              label={t("Nouveau numéro de PRM")}
              required
              {...bind("measure_reference_point_id")}
            />
          </Form>
        </section>
      </main>
      <footer>
        <Button
          submit={FORM_ID}
          variant="primary"
          icon={Plus}
          label={t("Remplacer l'ancien compteur")}
          asideX
        />
      </footer>
    </Dialog>
  )
}
