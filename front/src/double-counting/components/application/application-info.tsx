import { Alert } from "common/components/alert"
import { Button } from "common/components/button"
import { Dialog } from "common/components/dialog"
import { AlertCircle, InfoCircle, Plus, Return } from "common/components/icons"
import Tabs from "common/components/tabs"
import Tag from "common/components/tag"
import { useState } from "react"
import { Trans, useTranslation } from "react-i18next"
import { getErrorText } from "settings/utils/double-counting"
import { DoubleCountingFileInfo, DoubleCountingSourcing, DoubleCountingSourcingAggregation, DoubleCountingUploadError } from "../../types"
import { ProductionTable, SourcingAggregationTable, SourcingTable } from "../dc-tables"
import Collapse from "common/components/collapse"
import Checkbox from "common/components/checkbox"
import { t } from "i18next"
import Tooltip from "common/components/tooltip"

const ApplicationInfo = ({ fileData }: { fileData: DoubleCountingFileInfo }) => {

    return <section>
        <p>
            <Trans
                values={{
                    productionSite: fileData.production_site,
                }}
                defaults={`Pour le site de production <b>{{productionSite}}</b> par `}
            /><a href={`mailto:${fileData.producer_email}`}>{fileData.producer_email}</a>.
        </p>
        <p>
            <Trans
                values={{
                    fileName: fileData.file_name,
                }}
                defaults="Fichier excel téléchargé : <b>{{fileName}}</b>"
            />
        </p>
        <p>
            <Tooltip title={t(`L'année détectée est renseignée en bas de l'onglet "Reconnaissance double comptage" du fichier excel.`)}>
                <Trans
                    values={{
                        period: `${fileData.year} - ${fileData.year + 1}`,
                    }}
                    defaults="Période demandée : <b>{{period}}</b>"
                />
                <InfoCircle
                    color="#a4a4a4"
                    size={15}
                    style={{
                        margin: "7px 0px 0 2px",
                        position: "absolute",
                    }}
                />
            </Tooltip>


        </p>
    </section>
}
export default ApplicationInfo
