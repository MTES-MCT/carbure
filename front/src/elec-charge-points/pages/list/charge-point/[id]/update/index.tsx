import useEntity from "carbure/hooks/entity"
import Dialog from "common/components/dialog"
import Form, { useForm } from "common/components/form"
import { useHashMatch } from "common/components/hash-route"
import { TextInput } from "common/components/input"
import Portal from "common/components/portal"
import { useQuery } from "common/hooks/async"
import { ChargePointStatusTag } from "elec-charge-points/components/charge-point-status-tag"
import { ChargePoint } from "elec-charge-points/types"
import { useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import * as api from "./api"

const UpdateChargePointDialog = () => {
  const entity = useEntity()
  const navigate = useNavigate()
  const location = useLocation()
  const { t } = useTranslation()
  const closeDialog = () => navigate({ search: location.search, hash: "#" })
  const match = useHashMatch("charge-point/:id/update")
  const { value, bind, setValue } = useForm<ChargePoint | undefined>(undefined)

  const chargePointDetailQuery = useQuery(api.getChargePointDetail, {
    key: "charge-points-details",
    params: [entity.id, parseInt(match?.params.id || "")],
    onSuccess: (response) => {
      if (response.data.data) {
        setValue(response.data.data)
      }
    },
  })

  const chargePointDetails = chargePointDetailQuery.result?.data.data

  if (!value) {
    return null
  }

  return (
    <Portal onClose={closeDialog}>
      <Dialog onClose={closeDialog}>
        <header>
          <ChargePointStatusTag status={value.status} />
          <h1>
            {t("PDC")} - {value.charge_point_id}
          </h1>
        </header>

        <main>
          <section>
            <strong>{t("Informations")}</strong>
            <Form>
              <TextInput
                label={t("Identifiant du point de recharge")}
                value={`${value.charge_point_id}`}
                readOnly
              />
            </Form>
          </section>
        </main>
      </Dialog>
    </Portal>
  )
}

export default UpdateChargePointDialog
