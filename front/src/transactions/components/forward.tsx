import React from "react"
import { LotForwarder } from "transactions/hooks/actions/use-forward-lots";
import { PromptFormProps } from "common/components/dialog";
import { Entity } from "common/types";

import styles from "./forward.module.css"
import { Box } from "common/components";
import { EntityDeliverySite } from "settings/hooks/use-delivery-sites";

export const OperatorForwardPromptFactory = (forwarder: LotForwarder, outsourceddepots: EntityDeliverySite[] | undefined) => ({
    onConfirm,
    onCancel,
  }: PromptFormProps<Entity>) => (
      <Box className={styles.importExplanation}>
          Voici vers quels opérateurs les lots seront transférés:
          <p>{outsourceddepots}</p>
          {outsourceddepots?.forEach((d) => (
            <span>{d.depot?.name} : {d.blender_entity_id?.name}</span>
          ))}
      </Box>
  )
