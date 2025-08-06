import { NumberInput, RadioGroup } from "common/components/inputs2"
import { SelectDsfr } from "common/components/selects2"
import { EditableCard } from "common/molecules/editable-card"
import { useTranslation } from "react-i18next"
import {
  useMutateContractInfos,
  useInstallationCategoryOptions,
  useTariffReferenceOptions,
} from "./contract-infos.hooks"
import { Grid } from "common/components/scaffold"
import { Autocomplete } from "common/components/autocomplete2"
import { findBuyerBiomethaneEntities } from "../../../api"
import { useForm } from "common/components/form2"
import { apiTypes } from "common/services/api-fetch.types"
import { DeepPartial, ReplaceNullWithUndefined } from "common/types"
import { isTariffReference2011Or2020 } from "./contract-infos.utils"
import { getYesNoOptions } from "common/utils/normalizers"
import { Button } from "common/components/button2"
import { BiomethaneEntityConfigContract } from "biomethane/types"

type ContractInfosForm = DeepPartial<
  ReplaceNullWithUndefined<apiTypes["BiomethaneEntityConfigContractAddRequest"]>
>

export const ContractInfos = ({
  contract,
}: {
  contract?: BiomethaneEntityConfigContract
}) => {
  const { t } = useTranslation()
  const { bind, value } = useForm<ContractInfosForm>({})
  const tariffReferenceOptions = useTariffReferenceOptions()
  const installationCategoryOptions = useInstallationCategoryOptions()
  const { execute: updateContract, loading } = useMutateContractInfos(
    contract !== undefined
  )

  const handleSubmit = (
    form: apiTypes["BiomethaneEntityConfigContractAddRequest"]
  ) => {
    updateContract(form!)
  }

  return (
    <EditableCard
      title={t("Caractéristiques du contrat d’achat à tarif réglementé")}
    >
      <EditableCard.Form onSubmit={handleSubmit}>
        <Grid cols={2} gap="lg">
          <SelectDsfr
            label={t("Référence de l'arrêté tarifaire")}
            options={tariffReferenceOptions}
            required
            {...bind("tariff_reference")}
          />
          <Autocomplete
            label={t("Acheteur")}
            getOptions={findBuyerBiomethaneEntities}
            normalize={(entity) => ({
              label: entity.name,
              value: entity.id,
            })}
            required
            {...bind("buyer")}
          />
        </Grid>
        <SelectDsfr
          label={t("Catégorie d'installation")}
          options={installationCategoryOptions}
          required
          {...bind("installation_category")}
        />

        {isTariffReference2011Or2020(value.tariff_reference) && (
          <>
            <Grid cols={2} gap="lg">
              <NumberInput
                label={t("Cmax (Nm³/h)")}
                {...bind("cmax")}
                required
              />
              <RadioGroup
                label={t("Annualisation du contrôle de la Cmax")}
                options={getYesNoOptions()}
                orientation="horizontal"
                required
                {...bind("cmax_annualized")}
              />
            </Grid>

            {value.cmax_annualized && (
              <NumberInput
                label={t("Cmax annualisée (GWhPCS/an)")}
                required
                {...bind("cmax_annualized_value")}
              />
            )}
          </>
        )}
        <Button type="submit" iconId="ri-save-line" asideX loading={loading}>
          {t("Sauvegarder")}
        </Button>
      </EditableCard.Form>
    </EditableCard>
  )
}
