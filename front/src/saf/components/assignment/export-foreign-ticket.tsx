import useEntity from "common/hooks/entity"
import { Button } from "common/components/button2"
import { Dialog } from "common/components/dialog2"
import Portal from "common/components/portal"
import { useMutation } from "common/hooks/async"
import { useTranslation } from "react-i18next"
import * as api from "saf/api"
import * as commonApi from "common/api"
import * as norm from "common/utils/normalizers"
import { SafTicketSourceDetails } from "saf/types"
import Form, { useForm } from "common/components/form"
import { TextInput } from "common/components/inputs2"
import { Autocomplete } from "common/components/autocomplete2"
import { Country } from "common/types"
import { VolumeInput } from "./volume-input"
import { PeriodSelect } from "./period-select"

export interface ExportForeignTicketProps {
  ticketSource: SafTicketSourceDetails
  onClose: () => void
  onTicketExported: (volume: number, clientName: string) => void
}

export const ExportForeignTicket = ({
  ticketSource,
  onClose,
  onTicketExported,
}: ExportForeignTicketProps) => {
  const { t } = useTranslation()
  const entity = useEntity()

  const exportSafTicketSource = useMutation(api.exportSafTicketSource, {
    invalidates: [
      "ticket-source-details",
      "ticket-sources",
      "tickets",
      "operator-snapshot",
      "saf-snapshot",
    ],
  })

  const remainingVolume =
    ticketSource.total_volume - ticketSource.assigned_volume

  const { value, bind, setField, setFieldError } =
    useForm<ExportForeignTicketFormData>({
      volume: 0,
      assignment_period: ticketSource.delivery_period,
      export_country: undefined,
      unknown_airline_client: "",
    })

  const setMaximumVolume = () => {
    setField("volume", remainingVolume)
  }

  const handleSubmit = async () => {
    if (!value.volume || value.volume < 1) {
      return setFieldError("volume", t("Entrez un volume"))
    }

    if (!value.export_country) {
      return setFieldError("export_country", t("Sélectionnez un pays"))
    }

    const unknownAirlineClient = value.unknown_airline_client?.trim()

    if (!unknownAirlineClient) {
      return setFieldError("unknown_airline_client", t("Entrez un client"))
    }

    await exportSafTicketSource.execute(
      entity.id,
      ticketSource.id,
      value.volume,
      value.assignment_period,
      value.export_country,
      unknownAirlineClient
    )

    onTicketExported(value.volume, unknownAirlineClient)
    onClose()
  }

  return (
    <Portal onClose={onClose}>
      <Dialog
        onClose={onClose}
        header={
          <Dialog.Title>
            {t("Exporter le volume CAD n°")}
            {ticketSource?.carbure_id}
          </Dialog.Title>
        }
        footer={
          <Button
            loading={exportSafTicketSource.loading}
            iconId="ri-send-plane-line"
            priority="primary"
            nativeButtonProps={{
              form: "export-foreign-ticket",
            }}
            type="submit"
          >
            {t("Exporter")}
          </Button>
        }
      >
        <p>
          {t(
            "Veuillez remplir le formulaire ci-dessous afin de déclarer l'export d'une partie ou tout le volume du lot vers un pays étranger."
          )}
        </p>

        <Form<ExportForeignTicketFormData>
          id="export-foreign-ticket"
          onSubmit={handleSubmit}
        >
          <VolumeInput
            remainingVolume={remainingVolume}
            onSetMaximumVolume={setMaximumVolume}
            {...bind("volume")}
          />

          <PeriodSelect
            label={t("Période")}
            deliveryPeriod={ticketSource.delivery_period}
            {...bind("assignment_period")}
          />

          <Autocomplete
            required
            label={t("Pays d'export")}
            placeholder={t("Sélectionnez un pays")}
            getOptions={(query) =>
              commonApi.findCountries(query, { exclude_france: true })
            }
            normalize={norm.normalizeCountry}
            {...bind("export_country")}
          />

          <TextInput
            required
            label={t("Client")}
            placeholder={t("Ex: Compagnie aérienne étrangère")}
            {...bind("unknown_airline_client")}
          />
        </Form>
      </Dialog>
    </Portal>
  )
}

export interface ExportForeignTicketFormData {
  volume?: number
  assignment_period: number
  export_country?: Country
  unknown_airline_client?: string
}

export default ExportForeignTicket
