export const checkDoubleCountingFilesResponse = {
  files: [
    {
      file_name:
        "20221025 bp Castellon Dossier de demande de reconnaissance au double comptage.xlsx",
      errors: {
        sourcing: [],
        production: [
          {
            error: "MP_BC_INCOHERENT",
            line_number: 19,
            is_blocking: true,
            meta: {
              feedstock: "HUILE_ALIMENTAIRE_USAGEE",
              biofuel: "HVOG",
              infos: [
                "Des huiles alimentaires usagées ne peuvent donner que des EMHU ou HOG/HOE/HOC",
                "Un HVO doit provenir d'huiles végétales uniquement. Pour les autres huiles hydrotraitées, voir la nomenclature HOE/HOG/HOC",
              ],
            },
          },
          {
            error: "MP_BC_INCOHERENT",
            line_number: 20,
            is_blocking: true,
            meta: {
              feedstock: "HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2",
              biofuel: "HVOG",
              infos: [
                "Des huiles ou graisses animales ne peuvent donner que des EMHA ou HOG/HOE/HOC",
                "Un HVO doit provenir d'huiles végétales uniquement. Pour les autres huiles hydrotraitées, voir la nomenclature HOE/HOG/HOC",
              ],
            },
          },
          {
            error: "MP_BC_INCOHERENT",
            line_number: 21,
            is_blocking: true,
            meta: {
              feedstock: "HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2",
              biofuel: "HVOG",
              infos: [
                "Des huiles ou graisses animales ne peuvent donner que des EMHA ou HOG/HOE/HOC",
                "Un HVO doit provenir d'huiles végétales uniquement. Pour les autres huiles hydrotraitées, voir la nomenclature HOE/HOG/HOC",
              ],
            },
          },
          {
            error: "MP_BC_INCOHERENT",
            line_number: 22,
            is_blocking: true,
            meta: {
              feedstock: "EFFLUENTS_HUILERIES_PALME_RAFLE",
              biofuel: "HVOG",
              infos: [
                "Un HVO doit provenir d'huiles végétales uniquement. Pour les autres huiles hydrotraitées, voir la nomenclature HOE/HOG/HOC",
              ],
            },
          },
          {
            error: "MP_BC_INCOHERENT",
            line_number: 26,
            is_blocking: true,
            meta: {
              feedstock: "HUILE_ALIMENTAIRE_USAGEE",
              biofuel: "HVOG",
              infos: [
                "Des huiles alimentaires usagées ne peuvent donner que des EMHU ou HOG/HOE/HOC",
                "Un HVO doit provenir d'huiles végétales uniquement. Pour les autres huiles hydrotraitées, voir la nomenclature HOE/HOG/HOC",
              ],
            },
          },
          {
            error: "MP_BC_INCOHERENT",
            line_number: 27,
            is_blocking: true,
            meta: {
              feedstock: "HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2",
              biofuel: "HVOG",
              infos: [
                "Des huiles ou graisses animales ne peuvent donner que des EMHA ou HOG/HOE/HOC",
                "Un HVO doit provenir d'huiles végétales uniquement. Pour les autres huiles hydrotraitées, voir la nomenclature HOE/HOG/HOC",
              ],
            },
          },
          {
            error: "MP_BC_INCOHERENT",
            line_number: 28,
            is_blocking: true,
            meta: {
              feedstock: "HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2",
              biofuel: "HVOG",
              infos: [
                "Des huiles ou graisses animales ne peuvent donner que des EMHA ou HOG/HOE/HOC",
                "Un HVO doit provenir d'huiles végétales uniquement. Pour les autres huiles hydrotraitées, voir la nomenclature HOE/HOG/HOC",
              ],
            },
          },
          {
            error: "MP_BC_INCOHERENT",
            line_number: 29,
            is_blocking: true,
            meta: {
              feedstock: "EFFLUENTS_HUILERIES_PALME_RAFLE",
              biofuel: "HVOG",
              infos: [
                "Un HVO doit provenir d'huiles végétales uniquement. Pour les autres huiles hydrotraitées, voir la nomenclature HOE/HOG/HOC",
              ],
            },
          },
        ],
        global: [],
      },
      error_count: 8,
      period: "NOT_YET_IMPLEMENTED",
      production_site: "NOT_YET_IMPLEMENTED",
    },
  ],
  checked_at: "2022-11-30T13:19:13.547625",
}
