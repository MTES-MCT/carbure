import { findFeedstocks } from "common/api"
import {
  Autocomplete,
  AutocompleteProps,
} from "common/components/autocomplete2"
import { useFeedstockParams } from "common/hooks/api/use-feedstocks"
import { FeedStockClassification } from "common/types"
import { useTranslation } from "react-i18next"

type AutoCompleteFeedstocksProps = AutocompleteProps<FeedStockClassification>

export const AutoCompleteFeedstocks = (props: AutoCompleteFeedstocksProps) => {
  const { t } = useTranslation()
  const feedstockParams = useFeedstockParams()

  return (
    <Autocomplete
      placeholder={t("Rechercher une matière première...")}
      getOptions={(query) =>
        findFeedstocks({
          query,
          ...feedstockParams,
        })
      }
      normalize={(feedstock) => {
        return {
          value: feedstock,
          label: feedstock.name,
        }
      }}
      {...props}
    />
  )
}
