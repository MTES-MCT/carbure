import React, { Fragment, useEffect, useState } from "react"

import { LotStatus, Transaction, ConvertETBE } from "common/types"

import useForm from "common/hooks/use-form"

import { Box } from "common/components"
import { Input, LabelInput } from "common/components/input"
import { Button } from "common/components/button"
import { Alert } from "common/components/alert"
import { Check, AlertCircle } from "common/components/icons"
import { DialogButtons, PromptFormProps } from "common/components/dialog"
import Select from "common/components/select"
import useAPI from "common/hooks/use-api"
import Table, { Column } from "common/components/table"
import * as C from "transactions/components/list-columns"
import * as api from "../api"

const PCI_ETHANOL = 21
const PCI_ETBE = 27
const ETHANOL_PCI_RATIO_IN_ETBE = 0.37
// const MIN_ETHANOL_AFTER = 98
// const MAX_ETHANOL_AFTER = 100

// function checkPCIRatio(data: ConvertETBE) {
//   const RealPCIEthanol: number = data.volume_ethanol * PCI_ETHANOL
//   const TheoPCIEthanol: number =
//     data.volume_etbe * ETHANOL_PCI_RATIO_IN_ETBE * PCI_ETBE
//   const RealVsTheoPCI: number = (RealPCIEthanol / TheoPCIEthanol) * 100
//   const isOdd: boolean =
//     RealVsTheoPCI > MAX_ETHANOL_AFTER || RealVsTheoPCI < MIN_ETHANOL_AFTER
//   return { isOdd, RealVsTheoPCI }
// }

// function checkVolumeDiff(data: ConvertETBE) {
//   return (
//     data.volume_etbe -
//     (data.volume_ethanol +
//       data.volume_fossile +
//       data.volume_pertes +
//       data.volume_denaturant)
//   )
// }

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

// export const ConvertETBEPrompt = ({
//   onConfirm,
//   onCancel,
// }: PromptFormProps<ConvertETBE>) => {
//   const { data, hasChange, onChange } = useForm<ConvertETBE>({
//     volume_ethanol: 0,
//     volume_etbe: 0,
//     volume_fossile: 0,
//     volume_denaturant: 0,
//     volume_pertes: 0,
//   })

//   function onSubmit(e: React.FormEvent) {
//     e.preventDefault()
//     onConfirm(data)
//   }

//   const { isOdd, RealVsTheoPCI } = checkPCIRatio(data)
//   const volumeDiff: number = checkVolumeDiff(data)

//   const canSave = Boolean(hasChange && volumeDiff === 0)

//   return (
//     <Box as="form" onSubmit={onSubmit}>
//       <LabelInput
//         type="number"
//         label="Volume d'ethanol"
//         name="volume_ethanol"
//         value={data.volume_ethanol}
//         onChange={onChange}
//       />
//       <LabelInput
//         type="number"
//         label="Volume d'ETBE"
//         name="volume_etbe"
//         value={data.volume_etbe}
//         onChange={onChange}
//       />
//       <LabelInput
//         type="number"
//         label="Volume fossile"
//         name="volume_fossile"
//         value={data.volume_fossile}
//         onChange={onChange}
//       />
//       <LabelInput
//         type="number"
//         label="Volume dénaturant"
//         name="volume_denaturant"
//         value={data.volume_denaturant}
//         onChange={onChange}
//       />
//       <LabelInput
//         type="number"
//         label="Volume pertes"
//         name="volume_pertes"
//         value={data.volume_pertes}
//         onChange={onChange}
//       />

//       {isOdd && (
//         <Alert level="warning" icon={AlertTriangle}>
//           Le rapport de PCI Ethanol dans ce lot d'ETBE est de{" "}
//           {RealVsTheoPCI.toFixed(2)}% (Taux habituel entre {MIN_ETHANOL_AFTER}%
//           et {MAX_ETHANOL_AFTER}%){" "}
//         </Alert>
//       )}

//       {volumeDiff !== 0 && (
//         <Alert level="error" icon={AlertCircle}>
//           Les volumes ne correspondent pas ({volumeDiff})
//         </Alert>
//       )}

//       <DialogButtons>
//         <Button
//           level="primary"
//           disabled={!canSave}
//           icon={Check}
//           onClick={() => onConfirm(data)}
//         >
//           Valider
//         </Button>
//         <Button onClick={onCancel}>Annuler</Button>
//       </DialogButtons>
//     </Box>
//   )
// }

export const ConvertETBEComplexPromptFactory = (entityID: number) =>
  function ConvertETBEComplexPrompt({
    onConfirm,
    onCancel,
  }: PromptFormProps<ConvertETBE[]>) {
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
      const volume = (data.volume_etbe * ETHANOL_PCI_RATIO_IN_ETBE * PCI_ETBE) / PCI_ETHANOL // prettier-ignore
      const volume_ethanol = Math.trunc(volume)

      const volume_fossile =
        data.volume_etbe - volume_ethanol - data.volume_denaturant

      patch({ volume_ethanol, volume_fossile })
    }, [patch, data.volume_etbe, data.volume_denaturant])

    useEffect(() => {
      const attributions = getVolumeAttributions(
        stocks.data?.lots ?? [],
        data.volume_ethanol + data.volume_denaturant
      )

      setConversions(attributions)
    }, [stocks.data?.lots, data.volume_ethanol, data.volume_denaturant])

    const convertedVolume: Column<Transaction> = {
      header: "Volume à convertir",
      render: (tx) => (
        <Input
          type="number"
          value={conversions[tx.id] ?? 0}
          onChange={(e) =>
            setConversions({
              ...conversions,
              [tx.id]: parseInt(e.target.value, 10),
            })
          }
        />
      ),
    }

    const lots = stocks.data?.lots ?? []

    const availableETH = lots.reduce((t, tx) => t + tx.lot.volume, 0)
    // const usedETH = Object.values(conversions).reduce((t, c) => t + c, 0)

    // const theoVolumeEth =
    //   (data.volume_etbe * ETHANOL_PCI_RATIO_IN_ETBE * PCI_ETBE) / PCI_ETHANOL

    // const currentETBEETHPciRatio =
    //   (data.volume_ethanol * PCI_ETHANOL) / (data.volume_etbe * PCI_ETBE)

    // const volumeDiff = checkVolumeDiff(data)
    // const { isOdd, RealVsTheoPCI } = checkPCIRatio(data)

    const volumeDiff = compareVolumes(
      data.volume_ethanol + data.volume_denaturant,
      conversions
    )

    const canSave = hasChange && volumeDiff === 0

    const columns = [
      C.carbureID,
      C.biocarburant,
      C.matierePremiere,
      convertedVolume,
      C.ghgReduction,
    ]

    const rows = lots.map((stock) => ({ value: stock }))

    const conversionDetails = Object.keys(conversions).map<ConvertETBE>(
      (txID) => ({
        previous_stock_tx_id: parseInt(txID, 10),
        volume_ethanol: conversions[txID],
        volume_denaturant: data.volume_denaturant,
        volume_etbe: data.volume_etbe,
        volume_fossile: data.volume_fossile,
        volume_pertes: data.volume_pertes,
      })
    )

    return (
      <Box>
        <Select
          value={depot as any}
          options={(depots.data as any) ?? []}
          placeholder="Choisir un dépôt"
          onChange={setDepot as any}
        />

        {depot && (
          <Fragment>
            <LabelInput
              type="number"
              label="Volume d'ETBE"
              name="volume_etbe"
              value={data.volume_etbe}
              onChange={onChange}
            />

            <LabelInput
              type="number"
              label="Volume de Dénaturant"
              name="volume_denaturant"
              value={data.volume_denaturant}
              onChange={onChange}
            />

            <LabelInput
              disabled
              type="number"
              label={`Volume d'Éthanol à convertir (${availableETH} litres disponibles)`}
              name="volume_ethanol"
              value={data.volume_ethanol}
            />

            <LabelInput
              disabled
              type="number"
              label="Volume Fossile"
              name="volume_fossile"
              value={data.volume_fossile}
            />

            {/* <LabelInput
              type="number"
              label="Pertes"
              name="volume_pertes"
              value={data.volume_pertes}
              onChange={onChange}
            /> */}
          </Fragment>
        )}

        {volumeDiff !== 0 && (
          <Alert level="error" icon={AlertCircle}>
            Les volumes ne correspondent pas ({volumeDiff} litres)
          </Alert>
        )}

        {/* {usedETH !== data.volume_ethanol && (
          <Alert level="error" icon={AlertCircle}>
            La somme des volumes à convertir ne correspond pas au volume total
            d'éthanol ({usedETH - data.volume_ethanol} litres)
          </Alert>
        )} */}

        {/* {!isNaN(currentETBEETHPciRatio) && (
          <Alert level={isOdd ? "warning" : "info"} icon={Filter}>
            Part PCI Ethanol de l'ETBE:{" "}
            {(currentETBEETHPciRatio * 100).toFixed(2)}% (
            {RealVsTheoPCI.toFixed(2)}% du ratio théorique de{" "}
            {(ETHANOL_PCI_RATIO_IN_ETBE * 100).toFixed()}%)
          </Alert>
        )} */}

        {rows.length > 0 && <Table columns={columns} rows={rows} />}

        <DialogButtons>
          <Button
            level="primary"
            icon={Check}
            disabled={!canSave}
            onClick={() => onConfirm(conversionDetails)}
          >
            Valider
          </Button>
          <Button onClick={onCancel}>Annuler</Button>
        </DialogButtons>
      </Box>
    )
  }
