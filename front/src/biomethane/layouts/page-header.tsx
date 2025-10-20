import Badge from "@codegouvfr/react-dsfr/Badge"
import { Button } from "common/components/button2"
import { Notice } from "common/components/notice"
import { Content, Main, Row } from "common/components/scaffold"
import { Select } from "common/components/selects2"
import { Title } from "common/components/title"
import { useTranslation } from "react-i18next"
import { declarationInterval } from "biomethane/utils"
import { usePortal } from "common/components/portal"
import { Confirm } from "common/components/dialog2"
import useYears from "common/hooks/years-2"
import { getAnnualDeclarationYears } from "biomethane/api"
import { useNotify } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import { Outlet } from "react-router-dom"
import { AnnualDeclarationProvider } from "biomethane/providers/annual-declaration.provider"

export interface BiomethanePageHeaderProps {
  status?: "PENDING" | "VALIDATED"
}

// Digestate and Energy pages share the same page header and the same declaration validation logic
export const BiomethanePageHeader = ({ status }: BiomethanePageHeaderProps) => {
  const { t } = useTranslation()
  const portal = usePortal()
  const notify = useNotify()
  const years = useYears("biomethane", getAnnualDeclarationYears)

  const validateAnnualDeclarationMutation = useMutation(() => {}, {
    invalidates: ["annual-declaration"],
    onSuccess: () => {
      notify(t("Les informations ont bien été validées."), {
        variant: "success",
      })
    },
  })
  const selectedYearIsInCurrentInterval =
    years.selected === declarationInterval.year
  const selectedYear = years.selected

  const openValidateDeclarationDialog = () => {
    portal((close) => (
      <Confirm
        onClose={close}
        confirm={t("Valider")}
        onConfirm={validateAnnualDeclarationMutation.execute}
        title={t("Valider mes informations annuelles")}
        description={
          <>
            {t("Voulez-vous valider vos informations annuelles ?")}
            <br />
            {selectedYear &&
              t(
                "Ces informations seront encore modifiables jusqu'au {{date}}",
                {
                  date: `31/03/${selectedYear + 1}`,
                }
              )}
          </>
        }
      />
    ))
  }
  return (
    <Main>
      <Row>
        <Select
          options={years.options}
          value={selectedYear}
          onChange={years.setYear}
        />
        <Button
          onClick={openValidateDeclarationDialog}
          iconId="ri-file-text-line"
          asideX
          disabled={
            !selectedYearIsInCurrentInterval ||
            status === "VALIDATED" ||
            !status
          }
        >
          {t("Valider mes informations annuelles")}
        </Button>
      </Row>
      <Row
        style={{
          justifyContent: "space-between",
          marginTop: "var(--spacing-2w)",
        }}
      >
        <Title
          is="h1"
          as="h5"
          style={{ color: "var(--artwork-major-blue-france" }}
        >
          {t("Récapitulatif de vos informations")}
        </Title>
        <Badge severity={status === "VALIDATED" ? "success" : "info"}>
          {status === "VALIDATED" ? t("Validé") : t("En cours")}
        </Badge>
      </Row>
      {selectedYearIsInCurrentInterval && (
        <Notice variant="info" icon="ri-time-line" isClosable>
          {t("A déclarer et mettre à jour une fois par an, avant le {{date}}", {
            date: `31/03/${selectedYear + 1}`,
          })}
        </Notice>
      )}
      <Content marginTop>
        <AnnualDeclarationProvider year={selectedYear}>
          <Outlet />
        </AnnualDeclarationProvider>
      </Content>
    </Main>
  )
}
