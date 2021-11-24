import React from "react"

import { Entity, DeliverySite, Country } from "common/types"

import useForm from "common/hooks/use-form"

import { Box } from "common/components"
import { Button } from "common/components/button"
import { Check } from "common/components/icons"
import {
  Dialog,
  DialogButtons,
  DialogText,
  DialogTitle,
  PromptProps,
} from "common/components/dialog"
import * as Fields from "transactions/components/form/fields"
import { FormGroup } from "common/components/form"
import { Trans, useTranslation } from "react-i18next"

export interface StockSendDetails {
  volume: number
  dae: string
  delivery_date: string
  client: Entity | string | null
  delivery_site: DeliverySite | string | null
  delivery_site_country: Country | null
  mac: boolean
  carbure_vendor_certificate: string
  carbure_vendor: Entity
}

type StockSendLotPromptProps = {
  entity: Entity
} & PromptProps<StockSendDetails>

export const StockSendLotPrompt = ({
  entity,
  onResolve,
}: StockSendLotPromptProps) => {
  const { t } = useTranslation()

  const { data, hasChange, onChange } = useForm<StockSendDetails>({
    volume: 0,
    dae: "",
    delivery_date: "",
    client: null,
    delivery_site: null,
    delivery_site_country: null,
    mac: false,
    carbure_vendor_certificate: "",
    carbure_vendor: entity,
  })

  function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    onResolve(data)
  }

  const canSave = Boolean(
    hasChange && data.client && data.dae && data.delivery_date && data.volume
  )

  return (
    <Dialog onResolve={onResolve}>
      <DialogTitle text={t("Préparer lot")} />
      <DialogText text={t("Veuillez préciser les détails du lot à envoyer")} />

      <Box as="form" onSubmit={onSubmit}>
        <FormGroup data={data} onChange={onChange}>
          <Fields.Volume />
          <Fields.Dae />
          <Fields.DeliveryDate required />
          <Fields.CarbureSelfCertificate />
          {entity?.has_mac && <Fields.Mac />}
          <Fields.Client required search={!data.mac} />
          <Fields.DeliverySite />
          <Fields.DeliverySiteCountry />
        </FormGroup>

        <DialogButtons>
          <Button
            level="primary"
            disabled={!canSave}
            icon={Check}
            onClick={() => onResolve(data)}
          >
            <Trans>Valider</Trans>
          </Button>
          <Button onClick={() => onResolve()}>
            <Trans>Annuler</Trans>
          </Button>
        </DialogButtons>
      </Box>
    </Dialog>
  )
}
