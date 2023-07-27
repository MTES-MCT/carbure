import { findBiofuels, findFeedstocks } from "carbure/api"
import useEntity from "carbure/hooks/entity"
import { Entity } from "carbure/types"
import { normalizeBiofuel, normalizeFeedstock } from "carbure/utils/normalizers"
import AutoComplete from "common/components/autocomplete"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import { Form, useForm } from "common/components/form"
import { Plus, Return, Save } from "common/components/icons"
import { NumberInput } from "common/components/input"
import Table, { Cell, Column } from "common/components/table"
import { useMutation, useQuery } from "common/hooks/async"
import { compact } from "common/utils/collection"
import { formatNumber } from "common/utils/formatters"
import {
  DoubleCountingApplication,
  DoubleCountingProduction,
  QuotaDetails,
} from "double-counting/types"
import { Trans, useTranslation } from "react-i18next"
import * as api from "../api/double-counting"

type DoubleCountingProductionDialogProps = {
  add?: boolean
  dcaID: number
  production?: DoubleCountingProduction
  entity: Entity
  onClose: () => void
}

const DoubleCountingProductionDialog = ({
  add,
  dcaID,
  production,
  onClose,
}: DoubleCountingProductionDialogProps) => {
  const { t } = useTranslation()
  const entity = useEntity()

  const { value, bind } = useForm<Partial<DoubleCountingProduction>>(
    production ?? {
      year: new Date().getFullYear(),
      feedstock: undefined,
      biofuel: undefined,
      estimated_production: 0,
      max_production_capacity: 0,
      requested_quota: 0,
    }
  )

  const addProduction = useMutation(api.addDoubleCountingProduction, {
    invalidates: ["dc-details"],
    onSuccess: () => onClose(),
  })

  const updateProduction = useMutation(api.updateDoubleCountingProduction, {
    invalidates: ["dc-details"],
  })

  async function saveProduction() {
    if (
      !value.year ||
      !value.feedstock ||
      !value.biofuel ||
      !value.requested_quota ||
      !value.estimated_production ||
      !value.max_production_capacity
    ) {
      return
    }

    if (add) {
      await addProduction.execute(
        entity.id,
        dcaID,
        value.year,
        value.feedstock.code,
        value.biofuel.code,
        value.estimated_production,
        value.max_production_capacity,
        value.requested_quota
      )
    } else if (production) {
      await updateProduction.execute(
        entity.id,
        production.id,
        value.estimated_production,
        value.max_production_capacity,
        value.requested_quota
      )
    }
  }

  const disabled =
    !value.year ||
    !value.feedstock ||
    !value.biofuel ||
    !value.requested_quota ||
    !value.estimated_production ||
    !value.max_production_capacity

  const loading = addProduction.loading || updateProduction.loading

  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>{t("Production")}</h1>
      </header>
      <main>
        <section>
          <p>
            {t(
              "Précisez les informations concernant votre production de biocarburant dans le formularie ci-dessous."
            )}
          </p>
        </section>
        <section>
          <Form id="dc-production" onSubmit={saveProduction}>
            <NumberInput
              autoFocus
              label={t("Année")}
              {...bind("year")}
              disabled={!add}
            />
            <AutoComplete
              label={t("Matière première")}
              normalize={normalizeFeedstock}
              getOptions={(search) => findFeedstocks(search, true)}
              defaultOptions={compact([value.feedstock])}
              {...bind("feedstock")}
              disabled={!add}
            />
            <AutoComplete
              label={t("Biocarburant")}
              getOptions={findBiofuels}
              defaultOptions={compact([value.biofuel])}
              normalize={normalizeBiofuel}
              {...bind("biofuel")}
              disabled={!add}
            />
            <NumberInput
              label={t("Production maximale")}
              type="number"
              {...bind("max_production_capacity")}
            />
            <NumberInput
              label={t("Production estimée")}
              type="number"
              {...bind("estimated_production")}
            />
            <NumberInput
              label={t("Quota demandé")}
              type="number"
              {...bind("requested_quota")}
            />
          </Form>
        </section>
      </main>
      <footer>
        <Button
          asideX
          disabled={disabled}
          submit="dc-production"
          variant="primary"
          loading={loading}
          icon={add ? Plus : Save}
        >
          {add ? (
            <Trans>Ajouter une production</Trans>
          ) : (
            <Trans>Enregistrer les modifications</Trans>
          )}
        </Button>
        <Button icon={Return} action={onClose} label={t("Annuler")} />
      </footer>
    </Dialog>
  )
}

type QuotasTableProps = {
  entity: Entity
  application: DoubleCountingApplication | undefined
}

const QuotasTable = ({ entity, application }: QuotasTableProps) => {
  const { t } = useTranslation()

  const entityID = entity?.id ?? -1
  const dcaID = application?.id ?? -1

  const details = useQuery(api.getQuotaDetails, {
    key: "quota-details",
    params: [entityID, dcaID],
  })

  const columns: Column<QuotaDetails>[] = [
    {
      header: t("Biocarburant"),
      cell: (d) => <Cell text={d.biofuel.name} />,
    },
    {
      header: t("Matière première"),
      cell: (d) => <Cell text={d.feedstock.name} />,
    },
    { header: t("Nombre de lots"), cell: (d) => d.nb_lots },
    {
      header: t("Volume produit"),
      cell: (d) => (
        <Cell
          text={`${formatNumber(d.volume)} L`}
          sub={`${d.current_production_weight_sum_tonnes} t`}
        />
      ),
    },
    {
      header: t("Quota approuvé"),
      cell: (d) => <Cell text={formatNumber(d.approved_quota)} />,
    },
    {
      header: t("Progression des quotas"),
      cell: (d) => (
        <progress
          max={d.approved_quota}
          value={d.current_production_weight_sum_tonnes}
          title={`${d.current_production_weight_sum_tonnes} / ${d.approved_quota}`}
        />
      ),
    },
  ]

  const rows = details.result?.data.data ?? []
  return <Table loading={details.loading} columns={columns} rows={rows} />
}

export default DoubleCountingProductionDialog
