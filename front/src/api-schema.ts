export interface paths {
  "/api/auth/activate/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["auth_activate_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/auth/login/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["auth_login_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/auth/logout/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["auth_logout_retrieve"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/auth/register/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["auth_register_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/auth/request-activation-link/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["auth_request_activation_link_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/auth/request-otp/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["auth_request_otp_retrieve"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/auth/request-password-reset/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["auth_request_password_reset_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/auth/reset-password/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["auth_reset_password_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/auth/verify-otp/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["auth_verify_otp_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/double-counting/agreements/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["double_counting_agreements_list"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/double-counting/agreements/{id}/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["double_counting_agreements_retrieve"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/double-counting/agreements/agreement-admin/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["double_counting_agreements_agreement_admin_retrieve"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/double-counting/agreements/agreement-public/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["double_counting_agreements_agreement_public_list"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/double-counting/agreements/export/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["double_counting_agreements_export_retrieve"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/double-counting/applications/{id}/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["double_counting_applications_retrieve"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/double-counting/applications/{id}/export/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["double_counting_applications_export_retrieve"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/double-counting/applications/{id}/update-approved-quotas/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["double_counting_applications_update_approved_quotas_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/double-counting/applications/add/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["double_counting_applications_add_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/double-counting/applications/approve/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["double_counting_applications_approve_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/double-counting/applications/check-admin-files/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["double_counting_applications_check_admin_files_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/double-counting/applications/check-file/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["double_counting_applications_check_file_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/double-counting/applications/export-application/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["double_counting_applications_export_application_retrieve"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/double-counting/applications/list-admin/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["double_counting_applications_list_admin_retrieve"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/double-counting/applications/reject/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["double_counting_applications_reject_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/double-counting/snapshot/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["double_counting_snapshot_retrieve"]
    put?: never
    post?: never
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
  "/api/resources/airports": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["resources_airports_list"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/resources/biofuels": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["resources_biofuels_list"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/resources/certificates": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["resources_certificates_list"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/resources/countries": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["resources_countries_list"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/resources/depots": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["resources_depots_list"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/resources/entities": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["resources_entities_list"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/resources/feedstocks": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["resources_feedstocks_list"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/resources/production-sites": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["resources_production_sites_list"]
    put?: never
    post?: never
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
  "/api/user/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get: operations["user_retrieve"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/user/request-access": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["user_request_access_create"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/api/user/revoke-access": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    post: operations["user_revoke_access_create"]
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
    AcceptRequest: {
      ets_status: components["schemas"]["EtsStatusEnum"]
      /** Format: date */
      ets_declaration_date?: string
    }
    ActivateAccountRequest: {
      uidb64: string
      token: string
      invite?: number
    }
    ActivateResponse: {
      message: string
      token?: string
    }
    AgreementLists: {
      active: components["schemas"]["DoubleCountingRegistration"][]
      incoming: components["schemas"]["DoubleCountingRegistration"][]
      expired: components["schemas"]["DoubleCountingRegistration"][]
    }
    Airport: {
      readonly id: number
      name: string
      city?: string
      icao_code?: string
      readonly country: components["schemas"]["Country"]
      site_type?: components["schemas"]["SiteTypeEnum"]
      address?: string
      postal_code?: string
      gps_coordinates?: string | null
    }
    ApplicationListe: {
      rejected: components["schemas"]["DoubleCountingApplicationPartial"][]
      pending: components["schemas"]["DoubleCountingApplicationPartial"][]
    }
    ApplicationSnapshot: {
      applications_pending: number
      applications_rejected: number
      agreements_incoming: number
      agreements_active: number
      agreements_expired: number
    }
    ApprouveDoubleCountingRequest: {
      dca_id: number
    }
    Biofuel: {
      name: string
      name_en: string
      code: string
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
    /**
     * @description * `CONV` - Conventionnel
     *     * `ANN-IX-A` - ANNEXE IX-A
     *     * `ANN-IX-B` - ANNEXE IX-B
     *     * `TALLOL` - Tallol
     *     * `OTHER` - Autre
     * @enum {string}
     */
    CategoryEnum: CategoryEnum
    /**
     * @description * `SYSTEME_NATIONAL` - SYSTEME_NATIONAL
     *     * `ISCC` - ISCC
     *     * `REDCERT` - REDCERT
     *     * `2BS` - 2BS
     * @enum {string}
     */
    CertificateTypeEnum: CertificateTypeEnum
    CheckAdminFileRequest: {
      files: File[]
    }
    CheckFileResponse: {
      file: components["schemas"]["File"]
      /** Format: date-time */
      checked_at: string
    }
    CommentRequest: {
      comment?: string
    }
    /**
     * @description * `MAC` - MAC
     *     * `MAC_DECLASSEMENT` - MAC_DECLASSEMENT
     * @enum {string}
     */
    ConsumptionTypeEnum: ConsumptionTypeEnum
    /**
     * @description * `NO_PROBLEMO` - NO_PROBLEMO
     *     * `IN_CORRECTION` - IN_CORRECTION
     *     * `FIXED` - FIXED
     * @enum {string}
     */
    CorrectionStatusEnum: CorrectionStatusEnum
    Country: {
      name: string
      name_en: string
      code_pays: string
      is_in_europe?: boolean
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
      /**
       * Format: double
       * @description Entre 0 et 1
       */
      electrical_efficiency?: number | null
      /**
       * Format: double
       * @description Entre 0 et 1
       */
      thermal_efficiency?: number | null
      /**
       * Format: double
       * @description En degrés Celsius
       */
      useful_temperature?: number | null
    }
    DoubleCountingAdminAddRequest: {
      certificate_id?: string
      entity_id: number
      producer_id: number
      production_site_id: number
      /** @default false */
      should_replace: boolean
      /** Format: binary */
      file: File
    }
    /**
     * @description * `ACTIVE` - ACTIVE
     *     * `EXPIRED` - EXPIRED
     *     * `EXPIRES_SOON` - EXPIRES_SOON
     *     * `INCOMING` - INCOMING
     * @enum {string}
     */
    DoubleCountingAgreementStatus: DoubleCountingAgreementStatus
    DoubleCountingApplication: {
      readonly id: number
      /** Format: date-time */
      readonly created_at: string
      readonly producer: components["schemas"]["Entity"]
      /**
       * Adresse électronique
       * Format: email
       */
      readonly producer_user: string
      readonly production_site: components["schemas"]["DoubleCountingProductionSite"]
      /** Format: date */
      period_start: string
      /** Format: date */
      period_end: string
      status?: components["schemas"]["DoubleCountingStatus"]
      readonly sourcing: components["schemas"]["DoubleCountingSourcing"][]
      readonly production: components["schemas"]["DoubleCountingProduction"][]
      readonly documents: components["schemas"]["DoubleCountingDocFile"][]
    }
    DoubleCountingApplicationPartial: {
      readonly id: number
      /** Format: date-time */
      readonly created_at: string
      readonly producer: components["schemas"]["EntitySummary"]
      readonly production_site: components["schemas"]["DoubleCountingProductionSite"]
      /** Format: date */
      period_start: string
      /** Format: date */
      period_end: string
      readonly status: components["schemas"]["DoubleCountingStatus"]
      certificate_id: string
      readonly agreement_id: number
      /** Format: double */
      readonly quotas_progression: number
      /**
       * Adresse électronique
       * Format: email
       */
      readonly producer_user: string
    }
    DoubleCountingDocFile: {
      readonly id: number
      file_name?: string
      file_type?: components["schemas"]["FileTypeEnum"]
    }
    DoubleCountingProduction: {
      readonly id: number
      readonly year: number
      readonly biofuel: components["schemas"]["Biofuel"]
      readonly feedstock: components["schemas"]["FeedStock"]
      readonly max_production_capacity: number
      readonly estimated_production: number
      readonly requested_quota: number
      readonly approved_quota: number
    }
    DoubleCountingProductionHistory: {
      readonly id: number
      readonly year: number
      readonly biofuel: components["schemas"]["Biofuel"]
      readonly feedstock: components["schemas"]["FeedStock"]
      readonly max_production_capacity: number
      readonly effective_production: number
    }
    DoubleCountingProductionSite: {
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
      readonly inputs: components["schemas"]["FeedStock"][]
      readonly outputs: components["schemas"]["Biofuel"][]
      readonly certificates: components["schemas"]["ProductionSiteCertificate"][]
    }
    DoubleCountingQuota: {
      approved_quota: number
      biofuel: components["schemas"]["Biofuel"]
      feedstock: components["schemas"]["FeedStock"]
      id: number
      lot_count: number
      production_tonnes: number
      quotas_progression: number
      requested_quota: number
      year: number
    }
    DoubleCountingRegistration: {
      readonly id: number
      certificate_id: string
      /** Format: date */
      valid_from: string
      readonly producer: components["schemas"]["EntitySummary"]
      production_site: components["schemas"]["DoubleCountingProductionSite"]
      /** Format: date */
      valid_until: string
      readonly status: components["schemas"]["DoubleCountingAgreementStatus"]
      /** Format: double */
      readonly quotas_progression: number
    }
    DoubleCountingRegistrationDetails: {
      readonly id: number
      certificate_id: string
      /** Format: date */
      valid_from: string
      /** Format: date */
      valid_until: string
      readonly status: components["schemas"]["DoubleCountingAgreementStatus"]
      readonly producer: string
      readonly production_site: string
      application: components["schemas"]["DoubleCountingApplication"]
      readonly quotas: components["schemas"]["DoubleCountingQuota"][]
    }
    DoubleCountingRegistrationPublic: {
      readonly production_site: components["schemas"]["FieldData"]
      certificate_id: string
      /** Format: date */
      valid_from: string
      /** Format: date */
      valid_until: string
      readonly biofuel_list: string
    }
    DoubleCountingSourcing: {
      readonly id: number
      readonly year: number
      readonly feedstock: components["schemas"]["FeedStock"]
      readonly origin_country: components["schemas"]["Country"]
      readonly supply_country: components["schemas"]["Country"]
      readonly transit_country: components["schemas"]["Country"]
      readonly metric_tonnes: number
    }
    DoubleCountingSourcingHistory: {
      readonly id: number
      year: number
      readonly feedstock: components["schemas"]["FeedStock"]
      readonly origin_country: components["schemas"]["Country"]
      readonly supply_country: components["schemas"]["Country"]
      readonly transit_country: components["schemas"]["Country"]
      metric_tonnes: number
      raw_material_supplier?: string
      supplier_certificate_name?: string
      supplier_certificate?: number | null
    }
    /**
     * @description * `PENDING` - PENDING
     *     * `INPROGRESS` - INPROGRESS
     *     * `REJECTED` - REJECTED
     *     * `ACCEPTED` - ACCEPTED
     * @enum {string}
     */
    DoubleCountingStatus: DoubleCountingStatus
    EmptyResponse: {
      empty?: string
    }
    EmptyResponseRequest: {
      empty?: string
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
      readonly name: string
      readonly entity_type: components["schemas"]["EntityTypeEnum"]
    }
    EntitySummary: {
      readonly id: number
      readonly name: string
      readonly entity_type: components["schemas"]["EntityTypeEnum"]
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
     * @description * `ETS_VALUATION` - Valorisation ETS
     *     * `OUTSIDE_ETS` - Hors ETS (schéma volontaire)
     *     * `NOT_CONCERNED` - Non concerné
     * @enum {string}
     */
    EtsStatusEnum: EtsStatusEnum
    /**
     * @description * `DCA` - DCA
     *     * `AGRIMER` - AGRIMER
     *     * `TIRIB` - TIRIB
     *     * `AIRLINE` - AIRLINE
     *     * `ELEC` - ELEC
     * @enum {string}
     */
    ExtAdminPagesEnum: ExtAdminPagesEnum
    FeedStock: {
      name: string
      name_en: string
      code: string
      category?: components["schemas"]["CategoryEnum"]
      is_double_compte?: boolean
    }
    FieldData: {
      name: string
      city: string
      address: string
      postal_code: string
      country: string
    }
    File: {
      file_name: string
      errors: components["schemas"]["FileErrors"]
      error_count: number
      start_year: number
      production_site: string
      /** Format: email */
      producer_email: string
      production: components["schemas"]["DoubleCountingProduction"][]
      sourcing: components["schemas"]["DoubleCountingSourcing"][]
      sourcing_history: components["schemas"]["DoubleCountingSourcingHistory"][]
      production_history: components["schemas"]["DoubleCountingProductionHistory"][]
      readonly has_dechets_industriels: boolean
    }
    FileError: {
      error: string
      is_blocking: boolean
      line_number: number
      line_merged: string
      meta: {
        [key: string]: unknown
      }
    }
    FileErrors: {
      sourcing_forecast: components["schemas"]["FileError"][]
      sourcing_history: components["schemas"]["FileError"][]
      production: components["schemas"]["FileError"][]
      production_history: components["schemas"]["FileError"][]
      global_errors: components["schemas"]["FileError"][]
    }
    /**
     * @description * `SOURCING` - SOURCING
     *     * `DECISION` - DECISION
     * @enum {string}
     */
    FileTypeEnum: FileTypeEnum
    GenericCertificate: {
      certificate_id: string
      certificate_type: components["schemas"]["CertificateTypeEnum"]
      certificate_holder: string
      certificate_issuer?: string | null
      address?: string | null
      /** Format: date */
      valid_from: string
      /** Format: date */
      valid_until: string
      download_link?: string | null
      scope?: unknown
      input?: unknown
      output?: unknown
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
    OtpResponse: {
      valid_until: string
    }
    PaginatedEntityPreviewList: {
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
      results: components["schemas"]["EntityPreview"][]
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
    ProductionSiteCertificate: {
      certificate_id: string
      certificate_type: components["schemas"]["CertificateTypeEnum"]
      certificate_holder: string
      certificate_issuer?: string | null
      address?: string | null
      /** Format: date */
      valid_from: string
      /** Format: date */
      valid_until: string
      download_link?: string | null
      scope?: unknown
      input?: unknown
      output?: unknown
    }
    RejectDoubleCountingRequest: {
      dca_id: number
    }
    RequestAccessRequest: {
      comment?: string
      role: string
      entity_id: number
    }
    RequestPasswordResetRequest: {
      username: string
    }
    ResetPasswordRequest: {
      uidb64: string
      token: string
      /** Mot de passe */
      password1: string
      /** Confirmation du mot de passe */
      password2: string
    }
    Response: {
      status: string
    }
    ResponseSuccess: {
      status: string
    }
    RevokeAccessRequest: {
      entity_id: number
    }
    /**
     * @description * `RO` - Lecture Seule
     *     * `RW` - Lecture/Écriture
     *     * `ADMIN` - Administrateur
     *     * `AUDITOR` - Auditeur
     * @enum {string}
     */
    RoleEnum: RoleEnum
    SafTicket: {
      readonly id: number
      carbure_id?: string | null
      year: number
      assignment_period: number
      status?: components["schemas"]["saf.filters.TicketFilter.status"]
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
      ets_status?: components["schemas"]["EtsStatusEnum"] | null
    }
    SafTicketDetails: {
      readonly id: number
      carbure_id?: string | null
      year: number
      assignment_period: number
      status?: components["schemas"]["saf.filters.TicketFilter.status"]
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
      shipping_method?: components["schemas"]["ShippingMethodEnum"] | null
      readonly reception_airport: components["schemas"]["Airport"]
      consumption_type?: components["schemas"]["ConsumptionTypeEnum"] | null
      ets_status?: components["schemas"]["EtsStatusEnum"] | null
      /** Format: date */
      ets_declaration_date?: string | null
    }
    SafTicketPreview: {
      readonly id: number
      carbure_id?: string | null
      readonly client: string
      /** Format: date */
      agreement_date?: string | null
      /** Format: double */
      volume: number
      status?: components["schemas"]["saf.filters.TicketFilter.status"]
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
      reception_airport?: number | null
      consumption_type?: string | null
      shipping_method?: string | null
    }
    SafTicketSourceAssignmentRequest: {
      client_id: number
      /** Format: double */
      volume: number
      agreement_reference?: string
      agreement_date?: string
      free_field?: string | null
      assignment_period: number
      reception_airport?: number | null
      consumption_type?: string | null
      shipping_method?: string | null
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
    SafTicketSourceGroupAssignmentRequest: {
      client_id: number
      /** Format: double */
      volume: number
      agreement_reference?: string
      agreement_date?: string
      free_field?: string | null
      assignment_period: number
      reception_airport?: number | null
      consumption_type?: string | null
      shipping_method?: string | null
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
    /**
     * @description * `PIPELINE` - PIPELINE
     *     * `TRUCK` - TRUCK
     *     * `TRAIN` - TRAIN
     *     * `BARGE` - BARGE
     * @enum {string}
     */
    ShippingMethodEnum: ShippingMethodEnum
    /**
     * @description * `OTHER` - Autre
     *     * `EFS` - EFS
     *     * `EFPE` - EFPE
     *     * `OIL DEPOT` - OIL DEPOT
     *     * `BIOFUEL DEPOT` - BIOFUEL DEPOT
     *     * `HEAT PLANT` - HEAT PLANT
     *     * `POWER PLANT` - POWER PLANT
     *     * `COGENERATION PLANT` - COGENERATION PLANT
     *     * `PRODUCTION BIOLIQUID` - PRODUCTION BIOLIQUID
     *     * `EFCA` - EFCA
     *     * `AIRPORT` - AIRPORT
     * @enum {string}
     */
    SiteTypeEnum: SiteTypeEnum
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
    UpdatedQuotasRequest: {
      approved_quotas: number[][]
    }
    /** @description Serializer for creating new users. Includes required fields
     *     and repeated password validation. */
    UserCreation: {
      /**
       * Adresse électronique
       * Format: email
       */
      email: string
      /** Nom */
      name: string
    }
    /** @description Serializer for creating new users. Includes required fields
     *     and repeated password validation. */
    UserCreationRequest: {
      /**
       * Adresse électronique
       * Format: email
       */
      email: string
      /** Nom */
      name: string
      /** Mot de passe */
      password1: string
      /** Confirmation du mot de passe */
      password2: string
    }
    UserEntity: {
      readonly id: number
      readonly name: string
      readonly is_enabled: boolean
      readonly entity_type: components["schemas"]["EntityTypeEnum"]
      readonly has_mac: boolean
      readonly has_trading: boolean
      readonly has_direct_deliveries: boolean
      readonly has_stocks: boolean
      readonly legal_name: string
      readonly registration_id: string
      readonly sustainability_officer: string
      readonly sustainability_officer_phone_number: string
      readonly sustainability_officer_email: string
      readonly registered_address: string
      readonly registered_zipcode: string
      readonly registered_city: string
      registered_country?: components["schemas"]["Country"]
      readonly default_certificate: string | null
      readonly preferred_unit: components["schemas"]["PreferredUnitEnum"]
      readonly has_saf: boolean
      readonly has_elec: boolean
      readonly activity_description: string
      /** Format: uri */
      readonly website: string
      readonly vat_number: string
      readonly ext_admin_pages: components["schemas"]["ExtAdminPagesEnum"][]
    }
    UserLoginRequest: {
      username: string
      password: string
    }
    /** @description A serializer for re-sending the user activation email. Includes email field only. */
    UserResendActivationLinkRequest: {
      /**
       * Courriel
       * Format: email
       */
      email: string
    }
    UserRights: {
      readonly name: string
      /** Format: email */
      readonly email: string
      entity: components["schemas"]["UserEntity"]
      readonly role: components["schemas"]["RoleEnum"]
      /** Format: date-time */
      expiration_date?: string | null
    }
    UserRightsRequests: {
      readonly id: number
      readonly user: string[]
      entity: components["schemas"]["UserEntity"]
      /** Format: date-time */
      readonly date_requested: string
      readonly status: components["schemas"]["UserRightsRequestsStatusEnum"]
      comment?: string | null
      readonly role: components["schemas"]["RoleEnum"]
      /** Format: date-time */
      expiration_date?: string | null
    }
    /**
     * @description * `PENDING` - En attente de validation
     *     * `ACCEPTED` - Accepté
     *     * `REJECTED` - Refusé
     *     * `REVOKED` - Révoqué
     * @enum {string}
     */
    UserRightsRequestsStatusEnum: UserRightsRequestsStatusEnum
    UserSettingsResponseSeriaizer: {
      /** Format: email */
      email: string
      rights: components["schemas"]["UserRights"][]
      requests: components["schemas"]["UserRightsRequests"][]
    }
    /** @description A serializer for submitting the OTP sent via email. Includes otp_token field only. */
    VerifyOTPRequest: {
      /** Entrez le code à 6 chiffres reçu par email */
      otp_token: string
    }
    /**
     * @description * `PENDING` - En attente
     *     * `ACCEPTED` - Accepté
     *     * `REJECTED` - Refusé
     * @enum {string}
     */
    "saf.filters.TicketFilter.status": PathsApiSafTicketsGetParametersQueryStatus
  }
  responses: never
  parameters: never
  requestBodies: never
  headers: never
  pathItems: never
}
export type $defs = Record<string, never>
export interface operations {
  auth_activate_create: {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    requestBody: {
      content: {
        "application/json": components["schemas"]["ActivateAccountRequest"]
        "application/x-www-form-urlencoded": components["schemas"]["ActivateAccountRequest"]
        "multipart/form-data": components["schemas"]["ActivateAccountRequest"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["ActivateResponse"]
        }
      }
      /** @description Bad request - missing fields. */
      400: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": unknown
        }
      }
    }
  }
  auth_login_create: {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    requestBody: {
      content: {
        "application/json": components["schemas"]["UserLoginRequest"]
        "application/x-www-form-urlencoded": components["schemas"]["UserLoginRequest"]
        "multipart/form-data": components["schemas"]["UserLoginRequest"]
      }
    }
    responses: {
      /** @description Request successful. */
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": unknown
        }
      }
      /** @description Bad request - missing fields. */
      400: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": unknown
        }
      }
    }
  }
  auth_logout_retrieve: {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    requestBody?: never
    responses: {
      /** @description Request successful. */
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": unknown
        }
      }
    }
  }
  auth_register_create: {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    requestBody: {
      content: {
        "application/json": components["schemas"]["UserCreationRequest"]
        "application/x-www-form-urlencoded": components["schemas"]["UserCreationRequest"]
        "multipart/form-data": components["schemas"]["UserCreationRequest"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["UserCreation"]
        }
      }
    }
  }
  auth_request_activation_link_create: {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    requestBody: {
      content: {
        "application/json": components["schemas"]["UserResendActivationLinkRequest"]
        "application/x-www-form-urlencoded": components["schemas"]["UserResendActivationLinkRequest"]
        "multipart/form-data": components["schemas"]["UserResendActivationLinkRequest"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["UserCreation"]
        }
      }
    }
  }
  auth_request_otp_retrieve: {
    parameters: {
      query?: never
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
          "application/json": components["schemas"]["OtpResponse"]
        }
      }
    }
  }
  auth_request_password_reset_create: {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    requestBody: {
      content: {
        "application/json": components["schemas"]["RequestPasswordResetRequest"]
        "application/x-www-form-urlencoded": components["schemas"]["RequestPasswordResetRequest"]
        "multipart/form-data": components["schemas"]["RequestPasswordResetRequest"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["UserCreation"]
        }
      }
    }
  }
  auth_reset_password_create: {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    requestBody: {
      content: {
        "application/json": components["schemas"]["ResetPasswordRequest"]
        "application/x-www-form-urlencoded": components["schemas"]["ResetPasswordRequest"]
        "multipart/form-data": components["schemas"]["ResetPasswordRequest"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["UserCreation"]
        }
      }
    }
  }
  auth_verify_otp_create: {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    requestBody: {
      content: {
        "application/json": components["schemas"]["VerifyOTPRequest"]
        "application/x-www-form-urlencoded": components["schemas"]["VerifyOTPRequest"]
        "multipart/form-data": components["schemas"]["VerifyOTPRequest"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["UserCreation"]
        }
      }
    }
  }
  double_counting_agreements_list: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
        /** @description Tri
         *
         *     * `production_site` - Production site
         *     * `-production_site` - Production site (décroissant)
         *     * `valid_until` - Valid until
         *     * `-valid_until` - Valid until (décroissant) */
        order_by?: PathsApiDoubleCountingAgreementsGetParametersQueryOrder_by[]
        /** @description Which field to use when ordering the results. */
        ordering?: string
        /** @description A search term. */
        search?: string
        /** @description Year */
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
          "application/json": components["schemas"]["DoubleCountingApplicationPartial"][]
        }
      }
    }
  }
  double_counting_agreements_retrieve: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path: {
        /** @description A unique integer value identifying this Certificat Double Compte. */
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
          "application/json": components["schemas"]["DoubleCountingRegistrationDetails"]
        }
      }
    }
  }
  double_counting_agreements_agreement_admin_retrieve: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
        /** @description Tri
         *
         *     * `production_site` - Production site
         *     * `-production_site` - Production site (décroissant)
         *     * `valid_until` - Valid until
         *     * `-valid_until` - Valid until (décroissant) */
        order_by?: PathsApiDoubleCountingAgreementsGetParametersQueryOrder_by[]
        /** @description Which field to use when ordering the results. */
        ordering?: string
        /** @description A search term. */
        search?: string
        /** @description Year */
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
          "application/json": components["schemas"]["AgreementLists"]
        }
      }
    }
  }
  double_counting_agreements_agreement_public_list: {
    parameters: {
      query?: {
        /** @description Tri
         *
         *     * `production_site` - Production site
         *     * `-production_site` - Production site (décroissant)
         *     * `valid_until` - Valid until
         *     * `-valid_until` - Valid until (décroissant) */
        order_by?: PathsApiDoubleCountingAgreementsGetParametersQueryOrder_by[]
        /** @description Which field to use when ordering the results. */
        ordering?: string
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
          "application/json": components["schemas"]["DoubleCountingRegistrationPublic"][]
        }
      }
    }
  }
  double_counting_agreements_export_retrieve: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
        /** @description Tri
         *
         *     * `production_site` - Production site
         *     * `-production_site` - Production site (décroissant)
         *     * `valid_until` - Valid until
         *     * `-valid_until` - Valid until (décroissant) */
        order_by?: PathsApiDoubleCountingAgreementsGetParametersQueryOrder_by[]
        /** @description Which field to use when ordering the results. */
        ordering?: string
        /** @description A search term. */
        search?: string
        /** @description Year */
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
          "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": string
        }
      }
    }
  }
  double_counting_applications_retrieve: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path: {
        /** @description A unique integer value identifying this Dossier Double Compte. */
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
          "application/json": components["schemas"]["DoubleCountingApplication"]
        }
      }
    }
  }
  double_counting_applications_export_retrieve: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path: {
        /** @description A unique integer value identifying this Dossier Double Compte. */
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
          "application/force-download": string
        }
      }
    }
  }
  double_counting_applications_update_approved_quotas_create: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
      }
      header?: never
      path: {
        /** @description A unique integer value identifying this Dossier Double Compte. */
        id: number
      }
      cookie?: never
    }
    requestBody: {
      content: {
        "application/json": components["schemas"]["UpdatedQuotasRequest"]
        "application/x-www-form-urlencoded": components["schemas"]["UpdatedQuotasRequest"]
        "multipart/form-data": components["schemas"]["UpdatedQuotasRequest"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["Response"]
        }
      }
    }
  }
  double_counting_applications_add_create: {
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
        "application/json": components["schemas"]["DoubleCountingAdminAddRequest"]
        "application/x-www-form-urlencoded": components["schemas"]["DoubleCountingAdminAddRequest"]
        "multipart/form-data": components["schemas"]["DoubleCountingAdminAddRequest"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["Response"]
        }
      }
    }
  }
  double_counting_applications_approve_create: {
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
        "application/json": components["schemas"]["ApprouveDoubleCountingRequest"]
        "application/x-www-form-urlencoded": components["schemas"]["ApprouveDoubleCountingRequest"]
        "multipart/form-data": components["schemas"]["ApprouveDoubleCountingRequest"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["Response"]
        }
      }
    }
  }
  double_counting_applications_check_admin_files_create: {
    parameters: {
      query: {
        /** @description Entity ID */
        entity_id: number
        /** @description Which field to use when ordering the results. */
        ordering?: string
        /** @description A search term. */
        search?: string
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody: {
      content: {
        "application/json": components["schemas"]["CheckAdminFileRequest"]
        "application/x-www-form-urlencoded": components["schemas"]["CheckAdminFileRequest"]
        "multipart/form-data": components["schemas"]["CheckAdminFileRequest"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["CheckFileResponse"][]
        }
      }
    }
  }
  double_counting_applications_check_file_create: {
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
        "multipart/form-data": {
          /** Format: binary */
          file?: File
        }
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["CheckFileResponse"]
        }
      }
    }
  }
  double_counting_applications_export_application_retrieve: {
    parameters: {
      query: {
        /** @description Doublecount application ID */
        dca_id: number
        /** @description Dechet industriel */
        di?: string
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
          "application/vnd.openxmlformats-officedocument.wordprocessingml.document": string
        }
      }
    }
  }
  double_counting_applications_list_admin_retrieve: {
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
          "application/json": components["schemas"]["ApplicationListe"]
        }
      }
    }
  }
  double_counting_applications_reject_create: {
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
        "application/json": components["schemas"]["RejectDoubleCountingRequest"]
        "application/x-www-form-urlencoded": components["schemas"]["RejectDoubleCountingRequest"]
        "multipart/form-data": components["schemas"]["RejectDoubleCountingRequest"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["Response"]
        }
      }
    }
  }
  double_counting_snapshot_retrieve: {
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
          "application/json": components["schemas"]["ApplicationSnapshot"]
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
    requestBody?: {
      content: {
        "application/json": components["schemas"]["EmptyResponseRequest"]
        "application/x-www-form-urlencoded": components["schemas"]["EmptyResponseRequest"]
        "multipart/form-data": components["schemas"]["EmptyResponseRequest"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["EmptyResponse"]
        }
      }
    }
  }
  resources_airports_list: {
    parameters: {
      query?: {
        /** @description Public Only */
        public_only?: boolean
        /** @description Search within the fields `name`, `icao_code` and `city` */
        query?: string
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
          "application/json": components["schemas"]["Airport"][]
        }
      }
    }
  }
  resources_biofuels_list: {
    parameters: {
      query?: {
        /** @description Search within the fields `name`, `name_en`, and `code` */
        query?: string
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
          "application/json": components["schemas"]["Biofuel"][]
        }
      }
    }
  }
  resources_certificates_list: {
    parameters: {
      query?: {
        /** @description Search within the fields `certificate_id` and `certificate_holder` */
        query?: string
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
          "application/json": components["schemas"]["GenericCertificate"][]
        }
      }
    }
  }
  resources_countries_list: {
    parameters: {
      query?: {
        /** @description Search within the fields `name`, `name_en` and `code_pays` */
        query?: string
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
          "application/json": components["schemas"]["Country"][]
        }
      }
    }
  }
  resources_depots_list: {
    parameters: {
      query?: {
        /** @description Public Only */
        public_only?: boolean
        /** @description Search within the fields `name`, `name_en` and `code_pays` */
        query?: string
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
          "application/json": components["schemas"]["Depot"][]
        }
      }
    }
  }
  resources_entities_list: {
    parameters: {
      query?: {
        /** @description Only keep specific entity types */
        entity_type?: string[]
        /** @description Only show enabled entities */
        is_enabled?: boolean
        /** @description Search within the field `name` */
        query?: string
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
          "application/json": components["schemas"]["EntityPreview"][]
        }
      }
    }
  }
  resources_feedstocks_list: {
    parameters: {
      query?: {
        /** @description Double compte only */
        double_count_only?: boolean
        /** @description Search within the fields `name`, `name_en` and `code` */
        query?: string
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
          "application/json": components["schemas"]["FeedStock"][]
        }
      }
    }
  }
  resources_production_sites_list: {
    parameters: {
      query?: {
        /** @description Search within the field `producer_id` */
        producer_id?: number
        /** @description Search within the field `name` */
        query?: string
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
          "application/json": components["schemas"]["ProductionSite"][]
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
          "application/json": components["schemas"]["PaginatedEntityPreviewList"]
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
          "application/json": components["schemas"]["EntityPreview"]
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
        /** @description Tri
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
        /** @description * `HISTORY` - HISTORY
         *     * `AVAILABLE` - AVAILABLE */
        status?: PathsApiSafTicketSourcesGetParametersQueryStatus
        /** @description Comma-separated list of supplier names */
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
        "application/json": components["schemas"]["SafTicketSourceAssignmentRequest"]
        "application/x-www-form-urlencoded": components["schemas"]["SafTicketSourceAssignmentRequest"]
        "multipart/form-data": components["schemas"]["SafTicketSourceAssignmentRequest"]
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
        /** @description Tri
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
        /** @description * `HISTORY` - HISTORY
         *     * `AVAILABLE` - AVAILABLE */
        status?: PathsApiSafTicketSourcesGetParametersQueryStatus
        /** @description Comma-separated list of supplier names */
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
        /** @description Tri
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
        /** @description * `HISTORY` - HISTORY
         *     * `AVAILABLE` - AVAILABLE */
        status?: PathsApiSafTicketSourcesGetParametersQueryStatus
        /** @description Comma-separated list of supplier names */
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
        "application/json": components["schemas"]["SafTicketSourceGroupAssignmentRequest"]
        "application/x-www-form-urlencoded": components["schemas"]["SafTicketSourceGroupAssignmentRequest"]
        "multipart/form-data": components["schemas"]["SafTicketSourceGroupAssignmentRequest"]
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
        /** @description Tri
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
        /** @description * `PENDING` - En attente
         *     * `ACCEPTED` - Accepté
         *     * `REJECTED` - Refusé */
        status?: PathsApiSafTicketsGetParametersQueryStatus
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
    requestBody: {
      content: {
        "application/json": components["schemas"]["AcceptRequest"]
        "application/x-www-form-urlencoded": components["schemas"]["AcceptRequest"]
        "multipart/form-data": components["schemas"]["AcceptRequest"]
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
        "application/json": components["schemas"]["CommentRequest"]
        "application/x-www-form-urlencoded": components["schemas"]["CommentRequest"]
        "multipart/form-data": components["schemas"]["CommentRequest"]
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
        "application/json": components["schemas"]["CommentRequest"]
        "application/x-www-form-urlencoded": components["schemas"]["CommentRequest"]
        "multipart/form-data": components["schemas"]["CommentRequest"]
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
        /** @description Tri
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
        /** @description * `PENDING` - En attente
         *     * `ACCEPTED` - Accepté
         *     * `REJECTED` - Refusé */
        status?: PathsApiSafTicketsGetParametersQueryStatus
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
        /** @description Tri
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
        /** @description * `PENDING` - En attente
         *     * `ACCEPTED` - Accepté
         *     * `REJECTED` - Refusé */
        status?: PathsApiSafTicketsGetParametersQueryStatus
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
  user_retrieve: {
    parameters: {
      query?: never
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
          "application/json": components["schemas"]["UserSettingsResponseSeriaizer"]
        }
      }
    }
  }
  user_request_access_create: {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    requestBody: {
      content: {
        "application/json": components["schemas"]["RequestAccessRequest"]
        "application/x-www-form-urlencoded": components["schemas"]["RequestAccessRequest"]
        "multipart/form-data": components["schemas"]["RequestAccessRequest"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["ResponseSuccess"]
        }
      }
    }
  }
  user_revoke_access_create: {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    requestBody: {
      content: {
        "application/json": components["schemas"]["RevokeAccessRequest"]
        "application/x-www-form-urlencoded": components["schemas"]["RevokeAccessRequest"]
        "multipart/form-data": components["schemas"]["RevokeAccessRequest"]
      }
    }
    responses: {
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["ResponseSuccess"]
        }
      }
    }
  }
}
export enum PathsApiDoubleCountingAgreementsGetParametersQueryOrder_by {
  ValueMinusproduction_site = "-production_site",
  ValueMinusvalid_until = "-valid_until",
  production_site = "production_site",
  valid_until = "valid_until",
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
export enum PathsApiSafTicketSourcesGetParametersQueryStatus {
  AVAILABLE = "AVAILABLE",
  HISTORY = "HISTORY",
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
export enum PathsApiSafTicketsGetParametersQueryStatus {
  ACCEPTED = "ACCEPTED",
  PENDING = "PENDING",
  REJECTED = "REJECTED",
}
export enum CategoryEnum {
  CONV = "CONV",
  ANN_IX_A = "ANN-IX-A",
  ANN_IX_B = "ANN-IX-B",
  TALLOL = "TALLOL",
  OTHER = "OTHER",
}
export enum CertificateTypeEnum {
  SYSTEME_NATIONAL = "SYSTEME_NATIONAL",
  ISCC = "ISCC",
  REDCERT = "REDCERT",
  Value2BS = "2BS",
}
export enum ConsumptionTypeEnum {
  MAC = "MAC",
  MAC_DECLASSEMENT = "MAC_DECLASSEMENT",
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
export enum DoubleCountingAgreementStatus {
  ACTIVE = "ACTIVE",
  EXPIRED = "EXPIRED",
  EXPIRES_SOON = "EXPIRES_SOON",
  INCOMING = "INCOMING",
}
export enum DoubleCountingStatus {
  PENDING = "PENDING",
  INPROGRESS = "INPROGRESS",
  REJECTED = "REJECTED",
  ACCEPTED = "ACCEPTED",
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
export enum EtsStatusEnum {
  ETS_VALUATION = "ETS_VALUATION",
  OUTSIDE_ETS = "OUTSIDE_ETS",
  NOT_CONCERNED = "NOT_CONCERNED",
}
export enum ExtAdminPagesEnum {
  DCA = "DCA",
  AGRIMER = "AGRIMER",
  TIRIB = "TIRIB",
  AIRLINE = "AIRLINE",
  ELEC = "ELEC",
}
export enum FileTypeEnum {
  SOURCING = "SOURCING",
  DECISION = "DECISION",
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
export enum RoleEnum {
  ReadOnly = "RO",
  ReadWrite = "RW",
  Admin = "ADMIN",
  Auditor = "AUDITOR",
}
export enum ShippingMethodEnum {
  PIPELINE = "PIPELINE",
  TRUCK = "TRUCK",
  TRAIN = "TRAIN",
  BARGE = "BARGE",
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
  PRODUCTION_BIOLIQUID = "PRODUCTION BIOLIQUID",
  EFCA = "EFCA",
  AIRPORT = "AIRPORT",
}
export enum TransportDocumentTypeEnum {
  DAU = "DAU",
  DAE = "DAE",
  DSA = "DSA",
  DSAC = "DSAC",
  DSP = "DSP",
  OTHER = "OTHER",
}
export enum UserRightsRequestsStatusEnum {
  Pending = "PENDING",
  Accepted = "ACCEPTED",
  Rejected = "REJECTED",
  Revoked = "REVOKED",
}
