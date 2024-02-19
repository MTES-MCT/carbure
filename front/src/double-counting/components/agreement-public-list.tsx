import useEntity from "carbure/hooks/entity"
import NoResult from "common/components/no-result"
import { Main } from "common/components/scaffold"
import Table, { Cell, Column, Order } from "common/components/table"
import { useQuery } from "common/hooks/async"
import useTitle from "common/hooks/title"
import { compact } from "common/utils/collection"
import { formatDateYear } from "common/utils/formatters"
import { useState } from "react"
import { Trans, useTranslation } from "react-i18next"
import * as api from "../../double-counting/api"
import { DoubleCountingAgreementPublic } from "../types"


const AgreementPublicList = () => {
  const { t } = useTranslation()

  const entity = useEntity()
  const [order, setOrder] = useState<Order | undefined>(undefined)

  useTitle(t("Listes des unités de production de biocarburants reconnues"))

  const agreementsResponse = useQuery(api.getDoubleCountingAgreementsPublicList, {
    key: "dc-agreements-public-list",
    params: [],
  })


  const agreements = agreementsResponse.result?.data.data


  const columns: Column<DoubleCountingAgreementPublic>[] = compact([
    {
      header: t("Unité de production"),
      cell: (a) => <Cell text={a.production_site.name || "-"} />,
    },
    {
      header: t("Adresse"),
      cell: (a) => <Cell text={a.production_site.address} />
    },
    {
      header: t("Pays"),
      cell: (a) => <Cell text={a.production_site.country || "-"} />,
    },
    {
      header: t("N° d'agrément"),
      cell: (a) => <Cell text={a.certificate_id} />
    },
    {
      header: t("Validité"),
      cell: (a) => <Cell text={`${formatDateYear(a.valid_from)}-${formatDateYear(a.valid_until)}`} />,
    },
    {
      header: t("Biocarburants reconnus"),
      cell: (a) => <Cell text={a.biofuel_list} />,
    }
  ])

  return (
    <Main>
      <section>
        <h1>
          <Trans>Listes des unités de production de biocarburants reconnues au titre du décret n°2019-570 du 7 juin 2019 portant sur la taxe incitative relative à l'incorporation des biocarburants</Trans>
        </h1>
      </section>
      <section>



        {agreements && <Table
          loading={agreementsResponse.loading}
          columns={columns}
          rows={agreements}
          order={order}
          onOrder={setOrder}
        />
        }
        {!agreements &&
          <NoResult
            loading={agreementsResponse.loading}

          />
        }


      </section>

    </Main>
  )
}

export default AgreementPublicList


