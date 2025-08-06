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
import { DeepPartial } from "common/types"
import {
  isContractRedii,
  isTariffReference2011Or2020,
  isTariffReference2021Or2023,
} from "./contract-infos.utils"
import { getYesNoOptions } from "common/utils/normalizers"
import { Button } from "common/components/button2"
import { BiomethaneEntityConfigContract } from "biomethane/types"
import { Notice } from "common/components/notice"
import { REDII_CMAX_THRESHOLD, REDII_PAP_THRESHOLD } from "biomethane/config"

type ContractInfosForm = DeepPartial<
  apiTypes["BiomethaneEntityConfigContractAddRequest"]
>

export const ContractInfos = ({
  contract,
}: {
  contract?: BiomethaneEntityConfigContract
}) => {
  const { t } = useTranslation()
  const { bind, value } = useForm<ContractInfosForm>(contract ?? {})
  const tariffReferenceOptions = useTariffReferenceOptions()
  const installationCategoryOptions = useInstallationCategoryOptions()
  const { execute: updateContract, loading } = useMutateContractInfos(
    contract !== undefined
  )

  // const resetFields = (tariffReference?: TariffReference) => {
  //   if (isTariffReference2011Or2020(tariffReference)) {
  //     setValue({
  //       ...value,
  //       tariff_reference: tariffReference,
  //       pap_contracted: null,
  //     })
  //   }

  //   if (isTariffReference2021Or2023(tariffReference)) {
  //     setValue({
  //       ...value,
  //       tariff_reference: tariffReference,
  //       cmax: null,
  //       cmax_annualized: null,
  //       cmax_annualized_value: null,
  //     })
  //   }
  // }

  return (
    <EditableCard
      title={t("Caractéristiques du contrat d’achat à tarif réglementé")}
    >
      {({ isEditing }) => (
        <EditableCard.Form onSubmit={() => updateContract(value!)}>
          {isContractRedii(value) && (
            <Notice variant="info" icon="fr-icon-info-line">
              {t(
                "Votre Capacité maximale de production contractualisée est strictement supérieure à {{value}}, votre production de biométhane est donc soumise aux exigences RED.",
                {
                  value: isTariffReference2011Or2020(value?.tariff_reference)
                    ? `${REDII_CMAX_THRESHOLD} Nm³/h`
                    : `${REDII_PAP_THRESHOLD} GWhPCS/an`,
                }
              )}
            </Notice>
          )}
          <Grid cols={2} gap="lg">
            <SelectDsfr
              label={t("Référence de l'arrêté tarifaire")}
              options={tariffReferenceOptions}
              required
              {...bind("tariff_reference")}
              readOnly={!isEditing}
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
              readOnly={!isEditing}
            />
          </Grid>
          <SelectDsfr
            label={t("Catégorie d'installation")}
            options={installationCategoryOptions}
            required
            {...bind("installation_category")}
            readOnly={!isEditing}
          />

          {isTariffReference2011Or2020(value.tariff_reference) && (
            <>
              <Grid cols={2} gap="lg">
                <NumberInput
                  label={t("Cmax (Nm³/h)")}
                  {...bind("cmax")}
                  required
                  readOnly={!isEditing}
                />
                <RadioGroup
                  label={t("Annualisation du contrôle de la Cmax")}
                  options={getYesNoOptions()}
                  orientation="horizontal"
                  required
                  {...bind("cmax_annualized")}
                  value={value.cmax_annualized ?? false}
                  readOnly={!isEditing}
                />
              </Grid>

              {value.cmax_annualized && (
                <NumberInput
                  label={t("Cmax annualisée (GWhPCS/an)")}
                  required
                  {...bind("cmax_annualized_value")}
                  readOnly={!isEditing}
                />
              )}
            </>
          )}

          {isTariffReference2021Or2023(value.tariff_reference) && (
            <NumberInput
              label={t("PAP contractualisée (GWhPCS/an)")}
              {...bind("pap_contracted")}
              required
              readOnly={!isEditing}
            />
          )}
          {isEditing && (
            <Button
              type="submit"
              iconId="ri-save-line"
              asideX
              loading={loading}
            >
              {t("Sauvegarder")}
            </Button>
          )}
        </EditableCard.Form>
      )}
    </EditableCard>
  )
}
