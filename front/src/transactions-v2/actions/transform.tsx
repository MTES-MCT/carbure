import { useState, useMemo } from "react"
import { useTranslation } from "react-i18next"
import useEntity from "carbure/hooks/entity"
import { useQuery, useMutation } from "common-v2/hooks/async"
import { usePortal } from "common-v2/components/portal"
import { useNotify } from "common-v2/components/notifications"
import Form, { Fieldset, useForm } from "common-v2/components/form"
import Alert from "common-v2/components/alert"
import Button from "common-v2/components/button"
import Menu from "common-v2/components/menu"
import Dialog from "common-v2/components/dialog"
import Table, { Cell } from "common-v2/components/table"
import { NumberInput } from "common-v2/components/input"
import { Flask, Return, AlertCircle } from "common-v2/components/icons"
import { StockQuery, TransformETBEPayload } from "../types"
import { formatPercentage, formatNumber } from "common-v2/utils/formatters"
import * as api from '../api'


const PART_ETH_IN_ETBE = 0.47
const CONVERT_20_TO_15 = 0.995

interface TransformManyButtonProps {
  query: StockQuery
  selection: number[]
}

export const TransformManyButton = ({ query, selection }: TransformManyButtonProps) => {
  const { t } = useTranslation()

  const portal = usePortal()

  return <Menu icon={Flask} variant="primary" label={"Transformer"} items={[
    {
      label: t("ETBE"),
      action: () =>
        portal((close) => <ETBEDialog query={query} selection={selection} onClose={close} />),
    },
  ]} />
}

interface ETBEDialogProps {
  query: StockQuery
  selection: number[]
  onClose: () => void
}

export const ETBEDialog = ({ query, selection, onClose }: ETBEDialogProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()

  const subQuery = useMemo(() => 
    selection?.length
      ? { entity_id: entity.id, biofuels: ['ETH'], selection }
      : { ...query, biofuels: ['ETH'] }
  , [query])

  const stocks = useQuery(api.getStocks, {
    key: 'ethanol-stocks',
    params: [subQuery]
  })

  const [attributions, setAttributions] = useState<Record<number, number>>({})

  const { value, bind } = useForm({
    volume_etbe: 0 as number | undefined,
    volume_ethanol: 0 as number | undefined,
    volume_denaturant: 0 as number | undefined,
  })

  const transformETBE = useMutation(api.transformETBE, {
    invalidates: ['snapshot', 'stocks'],
    onSuccess: () => {
      notify(t("Les lots d'ETBE ont bien été créés !"), { variant: 'success' })
      onClose()
    },
    onError: () => {
      notify(t("Les lots d'ETBE n'ont pas pu être créés !"), { variant: 'danger' })
    },
  })

  function onTransform() {
    const payload = Object.entries(attributions)
      .map<TransformETBEPayload>(([stockID, volume]) => {
        const {
          volume_denaturant = 0,
          volume_etbe = 0,
          volume_ethanol = 0
        } = value

        const ratio = volume / volume_ethanol
        return {
          volume_ethanol: volume,
          volume_etbe: ratio * volume_etbe,
          volume_etbe_eligible: ratio * volEligibleETBE,
          volume_denaturant: ratio * volume_denaturant,
          stock_id: parseInt(stockID, 10),
          transformation_type: 'ETH_ETBE'
        }
      })
      .filter((d) => d.volume_ethanol > 0)

    transformETBE.execute(entity.id, payload)
  }

  const volumeDiff = compareVolumes(value.volume_ethanol!, attributions)

  const usedVolume = value.volume_ethanol! * CONVERT_20_TO_15 + value.volume_denaturant!
  const ratio = usedVolume / value.volume_etbe!

  const volEligibleETBE = value.volume_etbe! * (ratio / PART_ETH_IN_ETBE)

  const ratioEthToETBE = (value.volume_ethanol! / value.volume_etbe!) * 100.0
  const ratioEthToETBEWithDenaturant = ((value.volume_ethanol! + value.volume_denaturant!) / value.volume_etbe!) * 100.0

  const stockRows = stocks.result?.data.data?.stocks ?? []

  return (
    <Dialog limit onClose={onClose}>
      <header>
        <h1>
          {t("Transformation en ETBE")}
        </h1>
      </header>
      <main>
        {stockRows.length === 0 && (
          <section>
            <Alert icon={AlertCircle} variant="warning" label={t("Aucun lot d'éthanol trouvé dans les stocks sélectionnés")} />
          </section>
        )}

        {stockRows.length > 0 && (
          <section>
            <Form id="etbe" variant="columns">
              <Fieldset>
                <NumberInput
                  label={t("Volume d'ETBE produit")}
                  {...bind("volume_etbe")}
                />
                <NumberInput
                  label={t("Volume d'Éthanol utilisé")}
                  {...bind("volume_ethanol")}
                />
              </Fieldset>
              <Fieldset>
                <NumberInput
                  disabled
                  label={t("Volume d'ETBE éligible (à titre informatif)")}
                  value={isNaN(volEligibleETBE) ? 0 : Math.round(volEligibleETBE)}
                />
                <NumberInput
                  label={t("Volume total de dénaturant")}
                  {...bind("volume_denaturant")}
                />
              </Fieldset>
            </Form>
          </section>
        )}

        {stockRows.length > 0 && (
          <Table
            rows={stockRows}
            columns={[
              {
                header: t("Dépôt"),
                orderBy: (stock) => stock.depot?.name ?? '',
                cell: (stock) => <Cell text={stock.depot?.name} />
              },
              {
                header: t("Biocarburant"),
                cell: (stock) => <Cell text={t(stock.biofuel!.code, { ns: 'biofuels' })} sub={stock.remaining_volume} />
              },
              {
                header: t("Matière première"),
                cell: (stock) => <Cell text={t(stock.feedstock!.code, { ns: 'feedstocks' })} />
              },
              {
                small: true,
                header: t("Réd. GES"),
                cell: (stock) => <Cell text={formatPercentage(stock.ghg_reduction)} />,
              },
              {
                header: t("Volume à prélever (litres)"),
                cell: (stock) => (
                  <NumberInput
                    value={attributions[stock.id]}
                    onChange={volume => setAttributions({ ...attributions, [stock.id]: volume ?? 0 })}
                  />
                ),
              }
            ]}
          />
        )}
      </main>
      <footer>
        {!isNaN(volumeDiff) && volumeDiff !== 0 && (
          <Alert variant="danger" icon={AlertCircle}>
            {t("Les volumes attribués ne correspondent pas ({{ diff }} litres)", { diff: formatNumber(volumeDiff) })}
          </Alert>
        )}

        <Button
          asideX
          icon={Return}
          label={t("Retour")}
          action={onClose}
        />
        <Button
          disabled={volumeDiff !== 0}
          loading={transformETBE.loading}
          submit="etbe"
          variant="primary"
          icon={Flask}
          label={t("Créer ETBE")}
          action={onTransform}
        />
      </footer>
    </Dialog >
  )
}


function compareVolumes(volume: number, attributions: Record<number, number>) {
  let total_attributions = Object.values(attributions).reduce(
    (total, vol) => total + vol,
    0
  )
  return volume - total_attributions
}