import { Cell, Column } from "common/components/table2"
import { useTranslation } from "react-i18next"
import { BiomethaneProviderDeclaration } from "../types"

export const useProviderDeclarationsColumns =
  (): Column<BiomethaneProviderDeclaration>[] => {
    const { t } = useTranslation()

    return [
      {
        header: t("Producteur"),
        cell: (row) => <Cell text={row.producer.name} />,
      },
      {
        header: t("Siret"),
        cell: (row) => <Cell text={row.producer.registration_id || "-"} />,
        style: { flex: "0 0 160px" },
      },
      {
        header: t("Code INSEE"),
        cell: (row) => <Cell text={row.production_unit?.insee_code || "-"} />,
        style: { flex: "0 0 160px" },
      },
      {
        header: t("Adresse"),
        cell: (row) => {
          const { address, postal_code, city } = row.production_unit ?? {}
          const text = [address, postal_code, city].filter(Boolean).join(" ")
          return <Cell text={text || "-"} />
        },
        style: { flex: "2 1 0%" },
      },
    ]
  }
