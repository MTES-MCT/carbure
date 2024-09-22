import useEntity from "carbure/hooks/entity"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import Form, { useForm, Fieldset } from "common/components/form"
import { useHashMatch } from "common/components/hash-route"
import { Cross, Return } from "common/components/icons"
import { TextInput, NumberInput } from "common/components/input"
import Portal, { usePortal } from "common/components/portal"
import { LoaderOverlay } from "common/components/scaffold"
import { CONTACT_US_EMAIL } from "common/globals"
import { useQuery } from "common/hooks/async"
import { formatDate } from "common/utils/formatters"
import { ChargePointStatusTag } from "elec-charge-points/components/charge-point-status-tag"
import { ChargePoint, ChargePointStatus } from "elec-charge-points/types"
import { useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import * as api from "./api"
import { ChangeMeter } from "./change-meter"
import { ChangeMeasureReferencePoint } from "./change-prm"
import { DeleteChargePointDialog } from "./delete-charge-point-dialog"
import { MetersHistory } from "./meters-history"

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

  const openChangeMeterDialog = () => {
    if (!chargePointDetail) return

    portal((close) => (
      <ChangeMeter onClose={close} charge_point_id={chargePointDetail.id} />
    ))
  }

  const openChangeMeasureReferencePointDialog = () => {
    if (!chargePointDetail) return

    portal((close) => (
      <ChangeMeasureReferencePoint
        onClose={close}
        charge_point_id={chargePointDetail.id}
      />
    ))
  }

  if (chargePointDetailQuery.loading) {
    return <LoaderOverlay />
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

        {!chargePointDetail ? (
          <main>
            <section>{t("Point de recharge non trouvé.")}</section>
          </main>
        ) : (
          <>
            {" "}
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
                      label={`${t("Dernier index en kWh")}${value.measure_date ? ` - ${formatDate(value.measure_date)}` : ""}`}
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
                      readOnly
                      {...bind("mid_id")}
                    />
                    <Button variant="link" action={openChangeMeterDialog}>
                      {t("Mon compteur MID a changé ?")}
                    </Button>
                  </Fieldset>

                  <Fieldset label={t("PRM")}>
                    <TextInput
                      label={t("Numéro de PRM")}
                      readOnly
                      {...bind("measure_reference_point_id")}
                    />
                    <Button
                      variant="link"
                      action={openChangeMeasureReferencePointDialog}
                    >
                      {t("Mon PRM a changé ?")}
                    </Button>
                  </Fieldset>
                  {/* @ts-ignore */}
                  <MetersHistory charge_point_id={chargePointDetail.id} />
                </Form>
              </section>
            </main>
            <footer>
              <Button
                variant="danger"
                label={t("Supprimer")}
                icon={Cross}
                action={() =>
                  portal((close) => (
                    <DeleteChargePointDialog
                      charge_point_id={chargePointDetail.id}
                      onClose={close}
                    />
                  ))
                }
              />
              <Button
                variant="secondary"
                icon={Return}
                label={t("Retour")}
                action={closeDialog}
                asideX
              />
            </footer>
          </>
        )}
      </Dialog>
    </Portal>
  )
}

export default UpdateChargePointDialog
