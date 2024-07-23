export const dcApplicationErrors = {
  errors: {
    sourcing: [
      {
        error: "UNKNOWN_FEEDSTOCK",
        line_number: 2,
        is_blocking: true,
        meta: {
          feedstock: "FUIMERAav",
        },
      },
    ],
    production: [
      {
        error: "UNKNOWN_BIOFUEL",
        line_number: 2,
        is_blocking: true,
        meta: {
          biofuel: "SFALKWJ",
        },
      },
      {
        error: "UNKNOWN_FEEDSTOCK",
        line_number: 3,
        is_blocking: true,
        meta: {
          feedstock: "Asdasasfw2323",
        },
      },
      {
        error: "MISSING_BIOFUEL",
        line_number: 4,
        is_blocking: true,
        meta: {},
      },
      {
        error: "NOT_DC_FEEDSTOCK",
        line_number: 5,
        is_blocking: true,
        meta: {
          feedstock: "BLE",
        },
      },
      {
        error: "MP_BC_INCOHERENT",
        line_number: 4,
        is_blocking: true,
        meta: {
          feedstock: "MARC_DE_RAISIN",
          biofuel: "B100",
        },
      },
      {
        error: "POME_GT_2000",
        line_number: null,
        is_blocking: true,
      },
    ],
    global: [
      {
        error: "PRODUCTION_MISMATCH_SOURCING",
        line_number: null,
        is_blocking: true,
        meta: {
          year: 2002,
          feedstock: "MARC_DE_RAISIN",
          sourcing: 8000,
          production: 10000,
        },
      },
    ],
  },
}
