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
import { EntitySelection } from "carbure/hooks/use-entity"

export interface StockSendDetails {
  volume: number
  dae: string
  delivery_date: string
  client: Entity | string | null
  delivery_site: DeliverySite | string | null
  delivery_site_country: Country | null
  mac: boolean
}

type StockSendLotPromptProps = {
  entity: EntitySelection
} & PromptProps<StockSendDetails>

export const StockSendLotPrompt = ({
  entity,
  onResolve,
}: StockSendLotPromptProps) => {
  const { data, hasChange, onChange } = useForm<StockSendDetails>({
    volume: 0,
    dae: "",
    delivery_date: "",
    client: null,
    delivery_site: null,
    delivery_site_country: null,
    mac: false,
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
      <DialogTitle text="Préparer lot" />
      <DialogText text="Veuillez préciser les détails du lot à envoyer" />

      <Box as="form" onSubmit={onSubmit}>
        <FormGroup data={data} onChange={onChange}>
          <Fields.Volume />
          <Fields.Dae />
          <Fields.DeliveryDate required />
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
            Valider
          </Button>
          <Button onClick={() => onResolve()}>Annuler</Button>
        </DialogButtons>
      </Box>
    </Dialog>
  )
}
