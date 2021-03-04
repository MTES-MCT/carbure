import React from "react"

import { Entity, DeliverySite, Country } from "common/types"

import { findCountries, findDeliverySites, findEntities } from "common/api"
import useForm from "common/hooks/use-form"

import { Box } from "common/components"
import { LabelCheckbox, LabelInput } from "common/components/input"
import { Button } from "common/components/button"
import { Alert } from "common/components/alert"
import { LabelAutoComplete } from "common/components/autocomplete"
import { DialogButtons, PromptFormProps } from "common/components/dialog"
import { Check, AlertCircle, AlertTriangle } from "common/components/icons"

interface ConvertETBE {
  entity_id: number,
  previous_stock_tx_id: number,
  volume_ethanol: number,
  volume_etbe: number,
  volume_fossile: number,
  volume_denaturant: number,
  volume_pertes: number
}

const PCI_ETHANOL = 21
const PCI_ETBE = 27
const ETHANOL_PCI_RATIO_IN_ETBE = 0.37
const MIN_ETHANOL_AFTER = 98
const MAX_ETHANOL_AFTER = 100

export const ConvertETBEPrompt = ({
  onConfirm,
  onCancel,
}: PromptFormProps<ConvertETBE>) => {
  const { data, hasChange, onChange } = useForm<ConvertETBE>({
    entity_id: 0,
    previous_stock_tx_id: 0,
    volume_ethanol: 0,
    volume_etbe: 0,
    volume_fossile: 0,
    volume_denaturant: 0,
    volume_pertes: 0
  })

  function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    onConfirm(data)
  }


  const PCIEthanol: number = data.volume_ethanol * PCI_ETHANOL
  const PCIETBEPartEthanol: number = data.volume_etbe * ETHANOL_PCI_RATIO_IN_ETBE * PCI_ETBE
  const PercentagePciEtbeEth: number = (PCIETBEPartEthanol / PCIEthanol) * 100
  const isOdd: boolean = PercentagePciEtbeEth > MAX_ETHANOL_AFTER || PercentagePciEtbeEth < MIN_ETHANOL_AFTER
  const volumeDiff: number = data.volume_etbe - (data.volume_ethanol + data.volume_fossile + data.volume_pertes + data.volume_denaturant)

  const canSave = Boolean(
    hasChange && 
    (volumeDiff === 0)
  )

  return (
    <Box as="form" onSubmit={onSubmit}>
      <LabelInput
        type="number"
        label="Volume d'ethanol"
        name="volume_ethanol"
        value={data.volume_ethanol}
        onChange={onChange}
      />
      <LabelInput
        type="number"
        label="Volume d'ETBE"
        name="volume_etbe"
        value={data.volume_etbe}
        onChange={onChange}
      />
      <LabelInput
        type="number"
        label="Volume fossile"
        name="volume_fossile"
        value={data.volume_fossile}
        onChange={onChange}
      />
      <LabelInput
        type="number"
        label="Volume dénaturant"
        name="volume_denaturant"
        value={data.volume_denaturant}
        onChange={onChange}
      />
      <LabelInput
        type="number"
        label="Volume pertes"
        name="volume_pertes"
        value={data.volume_pertes}
        onChange={onChange}
      />

      {isOdd && (<Alert level="warning" icon={AlertTriangle}>Le rapport de PCI Ethanol dans ce lot d'ETBE est de {PercentagePciEtbeEth.toFixed(2)}% (Taux habituel entre {MIN_ETHANOL_AFTER}% et {MAX_ETHANOL_AFTER}%) </Alert>)}

      {volumeDiff !== 0 && (<Alert level="error" icon={AlertCircle}>Les volumes ne correspondent pas ({volumeDiff})</Alert>)}

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
