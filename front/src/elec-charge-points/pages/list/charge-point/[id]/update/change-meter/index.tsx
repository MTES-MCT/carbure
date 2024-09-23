import { useTranslation } from "react-i18next"
import Dialog from "common/components/dialog"
import Form, { Fieldset, useForm } from "common/components/form"
import { PortalInstance, usePortal } from "common/components/portal"
import { DateInput, NumberInput, TextInput } from "common/components/input"
import Button from "common/components/button"
import { Plus } from "common/components/icons"
import { AddMeterQuery } from "../types"
import { ChargePoint } from "elec-charge-points/types"
import { AcceptChangeMeter } from "./accept-change-meter"

const FORM_ID = "update-meter"

type ChangeMeterProps = {
  onClose: PortalInstance["close"]
  charge_point_id: ChargePoint["id"]
}

export const ChangeMeter = ({ onClose, charge_point_id }: ChangeMeterProps) => {
  const { t } = useTranslation()

  const portal = usePortal()

  const { value, bind } = useForm<AddMeterQuery>({
    initial_index_date: "",
    mid_certificate: "",
    initial_index: 0,
    charge_point_id,
  })

  const openAcceptChangeMeter = () =>
    portal((close) => (
      <AcceptChangeMeter
        onClose={close}
        data={value}
        onMeterChanged={() => onClose()}
      />
    ))

  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>{t("Déclarer un changement de compteur")}</h1>
      </header>
      <main>
        <section>
          <Form id={FORM_ID} onSubmit={openAcceptChangeMeter}>
            <DateInput
              label={t("Date d'installation")}
              required
              {...bind("initial_index_date")}
            />
            <TextInput
              label={t("Nouveau numéro de certificat MID")}
              required
              {...bind("mid_certificate")}
            />

            <Fieldset label={t("Relevé du nouveau compteur")}>
              <NumberInput
                label={t("Energie active totale relevée kWh (Index)")}
                required
                {...bind("initial_index")}
                min={0}
              />
            </Fieldset>
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
