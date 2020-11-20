import React, { useState } from "react"
import { Box, Button, LabelInput } from "../system"
import { DialogButtons, PromptFormProps } from "../system/dialog"

interface StockSendDetails {
  volume: number,
  client: string,
  delivery_date: string,
  delivery_site: string,
  dae: string
}

export const StockSendLotPrompt = ({
  onConfirm,
  onCancel,
}: PromptFormProps<StockSendDetails>) => {
  const [volume, setVolume] = useState(0)
  const [client, setClient] = useState("")
  const [delivery_site, setDeliverySite] = useState("")
  const [delivery_date, setDeliveryDate] = useState("")
  const [dae, setDae] = useState("")

  function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    onConfirm({ volume, client, delivery_date, delivery_site, dae })
  }

  return (
    <Box as="form" onSubmit={onSubmit} >
      
      <LabelInput
        label="Volume"
        value={volume}
        onChange={(e) => setVolume(parseInt(e.target.value))}
      />
      <LabelInput
        label="Client"
        value={client}
        onChange={(e) => setClient(e.target.value)}
      />
      <LabelInput
        label="Date de livraison"
        value={client}
        onChange={(e) => setDeliveryDate(e.target.value)}
      />
      <LabelInput
        label="Site de livraison"
        value={client}
        onChange={(e) => setDeliverySite(e.target.value)}
      />
      <LabelInput
        label="DAE"
        value={client}
        onChange={(e) => setDae(e.target.value)}
      />

      <DialogButtons>
        <Button
          level="primary"
          disabled={!volume || !client || !delivery_date || !delivery_site || !dae}
          onClick={() => onConfirm({ volume, client, delivery_date, delivery_site, dae })}
        >
          OK
        </Button>
        <Button onClick={onCancel}>Annuler</Button>
      </DialogButtons>
    </Box>
  )
}