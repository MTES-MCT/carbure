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
import { Form, useForm } from "common/components/form2"
import { DeepPartial } from "common/types"
import {
  getRediiThresholdLabel,
  isContractRedii,
  isTariffReference2011Or2020,
  isTariffReference2021Or2023,
} from "../../contract.utils"
import { getYesNoOptions } from "common/utils/normalizers"
import { Button } from "common/components/button2"
import {
  BiomethaneContract,
  BiomethaneContractPatchRequest,
} from "biomethane/pages/contract/types"
import { Notice } from "common/components/notice"
import { findBuyerBiomethaneEntities } from "biomethane/pages/contract/api"
import useEntity from "common/hooks/entity"
import { useState } from "react"
import { usePortal } from "common/components/portal"
import { RedIIDialog } from "./red-ii-dialog"

type ContractInfosForm = DeepPartial<BiomethaneContractPatchRequest>

export const ContractInfos = ({
  contract,
}: {
  contract?: BiomethaneContract
}) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const portal = usePortal()
  const [isEditing, setIsEditing] = useState(false)
  const { bind, value } = useForm<ContractInfosForm>(contract ?? {})
  const tariffReferenceOptions = useTariffReferenceOptions()
  const installationCategoryOptions = useInstallationCategoryOptions()
  const { execute: updateContract, loading } = useMutateContractInfos(contract)

  const onSubmit = () => {
    const update = (is_red_ii: boolean) => {
      updateContract({ ...value, is_red_ii }).then(() => {
        setIsEditing(false)
      })
    }

    // Allow the biomethane producer to set/unset the RED II status if the cmax or pap_contracted
    // is lower than the threshold
    if (entity.is_red_ii && !isContractRedii(value)) {
      portal((close) => (
        <RedIIDialog
          onClose={close}
          onConfirm={update}
          tariffReference={value.tariff_reference}
        />
      ))
    } else {
      updateContract(value).then(() => {
        setIsEditing(false)
      })
    }
  }

  return (
    <EditableCard
      title={t("Caractéristiques du contrat d’achat à tarif réglementé")}
      isEditing={isEditing}
      onEdit={setIsEditing}
    >
      <Form onSubmit={onSubmit}>
        {isContractRedii(value) && (
          <Notice variant="info" icon="fr-icon-info-line">
            {isTariffReference2011Or2020(value.tariff_reference)
              ? t(
                  "Votre Capacité maximale de production contractualisée est strictement supérieure à {{value}}, votre production de biométhane est donc soumise aux exigences RED.",
                  {
                    value: getRediiThresholdLabel(value.tariff_reference),
                  }
                )
              : t(
                  "Votre production annuelle prévisionnelle est strictement supérieure à {{value}}, votre production de biométhane est donc soumise aux exigences RED.",
                  {
                    value: getRediiThresholdLabel(value.tariff_reference),
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
          <Button type="submit" iconId="ri-save-line" asideX loading={loading}>
            {t("Sauvegarder")}
          </Button>
        )}
      </Form>
    </EditableCard>
  )
}
