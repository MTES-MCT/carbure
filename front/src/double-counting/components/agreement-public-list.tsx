import { NoResult } from "common/components/no-result2"
import { Main } from "common/components/scaffold"
import { Table } from "common/components/table2"
import { useQuery } from "common/hooks/async"
import useTitle from "common/hooks/title"
import { formatDateYear } from "common/utils/formatters"
import { Trans, useTranslation } from "react-i18next"
import * as api from "../../double-counting/api"
import { usePrivateNavigation } from "common/layouts/navigation"
import { Title } from "common/components/title"

const AgreementPublicList = () => {
  const { t } = useTranslation()
  useTitle(t("Listes des unités de production de biocarburants reconnues"))
  usePrivateNavigation(
    t("Listes des unités de production de biocarburants reconnues")
  )
  const agreementsResponse = useQuery(
    api.getDoubleCountingAgreementsPublicList,
    {
      key: "dc-agreements-public-list",
      params: [],
    }
  )
  const agreements = agreementsResponse.result?.data

  return (
    <Main>
      <section>
        <Title is="h1" as="h4">
          <Trans>
            Listes des unités de production de biocarburants reconnues au titre
            du décret n°2019-570 du 7 juin 2019 portant sur la taxe incitative
            relative à l'incorporation des biocarburants
          </Trans>
        </Title>
      </section>
      <section>
        {agreements && (
          <Table
            loading={agreementsResponse.loading}
            columns={[
              {
                header: t("Unité de production"),
                small: true,
                cell: (a) => a.production_site.name || "-",
              },
              {
                header: t("Adresse"),
                small: true,
                cell: (a) => a.production_site.address,
              },
              {
                header: t("Pays"),
                small: true,
                cell: (a) => a.production_site.country || "-",
              },
              {
                header: t("N° d'agrément"),
                small: true,
                cell: (a) => a.certificate_id,
              },
              {
                header: t("Validité"),
                small: true,
                cell: (a) =>
                  `${formatDateYear(a.valid_from)}-${formatDateYear(a.valid_until)}`,
              },
              {
                header: t("Biocarburants reconnus"),
                cell: (a) => a.biofuel_list,
              },
            ]}
            rows={agreements}
          />
        )}
        {!agreements && <NoResult loading={agreementsResponse.loading} />}
      </section>
    </Main>
  )
}

export default AgreementPublicList
