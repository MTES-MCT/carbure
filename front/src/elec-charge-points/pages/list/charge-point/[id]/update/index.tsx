import useEntity from "common/hooks/entity"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import Form, { useForm, Fieldset } from "common/components/form"
import { useHashMatch } from "common/components/hash-route"
import { Check, Cross, Return } from "common/components/icons"
import { TextInput, NumberInput } from "common/components/input"
import { useNotify } from "common/components/notifications"
import Portal, { usePortal } from "common/components/portal"
import { LoaderOverlay } from "common/components/scaffold"
import { CONTACT_US_EMAIL } from "common/globals"
import { useMutation, useQuery } from "common/hooks/async"
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
import { AxiosError } from "axios"
import { DeleteMeterDialog } from "./delete-meter-dialog"

const UpdateChargePointDialog = () => {
  const entity = useEntity()
  const navigate = useNavigate()
  const location = useLocation()
  const { t } = useTranslation()
  const portal = usePortal()
  const notify = useNotify()
  const closeDialog = () => navigate({ search: location.search, hash: "#" })
  const match = useHashMatch("charge-point/:id/update")
  const { value, bind, setValue, setFieldError } = useForm<
    Partial<ChargePoint>
  >({})

  const chargePointDetailQuery = useQuery(api.getChargePointDetail, {
    key: "charge-points-details",
    params: [entity.id, parseInt(match?.params.id || "")],
    onSuccess: (response) => {
      if (response.data.data) {
        setValue(response.data.data)
      }
    },
  })
  const chargePointUpdate = useMutation(api.updateChargePoint, {
    invalidates: ["charge-points-list"],
    onSuccess: () => {
      closeDialog()
      notify(t("Le point de recharge a bien été mis à jour."), {
        variant: "success",
      })
    },
    onError: (e) => {
      const errors: Record<
        string,
        { field: keyof ChargePoint; error: string }
      > = {
        CP_ID_NOT_IN_TGD: {
          field: "charge_point_id",
          error: t(
            "Identifiant non trouvé. Veuillez vérifier que votre point de recharge existe bien sur transport.data.gouv.fr."
          ),
        },
        CP_ID_ALREADY_EXISTS: {
          field: "charge_point_id",
          error: t(
            "Cet identifiant est déjà utilisé pour un autre point de charge."
          ),
        },
        INITIAL_INDEX_CANNOT_BE_UPDATED: {
          field: "initial_index",
          error: t(
            "Ce compteur a déjà des relevés associés, veuillez contacter l'administration si vous souhaitez modifier l'index initial de ce compteur."
          ),
        },
      }
      const error = (e as AxiosError<{ error: string }>).response?.data.error

      if (error && Object.keys(errors).includes(error)) {
        const errorKey = error as keyof typeof errors
        const currentError = errors[errorKey]!
        setFieldError(currentError.field, currentError.error)
      } else {
        notify(
          t(
            "Une erreur est survenue lors de la mise à jour du point de recharge."
          ),
          { variant: "danger" }
        )
      }
    },
  })

  const chargePointDetail = chargePointDetailQuery?.result?.data.data
  const isReadOnly = value.status === ChargePointStatus.AuditInProgress

  const hasChangedInitialIndex =
    chargePointDetailQuery.result?.data.data?.initial_index !=
    value.initial_index

  const openDeleteMeterDialog = () => {
    if (!chargePointDetail) return

    portal((close) => (
      <DeleteMeterDialog onClose={close} chargePointId={chargePointDetail.id} />
    ))
  }

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
            {t("PDC")} - {chargePointDetail?.charge_point_id}
          </h1>
        </header>

        {!chargePointDetail ? (
          <main>
            <section>{t("Point de recharge non trouvé.")}</section>
          </main>
        ) : (
          <>
            <main>
              <section>
                <Form style={{ gap: "var(--spacing-l)" }}>
                  <Fieldset label={t("Informations")}>
                    <TextInput
                      label={t("Identifiant du point de recharge")}
                      readOnly={isReadOnly}
                      hasTooltip
                      title={`${t(
                        "Pour modifier ce champ, veuillez contacter directement l'équipe de CarbuRe sur"
                      )} ${CONTACT_US_EMAIL}`}
                      {...bind("charge_point_id")}
                      hideError={false}
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
                    {value.mid_id && (
                      <>
                        <TextInput
                          label={t("Numéro du certificat (MID)")}
                          readOnly
                          {...bind("mid_id")}
                          rightContent={
                            <Button
                              variant="danger"
                              action={openDeleteMeterDialog}
                              disabled={isReadOnly}
                            >
                              {t("Suppr. compteur")}
                            </Button>
                          }
                        />

                        <NumberInput
                          label={`${t("Index initial relevé (kWh)")}${value.initial_index_date ? ` - ${formatDate(value.initial_index_date)}` : ""}`}
                          readOnly={isReadOnly}
                          hideError={false}
                          {...bind("initial_index")}
                          disabled={
                            value.initial_index != value.measure_energy ||
                            value.initial_index_date != value.measure_date
                          }
                        />
                        <NumberInput
                          label={`${t("Dernier index relevé (kWh)")}${value.measure_date ? ` - ${formatDate(value.measure_date)}` : ""}`}
                          readOnly
                          {...bind("measure_energy")}
                        />
                      </>
                    )}

                    <Button
                      variant="link"
                      action={openChangeMeterDialog}
                      disabled={isReadOnly}
                    >
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
                      disabled={isReadOnly}
                    >
                      {t("Mon PRM a changé ?")}
                    </Button>
                  </Fieldset>
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
                      id={chargePointDetail.id}
                      onClose={close}
                    />
                  ))
                }
                disabled={isReadOnly}
              />
              {isReadOnly ? (
                <Button
                  variant="secondary"
                  icon={Return}
                  label={t("Retour")}
                  action={closeDialog}
                  asideX
                />
              ) : (
                <Button
                  variant="primary"
                  icon={Check}
                  label={t("Sauvegarder")}
                  action={() =>
                    chargePointUpdate.execute(entity.id, chargePointDetail.id, {
                      charge_point_id: value.charge_point_id || "",
                      initial_index: hasChangedInitialIndex
                        ? value.initial_index
                        : undefined,
                    })
                  }
                  loading={chargePointUpdate.loading}
                  asideX
                />
              )}
            </footer>
          </>
        )}
      </Dialog>
    </Portal>
  )
}

export default UpdateChargePointDialog
