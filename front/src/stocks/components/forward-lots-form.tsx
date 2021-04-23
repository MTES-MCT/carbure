import React, { Fragment, useEffect, useState } from "react"

import { Certificate, Entity, ProductionCertificate } from "common/types"

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
import { findEntities, findCertificates } from "common/api"
import { LabelAutoComplete } from "common/components/autocomplete"

export interface ForwardClientFormState {
  carbure_client: Entity | null
  certificate: string | null
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
      <DialogTitle text="Transférer des lots" />
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
          getValue={(v) => v}
          getLabel={(v) => v}
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
