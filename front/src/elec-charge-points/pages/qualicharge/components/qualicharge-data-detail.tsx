import { Dialog } from "common/components/dialog2"
import { useHashMatch } from "common/components/hash-route"
import Portal, { usePortal } from "common/components/portal"
import { useQuery } from "common/hooks/async"
import { useTranslation } from "react-i18next"
import { useNavigate } from "react-router-dom"
import { getQualichargeDataDetail } from "../api"
import useEntity from "common/hooks/entity"
import { Box, Grid, LoaderOverlay, Row } from "common/components/scaffold"
import { QualichargeBadge } from "./qualicharge-badge"
import { NumberInput, TextInput } from "common/components/inputs2"
import { Button } from "common/components/button2"
import { ValidateDataDialog } from "./validate-data-dialog"
import { useValidateVolumes } from "../hooks/use-validate-volumes"
import { useNotify } from "common/components/notifications"

export const QualichargeDataDetail = () => {
  const match = useHashMatch("data/:id")
  const { t } = useTranslation()
  const navigate = useNavigate()
  const entity = useEntity()
  const portal = usePortal()
  const notify = useNotify()
  const { result, loading } = useQuery(getQualichargeDataDetail, {
    key: "qualicharge-data-detail",
    params: [parseInt(match?.params.id ?? ""), entity.id],
  })
  const closeDialog = () => {
    navigate({ search: location.search, hash: "#" })
  }

  const validateVolumes = useValidateVolumes({
    onSuccess: () => {
      closeDialog()
      notify(t("Le volume a été validé avec succès."), {
        variant: "success",
      })
    },
  })

  const openValidateDataModal = () => {
    portal((close) => (
      <ValidateDataDialog
        volume={result?.data?.energy_amount ?? 0}
        onConfirm={() =>
          validateVolumes.handleValidateVolumes([result?.data?.id as number])
        }
        onClose={close}
      />
    ))
  }
  return (
    <Portal>
      <Dialog
        header={
          <Row gap="md">
            <Dialog.Title>
              {t("Données Qualicharge") + " - ID " + match?.params.id}
            </Dialog.Title>
            {!loading && result?.data && (
              <QualichargeBadge status={result.data.validated_by} />
            )}
          </Row>
        }
        footer={
          <Button iconId="ri-check-line" onClick={openValidateDataModal}>
            {t("Valider")}
          </Button>
        }
        onClose={closeDialog}
        fitContent
      >
        {loading ? (
          <LoaderOverlay />
        ) : (
          <Box>
            <Grid cols={2} gap="xl">
              <TextInput
                label={t("Unité d'exploitation")}
                value={result?.data?.operating_unit}
                readOnly
              />
              <TextInput
                label={t("Station ID")}
                value={result?.data?.station_id}
                readOnly
              />
              <TextInput
                label={t("Début de la mesure")}
                value={result?.data?.date_from}
                readOnly
              />
              <TextInput
                label={t("Fin de la mesure")}
                value={result?.data?.date_to}
                readOnly
              />

              <NumberInput
                label={t("Energie (MWh)")}
                value={result?.data?.energy_amount}
                readOnly
              />

              <TextInput label={t("Taux utilisé")} value="25%" readOnly />
            </Grid>
          </Box>
        )}
      </Dialog>
    </Portal>
  )
}
