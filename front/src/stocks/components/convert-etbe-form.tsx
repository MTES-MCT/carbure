import { Fragment, useEffect, useState } from "react"

import { LotStatus, Transaction, ConvertETBE } from "common/types"
import useForm from "common/hooks/use-form"
import { Box } from "common/components"
import { Input, LabelInput } from "common/components/input"
import { Button } from "common/components/button"
import { Alert } from "common/components/alert"
import { Check, AlertCircle } from "common/components/icons"
import {
  Dialog,
  DialogButtons,
  DialogTitle,
  PromptProps,
} from "common/components/dialog"
import Select from "common/components/select"
import useAPI from "common/hooks/use-api"
import Table, { Column } from "common/components/table"
import * as C from "transactions/components/list-columns"
import * as api from "../api"

const PCI_ETHANOL = 21
const PCI_ETBE = 27
const ETHANOL_PCI_RATIO_IN_ETBE = 0.37

function compareVolumes(volume: number, attributions: { [k: string]: number }) {
  const total_attributions = Object.values(attributions).reduce(
    (total, vol) => total + vol,
    0
  )

  return volume - total_attributions
}

function getVolumeAttributions(stocks: Transaction[], volume: number) {
  let remainingVolume = volume
  const attributions: { [k: string]: number } = {}

  for (const tx of stocks) {
    if (remainingVolume <= 0) {
      break
    }

    attributions[tx.id] = Math.min(remainingVolume, tx.lot.volume)
    remainingVolume -= attributions[tx.id]
  }

  return attributions
}

type ConvertETBEPromptProps = PromptProps<ConvertETBE[]> & {
  entityID: number
}

export const ConvertETBEComplexPrompt = ({
  entityID,
  onResolve,
}: ConvertETBEPromptProps) => {
  const [depot, setDepot] = useState<string | null>(null)

  const { data, hasChange, onChange, patch } = useForm<ConvertETBE>({
    volume_etbe: 0,
    volume_ethanol: 0,
    volume_pertes: 0,
    volume_denaturant: 0,
    volume_fossile: 0,
  })

  const [conversions, setConversions] = useState<{ [key: string]: number }>({}) // prettier-ignore

  const [depots, getDepots] = useAPI(api.getDepots)
  const [stocks, getStocks] = useAPI(api.getStocks)

  const lots = stocks.data?.lots ?? []
  const vEthanolInStock = lots.reduce((t, tx) => t + tx.lot.volume, 0)

  useEffect(() => {
    getDepots(entityID, "ETH")
  }, [getDepots])

  useEffect(() => {
    if (depot) {
      getStocks(
        entityID,
        { delivery_sites: [depot], biocarburants: ["ETH"] },
        LotStatus.Stock
      )
    }
  }, [depot, getStocks])

  useEffect(() => {
    /*
        ratio_pci_eth_in_etbe = 0.37
        pci_etbe = 27
        pci_ethanol = 21

        vol_eth_en_stock = stocks.total
        vol_etbe_a_produire = formulaire.volume_etbe
        vol_denaturant_dans_stocks = formulaire.volume_denaturant

        vol_eth_pour_etbe = (vol_etbe_a_produire * ratio_pci_eth_in_etbe * pci_etbe) / pci_ethanol
        vol_denaturant_pour_etbe = vol_denaturant_dans_stocks * (vol_eth_pour_etbe / vol_eth_en_stock)

        vol_eth_a_deduire = vol_eth_pour_etbe - vol_denaturant_pour_etbe
        vol_fossile_pour_etbe = vol_etbe_a_produire - vol_eth_pour_etbe

        formulaire.volume_eth = vol_eth_a_deduire
        formulaire.volume_fossile = vol_fossile_pour_etbe

        et dispatcher vol_eth_a_deduire sur les stocks disponibles
      */

    const vETBE = data.volume_etbe
    const vDenaturantInStock = data.volume_denaturant
    const vEthanolForETBE = (vETBE * ETHANOL_PCI_RATIO_IN_ETBE * PCI_ETBE) / PCI_ETHANOL // prettier-ignore
    const vEthanolFromStock = vEthanolForETBE - (vEthanolForETBE * (vDenaturantInStock / vEthanolInStock)) // prettier-ignore
    const vFossile = vETBE - vEthanolForETBE

    patch({
      volume_ethanol: vEthanolFromStock || 0,
      volume_fossile: vFossile || 0,
    })
  }, [patch, data.volume_etbe, data.volume_denaturant, vEthanolInStock])

  useEffect(() => {
    const attributions = getVolumeAttributions(
      stocks.data?.lots ?? [],
      data.volume_ethanol
    )

    setConversions(attributions)
  }, [stocks.data?.lots, data.volume_ethanol, data.volume_denaturant])

  const convertedVolume: Column<Transaction> = {
    header: "Volume à convertir",
    render: (tx) => (
      <Input
        type="number"
        value={conversions[tx.id]?.toFixed(2) ?? 0}
        onChange={(e) =>
          setConversions({
            ...conversions,
            [tx.id]: parseInt(e.target.value, 10),
          })
        }
      />
    ),
  }

  const volumeDiff = compareVolumes(data.volume_ethanol, conversions)

  const canSave = hasChange && volumeDiff === 0

  const columns = [
    C.padding,
    C.carbureID,
    C.biocarburant,
    C.matierePremiere,
    convertedVolume,
    C.ghgReduction,
    C.padding,
  ]

  const rows = lots.map((stock) => ({ value: stock }))

  const vEthanolForETBE = (data.volume_etbe * ETHANOL_PCI_RATIO_IN_ETBE * PCI_ETBE) / PCI_ETHANOL // prettier-ignore
  const vDenaturantUsed = vEthanolForETBE * (data.volume_denaturant / vEthanolInStock) // prettier-ignore

  const conversionDetails = Object.keys(conversions).map<ConvertETBE>(
    (txID) => {
      const ratioOfTotal = conversions[txID] / data.volume_ethanol

      return {
        previous_stock_tx_id: parseInt(txID, 10),
        volume_ethanol: conversions[txID],
        volume_denaturant: vDenaturantUsed * ratioOfTotal,
        volume_etbe: data.volume_etbe * ratioOfTotal,
        volume_fossile: data.volume_fossile * ratioOfTotal,
        volume_pertes: data.volume_pertes * ratioOfTotal,
      }
    }
  )

  return (
    <Dialog onResolve={onResolve}>
      <DialogTitle text="Conversion ETBE" />

      <Box>
        <Select
          value={depot as any}
          options={(depots.data as any) ?? []}
          placeholder="Choisir un dépôt"
          onChange={setDepot as any}
          style={{ marginTop: 24, marginBottom: 16 }}
        />

        {depot && (
          <Fragment>
            <LabelInput
              type="number"
              label="Volume d'ETBE à produire"
              name="volume_etbe"
              value={data.volume_etbe}
              onChange={onChange}
            />

            <LabelInput
              type="number"
              label="Volume total de dénaturant dans vos stocks"
              name="volume_denaturant"
              value={data.volume_denaturant}
              onChange={onChange}
            />

            <LabelInput
              readOnly
              type="number"
              label={`Volume d'Éthanol à convertir (${vEthanolInStock.toFixed(
                2
              )} litres disponibles)`}
              name="volume_ethanol"
              value={data.volume_ethanol.toFixed(2)}
            />
          </Fragment>
        )}

        {!isNaN(volumeDiff) && volumeDiff !== 0 && (
          <Alert level="error" icon={AlertCircle}>
            Les volumes ne correspondent pas ({volumeDiff.toFixed(2)} litres)
          </Alert>
        )}

        {rows.length > 0 && (
          <div style={{ marginLeft: -24, marginRight: -24 }}>
            <Table columns={columns} rows={rows} />
          </div>
        )}

        <DialogButtons>
          <Button
            level="primary"
            icon={Check}
            disabled={!canSave}
            onClick={() => onResolve(conversionDetails)}
          >
            Valider
          </Button>
          <Button onClick={() => onResolve()}>Annuler</Button>
        </DialogButtons>
      </Box>
    </Dialog>
  )
}
