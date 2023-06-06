import { Alert } from "common/components/alert"
import { Button } from "common/components/button"
import { Dialog } from "common/components/dialog"
import { AlertCircle, Plus, Return } from "common/components/icons"
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

const ApplicationInfo = ({ file }: { file: DoubleCountingFileInfo }) => {

    return <section>
        <p>
            <Trans
                values={{
                    productionSite: file.production_site,
                }}
                defaults={`Pour le site de production <b>{{productionSite}}</b> par `}
            /><a href={`mailto:${file.producer_email}`}>{file.producer_email}</a>.
        </p>
        <p>
            <Trans
                values={{
                    fileName: file.file_name,
                }}
                defaults="Fichier excel téléchargé : <b>{{fileName}}</b>"
            />
        </p>
        <p>
            <Trans
                values={{
                    period: `${file.year} - ${file.year + 1}`,
                }}
                defaults="Période demandée : <b>{{period}}</b>"
            />


        </p>
    </section>
}
export default ApplicationInfo
