import React, { Fragment, useEffect, useState } from "react"

import { Entity, ProductionCertificate } from "common/types"

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
import { findEntities } from "common/api"
import { findCertificates } from "settings/api"
import { LabelAutoComplete } from "common/components/autocomplete"

export interface ForwardClientFormState {
  carbure_client: Entity | null
  certificate: ProductionCertificate | null
}

const initialState: ForwardClientFormState = {
  carbure_client: null,
  certificate: null,
}

type ForwardLotsClientSelectionPrompt = PromptProps<ForwardClientFormState> & {
  entityID: number
}

export const ForwardLotsClientSelectionPrompt = ({
  entityID,
  onResolve,
}: ForwardLotsClientSelectionPrompt) => {
  const { data, onChange} = useForm<ForwardClientFormState>(initialState) // prettier-ignore
  const canSave = data?.carbure_client !== null && data?.certificate !== null

  return (
    <Dialog onResolve={onResolve}>
      <DialogTitle text="Forward Lots" />
      <DialogText text="Vous pouvez utiliser cette interface pour transférer les lots dans le cadre d'une activité d'intermédiaire sans stockage." />

      <Box>
        <LabelAutoComplete
          label="Client"
          name="carbure_client"
          value={data.carbure_client}
          getValue={(c) => c.id.toString()}
          getLabel={(c) => c.name}
          getQuery={findEntities}
          onChange={onChange}
          minLength={0}
        />

        <LabelAutoComplete
          label="Certificat"
          name="certificate"
          value={data.certificate}
          getValue={(c) => c.certificate_id}
          getLabel={(c) => `${c.type} - ${c.holder} - ${c.certificate_id}`}
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
