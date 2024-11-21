import { useTranslation } from "react-i18next"
import { Stock, StockPayload } from "../types"
import * as api from "../api"
import useEntity from "carbure/hooks/entity"
import { useMutation } from "common/hooks/async"
import { useNotify } from "common/components/notifications"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import { Drop, Return } from "common/components/icons"
import { usePortal } from "common/components/portal"
import Form, { useForm } from "common/components/form"
import { Country, Depot, type EntityPreview } from "carbure/types"
import { DateInput, NumberInput, TextInput } from "common/components/input"
import Autocomplete from "common/components/autocomplete"
import {
  findBiofuelEntities,
  findCountries,
  findDepots,
  findMyCertificates,
} from "carbure/api"
import * as norm from "carbure/utils/normalizers"
import { useMatomo } from "matomo"
import Select from "common/components/select"
import { formatNumber } from "common/utils/formatters"
import { getDeliveryTypes } from "lot-add/components/delivery-fields"

export interface SplitOneButtonProps {
  disabled?: boolean
  stock: Stock
}

export const SplitOneButton = ({ disabled, stock }: SplitOneButtonProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  return (
    <Button
      disabled={disabled}
      variant="primary"
      icon={Drop}
      label={t("Extraire un lot")}
      action={() =>
        portal((close) => <SplitDialog stock={stock} onClose={close} />)
      }
    />
  )
}

interface ApproveFixDialogProps {
  stock: Stock
  onClose: () => void
}

const SplitDialog = ({ stock, onClose }: ApproveFixDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const matomo = useMatomo()
  const entity = useEntity()

  const { value, bind, setValue, setField } = useForm<SplitForm>(
    { ...defaultSplit, stock_id: stock.carbure_id },
    {
      setValue: (form) => {
        const knownClient = form.client instanceof Object ? form.client : null
        const isClientEntity = knownClient?.id === entity.id
        const isClientUnknown = knownClient === null

        if (!isClientEntity && !isClientUnknown) {
          form.delivery_type = undefined
        }

        return form
      },
    }
  )

  const deliveryTypes = getDeliveryTypes(entity, value.client)

  const splitStock = useMutation(api.splitStock, {
    invalidates: ["snapshot", "stock-details"],

    onSuccess: () => {
      notify(t("Le lot a bien été ajouté à vos brouillons !"), { variant: "success" }) // prettier-ignore
      setValue(defaultSplit)
    },

    onError: () => {
      notify(t("Le lot n'a pas pu être créé"), { variant: "danger" })
    },
  })

  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>{t("Extraire un lot")}</h1>
      </header>
      <main>
        <section>
          {t(
            "Veuillez remplir le formulaire ci-dessous afin de créer un nouveau lot basé sur le stock sélectionné :"
          )}
        </section>
        <section>
          <Form id="split-stock">
            <NumberInput
              autoFocus
              required
              {...bind("volume")}
              label={t("Volume ({{volume}} litres disponibles)", {
                count: stock.remaining_volume,
                volume: formatNumber(stock.remaining_volume),
              })}
              icon={() => (
                <Button
                  variant="primary"
                  label={t("Maximum")}
                  action={() => setField("volume", stock.remaining_volume ?? 0)}
                />
              )}
            />
            <TextInput
              label={t("N° Document d'accompagnement")}
              {...bind("transport_document_reference")}
            />
            <Autocomplete
              label={t("Votre certificat de négoce")}
              getOptions={(query) =>
                findMyCertificates(query, { entity_id: entity.id })
              }
              placeholder={entity.default_certificate}
              {...bind("supplier_certificate")}
            />
            <Autocomplete
              label={t("Client")}
              getOptions={findBiofuelEntities}
              normalize={norm.normalizeEntityPreviewOrUnknown}
              create={norm.identity}
              {...bind("client")}
            />
            {deliveryTypes.length > 0 && (
              <Select
                clear
                label={t("Type de livraison")}
                placeholder={t("Choisissez un type")}
                normalize={norm.normalizeDeliveryType}
                {...bind("delivery_type")}
                options={deliveryTypes}
              />
            )}
            <Autocomplete
              label={t("Site de livraison")}
              getOptions={findDepots}
              normalize={norm.normalizeDepotOrUnknown}
              create={norm.identity}
              {...bind("delivery_site")}
            />
            {value.delivery_site instanceof Object ? (
              <TextInput
                disabled
                label={t("Pays de livraison")}
                value={norm.normalizeCountry(value.delivery_site.country).label}
              />
            ) : (
              <Autocomplete
                required
                label={t("Pays de livraison")}
                getOptions={findCountries}
                normalize={norm.normalizeCountry}
                {...bind("delivery_site_country")}
              />
            )}
            <DateInput
              required
              label={t("Date de livraison")}
              {...bind("delivery_date")}
            />
          </Form>
        </section>
      </main>
      <footer>
        <Button
          asideX
          submit="split-stock"
          loading={splitStock.loading}
          variant="primary"
          icon={Drop}
          label={t("Extraire lot")}
          action={() => {
            matomo.push(["trackEvent", "stocks", "split-stock"])
            splitStock.execute(entity.id, [formToStockPayload(value)])
          }}
        />
        <Button
          disabled={splitStock.loading}
          icon={Return}
          label={t("Annuler")}
          action={onClose}
        />
      </footer>
    </Dialog>
  )
}

function formToStockPayload(form: SplitForm): StockPayload {
  return {
    stock_id: form.stock_id,
    volume: form.volume,
    supplier_certificate: form.supplier_certificate,
    transport_document_reference: form.transport_document_reference,
    transport_document_type: undefined,
    delivery_type: form.delivery_type,
    delivery_date: form.delivery_date,
    carbure_delivery_site_id:
      form.delivery_site instanceof Object
        ? form.delivery_site.customs_id
        : undefined,
    unknown_delivery_site:
      typeof form.delivery_site === "string" ? form.delivery_site : undefined,
    delivery_site_country_id: form.delivery_site_country?.code_pays,
    carbure_client_id:
      form.client instanceof Object ? form.client.id : undefined,
    unknown_client: typeof form.client === "string" ? form.client : undefined,
  }
}

const defaultSplit = {
  stock_id: undefined as string | undefined,
  delivery_type: undefined as string | undefined,
  volume: 0 as number | undefined,
  transport_document_reference: undefined as string | undefined,
  supplier_certificate: undefined as string | undefined,
  client: undefined as EntityPreview | string | undefined,
  delivery_date: undefined as string | undefined,
  delivery_site: undefined as Depot | string | undefined,
  delivery_site_country: undefined as Country | undefined,
}

type SplitForm = typeof defaultSplit
