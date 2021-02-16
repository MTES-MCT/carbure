import React from "react"

import { Entity, DeliverySite, Country } from "common/types"

import { findCountries, findDeliverySites, findEntities } from "common/api"
import useForm from "common/hooks/use-form"

import { Box } from "common/components"
import { LabelCheckbox, LabelInput } from "common/components/input"
import { Button } from "common/components/button"
import { LabelAutoComplete } from "common/components/autocomplete"
import { DialogButtons, PromptFormProps } from "common/components/dialog"
import { Check } from "common/components/icons"

interface StockSendDetails {
  volume: number
  dae: string
  delivery_date: string
  client_is_in_carbure: boolean
  carbure_client: Entity | null
  unknown_client: string
  delivery_site_is_in_carbure: boolean
  carbure_delivery_site: DeliverySite | null
  unknown_delivery_site: string
  unknown_delivery_site_country: Country | null
}

export const StockSendLotPrompt = ({
  onConfirm,
  onCancel,
}: PromptFormProps<StockSendDetails>) => {
  const { data, hasChange, onChange } = useForm<StockSendDetails>({
    volume: 0,
    dae: "",
    delivery_date: "",

    client_is_in_carbure: true,
    carbure_client: null,
    unknown_client: "",

    delivery_site_is_in_carbure: true,
    carbure_delivery_site: null,
    unknown_delivery_site: "",
    unknown_delivery_site_country: null,
  })

  function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    onConfirm(data)
  }

  const canSave = Boolean(
    hasChange &&
      (data.carbure_client || data.unknown_client) &&
      data.dae &&
      data.delivery_date &&
      (data.carbure_delivery_site || data.unknown_delivery_site) &&
      data.volume
  )

  return (
    <Box as="form" onSubmit={onSubmit}>
      <LabelInput
        type="number"
        label="Volume"
        name="volume"
        value={data.volume}
        onChange={onChange}
      />

      <LabelInput label="DAE" name="dae" value={data.dae} onChange={onChange} />

      <LabelInput
        type="date"
        label="Date de livraison"
        name="delivery_date"
        value={data.delivery_date}
        onChange={onChange}
      />

      <LabelCheckbox
        name="client_is_in_carbure"
        label="Client enregistré sur Carbure ?"
        checked={data.client_is_in_carbure}
        onChange={onChange}
      />

      {data.client_is_in_carbure ? (
        <LabelAutoComplete
          label="Client"
          placeholder="Rechercher un client..."
          name="carbure_client"
          value={data.carbure_client}
          getValue={(c) => `${c.id}`}
          getLabel={(c) => c.name}
          getQuery={findEntities}
          onChange={onChange}
        />
      ) : (
        <LabelInput
          label="Client"
          name="unknown_client"
          value={data.unknown_client}
          onChange={onChange}
        />
      )}

      <LabelCheckbox
        name="delivery_site_is_in_carbure"
        label="Site de livraison enregistré sur Carbure ?"
        checked={data.delivery_site_is_in_carbure}
        onChange={onChange}
      />

      {data.delivery_site_is_in_carbure ? (
        <LabelAutoComplete
          label="Site de livraison"
          placeholder="Rechercher un site de livraison..."
          name="carbure_delivery_site"
          value={data.carbure_delivery_site}
          getValue={(d) => d.depot_id}
          getLabel={(d) => d.name}
          getQuery={findDeliverySites}
          onChange={onChange}
        />
      ) : (
        <React.Fragment>
          <LabelInput
            label="Site de livraison"
            name="unknown_delivery_site"
            value={data.unknown_delivery_site}
            onChange={onChange}
          />
        </React.Fragment>
      )}

      {data.delivery_site_is_in_carbure ? (
        <LabelInput
          disabled
          label="Pays de livraison"
          value={data.carbure_delivery_site?.country?.name}
        />
      ) : (
        <LabelAutoComplete
          disabled={true}
          label="Pays de livraison"
          name="unknown_delivery_site_country"
          value={data.unknown_delivery_site_country}
          getValue={(c) => c.code_pays}
          getLabel={(c) => c.name}
          getQuery={findCountries}
          onChange={onChange}
        />
      )}

      <DialogButtons>
        <Button
          level="primary"
          disabled={!canSave}
          icon={Check}
          onClick={() => onConfirm(data)}
        >
          Valider
        </Button>
        <Button onClick={onCancel}>Annuler</Button>
      </DialogButtons>
    </Box>
  )
}
