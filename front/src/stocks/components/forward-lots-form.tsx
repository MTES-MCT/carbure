import React, { Fragment, useEffect, useState } from "react"

import { Entity, ProductionCertificate } from "common/types"

import useForm from "common/hooks/use-form"

import { Box } from "common/components"
import { Button } from "common/components/button"
import { Check, AlertCircle } from "common/components/icons"
import { DialogButtons, PromptFormProps } from "common/components/dialog"
import {findEntities} from "common/api"
import {findCertificates} from "settings/api"
import { LabelAutoComplete } from "common/components/autocomplete"

export interface ForwardClientFormState {
  carbure_client: Entity | null
  certificate: ProductionCertificate | null
}

const initialState: ForwardClientFormState = {
  carbure_client: null,
  certificate: null
}

export const ForwardLotsClientSelectionPromptFactory = (entityID: number) =>
  function ForwardLotsClientSelectionPrompt({
    onConfirm,
    onCancel,
  }: PromptFormProps<ForwardClientFormState>) {
    const { data, onChange} = useForm<ForwardClientFormState>(initialState) // prettier-ignore
    const canSave = data?.carbure_client !== null && data?.certificate !== null

    return (
      <Box>
        <LabelAutoComplete
          label="Client"
          name="carbure_client"
          value={data.carbure_client}
          getValue={c => c.id.toString()}
          getLabel={c => c.name}
          getQuery={findEntities}
          onChange={onChange}
          minLength={0}
        />

        <LabelAutoComplete
          label="Certificat"
          name="certificate"
          value={data.certificate}
          getValue={c => c.certificate_id}
          getLabel={(c) => {return `${c.type} - ${c.holder} - ${c.certificate_id}`}}
          getQuery={findCertificates}
          queryArgs={[entityID]}
          onChange={onChange}
          minLength={0}
        />

        <DialogButtons>
          <Button
            level="primary"
            icon={Check}
            disabled={!canSave}
            onClick={() => onConfirm(data)}
          >
            Valider
          </Button>
          <Button onClick={onCancel}>Annuler</Button>
        </DialogButtons>
      </Box>
    )
  }
