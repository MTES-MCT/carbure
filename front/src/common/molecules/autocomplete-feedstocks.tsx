import { findFeedstocks } from "common/api"
import {
  Autocomplete,
  AutocompleteProps,
} from "common/components/autocomplete2"
import { FeedStockClassification } from "common/types"
import { useTranslation } from "react-i18next"

type AutoCompleteFeedstocksProps =
  AutocompleteProps<FeedStockClassification> & {
    isBiofuelFeedstock?: boolean
    isMethanogenic?: boolean
  }

export const AutoCompleteFeedstocks = ({
  isBiofuelFeedstock,
  isMethanogenic,
  ...props
}: AutoCompleteFeedstocksProps) => {
  const { t } = useTranslation()
  return (
    <Autocomplete
      placeholder={t("Rechercher une matière première...")}
      getOptions={(query) =>
        findFeedstocks({
          query,
          is_biofuel_feedstock: isBiofuelFeedstock,
          is_methanogenic: isMethanogenic,
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
