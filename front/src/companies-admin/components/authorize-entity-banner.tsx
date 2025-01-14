import Alert from "common/components/alert"
import Button from "common/components/button"
import { AlertCircle, Check } from "common/components/icons"
import { usePortal } from "common/components/portal"
import { Col } from "common/components/scaffold"
import { useMutation } from "common/hooks/async"
import { useTranslation } from "react-i18next"
import * as api from "../api"
import { Confirm } from "common/components/dialog"
import type { Entity } from "carbure/types"
import useEntity from "carbure/hooks/entity"
import { Title } from "common/components/title"

type AuthorizeEntityBannerProps = {
  company: Entity
}

export function AuthorizeEntityBanner({ company }: AuthorizeEntityBannerProps) {
  const { t } = useTranslation()
  const portal = usePortal()
  const entity = useEntity()

  const enableCompany = useMutation(api.enableCompany, {
    invalidates: ["entity-details", "user-right-requests"],
  })

  return (
    <Alert variant="warning" icon={AlertCircle} label={t("Attention")}>
      <Col style={{ gap: "var(--spacing-m)", padding: "var(--spacing-m) 0" }}>
        <Title is="h1" as="h5">
          {t("Cette société n'est pas encore autorisée")}
        </Title>
        <p>
          {t(
            "Si les informations ci-dessous vous semblent correctes, vous pouvez autoriser cette société en cliquant sur le bouton suivant :"
          )}
        </p>
        <Button
          variant="success"
          icon={<Check color="var(--green-dark)" />}
          loading={enableCompany.loading}
          action={() =>
            portal((close) => (
              <Confirm
                icon={Check}
                variant="success"
                title={t("Autoriser la société")}
                description={t(
                  `Voulez vous autoriser la société {{entity}} à accéder à CarbuRe ?`,
                  { entity: company?.name ?? "N/A" }
                )}
                confirm={t("Autoriser")}
                onClose={close}
                onConfirm={() => enableCompany.execute(entity.id, company.id)}
              />
            ))
          }
          style={{
            alignSelf: "flex-start",
            marginTop: "var(--spacing-s)",
          }}
        >
          {t("Autoriser la société")}
        </Button>
      </Col>
    </Alert>
  )
}
