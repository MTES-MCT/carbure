import useEntity from "carbure/hooks/entity"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import Form, { useForm, Fieldset } from "common/components/form"
import { useHashMatch } from "common/components/hash-route"
import { TextInput, NumberInput } from "common/components/input"
import Portal, { usePortal } from "common/components/portal"
import { CONTACT_US_EMAIL } from "common/globals"
import { useQuery } from "common/hooks/async"
import { formatDate } from "common/utils/formatters"
import { ChargePointStatusTag } from "elec-charge-points/components/charge-point-status-tag"
import { ChargePoint, ChargePointStatus } from "elec-charge-points/types"
import { useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import * as api from "./api"
import { ChangeMeter } from "./change-meter"

const UpdateChargePointDialog = () => {
  const entity = useEntity()
  const navigate = useNavigate()
  const location = useLocation()
  const { t } = useTranslation()
  const portal = usePortal()
  const closeDialog = () => navigate({ search: location.search, hash: "#" })
  const match = useHashMatch("charge-point/:id/update")
  const { value, bind, setValue } = useForm<Partial<ChargePoint>>({})

  const chargePointDetailQuery = useQuery(api.getChargePointDetail, {
    key: "charge-points-details",
    params: [entity.id, parseInt(match?.params.id || "")],
    onSuccess: (response) => {
      if (response.data.data) {
        setValue(response.data.data)
      }
    },
  })
  const chargePointDetail = chargePointDetailQuery?.result?.data.data

  if (!value || !chargePointDetail) {
    return null
  }

  const openChangeMeterDialog = () => {
    portal((close) => (
      <ChangeMeter onClose={close} charge_point_id={chargePointDetail.id} />
    ))
  }

  return (
    <Portal onClose={closeDialog}>
      <Dialog onClose={closeDialog}>
        <header>
          {value.status && <ChargePointStatusTag status={value.status} />}
          <h1>
            {t("PDC")} - {value.charge_point_id}
          </h1>
        </header>

        <main>
          <section>
            <Form>
              <Fieldset label={t("Informations")}>
                <TextInput
                  label={t("Identifiant du point de recharge")}
                  readOnly={value.status !== ChargePointStatus.Pending}
                  hasTooltip
                  title={`${t(
                    "Pour modifier ce champ, veuillez contacter directement l'équipe de CarbuRe sur"
                  )} ${CONTACT_US_EMAIL}`}
                  {...bind("charge_point_id")}
                />
                <NumberInput
                  label={`${t("Dernier index en kWh")}${value.measure_date ? `- ${formatDate(value.measure_date)}` : ""}`}
                  readOnly
                  {...bind("measure_energy")}
                />
                <NumberInput
                  label={t("Longitude")}
                  readOnly
                  {...bind("longitude")}
                />
                <NumberInput
                  label={t("Latitude")}
                  readOnly
                  {...bind("latitude")}
                />
                <NumberInput
                  label={t("Puissance nominale - kW")}
                  readOnly
                  {...bind("nominal_power")}
                />
              </Fieldset>

              <Fieldset label={t("Compteur MID")}>
                <TextInput
                  label={t("Numéro du certificat (MID)")}
                  {...bind("mid_id")}
                />
                <Button variant="link" action={openChangeMeterDialog}>
                  {t("Mon compteur MID a changé ?")}
                </Button>
              </Fieldset>
            </Form>
          </section>
        </main>
      </Dialog>
    </Portal>
  )
}

export default UpdateChargePointDialog
