import { EntityTypeEnum as BaseEntityTypeEnum } from "./api-schema"

declare module "./api-schema" {
  // Entity type exported by the generated schema has bad keys.
  // The only way to overrides without changing schema is to extends the current EntityTypeEnum and renaming keys
  export enum EntityTypeEnum {
    Producer = BaseEntityTypeEnum["Producteur"],
    Operator = BaseEntityTypeEnum["Op_rateur"],
    Airline = BaseEntityTypeEnum["Compagnie_a_rienne"],
    ExternalAdmin = BaseEntityTypeEnum["Administration_Externe"],
    CPO = BaseEntityTypeEnum["Charge_Point_Operator"],
    PowerOrHeatProducer = BaseEntityTypeEnum["Power_or_Heat_Producer"],
  }
}
