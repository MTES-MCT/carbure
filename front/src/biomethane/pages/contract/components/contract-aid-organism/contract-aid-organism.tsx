import { EditableCard } from "common/molecules/editable-card"
import {
  BiomethaneContract,
  BiomethaneContractPatchRequest,
  ComplementaryAidOrganisms,
} from "biomethane/pages/contract/types"
import { useTranslation } from "react-i18next"
import { getYesNoOptions } from "common/utils/normalizers"
import { CheckboxGroup, RadioGroup, TextInput } from "common/components/inputs2"
import { useForm } from "common/components/form2"
import { useContractAidOrganismOptions } from "./contract-aid-organism.hooks"
import { Button } from "common/components/button2"
import { useMutateContractInfos } from "../contract-infos/contract-infos.hooks"
import { useSelectedEntity } from "common/providers/selected-entity-provider"

type ContractAidOrganismForm = Pick<
  BiomethaneContractPatchRequest,
  | "has_complementary_investment_aid"
  | "complementary_aid_organisms"
  | "complementary_aid_other_organism_name"
>

const extractValues = (contract?: BiomethaneContract) => {
  return {
    has_complementary_investment_aid:
      contract?.has_complementary_investment_aid,
    complementary_aid_organisms: contract?.complementary_aid_organisms ?? [],
    complementary_aid_other_organism_name:
      contract?.complementary_aid_other_organism_name ?? "",
  }
}

export const ContractAidOrganism = ({
  contract,
}: {
  contract?: BiomethaneContract
}) => {
  const { t } = useTranslation()
  const { hasSelectedEntity } = useSelectedEntity()

  const { bind, value } = useForm<ContractAidOrganismForm>(
    extractValues(contract)
  )
  const { execute: updateContractAidOrganism, loading } =
    useMutateContractInfos(contract)

  const complementaryAidOrganismOptions = useContractAidOrganismOptions()

  return (
    <EditableCard
      title={t("Aide complémentaire à l'investissement")}
      readOnly={hasSelectedEntity}
    >
      {({ isEditing }) => (
        <EditableCard.Form onSubmit={() => updateContractAidOrganism(value)}>
          <RadioGroup
            readOnly={!isEditing}
            label={t(
              "Est-ce que votre installation a bénéficié d'une ou plusieurs aide(s) complémentaire(s) à l'investissement?"
            )}
            options={getYesNoOptions()}
            {...bind("has_complementary_investment_aid")}
            orientation="horizontal"
            required
          />
          {value.has_complementary_investment_aid && (
            <>
              <CheckboxGroup
                readOnly={!isEditing}
                label={t("Organisme qui a attribué l'aide complémentaire")}
                options={complementaryAidOrganismOptions}
                {...bind("complementary_aid_organisms")}
                required
              />
              {value.complementary_aid_organisms?.includes(
                ComplementaryAidOrganisms.OTHER
              ) && (
                <TextInput
                  readOnly={!isEditing}
                  label={t(
                    "Précisez le nom du ou des organismes publics ayant octroyé l'aide"
                  )}
                  {...bind("complementary_aid_other_organism_name")}
                />
              )}
            </>
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
