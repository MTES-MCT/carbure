import { findFeedstocksClassification } from "common/api"
import {
  Autocomplete,
  AutocompleteProps,
} from "common/components/autocomplete2"
import { FeedstockClassification } from "common/types"
import { normalizeFeedstockClassification } from "common/utils/normalizers"
import { useTranslation } from "react-i18next"

type AutoCompleteFeedstocksProps =
  AutocompleteProps<FeedstockClassification> & {
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
        findFeedstocksClassification({
          query,
          is_biofuel_feedstock: isBiofuelFeedstock,
          is_methanogenic: isMethanogenic,
        })
      }
      normalize={normalizeFeedstockClassification}
      {...props}
    />
  )
}
