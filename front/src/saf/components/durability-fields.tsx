import { Divider } from "common/components/divider"
import { TextInput } from "common/components/inputs2"
import { Col, Row } from "common/components/scaffold"
import {
  formatGHG,
  formatNumber,
  formatPercentage,
} from "common/utils/formatters"
import { useGhgEmissionTitles } from "traceability/hooks/use-ghg-emission-titles"
import { useTranslation } from "react-i18next"
import { Dialog } from "common/components/dialog2"
import { SafDurability } from "saf/types"

const formatNumberToText = (value: number | undefined) =>
  value ? formatNumber(value) : ""
const DurabilityFields = ({ durability }: { durability: SafDurability }) => {
  const { t } = useTranslation()
  const emissionTitles = useGhgEmissionTitles()

  return (
    <Dialog.Section label={t("Émissions/Réductions")}>
      <Row style={{ gap: "16px" }}>
        <Col grow gap="md">
          <TextInput
            hasTooltip
            label="EEC"
            title={emissionTitles.eec}
            value={durability.eec ? formatNumberToText(durability.eec) : "-"}
            readOnly
          />
          <TextInput
            hasTooltip
            label="EL"
            title={emissionTitles.el}
            value={durability.el ? formatNumberToText(durability.el) : "-"}
            readOnly
          />
          <TextInput
            required
            hasTooltip
            label="EP"
            title={emissionTitles.ep}
            value={durability.ep ? formatNumberToText(durability.ep) : "-"}
            readOnly
          />
          <TextInput
            required
            hasTooltip
            label="ETD"
            title={emissionTitles.etd}
            value={durability.etd ? formatNumberToText(durability.etd) : "-"}
            readOnly
          />
        </Col>
        <Col grow gap="md">
          <TextInput
            label="ESCA"
            hasTooltip
            title={emissionTitles.esca}
            value={durability.esca ? formatNumberToText(durability.esca) : "-"}
            readOnly
          />
          <TextInput
            label="ECCS"
            hasTooltip
            title={emissionTitles.eccs}
            value={durability.eccs ? formatNumberToText(durability.eccs) : "-"}
            readOnly
          />
          <TextInput
            label="ECCR"
            hasTooltip
            title={emissionTitles.eccr}
            value={durability.eccr ? formatNumberToText(durability.eccr) : "-"}
            readOnly
          />
          <TextInput
            label="EEE"
            hasTooltip
            title={emissionTitles.eee}
            value={durability.eee ? formatNumberToText(durability.eee) : "-"}
            readOnly
          />
        </Col>
      </Row>
      <Divider />
      <TextInput
        readOnly
        label="Total"
        value={durability.ghg_total ? formatGHG(durability.ghg_total) : "-"}
      />

      <TextInput
        readOnly
        label={t("Réduction")}
        value={
          durability.ghg_reduction
            ? formatPercentage(durability.ghg_reduction)
            : "-"
        }
      />
    </Dialog.Section>
  )
}

export default DurabilityFields
