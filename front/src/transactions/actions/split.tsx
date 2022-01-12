import { useTranslation } from "react-i18next"
import { Stock, StockPayload } from "../types"
import * as api from "../api"
import useEntity from "carbure/hooks/entity"
import { useMutation } from "common-v2/hooks/async"
import { useNotify } from "common-v2/components/notifications"
import Button from "common-v2/components/button"
import Dialog from "common-v2/components/dialog"
import { Drop, Return } from "common-v2/components/icons"
import { usePortal } from "common-v2/components/portal"
import Form, { useForm } from "common-v2/components/form"
import { Entity } from "carbure/types"
import { Country, Depot } from "common/types"
import { DateInput, NumberInput, TextInput } from "common-v2/components/input"
import Autocomplete from "common-v2/components/autocomplete"
import { findCountries, findDepots, findEntities } from "common-v2/api"
import * as norm from "common-v2/utils/normalizers"

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
  const entity = useEntity()

  const splitStock = useMutation(api.splitStock, {
    invalidates: ["snapshot"],

    onSuccess: () => {
      notify(t("Le lot a bien été ajouté à vos brouillons !"), {
        variant: "success",
      })
      onClose()
    },

    onError: () => {
      notify(t("Le lot n'a pas pu être créé"), { variant: "danger" })
      onClose()
    },
  })

  const { value, bind } = useForm(defaultSplit)

  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>{t("Extraire un lot")}</h1>
      </header>
      <main>
        <section>
          {t(
            "Veuillez remplir le formulaire ci-dessous afin de créer un nouveau lot basé sur le stock sélectionné"
          )}
        </section>
        <section>
          <Form id="split-stock">
            <NumberInput label={t("Volume")} {...bind("volume")} />
            <TextInput
              label={t("N° Document d'accompagnement")}
              {...bind("transport_document_reference")}
            />
            <Autocomplete
              label={t("Client")}
              getOptions={findEntities}
              normalize={norm.normalizeEntity}
              create={norm.identity}
              {...bind("client")}
            />
            <Autocomplete
              label={t("Site de livraison")}
              getOptions={findDepots}
              normalize={norm.normalizeDepot}
              {...bind("delivery_site")}
            />
            <Autocomplete
              label={t("Pays de livraison")}
              getOptions={findCountries}
              normalize={norm.normalizeCountry}
              {...bind("delivery_site_country")}
            />
            <DateInput
              label={t("Date de livraison")}
              {...bind("delivery_date")}
            />
          </Form>
        </section>
      </main>
      <footer>
        <Button
          asideX
          disabled={splitStock.loading}
          icon={Return}
          label={t("Annuler")}
          action={onClose}
        />
        <Button
          submit="split-stock"
          loading={splitStock.loading}
          variant="primary"
          icon={Drop}
          label={t("Extraire lot")}
          action={() =>
            splitStock.execute(entity.id, [formToStockPayload(stock.id, value)])
          }
        />
      </footer>
    </Dialog>
  )
}

function formToStockPayload(
  stock_id: number,
  form: typeof defaultSplit
): StockPayload {
  return {
    stock_id,
    volume: form.volume,
    transport_document_reference: form.transport_document_reference,
    transport_document_type: undefined,
    delivery_type: undefined,
    delivery_date: form.delivery_date,
    carbure_delivery_site_id:
      form.delivery_site instanceof Object
        ? form.delivery_site.depot_id
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
  volume: 0 as number | undefined,
  transport_document_reference: undefined as string | undefined,
  client: undefined as Entity | string | undefined,
  delivery_date: undefined as string | undefined,
  delivery_site: undefined as Depot | string | undefined,
  delivery_site_country: undefined as Country | undefined,
}
