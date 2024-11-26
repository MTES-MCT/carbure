export interface paths {
  "/api/apikey/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["apikey_list"]
    put?: never
    post: operations["apikey_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/apikey/{id}/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["apikey_retrieve"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/apikey/{id}/revoke/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["apikey_revoke_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/entities/{id}/enable/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["entities_enable_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/saf/clients/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["saf_clients_list"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/saf/clients/{id}/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["saf_clients_retrieve"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/saf/snapshot/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["saf_snapshot_retrieve"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/saf/ticket-sources/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["saf_ticket_sources_list"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/saf/ticket-sources/{id}/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["saf_ticket_sources_retrieve"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/saf/ticket-sources/{id}/assign/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["saf_ticket_sources_assign_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/saf/ticket-sources/export/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["saf_ticket_sources_export_retrieve"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/saf/ticket-sources/filters/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["saf_ticket_sources_filters_retrieve"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/saf/ticket-sources/group-assign/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["saf_ticket_sources_group_assign_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/saf/tickets/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["saf_tickets_list"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/saf/tickets/{id}/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["saf_tickets_retrieve"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/saf/tickets/{id}/accept/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["saf_tickets_accept_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/saf/tickets/{id}/cancel/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["saf_tickets_cancel_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/saf/tickets/{id}/credit-source/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["saf_tickets_credit_source_retrieve"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/saf/tickets/{id}/reject/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["saf_tickets_reject_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/saf/tickets/export/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["saf_tickets_export_retrieve"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/saf/tickets/filters/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["saf_tickets_filters_retrieve"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/saf/years/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["saf_years_retrieve"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/lots/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["transactions_lots_list"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/lots/{id}/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["transactions_lots_retrieve"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/lots/{id}/duplicate/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["transactions_lots_duplicate_retrieve"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/lots/{id}/toggle-warning/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["transactions_lots_toggle_warning_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/lots/{id}/update-lot/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["transactions_lots_update_lot_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/lots/accept-blending/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["transactions_lots_accept_blending_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/lots/accept-consumption/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["transactions_lots_accept_consumption_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/lots/accept-direct-delivery/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["transactions_lots_accept_direct_delivery_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/lots/accept-export/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["transactions_lots_accept_export_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/lots/accept-in-stock/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["transactions_lots_accept_in_stock_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/lots/accept-processing/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["transactions_lots_accept_processing_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/lots/accept-rfc/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["transactions_lots_accept_rfc_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/lots/accept-trading/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["transactions_lots_accept_trading_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/lots/add/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["transactions_lots_add_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/lots/add-comment/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["transactions_lots_add_comment_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/lots/add-excel/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["transactions_lots_add_excel_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/lots/admin-declarations/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["transactions_lots_admin_declarations_retrieve"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/lots/approuve-fix/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["transactions_lots_approuve_fix_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/lots/bulk-create/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["transactions_lots_bulk_create_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/lots/cancel-accept/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["transactions_lots_cancel_accept_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/lots/declarations/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["transactions_lots_declarations_retrieve"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/lots/declarations-invalidate/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["transactions_lots_declarations_invalidate_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/lots/declarations-validate/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["transactions_lots_declarations_validate_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/lots/delete/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["transactions_lots_delete_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/lots/delete-many/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["transactions_lots_delete_many_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/lots/export/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["transactions_lots_export_retrieve"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/lots/filters/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["transactions_lots_filters_retrieve"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/lots/map/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["transactions_lots_map_retrieve"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/lots/mark-conform/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["transactions_lots_mark_conform_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/lots/mark-non-conform/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["transactions_lots_mark_non_conform_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/lots/reject/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["transactions_lots_reject_retrieve"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/lots/request-fix/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["transactions_lots_request_fix_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/lots/send/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["transactions_lots_send_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/lots/submit-fix/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["transactions_lots_submit_fix_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/lots/summary/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["transactions_lots_summary_retrieve"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/lots/template/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["transactions_lots_template_retrieve"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/lots/toggle-pin/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["transactions_lots_toggle_pin_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/lots/update-many/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["transactions_lots_update_many_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/snapshot": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["transactions_snapshot_retrieve"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/stocks/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["transactions_stocks_list"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/stocks/{id}/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["transactions_stocks_retrieve"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/stocks/cancel-transformation/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["transactions_stocks_cancel_transformation_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/stocks/filters/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["transactions_stocks_filters_retrieve"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/stocks/flush/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["transactions_stocks_flush_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/stocks/split/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["transactions_stocks_split_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/stocks/summary/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["transactions_stocks_summary_retrieve"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/stocks/template/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["transactions_stocks_template_retrieve"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/stocks/transform/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["transactions_stocks_transform_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/transactions/years": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["transactions_years_retrieve"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
}
export type webhooks = Record<string, never>
export interface components {
  schemas: {
    APIKey: {
      name?: string | null
    }
    APIKeyList: {
      readonly id: number
      name?: string | null
      key: string
      /** Format: date-time */
      readonly created_at: string
      revoked?: boolean
      /** Format: date-time */
      last_used?: string | null
      /** Format: int64 */
      usage_count?: number
    }
    AcceptBlending: {
      selection: number[]
    }
    AcceptConsumption: {
      selection: number[]
    }
    AcceptDirectDelivery: {
      selection: number[]
    }
    AcceptExport: {
      selection: number[]
    }
    AcceptProcessing: {
      selection: number[]
      processing_entity_id: number
    }
    AcceptRFC: {
      selection: number[]
    }
    AcceptStock: {
      selection: number[]
    }
    AcceptTrading: {
      selection: number[]
      client_entity_id?: string
      unknown_client?: string
      certificate?: string
    }
    AddComment: {
      comment: string
      /** @default false */
      is_visible_by_admin: boolean
      /** @default false */
      is_visible_by_auditor: boolean
      selection: number[]
    }
    AddExcel: {
      /** Format: uri */
      file: string
    }
    AdminSnapshotReponse: {
      alerts: number
      lots: number
      stocks: number
    }
    ApproveFix: {
      lot_ids: number[]
    }
    Biofuel: {
      name: string
      name_en: string
      code: string
    }
    BulkCreateResponse: {
      lots: number
      valid: number
      invalid: number
      errors: components["schemas"]["EmbeddedGenericError"][]
    }
    CancelAccept: {
      lot_ids: number[]
    }
    CarbureLotComment: {
      readonly entity: components["schemas"]["Entity"]
      user?: number | null
      comment_type?: components["schemas"]["CommentTypeEnum"]
      /** Format: date-time */
      readonly comment_dt: string
      comment: string
    }
    CarbureLotEvent: {
      readonly user: string
      event_type: components["schemas"]["EventTypeEnum"]
      /** Format: date-time */
      readonly event_dt: string
      metadata?: unknown
    }
    CarbureLotPublic: {
      readonly id: number
      year: number
      period: number
      carbure_id?: string
      readonly carbure_producer: components["schemas"]["EntitySummary"]
      unknown_producer?: string | null
      readonly carbure_production_site: components["schemas"]["ProductionSite"]
      unknown_production_site?: string | null
      readonly production_country: components["schemas"]["Country"]
      /** Format: date */
      production_site_commissioning_date?: string | null
      production_site_certificate?: string | null
      production_site_double_counting_certificate?: string | null
      readonly carbure_supplier: components["schemas"]["EntitySummary"]
      unknown_supplier?: string | null
      supplier_certificate?: string | null
      supplier_certificate_type?: string | null
      transport_document_type?: components["schemas"]["TransportDocumentTypeEnum"]
      transport_document_reference?: string | null
      readonly carbure_client: components["schemas"]["EntitySummary"]
      unknown_client?: string | null
      /** Format: date */
      dispatch_date?: string | null
      readonly carbure_dispatch_site: components["schemas"]["Depot"]
      unknown_dispatch_site?: string | null
      readonly dispatch_site_country: components["schemas"]["Country"]
      /** Format: date */
      delivery_date?: string | null
      readonly carbure_delivery_site: components["schemas"]["Depot"]
      unknown_delivery_site?: string | null
      readonly delivery_site_country: components["schemas"]["Country"]
      delivery_type?: components["schemas"]["DeliveryTypeEnum"]
      lot_status?: components["schemas"]["LotStatusEnum"]
      correction_status?: components["schemas"]["CorrectionStatusEnum"]
      /** Format: double */
      volume?: number
      /** Format: double */
      weight?: number
      /** Format: double */
      lhv_amount?: number
      readonly feedstock: components["schemas"]["FeedStock"]
      readonly biofuel: components["schemas"]["Biofuel"]
      readonly country_of_origin: components["schemas"]["Country"]
      /** Format: double */
      eec?: number
      /** Format: double */
      el?: number
      /** Format: double */
      ep?: number
      /** Format: double */
      etd?: number
      /** Format: double */
      eu?: number
      /** Format: double */
      esca?: number
      /** Format: double */
      eccs?: number
      /** Format: double */
      eccr?: number
      /** Format: double */
      eee?: number
      /** Format: double */
      ghg_total?: number
      /** Format: double */
      ghg_reference?: number
      /** Format: double */
      ghg_reduction?: number
      /** Format: double */
      ghg_reference_red_ii?: number
      /** Format: double */
      ghg_reduction_red_ii?: number
      free_field?: string | null
      readonly added_by: components["schemas"]["EntitySummary"]
      /** Format: date-time */
      readonly created_at: string | null
      readonly carbure_vendor: components["schemas"]["EntitySummary"]
      vendor_certificate?: string | null
      vendor_certificate_type?: string | null
      data_reliability_score?: string
    }
    CarbureStockPublic: {
      readonly id: number
      carbure_id?: string
      readonly depot: components["schemas"]["Depot"]
      readonly carbure_client: components["schemas"]["Entity"]
      /** Format: double */
      remaining_volume?: number
      /** Format: double */
      remaining_weight?: number
      /** Format: double */
      remaining_lhv_amount?: number
      readonly feedstock: components["schemas"]["FeedStock"]
      readonly biofuel: components["schemas"]["Biofuel"]
      readonly country_of_origin: components["schemas"]["Country"]
      readonly carbure_production_site: components["schemas"]["ProductionSite"]
      unknown_production_site?: string | null
      readonly production_country: components["schemas"]["Country"]
      readonly carbure_supplier: components["schemas"]["Entity"]
      unknown_supplier?: string | null
      /** Format: double */
      ghg_reduction?: number
      /** Format: double */
      ghg_reduction_red_ii?: number
      readonly initial_volume: string
      readonly delivery_date: string
      readonly period: string
      readonly initial_weight: string
      readonly initial_lhv_amount: string
    }
    CarbureStockTransformationPublic: {
      transformation_type?: components["schemas"]["TransformationTypeEnum"]
      readonly source_stock: components["schemas"]["CarbureStockPublic"]
      readonly dest_stock: components["schemas"]["CarbureStockPublic"]
      /** Format: double */
      volume_deducted_from_source?: number
      /** Format: double */
      volume_destination?: number
      metadata: unknown
      transformed_by?: number | null
      entity?: number | null
      /** Format: date-time */
      readonly transformation_dt: string
    }
    /**
     * @description * `CONV` - Conventionnel
     *     * `ANN-IX-A` - ANNEXE IX-A
     *     * `ANN-IX-B` - ANNEXE IX-B
     *     * `TALLOL` - Tallol
     *     * `OTHER` - Autre
     * @enum {string}
     */
    CategoryEnum: CategoryEnum
    Comment: {
      comment?: string
    }
    /**
     * @description * `REGULAR` - REGULAR
     *     * `AUDITOR` - AUDITOR
     *     * `ADMIN` - ADMIN
     * @enum {string}
     */
    CommentTypeEnum: CommentTypeEnum
    /**
     * @description * `NO_PROBLEMO` - NO_PROBLEMO
     *     * `IN_CORRECTION` - IN_CORRECTION
     *     * `FIXED` - FIXED
     * @enum {string}
     */
    CorrectionStatusEnum: CorrectionStatusEnum
    Count: {
      drafts: number
      output: number
      input: number
      corrections: number
    }
    Country: {
      name: string
      name_en: string
      code_pays: string
      is_in_europe?: boolean
    }
    CreateLot: {
      free_field?: string | null
      carbure_stock_id?: string | null
      /** Format: date */
      delivery_date?: string | null
      biofuel_code?: string | null
      feedstock_code?: string | null
      country_code?: string | null
      production_site_certificate?: string | null
      production_site_certificate_type?: string | null
      carbure_production_site?: string | null
      unknown_producer?: string
      unknown_production_site?: string
      production_country_code?: string | null
      /** Format: date */
      production_site_commissioning_date?: string | null
      production_site_double_counting_certificate?: string | null
      /** Format: double */
      eec?: number | null
      /** Format: double */
      el?: number | null
      /** Format: double */
      ep?: number | null
      /** Format: double */
      etd?: number | null
      /** Format: double */
      eu?: number | null
      /** Format: double */
      esca?: number | null
      /** Format: double */
      eccs?: number | null
      /** Format: double */
      eccr?: number | null
      /** Format: double */
      eee?: number | null
      delivery_type?: string | null
      carbure_client_id?: number | null
      unknown_client?: string
      /** Format: double */
      quantity?: number | null
      unit?: string | null
      /** Format: double */
      volume?: number | null
      /** Format: double */
      weight?: number | null
      /** Format: double */
      lhv_amount?: number | null
      unknown_supplier?: string
      supplier_certificate?: string | null
      transport_document_type?: string | null
      transport_document_reference?: string | null
      carbure_delivery_site_depot_id?: number | null
      unknown_delivery_site?: string
      delivery_site_country_code?: string | null
      vendor_certificate?: string | null
    }
    DeclarationSummary: {
      declaration: components["schemas"]["SustainabilityDeclaration"]
      count: components["schemas"]["Count"]
    }
    DeleteLots: {
      /** @default false */
      dry_run: boolean
      selection: number[]
    }
    DeleteLotsMany: {
      /** @default false */
      dry_run: boolean
      lots_ids: number[]
      comment?: string
    }
    DeleteLotsManyResponse: {
      deletions: components["schemas"]["DeleteLotsNodeDiff"][]
      updates: components["schemas"]["DeleteLotsNodeDiff"][]
    }
    DeleteLotsNodeDiff: {
      node: {
        [key: string]: unknown
      }
      diff: {
        [key: string]: unknown
      }
    }
    DeleteLotsResponse: {
      deletions: components["schemas"]["DeleteLotsNodeDiff"][]
      updates: components["schemas"]["DeleteLotsNodeDiff"][]
    }
    /**
     * @description * `UNKNOWN` - UNKNOWN
     *     * `RFC` - RFC
     *     * `STOCK` - STOCK
     *     * `BLENDING` - BLENDING
     *     * `EXPORT` - EXPORT
     *     * `TRADING` - TRADING
     *     * `PROCESSING` - PROCESSING
     *     * `DIRECT` - DIRECT
     *     * `FLUSHED` - FLUSHED
     *     * `CONSUMPTION` - CONSUMPTION
     * @enum {string}
     */
    DeliveryTypeEnum: DeliveryTypeEnum
    Depot: {
      readonly id: number
      name: string
      city?: string
      customs_id?: string
      readonly country: components["schemas"]["Country"]
      site_type?: components["schemas"]["SiteTypeEnum"]
      address?: string
      postal_code?: string
      gps_coordinates?: string | null
      accise?: string
    }
    EmbeddedGenericError: {
      index: number
      errors: string[]
    }
    Entity: {
      readonly id: number
      name: string
      entity_type?: components["schemas"]["EntityTypeEnum"]
      has_mac?: boolean
      has_trading?: boolean
      has_direct_deliveries?: boolean
      has_stocks?: boolean
      preferred_unit?: components["schemas"]["PreferredUnitEnum"]
      legal_name?: string
      registration_id?: string
      sustainability_officer_phone_number?: string
      sustainability_officer?: string
      registered_address?: string
      registered_zipcode?: string
      registered_city?: string
      registered_country?: number | null
      activity_description?: string
      /** Format: uri */
      website?: string
      vat_number?: string
    }
    EntityPreview: {
      readonly id: number
      name: string
      entity_type?: components["schemas"]["EntityTypeEnum"]
    }
    EntitySummary: {
      readonly id: number
      name: string
      entity_type?: components["schemas"]["EntityTypeEnum"]
    }
    /**
     * @description * `Producteur` - Producteur
     *     * `Opérateur` - Opérateur
     *     * `Administration` - Administration
     *     * `Trader` - Trader
     *     * `Auditor` - Auditeur
     *     * `Administration Externe` - Administration Externe
     *     * `Charge Point Operator` - Charge Point Operator
     *     * `Compagnie aérienne` - Compagnie aérienne
     *     * `Unknown` - Unknown
     *     * `Power or Heat Producer` - Producteur d'électricité ou de chaleur
     * @enum {string}
     */
    EntityTypeEnum: EntityTypeEnum
    ErrorResponse: {
      message: string
    }
    /**
     * @description * `CREATED` - CREATED
     *     * `UPDATED` - UPDATED
     *     * `VALIDATED` - VALIDATED
     *     * `FIX_REQUESTED` - FIX_REQUESTED
     *     * `MARKED_AS_FIXED` - MARKED_AS_FIXED
     *     * `FIX_ACCEPTED` - FIX_ACCEPTED
     *     * `ACCEPTED` - ACCEPTED
     *     * `REJECTED` - REJECTED
     *     * `RECALLED` - RECALLED
     *     * `DECLARED` - DECLARED
     *     * `DELETED` - DELETED
     *     * `DECLCANCEL` - DECLCANCEL
     *     * `RESTORED` - RESTORED
     *     * `CANCELLED` - CANCELLED
     *     * `UPDATED_BY_ADMIN` - UPDATED_BY_ADMIN
     *     * `DELETED_BY_ADMIN` - DELETED_BY_ADMIN
     * @enum {string}
     */
    EventTypeEnum: EventTypeEnum
    FeedStock: {
      name: string
      name_en: string
      code: string
      category?: components["schemas"]["CategoryEnum"]
      is_double_compte?: boolean
    }
    /**
     * @description * `Default` - Valeurs par défaut
     *     * `Actual` - Valeurs réelles
     *     * `NUTS2` - Valeurs NUTS2
     * @enum {string}
     */
    GesOptionEnum: GesOptionEnum
    GroupAssignmentResponse: {
      assigned_tickets_count: number
    }
    Invalidate: {
      period: number
    }
    Lot: {
      transport_document_type?: string
      transport_document_reference?: string
      /** Format: double */
      quantity?: number
      /** Format: double */
      volume?: number
      unit?: components["schemas"]["UnitEnum"]
      biofuel_code?: string
      feedstock_code?: string
      country_code?: string
      free_field?: string
      /** Format: double */
      eec?: number
      /** Format: double */
      el?: number
      /** Format: double */
      ep?: number
      /** Format: double */
      etd?: number
      /** Format: double */
      eu?: number
      /** Format: double */
      esca?: number
      /** Format: double */
      eccs?: number
      /** Format: double */
      eccr?: number
      /** Format: double */
      eee?: number
      carbure_producer_id?: number
      unknown_producer?: string
      carbure_production_site?: string[]
      unknown_production_site?: string
      production_site_certificate?: string
      production_site_certificate_type?: string
      production_country_code?: string
      /** Format: date */
      production_site_commissioning_date?: string
      production_site_double_counting_certificate?: string
      carbure_supplier_id?: number
      unknown_supplier?: string
      supplier_certificate?: string
      supplier_certificate_type?: string
      vendor_certificate?: string
      vendor_certificate_type?: string
      delivery_type?: string
      /** Format: date */
      delivery_date?: string
      carbure_client_id?: number
      unknown_client?: string
      carbure_delivery_site_depot_id?: string[]
      unknown_delivery_site?: string
      delivery_site_country_code?: string
    }
    /**
     * @description * `DRAFT` - DRAFT
     *     * `PENDING` - PENDING
     *     * `ACCEPTED` - ACCEPTED
     *     * `REJECTED` - REJECTED
     *     * `FROZEN` - FROZEN
     *     * `DELETED` - DELETED
     * @enum {string}
     */
    LotStatusEnum: LotStatusEnum
    LotsInOut: {
      supplier: string
      client?: string
      biofuel_code: string
      delivery_type?: string
      /** Format: double */
      volume_sum: number
      /** Format: double */
      weight_sum: number
      /** Format: double */
      lhv_amount_sum: number
      /** Format: double */
      avg_ghg_reduction: number
      total: number
      pending: number
    }
    MarkConform: {
      selection: number[]
    }
    MarkNonConform: {
      selection: number[]
    }
    PaginatedAPIKeyListList: {
      /** @example 123 */
      count: number
      /**
       * Format: uri
       * @example http://api.example.org/accounts/?page=4
       */
      next?: string | null
      /**
       * Format: uri
       * @example http://api.example.org/accounts/?page=2
       */
      previous?: string | null
      results: components["schemas"]["APIKeyList"][]
    }
    PaginatedCarbureLotPublicList: {
      /** @example 123 */
      count: number
      /**
       * Format: uri
       * @example http://api.example.org/accounts/?page=4
       */
      next?: string | null
      /**
       * Format: uri
       * @example http://api.example.org/accounts/?page=2
       */
      previous?: string | null
      results: components["schemas"]["CarbureLotPublic"][]
    }
    PaginatedCarbureStockPublicList: {
      /** @example 123 */
      count: number
      /**
       * Format: uri
       * @example http://api.example.org/accounts/?page=4
       */
      next?: string | null
      /**
       * Format: uri
       * @example http://api.example.org/accounts/?page=2
       */
      previous?: string | null
      results: components["schemas"]["CarbureStockPublic"][]
    }
    PaginatedSafClientList: {
      /** @example 123 */
      count: number
      /**
       * Format: uri
       * @example http://api.example.org/accounts/?page=4
       */
      next?: string | null
      /**
       * Format: uri
       * @example http://api.example.org/accounts/?page=2
       */
      previous?: string | null
      results: components["schemas"]["SafClient"][]
    }
    PaginatedSafTicketList: {
      /** @example 123 */
      count: number
      /**
       * Format: uri
       * @example http://api.example.org/accounts/?page=4
       */
      next?: string | null
      /**
       * Format: uri
       * @example http://api.example.org/accounts/?page=2
       */
      previous?: string | null
      results: components["schemas"]["SafTicket"][]
    }
    PaginatedSafTicketSourceList: {
      /** @example 123 */
      count: number
      /**
       * Format: uri
       * @example http://api.example.org/accounts/?page=4
       */
      next?: string | null
      /**
       * Format: uri
       * @example http://api.example.org/accounts/?page=2
       */
      previous?: string | null
      results: components["schemas"]["SafTicketSource"][]
    }
    /**
     * @description * `l` - litres
     *     * `kg` - kg
     *     * `MJ` - MJ
     * @enum {string}
     */
    PreferredUnitEnum: PreferredUnitEnum
    ProductionSite: {
      readonly id: number
      readonly producer: components["schemas"]["Entity"]
      name: string
      readonly country: components["schemas"]["Country"]
      /** Format: date */
      date_mise_en_service?: string | null
      ges_option?: components["schemas"]["GesOptionEnum"]
      eligible_dc?: boolean
      dc_reference?: string
      site_siret?: string
      address?: string
      city?: string
      postal_code?: string
      gps_coordinates?: string | null
      manager_name?: string
      manager_phone?: string
      manager_email?: string
    }
    RequestFix: {
      lot_ids: number[]
    }
    Response200:
      | components["schemas"]["SnapshotReponse"]
      | components["schemas"]["AdminSnapshotReponse"]
    SafClient: {
      readonly id: number
      entity_type?: components["schemas"]["EntityTypeEnum"]
      name: string
    }
    SafTicket: {
      readonly id: number
      carbure_id?: string | null
      year: number
      assignment_period: number
      status?: components["schemas"]["StatusEnum"]
      /** Format: date */
      agreement_date?: string | null
      readonly supplier: string
      readonly client: string
      /** Format: double */
      volume: number
      readonly feedstock: components["schemas"]["FeedStock"]
      readonly biofuel: components["schemas"]["Biofuel"]
      readonly country_of_origin: components["schemas"]["Country"]
      /** Format: double */
      ghg_reduction?: number
    }
    SafTicketDetails: {
      readonly id: number
      carbure_id?: string | null
      year: number
      assignment_period: number
      status?: components["schemas"]["StatusEnum"]
      /** Format: date-time */
      readonly created_at: string | null
      readonly supplier: string
      readonly client: string
      free_field?: string | null
      /** Format: date */
      agreement_date?: string | null
      agreement_reference?: string | null
      /** Format: double */
      volume: number
      readonly feedstock: components["schemas"]["FeedStock"]
      readonly biofuel: components["schemas"]["Biofuel"]
      readonly country_of_origin: components["schemas"]["Country"]
      readonly carbure_producer: components["schemas"]["EntityPreview"]
      unknown_producer?: string | null
      readonly carbure_production_site: components["schemas"]["ProductionSite"]
      unknown_production_site?: string | null
      /** Format: date */
      production_site_commissioning_date?: string | null
      /** Format: double */
      eec?: number
      /** Format: double */
      el?: number
      /** Format: double */
      ep?: number
      /** Format: double */
      etd?: number
      /** Format: double */
      eu?: number
      /** Format: double */
      esca?: number
      /** Format: double */
      eccs?: number
      /** Format: double */
      eccr?: number
      /** Format: double */
      eee?: number
      /** Format: double */
      ghg_reduction?: number
      /** Format: double */
      ghg_total?: number
      client_comment?: string | null
      readonly parent_ticket_source: components["schemas"]["SafTicketSourcePreview"]
    }
    SafTicketPreview: {
      readonly id: number
      carbure_id?: string | null
      readonly client: string
      /** Format: date */
      agreement_date?: string | null
      /** Format: double */
      volume: number
      status?: components["schemas"]["StatusEnum"]
      /** Format: date-time */
      readonly created_at: string | null
    }
    SafTicketSource: {
      readonly id: number
      carbure_id?: string | null
      year: number
      delivery_period: number
      /** Format: date-time */
      readonly created_at: string | null
      /** Format: double */
      total_volume: number
      /** Format: double */
      assigned_volume: number
      readonly feedstock: components["schemas"]["FeedStock"]
      readonly biofuel: components["schemas"]["Biofuel"]
      readonly country_of_origin: components["schemas"]["Country"]
      /** Format: double */
      ghg_reduction?: number
      readonly assigned_tickets: components["schemas"]["SafTicketPreview"][]
      readonly parent_lot: components["schemas"]["SafTicketSourceParentLot"]
    }
    SafTicketSourceAssignment: {
      client_id: number
      /** Format: double */
      volume: number
      agreement_reference?: string
      agreement_date?: string
      free_field?: string | null
      assignment_period: number
    }
    SafTicketSourceDetails: {
      readonly id: number
      carbure_id?: string | null
      year: number
      delivery_period: number
      /** Format: date-time */
      readonly created_at: string | null
      readonly added_by: components["schemas"]["EntityPreview"]
      /** Format: double */
      total_volume: number
      /** Format: double */
      assigned_volume: number
      readonly feedstock: components["schemas"]["FeedStock"]
      readonly biofuel: components["schemas"]["Biofuel"]
      readonly country_of_origin: components["schemas"]["Country"]
      readonly assigned_tickets: components["schemas"]["SafTicketPreview"][]
      readonly carbure_producer: components["schemas"]["EntityPreview"]
      unknown_producer?: string | null
      readonly carbure_production_site: components["schemas"]["ProductionSite"]
      unknown_production_site?: string | null
      /** Format: date */
      production_site_commissioning_date?: string | null
      /** Format: double */
      eec?: number
      /** Format: double */
      el?: number
      /** Format: double */
      ep?: number
      /** Format: double */
      etd?: number
      /** Format: double */
      eu?: number
      /** Format: double */
      esca?: number
      /** Format: double */
      eccs?: number
      /** Format: double */
      eccr?: number
      /** Format: double */
      eee?: number
      /** Format: double */
      ghg_reduction?: number
      /** Format: double */
      ghg_total?: number
      parent_lot: components["schemas"]["CarbureLotPublic"]
    }
    SafTicketSourceGroupAssignment: {
      client_id: number
      /** Format: double */
      volume: number
      agreement_reference?: string
      agreement_date?: string
      free_field?: string | null
      assignment_period: number
      ticket_sources_ids: number[]
    }
    SafTicketSourceParentLot: {
      readonly id: number
      carbure_id?: string
    }
    SafTicketSourcePreview: {
      readonly id: number
      carbure_id?: string | null
      /** Format: double */
      total_volume: number
      /** Format: double */
      assigned_volume: number
    }
    Send: {
      selection: number[]
    }
    SendResponse: {
      submitted: number
      sent: number
      auto_accepted: number
      ignored: number
      rejected: number
    }
    /**
     * @description * `OTHER` - Autre
     *     * `EFS` - EFS
     *     * `EFPE` - EFPE
     *     * `OIL DEPOT` - OIL DEPOT
     *     * `BIOFUEL DEPOT` - BIOFUEL DEPOT
     *     * `HEAT PLANT` - HEAT PLANT
     *     * `POWER PLANT` - POWER PLANT
     *     * `COGENERATION PLANT` - COGENERATION PLANT
     *     * `PRODUCTION SITE` - PRODUCTION SITE
     *     * `EFCA` - EFCA
     * @enum {string}
     */
    SiteTypeEnum: SiteTypeEnum
    SnapshotReponse: {
      draft: number
      in_total: number
      in_pending: number
      in_tofix: number
      stock: number
      stock_total: number
      out_total: number
      out_pending: number
      out_tofix: number
      draft_imported: number
      draft_stocks: number
    }
    Split: {
      payload: components["schemas"]["SplitCreate"][]
    }
    SplitCreate: {
      stock_id: string
      /** Format: double */
      volume: number
      /** Format: date */
      delivery_date: string
      supplier_certificate?: string
      /** Format: date */
      dispatch_date?: string
      unknown_client?: string
      unknown_delivery_site?: string
      delivery_site_country_id?: string
      transport_document_type?: string
      delivery_type?: string
      transport_document_reference?: string
      carbure_delivery_site_id?: string
      carbure_client_id?: string
    }
    SplitResponse: {
      /** @default success */
      status: string
      data: number[]
    }
    /**
     * @description * `PENDING` - En attente
     *     * `ACCEPTED` - Accepté
     *     * `REJECTED` - Refusé
     * @enum {string}
     */
    StatusEnum: StatusEnum
    StockCancelTransformation: {
      stock_ids: number[]
    }
    StockDetailsResponse: {
      stock: components["schemas"]["CarbureStockPublic"]
      parent_lot: components["schemas"]["CarbureLotPublic"] | null
      parent_transformation:
        | components["schemas"]["CarbureStockTransformationPublic"]
        | null
      children_lot: components["schemas"]["CarbureLotPublic"][]
      children_transformation: components["schemas"]["CarbureStockTransformationPublic"][]
      events: components["schemas"]["CarbureLotComment"][]
      updates: components["schemas"]["CarbureLotComment"][]
      comments: components["schemas"]["CarbureLotEvent"][]
    }
    StockFlush: {
      stock_ids: number[]
      free_field?: string | null
    }
    StockSummary: {
      supplier: string
      biofuel_code: string
      /** Format: double */
      remaining_volume_sum: number
      /** Format: double */
      remaining_weight_sum: number
      /** Format: double */
      remaining_lhv_amount_sum: number
      /** Format: double */
      avg_ghg_reduction: number
      total: number
    }
    StocksSummaryResponse: {
      count: number
      /** Format: double */
      total_remaining_volume: number
      /** Format: double */
      total_remaining_weight: number
      /** Format: double */
      total_remaining_lhv_amount: number
      stock: components["schemas"]["StockSummary"][]
    }
    SubmitFix: {
      lot_ids: number[]
    }
    SummaryResponse: {
      count: number
      /** Format: double */
      total_volume: number
      /** Format: double */
      total_weight: number
      /** Format: double */
      total_lhv_amount: number
      /** In  */
      in_: components["schemas"]["LotsInOut"][]
      out: components["schemas"]["LotsInOut"][]
      lots: components["schemas"]["LotsInOut"][]
    }
    SustainabilityDeclaration: {
      entity: components["schemas"]["Entity"]
      declared?: boolean
      checked?: boolean
      /** Format: date */
      deadline?: string
      readonly period: string
      reminder_count?: number
    }
    TogglePin: {
      selection: number[]
      /** @default false */
      notify_admin: boolean
      /** @default false */
      notify_auditor: boolean
    }
    ToggleWarning: {
      errors: string[]
      /** @default false */
      checked: boolean
    }
    Transform: {
      payload: unknown
    }
    /**
     * @description * `UNKNOWN` - UNKNOWN
     *     * `ETH_ETBE` - ETH_ETBE
     * @enum {string}
     */
    TransformationTypeEnum: TransformationTypeEnum
    /**
     * @description * `DAU` - DAU
     *     * `DAE` - DAE
     *     * `DSA` - DSA
     *     * `DSAC` - DSAC
     *     * `DSP` - DSP
     *     * `OTHER` - OTHER
     * @enum {string}
     */
    TransportDocumentTypeEnum: TransportDocumentTypeEnum
    /**
     * @description * `l` - l
     *     * `kg` - kg
     *     * `mj` - pci
     * @enum {string}
     */
    UnitEnum: UnitEnum
    UpdateMany: {
      transport_document_type?: string
      transport_document_reference?: string
      /** Format: double */
      quantity?: number
      /** Format: double */
      volume?: number
      unit?: components["schemas"]["UnitEnum"]
      biofuel_code?: string
      feedstock_code?: string
      country_code?: string
      free_field?: string
      /** Format: double */
      eec?: number
      /** Format: double */
      el?: number
      /** Format: double */
      ep?: number
      /** Format: double */
      etd?: number
      /** Format: double */
      eu?: number
      /** Format: double */
      esca?: number
      /** Format: double */
      eccs?: number
      /** Format: double */
      eccr?: number
      /** Format: double */
      eee?: number
      carbure_producer_id?: number
      unknown_producer?: string
      carbure_production_site?: string[]
      unknown_production_site?: string
      production_site_certificate?: string
      production_site_certificate_type?: string
      production_country_code?: string
      /** Format: date */
      production_site_commissioning_date?: string
      production_site_double_counting_certificate?: string
      carbure_supplier_id?: number
      unknown_supplier?: string
      supplier_certificate?: string
      supplier_certificate_type?: string
      vendor_certificate?: string
      vendor_certificate_type?: string
      delivery_type?: string
      /** Format: date */
      delivery_date?: string
      carbure_client_id?: number
      unknown_client?: string
      carbure_delivery_site_depot_id?: string[]
      unknown_delivery_site?: string
      delivery_site_country_code?: string
      /** @default false */
      dry_run: boolean
      lots_ids: number[]
      comment: string
    }
    ValidateDeclaration: {
      period: number
    }
    Years: {
      years: number[]
    }
    addExcelResponse: {
      lots: number
      valid: number
      invalid: number
    }
  }
  responses: never
  parameters: never
  requestBodies: never
  headers: never
  pathItems: never
}
export type $defs = Record<string, never>
export interface operations {
  apikey_list: {
    parameters: {
      query?: {
        /** @description Which field to use when ordering the results. */
        ordering?: string
        /** @description A page number within the paginated result set. */
        page?: number
        /** @description Number of results to return per page. */
        page_size?: number
        /** @description A search term. */
        search?: string
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody?: never
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["PaginatedAPIKeyListList"]
        }
      }
    }
  }
  apikey_create: {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    requestBody?: {
      content: {
        "application/json": components["schemas"]["APIKey"]
        "application/x-www-form-urlencoded": components["schemas"]["APIKey"]
        "multipart/form-data": components["schemas"]["APIKey"]
      }
    }
    responses: {
      201: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["APIKey"]
        }
      }
    }
  }
  apikey_retrieve: {
    parameters: {
      query?: never
      header?: never
      path: {
        id: string
      }
      cookie?: never
    }
    requestBody?: never
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["APIKey"]
        }
      }
    }
  }
  apikey_revoke_create: {
    parameters: {
      query?: never
      header?: never
      path: {
        id: string
      }
      cookie?: never
    }
    requestBody?: {
      content: {
        "application/json": components["schemas"]["APIKey"]
        "application/x-www-form-urlencoded": components["schemas"]["APIKey"]
        "multipart/form-data": components["schemas"]["APIKey"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["APIKey"]
        }
      }
    }
  }
  entities_enable_create: {
    parameters: {
      query: {
        /** @description The id of the admin entity enabling the company */
        entity_id: number
      }
      header?: never
      path: {
        /** @description A unique integer value identifying this Entity. */
        id: number
      }
      cookie?: never
    }
    requestBody?: never
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": unknown
        }
      }
      400: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["ErrorResponse"]
        }
      }
    }
  }
  saf_clients_list: {
    parameters: {
      query?: {
        entity_id?: string
        /** @description Which field to use when ordering the results. */
        ordering?: string
        /** @description A page number within the paginated result set. */
        page?: number
        /** @description Number of results to return per page. */
        page_size?: number
        /** @description A search term. */
        search?: string
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody?: never
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["PaginatedSafClientList"]
        }
      }
    }
  }
  saf_clients_retrieve: {
    parameters: {
      query?: never
      header?: never
      path: {
        /** @description A unique integer value identifying this Entity. */
        id: number
      }
      cookie?: never
    }
    requestBody?: never
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["SafClient"]
        }
      }
    }
  }
  saf_snapshot_retrieve: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
        /** @description Year */
        year: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody?: never
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json":
            | {
                tickets_pending: number
                tickets_accepted: number
              }
            | {
                ticket_sources_available: number
                ticket_sources_history: number
                tickets_assigned: number
                tickets_assigned_pending: number
                tickets_assigned_accepted: number
                tickets_assigned_rejected: number
                tickets_received: number
                tickets_received_pending: number
                tickets_received_accepted: number
              }
        }
      }
      400: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["ErrorResponse"]
        }
      }
    }
  }
  saf_ticket_sources_list: {
    parameters: {
      query: {
        /** @description Les valeurs multiples doivent être séparées par des virgules. */
        clients?: string[]
        /** @description Les valeurs multiples doivent être séparées par des virgules. */
        countries_of_origin?: string[]
        /** @description Les valeurs multiples doivent être séparées par des virgules. */
        delivery_sites?: string[]
        entity_id: number
        /** @description Les valeurs multiples doivent être séparées par des virgules. */
        feedstocks?: string[]
        /** @description Ordre
         *
         *     * `volume` - Volume
         *     * `-volume` - Volume (décroissant)
         *     * `period` - Period
         *     * `-period` - Period (décroissant)
         *     * `feedstock` - Feedstock
         *     * `-feedstock` - Feedstock (décroissant)
         *     * `ghg_reduction` - Ghg reduction
         *     * `-ghg_reduction` - Ghg reduction (décroissant) */
        order?: PathsApiSafTicketSourcesGetParametersQueryOrder[]
        /** @description Which field to use when ordering the results. */
        ordering?: string
        /** @description A page number within the paginated result set. */
        page?: number
        /** @description Number of results to return per page. */
        page_size?: number
        /** @description Les valeurs multiples doivent être séparées par des virgules. */
        periods?: number[]
        /** @description Les valeurs multiples doivent être séparées par des virgules. */
        production_sites?: string[]
        /** @description A search term. */
        search?: string
        status?: string
        /** @description Les valeurs multiples doivent être séparées par des virgules. */
        suppliers?: string[]
        year?: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody?: never
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["PaginatedSafTicketSourceList"]
        }
      }
    }
  }
  saf_ticket_sources_retrieve: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path: {
        /** @description A unique integer value identifying this Tickets source SAF. */
        id: number
      }
      cookie?: never
    }
    requestBody?: never
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["SafTicketSourceDetails"]
        }
      }
    }
  }
  saf_ticket_sources_assign_create: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path: {
        /** @description A unique integer value identifying this Tickets source SAF. */
        id: number
      }
      cookie?: never
    }
    requestBody: {
      content: {
        "application/json": components["schemas"]["SafTicketSourceAssignment"]
        "application/x-www-form-urlencoded": components["schemas"]["SafTicketSourceAssignment"]
        "multipart/form-data": components["schemas"]["SafTicketSourceAssignment"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["SafTicketSourceAssignment"]
        }
      }
    }
  }
  saf_ticket_sources_export_retrieve: {
    parameters: {
      query: {
        /** @description Les valeurs multiples doivent être séparées par des virgules. */
        clients?: string[]
        /** @description Les valeurs multiples doivent être séparées par des virgules. */
        countries_of_origin?: string[]
        /** @description Les valeurs multiples doivent être séparées par des virgules. */
        delivery_sites?: string[]
        entity_id: number
        /** @description Les valeurs multiples doivent être séparées par des virgules. */
        feedstocks?: string[]
        /** @description Ordre
         *
         *     * `volume` - Volume
         *     * `-volume` - Volume (décroissant)
         *     * `period` - Period
         *     * `-period` - Period (décroissant)
         *     * `feedstock` - Feedstock
         *     * `-feedstock` - Feedstock (décroissant)
         *     * `ghg_reduction` - Ghg reduction
         *     * `-ghg_reduction` - Ghg reduction (décroissant) */
        order?: PathsApiSafTicketSourcesGetParametersQueryOrder[]
        /** @description Which field to use when ordering the results. */
        ordering?: string
        /** @description Les valeurs multiples doivent être séparées par des virgules. */
        periods?: number[]
        /** @description Les valeurs multiples doivent être séparées par des virgules. */
        production_sites?: string[]
        /** @description A search term. */
        search?: string
        status?: string
        /** @description Les valeurs multiples doivent être séparées par des virgules. */
        suppliers?: string[]
        year?: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody?: never
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/vnd.ms-excel": string
        }
      }
    }
  }
  saf_ticket_sources_filters_retrieve: {
    parameters: {
      query: {
        /** @description Les valeurs multiples doivent être séparées par des virgules. */
        clients?: string[]
        /** @description Les valeurs multiples doivent être séparées par des virgules. */
        countries_of_origin?: string[]
        /** @description Les valeurs multiples doivent être séparées par des virgules. */
        delivery_sites?: string[]
        entity_id: number
        /** @description Les valeurs multiples doivent être séparées par des virgules. */
        feedstocks?: string[]
        /** @description Filter string to apply */
        filter?: string
        /** @description Ordre
         *
         *     * `volume` - Volume
         *     * `-volume` - Volume (décroissant)
         *     * `period` - Period
         *     * `-period` - Period (décroissant)
         *     * `feedstock` - Feedstock
         *     * `-feedstock` - Feedstock (décroissant)
         *     * `ghg_reduction` - Ghg reduction
         *     * `-ghg_reduction` - Ghg reduction (décroissant) */
        order?: PathsApiSafTicketSourcesGetParametersQueryOrder[]
        /** @description Which field to use when ordering the results. */
        ordering?: string
        /** @description Les valeurs multiples doivent être séparées par des virgules. */
        periods?: number[]
        /** @description Les valeurs multiples doivent être séparées par des virgules. */
        production_sites?: string[]
        /** @description A search term. */
        search?: string
        status?: string
        /** @description Les valeurs multiples doivent être séparées par des virgules. */
        suppliers?: string[]
        year?: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody?: never
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": string[]
        }
      }
    }
  }
  saf_ticket_sources_group_assign_create: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody: {
      content: {
        "application/json": components["schemas"]["SafTicketSourceGroupAssignment"]
        "application/x-www-form-urlencoded": components["schemas"]["SafTicketSourceGroupAssignment"]
        "multipart/form-data": components["schemas"]["SafTicketSourceGroupAssignment"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["GroupAssignmentResponse"]
        }
      }
      400: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["ErrorResponse"]
        }
      }
    }
  }
  saf_tickets_list: {
    parameters: {
      query: {
        /** @description Les valeurs multiples doivent être séparées par des virgules. */
        clients?: string[]
        /** @description Les valeurs multiples doivent être séparées par des virgules. */
        countries_of_origin?: string[]
        entity_id: number
        /** @description Les valeurs multiples doivent être séparées par des virgules. */
        feedstocks?: string[]
        /** @description Ordre
         *
         *     * `client` - Client
         *     * `-client` - Client (décroissant)
         *     * `volume` - Volume
         *     * `-volume` - Volume (décroissant)
         *     * `period` - Period
         *     * `-period` - Period (décroissant)
         *     * `feedstock` - Feedstock
         *     * `-feedstock` - Feedstock (décroissant)
         *     * `ghg_reduction` - Ghg reduction
         *     * `-ghg_reduction` - Ghg reduction (décroissant)
         *     * `created_at` - Created at
         *     * `-created_at` - Created at (décroissant)
         *     * `suppliers` - Suppliers
         *     * `-suppliers` - Suppliers (décroissant) */
        order?: PathsApiSafTicketsGetParametersQueryOrder[]
        /** @description Which field to use when ordering the results. */
        ordering?: string
        /** @description A page number within the paginated result set. */
        page?: number
        /** @description Number of results to return per page. */
        page_size?: number
        /** @description Les valeurs multiples doivent être séparées par des virgules. */
        periods?: number[]
        /** @description Les valeurs multiples doivent être séparées par des virgules. */
        production_sites?: string[]
        /** @description A search term. */
        search?: string
        status?: string
        /** @description Les valeurs multiples doivent être séparées par des virgules. */
        suppliers?: string[]
        year?: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody?: never
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["PaginatedSafTicketList"]
        }
      }
    }
  }
  saf_tickets_retrieve: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path: {
        /** @description A unique integer value identifying this Ticket SAF. */
        id: number
      }
      cookie?: never
    }
    requestBody?: never
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["SafTicketDetails"]
        }
      }
    }
  }
  saf_tickets_accept_create: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path: {
        /** @description A unique integer value identifying this Ticket SAF. */
        id: number
      }
      cookie?: never
    }
    requestBody?: {
      content: {
        "application/json": components["schemas"]["Comment"]
        "application/x-www-form-urlencoded": components["schemas"]["Comment"]
        "multipart/form-data": components["schemas"]["Comment"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": unknown
        }
      }
      400: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["ErrorResponse"]
        }
      }
    }
  }
  saf_tickets_cancel_create: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path: {
        /** @description A unique integer value identifying this Ticket SAF. */
        id: number
      }
      cookie?: never
    }
    requestBody?: {
      content: {
        "application/json": components["schemas"]["Comment"]
        "application/x-www-form-urlencoded": components["schemas"]["Comment"]
        "multipart/form-data": components["schemas"]["Comment"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": unknown
        }
      }
      400: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["ErrorResponse"]
        }
      }
    }
  }
  saf_tickets_credit_source_retrieve: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path: {
        /** @description A unique integer value identifying this Ticket SAF. */
        id: number
      }
      cookie?: never
    }
    requestBody?: never
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["SafTicket"]
        }
      }
    }
  }
  saf_tickets_reject_create: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path: {
        /** @description A unique integer value identifying this Ticket SAF. */
        id: number
      }
      cookie?: never
    }
    requestBody?: {
      content: {
        "application/json": components["schemas"]["Comment"]
        "application/x-www-form-urlencoded": components["schemas"]["Comment"]
        "multipart/form-data": components["schemas"]["Comment"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": unknown
        }
      }
      400: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["ErrorResponse"]
        }
      }
    }
  }
  saf_tickets_export_retrieve: {
    parameters: {
      query: {
        /** @description Les valeurs multiples doivent être séparées par des virgules. */
        clients?: string[]
        /** @description Les valeurs multiples doivent être séparées par des virgules. */
        countries_of_origin?: string[]
        entity_id: number
        /** @description Les valeurs multiples doivent être séparées par des virgules. */
        feedstocks?: string[]
        /** @description Ordre
         *
         *     * `client` - Client
         *     * `-client` - Client (décroissant)
         *     * `volume` - Volume
         *     * `-volume` - Volume (décroissant)
         *     * `period` - Period
         *     * `-period` - Period (décroissant)
         *     * `feedstock` - Feedstock
         *     * `-feedstock` - Feedstock (décroissant)
         *     * `ghg_reduction` - Ghg reduction
         *     * `-ghg_reduction` - Ghg reduction (décroissant)
         *     * `created_at` - Created at
         *     * `-created_at` - Created at (décroissant)
         *     * `suppliers` - Suppliers
         *     * `-suppliers` - Suppliers (décroissant) */
        order?: PathsApiSafTicketsGetParametersQueryOrder[]
        /** @description Which field to use when ordering the results. */
        ordering?: string
        /** @description Les valeurs multiples doivent être séparées par des virgules. */
        periods?: number[]
        /** @description Les valeurs multiples doivent être séparées par des virgules. */
        production_sites?: string[]
        /** @description A search term. */
        search?: string
        status?: string
        /** @description Les valeurs multiples doivent être séparées par des virgules. */
        suppliers?: string[]
        year?: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody?: never
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/vnd.ms-excel": string
        }
      }
    }
  }
  saf_tickets_filters_retrieve: {
    parameters: {
      query: {
        /** @description Les valeurs multiples doivent être séparées par des virgules. */
        clients?: string[]
        /** @description Les valeurs multiples doivent être séparées par des virgules. */
        countries_of_origin?: string[]
        entity_id: number
        /** @description Les valeurs multiples doivent être séparées par des virgules. */
        feedstocks?: string[]
        /** @description Filter string to apply */
        filter?: string
        /** @description Ordre
         *
         *     * `client` - Client
         *     * `-client` - Client (décroissant)
         *     * `volume` - Volume
         *     * `-volume` - Volume (décroissant)
         *     * `period` - Period
         *     * `-period` - Period (décroissant)
         *     * `feedstock` - Feedstock
         *     * `-feedstock` - Feedstock (décroissant)
         *     * `ghg_reduction` - Ghg reduction
         *     * `-ghg_reduction` - Ghg reduction (décroissant)
         *     * `created_at` - Created at
         *     * `-created_at` - Created at (décroissant)
         *     * `suppliers` - Suppliers
         *     * `-suppliers` - Suppliers (décroissant) */
        order?: PathsApiSafTicketsGetParametersQueryOrder[]
        /** @description Which field to use when ordering the results. */
        ordering?: string
        /** @description Les valeurs multiples doivent être séparées par des virgules. */
        periods?: number[]
        /** @description Les valeurs multiples doivent être séparées par des virgules. */
        production_sites?: string[]
        /** @description A search term. */
        search?: string
        status?: string
        /** @description Les valeurs multiples doivent être séparées par des virgules. */
        suppliers?: string[]
        year?: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody?: never
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": string[]
        }
      }
    }
  }
  saf_years_retrieve: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody?: never
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": number[]
        }
      }
      400: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["ErrorResponse"]
        }
      }
    }
  }
  transactions_lots_list: {
    parameters: {
      query?: {
        added_by?: string
        biofuels?: string
        category?: string
        clients?: string
        conformity?: string
        correction_status?: string
        countries_of_origin?: string
        deadline?: boolean
        delivery_sites?: string
        delivery_types?: string
        errors?: string
        feedstocks?: string
        invalid?: boolean
        lot_status?: string
        ml_scoring?: string
        /** @description Which field to use when ordering the results. */
        ordering?: string
        /** @description A page number within the paginated result set. */
        page?: number
        /** @description Number of results to return per page. */
        page_size?: number
        periods?: string
        production_sites?: string
        scores?: string
        /** @description A search term. */
        search?: string
        selection?: string
        /** @description * `DRAFTS` - DRAFTS
         *     * `IN` - IN
         *     * `OUT` - OUT
         *     * `DECLARATION` - DECLARATION
         *     * `ALERTS` - ALERTS
         *     * `LOTS` - LOTS */
        status?: PathsApiTransactionsLotsGetParametersQueryStatus
        suppliers?: string
        year?: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody?: never
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["PaginatedCarbureLotPublicList"]
        }
      }
    }
  }
  transactions_lots_retrieve: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path: {
        /** @description A unique integer value identifying this CarbureLot. */
        id: number
      }
      cookie?: never
    }
    requestBody?: never
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["CarbureLotPublic"]
        }
      }
    }
  }
  transactions_lots_duplicate_retrieve: {
    parameters: {
      query?: never
      header?: never
      path: {
        /** @description A unique integer value identifying this CarbureLot. */
        id: number
      }
      cookie?: never
    }
    requestBody?: never
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["CarbureLotPublic"]
        }
      }
    }
  }
  transactions_lots_toggle_warning_create: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path: {
        /** @description A unique integer value identifying this CarbureLot. */
        id: number
      }
      cookie?: never
    }
    requestBody: {
      content: {
        "application/json": components["schemas"]["ToggleWarning"]
        "application/x-www-form-urlencoded": components["schemas"]["ToggleWarning"]
        "multipart/form-data": components["schemas"]["ToggleWarning"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["CarbureLotPublic"]
        }
      }
    }
  }
  transactions_lots_update_lot_create: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path: {
        /** @description A unique integer value identifying this CarbureLot. */
        id: number
      }
      cookie?: never
    }
    requestBody?: {
      content: {
        "application/json": components["schemas"]["Lot"]
        "application/x-www-form-urlencoded": components["schemas"]["Lot"]
        "multipart/form-data": components["schemas"]["Lot"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["CarbureLotPublic"]
        }
      }
    }
  }
  transactions_lots_accept_blending_create: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody: {
      content: {
        "application/json": components["schemas"]["AcceptBlending"]
        "application/x-www-form-urlencoded": components["schemas"]["AcceptBlending"]
        "multipart/form-data": components["schemas"]["AcceptBlending"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["CarbureLotPublic"]
        }
      }
    }
  }
  transactions_lots_accept_consumption_create: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody: {
      content: {
        "application/json": components["schemas"]["AcceptConsumption"]
        "application/x-www-form-urlencoded": components["schemas"]["AcceptConsumption"]
        "multipart/form-data": components["schemas"]["AcceptConsumption"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["CarbureLotPublic"]
        }
      }
    }
  }
  transactions_lots_accept_direct_delivery_create: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody: {
      content: {
        "application/json": components["schemas"]["AcceptDirectDelivery"]
        "application/x-www-form-urlencoded": components["schemas"]["AcceptDirectDelivery"]
        "multipart/form-data": components["schemas"]["AcceptDirectDelivery"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["CarbureLotPublic"]
        }
      }
    }
  }
  transactions_lots_accept_export_create: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody: {
      content: {
        "application/json": components["schemas"]["AcceptExport"]
        "application/x-www-form-urlencoded": components["schemas"]["AcceptExport"]
        "multipart/form-data": components["schemas"]["AcceptExport"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["CarbureLotPublic"]
        }
      }
    }
  }
  transactions_lots_accept_in_stock_create: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody: {
      content: {
        "application/json": components["schemas"]["AcceptStock"]
        "application/x-www-form-urlencoded": components["schemas"]["AcceptStock"]
        "multipart/form-data": components["schemas"]["AcceptStock"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["CarbureLotPublic"]
        }
      }
    }
  }
  transactions_lots_accept_processing_create: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody: {
      content: {
        "application/json": components["schemas"]["AcceptProcessing"]
        "application/x-www-form-urlencoded": components["schemas"]["AcceptProcessing"]
        "multipart/form-data": components["schemas"]["AcceptProcessing"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["CarbureLotPublic"]
        }
      }
    }
  }
  transactions_lots_accept_rfc_create: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody: {
      content: {
        "application/json": components["schemas"]["AcceptRFC"]
        "application/x-www-form-urlencoded": components["schemas"]["AcceptRFC"]
        "multipart/form-data": components["schemas"]["AcceptRFC"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["CarbureLotPublic"]
        }
      }
    }
  }
  transactions_lots_accept_trading_create: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody: {
      content: {
        "application/json": components["schemas"]["AcceptTrading"]
        "application/x-www-form-urlencoded": components["schemas"]["AcceptTrading"]
        "multipart/form-data": components["schemas"]["AcceptTrading"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["CarbureLotPublic"]
        }
      }
    }
  }
  transactions_lots_add_create: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody?: {
      content: {
        "application/json": components["schemas"]["CreateLot"]
        "application/x-www-form-urlencoded": components["schemas"]["CreateLot"]
        "multipart/form-data": components["schemas"]["CreateLot"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["CarbureLotPublic"]
        }
      }
    }
  }
  transactions_lots_add_comment_create: {
    parameters: {
      query: {
        added_by?: string
        biofuels?: string
        category?: string
        clients?: string
        conformity?: string
        correction_status?: string
        countries_of_origin?: string
        deadline?: boolean
        delivery_sites?: string
        delivery_types?: string
        /** @description Entity ID */
        entity_id: number
        errors?: string
        feedstocks?: string
        invalid?: boolean
        lot_status?: string
        ml_scoring?: string
        /** @description Which field to use when ordering the results. */
        ordering?: string
        periods?: string
        production_sites?: string
        scores?: string
        /** @description A search term. */
        search?: string
        selection?: string
        /** @description * `DRAFTS` - DRAFTS
         *     * `IN` - IN
         *     * `OUT` - OUT
         *     * `DECLARATION` - DECLARATION
         *     * `ALERTS` - ALERTS
         *     * `LOTS` - LOTS */
        status?: PathsApiTransactionsLotsGetParametersQueryStatus
        suppliers?: string
        year?: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody: {
      content: {
        "application/json": components["schemas"]["AddComment"]
        "application/x-www-form-urlencoded": components["schemas"]["AddComment"]
        "multipart/form-data": components["schemas"]["AddComment"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["CarbureLotPublic"]
        }
      }
    }
  }
  transactions_lots_add_excel_create: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody: {
      content: {
        "application/json": components["schemas"]["AddExcel"]
        "application/x-www-form-urlencoded": components["schemas"]["AddExcel"]
        "multipart/form-data": components["schemas"]["AddExcel"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["addExcelResponse"]
        }
      }
    }
  }
  transactions_lots_admin_declarations_retrieve: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
        /** @description Period */
        period: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody?: never
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["DeclarationSummary"]
        }
      }
    }
  }
  transactions_lots_approuve_fix_create: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody: {
      content: {
        "application/json": components["schemas"]["ApproveFix"]
        "application/x-www-form-urlencoded": components["schemas"]["ApproveFix"]
        "multipart/form-data": components["schemas"]["ApproveFix"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["CarbureLotPublic"]
        }
      }
    }
  }
  transactions_lots_bulk_create_create: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody: {
      content: {
        "application/json": components["schemas"]["CreateLot"][]
        "application/x-www-form-urlencoded": components["schemas"]["CreateLot"][]
        "multipart/form-data": components["schemas"]["CreateLot"][]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["BulkCreateResponse"]
        }
      }
    }
  }
  transactions_lots_cancel_accept_create: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody: {
      content: {
        "application/json": components["schemas"]["CancelAccept"]
        "application/x-www-form-urlencoded": components["schemas"]["CancelAccept"]
        "multipart/form-data": components["schemas"]["CancelAccept"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["CarbureLotPublic"]
        }
      }
    }
  }
  transactions_lots_declarations_retrieve: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
        /** @description Year */
        year: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody?: never
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["CarbureLotPublic"]
        }
      }
    }
  }
  transactions_lots_declarations_invalidate_create: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody: {
      content: {
        "application/json": components["schemas"]["Invalidate"]
        "application/x-www-form-urlencoded": components["schemas"]["Invalidate"]
        "multipart/form-data": components["schemas"]["Invalidate"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["CarbureLotPublic"]
        }
      }
    }
  }
  transactions_lots_declarations_validate_create: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody: {
      content: {
        "application/json": components["schemas"]["ValidateDeclaration"]
        "application/x-www-form-urlencoded": components["schemas"]["ValidateDeclaration"]
        "multipart/form-data": components["schemas"]["ValidateDeclaration"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["CarbureLotPublic"]
        }
      }
    }
  }
  transactions_lots_delete_create: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody: {
      content: {
        "application/json": components["schemas"]["DeleteLots"]
        "application/x-www-form-urlencoded": components["schemas"]["DeleteLots"]
        "multipart/form-data": components["schemas"]["DeleteLots"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["DeleteLotsResponse"]
        }
      }
    }
  }
  transactions_lots_delete_many_create: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody: {
      content: {
        "application/json": components["schemas"]["DeleteLotsMany"]
        "application/x-www-form-urlencoded": components["schemas"]["DeleteLotsMany"]
        "multipart/form-data": components["schemas"]["DeleteLotsMany"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["DeleteLotsManyResponse"]
        }
      }
    }
  }
  transactions_lots_export_retrieve: {
    parameters: {
      query: {
        added_by?: string
        biofuels?: string
        category?: string
        clients?: string
        conformity?: string
        correction_status?: string
        countries_of_origin?: string
        deadline?: boolean
        delivery_sites?: string
        delivery_types?: string
        /** @description Entity ID */
        entity_id: number
        errors?: string
        feedstocks?: string
        invalid?: boolean
        lot_status?: string
        ml_scoring?: string
        /** @description Which field to use when ordering the results. */
        ordering?: string
        periods?: string
        production_sites?: string
        scores?: string
        /** @description A search term. */
        search?: string
        selection?: string
        /** @description * `DRAFTS` - DRAFTS
         *     * `IN` - IN
         *     * `OUT` - OUT
         *     * `DECLARATION` - DECLARATION
         *     * `ALERTS` - ALERTS
         *     * `LOTS` - LOTS */
        status?: PathsApiTransactionsLotsGetParametersQueryStatus
        suppliers?: string
        year?: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody?: never
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/vnd.ms-excel": string
        }
      }
    }
  }
  transactions_lots_filters_retrieve: {
    parameters: {
      query: {
        added_by?: string
        biofuels?: string
        category?: string
        clients?: string
        conformity?: string
        correction_status?: string
        countries_of_origin?: string
        deadline?: boolean
        delivery_sites?: string
        delivery_types?: string
        /** @description Entity ID */
        entity_id: number
        errors?: string
        feedstocks?: string
        invalid?: boolean
        lot_status?: string
        ml_scoring?: string
        /** @description Which field to use when ordering the results. */
        ordering?: string
        periods?: string
        production_sites?: string
        scores?: string
        /** @description A search term. */
        search?: string
        selection?: string
        /** @description * `DRAFTS` - DRAFTS
         *     * `IN` - IN
         *     * `OUT` - OUT
         *     * `DECLARATION` - DECLARATION
         *     * `ALERTS` - ALERTS
         *     * `LOTS` - LOTS */
        status?: PathsApiTransactionsLotsGetParametersQueryStatus
        suppliers?: string
        year?: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody?: never
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["CarbureLotPublic"]
        }
      }
    }
  }
  transactions_lots_map_retrieve: {
    parameters: {
      query: {
        added_by?: string
        biofuels?: string
        category?: string
        clients?: string
        conformity?: string
        correction_status?: string
        countries_of_origin?: string
        deadline?: boolean
        delivery_sites?: string
        delivery_types?: string
        /** @description Entity ID */
        entity_id: number
        errors?: string
        feedstocks?: string
        invalid?: boolean
        lot_status?: string
        ml_scoring?: string
        /** @description Which field to use when ordering the results. */
        ordering?: string
        periods?: string
        production_sites?: string
        scores?: string
        /** @description A search term. */
        search?: string
        selection?: string
        /** @description * `DRAFTS` - DRAFTS
         *     * `IN` - IN
         *     * `OUT` - OUT
         *     * `DECLARATION` - DECLARATION
         *     * `ALERTS` - ALERTS
         *     * `LOTS` - LOTS */
        status?: PathsApiTransactionsLotsGetParametersQueryStatus
        suppliers?: string
        year?: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody?: never
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "text/html": string
        }
      }
    }
  }
  transactions_lots_mark_conform_create: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody: {
      content: {
        "application/json": components["schemas"]["MarkConform"]
        "application/x-www-form-urlencoded": components["schemas"]["MarkConform"]
        "multipart/form-data": components["schemas"]["MarkConform"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["CarbureLotPublic"]
        }
      }
    }
  }
  transactions_lots_mark_non_conform_create: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody: {
      content: {
        "application/json": components["schemas"]["MarkNonConform"]
        "application/x-www-form-urlencoded": components["schemas"]["MarkNonConform"]
        "multipart/form-data": components["schemas"]["MarkNonConform"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["CarbureLotPublic"]
        }
      }
    }
  }
  transactions_lots_reject_retrieve: {
    parameters: {
      query: {
        added_by?: string
        biofuels?: string
        category?: string
        clients?: string
        conformity?: string
        correction_status?: string
        countries_of_origin?: string
        deadline?: boolean
        delivery_sites?: string
        delivery_types?: string
        /** @description Entity ID */
        entity_id: number
        errors?: string
        feedstocks?: string
        invalid?: boolean
        lot_status?: string
        ml_scoring?: string
        /** @description Which field to use when ordering the results. */
        ordering?: string
        periods?: string
        production_sites?: string
        scores?: string
        /** @description A search term. */
        search?: string
        selection?: string
        /** @description * `DRAFTS` - DRAFTS
         *     * `IN` - IN
         *     * `OUT` - OUT
         *     * `DECLARATION` - DECLARATION
         *     * `ALERTS` - ALERTS
         *     * `LOTS` - LOTS */
        status?: PathsApiTransactionsLotsGetParametersQueryStatus
        suppliers?: string
        year?: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody?: never
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["CarbureLotPublic"]
        }
      }
    }
  }
  transactions_lots_request_fix_create: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody: {
      content: {
        "application/json": components["schemas"]["RequestFix"]
        "application/x-www-form-urlencoded": components["schemas"]["RequestFix"]
        "multipart/form-data": components["schemas"]["RequestFix"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["CarbureLotPublic"]
        }
      }
    }
  }
  transactions_lots_send_create: {
    parameters: {
      query: {
        added_by?: string
        biofuels?: string
        category?: string
        clients?: string
        conformity?: string
        correction_status?: string
        countries_of_origin?: string
        deadline?: boolean
        delivery_sites?: string
        delivery_types?: string
        /** @description Entity ID */
        entity_id: number
        errors?: string
        feedstocks?: string
        invalid?: boolean
        lot_status?: string
        ml_scoring?: string
        /** @description Which field to use when ordering the results. */
        ordering?: string
        periods?: string
        production_sites?: string
        scores?: string
        /** @description A search term. */
        search?: string
        selection?: string
        /** @description * `DRAFTS` - DRAFTS
         *     * `IN` - IN
         *     * `OUT` - OUT
         *     * `DECLARATION` - DECLARATION
         *     * `ALERTS` - ALERTS
         *     * `LOTS` - LOTS */
        status?: PathsApiTransactionsLotsGetParametersQueryStatus
        suppliers?: string
        year?: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody: {
      content: {
        "application/json": components["schemas"]["Send"]
        "application/x-www-form-urlencoded": components["schemas"]["Send"]
        "multipart/form-data": components["schemas"]["Send"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["SendResponse"]
        }
      }
    }
  }
  transactions_lots_submit_fix_create: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody: {
      content: {
        "application/json": components["schemas"]["SubmitFix"]
        "application/x-www-form-urlencoded": components["schemas"]["SubmitFix"]
        "multipart/form-data": components["schemas"]["SubmitFix"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["CarbureLotPublic"]
        }
      }
    }
  }
  transactions_lots_summary_retrieve: {
    parameters: {
      query: {
        added_by?: string
        biofuels?: string
        category?: string
        clients?: string
        conformity?: string
        correction_status?: string
        countries_of_origin?: string
        deadline?: boolean
        delivery_sites?: string
        delivery_types?: string
        /** @description Entity ID */
        entity_id: number
        errors?: string
        feedstocks?: string
        invalid?: boolean
        lot_status?: string
        ml_scoring?: string
        /** @description Which field to use when ordering the results. */
        ordering?: string
        periods?: string
        production_sites?: string
        scores?: string
        /** @description A search term. */
        search?: string
        selection?: string
        /** @description * `DRAFTS` - DRAFTS
         *     * `IN` - IN
         *     * `OUT` - OUT
         *     * `DECLARATION` - DECLARATION
         *     * `ALERTS` - ALERTS
         *     * `LOTS` - LOTS */
        status?: PathsApiTransactionsLotsGetParametersQueryStatus
        suppliers?: string
        year?: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody?: never
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["SummaryResponse"]
        }
      }
    }
  }
  transactions_lots_template_retrieve: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody?: never
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/vnd.ms-excel": string
        }
      }
    }
  }
  transactions_lots_toggle_pin_create: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody: {
      content: {
        "application/json": components["schemas"]["TogglePin"]
        "application/x-www-form-urlencoded": components["schemas"]["TogglePin"]
        "multipart/form-data": components["schemas"]["TogglePin"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["CarbureLotPublic"]
        }
      }
    }
  }
  transactions_lots_update_many_create: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody: {
      content: {
        "application/json": components["schemas"]["UpdateMany"]
        "application/x-www-form-urlencoded": components["schemas"]["UpdateMany"]
        "multipart/form-data": components["schemas"]["UpdateMany"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["CarbureLotPublic"]
        }
      }
    }
  }
  transactions_snapshot_retrieve: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody?: never
    responses: {
      /** @description Response regular user or admin or auditor user */
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["Response200"]
        }
      }
    }
  }
  transactions_stocks_list: {
    parameters: {
      query: {
        biofuels?: string
        blacklist?: string
        clients?: string
        countries_of_origin?: string
        depots?: string
        /** @description Entity ID */
        entity_id: number
        feedstocks?: string
        /** @description Which field to use when ordering the results. */
        ordering?: string
        /** @description A page number within the paginated result set. */
        page?: number
        /** @description Number of results to return per page. */
        page_size?: number
        periods?: string
        production_sites?: string
        query?: string
        /** @description A search term. */
        search?: string
        selection?: string[]
        suppliers?: string
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody?: never
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["PaginatedCarbureStockPublicList"]
        }
      }
    }
  }
  transactions_stocks_retrieve: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path: {
        /** @description A unique integer value identifying this CarbureStock. */
        id: number
      }
      cookie?: never
    }
    requestBody?: never
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["StockDetailsResponse"]
        }
      }
    }
  }
  transactions_stocks_cancel_transformation_create: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody: {
      content: {
        "application/json": components["schemas"]["StockCancelTransformation"]
        "application/x-www-form-urlencoded": components["schemas"]["StockCancelTransformation"]
        "multipart/form-data": components["schemas"]["StockCancelTransformation"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["CarbureStockPublic"]
        }
      }
    }
  }
  transactions_stocks_filters_retrieve: {
    parameters: {
      query: {
        biofuels?: string
        blacklist?: string
        clients?: string
        countries_of_origin?: string
        depots?: string
        /** @description Entity ID */
        entity_id: number
        feedstocks?: string
        /** @description Which field to use when ordering the results. */
        ordering?: string
        periods?: string
        production_sites?: string
        query?: string
        /** @description A search term. */
        search?: string
        selection?: string[]
        suppliers?: string
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody?: never
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["CarbureStockPublic"]
        }
      }
    }
  }
  transactions_stocks_flush_create: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody: {
      content: {
        "application/json": components["schemas"]["StockFlush"]
        "application/x-www-form-urlencoded": components["schemas"]["StockFlush"]
        "multipart/form-data": components["schemas"]["StockFlush"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["StockFlush"]
        }
      }
    }
  }
  transactions_stocks_split_create: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody: {
      content: {
        "application/json": components["schemas"]["Split"]
        "application/x-www-form-urlencoded": components["schemas"]["Split"]
        "multipart/form-data": components["schemas"]["Split"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["SplitResponse"]
        }
      }
    }
  }
  transactions_stocks_summary_retrieve: {
    parameters: {
      query: {
        biofuels?: string
        blacklist?: string
        clients?: string
        countries_of_origin?: string
        depots?: string
        /** @description Entity ID */
        entity_id: number
        feedstocks?: string
        /** @description Which field to use when ordering the results. */
        ordering?: string
        periods?: string
        production_sites?: string
        query?: string
        /** @description A search term. */
        search?: string
        selection?: string[]
        suppliers?: string
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody?: never
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["StocksSummaryResponse"]
        }
      }
    }
  }
  transactions_stocks_template_retrieve: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody?: never
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/vnd.ms-excel": string
        }
      }
    }
  }
  transactions_stocks_transform_create: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody: {
      content: {
        "application/json": components["schemas"]["Transform"]
        "application/x-www-form-urlencoded": components["schemas"]["Transform"]
        "multipart/form-data": components["schemas"]["Transform"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["CarbureStockPublic"]
        }
      }
    }
  }
  transactions_years_retrieve: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody?: never
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["Years"]
        }
      }
    }
  }
}
export enum PathsApiSafTicketSourcesGetParametersQueryOrder {
  ValueMinusfeedstock = "-feedstock",
  ValueMinusghg_reduction = "-ghg_reduction",
  ValueMinusperiod = "-period",
  ValueMinusvolume = "-volume",
  feedstock = "feedstock",
  ghg_reduction = "ghg_reduction",
  period = "period",
  volume = "volume",
}
export enum PathsApiSafTicketsGetParametersQueryOrder {
  ValueMinusclient = "-client",
  ValueMinuscreated_at = "-created_at",
  ValueMinusfeedstock = "-feedstock",
  ValueMinusghg_reduction = "-ghg_reduction",
  ValueMinusperiod = "-period",
  ValueMinussuppliers = "-suppliers",
  ValueMinusvolume = "-volume",
  client = "client",
  created_at = "created_at",
  feedstock = "feedstock",
  ghg_reduction = "ghg_reduction",
  period = "period",
  suppliers = "suppliers",
  volume = "volume",
}
export enum PathsApiTransactionsLotsGetParametersQueryStatus {
  ALERTS = "ALERTS",
  DECLARATION = "DECLARATION",
  DRAFTS = "DRAFTS",
  IN = "IN",
  LOTS = "LOTS",
  OUT = "OUT",
}
export enum CategoryEnum {
  CONV = "CONV",
  ANN_IX_A = "ANN-IX-A",
  ANN_IX_B = "ANN-IX-B",
  TALLOL = "TALLOL",
  OTHER = "OTHER",
}
export enum CommentTypeEnum {
  REGULAR = "REGULAR",
  AUDITOR = "AUDITOR",
  ADMIN = "ADMIN",
}
export enum CorrectionStatusEnum {
  NO_PROBLEMO = "NO_PROBLEMO",
  IN_CORRECTION = "IN_CORRECTION",
  FIXED = "FIXED",
}
export enum DeliveryTypeEnum {
  UNKNOWN = "UNKNOWN",
  RFC = "RFC",
  STOCK = "STOCK",
  BLENDING = "BLENDING",
  EXPORT = "EXPORT",
  TRADING = "TRADING",
  PROCESSING = "PROCESSING",
  DIRECT = "DIRECT",
  FLUSHED = "FLUSHED",
  CONSUMPTION = "CONSUMPTION",
}
export enum EntityTypeEnum {
  Producer = "Producteur",
  Operator = "Op\u00E9rateur",
  Administration = "Administration",
  Trader = "Trader",
  Auditor = "Auditor",
  ExternalAdmin = "Administration Externe",
  CPO = "Charge Point Operator",
  Airline = "Compagnie a\u00E9rienne",
  Unknown = "Unknown",
  PowerOrHeatProducer = "Power or Heat Producer",
}
export enum EventTypeEnum {
  CREATED = "CREATED",
  UPDATED = "UPDATED",
  VALIDATED = "VALIDATED",
  FIX_REQUESTED = "FIX_REQUESTED",
  MARKED_AS_FIXED = "MARKED_AS_FIXED",
  FIX_ACCEPTED = "FIX_ACCEPTED",
  ACCEPTED = "ACCEPTED",
  REJECTED = "REJECTED",
  RECALLED = "RECALLED",
  DECLARED = "DECLARED",
  DELETED = "DELETED",
  DECLCANCEL = "DECLCANCEL",
  RESTORED = "RESTORED",
  CANCELLED = "CANCELLED",
  UPDATED_BY_ADMIN = "UPDATED_BY_ADMIN",
  DELETED_BY_ADMIN = "DELETED_BY_ADMIN",
}
export enum GesOptionEnum {
  Default = "Default",
  Actual = "Actual",
  NUTS2 = "NUTS2",
}
export enum LotStatusEnum {
  DRAFT = "DRAFT",
  PENDING = "PENDING",
  ACCEPTED = "ACCEPTED",
  REJECTED = "REJECTED",
  FROZEN = "FROZEN",
  DELETED = "DELETED",
}
export enum PreferredUnitEnum {
  l = "l",
  kg = "kg",
  MJ = "MJ",
}
export enum SiteTypeEnum {
  OTHER = "OTHER",
  EFS = "EFS",
  EFPE = "EFPE",
  OIL_DEPOT = "OIL DEPOT",
  BIOFUEL_DEPOT = "BIOFUEL DEPOT",
  HEAT_PLANT = "HEAT PLANT",
  POWER_PLANT = "POWER PLANT",
  COGENERATION_PLANT = "COGENERATION PLANT",
  PRODUCTION_SITE = "PRODUCTION SITE",
  EFCA = "EFCA",
}
export enum StatusEnum {
  PENDING = "PENDING",
  ACCEPTED = "ACCEPTED",
  REJECTED = "REJECTED",
}
export enum TransformationTypeEnum {
  UNKNOWN = "UNKNOWN",
  ETH_ETBE = "ETH_ETBE",
}
export enum TransportDocumentTypeEnum {
  DAU = "DAU",
  DAE = "DAE",
  DSA = "DSA",
  DSAC = "DSAC",
  DSP = "DSP",
  OTHER = "OTHER",
}
export enum UnitEnum {
  l = "l",
  kg = "kg",
  mj = "mj",
}
