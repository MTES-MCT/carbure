export interface paths {
    "/api/auth/activate/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["auth_activate_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/auth/confirm-email-change/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["auth_confirm_email_change_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/auth/login/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["auth_login_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/auth/logout/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["auth_logout_retrieve"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/auth/register/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["auth_register_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/auth/request-activation-link/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["auth_request_activation_link_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/auth/request-email-change/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["auth_request_email_change_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/auth/request-otp/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["auth_request_otp_retrieve"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/auth/request-password-change/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["auth_request_password_change_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/auth/request-password-reset/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["auth_request_password_reset_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/auth/reset-password/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["auth_reset_password_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/auth/verify-otp/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["auth_verify_otp_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/biomethane/annual-declaration/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** @description Retrieve the declaration. Returns a single declaration object. */
        get: operations["biomethane_annual_declaration_retrieve"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/biomethane/annual-declaration/validate/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["biomethane_annual_declaration_validate_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/biomethane/annual-declaration/years/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["biomethane_annual_declaration_years_retrieve"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/biomethane/contract/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** @description Retrieve the contract for the current entity. Returns a single contract object. */
        get: operations["biomethane_contract_retrieve"];
        /** @description Create or update contract using upsert logic. */
        put: operations["biomethane_contract_update"];
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/biomethane/contract/amendments/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["biomethane_contract_amendments_list"];
        put?: never;
        post: operations["biomethane_contract_amendments_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/biomethane/contract/amendments/{id}/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["biomethane_contract_amendments_retrieve"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/biomethane/digestate/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** @description Retrieve the digestate for the current entity and the current year. Returns a single digestate object. */
        get: operations["biomethane_digestate_retrieve"];
        /** @description Create or update the digestate for the current entity (upsert operation). */
        put: operations["biomethane_digestate_update"];
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/biomethane/digestate-storage/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["biomethane_digestate_storage_list"];
        put?: never;
        post: operations["biomethane_digestate_storage_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/biomethane/digestate-storage/{id}/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["biomethane_digestate_storage_retrieve"];
        put: operations["biomethane_digestate_storage_update"];
        post?: never;
        delete: operations["biomethane_digestate_storage_destroy"];
        options?: never;
        head?: never;
        patch: operations["biomethane_digestate_storage_partial_update"];
        trace?: never;
    };
    "/api/biomethane/digestate/spreading/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["biomethane_digestate_spreading_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/biomethane/digestate/spreading/{id}/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post?: never;
        delete: operations["biomethane_digestate_spreading_destroy"];
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/biomethane/digestate/validate/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["biomethane_digestate_validate_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/biomethane/energy/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** @description Retrieve the energy declaration for the current entity and year. Returns a single energy object. */
        get: operations["biomethane_energy_retrieve"];
        /** @description Create or update the energy declaration for the current entity and the current year. */
        put: operations["biomethane_energy_update"];
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/biomethane/energy/monthly-reports/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** @description Retrieve the energy declaration monthly reports for the current entity and year */
        get: operations["biomethane_energy_monthly_reports_list"];
        /** @description Create or update monthly reports for the specified energy declaration. */
        put: operations["biomethane_energy_monthly_reports_update"];
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/biomethane/energy/validate/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["biomethane_energy_validate_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/biomethane/injection-site/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** @description Retrieve the injection site for the current entity. Returns a single object. */
        get: operations["biomethane_injection_site_retrieve"];
        /** @description Create or update the injection site for the current entity (upsert operation). */
        put: operations["biomethane_injection_site_update"];
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/biomethane/production-unit/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** @description Retrieve the production unit for the current entity. Returns a single production unit object. */
        get: operations["biomethane_production_unit_retrieve"];
        /** @description Create or update the production unit for the current entity (upsert operation). */
        put: operations["biomethane_production_unit_update"];
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/biomethane/supply-input/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["biomethane_supply_input_list"];
        put?: never;
        post: operations["biomethane_supply_input_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/biomethane/supply-input/{id}/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["biomethane_supply_input_retrieve"];
        put: operations["biomethane_supply_input_update"];
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch: operations["biomethane_supply_input_partial_update"];
        trace?: never;
    };
    "/api/biomethane/supply-input/export/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["biomethane_supply_input_export_retrieve"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/biomethane/supply-input/filters/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["biomethane_supply_input_filters_retrieve"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/biomethane/supply-plan/download-template/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** @description Download Supply Plan Excel Template */
        get: operations["biomethane_supply_plan_download_template_retrieve"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/biomethane/supply-plan/export/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["biomethane_supply_plan_export_retrieve"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/biomethane/supply-plan/import/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** @description Upload and process an Excel file to create supply plan entries.  */
        post: operations["import_supply_plan_from_excel"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/biomethane/supply-plan/years/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["biomethane_supply_plan_years_retrieve"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/double-counting/agreements/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["double_counting_agreements_list"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/double-counting/agreements/{id}/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["double_counting_agreements_retrieve"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/double-counting/agreements/agreement-admin/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["double_counting_agreements_agreement_admin_retrieve"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/double-counting/agreements/agreement-public/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["double_counting_agreements_agreement_public_list"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/double-counting/agreements/export/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["double_counting_agreements_export_retrieve"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/double-counting/agreements/filters/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["double_counting_agreements_filters_retrieve"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/double-counting/applications/{id}/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["double_counting_applications_retrieve"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/double-counting/applications/{id}/export/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["double_counting_applications_export_retrieve"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/double-counting/applications/{id}/files/{file_id}/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post?: never;
        delete: operations["double_counting_applications_files_destroy"];
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/double-counting/applications/{id}/update-approved-quotas/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["double_counting_applications_update_approved_quotas_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/double-counting/applications/{id}/upload-files/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["double_counting_applications_upload_files_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/double-counting/applications/add/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["double_counting_applications_add_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/double-counting/applications/approve/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["double_counting_applications_approve_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/double-counting/applications/check-file/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["double_counting_applications_check_file_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/double-counting/applications/filters/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["double_counting_applications_filters_retrieve"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/double-counting/applications/generate-decision/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["double_counting_applications_generate_decision_retrieve"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/double-counting/applications/list-admin/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["double_counting_applications_list_admin_retrieve"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/double-counting/applications/reject/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["double_counting_applications_reject_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/double-counting/snapshot/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["double_counting_snapshot_retrieve"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/elec/certificates/clients/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["elec_certificates_clients_list"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/elec/certificates/snapshot/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["elec_certificates_snapshot_retrieve"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/elec/certificates/years/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["elec_certificates_years_retrieve"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/elec/provision-certificates/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["elec_provision_certificates_list"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/elec/provision-certificates-qualicharge/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["elec_provision_certificates_qualicharge_list"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/elec/provision-certificates-qualicharge/{id}/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["elec_provision_certificates_qualicharge_retrieve"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/elec/provision-certificates-qualicharge/bulk-create/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** @description Create multiple provision certificates in bulk (from Qualicharge) */
        post: operations["bulk_create_provision_certificates_qualicharge"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/elec/provision-certificates-qualicharge/bulk-update/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** @description Update multiple provision certificates in bulk (from Qualicharge) */
        post: operations["bulk_update_provision_certificates_qualicharge"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/elec/provision-certificates-qualicharge/filters/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** @description Retrieve content of a specific filter */
        get: operations["filter_provision_certificates_qualicharge"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/elec/provision-certificates/{id}/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["elec_provision_certificates_retrieve"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/elec/provision-certificates/balance/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["elec_provision_certificates_balance_retrieve"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/elec/provision-certificates/export/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["export_provision_certificates_excel"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/elec/provision-certificates/filters/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["elec_provision_certificates_filters_retrieve"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/elec/provision-certificates/import/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["elec_provision_certificates_import_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/elec/provision-certificates/transfer/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["elec_provision_certificates_transfer_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/elec/transfer-certificates/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["elec_transfer_certificates_list"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/elec/transfer-certificates/{id}/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["elec_transfer_certificates_retrieve"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/elec/transfer-certificates/{id}/accept/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["elec_transfer_certificates_accept_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/elec/transfer-certificates/{id}/cancel/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["elec_transfer_certificates_cancel_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/elec/transfer-certificates/{id}/reject/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["elec_transfer_certificates_reject_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/elec/transfer-certificates/export/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["export_transfer_certificates_excel"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/elec/transfer-certificates/filters/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["elec_transfer_certificates_filters_retrieve"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/entities/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["entities_list"];
        put?: never;
        post: operations["entities_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/entities/{id}/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["entities_retrieve"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/entities/{id}/enable/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["entities_enable_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/entities/add-company": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["entities_add_company_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/entities/certificates/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["entities_certificates_list"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/entities/certificates/{id}/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["entities_certificates_retrieve"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/entities/certificates/add/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["entities_certificates_add_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/entities/certificates/check-entity/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["entities_certificates_check_entity_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/entities/certificates/delete/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["entities_certificates_delete_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/entities/certificates/reject-entity/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["entities_certificates_reject_entity_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/entities/certificates/set-default/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["entities_certificates_set_default_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/entities/certificates/update-certificate/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["entities_certificates_update_certificate_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/entities/depots/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["entities_depots_list"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/entities/depots/add/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["entities_depots_add_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/entities/depots/create-depot/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["entities_depots_create_depot_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/entities/depots/delete-depot/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["entities_depots_delete_depot_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/entities/direct-deliveries/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["entities_direct_deliveries_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/entities/elec/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["entities_elec_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/entities/notifications/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["entities_notifications_list"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/entities/notifications/ack/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["entities_notifications_ack_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/entities/production-sites/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["entities_production_sites_list"];
        put?: never;
        post: operations["entities_production_sites_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/entities/production-sites/{id}/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["entities_production_sites_retrieve"];
        put: operations["entities_production_sites_update"];
        post?: never;
        delete: operations["entities_production_sites_destroy"];
        options?: never;
        head?: never;
        patch: operations["entities_production_sites_partial_update"];
        trace?: never;
    };
    "/api/entities/release-for-consumption/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["entities_release_for_consumption_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/entities/search-company/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["entities_search_company_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/entities/stats/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["entities_stats_retrieve"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/entities/stocks/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["entities_stocks_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/entities/trading/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["entities_trading_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/entities/unit/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["entities_unit_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/entities/update-entity-info/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["entities_update_entity_info_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/entities/users/accept-user/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["entities_users_accept_user_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/entities/users/change-role/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["entities_users_change_role_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/entities/users/entity-rights-requests/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["entities_users_entity_rights_requests_retrieve"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/entities/users/invite-user/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["entities_users_invite_user_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/entities/users/revoke-access/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["entities_users_revoke_access_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/entities/users/rights-requests/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["entities_users_rights_requests_list"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/entities/users/update-right-request/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["entities_users_update_right_request_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/entities/users/update-user-role/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["entities_users_update_user_role_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/nav-stats": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["nav_stats_retrieve"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/resources/airports": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["resources_airports_list"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/resources/biofuels": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["resources_biofuels_list"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/resources/certificates": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["resources_certificates_list"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/resources/countries": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["resources_countries_list"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/resources/depots": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["resources_depots_list"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/resources/entities": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["resources_entities_list"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/resources/feedstocks": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["resources_feedstocks_list"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/resources/production-sites": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["resources_production_sites_list"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/resources/systeme-national": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["resources_systeme_national_list"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/saf/clients/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["saf_clients_list"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/saf/clients/{id}/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["saf_clients_retrieve"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/saf/snapshot/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["saf_snapshot_retrieve"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/saf/ticket-sources/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["saf_ticket_sources_list"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/saf/ticket-sources/{id}/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["saf_ticket_sources_retrieve"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/saf/ticket-sources/{id}/assign/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["saf_ticket_sources_assign_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/saf/ticket-sources/export/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["saf_ticket_sources_export_retrieve"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/saf/ticket-sources/filters/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["saf_ticket_sources_filters_retrieve"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/saf/ticket-sources/group-assign/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["saf_ticket_sources_group_assign_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/saf/tickets/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["saf_tickets_list"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/saf/tickets/{id}/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["saf_tickets_retrieve"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/saf/tickets/{id}/accept/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["saf_tickets_accept_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/saf/tickets/{id}/cancel/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["saf_tickets_cancel_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/saf/tickets/{id}/credit-source/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["saf_tickets_credit_source_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/saf/tickets/{id}/reject/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["saf_tickets_reject_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/saf/tickets/export/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["saf_tickets_export_retrieve"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/saf/tickets/filters/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["saf_tickets_filters_retrieve"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/saf/years/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["saf_years_retrieve"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/tiruert/admin-objectives/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** @description Get agregated objectives for all entities - admin view */
        get: operations["admin_objectives"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/tiruert/admin-objectives-entity/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** @description Get objectives for a specific entity - admin view */
        get: operations["admin_objectives_entity"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/tiruert/elec-operations/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** @description Retrieve a list of operations with optional filtering and pagination. */
        get: operations["list_elec_operations"];
        put?: never;
        /** @description Create a new operation. */
        post: operations["create_elec_operation"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/tiruert/elec-operations/{id}/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** @description Retrieve one specific operation. */
        get: operations["get_elec_operation"];
        put?: never;
        post?: never;
        /** @description Delete an operation. Only allowed for certain types and statuses. */
        delete: operations["delete_elec_operation"];
        options?: never;
        head?: never;
        /** @description Update a part of operation. */
        patch: operations["update_elec_operation"];
        trace?: never;
    };
    "/api/tiruert/elec-operations/{id}/accept/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** @description Set status operation to ACCEPTED */
        post: operations["accept_elec_operation"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/tiruert/elec-operations/{id}/reject/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** @description Set status operation to REJECTED */
        post: operations["reject_elec_operation"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/tiruert/elec-operations/balance/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** @description Retrieve electricity balance */
        get: operations["list_elec_balance"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/tiruert/elec-operations/filters/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** @description Retrieve content of a specific filter */
        get: operations["filter_elec_operations"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/tiruert/elec-operations/teneur/declare/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** @description Set teneur operations to DECLARED */
        post: operations["declare_elec_teneur"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/tiruert/mac-fossil-fuel/export/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["tiruert_mac_fossil_fuel_export_retrieve"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/tiruert/objectives/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** @description Get all objectives */
        get: operations["objectives"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/tiruert/operations/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** @description Retrieve a list of operations with optional filtering and pagination. */
        get: operations["list_operations"];
        put?: never;
        /** @description Create a new operation. */
        post: operations["create_operation"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/tiruert/operations/{id}/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** @description Retrieve one specific operation. */
        get: operations["get_operation"];
        put?: never;
        post?: never;
        /** @description Delete an operation. Only allowed for certain types and statuses. */
        delete: operations["delete_operation"];
        options?: never;
        head?: never;
        /** @description Update a part of operation. */
        patch: operations["update_operation"];
        trace?: never;
    };
    "/api/tiruert/operations/{id}/accept/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** @description Set status operation to ACCEPTED */
        post: operations["accept_operation"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/tiruert/operations/{id}/correct/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** @description Create a new operation 'CUSTOMS_CORRECTION' with a volume to add or remove */
        post: operations["correct_operation"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/tiruert/operations/{id}/reject/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** @description Set status operation to REJECTED */
        post: operations["reject_operation"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/tiruert/operations/balance/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** @description Retrieve balances grouped by mp category / biofuel or by sector or by depot */
        get: operations["list_balances"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/tiruert/operations/balance/filters/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** @description Retrieve content of a specific filter */
        get: operations["filter_balances"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/tiruert/operations/export/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["tiruert_operations_export_retrieve"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/tiruert/operations/filters/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** @description Retrieve content of a specific filter */
        get: operations["filter_operations"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/tiruert/operations/simulate/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** @description Simulate a blending operation */
        post: operations["simulate"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/tiruert/operations/simulate/min_max/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** @description Get bounds for blending operation */
        post: operations["simulation_bounds"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/tiruert/operations/teneur/declare/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** @description Set teneur operations to DECLARED */
        post: operations["declare_teneur"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/token/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** @description Takes a set of user credentials and returns an access and refresh JSON web
         *     token pair to prove the authentication of those credentials. */
        post: operations["token_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/token/refresh/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** @description Takes a refresh type JSON web token and returns an access type JSON web
         *     token if the refresh token is valid. */
        post: operations["token_refresh_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/user/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["user_retrieve"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/user/request-access": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["user_request_access_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/user/revoke-access": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["user_revoke_access_create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
}
export type webhooks = Record<string, never>;
export interface components {
    schemas: {
        AcceptRequest: {
            ets_status: components["schemas"]["EtsStatusEnum"];
        };
        ActivateAccountRequest: {
            uidb64: string;
            token: string;
            invite?: number;
        };
        ActivateResponse: {
            message: string;
            token?: string;
        };
        AddCertificateRequest: {
            certificate_id: string;
            certificate_type: string;
        };
        AddDepotRequest: {
            delivery_site_id: string;
            ownership_type: components["schemas"]["OwnershipTypeEnum"];
            /** @default false */
            blending_is_outsourced: boolean;
            blending_entity_id?: number;
        };
        AgreementLists: {
            active: components["schemas"]["DoubleCountingRegistration"][];
            incoming: components["schemas"]["DoubleCountingRegistration"][];
            expired: components["schemas"]["DoubleCountingRegistration"][];
        };
        Airport: {
            readonly id: number;
            name: string;
            city?: string;
            icao_code?: string;
            readonly country: components["schemas"]["Country"];
            site_type?: components["schemas"]["SiteTypeEnum"];
            address?: string;
            postal_code?: string;
            gps_coordinates?: string | null;
            is_ue_airport?: boolean;
        };
        /**
         * @description * `CMAX_PAP_UPDATE` - CMAX_PAP_UPDATE
         *     * `EFFECTIVE_DATE` - EFFECTIVE_DATE
         *     * `CMAX_ANNUALIZATION` - CMAX_ANNUALIZATION
         *     * `INPUT_BONUS_UPDATE` - INPUT_BONUS_UPDATE
         *     * `L_INDEXATION_UPDATE` - L_INDEXATION_UPDATE
         *     * `PRODUCER_BUYER_INFO_CHANGE` - PRODUCER_BUYER_INFO_CHANGE
         *     * `ENERGY_ENVIRONMENTAL_EFFICIENCY_UPDATE` - ENERGY_ENVIRONMENTAL_EFFICIENCY_UPDATE
         *     * `OTHER` - OTHER
         * @enum {string}
         */
        AmendmentObjectEnum: AmendmentObjectEnum;
        ApplicationFileUploadRequest: {
            extra_files?: File[];
        };
        ApplicationListe: {
            rejected: components["schemas"]["DoubleCountingApplicationPartial"][];
            pending: components["schemas"]["DoubleCountingApplicationPartial"][];
        };
        ApplicationSnapshot: {
            applications_pending: number;
            applications_rejected: number;
            agreements_incoming: number;
            agreements_active: number;
            agreements_expired: number;
        };
        ApproveDoubleCountingRequest: {
            dca_id: number;
        };
        Balance: {
            sector: components["schemas"]["ObjectiveSectorCodeEnum"];
            /** Format: double */
            readonly initial_balance: number;
            /** Format: double */
            available_balance: number;
            quantity: components["schemas"]["BalanceQuantity"];
            /** Format: double */
            pending_teneur: number;
            /** Format: double */
            declared_teneur: number;
            pending_operations: number;
            unit: string;
            customs_category: components["schemas"]["MPCategoriesEnum"];
            biofuel: components["schemas"]["BalanceBiofuel"];
            /** Format: double */
            ghg_reduction_min: number;
            /** Format: double */
            ghg_reduction_max: number;
            /** Format: double */
            saved_emissions: number;
        };
        BalanceBiofuel: {
            id: number;
            code: string;
            /** Format: double */
            renewable_energy_share: number;
        };
        BalanceByDepot: {
            customs_category: string;
            biofuel: components["schemas"]["BalanceBiofuel"];
            depots: components["schemas"]["BalanceDepot"][];
        };
        BalanceBySector: {
            sector: components["schemas"]["ObjectiveSectorCodeEnum"];
            /** Format: double */
            readonly initial_balance: number;
            /** Format: double */
            available_balance: number;
            quantity: components["schemas"]["BalanceQuantity"];
            /** Format: double */
            pending_teneur: number;
            /** Format: double */
            declared_teneur: number;
            pending_operations: number;
            unit: string;
        };
        BalanceDepot: {
            id: number;
            name: string;
            quantity: components["schemas"]["BalanceQuantity"];
            unit?: string;
        };
        BalanceQuantity: {
            /**
             * Format: double
             * @default 0
             */
            credit: number;
            /**
             * Format: double
             * @default 0
             */
            debit: number;
        };
        BalanceResponse: components["schemas"]["Balance"] | components["schemas"]["BalanceByDepot"] | components["schemas"]["BalanceBySector"];
        Biofuel: {
            name: string;
            name_en: string;
            code: string;
        };
        BiomethaneAnnualDeclaration: {
            readonly year: number;
            status?: components["schemas"]["BiomethaneAnnualDeclarationStatusEnum"];
            readonly missing_fields: string;
            readonly is_ready: string;
        };
        /**
         * @description * `PENDING` - PENDING
         *     * `DECLARED` - DECLARED
         * @enum {string}
         */
        BiomethaneAnnualDeclarationStatusEnum: BiomethaneAnnualDeclarationStatusEnum;
        BiomethaneContract: {
            readonly id: number;
            readonly amendments: components["schemas"]["BiomethaneContractAmendment"][];
            readonly tracked_amendment_types: components["schemas"]["TrackedAmendmentTypesEnum"][];
            tariff_reference?: components["schemas"]["TariffReferenceEnum"] | null;
            installation_category?: components["schemas"]["InstallationCategoryEnum"] | null;
            /** Format: double */
            cmax?: number | null;
            cmax_annualized?: boolean;
            /** Format: double */
            cmax_annualized_value?: number | null;
            /** Format: double */
            pap_contracted?: number | null;
            /** Format: date */
            signature_date?: string | null;
            /** Format: date */
            effective_date?: string | null;
            /** Format: uri */
            general_conditions_file?: string | null;
            /** Format: uri */
            specific_conditions_file?: string | null;
            buyer?: number | null;
            producer: number;
        };
        BiomethaneContractAmendment: {
            readonly id: number;
            amendment_object: components["schemas"]["AmendmentObjectEnum"][];
            /** Format: date */
            signature_date: string;
            /** Format: date */
            effective_date: string;
            /** Format: uri */
            amendment_file: string;
            amendment_details?: string | null;
            contract: number;
        };
        BiomethaneContractAmendmentAdd: {
            readonly id: number;
            amendment_object: components["schemas"]["AmendmentObjectEnum"][];
            /** Format: date */
            signature_date: string;
            /** Format: date */
            effective_date: string;
            /** Format: uri */
            amendment_file: string;
            amendment_details?: string | null;
        };
        BiomethaneContractAmendmentAddRequest: {
            amendment_object: components["schemas"]["AmendmentObjectEnum"][];
            /** Format: date */
            signature_date: string;
            /** Format: date */
            effective_date: string;
            /** Format: binary */
            amendment_file: File;
            amendment_details?: string | null;
        };
        BiomethaneContractInputRequest: {
            cmax_annualized?: boolean | null;
            is_red_ii?: boolean;
            tariff_reference?: components["schemas"]["TariffReferenceEnum"] | null;
            installation_category?: components["schemas"]["InstallationCategoryEnum"] | null;
            /** Format: double */
            cmax?: number | null;
            /** Format: double */
            cmax_annualized_value?: number | null;
            /** Format: double */
            pap_contracted?: number | null;
            /** Format: date */
            signature_date?: string | null;
            /** Format: date */
            effective_date?: string | null;
            /** Format: binary */
            general_conditions_file?: File | null;
            /** Format: binary */
            specific_conditions_file?: File | null;
            tracked_amendment_types?: unknown;
            buyer?: number | null;
        };
        BiomethaneDigestate: {
            readonly id: number;
            composting_locations?: components["schemas"]["CompostingLocationsEnum"][];
            readonly spreadings: components["schemas"]["BiomethaneDigestateSpreading"][];
            year: number;
            status: components["schemas"]["BiomethaneDigestateStatusEnum"];
            /** Format: double */
            raw_digestate_tonnage_produced?: number | null;
            /** Format: double */
            raw_digestate_dry_matter_rate?: number | null;
            /** Format: double */
            solid_digestate_tonnage?: number | null;
            /** Format: double */
            liquid_digestate_quantity?: number | null;
            /** Format: double */
            average_spreading_valorization_distance?: number | null;
            external_platform_name?: string | null;
            /** Format: double */
            external_platform_digestate_volume?: number | null;
            external_platform_department?: string | null;
            external_platform_municipality?: string | null;
            /** Format: double */
            on_site_composted_digestate_volume?: number | null;
            /** Format: double */
            annual_eliminated_volume?: number | null;
            incinerator_landfill_center_name?: string | null;
            /** Format: double */
            wwtp_materials_to_incineration?: number | null;
            acquiring_companies?: string | null;
            /** Format: double */
            sold_volume?: number | null;
            producer: number;
        };
        BiomethaneDigestateInputRequest: {
            composting_locations?: components["schemas"]["CompostingLocationsEnum"][];
            /** Format: double */
            raw_digestate_tonnage_produced?: number | null;
            /** Format: double */
            raw_digestate_dry_matter_rate?: number | null;
            /** Format: double */
            solid_digestate_tonnage?: number | null;
            /** Format: double */
            liquid_digestate_quantity?: number | null;
            /** Format: double */
            average_spreading_valorization_distance?: number | null;
            external_platform_name?: string | null;
            /** Format: double */
            external_platform_digestate_volume?: number | null;
            external_platform_department?: string | null;
            external_platform_municipality?: string | null;
            /** Format: double */
            on_site_composted_digestate_volume?: number | null;
            /** Format: double */
            annual_eliminated_volume?: number | null;
            incinerator_landfill_center_name?: string | null;
            /** Format: double */
            wwtp_materials_to_incineration?: number | null;
            acquiring_companies?: string | null;
            /** Format: double */
            sold_volume?: number | null;
        };
        BiomethaneDigestateSpreading: {
            readonly id: number;
            spreading_department: string;
            /** Format: double */
            spread_quantity: number;
            /** Format: double */
            spread_parcels_area: number;
            digestate: number;
        };
        BiomethaneDigestateSpreadingAdd: {
            readonly id: number;
            spreading_department: string;
            /** Format: double */
            spread_quantity: number;
            /** Format: double */
            spread_parcels_area: number;
        };
        BiomethaneDigestateSpreadingAddRequest: {
            spreading_department: string;
            /** Format: double */
            spread_quantity: number;
            /** Format: double */
            spread_parcels_area: number;
        };
        /**
         * @description * `PENDING` - PENDING
         *     * `VALIDATED` - VALIDATED
         * @enum {string}
         */
        BiomethaneDigestateStatusEnum: BiomethaneDigestateStatusEnum;
        BiomethaneDigestateStorage: {
            readonly id: number;
            type: string;
            /** Format: double */
            capacity: number;
            has_cover?: boolean;
            has_biogas_recovery?: boolean;
            producer: number;
        };
        BiomethaneDigestateStorageInput: {
            readonly id: number;
            type: string;
            /** Format: double */
            capacity: number;
            has_cover?: boolean;
            has_biogas_recovery?: boolean;
        };
        BiomethaneDigestateStorageInputRequest: {
            type: string;
            /** Format: double */
            capacity: number;
            has_cover?: boolean;
            has_biogas_recovery?: boolean;
        };
        BiomethaneEnergy: {
            readonly id: number;
            year: number;
            status?: components["schemas"]["BiomethaneDigestateStatusEnum"];
            /** Format: double */
            injected_biomethane_gwh_pcs_per_year?: number | null;
            /** Format: double */
            injected_biomethane_nm3_per_year?: number | null;
            /** Format: double */
            injected_biomethane_ch4_rate_percent?: number | null;
            /** Format: double */
            injected_biomethane_pcs_kwh_per_nm3?: number | null;
            /** Format: double */
            operating_hours?: number | null;
            /** Format: double */
            produced_biogas_nm3_per_year?: number | null;
            /** Format: double */
            flared_biogas_nm3_per_year?: number | null;
            /** Format: double */
            flaring_operating_hours?: number | null;
            attest_no_fossil_for_digester_heating_and_purification?: boolean;
            energy_used_for_digester_heating?: string | null;
            fossil_details_for_digester_heating?: string | null;
            attest_no_fossil_for_installation_needs?: boolean;
            energy_used_for_installation_needs?: string | null;
            fossil_details_for_installation_needs?: string | null;
            /** Format: double */
            purified_biogas_quantity_nm3?: number | null;
            /** Format: double */
            purification_electric_consumption_kwe?: number | null;
            /** Format: double */
            self_consumed_biogas_nm3?: number | null;
            /** Format: double */
            total_unit_electric_consumption_kwe?: number | null;
            /** Format: double */
            butane_or_propane_addition?: number | null;
            /** Format: double */
            fossil_fuel_consumed_kwh?: number | null;
            has_opposition_or_complaints_acceptability?: boolean;
            estimated_work_days_acceptability?: number | null;
            has_malfunctions?: boolean;
            malfunction_cumulative_duration_days?: number | null;
            malfunction_types?: components["schemas"]["MalfunctionTypesEnum"] | null;
            malfunction_details?: string | null;
            has_injection_difficulties_due_to_network_saturation?: boolean;
            injection_impossibility_hours?: number | null;
            producer: number;
        };
        BiomethaneEnergyInputRequest: {
            /** Format: double */
            injected_biomethane_gwh_pcs_per_year?: number | null;
            /** Format: double */
            injected_biomethane_nm3_per_year?: number | null;
            /** Format: double */
            injected_biomethane_ch4_rate_percent?: number | null;
            /** Format: double */
            injected_biomethane_pcs_kwh_per_nm3?: number | null;
            /** Format: double */
            operating_hours?: number | null;
            /** Format: double */
            produced_biogas_nm3_per_year?: number | null;
            /** Format: double */
            flared_biogas_nm3_per_year?: number | null;
            /** Format: double */
            flaring_operating_hours?: number | null;
            attest_no_fossil_for_digester_heating_and_purification?: boolean;
            energy_used_for_digester_heating?: string | null;
            fossil_details_for_digester_heating?: string | null;
            attest_no_fossil_for_installation_needs?: boolean;
            energy_used_for_installation_needs?: string | null;
            fossil_details_for_installation_needs?: string | null;
            /** Format: double */
            purified_biogas_quantity_nm3?: number | null;
            /** Format: double */
            purification_electric_consumption_kwe?: number | null;
            /** Format: double */
            self_consumed_biogas_nm3?: number | null;
            /** Format: double */
            total_unit_electric_consumption_kwe?: number | null;
            /** Format: double */
            butane_or_propane_addition?: number | null;
            /** Format: double */
            fossil_fuel_consumed_kwh?: number | null;
            has_opposition_or_complaints_acceptability?: boolean;
            estimated_work_days_acceptability?: number | null;
            has_malfunctions?: boolean;
            malfunction_cumulative_duration_days?: number | null;
            malfunction_types?: components["schemas"]["MalfunctionTypesEnum"] | null;
            malfunction_details?: string | null;
            has_injection_difficulties_due_to_network_saturation?: boolean;
            injection_impossibility_hours?: number | null;
        };
        BiomethaneEnergyMonthlyReport: {
            readonly id: number;
            month: number;
            /** Format: double */
            injected_volume_nm3?: number;
            /** Format: double */
            average_monthly_flow_nm3_per_hour?: number;
            /** Format: double */
            injection_hours?: number;
            energy: number;
        };
        BiomethaneInjectionSite: {
            readonly id: number;
            unique_identification_number: string;
            is_shared_injection_site?: boolean;
            meter_number?: string | null;
            is_different_from_production_site?: boolean;
            company_address?: string | null;
            city?: string | null;
            postal_code?: string | null;
            network_type?: components["schemas"]["NetworkTypeEnum"] | null;
            network_manager_name?: string | null;
            producer: number;
        };
        BiomethaneInjectionSiteInputRequest: {
            unique_identification_number: string;
            is_shared_injection_site?: boolean;
            meter_number?: string | null;
            is_different_from_production_site?: boolean;
            company_address?: string | null;
            city?: string | null;
            postal_code?: string | null;
            network_type: components["schemas"]["NetworkTypeEnum"] | null;
            network_manager_name: string | null;
        };
        BiomethaneProductionUnit: {
            readonly id: number;
            installed_meters?: components["schemas"]["InstalledMetersEnum"][];
            digestate_valorization_methods?: components["schemas"]["DigestateValorizationMethodsEnum"][];
            spreading_management_methods?: components["schemas"]["SpreadingManagementMethodsEnum"][];
            unit_name?: string | null;
            siret_number?: string | null;
            company_address?: string | null;
            postal_code?: string | null;
            city?: string | null;
            department?: string | null;
            unit_type?: components["schemas"]["UnitTypeEnum"] | null;
            has_sanitary_approval?: boolean;
            sanitary_approval_number?: string | null;
            has_hygienization_exemption?: boolean;
            hygienization_exemption_type?: components["schemas"]["HygienizationExemptionTypeEnum"] | null;
            icpe_number?: string | null;
            icpe_regime?: components["schemas"]["IcpeRegimeEnum"] | null;
            process_type?: components["schemas"]["ProcessTypeEnum"] | null;
            methanization_process?: components["schemas"]["MethanizationProcessEnum"] | null;
            /** Format: double */
            production_efficiency?: number | null;
            has_hygienization_unit?: boolean;
            has_co2_valorization_process?: boolean;
            has_digestate_phase_separation?: boolean;
            raw_digestate_treatment_steps?: string | null;
            liquid_phase_treatment_steps?: string | null;
            solid_phase_treatment_steps?: string | null;
            digestate_sale_type?: components["schemas"]["DigestateSaleTypeEnum"] | null;
            producer: number;
        };
        BiomethaneProductionUnitUpsertRequest: {
            installed_meters?: components["schemas"]["InstalledMetersEnum"][];
            digestate_valorization_methods?: components["schemas"]["DigestateValorizationMethodsEnum"][];
            spreading_management_methods?: components["schemas"]["SpreadingManagementMethodsEnum"][];
            unit_name?: string | null;
            siret_number?: string | null;
            company_address?: string | null;
            postal_code?: string | null;
            city?: string | null;
            department?: string | null;
            unit_type?: components["schemas"]["UnitTypeEnum"] | null;
            has_sanitary_approval?: boolean;
            sanitary_approval_number?: string | null;
            has_hygienization_exemption?: boolean;
            hygienization_exemption_type?: components["schemas"]["HygienizationExemptionTypeEnum"] | null;
            icpe_number?: string | null;
            icpe_regime?: components["schemas"]["IcpeRegimeEnum"] | null;
            process_type?: components["schemas"]["ProcessTypeEnum"] | null;
            methanization_process?: components["schemas"]["MethanizationProcessEnum"] | null;
            /** Format: double */
            production_efficiency?: number | null;
            has_hygienization_unit?: boolean;
            has_co2_valorization_process?: boolean;
            has_digestate_phase_separation?: boolean;
            raw_digestate_treatment_steps?: string | null;
            liquid_phase_treatment_steps?: string | null;
            solid_phase_treatment_steps?: string | null;
            digestate_sale_type?: components["schemas"]["DigestateSaleTypeEnum"] | null;
        };
        BiomethaneSupplyInput: {
            readonly id: number;
            origin_country: components["schemas"]["Country"];
            source: components["schemas"]["BiomethaneSupplyInputSourceEnum"];
            crop_type: components["schemas"]["CropTypeEnum"];
            input_category: components["schemas"]["InputCategoryEnum"];
            input_type: string;
            material_unit: components["schemas"]["MaterialUnitEnum"];
            /** Format: double */
            dry_matter_ratio_percent?: number | null;
            /** Format: double */
            volume: number;
            origin_department?: string | null;
            /** Format: double */
            average_weighted_distance_km?: number | null;
            /** Format: double */
            maximum_distance_km?: number | null;
            supply_plan: number;
        };
        BiomethaneSupplyInputCreate: {
            readonly id: number;
            source: components["schemas"]["BiomethaneSupplyInputSourceEnum"];
            crop_type: components["schemas"]["CropTypeEnum"];
            input_category: components["schemas"]["InputCategoryEnum"];
            material_unit: components["schemas"]["MaterialUnitEnum"];
            origin_country: string;
            /** Format: double */
            dry_matter_ratio_percent?: number | null;
            /** Format: double */
            volume: number;
            /** Format: double */
            average_weighted_distance_km?: number | null;
            /** Format: double */
            maximum_distance_km?: number | null;
            input_type: string;
            origin_department?: string | null;
        };
        BiomethaneSupplyInputCreateRequest: {
            source: components["schemas"]["BiomethaneSupplyInputSourceEnum"];
            crop_type: components["schemas"]["CropTypeEnum"];
            input_category: components["schemas"]["InputCategoryEnum"];
            material_unit: components["schemas"]["MaterialUnitEnum"];
            origin_country: string;
            /** Format: double */
            dry_matter_ratio_percent?: number | null;
            /** Format: double */
            volume: number;
            /** Format: double */
            average_weighted_distance_km?: number | null;
            /** Format: double */
            maximum_distance_km?: number | null;
            input_type: string;
            origin_department?: string | null;
        };
        BiomethaneSupplyInputExport: {
            readonly year: number;
            readonly origin_country: string;
            source: components["schemas"]["BiomethaneSupplyInputSourceEnum"];
            crop_type: components["schemas"]["CropTypeEnum"];
            input_category: components["schemas"]["InputCategoryEnum"];
            input_type: string;
            material_unit: components["schemas"]["MaterialUnitEnum"];
            /** Format: double */
            dry_matter_ratio_percent?: number | null;
            /** Format: double */
            volume: number;
            origin_department?: string | null;
            /** Format: double */
            average_weighted_distance_km?: number | null;
            /** Format: double */
            maximum_distance_km?: number | null;
        };
        /**
         * @description * `INTERNAL` - Interne
         *     * `EXTERNAL` - Externe
         * @enum {string}
         */
        BiomethaneSupplyInputSourceEnum: PathsApiBiomethaneSupplyInputGetParametersQuerySource;
        BiomethaneUploadExcelRequest: {
            /** Format: binary */
            file: File;
        };
        CarbureLotPublic: {
            readonly id: number;
            year: number;
            period: number;
            carbure_id?: string;
            readonly carbure_producer: components["schemas"]["EntitySummary"];
            unknown_producer?: string | null;
            readonly carbure_production_site: components["schemas"]["ProductionSite"];
            unknown_production_site?: string | null;
            readonly production_country: components["schemas"]["Country"];
            /** Format: date */
            production_site_commissioning_date?: string | null;
            production_site_certificate?: string | null;
            production_site_double_counting_certificate?: string | null;
            readonly carbure_supplier: components["schemas"]["EntitySummary"];
            unknown_supplier?: string | null;
            supplier_certificate?: string | null;
            supplier_certificate_type?: string | null;
            transport_document_type?: components["schemas"]["TransportDocumentTypeEnum"];
            transport_document_reference?: string | null;
            readonly carbure_client: components["schemas"]["EntitySummary"];
            unknown_client?: string | null;
            /** Format: date */
            dispatch_date?: string | null;
            readonly carbure_dispatch_site: components["schemas"]["Depot"];
            unknown_dispatch_site?: string | null;
            readonly dispatch_site_country: components["schemas"]["Country"];
            /** Format: date */
            delivery_date?: string | null;
            readonly carbure_delivery_site: components["schemas"]["Depot"];
            unknown_delivery_site?: string | null;
            readonly delivery_site_country: components["schemas"]["Country"];
            delivery_type?: components["schemas"]["DeliveryTypeEnum"];
            lot_status?: components["schemas"]["LotStatusEnum"];
            correction_status?: components["schemas"]["CorrectionStatusEnum"];
            /** Format: double */
            volume?: number;
            /** Format: double */
            weight?: number;
            /** Format: double */
            lhv_amount?: number;
            readonly feedstock: components["schemas"]["FeedStock"];
            readonly biofuel: components["schemas"]["Biofuel"];
            readonly country_of_origin: components["schemas"]["Country"];
            /** Format: double */
            eec?: number;
            /** Format: double */
            el?: number;
            /** Format: double */
            ep?: number;
            /** Format: double */
            etd?: number;
            /** Format: double */
            eu?: number;
            /** Format: double */
            esca?: number;
            /** Format: double */
            eccs?: number;
            /** Format: double */
            eccr?: number;
            /** Format: double */
            eee?: number;
            /** Format: double */
            ghg_total?: number;
            /** Format: double */
            ghg_reference?: number;
            /** Format: double */
            ghg_reduction?: number;
            /** Format: double */
            ghg_reference_red_ii?: number;
            /** Format: double */
            ghg_reduction_red_ii?: number;
            free_field?: string | null;
            readonly added_by: components["schemas"]["EntitySummary"];
            /** Format: date-time */
            readonly created_at: string | null;
            readonly carbure_vendor: components["schemas"]["EntitySummary"];
            vendor_certificate?: string | null;
            vendor_certificate_type?: string | null;
            data_reliability_score?: string;
        };
        CarbureNotification: {
            readonly id: number;
            dest: components["schemas"]["Entity"];
            /** Format: date-time */
            readonly datetime: string;
            type: components["schemas"]["CarbureNotificationTypeEnum"];
            acked?: boolean;
            send_by_email?: boolean;
            email_sent?: boolean;
            meta?: unknown;
        };
        /**
         * @description * `CORRECTION_REQUEST` - CORRECTION_REQUEST
         *     * `CORRECTION_DONE` - CORRECTION_DONE
         *     * `LOTS_REJECTED` - LOTS_REJECTED
         *     * `LOTS_RECEIVED` - LOTS_RECEIVED
         *     * `LOTS_RECALLED` - LOTS_RECALLED
         *     * `CERTIFICATE_EXPIRED` - CERTIFICATE_EXPIRED
         *     * `CERTIFICATE_REJECTED` - CERTIFICATE_REJECTED
         *     * `DECLARATION_VALIDATED` - DECLARATION_VALIDATED
         *     * `DECLARATION_CANCELLED` - DECLARATION_CANCELLED
         *     * `METER_READINGS_APP_STARTED` - METER_READINGS_APP_STARTED
         *     * `METER_READINGS_APP_ENDING_SOON` - METER_READINGS_APP_ENDING_SOON
         *     * `DECLARATION_REMINDER` - DECLARATION_REMINDER
         *     * `SAF_TICKET_REJECTED` - SAF_TICKET_REJECTED
         *     * `SAF_TICKET_ACCEPTED` - SAF_TICKET_ACCEPTED
         *     * `SAF_TICKET_RECEIVED` - SAF_TICKET_RECEIVED
         *     * `LOTS_UPDATED_BY_ADMIN` - LOTS_UPDATED_BY_ADMIN
         *     * `LOTS_DELETED_BY_ADMIN` - LOTS_DELETED_BY_ADMIN
         *     * `ELEC_TRANSFER_CERTIFICATE` - ELEC_TRANSFER_CERTIFICATE
         * @enum {string}
         */
        CarbureNotificationTypeEnum: CarbureNotificationTypeEnum;
        /**
         * @description * `SYSTEME_NATIONAL` - SYSTEME_NATIONAL
         *     * `ISCC` - ISCC
         *     * `REDCERT` - REDCERT
         *     * `2BS` - 2BS
         * @enum {string}
         */
        CertificateTypeEnum: CertificateTypeEnum;
        ChangePasswordError: {
            /** @description Message d'erreur général */
            message?: string;
            /** @description Détails des erreurs de validation */
            errors?: string;
        };
        ChangePasswordRequest: {
            current_password: string;
            new_password: string;
            confirm_new_password: string;
        };
        ChangePasswordSuccess: {
            /** @default success */
            status: string;
        };
        ChangeRoleRequest: {
            /** Format: email */
            email: string;
            role: string;
        };
        CheckCertificateRequest: {
            entity_certificate_id: number;
        };
        CheckFileResponse: {
            file: components["schemas"]["File"];
            /** Format: date-time */
            checked_at: string;
        };
        CommentRequest: {
            comment?: string;
        };
        CompanyPreview: {
            name: string;
            legal_name: string;
            registration_id: string;
            registered_address: string;
            registered_city: string;
            registered_zipcode: string;
            registered_country: components["schemas"]["RegistrationCountry"];
            department_code: string;
        };
        /**
         * @description * `ON_SITE` - Sur site
         *     * `EXTERNAL_PLATFORM` - Plateforme externe
         * @enum {string}
         */
        CompostingLocationsEnum: CompostingLocationsEnum;
        ConfirmEmailChangeError: {
            /** @description Message d'erreur général */
            message?: string;
            /** @description Détails des erreurs de validation */
            errors?: string;
            /** @description Code d'erreur spécifique */
            error?: string;
        };
        ConfirmEmailChangeRequest: {
            /** Format: email */
            new_email: string;
            otp_token: string;
        };
        ConfirmEmailChangeSuccess: {
            /** @default success */
            status: string;
        };
        /**
         * @description * `MAC` - MAC
         *     * `MAC_DECLASSEMENT` - MAC_DECLASSEMENT
         * @enum {string}
         */
        ConsumptionTypeEnum: PathsApiSafTicketsGetParametersQueryConsumption_type;
        /**
         * @description * `NO_PROBLEMO` - NO_PROBLEMO
         *     * `IN_CORRECTION` - IN_CORRECTION
         *     * `FIXED` - FIXED
         * @enum {string}
         */
        CorrectionStatusEnum: CorrectionStatusEnum;
        Country: {
            name: string;
            name_en: string;
            code_pays: string;
            is_in_europe?: boolean;
        };
        CreateDepotRequest: {
            country_code: string;
            entity_id: number;
            depot_id: string;
            depot_type: string;
            ownership_type: components["schemas"]["OwnershipTypeEnum"];
            /** @default false */
            blending_is_outsourced: boolean;
            blending_entity_id?: number;
            name: string;
            site_siret?: string;
            customs_id?: string;
            icao_code?: string;
            site_type?: components["schemas"]["SiteTypeEnum"];
            address?: string;
            postal_code?: string;
            city?: string;
            gps_coordinates?: string | null;
            accise?: string;
            /**
             * Format: double
             * @description Entre 0 et 1
             */
            electrical_efficiency?: number | null;
            /**
             * Format: double
             * @description Entre 0 et 1
             */
            thermal_efficiency?: number | null;
            /**
             * Format: double
             * @description En degrés Celsius
             */
            useful_temperature?: number | null;
            ges_option?: components["schemas"]["GesOptionEnum"];
            eligible_dc?: boolean;
            dc_number?: string;
            dc_reference?: string;
            manager_name?: string;
            manager_phone?: string;
            manager_email?: string;
            private?: boolean;
            is_enabled?: boolean;
            /** Format: date */
            date_mise_en_service?: string | null;
            is_ue_airport?: boolean;
            country?: number | null;
            created_by?: number | null;
        };
        CreateEntityRequest: {
            name: string;
            entity_type?: components["schemas"]["EntityTypeEnum"];
            has_saf?: boolean;
            has_elec?: boolean;
        };
        /**
         * @description * `MAIN` - Principale
         *     * `INTERMEDIATE` - Intermédiaire
         * @enum {string}
         */
        CropTypeEnum: CropTypeEnum;
        DeleteCertificateRequest: {
            certificate_id: string;
            certificate_type: string;
        };
        DeleteDepotRequest: {
            delivery_site_id: string;
        };
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
        DeliveryTypeEnum: DeliveryTypeEnum;
        Depot: {
            readonly id: number;
            name: string;
            city?: string;
            customs_id?: string;
            readonly country: components["schemas"]["Country"];
            site_type?: components["schemas"]["SiteTypeEnum"];
            address?: string;
            postal_code?: string;
            gps_coordinates?: string | null;
            accise?: string;
            /**
             * Format: double
             * @description Entre 0 et 1
             */
            electrical_efficiency?: number | null;
            /**
             * Format: double
             * @description Entre 0 et 1
             */
            thermal_efficiency?: number | null;
            /**
             * Format: double
             * @description En degrés Celsius
             */
            useful_temperature?: number | null;
        };
        DepotProductionSite: {
            address?: string;
            name: string;
            country: components["schemas"]["Pays"];
            readonly id: number;
            /** Format: date */
            date_mise_en_service?: string | null;
            site_siret?: string;
            postal_code?: string;
            manager_name?: string;
            manager_phone?: string;
            manager_email?: string;
            ges_option?: components["schemas"]["GesOptionEnum"];
            eligible_dc?: boolean;
            dc_reference?: string;
            dc_number?: string;
            city?: string;
            certificates: components["schemas"]["ProductionSiteCertificateSertificate"][];
        };
        /**
         * @description * `DIG_AGRI_SPECIFICATIONS` - Cahier de charges DIG Agri
         *     * `HOMOLOGATION` - Homologation
         *     * `STANDARDIZED_PRODUCT` - Produit normé
         * @enum {string}
         */
        DigestateSaleTypeEnum: DigestateSaleTypeEnum;
        /**
         * @description * `SPREADING` - Épandage
         *     * `COMPOSTING` - Compostage
         *     * `INCINERATION_LANDFILLING` - Incinération / Enfouissement
         * @enum {string}
         */
        DigestateValorizationMethodsEnum: DigestateValorizationMethodsEnum;
        DirectDeliveriesRequest: {
            /** @default false */
            has_direct_deliveries: boolean;
        };
        DoubleCountingAdminAddRequest: {
            certificate_id?: string;
            entity_id: number;
            producer_id: number;
            production_site_id: number;
            /** @default false */
            should_replace: boolean;
            /** Format: binary */
            file: File;
            extra_files?: File[];
        };
        /**
         * @description * `ACTIVE` - ACTIVE
         *     * `EXPIRED` - EXPIRED
         *     * `EXPIRES_SOON` - EXPIRES_SOON
         *     * `INCOMING` - INCOMING
         * @enum {string}
         */
        DoubleCountingAgreementStatus: DoubleCountingAgreementStatus;
        DoubleCountingApplication: {
            readonly id: number;
            /** Format: date-time */
            readonly created_at: string;
            readonly producer: components["schemas"]["Entity"];
            /**
             * Adresse électronique
             * Format: email
             */
            readonly producer_user: string;
            readonly production_site: components["schemas"]["DoubleCountingProductionSite"];
            /** Format: date */
            period_start: string;
            /** Format: date */
            period_end: string;
            status?: components["schemas"]["DoubleCountingStatus"];
            readonly sourcing: components["schemas"]["DoubleCountingSourcing"][];
            readonly production: components["schemas"]["DoubleCountingProduction"][];
            readonly documents: components["schemas"]["DoubleCountingDocFile"][];
            readonly download_link: string;
            readonly has_dechets_industriels: boolean;
        };
        DoubleCountingApplicationPartial: {
            readonly id: number;
            /** Format: date-time */
            readonly created_at: string;
            readonly producer: components["schemas"]["EntitySummary"];
            readonly production_site: components["schemas"]["DoubleCountingProductionSitePreview"];
            /** Format: date */
            period_start: string;
            /** Format: date */
            period_end: string;
            readonly status: components["schemas"]["DoubleCountingStatus"];
            certificate_id: string;
            readonly agreement_id: number;
            /** Format: double */
            readonly quotas_progression: number;
            /**
             * Adresse électronique
             * Format: email
             */
            readonly producer_user: string;
        };
        DoubleCountingDocFile: {
            readonly id: number;
            file_name?: string;
            file_type?: components["schemas"]["FileTypeEnum"];
            readonly url: string;
        };
        DoubleCountingProduction: {
            readonly id: number;
            readonly year: number;
            readonly biofuel: components["schemas"]["Biofuel"];
            readonly feedstock: components["schemas"]["FeedStock"];
            readonly max_production_capacity: number;
            readonly estimated_production: number;
            readonly requested_quota: number;
            readonly approved_quota: number;
        };
        DoubleCountingProductionHistory: {
            readonly id: number;
            readonly year: number;
            readonly biofuel: components["schemas"]["Biofuel"];
            readonly feedstock: components["schemas"]["FeedStock"];
            readonly max_production_capacity: number;
            readonly effective_production: number;
        };
        DoubleCountingProductionSite: {
            readonly id: number;
            readonly producer: components["schemas"]["Entity"];
            name: string;
            readonly country: components["schemas"]["Country"];
            /** Format: date */
            date_mise_en_service?: string | null;
            ges_option?: components["schemas"]["GesOptionEnum"];
            eligible_dc?: boolean;
            dc_reference?: string;
            site_siret?: string;
            address?: string;
            city?: string;
            postal_code?: string;
            gps_coordinates?: string | null;
            manager_name?: string;
            manager_phone?: string;
            manager_email?: string;
            readonly inputs: components["schemas"]["FeedStock"][];
            readonly outputs: components["schemas"]["Biofuel"][];
            readonly certificates: components["schemas"]["GenericCertificate"][];
        };
        DoubleCountingProductionSitePreview: {
            readonly id: number;
            name: string;
        };
        DoubleCountingQuota: {
            approved_quota: number;
            biofuel: components["schemas"]["Biofuel"];
            feedstock: components["schemas"]["FeedStock"];
            id: number;
            lot_count: number;
            production_tonnes: number;
            quotas_progression: number;
            requested_quota: number;
            year: number;
        };
        DoubleCountingRegistration: {
            readonly id: number;
            certificate_id: string;
            /** Format: date */
            valid_from: string;
            readonly producer: components["schemas"]["EntitySummary"];
            readonly production_site: string;
            /** Format: date */
            valid_until: string;
            readonly status: components["schemas"]["DoubleCountingAgreementStatus"];
            /** Format: double */
            readonly quotas_progression: number;
        };
        DoubleCountingRegistrationDetails: {
            readonly id: number;
            certificate_id: string;
            /** Format: date */
            valid_from: string;
            /** Format: date */
            valid_until: string;
            readonly status: components["schemas"]["DoubleCountingAgreementStatus"];
            readonly producer: string;
            readonly production_site: string;
            application: components["schemas"]["DoubleCountingApplication"];
            readonly quotas: components["schemas"]["DoubleCountingQuota"][];
        };
        DoubleCountingRegistrationPublic: {
            readonly production_site: components["schemas"]["FieldData"];
            certificate_id: string;
            /** Format: date */
            valid_from: string;
            /** Format: date */
            valid_until: string;
            readonly biofuel_list: string;
        };
        DoubleCountingSourcing: {
            readonly id: number;
            readonly year: number;
            readonly feedstock: components["schemas"]["FeedStock"];
            readonly origin_country: components["schemas"]["Country"];
            readonly supply_country: components["schemas"]["Country"];
            readonly transit_country: components["schemas"]["Country"];
            readonly metric_tonnes: number;
        };
        DoubleCountingSourcingHistory: {
            readonly id: number;
            year: number;
            readonly feedstock: components["schemas"]["FeedStock"];
            readonly origin_country: components["schemas"]["Country"];
            readonly supply_country: components["schemas"]["Country"];
            readonly transit_country: components["schemas"]["Country"];
            metric_tonnes: number;
            raw_material_supplier?: string;
            supplier_certificate_name?: string;
            supplier_certificate?: number | null;
        };
        /**
         * @description * `PENDING` - PENDING
         *     * `INPROGRESS` - INPROGRESS
         *     * `REJECTED` - REJECTED
         *     * `ACCEPTED` - ACCEPTED
         * @enum {string}
         */
        DoubleCountingStatus: DoubleCountingStatus;
        ElecBalance: {
            sector: components["schemas"]["ElecBalanceSectorEnum"];
            /** Format: double */
            readonly initial_balance: number;
            /** Format: double */
            available_balance: number;
            quantity: components["schemas"]["BalanceQuantity"];
            /** Format: double */
            pending_teneur: number;
            /** Format: double */
            declared_teneur: number;
            pending_operations: number;
        };
        /**
         * @description * `ELEC` - ELEC
         * @enum {string}
         */
        ElecBalanceSectorEnum: ElecBalanceSectorEnum;
        ElecOperation: {
            readonly id: number;
            readonly type: string;
            status?: components["schemas"]["ElecOperationStatusEnum"];
            credited_entity: components["schemas"]["ElecOperationEntity"];
            debited_entity: components["schemas"]["ElecOperationEntity"];
            /** Format: double */
            quantity?: number;
            /** Format: date-time */
            readonly created_at: string;
            /** Format: double */
            avoided_emissions: number;
        };
        ElecOperationEntity: {
            id: number;
            name: string;
        };
        ElecOperationInputRequest: {
            type: components["schemas"]["ElecOperationTypeEnum"];
            credited_entity?: number | null;
            debited_entity?: number | null;
            /** Format: double */
            quantity?: number;
        };
        ElecOperationList: {
            readonly id: number;
            readonly type: string;
            status?: components["schemas"]["ElecOperationStatusEnum"];
            credited_entity: components["schemas"]["ElecOperationEntity"];
            debited_entity: components["schemas"]["ElecOperationEntity"];
            /** Format: double */
            quantity?: number;
            /** Format: date-time */
            readonly created_at: string;
        };
        /**
         * @description * `PENDING` - PENDING
         *     * `ACCEPTED` - ACCEPTED
         *     * `REJECTED` - REJECTED
         *     * `CANCELED` - CANCELED
         *     * `DECLARED` - DECLARED
         * @enum {string}
         */
        ElecOperationStatusEnum: PathsApiTiruertElecOperationsGetParametersQueryStatus;
        /**
         * @description * `ACQUISITION_FROM_CPO` - ACQUISITION_FROM_CPO
         *     * `CESSION` - CESSION
         *     * `TENEUR` - TENEUR
         * @enum {string}
         */
        ElecOperationTypeEnum: ElecOperationTypeEnum;
        ElecProvisionCertificate: {
            readonly id: number;
            readonly cpo: components["schemas"]["EntityPreview"];
            source?: components["schemas"]["ElecProvisionCertificateSourceEnum"] | null;
            quarter: components["schemas"]["QuarterEnum"];
            year: number;
            operating_unit: string;
            /** Format: double */
            energy_amount: number;
            /** Format: double */
            remaining_energy_amount: number;
            /** Format: date-time */
            readonly created_at: string | null;
        };
        ElecProvisionCertificateQualicharge: {
            readonly id: number;
            readonly cpo: components["schemas"]["EntityPreview"];
            /** Format: date */
            date_from: string;
            /** Format: date */
            date_to: string;
            year: number;
            operating_unit: string;
            station_id: string;
            /** Format: double */
            energy_amount: number;
            is_controlled_by_qualicharge?: boolean;
            validated_by?: components["schemas"]["ValidatedByEnum"];
            /** Format: date-time */
            readonly created_at: string | null;
        };
        /**
         * @description * `MANUAL` - MANUAL
         *     * `METER_READINGS` - METER_READINGS
         *     * `QUALICHARGE` - QUALICHARGE
         * @enum {string}
         */
        ElecProvisionCertificateSourceEnum: PathsApiElecProvisionCertificatesGetParametersQuerySource;
        ElecTransferAcceptRequest: {
            used_in_tiruert: string;
            /** Format: date */
            consumption_date?: string;
        };
        ElecTransferCertificate: {
            readonly id: number;
            readonly supplier: components["schemas"]["EntityPreview"];
            readonly client: components["schemas"]["EntityPreview"];
            /** Format: date */
            transfer_date: string;
            /** Format: double */
            energy_amount: number;
            status?: components["schemas"]["ElecTransferCertificateStatusEnum"];
            certificate_id: string;
            used_in_tiruert?: boolean;
            /** Format: date */
            consumption_date?: string | null;
        };
        /**
         * @description * `PENDING` - PENDING
         *     * `ACCEPTED` - ACCEPTED
         *     * `REJECTED` - REJECTED
         * @enum {string}
         */
        ElecTransferCertificateStatusEnum: PathsApiSafTicketsGetParametersQueryStatus;
        ElecTransferRejectRequest: {
            comment: string;
        };
        ElecTransferRequest: {
            /** Format: double */
            energy_amount: number;
            client: number;
        };
        EmptyResponse: {
            empty?: string;
        };
        EmptyResponseRequest: {
            empty?: string;
        };
        Entity: {
            readonly id: number;
            name: string;
            entity_type?: components["schemas"]["EntityTypeEnum"];
            has_mac?: boolean;
            has_trading?: boolean;
            has_direct_deliveries?: boolean;
            has_stocks?: boolean;
            preferred_unit?: components["schemas"]["PreferredUnitEnum"];
            legal_name?: string;
            registration_id?: string;
            sustainability_officer_phone_number?: string;
            sustainability_officer?: string;
            registered_address?: string;
            registered_zipcode?: string;
            registered_city?: string;
            registered_country?: number | null;
            activity_description?: string;
            /** Format: uri */
            website?: string;
            vat_number?: string;
            is_enabled?: boolean;
        };
        EntityCertificate: {
            readonly id: number;
            entity: components["schemas"]["Entity"];
            certificate: components["schemas"]["GenericCertificate"];
            has_been_updated?: boolean;
            checked_by_admin?: boolean;
            rejected_by_admin?: boolean;
            /** Format: date-time */
            readonly added_dt: string;
        };
        EntityCompanyRequest: {
            certificate_type?: components["schemas"]["CertificateTypeEnum"];
            certificate_id?: string;
            activity_description?: string;
            entity_type?: components["schemas"]["EntityTypeEnum"];
            name: string;
            legal_name?: string;
            registered_address?: string;
            registered_city?: string;
            registered_country?: string;
            registered_zipcode?: string;
            registration_id?: string;
            sustainability_officer?: string;
            sustainability_officer_email?: string;
            sustainability_officer_phone_number?: string;
            /** Format: uri */
            website?: string;
            vat_number?: string;
        };
        EntityDepot: {
            readonly id: number;
            customs_id?: string;
            name: string;
            city?: string;
            country: components["schemas"]["Pays"];
            site_type?: components["schemas"]["SiteTypeEnum"];
            address?: string;
            postal_code?: string;
            /**
             * Format: double
             * @description Entre 0 et 1
             */
            electrical_efficiency?: number | null;
            /**
             * Format: double
             * @description Entre 0 et 1
             */
            thermal_efficiency?: number | null;
            /**
             * Format: double
             * @description En degrés Celsius
             */
            useful_temperature?: number | null;
            is_enabled?: boolean;
        };
        EntityMetrics: {
            entity: components["schemas"]["UserEntity"];
            users: number;
            requests: number;
            depots: number;
            production_sites: number;
            certificates: number;
            certificates_pending: number;
            double_counting: number;
            double_counting_requests: number;
            charge_points_accepted: number;
            charge_points_pending: number;
            meter_readings_accepted: number;
            meter_readings_pending: number;
        };
        EntityPreview: {
            readonly id: number;
            readonly name: string;
            readonly entity_type: components["schemas"]["EntityTypeEnum"];
            readonly registration_id: string;
        };
        EntityProductionSite: {
            readonly id: number;
            address?: string;
            name: string;
            readonly country: components["schemas"]["Country"];
            /** Format: date */
            date_mise_en_service?: string | null;
            site_siret?: string;
            postal_code?: string;
            manager_name?: string;
            manager_phone?: string;
            manager_email?: string;
            ges_option?: components["schemas"]["GesOptionEnum"];
            eligible_dc?: boolean;
            dc_reference?: string;
            dc_number?: string;
            city?: string;
            readonly certificates: components["schemas"]["GenericCertificate"][];
            readonly inputs: components["schemas"]["FeedStock"][];
            readonly outputs: components["schemas"]["Biofuel"][];
        };
        EntityProductionSiteWrite: {
            address?: string;
            certificates: string[];
            city?: string;
            country_code: string;
            /** Format: date */
            date_mise_en_service?: string | null;
            dc_reference?: string;
            eligible_dc?: boolean;
            ges_option?: components["schemas"]["GesOptionEnum"];
            inputs: string[];
            manager_email?: string;
            manager_name?: string;
            manager_phone?: string;
            name: string;
            outputs: string[];
            postal_code?: string;
            site_siret?: string;
        };
        EntityProductionSiteWriteRequest: {
            address?: string;
            certificates: string[];
            city?: string;
            country_code: string;
            /** Format: date */
            date_mise_en_service?: string | null;
            dc_reference?: string;
            eligible_dc?: boolean;
            ges_option?: components["schemas"]["GesOptionEnum"];
            inputs: string[];
            manager_email?: string;
            manager_name?: string;
            manager_phone?: string;
            name: string;
            outputs: string[];
            postal_code?: string;
            site_siret?: string;
        };
        EntitySite: {
            ownership_type: components["schemas"]["OwnershipTypeEnum"];
            blending_is_outsourced: boolean;
            blender: components["schemas"]["UserEntity"];
            readonly depot: components["schemas"]["EntityDepot"] | null;
            readonly site: components["schemas"]["DepotProductionSite"] | null;
        };
        EntitySummary: {
            readonly id: number;
            readonly name: string;
            readonly entity_type: components["schemas"]["EntityTypeEnum"];
        };
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
         *     * `SAF Trader` - Trader de SAF
         *     * `Producteur de biométhane` - Producteur de biométhane
         * @enum {string}
         */
        EntityTypeEnum: EntityTypeEnum;
        ErrorResponse: {
            message: string;
        };
        /**
         * @description * `ETS_VALUATION` - Valorisation ETS
         *     * `OUTSIDE_ETS` - Hors ETS (volontaire)
         *     * `NOT_CONCERNED` - Non concerné
         * @enum {string}
         */
        EtsStatusEnum: EtsStatusEnum;
        /**
         * @description * `DCA` - DCA
         *     * `AGRIMER` - AGRIMER
         *     * `TIRIB` - TIRIB
         *     * `AIRLINE` - AIRLINE
         *     * `ELEC` - ELEC
         *     * `TRANSFERRED_ELEC` - TRANSFERRED_ELEC
         *     * `BIOFUEL` - BIOFUEL
         * @enum {string}
         */
        ExtAdminPagesEnum: ExtAdminPagesEnum;
        FeedStock: {
            name: string;
            name_en: string;
            code: string;
            category?: components["schemas"]["MPCategoriesEnum"];
            is_double_compte?: boolean;
        };
        FieldData: {
            name: string;
            city: string;
            address: string;
            postal_code: string;
            country: string;
        };
        File: {
            file_name: string;
            errors: components["schemas"]["FileErrors"];
            error_count: number;
            start_year: number;
            production_site: string;
            /** Format: email */
            producer_email: string;
            production: components["schemas"]["DoubleCountingProduction"][];
            sourcing: components["schemas"]["DoubleCountingSourcing"][];
            sourcing_history: components["schemas"]["DoubleCountingSourcingHistory"][];
            production_history: components["schemas"]["DoubleCountingProductionHistory"][];
            readonly has_dechets_industriels: boolean;
        };
        FileError: {
            error: string;
            is_blocking: boolean;
            line_number: number;
            line_merged: string;
            meta: {
                [key: string]: unknown;
            };
        };
        FileErrors: {
            sourcing_forecast: components["schemas"]["FileError"][];
            sourcing_history: components["schemas"]["FileError"][];
            production: components["schemas"]["FileError"][];
            production_history: components["schemas"]["FileError"][];
            global_errors: components["schemas"]["FileError"][];
        };
        /**
         * @description * `EXCEL` - EXCEL
         *     * `EXTRA` - EXTRA
         *     * `DECISION` - DECISION
         * @enum {string}
         */
        FileTypeEnum: FileTypeEnum;
        GenericCertificate: {
            certificate_id: string;
            certificate_type: components["schemas"]["CertificateTypeEnum"];
            certificate_holder: string;
            certificate_issuer?: string | null;
            address?: string | null;
            /** Format: date */
            valid_from: string;
            /** Format: date */
            valid_until: string;
            download_link?: string | null;
            scope?: unknown;
            input?: unknown;
            output?: unknown;
        };
        /**
         * @description * `Default` - Valeurs par défaut
         *     * `Actual` - Valeurs réelles
         *     * `NUTS2` - Valeurs NUTS2
         * @enum {string}
         */
        GesOptionEnum: GesOptionEnum;
        GrantAccessRequest: {
            request_id: number;
        };
        GroupAssignmentResponse: {
            assigned_tickets_count: number;
        };
        /**
         * @description * `TOTAL` - Totale
         *     * `PARTIAL` - Partielle
         * @enum {string}
         */
        HygienizationExemptionTypeEnum: HygienizationExemptionTypeEnum;
        /**
         * @description * `AUTHORIZATION` - Autorisation
         *     * `REGISTRATION` - Enregistrement
         *     * `DECLARATION_PERIODIC_CONTROLS` - Déclaration (avec contrôles périodiques)
         * @enum {string}
         */
        IcpeRegimeEnum: IcpeRegimeEnum;
        /**
         * @description * `LIVESTOCK_EFFLUENTS` - Effluents d'élevage
         *     * `PRIMARY_CROPS` - Culture principale
         *     * `INTERMEDIATE_CROPS` - Culture intermédiaire
         *     * `CIVE` - CIVE
         *     * `IAA_WASTE_RESIDUES` - Déchets/Résidus d'IAA
         * @enum {string}
         */
        InputCategoryEnum: PathsApiBiomethaneSupplyInputGetParametersQueryCategory;
        /**
         * @description * `INSTALLATION_CATEGORY_1` - INSTALLATION_CATEGORY_1
         *     * `INSTALLATION_CATEGORY_2` - INSTALLATION_CATEGORY_2
         *     * `INSTALLATION_CATEGORY_3` - INSTALLATION_CATEGORY_3
         * @enum {string}
         */
        InstallationCategoryEnum: InstallationCategoryEnum;
        /**
         * @description * `BIOGAS_PRODUCTION_FLOWMETER` - Débitmètre dédié à la production de biogaz
         *     * `PURIFICATION_FLOWMETER` - Débitmètre dédié au volume de biogaz traité en épuration
         *     * `FLARING_FLOWMETER` - Débitmètre dédié au volume de biogaz torché
         *     * `HEATING_FLOWMETER` - Débitmètre dédié au volume de biogaz ou biométhane utilisé pour le chauffage du digesteur
         *     * `PURIFICATION_ELECTRICAL_METER` - Compteur dédié à la consommation électrique au système d'épuration et traitement des évents
         *     * `GLOBAL_ELECTRICAL_METER` - Compteur dédié à la consommation électrique de l'ensemble de l'unité de production
         * @enum {string}
         */
        InstalledMetersEnum: InstalledMetersEnum;
        InviteUserRequest: {
            /** Format: email */
            email: string;
            role: string;
        };
        /**
         * @description * `DRAFT` - DRAFT
         *     * `PENDING` - PENDING
         *     * `ACCEPTED` - ACCEPTED
         *     * `REJECTED` - REJECTED
         *     * `FROZEN` - FROZEN
         *     * `DELETED` - DELETED
         * @enum {string}
         */
        LotStatusEnum: LotStatusEnum;
        /**
         * @description * `CONV` - Conventionnel
         *     * `ANN-IX-A` - ANNEXE IX-A
         *     * `ANN-IX-B` - ANNEXE IX-B
         *     * `TALLOL` - Tallol
         *     * `OTHER` - Autre
         *     * `EP2AM` - EP2AM
         * @enum {string}
         */
        MPCategoriesEnum: PathsApiTiruertOperationsGetParametersQueryCustoms_category;
        MainObjective: {
            /** Format: double */
            available_balance: number;
            /** Format: double */
            target: number;
            /** Format: double */
            pending_teneur: number;
            /** Format: double */
            declared_teneur: number;
            unit: string;
            penalty: number;
            /** Format: double */
            target_percent: number;
            /** Format: double */
            energy_basis: number;
        };
        /**
         * @description * `CONCEPTION` - Conception
         *     * `MAINTENANCE` - Entretien/Maintenance
         *     * `BIOLOGICAL` - Biologique
         *     * `ACCIDENT` - Accident deversement
         *     * `PURIFIER` - Épurateur
         *     * `INJECTION_POST` - Poste d'injection (autre que problématiques de saturation des réseaux)
         *     * `INPUTS` - Intrants
         *     * `OTHER` - Autres (à préciser)
         * @enum {string}
         */
        MalfunctionTypesEnum: MalfunctionTypesEnum;
        /**
         * @description * `DRY` - Sèche
         *     * `WET` - Brute
         * @enum {string}
         */
        MaterialUnitEnum: MaterialUnitEnum;
        /**
         * @description * `CONTINUOUS_INFINITELY_MIXED` - Continu (infiniment mélangé)
         *     * `PLUG_FLOW_SEMI_CONTINUOUS` - En piston (semi-continu)
         *     * `BATCH_SILOS` - En silos (batch)
         * @enum {string}
         */
        MethanizationProcessEnum: MethanizationProcessEnum;
        MonthlyReportDataRequest: {
            month: number;
            /** Format: double */
            injected_volume_nm3: number;
            /** Format: double */
            average_monthly_flow_nm3_per_hour: number;
            /** Format: double */
            injection_hours: number;
        };
        NavStats: {
            total_pending_action_for_admin?: number;
            pending_draft_lots?: number;
            in_pending_lots?: number;
            doublecount_agreement_pending?: number;
            charge_point_registration_pending?: number;
            metering_reading_pending?: number;
            pending_transfer_certificates?: number;
            audits?: number;
            tickets?: number;
        };
        /**
         * @description * `TRANSPORT` - Transport
         *     * `DISTRIBUTION` - Dristribution
         * @enum {string}
         */
        NetworkTypeEnum: NetworkTypeEnum;
        NotificationRequest: {
            notification_ids: number[];
        };
        Objective: {
            /** Format: double */
            target_mj: number;
            target_type: string;
            penalty: number;
            /** Format: double */
            target_percent: number;
        };
        ObjectiveCategory: {
            code: components["schemas"]["MPCategoriesEnum"];
            /** Format: double */
            pending_teneur: number;
            /** Format: double */
            declared_teneur: number;
            /** Format: double */
            available_balance: number;
            unit: string;
            objective: components["schemas"]["Objective"];
        };
        ObjectiveOutput: {
            main: components["schemas"]["MainObjective"];
            sectors: components["schemas"]["ObjectiveSector"][];
            categories: components["schemas"]["ObjectiveCategory"][];
        };
        ObjectiveSector: {
            code: components["schemas"]["ObjectiveSectorCodeEnum"];
            /** Format: double */
            pending_teneur: number;
            /** Format: double */
            declared_teneur: number;
            /** Format: double */
            available_balance: number;
            unit: string;
            objective: components["schemas"]["Objective"];
        };
        /**
         * @description * `ESSENCE` - ESSENCE
         *     * `GAZOLE` - GAZOLE
         *     * `CARBURÉACTEUR` - CARBURÉACTEUR
         * @enum {string}
         */
        ObjectiveSectorCodeEnum: PathsApiTiruertOperationsGetParametersQuerySector;
        Operation: {
            readonly id: number;
            readonly type: string;
            status?: components["schemas"]["OperationStatusEnum"];
            readonly sector: string;
            customs_category?: components["schemas"]["MPCategoriesEnum"];
            readonly biofuel: string;
            /** Format: double */
            renewable_energy_share: number;
            credited_entity: components["schemas"]["OperationEntity"];
            debited_entity: components["schemas"]["OperationEntity"];
            /**  entity */
            readonly _entity: string;
            from_depot: components["schemas"]["OperationDepot"];
            to_depot: components["schemas"]["OperationDepot"];
            /**  depot */
            readonly _depot: string;
            readonly export_country: components["schemas"]["Country"];
            export_recipient?: string;
            /** Format: date-time */
            readonly created_at: string;
            /** Format: date */
            validation_date?: string | null;
            durability_period?: string | null;
            /** Format: double */
            readonly quantity: number;
            /** Format: double */
            readonly quantity_mj: number;
            /** Format: double */
            readonly avoided_emissions: number;
            readonly unit: string;
            details?: components["schemas"]["OperationDetail"][];
        };
        OperationCorrectionRequest: {
            /** Format: double */
            correction_volume: number;
        };
        OperationDepot: {
            id: number;
            name: string;
        };
        OperationDetail: {
            lot: number;
            /** Format: double */
            volume?: number;
            /** Format: double */
            emission_rate_per_mj?: number;
        };
        OperationEntity: {
            id: number;
            name: string;
        };
        OperationInputRequest: {
            type: components["schemas"]["OperationTypeEnum"];
            customs_category: components["schemas"]["MPCategoriesEnum"];
            biofuel: number | null;
            credited_entity?: number | null;
            debited_entity: number | null;
            from_depot?: number | null;
            to_depot?: number | null;
            export_country?: string | null;
            export_recipient?: string;
            lots: components["schemas"]["OperationLotRequest"][];
            status?: components["schemas"]["OperationStatusEnum"];
        };
        OperationList: {
            readonly id: number;
            readonly type: string;
            status?: components["schemas"]["OperationStatusEnum"];
            readonly sector: string;
            customs_category?: components["schemas"]["MPCategoriesEnum"];
            readonly biofuel: string;
            /** Format: double */
            renewable_energy_share: number;
            credited_entity: components["schemas"]["OperationEntity"];
            debited_entity: components["schemas"]["OperationEntity"];
            /**  entity */
            readonly _entity: string;
            from_depot: components["schemas"]["OperationDepot"];
            to_depot: components["schemas"]["OperationDepot"];
            /**  depot */
            readonly _depot: string;
            export_country?: number | null;
            /** Format: date-time */
            readonly created_at: string;
            /** Format: double */
            readonly quantity: number;
            readonly unit: string;
            details?: components["schemas"]["OperationDetail"][];
        };
        OperationLotRequest: {
            id: number;
            /** Format: double */
            volume: number;
            /** Format: double */
            emission_rate_per_mj: number;
        };
        /**
         * @description * `PENDING` - PENDING
         *     * `ACCEPTED` - ACCEPTED
         *     * `REJECTED` - REJECTED
         *     * `CANCELED` - CANCELED
         *     * `DECLARED` - DECLARED
         *     * `CORRECTED` - CORRECTED
         *     * `VALIDATED` - VALIDATED
         *     * `DRAFT` - DRAFT
         * @enum {string}
         */
        OperationStatusEnum: PathsApiTiruertOperationsGetParametersQueryStatus;
        /**
         * @description * `INCORPORATION` - INCORPORATION
         *     * `CESSION` - CESSION
         *     * `TENEUR` - TENEUR
         *     * `LIVRAISON_DIRECTE` - LIVRAISON_DIRECTE
         *     * `MAC_BIO` - MAC_BIO
         *     * `EXPORTATION` - EXPORTATION
         *     * `EXPEDITION` - EXPEDITION
         *     * `DEVALUATION` - DEVALUATION
         *     * `CUSTOMS_CORRECTION` - CUSTOMS_CORRECTION
         *     * `TRANSFERT` - TRANSFERT
         * @enum {string}
         */
        OperationTypeEnum: OperationTypeEnum;
        OperationalUnitRequest: {
            code: string;
            /** Format: date */
            from: string;
            /** Format: date */
            to: string;
            stations?: components["schemas"]["StationRequest"][];
        };
        OtpResponse: {
            valid_until: string;
        };
        /**
         * @description * `OWN` - Propre
         *     * `THIRD_PARTY` - Tiers
         *     * `PROCESSING` - Processing
         * @enum {string}
         */
        OwnershipTypeEnum: OwnershipTypeEnum;
        PaginatedBalanceResponseList: {
            /** @example 123 */
            count: number;
            /**
             * Format: uri
             * @example http://api.example.org/accounts/?page=4
             */
            next?: string | null;
            /**
             * Format: uri
             * @example http://api.example.org/accounts/?page=2
             */
            previous?: string | null;
            results: components["schemas"]["BalanceResponse"][];
            total_quantity?: number;
        };
        PaginatedBiomethaneContractAmendmentList: {
            /** @example 123 */
            count: number;
            /**
             * Format: uri
             * @example http://api.example.org/accounts/?page=4
             */
            next?: string | null;
            /**
             * Format: uri
             * @example http://api.example.org/accounts/?page=2
             */
            previous?: string | null;
            results: components["schemas"]["BiomethaneContractAmendment"][];
        };
        PaginatedBiomethaneSupplyInputList: {
            /** @example 123 */
            count: number;
            /**
             * Format: uri
             * @example http://api.example.org/accounts/?page=4
             */
            next?: string | null;
            /**
             * Format: uri
             * @example http://api.example.org/accounts/?page=2
             */
            previous?: string | null;
            results: components["schemas"]["BiomethaneSupplyInput"][];
            annual_volumes_in_t?: number;
        };
        PaginatedElecBalanceList: {
            /** @example 123 */
            count: number;
            /**
             * Format: uri
             * @example http://api.example.org/accounts/?page=4
             */
            next?: string | null;
            /**
             * Format: uri
             * @example http://api.example.org/accounts/?page=2
             */
            previous?: string | null;
            results: components["schemas"]["ElecBalance"][];
            total_quantity?: number;
        };
        PaginatedElecOperationListList: {
            /** @example 123 */
            count: number;
            /**
             * Format: uri
             * @example http://api.example.org/accounts/?page=4
             */
            next?: string | null;
            /**
             * Format: uri
             * @example http://api.example.org/accounts/?page=2
             */
            previous?: string | null;
            results: components["schemas"]["ElecOperationList"][];
            total_quantity?: number;
        };
        PaginatedElecProvisionCertificateList: {
            /** @example 123 */
            count: number;
            /**
             * Format: uri
             * @example http://api.example.org/accounts/?page=4
             */
            next?: string | null;
            /**
             * Format: uri
             * @example http://api.example.org/accounts/?page=2
             */
            previous?: string | null;
            results: components["schemas"]["ElecProvisionCertificate"][];
            available_energy?: number;
        };
        PaginatedElecProvisionCertificateQualichargeList: {
            /** @example 123 */
            count: number;
            /**
             * Format: uri
             * @example http://api.example.org/accounts/?page=4
             */
            next?: string | null;
            /**
             * Format: uri
             * @example http://api.example.org/accounts/?page=2
             */
            previous?: string | null;
            results: components["schemas"]["ElecProvisionCertificateQualicharge"][];
            total_quantity?: number;
        };
        PaginatedElecTransferCertificateList: {
            /** @example 123 */
            count: number;
            /**
             * Format: uri
             * @example http://api.example.org/accounts/?page=4
             */
            next?: string | null;
            /**
             * Format: uri
             * @example http://api.example.org/accounts/?page=2
             */
            previous?: string | null;
            results: components["schemas"]["ElecTransferCertificate"][];
            transferred_energy?: number;
        };
        PaginatedEntityPreviewList: {
            /** @example 123 */
            count: number;
            /**
             * Format: uri
             * @example http://api.example.org/accounts/?page=4
             */
            next?: string | null;
            /**
             * Format: uri
             * @example http://api.example.org/accounts/?page=2
             */
            previous?: string | null;
            results: components["schemas"]["EntityPreview"][];
        };
        PaginatedEntityProductionSiteList: {
            /** @example 123 */
            count: number;
            /**
             * Format: uri
             * @example http://api.example.org/accounts/?page=4
             */
            next?: string | null;
            /**
             * Format: uri
             * @example http://api.example.org/accounts/?page=2
             */
            previous?: string | null;
            results: components["schemas"]["EntityProductionSite"][];
        };
        PaginatedOperationListList: {
            /** @example 123 */
            count: number;
            /**
             * Format: uri
             * @example http://api.example.org/accounts/?page=4
             */
            next?: string | null;
            /**
             * Format: uri
             * @example http://api.example.org/accounts/?page=2
             */
            previous?: string | null;
            results: components["schemas"]["OperationList"][];
            total_quantity?: number;
        };
        PaginatedSafTicketPreviewList: {
            /** @example 123 */
            count: number;
            /**
             * Format: uri
             * @example http://api.example.org/accounts/?page=4
             */
            next?: string | null;
            /**
             * Format: uri
             * @example http://api.example.org/accounts/?page=2
             */
            previous?: string | null;
            results: components["schemas"]["SafTicketPreview"][];
            total_volume?: number;
        };
        PaginatedSafTicketSourcePreviewList: {
            /** @example 123 */
            count: number;
            /**
             * Format: uri
             * @example http://api.example.org/accounts/?page=4
             */
            next?: string | null;
            /**
             * Format: uri
             * @example http://api.example.org/accounts/?page=2
             */
            previous?: string | null;
            results: components["schemas"]["SafTicketSourcePreview"][];
            total_available_volume?: number;
        };
        PatchedBiomethaneDigestateStorageInputRequest: {
            type?: string;
            /** Format: double */
            capacity?: number;
            has_cover?: boolean;
            has_biogas_recovery?: boolean;
        };
        PatchedBiomethaneSupplyInputCreateRequest: {
            source?: components["schemas"]["BiomethaneSupplyInputSourceEnum"];
            crop_type?: components["schemas"]["CropTypeEnum"];
            input_category?: components["schemas"]["InputCategoryEnum"];
            material_unit?: components["schemas"]["MaterialUnitEnum"];
            origin_country?: string;
            /** Format: double */
            dry_matter_ratio_percent?: number | null;
            /** Format: double */
            volume?: number;
            /** Format: double */
            average_weighted_distance_km?: number | null;
            /** Format: double */
            maximum_distance_km?: number | null;
            input_type?: string;
            origin_department?: string | null;
        };
        PatchedElecOperationUpdateRequest: {
            type?: components["schemas"]["ElecOperationTypeEnum"];
            credited_entity?: number | null;
            debited_entity?: number | null;
            /** Format: double */
            quantity?: number;
        };
        PatchedEntityProductionSiteWriteRequest: {
            address?: string;
            certificates?: string[];
            city?: string;
            country_code?: string;
            /** Format: date */
            date_mise_en_service?: string | null;
            dc_reference?: string;
            eligible_dc?: boolean;
            ges_option?: components["schemas"]["GesOptionEnum"];
            inputs?: string[];
            manager_email?: string;
            manager_name?: string;
            manager_phone?: string;
            name?: string;
            outputs?: string[];
            postal_code?: string;
            site_siret?: string;
        };
        PatchedOperationUpdateRequest: {
            to_depot?: number | null;
            status?: components["schemas"]["OperationStatusEnum"];
        };
        Pays: {
            code_pays: string;
            name: string;
            name_en: string;
            is_in_europe?: boolean;
        };
        /**
         * @description * `l` - litres
         *     * `kg` - kg
         *     * `MJ` - MJ
         * @enum {string}
         */
        PreferredUnitEnum: PathsApiTiruertOperationsGetParametersQueryUnit;
        /**
         * @description * `LIQUID_PROCESS` - Voie liquide
         *     * `DRY_PROCESS` - Voie sèche
         * @enum {string}
         */
        ProcessTypeEnum: ProcessTypeEnum;
        ProductionSite: {
            readonly id: number;
            readonly producer: components["schemas"]["Entity"];
            name: string;
            readonly country: components["schemas"]["Country"];
            /** Format: date */
            date_mise_en_service?: string | null;
            ges_option?: components["schemas"]["GesOptionEnum"];
            eligible_dc?: boolean;
            dc_reference?: string;
            site_siret?: string;
            address?: string;
            city?: string;
            postal_code?: string;
            gps_coordinates?: string | null;
            manager_name?: string;
            manager_phone?: string;
            manager_email?: string;
        };
        ProductionSiteCertificateSertificate: {
            readonly type: string;
            readonly certificate_id: string;
        };
        ProvisionCertificateBulkRequest: {
            entity: string;
            siren: string;
            operational_units: components["schemas"]["OperationalUnitRequest"][];
        };
        ProvisionCertificateUpdateBulkRequest: {
            certificate_ids: number[];
            validated_by: components["schemas"]["ValidatedByEnum"];
        };
        /**
         * @description * `1` - T1
         *     * `2` - T2
         *     * `3` - T3
         *     * `4` - T4
         * @enum {integer}
         */
        QuarterEnum: PathsApiElecProvisionCertificatesGetParametersQueryQuarter;
        RegistrationCountry: {
            name: string;
            name_en: string;
            code_pays: string;
            is_in_europe: boolean;
        };
        RejectCertificateRequest: {
            entity_certificate_id: number;
        };
        RejectDoubleCountingRequest: {
            dca_id: number;
        };
        RequestAccessRequest: {
            comment?: string;
            role: string;
            entity_id: number;
        };
        RequestEmailChangeError: {
            /** @description Message d'erreur général */
            message?: string;
            /** @description Détails des erreurs de validation */
            errors?: string;
        };
        RequestEmailChangeRequest: {
            /** Format: email */
            new_email: string;
            password: string;
        };
        RequestEmailChangeSuccess: {
            /** @default otp_sent */
            status: string;
        };
        RequestPasswordResetRequest: {
            username: string;
        };
        ResetPasswordRequest: {
            uidb64: string;
            token: string;
            /** Mot de passe */
            password1: string;
            /** Confirmation du mot de passe */
            password2: string;
        };
        Response: {
            status: string;
        };
        ResponseData: {
            company_preview: components["schemas"]["CompanyPreview"];
            warning?: components["schemas"]["Warning"];
        };
        ResponseSuccess: {
            status: string;
        };
        RevokeAccessRequest: {
            entity_id: number;
        };
        RevokeUserRequest: {
            /** Format: email */
            email: string;
        };
        /**
         * @description * `RO` - Lecture Seule
         *     * `RW` - Lecture/Écriture
         *     * `ADMIN` - Administrateur
         *     * `AUDITOR` - Auditeur
         * @enum {string}
         */
        RoleEnum: RoleEnum;
        SafAssignedTicket: {
            readonly id: number;
            carbure_id?: string | null;
            readonly client: string;
            /** Format: date */
            agreement_date?: string | null;
            /** Format: double */
            volume: number;
            status?: components["schemas"]["saf.filters.TicketFilter.status"];
            /** Format: date-time */
            readonly created_at: string | null;
            assignment_period: number;
        };
        SafParentLot: {
            readonly id: number;
            carbure_id?: string;
        };
        SafParentTicket: {
            readonly id: number;
            carbure_id?: string | null;
        };
        SafRelatedTicketSource: {
            readonly id: number;
            carbure_id?: string | null;
            /** Format: double */
            total_volume: number;
            /** Format: double */
            assigned_volume: number;
        };
        SafTicket: {
            readonly id: number;
            carbure_id?: string | null;
            year: number;
            assignment_period: number;
            status?: components["schemas"]["saf.filters.TicketFilter.status"];
            /** Format: date */
            agreement_date?: string | null;
            readonly supplier: string;
            readonly client: string;
            /** Format: double */
            volume: number;
            readonly feedstock: components["schemas"]["FeedStock"];
            readonly biofuel: components["schemas"]["Biofuel"];
            readonly country_of_origin: components["schemas"]["Country"];
            /** Format: double */
            ghg_reduction?: number;
            consumption_type?: components["schemas"]["ConsumptionTypeEnum"] | null;
            ets_status?: components["schemas"]["EtsStatusEnum"] | null;
            /** Format: date-time */
            readonly created_at: string | null;
            readonly reception_airport: components["schemas"]["Airport"];
            free_field?: string | null;
            agreement_reference?: string | null;
            readonly carbure_producer: components["schemas"]["EntityPreview"];
            unknown_producer?: string | null;
            readonly carbure_production_site: components["schemas"]["ProductionSite"];
            unknown_production_site?: string | null;
            /** Format: date */
            production_site_commissioning_date?: string | null;
            /** Format: double */
            eec?: number;
            /** Format: double */
            el?: number;
            /** Format: double */
            ep?: number;
            /** Format: double */
            etd?: number;
            /** Format: double */
            eu?: number;
            /** Format: double */
            esca?: number;
            /** Format: double */
            eccs?: number;
            /** Format: double */
            eccr?: number;
            /** Format: double */
            eee?: number;
            /** Format: double */
            ghg_total?: number;
            client_comment?: string | null;
            readonly parent_ticket_source: components["schemas"]["SafRelatedTicketSource"];
            shipping_method?: components["schemas"]["ShippingMethodEnum"] | null;
            readonly child_ticket_sources: components["schemas"]["SafRelatedTicketSource"][];
            origin_lot?: components["schemas"]["SafParentLot"];
            origin_lot_site?: components["schemas"]["Site"];
        };
        SafTicketPreview: {
            readonly id: number;
            carbure_id?: string | null;
            year: number;
            assignment_period: number;
            status?: components["schemas"]["saf.filters.TicketFilter.status"];
            /** Format: date */
            agreement_date?: string | null;
            readonly supplier: string;
            readonly client: string;
            /** Format: double */
            volume: number;
            readonly feedstock: components["schemas"]["FeedStock"];
            readonly biofuel: components["schemas"]["Biofuel"];
            readonly country_of_origin: components["schemas"]["Country"];
            /** Format: double */
            ghg_reduction?: number;
            consumption_type?: components["schemas"]["ConsumptionTypeEnum"] | null;
            ets_status?: components["schemas"]["EtsStatusEnum"] | null;
            /** Format: date-time */
            readonly created_at: string | null;
            readonly reception_airport: components["schemas"]["Airport"];
        };
        SafTicketSource: {
            readonly id: number;
            carbure_id?: string | null;
            year: number;
            delivery_period: number;
            /** Format: date-time */
            readonly created_at: string | null;
            /** Format: double */
            total_volume: number;
            /** Format: double */
            assigned_volume: number;
            readonly feedstock: components["schemas"]["FeedStock"];
            readonly biofuel: components["schemas"]["Biofuel"];
            readonly country_of_origin: components["schemas"]["Country"];
            /** Format: double */
            ghg_reduction?: number;
            readonly assigned_tickets: components["schemas"]["SafAssignedTicket"][];
            parent_lot?: components["schemas"]["CarbureLotPublic"];
            parent_ticket?: components["schemas"]["SafParentTicket"];
            readonly added_by: components["schemas"]["EntityPreview"];
            readonly carbure_producer: components["schemas"]["EntityPreview"];
            unknown_producer?: string | null;
            readonly carbure_production_site: components["schemas"]["ProductionSite"];
            unknown_production_site?: string | null;
            /** Format: date */
            production_site_commissioning_date?: string | null;
            /** Format: double */
            eec?: number;
            /** Format: double */
            el?: number;
            /** Format: double */
            ep?: number;
            /** Format: double */
            etd?: number;
            /** Format: double */
            eu?: number;
            /** Format: double */
            esca?: number;
            /** Format: double */
            eccs?: number;
            /** Format: double */
            eccr?: number;
            /** Format: double */
            eee?: number;
            /** Format: double */
            ghg_total?: number;
            origin_lot?: components["schemas"]["SafParentLot"];
            origin_lot_site?: components["schemas"]["Site"];
        };
        SafTicketSourceAssignment: {
            client_id: number;
            /** Format: double */
            volume: number;
            agreement_reference?: string;
            agreement_date?: string;
            free_field?: string | null;
            assignment_period: number;
            reception_airport?: number | null;
            consumption_type?: string | null;
            shipping_method?: string | null;
        };
        SafTicketSourceAssignmentRequest: {
            client_id: number;
            /** Format: double */
            volume: number;
            agreement_reference?: string;
            agreement_date?: string;
            free_field?: string | null;
            assignment_period: number;
            reception_airport?: number | null;
            consumption_type?: string | null;
            shipping_method?: string | null;
        };
        SafTicketSourceGroupAssignmentRequest: {
            client_id: number;
            /** Format: double */
            volume: number;
            agreement_reference?: string;
            agreement_date?: string;
            free_field?: string | null;
            assignment_period: number;
            reception_airport?: number | null;
            consumption_type?: string | null;
            shipping_method?: string | null;
            ticket_sources_ids: number[];
        };
        SafTicketSourcePreview: {
            readonly id: number;
            carbure_id?: string | null;
            year: number;
            delivery_period: number;
            /** Format: date-time */
            readonly created_at: string | null;
            /** Format: double */
            total_volume: number;
            /** Format: double */
            assigned_volume: number;
            readonly feedstock: components["schemas"]["FeedStock"];
            readonly biofuel: components["schemas"]["Biofuel"];
            readonly country_of_origin: components["schemas"]["Country"];
            /** Format: double */
            ghg_reduction?: number;
            readonly assigned_tickets: components["schemas"]["SafAssignedTicket"][];
            readonly parent_lot: components["schemas"]["SafParentLot"];
            parent_ticket?: components["schemas"]["SafParentTicket"];
            readonly added_by: components["schemas"]["EntityPreview"];
        };
        SeachCompanyRequest: {
            registration_id: string;
        };
        SetDefaultCertificateRequest: {
            certificate_id: string;
        };
        /**
         * @description * `PIPELINE` - PIPELINE
         *     * `TRUCK` - TRUCK
         *     * `TRAIN` - TRAIN
         *     * `BARGE` - BARGE
         * @enum {string}
         */
        ShippingMethodEnum: ShippingMethodEnum;
        SimulationInputRequest: {
            customs_category: components["schemas"]["MPCategoriesEnum"];
            biofuel: number | null;
            debited_entity: number | null;
            /** Format: double */
            target_volume: number;
            /** Format: double */
            target_emission: number;
            max_n_batches?: number;
            enforced_volumes?: number[];
            unit?: string;
            from_depot?: number | null;
            /** Format: double */
            ges_bound_min?: number;
            /** Format: double */
            ges_bound_max?: number;
        };
        SimulationLotOutput: {
            lot_id: number;
            /** Format: decimal */
            volume: string;
            /** Format: double */
            emission_rate_per_mj: number;
        };
        SimulationMinMaxInputRequest: {
            customs_category: components["schemas"]["MPCategoriesEnum"];
            biofuel: number | null;
            debited_entity: number | null;
            /** Format: double */
            target_volume: number;
            unit?: string;
            from_depot?: number | null;
            /** Format: double */
            ges_bound_min?: number;
            /** Format: double */
            ges_bound_max?: number;
        };
        SimulationMinMaxOutput: {
            /** Format: double */
            min_avoided_emissions: number;
            /** Format: double */
            max_avoided_emissions: number;
        };
        SimulationOutput: {
            selected_lots: components["schemas"]["SimulationLotOutput"][];
            /** Format: double */
            fun: number;
        };
        Site: {
            id: number;
            name: string;
        };
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
        SiteTypeEnum: SiteTypeEnum;
        /**
         * @description * `DIRECT_SPREADING` - Épandage direct
         *     * `SPREADING_VIA_PROVIDER` - Épandage via un prestataire
         *     * `TRANSFER` - Cession
         *     * `SALE` - Vente
         * @enum {string}
         */
        SpreadingManagementMethodsEnum: SpreadingManagementMethodsEnum;
        StationRequest: {
            id: string;
            /** Format: double */
            energy: number;
            is_controlled: boolean;
        };
        StatsResponse: {
            metabase_iframe_url: string;
        };
        /**
         * @description * `2011` - 2011
         *     * `2020` - 2020
         *     * `2021` - 2021
         *     * `2023` - 2023
         * @enum {string}
         */
        TariffReferenceEnum: TariffReferenceEnum;
        ToggleElecRequest: {
            /** @default false */
            has_elec: boolean;
        };
        ToggleRFCRequest: {
            /** @default false */
            has_mac: boolean;
        };
        ToggleStocksRequest: {
            /** @default false */
            has_stocks: boolean;
        };
        ToggleTradingRequest: {
            /** @default false */
            has_trading: boolean;
        };
        TokenObtainPair: {
            readonly access: string;
            readonly refresh: string;
        };
        TokenObtainPairRequest: {
            email: string;
            password: string;
        };
        TokenRefresh: {
            readonly access: string;
        };
        TokenRefreshRequest: {
            refresh: string;
        };
        /**
         * @description * `CMAX_PAP_UPDATE` - CMAX_PAP_UPDATE
         *     * `CMAX_ANNUALIZATION` - CMAX_ANNUALIZATION
         *     * `PRODUCER_BUYER_INFO_CHANGE` - PRODUCER_BUYER_INFO_CHANGE
         * @enum {string}
         */
        TrackedAmendmentTypesEnum: TrackedAmendmentTypesEnum;
        /**
         * @description * `DAU` - DAU
         *     * `DAE` - DAE
         *     * `DSA` - DSA
         *     * `DSAC` - DSAC
         *     * `DSP` - DSP
         *     * `OTHER` - OTHER
         * @enum {string}
         */
        TransportDocumentTypeEnum: TransportDocumentTypeEnum;
        UnitRequest: {
            /** @default l */
            unit: components["schemas"]["PreferredUnitEnum"];
        };
        /**
         * @description * `AGRICULTURAL_AUTONOMOUS` - Agricole autonome
         *     * `AGRICULTURAL_TERRITORIAL` - Agricole territorial
         *     * `INDUSTRIAL_TERRITORIAL` - Industriel territorial
         *     * `HOUSEHOLD_WASTE_BIOWASTE` - Déchets ménagers et biodéchets
         *     * `ISDND` - ISDND
         * @enum {string}
         */
        UnitTypeEnum: UnitTypeEnum;
        UpdateCertificateRequest: {
            old_certificate_id: string;
            old_certificate_type: string;
            new_certificate_id: string;
            new_certificate_type: string;
        };
        UpdateEntityInfoRequest: {
            activity_description?: string;
            legal_name?: string;
            registered_address?: string;
            registered_city?: string;
            registered_country_code?: string;
            registered_zipcode?: string;
            registration_id?: string;
            sustainability_officer?: string;
            /** Format: email */
            sustainability_officer_email?: string;
            sustainability_officer_phone_number?: string;
            vat_number?: string;
            /** Format: uri */
            website?: string;
        };
        UpdateRightsRequestsRequest: {
            id: number;
            status: components["schemas"]["UserRightsRequestsStatusEnum"];
        };
        UpdateUserRoleRequest: {
            request_id: number;
            role: string;
        };
        UpdatedQuotasRequest: {
            approved_quotas: number[][];
        };
        /** @description Serializer for creating new users. Includes required fields
         *     and repeated password validation. */
        UserCreation: {
            /**
             * Adresse électronique
             * Format: email
             */
            email: string;
            /** Nom */
            name: string;
        };
        /** @description Serializer for creating new users. Includes required fields
         *     and repeated password validation. */
        UserCreationRequest: {
            /**
             * Adresse électronique
             * Format: email
             */
            email: string;
            /** Nom */
            name: string;
            /** Mot de passe */
            password1: string;
            /** Confirmation du mot de passe */
            password2: string;
        };
        UserEntity: {
            readonly id: number;
            readonly name: string;
            readonly is_enabled: boolean;
            readonly entity_type: components["schemas"]["EntityTypeEnum"];
            readonly has_mac: boolean;
            readonly has_trading: boolean;
            readonly has_direct_deliveries: boolean;
            readonly has_stocks: boolean;
            readonly legal_name: string;
            readonly registration_id: string;
            readonly sustainability_officer: string;
            readonly sustainability_officer_phone_number: string;
            readonly sustainability_officer_email: string;
            readonly registered_address: string;
            readonly registered_zipcode: string;
            readonly registered_city: string;
            registered_country?: components["schemas"]["Country"];
            readonly default_certificate: string | null;
            readonly preferred_unit: components["schemas"]["PreferredUnitEnum"];
            readonly has_saf: boolean;
            readonly has_elec: boolean;
            readonly activity_description: string;
            /** Format: uri */
            readonly website: string;
            readonly vat_number: string;
            readonly ext_admin_pages: components["schemas"]["ExtAdminPagesEnum"][];
            readonly is_tiruert_liable: boolean;
            readonly accise_number: string;
            readonly is_red_ii: boolean;
        };
        UserLoginRequest: {
            username: string;
            password: string;
        };
        /** @description A serializer for re-sending the user activation email. Includes email field only. */
        UserResendActivationLinkRequest: {
            /**
             * Courriel
             * Format: email
             */
            email: string;
        };
        UserRights: {
            readonly name: string;
            /** Format: email */
            readonly email: string;
            entity: components["schemas"]["UserEntity"];
            role?: components["schemas"]["RoleEnum"];
            /** Format: date-time */
            expiration_date?: string | null;
        };
        UserRightsRequests: {
            readonly id: number;
            readonly user: string[];
            entity: components["schemas"]["EntitySummary"];
            /** Format: date-time */
            readonly date_requested: string;
            readonly status: components["schemas"]["UserRightsRequestsStatusEnum"];
            comment?: string | null;
            readonly role: components["schemas"]["RoleEnum"];
            /** Format: date-time */
            expiration_date?: string | null;
        };
        /**
         * @description * `PENDING` - En attente de validation
         *     * `ACCEPTED` - Accepté
         *     * `REJECTED` - Refusé
         *     * `REVOKED` - Révoqué
         * @enum {string}
         */
        UserRightsRequestsStatusEnum: UserRightsRequestsStatusEnum;
        UserRightsResponse: {
            rights: components["schemas"]["UserRights"][];
            requests: components["schemas"]["UserRightsRequests"][];
        };
        UserSettingsResponse: {
            /** Format: email */
            email: string;
            rights: components["schemas"]["UserRights"][];
            requests: components["schemas"]["UserRightsRequests"][];
        };
        /**
         * @description * `NO_ONE` - NO_ONE
         *     * `DGEC` - DGEC
         *     * `CPO` - CPO
         *     * `BOTH` - BOTH
         * @enum {string}
         */
        ValidatedByEnum: PathsApiElecProvisionCertificatesQualichargeGetParametersQueryValidated_by;
        /** @description A serializer for submitting the OTP sent via email. Includes otp_token field only. */
        VerifyOTPRequest: {
            /** Entrez le code à 6 chiffres reçu par email */
            otp_token: string;
        };
        Warning: {
            code: string;
            meta: {
                [key: string]: unknown;
            };
        };
        /**
         * @description * `PENDING` - En attente
         *     * `ACCEPTED` - Accepté
         *     * `REJECTED` - Refusé
         * @enum {string}
         */
        "saf.filters.TicketFilter.status": PathsApiSafTicketsGetParametersQueryStatus;
    };
    responses: never;
    parameters: never;
    requestBodies: never;
    headers: never;
    pathItems: never;
}
export type $defs = Record<string, never>;
export interface operations {
    auth_activate_create: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ActivateAccountRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["ActivateAccountRequest"];
                "multipart/form-data": components["schemas"]["ActivateAccountRequest"];
            };
        };
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ActivateResponse"];
                };
            };
            /** @description Bad request - missing fields. */
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    auth_confirm_email_change_create: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ConfirmEmailChangeRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["ConfirmEmailChangeRequest"];
                "multipart/form-data": components["schemas"]["ConfirmEmailChangeRequest"];
            };
        };
        responses: {
            /** @description Email mis à jour avec succès */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ConfirmEmailChangeSuccess"];
                };
            };
            /** @description Erreurs possibles: données invalides, aucune demande en cours, code expiré, code incorrect */
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ConfirmEmailChangeError"];
                };
            };
        };
    };
    auth_login_create: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["UserLoginRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["UserLoginRequest"];
                "multipart/form-data": components["schemas"]["UserLoginRequest"];
            };
        };
        responses: {
            /** @description Request successful. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Bad request - missing fields. */
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    auth_logout_retrieve: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Request successful. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    auth_register_create: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["UserCreationRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["UserCreationRequest"];
                "multipart/form-data": components["schemas"]["UserCreationRequest"];
            };
        };
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["UserCreation"];
                };
            };
        };
    };
    auth_request_activation_link_create: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["UserResendActivationLinkRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["UserResendActivationLinkRequest"];
                "multipart/form-data": components["schemas"]["UserResendActivationLinkRequest"];
            };
        };
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["UserCreation"];
                };
            };
        };
    };
    auth_request_email_change_create: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["RequestEmailChangeRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["RequestEmailChangeRequest"];
                "multipart/form-data": components["schemas"]["RequestEmailChangeRequest"];
            };
        };
        responses: {
            /** @description Code OTP envoyé avec succès à la nouvelle adresse email */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["RequestEmailChangeSuccess"];
                };
            };
            /** @description Erreurs possibles: données invalides, mot de passe incorrect, email déjà utilisé */
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["RequestEmailChangeError"];
                };
            };
        };
    };
    auth_request_otp_retrieve: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["OtpResponse"];
                };
            };
        };
    };
    auth_request_password_change_create: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ChangePasswordRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["ChangePasswordRequest"];
                "multipart/form-data": components["schemas"]["ChangePasswordRequest"];
            };
        };
        responses: {
            /** @description Mot de passe modifié avec succès */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ChangePasswordSuccess"];
                };
            };
            /** @description Erreurs possibles: données invalides, mot de passe actuel incorrect, nouveau mot de passe invalide */
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ChangePasswordError"];
                };
            };
        };
    };
    auth_request_password_reset_create: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["RequestPasswordResetRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["RequestPasswordResetRequest"];
                "multipart/form-data": components["schemas"]["RequestPasswordResetRequest"];
            };
        };
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["UserCreation"];
                };
            };
        };
    };
    auth_reset_password_create: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ResetPasswordRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["ResetPasswordRequest"];
                "multipart/form-data": components["schemas"]["ResetPasswordRequest"];
            };
        };
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["UserCreation"];
                };
            };
        };
    };
    auth_verify_otp_create: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["VerifyOTPRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["VerifyOTPRequest"];
                "multipart/form-data": components["schemas"]["VerifyOTPRequest"];
            };
        };
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["UserCreation"];
                };
            };
        };
    };
    biomethane_annual_declaration_retrieve: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Declaration details for the entity */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["BiomethaneAnnualDeclaration"];
                };
            };
            /** @description Declaration created for the entity */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["BiomethaneAnnualDeclaration"];
                };
            };
        };
    };
    biomethane_annual_declaration_validate_create: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description No response body */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    biomethane_annual_declaration_years_retrieve: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": number[];
                };
            };
        };
    };
    biomethane_contract_retrieve: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Contract details for the entity */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["BiomethaneContract"];
                };
            };
            /** @description Contract not found for this entity. */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    biomethane_contract_update: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: {
            content: {
                "application/json": components["schemas"]["BiomethaneContractInputRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["BiomethaneContractInputRequest"];
                "multipart/form-data": components["schemas"]["BiomethaneContractInputRequest"];
            };
        };
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["BiomethaneContract"];
                };
            };
        };
    };
    biomethane_contract_amendments_list: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
                /** @description Which field to use when ordering the results. */
                ordering?: string;
                /** @description A page number within the paginated result set. */
                page?: number;
                /** @description Number of results to return per page. */
                page_size?: number;
                /** @description A search term. */
                search?: string;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["PaginatedBiomethaneContractAmendmentList"];
                };
            };
        };
    };
    biomethane_contract_amendments_create: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["BiomethaneContractAmendmentAddRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["BiomethaneContractAmendmentAddRequest"];
                "multipart/form-data": components["schemas"]["BiomethaneContractAmendmentAddRequest"];
            };
        };
        responses: {
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["BiomethaneContractAmendmentAdd"];
                };
            };
        };
    };
    biomethane_contract_amendments_retrieve: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
            };
            header?: never;
            path: {
                /** @description A unique integer value identifying this Biométhane - Avenant au contrat. */
                id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["BiomethaneContractAmendment"];
                };
            };
        };
    };
    biomethane_digestate_retrieve: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
                /** @description Declaration year. */
                year: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Digestate details for the entity */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["BiomethaneDigestate"];
                };
            };
            /** @description Digestate not found for this entity. */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    biomethane_digestate_update: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: {
            content: {
                "application/json": components["schemas"]["BiomethaneDigestateInputRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["BiomethaneDigestateInputRequest"];
                "multipart/form-data": components["schemas"]["BiomethaneDigestateInputRequest"];
            };
        };
        responses: {
            /** @description Digestate updated successfully */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["BiomethaneDigestate"];
                };
            };
            /** @description Digestate created successfully */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["BiomethaneDigestate"];
                };
            };
        };
    };
    biomethane_digestate_storage_list: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
                /** @description Which field to use when ordering the results. */
                ordering?: string;
                /** @description A search term. */
                search?: string;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["BiomethaneDigestateStorage"][];
                };
            };
        };
    };
    biomethane_digestate_storage_create: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["BiomethaneDigestateStorageInputRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["BiomethaneDigestateStorageInputRequest"];
                "multipart/form-data": components["schemas"]["BiomethaneDigestateStorageInputRequest"];
            };
        };
        responses: {
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["BiomethaneDigestateStorageInput"];
                };
            };
        };
    };
    biomethane_digestate_storage_retrieve: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
            };
            header?: never;
            path: {
                /** @description A unique integer value identifying this Biométhane - Stockage de Digestat. */
                id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["BiomethaneDigestateStorage"];
                };
            };
        };
    };
    biomethane_digestate_storage_update: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
            };
            header?: never;
            path: {
                /** @description A unique integer value identifying this Biométhane - Stockage de Digestat. */
                id: number;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["BiomethaneDigestateStorageInputRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["BiomethaneDigestateStorageInputRequest"];
                "multipart/form-data": components["schemas"]["BiomethaneDigestateStorageInputRequest"];
            };
        };
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["BiomethaneDigestateStorageInput"];
                };
            };
        };
    };
    biomethane_digestate_storage_destroy: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
            };
            header?: never;
            path: {
                /** @description A unique integer value identifying this Biométhane - Stockage de Digestat. */
                id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description No response body */
            204: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    biomethane_digestate_storage_partial_update: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
            };
            header?: never;
            path: {
                /** @description A unique integer value identifying this Biométhane - Stockage de Digestat. */
                id: number;
            };
            cookie?: never;
        };
        requestBody?: {
            content: {
                "application/json": components["schemas"]["PatchedBiomethaneDigestateStorageInputRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["PatchedBiomethaneDigestateStorageInputRequest"];
                "multipart/form-data": components["schemas"]["PatchedBiomethaneDigestateStorageInputRequest"];
            };
        };
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["BiomethaneDigestateStorageInput"];
                };
            };
        };
    };
    biomethane_digestate_spreading_create: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["BiomethaneDigestateSpreadingAddRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["BiomethaneDigestateSpreadingAddRequest"];
                "multipart/form-data": components["schemas"]["BiomethaneDigestateSpreadingAddRequest"];
            };
        };
        responses: {
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["BiomethaneDigestateSpreadingAdd"];
                };
            };
        };
    };
    biomethane_digestate_spreading_destroy: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
            };
            header?: never;
            path: {
                /** @description A unique integer value identifying this Biométhane - Données d'épandage du digestat. */
                id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description No response body */
            204: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    biomethane_digestate_validate_create: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description No response body */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    biomethane_energy_retrieve: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
                /** @description Declaration year. */
                year: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Energy declaration details for the entity */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["BiomethaneEnergy"];
                };
            };
            /** @description Energy not found for this entity. */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    biomethane_energy_update: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: {
            content: {
                "application/json": components["schemas"]["BiomethaneEnergyInputRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["BiomethaneEnergyInputRequest"];
                "multipart/form-data": components["schemas"]["BiomethaneEnergyInputRequest"];
            };
        };
        responses: {
            /** @description Energy declaration updated successfully */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["BiomethaneEnergy"];
                };
            };
            /** @description Energy declaration created successfully */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["BiomethaneEnergy"];
                };
            };
        };
    };
    biomethane_energy_monthly_reports_list: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
                /** @description Which field to use when ordering the results. */
                ordering?: string;
                /** @description A search term. */
                search?: string;
                /** @description Declaration year. */
                year: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Energy declaration monthly reports for the year */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["BiomethaneEnergyMonthlyReport"][];
                };
            };
            /** @description Energy monthly reports not found for this entity and year. */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    biomethane_energy_monthly_reports_update: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["MonthlyReportDataRequest"][];
                "application/x-www-form-urlencoded": components["schemas"]["MonthlyReportDataRequest"][];
                "multipart/form-data": components["schemas"]["MonthlyReportDataRequest"][];
            };
        };
        responses: {
            /** @description Monthly reports created or updated successfully */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    biomethane_energy_validate_create: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description No response body */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    biomethane_injection_site_retrieve: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Injection site details for the entity */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["BiomethaneInjectionSite"];
                };
            };
            /** @description Injection site not found for this entity. */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    biomethane_injection_site_update: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["BiomethaneInjectionSiteInputRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["BiomethaneInjectionSiteInputRequest"];
                "multipart/form-data": components["schemas"]["BiomethaneInjectionSiteInputRequest"];
            };
        };
        responses: {
            /** @description Injection site updated successfully */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["BiomethaneInjectionSite"];
                };
            };
            /** @description Injection site created successfully */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["BiomethaneInjectionSite"];
                };
            };
        };
    };
    biomethane_production_unit_retrieve: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Production unit details for the entity */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["BiomethaneProductionUnit"];
                };
            };
            /** @description Production unit not found for this entity. */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    biomethane_production_unit_update: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: {
            content: {
                "application/json": components["schemas"]["BiomethaneProductionUnitUpsertRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["BiomethaneProductionUnitUpsertRequest"];
                "multipart/form-data": components["schemas"]["BiomethaneProductionUnitUpsertRequest"];
            };
        };
        responses: {
            /** @description Production unit updated successfully */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["BiomethaneProductionUnit"];
                };
            };
            /** @description Production unit created successfully */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["BiomethaneProductionUnit"];
                };
            };
        };
    };
    biomethane_supply_input_list: {
        parameters: {
            query: {
                /** @description * `LIVESTOCK_EFFLUENTS` - Effluents d'élevage
                 *     * `PRIMARY_CROPS` - Culture principale
                 *     * `INTERMEDIATE_CROPS` - Culture intermédiaire
                 *     * `CIVE` - CIVE
                 *     * `IAA_WASTE_RESIDUES` - Déchets/Résidus d'IAA */
                category?: PathsApiBiomethaneSupplyInputGetParametersQueryCategory;
                /** @description Authorised entity ID. */
                entity_id: number;
                /** @description Which field to use when ordering the results. */
                ordering?: string;
                /** @description A page number within the paginated result set. */
                page?: number;
                /** @description Number of results to return per page. */
                page_size?: number;
                /** @description A search term. */
                search?: string;
                /** @description * `INTERNAL` - Interne
                 *     * `EXTERNAL` - Externe */
                source?: PathsApiBiomethaneSupplyInputGetParametersQuerySource;
                type?: string;
                year: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["PaginatedBiomethaneSupplyInputList"];
                };
            };
        };
    };
    biomethane_supply_input_create: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["BiomethaneSupplyInputCreateRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["BiomethaneSupplyInputCreateRequest"];
                "multipart/form-data": components["schemas"]["BiomethaneSupplyInputCreateRequest"];
            };
        };
        responses: {
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["BiomethaneSupplyInputCreate"];
                };
            };
        };
    };
    biomethane_supply_input_retrieve: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
            };
            header?: never;
            path: {
                /** @description A unique integer value identifying this Biométhane - Intrant d'approvisionnement. */
                id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["BiomethaneSupplyInput"];
                };
            };
        };
    };
    biomethane_supply_input_update: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
            };
            header?: never;
            path: {
                /** @description A unique integer value identifying this Biométhane - Intrant d'approvisionnement. */
                id: number;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["BiomethaneSupplyInputCreateRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["BiomethaneSupplyInputCreateRequest"];
                "multipart/form-data": components["schemas"]["BiomethaneSupplyInputCreateRequest"];
            };
        };
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["BiomethaneSupplyInputCreate"];
                };
            };
        };
    };
    biomethane_supply_input_partial_update: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
            };
            header?: never;
            path: {
                /** @description A unique integer value identifying this Biométhane - Intrant d'approvisionnement. */
                id: number;
            };
            cookie?: never;
        };
        requestBody?: {
            content: {
                "application/json": components["schemas"]["PatchedBiomethaneSupplyInputCreateRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["PatchedBiomethaneSupplyInputCreateRequest"];
                "multipart/form-data": components["schemas"]["PatchedBiomethaneSupplyInputCreateRequest"];
            };
        };
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["BiomethaneSupplyInputCreate"];
                };
            };
        };
    };
    biomethane_supply_input_export_retrieve: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["BiomethaneSupplyInputExport"];
                };
            };
        };
    };
    biomethane_supply_input_filters_retrieve: {
        parameters: {
            query: {
                /** @description * `LIVESTOCK_EFFLUENTS` - Effluents d'élevage
                 *     * `PRIMARY_CROPS` - Culture principale
                 *     * `INTERMEDIATE_CROPS` - Culture intermédiaire
                 *     * `CIVE` - CIVE
                 *     * `IAA_WASTE_RESIDUES` - Déchets/Résidus d'IAA */
                category?: PathsApiBiomethaneSupplyInputGetParametersQueryCategory;
                /** @description Authorised entity ID. */
                entity_id: number;
                /** @description Filter string to apply */
                filter: PathsApiBiomethaneSupplyInputFiltersGetParametersQueryFilter;
                /** @description Which field to use when ordering the results. */
                ordering?: string;
                /** @description A search term. */
                search?: string;
                /** @description * `INTERNAL` - Interne
                 *     * `EXTERNAL` - Externe */
                source?: PathsApiBiomethaneSupplyInputGetParametersQuerySource;
                type?: string;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": string[];
                };
            };
        };
    };
    biomethane_supply_plan_download_template_retrieve: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Fichier Excel généré */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": File;
                };
            };
        };
    };
    biomethane_supply_plan_export_retrieve: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["BiomethaneSupplyInputExport"];
                };
            };
        };
    };
    import_supply_plan_from_excel: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["BiomethaneUploadExcelRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["BiomethaneUploadExcelRequest"];
                "multipart/form-data": components["schemas"]["BiomethaneUploadExcelRequest"];
            };
        };
        responses: {
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": Record<string, never>;
                };
            };
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": Record<string, never>;
                };
            };
        };
    };
    biomethane_supply_plan_years_retrieve: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": number[];
                };
            };
        };
    };
    double_counting_agreements_list: {
        parameters: {
            query: {
                certificate_id?: string;
                /** @description Entity ID */
                entity_id: number;
                /** @description Ordre
                 *
                 *     * `production_site` - Production site
                 *     * `-production_site` - Production site (décroissant)
                 *     * `valid_until` - Valid until
                 *     * `-valid_until` - Valid until (décroissant)
                 *     * `producer` - Producer
                 *     * `-producer` - Producer (décroissant)
                 *     * `certificate_id` - Certificate id
                 *     * `-certificate_id` - Certificate id (décroissant) */
                order_by?: PathsApiDoubleCountingAgreementsGetParametersQueryOrder_by[];
                /** @description Which field to use when ordering the results. */
                ordering?: string;
                producers?: string;
                production_sites?: string;
                /** @description A search term. */
                search?: string;
                /** @description Year */
                year?: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["DoubleCountingApplicationPartial"][];
                };
            };
        };
    };
    double_counting_agreements_retrieve: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path: {
                /** @description A unique integer value identifying this Certificat Double Compte. */
                id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["DoubleCountingRegistrationDetails"];
                };
            };
        };
    };
    double_counting_agreements_agreement_admin_retrieve: {
        parameters: {
            query: {
                certificate_id?: string;
                /** @description Entity ID */
                entity_id: number;
                /** @description Ordre
                 *
                 *     * `production_site` - Production site
                 *     * `-production_site` - Production site (décroissant)
                 *     * `valid_until` - Valid until
                 *     * `-valid_until` - Valid until (décroissant)
                 *     * `producer` - Producer
                 *     * `-producer` - Producer (décroissant)
                 *     * `certificate_id` - Certificate id
                 *     * `-certificate_id` - Certificate id (décroissant) */
                order_by?: PathsApiDoubleCountingAgreementsGetParametersQueryOrder_by[];
                /** @description Which field to use when ordering the results. */
                ordering?: string;
                producers?: string;
                production_sites?: string;
                /** @description A search term. */
                search?: string;
                /** @description Year */
                year?: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AgreementLists"];
                };
            };
        };
    };
    double_counting_agreements_agreement_public_list: {
        parameters: {
            query?: {
                certificate_id?: string;
                /** @description Ordre
                 *
                 *     * `production_site` - Production site
                 *     * `-production_site` - Production site (décroissant)
                 *     * `valid_until` - Valid until
                 *     * `-valid_until` - Valid until (décroissant)
                 *     * `producer` - Producer
                 *     * `-producer` - Producer (décroissant)
                 *     * `certificate_id` - Certificate id
                 *     * `-certificate_id` - Certificate id (décroissant) */
                order_by?: PathsApiDoubleCountingAgreementsGetParametersQueryOrder_by[];
                /** @description Which field to use when ordering the results. */
                ordering?: string;
                producers?: string;
                production_sites?: string;
                /** @description A search term. */
                search?: string;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["DoubleCountingRegistrationPublic"][];
                };
            };
        };
    };
    double_counting_agreements_export_retrieve: {
        parameters: {
            query: {
                certificate_id?: string;
                /** @description Entity ID */
                entity_id: number;
                /** @description Ordre
                 *
                 *     * `production_site` - Production site
                 *     * `-production_site` - Production site (décroissant)
                 *     * `valid_until` - Valid until
                 *     * `-valid_until` - Valid until (décroissant)
                 *     * `producer` - Producer
                 *     * `-producer` - Producer (décroissant)
                 *     * `certificate_id` - Certificate id
                 *     * `-certificate_id` - Certificate id (décroissant) */
                order_by?: PathsApiDoubleCountingAgreementsGetParametersQueryOrder_by[];
                /** @description Which field to use when ordering the results. */
                ordering?: string;
                producers?: string;
                production_sites?: string;
                /** @description A search term. */
                search?: string;
                /** @description Year */
                year?: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": string;
                };
            };
        };
    };
    double_counting_agreements_filters_retrieve: {
        parameters: {
            query?: {
                certificate_id?: string;
                /** @description Filter string to apply */
                filter?: string;
                /** @description Ordre
                 *
                 *     * `production_site` - Production site
                 *     * `-production_site` - Production site (décroissant)
                 *     * `valid_until` - Valid until
                 *     * `-valid_until` - Valid until (décroissant)
                 *     * `producer` - Producer
                 *     * `-producer` - Producer (décroissant)
                 *     * `certificate_id` - Certificate id
                 *     * `-certificate_id` - Certificate id (décroissant) */
                order_by?: PathsApiDoubleCountingAgreementsGetParametersQueryOrder_by[];
                /** @description Which field to use when ordering the results. */
                ordering?: string;
                producers?: string;
                production_sites?: string;
                /** @description A search term. */
                search?: string;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": string[];
                };
            };
            /** @description Bad request - invalid filter or not found. */
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    double_counting_applications_retrieve: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path: {
                /** @description A unique integer value identifying this Dossier Double Compte. */
                id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["DoubleCountingApplication"];
                };
            };
        };
    };
    double_counting_applications_export_retrieve: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path: {
                /** @description A unique integer value identifying this Dossier Double Compte. */
                id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/force-download": string;
                };
            };
        };
    };
    double_counting_applications_files_destroy: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path: {
                /** @description File ID to delete */
                file_id: number;
                /** @description A unique integer value identifying this Dossier Double Compte. */
                id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Response"];
                };
            };
        };
    };
    double_counting_applications_update_approved_quotas_create: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path: {
                /** @description A unique integer value identifying this Dossier Double Compte. */
                id: number;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["UpdatedQuotasRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["UpdatedQuotasRequest"];
                "multipart/form-data": components["schemas"]["UpdatedQuotasRequest"];
            };
        };
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Response"];
                };
            };
        };
    };
    double_counting_applications_upload_files_create: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path: {
                /** @description A unique integer value identifying this Dossier Double Compte. */
                id: number;
            };
            cookie?: never;
        };
        requestBody?: {
            content: {
                "application/json": components["schemas"]["ApplicationFileUploadRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["ApplicationFileUploadRequest"];
                "multipart/form-data": components["schemas"]["ApplicationFileUploadRequest"];
            };
        };
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Response"];
                };
            };
        };
    };
    double_counting_applications_add_create: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["DoubleCountingAdminAddRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["DoubleCountingAdminAddRequest"];
                "multipart/form-data": components["schemas"]["DoubleCountingAdminAddRequest"];
            };
        };
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Response"];
                };
            };
        };
    };
    double_counting_applications_approve_create: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ApproveDoubleCountingRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["ApproveDoubleCountingRequest"];
                "multipart/form-data": components["schemas"]["ApproveDoubleCountingRequest"];
            };
        };
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Response"];
                };
            };
        };
    };
    double_counting_applications_check_file_create: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: {
            content: {
                "multipart/form-data": {
                    /** Format: binary */
                    file?: File;
                };
            };
        };
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["CheckFileResponse"];
                };
            };
        };
    };
    double_counting_applications_filters_retrieve: {
        parameters: {
            query?: {
                certificate_id?: string;
                /** @description Filter string to apply */
                filter?: string;
                /** @description Ordre
                 *
                 *     * `production_site` - Production site
                 *     * `-production_site` - Production site (décroissant)
                 *     * `valid_until` - Valid until
                 *     * `-valid_until` - Valid until (décroissant)
                 *     * `producer` - Producer
                 *     * `-producer` - Producer (décroissant)
                 *     * `created_at` - Created at
                 *     * `-created_at` - Created at (décroissant)
                 *     * `certificate_id` - Certificate id
                 *     * `-certificate_id` - Certificate id (décroissant) */
                order_by?: PathsApiDoubleCountingApplicationsFiltersGetParametersQueryOrder_by[];
                /** @description Which field to use when ordering the results. */
                ordering?: string;
                producers?: string;
                production_sites?: string;
                /** @description A search term. */
                search?: string;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": string[];
                };
            };
            /** @description Bad request - invalid filter or not found. */
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    double_counting_applications_generate_decision_retrieve: {
        parameters: {
            query: {
                /** @description Doublecount application ID */
                dca_id: number;
                /** @description Dechet industriel */
                di?: string;
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": string;
                };
            };
        };
    };
    double_counting_applications_list_admin_retrieve: {
        parameters: {
            query: {
                certificate_id?: string;
                /** @description Entity ID */
                entity_id: number;
                /** @description Ordre
                 *
                 *     * `production_site` - Production site
                 *     * `-production_site` - Production site (décroissant)
                 *     * `valid_until` - Valid until
                 *     * `-valid_until` - Valid until (décroissant)
                 *     * `producer` - Producer
                 *     * `-producer` - Producer (décroissant)
                 *     * `created_at` - Created at
                 *     * `-created_at` - Created at (décroissant)
                 *     * `certificate_id` - Certificate id
                 *     * `-certificate_id` - Certificate id (décroissant) */
                order_by?: PathsApiDoubleCountingApplicationsFiltersGetParametersQueryOrder_by[];
                /** @description Which field to use when ordering the results. */
                ordering?: string;
                producers?: string;
                production_sites?: string;
                /** @description A search term. */
                search?: string;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApplicationListe"];
                };
            };
        };
    };
    double_counting_applications_reject_create: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["RejectDoubleCountingRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["RejectDoubleCountingRequest"];
                "multipart/form-data": components["schemas"]["RejectDoubleCountingRequest"];
            };
        };
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Response"];
                };
            };
        };
    };
    double_counting_snapshot_retrieve: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApplicationSnapshot"];
                };
            };
        };
    };
    elec_certificates_clients_list: {
        parameters: {
            query?: {
                /** @description Entity querying the endpoint */
                entity_id?: number;
                /** @description Search within the field `name` */
                query?: string;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["EntityPreview"][];
                };
            };
        };
    };
    elec_certificates_snapshot_retrieve: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
                /** @description Year */
                year: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": {
                        provision_certificates_available: number;
                        provision_certificates_history: number;
                        transfer_certificates_pending: number;
                        transfer_certificates_accepted: number;
                        transfer_certificates_rejected: number;
                    };
                };
            };
        };
    };
    elec_certificates_years_retrieve: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": number[];
                };
            };
        };
    };
    elec_provision_certificates_list: {
        parameters: {
            query: {
                /** @description Les valeurs multiples doivent être séparées par des virgules. */
                cpo?: string[];
                energy_amount?: number;
                /** @description Entity ID */
                entity_id: number;
                /** @description Les valeurs multiples doivent être séparées par des virgules. */
                operating_unit?: string[];
                /** @description Ordre
                 *
                 *     * `quarter` - Quarter
                 *     * `-quarter` - Quarter (décroissant)
                 *     * `remaining_energy_amount` - Remaining energy amount
                 *     * `-remaining_energy_amount` - Remaining energy amount (décroissant)
                 *     * `cpo` - Cpo
                 *     * `-cpo` - Cpo (décroissant)
                 *     * `operating_unit` - Operating unit
                 *     * `-operating_unit` - Operating unit (décroissant)
                 *     * `source` - Source
                 *     * `-source` - Source (décroissant) */
                order_by?: PathsApiElecProvisionCertificatesGetParametersQueryOrder_by[];
                /** @description Which field to use when ordering the results. */
                ordering?: string;
                /** @description A page number within the paginated result set. */
                page?: number;
                /** @description Number of results to return per page. */
                page_size?: number;
                /** @description Les valeurs multiples doivent être séparées par des virgules. */
                quarter?: PathsApiElecProvisionCertificatesGetParametersQueryQuarter[];
                /** @description A search term. */
                search?: string;
                /** @description Les valeurs multiples doivent être séparées par des virgules. */
                source?: (PathsApiElecProvisionCertificatesGetParametersQuerySource | null)[];
                status?: string;
                year?: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["PaginatedElecProvisionCertificateList"];
                };
            };
        };
    };
    elec_provision_certificates_qualicharge_list: {
        parameters: {
            query: {
                /** @description Les valeurs multiples doivent être séparées par des virgules. */
                cpo?: string[];
                date_from?: string;
                /** @description Authorised entity ID. */
                entity_id: number;
                not_validated?: boolean;
                /** @description Les valeurs multiples doivent être séparées par des virgules. */
                operating_unit?: string[];
                /** @description Which field to use when ordering the results. */
                ordering?: string;
                /** @description A page number within the paginated result set. */
                page?: number;
                /** @description Number of results to return per page. */
                page_size?: number;
                /** @description A search term. */
                search?: string;
                /** @description Les valeurs multiples doivent être séparées par des virgules. */
                station_id?: string[];
                /** @description * `NO_ONE` - NO_ONE
                 *     * `DGEC` - DGEC
                 *     * `CPO` - CPO
                 *     * `BOTH` - BOTH */
                validated_by?: PathsApiElecProvisionCertificatesQualichargeGetParametersQueryValidated_by[];
                year?: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["PaginatedElecProvisionCertificateQualichargeList"];
                };
            };
        };
    };
    elec_provision_certificates_qualicharge_retrieve: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
            };
            header?: never;
            path: {
                /** @description A unique integer value identifying this Certificat de Fourniture Qualicharge (elec). */
                id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ElecProvisionCertificateQualicharge"];
                };
            };
        };
    };
    bulk_create_provision_certificates_qualicharge: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ProvisionCertificateBulkRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["ProvisionCertificateBulkRequest"];
                "multipart/form-data": components["schemas"]["ProvisionCertificateBulkRequest"];
            };
        };
        responses: {
            /** @description Success message */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    bulk_update_provision_certificates_qualicharge: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ProvisionCertificateUpdateBulkRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["ProvisionCertificateUpdateBulkRequest"];
                "multipart/form-data": components["schemas"]["ProvisionCertificateUpdateBulkRequest"];
            };
        };
        responses: {
            /** @description Success message */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    filter_provision_certificates_qualicharge: {
        parameters: {
            query: {
                /** @description Les valeurs multiples doivent être séparées par des virgules. */
                cpo?: string[];
                date_from?: string;
                /** @description Authorised entity ID. */
                entity_id: number;
                /** @description Filter string to apply */
                filter: PathsApiElecProvisionCertificatesQualichargeFiltersGetParametersQueryFilter;
                not_validated?: boolean;
                /** @description Les valeurs multiples doivent être séparées par des virgules. */
                operating_unit?: string[];
                /** @description Which field to use when ordering the results. */
                ordering?: string;
                /** @description A search term. */
                search?: string;
                /** @description Les valeurs multiples doivent être séparées par des virgules. */
                station_id?: string[];
                /** @description * `NO_ONE` - NO_ONE
                 *     * `DGEC` - DGEC
                 *     * `CPO` - CPO
                 *     * `BOTH` - BOTH */
                validated_by?: PathsApiElecProvisionCertificatesQualichargeGetParametersQueryValidated_by[];
                year?: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": string[];
                };
            };
        };
    };
    elec_provision_certificates_retrieve: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path: {
                /** @description A unique integer value identifying this Certificat de Fourniture (elec). */
                id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ElecProvisionCertificate"];
                };
            };
        };
    };
    elec_provision_certificates_balance_retrieve: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": {
                        balance?: number;
                    };
                };
            };
        };
    };
    export_provision_certificates_excel: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": File;
                };
            };
        };
    };
    elec_provision_certificates_filters_retrieve: {
        parameters: {
            query: {
                /** @description Les valeurs multiples doivent être séparées par des virgules. */
                cpo?: string[];
                energy_amount?: number;
                /** @description Entity ID */
                entity_id: number;
                /** @description Filter string to apply */
                filter: PathsApiElecProvisionCertificatesFiltersGetParametersQueryFilter;
                /** @description Les valeurs multiples doivent être séparées par des virgules. */
                operating_unit?: string[];
                /** @description Ordre
                 *
                 *     * `quarter` - Quarter
                 *     * `-quarter` - Quarter (décroissant)
                 *     * `remaining_energy_amount` - Remaining energy amount
                 *     * `-remaining_energy_amount` - Remaining energy amount (décroissant)
                 *     * `cpo` - Cpo
                 *     * `-cpo` - Cpo (décroissant)
                 *     * `operating_unit` - Operating unit
                 *     * `-operating_unit` - Operating unit (décroissant)
                 *     * `source` - Source
                 *     * `-source` - Source (décroissant) */
                order_by?: PathsApiElecProvisionCertificatesGetParametersQueryOrder_by[];
                /** @description Which field to use when ordering the results. */
                ordering?: string;
                /** @description Les valeurs multiples doivent être séparées par des virgules. */
                quarter?: PathsApiElecProvisionCertificatesGetParametersQueryQuarter[];
                /** @description A search term. */
                search?: string;
                /** @description Les valeurs multiples doivent être séparées par des virgules. */
                source?: (PathsApiElecProvisionCertificatesGetParametersQuerySource | null)[];
                status?: string;
                year?: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": string[];
                };
            };
        };
    };
    elec_provision_certificates_import_create: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: {
            content: {
                "multipart/form-data": {
                    /**
                     * Format: binary
                     * @description CSV file to import
                     */
                    file: File;
                };
            };
        };
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": Record<string, never>;
                };
            };
        };
    };
    elec_provision_certificates_transfer_create: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ElecTransferRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["ElecTransferRequest"];
                "multipart/form-data": components["schemas"]["ElecTransferRequest"];
            };
        };
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ElecTransferCertificate"];
                };
            };
        };
    };
    elec_transfer_certificates_list: {
        parameters: {
            query: {
                certificate_id?: string;
                client?: number;
                consumption_date?: string;
                /** @description Les valeurs multiples doivent être séparées par des virgules. */
                cpo?: string[];
                energy_amount?: number;
                /** @description Entity ID */
                entity_id: number;
                month?: number;
                /** @description Les valeurs multiples doivent être séparées par des virgules. */
                operator?: string[];
                /** @description Ordre
                 *
                 *     * `status` - Status
                 *     * `-status` - Status (décroissant)
                 *     * `energy_amount` - Energy amount
                 *     * `-energy_amount` - Energy amount (décroissant)
                 *     * `cpo` - Cpo
                 *     * `-cpo` - Cpo (décroissant)
                 *     * `operator` - Operator
                 *     * `-operator` - Operator (décroissant)
                 *     * `certificate_id` - Certificate id
                 *     * `-certificate_id` - Certificate id (décroissant)
                 *     * `transfer_date` - Transfer date
                 *     * `-transfer_date` - Transfer date (décroissant)
                 *     * `consumption_date` - Consumption date
                 *     * `-consumption_date` - Consumption date (décroissant) */
                order_by?: PathsApiElecTransferCertificatesGetParametersQueryOrder_by[];
                /** @description Which field to use when ordering the results. */
                ordering?: string;
                /** @description A page number within the paginated result set. */
                page?: number;
                /** @description Number of results to return per page. */
                page_size?: number;
                /** @description A search term. */
                search?: string;
                status?: string;
                supplier?: number;
                transfer_date?: string;
                used_in_tiruert?: boolean;
                year?: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["PaginatedElecTransferCertificateList"];
                };
            };
        };
    };
    elec_transfer_certificates_retrieve: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path: {
                /** @description A unique integer value identifying this Certificat de Cession (elec). */
                id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ElecTransferCertificate"];
                };
            };
        };
    };
    elec_transfer_certificates_accept_create: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path: {
                /** @description A unique integer value identifying this Certificat de Cession (elec). */
                id: number;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ElecTransferAcceptRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["ElecTransferAcceptRequest"];
                "multipart/form-data": components["schemas"]["ElecTransferAcceptRequest"];
            };
        };
        responses: {
            /** @description No response body */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    elec_transfer_certificates_cancel_create: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path: {
                /** @description A unique integer value identifying this Certificat de Cession (elec). */
                id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description No response body */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    elec_transfer_certificates_reject_create: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path: {
                /** @description A unique integer value identifying this Certificat de Cession (elec). */
                id: number;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ElecTransferRejectRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["ElecTransferRejectRequest"];
                "multipart/form-data": components["schemas"]["ElecTransferRejectRequest"];
            };
        };
        responses: {
            /** @description No response body */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    export_transfer_certificates_excel: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": File;
                };
            };
        };
    };
    elec_transfer_certificates_filters_retrieve: {
        parameters: {
            query: {
                certificate_id?: string;
                client?: number;
                consumption_date?: string;
                /** @description Les valeurs multiples doivent être séparées par des virgules. */
                cpo?: string[];
                energy_amount?: number;
                /** @description Entity ID */
                entity_id: number;
                /** @description Filter string to apply */
                filter: PathsApiElecTransferCertificatesFiltersGetParametersQueryFilter;
                month?: number;
                /** @description Les valeurs multiples doivent être séparées par des virgules. */
                operator?: string[];
                /** @description Ordre
                 *
                 *     * `status` - Status
                 *     * `-status` - Status (décroissant)
                 *     * `energy_amount` - Energy amount
                 *     * `-energy_amount` - Energy amount (décroissant)
                 *     * `cpo` - Cpo
                 *     * `-cpo` - Cpo (décroissant)
                 *     * `operator` - Operator
                 *     * `-operator` - Operator (décroissant)
                 *     * `certificate_id` - Certificate id
                 *     * `-certificate_id` - Certificate id (décroissant)
                 *     * `transfer_date` - Transfer date
                 *     * `-transfer_date` - Transfer date (décroissant)
                 *     * `consumption_date` - Consumption date
                 *     * `-consumption_date` - Consumption date (décroissant) */
                order_by?: PathsApiElecTransferCertificatesGetParametersQueryOrder_by[];
                /** @description Which field to use when ordering the results. */
                ordering?: string;
                /** @description A search term. */
                search?: string;
                status?: string;
                supplier?: number;
                transfer_date?: string;
                used_in_tiruert?: boolean;
                year?: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": string[];
                };
            };
        };
    };
    entities_list: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
                /** @description Has requests */
                has_requests?: boolean;
                /** @description Search query */
                q?: string;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["EntityMetrics"][];
                };
            };
        };
    };
    entities_create: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["CreateEntityRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["CreateEntityRequest"];
                "multipart/form-data": components["schemas"]["CreateEntityRequest"];
            };
        };
        responses: {
            /** @description Request successful. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Bad request. */
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    entities_retrieve: {
        parameters: {
            query: {
                /** @description The id of the admin entity enabling the company */
                entity_id: number;
            };
            header?: never;
            path: {
                /** @description A unique integer value identifying this Entity. */
                id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["UserEntity"];
                };
            };
        };
    };
    entities_enable_create: {
        parameters: {
            query: {
                /** @description The id of the admin entity enabling the company */
                entity_id: number;
            };
            header?: never;
            path: {
                /** @description A unique integer value identifying this Entity. */
                id: number;
            };
            cookie?: never;
        };
        requestBody?: {
            content: {
                "application/json": components["schemas"]["EmptyResponseRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["EmptyResponseRequest"];
                "multipart/form-data": components["schemas"]["EmptyResponseRequest"];
            };
        };
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["EmptyResponse"];
                };
            };
        };
    };
    entities_add_company_create: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["EntityCompanyRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["EntityCompanyRequest"];
                "multipart/form-data": components["schemas"]["EntityCompanyRequest"];
            };
        };
        responses: {
            /** @description Request successful. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Bad request. */
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    entities_certificates_list: {
        parameters: {
            query: {
                /** @description Compay ID, Admin only */
                company_id?: number;
                /** @description Search within certificates valid at this date */
                date?: string;
                /** @description Entity ID */
                entity_id: number;
                /** @description Which field to use when ordering the results. */
                ordering?: string;
                /** @description Production site ID */
                production_site_id?: number;
                /** @description Search within the field `certificate_id` */
                query?: string;
                /** @description A search term. */
                search?: string;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["EntityCertificate"][];
                };
            };
        };
    };
    entities_certificates_retrieve: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                /** @description A unique integer value identifying this CarbureEntityCertificates. */
                id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["EntityCertificate"];
                };
            };
        };
    };
    entities_certificates_add_create: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["AddCertificateRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["AddCertificateRequest"];
                "multipart/form-data": components["schemas"]["AddCertificateRequest"];
            };
        };
        responses: {
            /** @description Request successful. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Bad request. */
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    entities_certificates_check_entity_create: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["CheckCertificateRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["CheckCertificateRequest"];
                "multipart/form-data": components["schemas"]["CheckCertificateRequest"];
            };
        };
        responses: {
            /** @description Request successful. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Bad request. */
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    entities_certificates_delete_create: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["DeleteCertificateRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["DeleteCertificateRequest"];
                "multipart/form-data": components["schemas"]["DeleteCertificateRequest"];
            };
        };
        responses: {
            /** @description Request successful. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Bad request. */
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    entities_certificates_reject_entity_create: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["RejectCertificateRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["RejectCertificateRequest"];
                "multipart/form-data": components["schemas"]["RejectCertificateRequest"];
            };
        };
        responses: {
            /** @description Request successful. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Bad request. */
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    entities_certificates_set_default_create: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["SetDefaultCertificateRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["SetDefaultCertificateRequest"];
                "multipart/form-data": components["schemas"]["SetDefaultCertificateRequest"];
            };
        };
        responses: {
            /** @description Request successful. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Bad request. */
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    entities_certificates_update_certificate_create: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["UpdateCertificateRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["UpdateCertificateRequest"];
                "multipart/form-data": components["schemas"]["UpdateCertificateRequest"];
            };
        };
        responses: {
            /** @description Request successful. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Bad request. */
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    entities_depots_list: {
        parameters: {
            query: {
                /** @description Compay ID, Admin only */
                company_id?: number;
                /** @description Entity ID */
                entity_id: number;
                /** @description Which field to use when ordering the results. */
                ordering?: string;
                /** @description A search term. */
                search?: string;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["EntitySite"][];
                };
            };
        };
    };
    entities_depots_add_create: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["AddDepotRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["AddDepotRequest"];
                "multipart/form-data": components["schemas"]["AddDepotRequest"];
            };
        };
        responses: {
            /** @description Request successful. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Bad request. */
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    entities_depots_create_depot_create: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["CreateDepotRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["CreateDepotRequest"];
                "multipart/form-data": components["schemas"]["CreateDepotRequest"];
            };
        };
        responses: {
            /** @description Request successful. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Bad request. */
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    entities_depots_delete_depot_create: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["DeleteDepotRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["DeleteDepotRequest"];
                "multipart/form-data": components["schemas"]["DeleteDepotRequest"];
            };
        };
        responses: {
            /** @description Request successful. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Bad request. */
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    entities_direct_deliveries_create: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: {
            content: {
                "application/json": components["schemas"]["DirectDeliveriesRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["DirectDeliveriesRequest"];
                "multipart/form-data": components["schemas"]["DirectDeliveriesRequest"];
            };
        };
        responses: {
            /** @description Request successful. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Bad request. */
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    entities_elec_create: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: {
            content: {
                "application/json": components["schemas"]["ToggleElecRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["ToggleElecRequest"];
                "multipart/form-data": components["schemas"]["ToggleElecRequest"];
            };
        };
        responses: {
            /** @description Request successful. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Bad request. */
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    entities_notifications_list: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
                /** @description Which field to use when ordering the results. */
                ordering?: string;
                /** @description A search term. */
                search?: string;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["CarbureNotification"][];
                };
            };
        };
    };
    entities_notifications_ack_create: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["NotificationRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["NotificationRequest"];
                "multipart/form-data": components["schemas"]["NotificationRequest"];
            };
        };
        responses: {
            /** @description Request successful. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Bad request. */
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    entities_production_sites_list: {
        parameters: {
            query: {
                /** @description Entity ID */
                company_id?: number;
                /** @description Entity ID */
                entity_id: number;
                /** @description Which field to use when ordering the results. */
                ordering?: string;
                /** @description A page number within the paginated result set. */
                page?: number;
                /** @description Number of results to return per page. */
                page_size?: number;
                /** @description A search term. */
                search?: string;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["PaginatedEntityProductionSiteList"];
                };
            };
        };
    };
    entities_production_sites_create: {
        parameters: {
            query: {
                /** @description Entity ID */
                company_id?: number;
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["EntityProductionSiteWriteRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["EntityProductionSiteWriteRequest"];
                "multipart/form-data": components["schemas"]["EntityProductionSiteWriteRequest"];
            };
        };
        responses: {
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["EntityProductionSiteWrite"];
                };
            };
        };
    };
    entities_production_sites_retrieve: {
        parameters: {
            query: {
                /** @description Entity ID */
                company_id?: number;
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path: {
                /** @description A unique integer value identifying this Site de stockage de carburant. */
                id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["EntityProductionSite"];
                };
            };
        };
    };
    entities_production_sites_update: {
        parameters: {
            query: {
                /** @description Entity ID */
                company_id?: number;
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path: {
                /** @description A unique integer value identifying this Site de stockage de carburant. */
                id: number;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["EntityProductionSiteWriteRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["EntityProductionSiteWriteRequest"];
                "multipart/form-data": components["schemas"]["EntityProductionSiteWriteRequest"];
            };
        };
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["EntityProductionSiteWrite"];
                };
            };
        };
    };
    entities_production_sites_destroy: {
        parameters: {
            query: {
                /** @description Entity ID */
                company_id?: number;
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path: {
                /** @description A unique integer value identifying this Site de stockage de carburant. */
                id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description No response body */
            204: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    entities_production_sites_partial_update: {
        parameters: {
            query: {
                /** @description Entity ID */
                company_id?: number;
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path: {
                /** @description A unique integer value identifying this Site de stockage de carburant. */
                id: number;
            };
            cookie?: never;
        };
        requestBody?: {
            content: {
                "application/json": components["schemas"]["PatchedEntityProductionSiteWriteRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["PatchedEntityProductionSiteWriteRequest"];
                "multipart/form-data": components["schemas"]["PatchedEntityProductionSiteWriteRequest"];
            };
        };
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["EntityProductionSiteWrite"];
                };
            };
        };
    };
    entities_release_for_consumption_create: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: {
            content: {
                "application/json": components["schemas"]["ToggleRFCRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["ToggleRFCRequest"];
                "multipart/form-data": components["schemas"]["ToggleRFCRequest"];
            };
        };
        responses: {
            /** @description Request successful. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Bad request. */
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    entities_search_company_create: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["SeachCompanyRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["SeachCompanyRequest"];
                "multipart/form-data": components["schemas"]["SeachCompanyRequest"];
            };
        };
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ResponseData"];
                };
            };
        };
    };
    entities_stats_retrieve: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["StatsResponse"];
                };
            };
            /** @description Bad request. */
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    entities_stocks_create: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: {
            content: {
                "application/json": components["schemas"]["ToggleStocksRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["ToggleStocksRequest"];
                "multipart/form-data": components["schemas"]["ToggleStocksRequest"];
            };
        };
        responses: {
            /** @description Request successful. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Bad request. */
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    entities_trading_create: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: {
            content: {
                "application/json": components["schemas"]["ToggleTradingRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["ToggleTradingRequest"];
                "multipart/form-data": components["schemas"]["ToggleTradingRequest"];
            };
        };
        responses: {
            /** @description Request successful. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Bad request. */
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    entities_unit_create: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: {
            content: {
                "application/json": components["schemas"]["UnitRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["UnitRequest"];
                "multipart/form-data": components["schemas"]["UnitRequest"];
            };
        };
        responses: {
            /** @description Request successful. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Bad request. */
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    entities_update_entity_info_create: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: {
            content: {
                "application/json": components["schemas"]["UpdateEntityInfoRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["UpdateEntityInfoRequest"];
                "multipart/form-data": components["schemas"]["UpdateEntityInfoRequest"];
            };
        };
        responses: {
            /** @description Request successful. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Bad request. */
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    entities_users_accept_user_create: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["GrantAccessRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["GrantAccessRequest"];
                "multipart/form-data": components["schemas"]["GrantAccessRequest"];
            };
        };
        responses: {
            /** @description Request successful. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Bad request. */
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    entities_users_change_role_create: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ChangeRoleRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["ChangeRoleRequest"];
                "multipart/form-data": components["schemas"]["ChangeRoleRequest"];
            };
        };
        responses: {
            /** @description Request successful. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Bad request. */
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    entities_users_entity_rights_requests_retrieve: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["UserRightsResponse"];
                };
            };
        };
    };
    entities_users_invite_user_create: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["InviteUserRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["InviteUserRequest"];
                "multipart/form-data": components["schemas"]["InviteUserRequest"];
            };
        };
        responses: {
            /** @description Request successful. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Bad request. */
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    entities_users_revoke_access_create: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["RevokeUserRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["RevokeUserRequest"];
                "multipart/form-data": components["schemas"]["RevokeUserRequest"];
            };
        };
        responses: {
            /** @description Request successful. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Bad request. */
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    entities_users_rights_requests_list: {
        parameters: {
            query: {
                /** @description Filter by entity ID. */
                company_id?: number;
                /** @description Entity ID */
                entity_id: number;
                /** @description Which field to use when ordering the results. */
                ordering?: string;
                /** @description Search in user email or entity name. */
                q?: string;
                /** @description A search term. */
                search?: string;
                /** @description Comma-separated list of statuses (e.g., active,pending). */
                statuses?: string[];
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["UserRightsRequests"][];
                };
            };
        };
    };
    entities_users_update_right_request_create: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["UpdateRightsRequestsRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["UpdateRightsRequestsRequest"];
                "multipart/form-data": components["schemas"]["UpdateRightsRequestsRequest"];
            };
        };
        responses: {
            /** @description Request successful. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Bad request. */
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    entities_users_update_user_role_create: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["UpdateUserRoleRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["UpdateUserRoleRequest"];
                "multipart/form-data": components["schemas"]["UpdateUserRoleRequest"];
            };
        };
        responses: {
            /** @description Request successful. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Bad request. */
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    nav_stats_retrieve: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["NavStats"];
                };
            };
        };
    };
    resources_airports_list: {
        parameters: {
            query?: {
                /** @description Public Only */
                public_only?: boolean;
                /** @description Search within the fields `name`, `icao_code` and `city` */
                query?: string;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Airport"][];
                };
            };
        };
    };
    resources_biofuels_list: {
        parameters: {
            query?: {
                /** @description Search within the fields `name`, `name_en`, and `code` */
                query?: string;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Biofuel"][];
                };
            };
        };
    };
    resources_certificates_list: {
        parameters: {
            query?: {
                /** @description Only return certificates valid at the given date */
                date?: string;
                /** @description Search within the fields `certificate_id` and `certificate_holder` */
                query?: string;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["GenericCertificate"][];
                };
            };
        };
    };
    resources_countries_list: {
        parameters: {
            query?: {
                /** @description Search within the fields `name`, `name_en` and `code_pays` */
                query?: string;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Country"][];
                };
            };
        };
    };
    resources_depots_list: {
        parameters: {
            query?: {
                /** @description Public Only */
                public_only?: boolean;
                /** @description Search within the fields `name`, `name_en` and `code_pays` */
                query?: string;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Depot"][];
                };
            };
        };
    };
    resources_entities_list: {
        parameters: {
            query?: {
                /** @description Only show entities allowed to be tiruert */
                allowed_tiruert?: boolean;
                /** @description Only keep specific entity types */
                entity_type?: string[];
                /** @description Only show enabled entities */
                is_enabled?: boolean;
                /** @description Only show liable entities */
                is_tiruert_liable?: boolean;
                /** @description Search within the field `name` */
                query?: string;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["EntityPreview"][];
                };
            };
        };
    };
    resources_feedstocks_list: {
        parameters: {
            query?: {
                /** @description Double compte only */
                double_count_only?: boolean;
                /** @description Search within the fields `name`, `name_en` and `code` */
                query?: string;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["FeedStock"][];
                };
            };
        };
    };
    resources_production_sites_list: {
        parameters: {
            query?: {
                /** @description Search within the field `producer_id` */
                producer_id?: number;
                /** @description Search within the field `name` */
                query?: string;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ProductionSite"][];
                };
            };
        };
    };
    resources_systeme_national_list: {
        parameters: {
            query?: {
                query?: string;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["GenericCertificate"][];
                };
            };
        };
    };
    saf_clients_list: {
        parameters: {
            query?: {
                /** @description Which field to use when ordering the results. */
                ordering?: string;
                /** @description A page number within the paginated result set. */
                page?: number;
                /** @description Number of results to return per page. */
                page_size?: number;
                /** @description A search term. */
                search?: string;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["PaginatedEntityPreviewList"];
                };
            };
        };
    };
    saf_clients_retrieve: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["EntityPreview"];
                };
            };
        };
    };
    saf_snapshot_retrieve: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
                /** @description Year */
                year: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": {
                        ticket_sources_available: number;
                        ticket_sources_history: number;
                        tickets_assigned: number;
                        tickets_assigned_pending: number;
                        tickets_assigned_accepted: number;
                        tickets_assigned_rejected: number;
                        tickets_received: number;
                        tickets_received_pending: number;
                        tickets_received_accepted: number;
                    };
                };
            };
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorResponse"];
                };
            };
        };
    };
    saf_ticket_sources_list: {
        parameters: {
            query: {
                added_by?: string[];
                client?: string[];
                country_of_origin?: string[];
                delivery_site?: string[];
                /** @description Entity ID */
                entity_id: number;
                feedstock?: string[];
                /** @description Ordre
                 *
                 *     * `volume` - Volume
                 *     * `-volume` - Volume (décroissant)
                 *     * `period` - Period
                 *     * `-period` - Period (décroissant)
                 *     * `feedstock` - Feedstock
                 *     * `-feedstock` - Feedstock (décroissant)
                 *     * `ghg_reduction` - Ghg reduction
                 *     * `-ghg_reduction` - Ghg reduction (décroissant)
                 *     * `added_by` - Added by
                 *     * `-added_by` - Added by (décroissant) */
                order_by?: PathsApiSafTicketSourcesGetParametersQueryOrder_by[];
                /** @description Which field to use when ordering the results. */
                ordering?: string;
                /** @description A page number within the paginated result set. */
                page?: number;
                /** @description Number of results to return per page. */
                page_size?: number;
                period?: number[];
                production_site?: string[];
                /** @description A search term. */
                search?: string;
                /** @description * `HISTORY` - HISTORY
                 *     * `AVAILABLE` - AVAILABLE */
                status?: PathsApiSafTicketSourcesGetParametersQueryStatus;
                /** @description List of suppliers provided via ?suppliers=supplier1&suppliers=supplier2&suppliers=supplier3 */
                supplier?: string[];
                year?: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["PaginatedSafTicketSourcePreviewList"];
                };
            };
        };
    };
    saf_ticket_sources_retrieve: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path: {
                /** @description A unique integer value identifying this Tickets source SAF. */
                id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["SafTicketSource"];
                };
            };
        };
    };
    saf_ticket_sources_assign_create: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path: {
                /** @description A unique integer value identifying this Tickets source SAF. */
                id: number;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["SafTicketSourceAssignmentRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["SafTicketSourceAssignmentRequest"];
                "multipart/form-data": components["schemas"]["SafTicketSourceAssignmentRequest"];
            };
        };
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["SafTicketSourceAssignment"];
                };
            };
        };
    };
    saf_ticket_sources_export_retrieve: {
        parameters: {
            query: {
                added_by?: string[];
                client?: string[];
                country_of_origin?: string[];
                delivery_site?: string[];
                /** @description Entity ID */
                entity_id: number;
                feedstock?: string[];
                /** @description Ordre
                 *
                 *     * `volume` - Volume
                 *     * `-volume` - Volume (décroissant)
                 *     * `period` - Period
                 *     * `-period` - Period (décroissant)
                 *     * `feedstock` - Feedstock
                 *     * `-feedstock` - Feedstock (décroissant)
                 *     * `ghg_reduction` - Ghg reduction
                 *     * `-ghg_reduction` - Ghg reduction (décroissant)
                 *     * `added_by` - Added by
                 *     * `-added_by` - Added by (décroissant) */
                order_by?: PathsApiSafTicketSourcesGetParametersQueryOrder_by[];
                /** @description Which field to use when ordering the results. */
                ordering?: string;
                period?: number[];
                production_site?: string[];
                /** @description A search term. */
                search?: string;
                /** @description * `HISTORY` - HISTORY
                 *     * `AVAILABLE` - AVAILABLE */
                status?: PathsApiSafTicketSourcesGetParametersQueryStatus;
                /** @description List of suppliers provided via ?suppliers=supplier1&suppliers=supplier2&suppliers=supplier3 */
                supplier?: string[];
                year?: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/vnd.ms-excel": string;
                };
            };
        };
    };
    saf_ticket_sources_filters_retrieve: {
        parameters: {
            query: {
                added_by?: string[];
                client?: string[];
                country_of_origin?: string[];
                delivery_site?: string[];
                /** @description Entity ID */
                entity_id: number;
                feedstock?: string[];
                /** @description Filter string to apply */
                filter?: string;
                /** @description Ordre
                 *
                 *     * `volume` - Volume
                 *     * `-volume` - Volume (décroissant)
                 *     * `period` - Period
                 *     * `-period` - Period (décroissant)
                 *     * `feedstock` - Feedstock
                 *     * `-feedstock` - Feedstock (décroissant)
                 *     * `ghg_reduction` - Ghg reduction
                 *     * `-ghg_reduction` - Ghg reduction (décroissant)
                 *     * `added_by` - Added by
                 *     * `-added_by` - Added by (décroissant) */
                order_by?: PathsApiSafTicketSourcesGetParametersQueryOrder_by[];
                /** @description Which field to use when ordering the results. */
                ordering?: string;
                period?: number[];
                production_site?: string[];
                /** @description A search term. */
                search?: string;
                /** @description * `HISTORY` - HISTORY
                 *     * `AVAILABLE` - AVAILABLE */
                status?: PathsApiSafTicketSourcesGetParametersQueryStatus;
                /** @description List of suppliers provided via ?suppliers=supplier1&suppliers=supplier2&suppliers=supplier3 */
                supplier?: string[];
                year?: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": string[];
                };
            };
        };
    };
    saf_ticket_sources_group_assign_create: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["SafTicketSourceGroupAssignmentRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["SafTicketSourceGroupAssignmentRequest"];
                "multipart/form-data": components["schemas"]["SafTicketSourceGroupAssignmentRequest"];
            };
        };
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["GroupAssignmentResponse"];
                };
            };
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorResponse"];
                };
            };
        };
    };
    saf_tickets_list: {
        parameters: {
            query: {
                biofuel?: string[];
                client?: string[];
                /** @description * `MAC` - MAC
                 *     * `MAC_DECLASSEMENT` - MAC_DECLASSEMENT */
                consumption_type?: PathsApiSafTicketsGetParametersQueryConsumption_type[];
                country_of_origin?: string[];
                /** @description Entity ID */
                entity_id: number;
                feedstock?: string[];
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
                 *     * `supplier` - Supplier
                 *     * `-supplier` - Supplier (décroissant)
                 *     * `consumption_type` - Consumption type
                 *     * `-consumption_type` - Consumption type (décroissant)
                 *     * `reception_airport` - Reception airport
                 *     * `-reception_airport` - Reception airport (décroissant) */
                order_by?: PathsApiSafTicketsGetParametersQueryOrder_by[];
                /** @description Which field to use when ordering the results. */
                ordering?: string;
                /** @description A page number within the paginated result set. */
                page?: number;
                /** @description Number of results to return per page. */
                page_size?: number;
                period?: number[];
                production_site?: string[];
                reception_airport?: string[];
                /** @description A search term. */
                search?: string;
                /** @description * `PENDING` - En attente
                 *     * `ACCEPTED` - Accepté
                 *     * `REJECTED` - Refusé */
                status?: PathsApiSafTicketsGetParametersQueryStatus;
                supplier?: string[];
                year?: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["PaginatedSafTicketPreviewList"];
                };
            };
        };
    };
    saf_tickets_retrieve: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path: {
                /** @description A unique integer value identifying this Ticket SAF. */
                id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["SafTicket"];
                };
            };
        };
    };
    saf_tickets_accept_create: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path: {
                /** @description A unique integer value identifying this Ticket SAF. */
                id: number;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["AcceptRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["AcceptRequest"];
                "multipart/form-data": components["schemas"]["AcceptRequest"];
            };
        };
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorResponse"];
                };
            };
        };
    };
    saf_tickets_cancel_create: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path: {
                /** @description A unique integer value identifying this Ticket SAF. */
                id: number;
            };
            cookie?: never;
        };
        requestBody?: {
            content: {
                "application/json": components["schemas"]["CommentRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["CommentRequest"];
                "multipart/form-data": components["schemas"]["CommentRequest"];
            };
        };
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorResponse"];
                };
            };
        };
    };
    saf_tickets_credit_source_create: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path: {
                /** @description A unique integer value identifying this Ticket SAF. */
                id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["SafTicket"];
                };
            };
        };
    };
    saf_tickets_reject_create: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path: {
                /** @description A unique integer value identifying this Ticket SAF. */
                id: number;
            };
            cookie?: never;
        };
        requestBody?: {
            content: {
                "application/json": components["schemas"]["CommentRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["CommentRequest"];
                "multipart/form-data": components["schemas"]["CommentRequest"];
            };
        };
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorResponse"];
                };
            };
        };
    };
    saf_tickets_export_retrieve: {
        parameters: {
            query: {
                biofuel?: string[];
                client?: string[];
                /** @description * `MAC` - MAC
                 *     * `MAC_DECLASSEMENT` - MAC_DECLASSEMENT */
                consumption_type?: PathsApiSafTicketsGetParametersQueryConsumption_type[];
                country_of_origin?: string[];
                /** @description Entity ID */
                entity_id: number;
                feedstock?: string[];
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
                 *     * `supplier` - Supplier
                 *     * `-supplier` - Supplier (décroissant)
                 *     * `consumption_type` - Consumption type
                 *     * `-consumption_type` - Consumption type (décroissant)
                 *     * `reception_airport` - Reception airport
                 *     * `-reception_airport` - Reception airport (décroissant) */
                order_by?: PathsApiSafTicketsGetParametersQueryOrder_by[];
                /** @description Which field to use when ordering the results. */
                ordering?: string;
                period?: number[];
                production_site?: string[];
                reception_airport?: string[];
                /** @description A search term. */
                search?: string;
                /** @description * `PENDING` - En attente
                 *     * `ACCEPTED` - Accepté
                 *     * `REJECTED` - Refusé */
                status?: PathsApiSafTicketsGetParametersQueryStatus;
                supplier?: string[];
                year?: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/vnd.ms-excel": string;
                };
            };
        };
    };
    saf_tickets_filters_retrieve: {
        parameters: {
            query: {
                biofuel?: string[];
                client?: string[];
                /** @description * `MAC` - MAC
                 *     * `MAC_DECLASSEMENT` - MAC_DECLASSEMENT */
                consumption_type?: PathsApiSafTicketsGetParametersQueryConsumption_type[];
                country_of_origin?: string[];
                /** @description Entity ID */
                entity_id: number;
                feedstock?: string[];
                /** @description Filter string to apply */
                filter?: string;
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
                 *     * `supplier` - Supplier
                 *     * `-supplier` - Supplier (décroissant)
                 *     * `consumption_type` - Consumption type
                 *     * `-consumption_type` - Consumption type (décroissant)
                 *     * `reception_airport` - Reception airport
                 *     * `-reception_airport` - Reception airport (décroissant) */
                order_by?: PathsApiSafTicketsGetParametersQueryOrder_by[];
                /** @description Which field to use when ordering the results. */
                ordering?: string;
                period?: number[];
                production_site?: string[];
                reception_airport?: string[];
                /** @description A search term. */
                search?: string;
                /** @description * `PENDING` - En attente
                 *     * `ACCEPTED` - Accepté
                 *     * `REJECTED` - Refusé */
                status?: PathsApiSafTicketsGetParametersQueryStatus;
                supplier?: string[];
                year?: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": string[];
                };
            };
        };
    };
    saf_years_retrieve: {
        parameters: {
            query: {
                /** @description Entity ID */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": number[];
                };
            };
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorResponse"];
                };
            };
        };
    };
    admin_objectives: {
        parameters: {
            query: {
                /** @description Date from which to calculate balance for teneur */
                date_from: string;
                /** @description Date to which to calculate balance for teneur */
                date_to: string;
                /** @description Authorised entity ID. */
                entity_id: number;
                /** @description Year of the objectives */
                year: string;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description All agregated objectives for all liable enttities. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ObjectiveOutput"];
                };
            };
        };
    };
    admin_objectives_entity: {
        parameters: {
            query: {
                /** @description Date from which to calculate balance for teneur */
                date_from: string;
                /** @description Date to which to calculate balance for teneur */
                date_to: string;
                /** @description Authorised entity ID. */
                entity_id: number;
                /** @description Entity's objectives. */
                selected_entity_id: number;
                /** @description Year of the objectives */
                year: string;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description All objectives. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ObjectiveOutput"];
                };
            };
        };
    };
    list_elec_operations: {
        parameters: {
            query: {
                date_from?: string;
                date_to?: string;
                /** @description Include detailed information if set to `1`. */
                details?: boolean;
                /** @description Authorised entity ID. */
                entity_id: number;
                from_to?: string;
                operation?: PathsApiTiruertElecOperationsGetParametersQueryOperation[];
                /** @description Ordre
                 *
                 *     * `created_at` - Created at
                 *     * `-created_at` - Created at (décroissant)
                 *     * `operation` - Operation
                 *     * `-operation` - Operation (décroissant)
                 *     * `status` - Status
                 *     * `-status` - Status (décroissant)
                 *     * `period` - Period
                 *     * `-period` - Period (décroissant)
                 *     * `quantity` - Quantity
                 *     * `-quantity` - Quantity (décroissant)
                 *     * `from_to` - From to
                 *     * `-from_to` - From to (décroissant) */
                order_by?: PathsApiTiruertElecOperationsGetParametersQueryOrder_by[];
                /** @description A page number within the paginated result set. */
                page?: number;
                /** @description Number of results to return per page. */
                page_size?: number;
                period?: string[];
                status?: PathsApiTiruertElecOperationsGetParametersQueryStatus[];
                type?: PathsApiTiruertElecOperationsGetParametersQueryType[];
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description A list of operations. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["PaginatedElecOperationListList"];
                };
            };
        };
    };
    create_elec_operation: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ElecOperationInputRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["ElecOperationInputRequest"];
                "multipart/form-data": components["schemas"]["ElecOperationInputRequest"];
            };
        };
        responses: {
            /** @description The newly created operation. */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ElecOperationList"];
                };
            };
            /** @description Invalid input data. */
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    get_elec_operation: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
            };
            header?: never;
            path: {
                /** @description A unique integer value identifying this Opération électricité. */
                id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Details of specific operation. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ElecOperation"];
                };
            };
        };
    };
    delete_elec_operation: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
            };
            header?: never;
            path: {
                /** @description A unique integer value identifying this Opération électricité. */
                id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Operation deleted successfully. */
            204: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Forbidden. The operation type or status does not allow deletion. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    update_elec_operation: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
            };
            header?: never;
            path: {
                /** @description A unique integer value identifying this Opération électricité. */
                id: number;
            };
            cookie?: never;
        };
        requestBody?: {
            content: {
                "application/json": components["schemas"]["PatchedElecOperationUpdateRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["PatchedElecOperationUpdateRequest"];
                "multipart/form-data": components["schemas"]["PatchedElecOperationUpdateRequest"];
            };
        };
        responses: {
            /** @description The updated operation. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ElecOperation"];
                };
            };
            /** @description Invalid input data. */
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    accept_elec_operation: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
            };
            header?: never;
            path: {
                /** @description A unique integer value identifying this Opération électricité. */
                id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Success message */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Error message */
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Error message */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    reject_elec_operation: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
            };
            header?: never;
            path: {
                /** @description A unique integer value identifying this Opération électricité. */
                id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Success message */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Error message */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    list_elec_balance: {
        parameters: {
            query: {
                /** @description Date from when to calculate teneur and quantity */
                date_from?: string;
                date_to?: string;
                /** @description Authorised entity ID. */
                entity_id: number;
                from_to?: string;
                operation?: PathsApiTiruertElecOperationsGetParametersQueryOperation[];
                /** @description Ordre
                 *
                 *     * `created_at` - Created at
                 *     * `-created_at` - Created at (décroissant)
                 *     * `operation` - Operation
                 *     * `-operation` - Operation (décroissant)
                 *     * `status` - Status
                 *     * `-status` - Status (décroissant)
                 *     * `period` - Period
                 *     * `-period` - Period (décroissant)
                 *     * `quantity` - Quantity
                 *     * `-quantity` - Quantity (décroissant)
                 *     * `from_to` - From to
                 *     * `-from_to` - From to (décroissant) */
                order_by?: PathsApiTiruertElecOperationsGetParametersQueryOrder_by[];
                /** @description A page number within the paginated result set. */
                page?: number;
                /** @description Number of results to return per page. */
                page_size?: number;
                period?: string[];
                status?: PathsApiTiruertElecOperationsGetParametersQueryStatus[];
                type?: PathsApiTiruertElecOperationsGetParametersQueryType[];
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["PaginatedElecBalanceList"];
                };
            };
        };
    };
    filter_elec_operations: {
        parameters: {
            query: {
                date_from?: string;
                date_to?: string;
                /** @description Authorised entity ID. */
                entity_id: number;
                /** @description Filter string to apply */
                filter: PathsApiTiruertElecOperationsFiltersGetParametersQueryFilter;
                from_to?: string;
                operation?: PathsApiTiruertElecOperationsGetParametersQueryOperation[];
                /** @description Ordre
                 *
                 *     * `created_at` - Created at
                 *     * `-created_at` - Created at (décroissant)
                 *     * `operation` - Operation
                 *     * `-operation` - Operation (décroissant)
                 *     * `status` - Status
                 *     * `-status` - Status (décroissant)
                 *     * `period` - Period
                 *     * `-period` - Period (décroissant)
                 *     * `quantity` - Quantity
                 *     * `-quantity` - Quantity (décroissant)
                 *     * `from_to` - From to
                 *     * `-from_to` - From to (décroissant) */
                order_by?: PathsApiTiruertElecOperationsGetParametersQueryOrder_by[];
                period?: string[];
                status?: PathsApiTiruertElecOperationsGetParametersQueryStatus[];
                type?: PathsApiTiruertElecOperationsGetParametersQueryType[];
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": string[];
                };
            };
        };
    };
    declare_elec_teneur: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Success message */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Error message */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    tiruert_mac_fossil_fuel_export_retrieve: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": string;
                };
            };
        };
    };
    objectives: {
        parameters: {
            query: {
                /** @description Date from which to calculate balance for teneur */
                date_from: string;
                /** @description Date to which to calculate balance for teneur */
                date_to: string;
                /** @description Authorised entity ID. */
                entity_id: number;
                /** @description Year of the objectives */
                year: string;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description All objectives. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ObjectiveOutput"];
                };
            };
        };
    };
    list_operations: {
        parameters: {
            query: {
                biofuel?: string[];
                /** @description * `CONV` - Conventionnel
                 *     * `ANN-IX-A` - ANNEXE IX-A
                 *     * `ANN-IX-B` - ANNEXE IX-B
                 *     * `TALLOL` - Tallol
                 *     * `OTHER` - Autre
                 *     * `EP2AM` - EP2AM */
                customs_category?: PathsApiTiruertOperationsGetParametersQueryCustoms_category[];
                date_from?: string;
                date_to?: string;
                depot?: string[];
                /** @description Include detailed information if set to `1`. */
                details?: boolean;
                /** @description Authorised entity ID. */
                entity_id: number;
                from_to?: string;
                /** @description * `INCORPORATION` - INCORPORATION
                 *     * `CESSION` - CESSION
                 *     * `TENEUR` - TENEUR
                 *     * `LIVRAISON_DIRECTE` - LIVRAISON_DIRECTE
                 *     * `MAC_BIO` - MAC_BIO
                 *     * `EXPORTATION` - EXPORTATION
                 *     * `EXPEDITION` - EXPEDITION
                 *     * `DEVALUATION` - DEVALUATION
                 *     * `CUSTOMS_CORRECTION` - CUSTOMS_CORRECTION
                 *     * `TRANSFERT` - TRANSFERT
                 *     * `ACQUISITION` - ACQUISITION */
                operation?: PathsApiTiruertOperationsGetParametersQueryOperation[];
                /** @description Ordre
                 *
                 *     * `status` - Status
                 *     * `-status` - Status (décroissant)
                 *     * `created_at` - Created at
                 *     * `-created_at` - Created at (décroissant)
                 *     * `sector` - Sector
                 *     * `-sector` - Sector (décroissant)
                 *     * `biofuel` - Biofuel
                 *     * `-biofuel` - Biofuel (décroissant)
                 *     * `customs_category` - Customs category
                 *     * `-customs_category` - Customs category (décroissant)
                 *     * `type` - Type
                 *     * `-type` - Type (décroissant)
                 *     * `depot` - Depot
                 *     * `-depot` - Depot (décroissant)
                 *     * `from_to` - From to
                 *     * `-from_to` - From to (décroissant)
                 *     * `quantity` - Quantity
                 *     * `-quantity` - Quantity (décroissant)
                 *     * `available_balance` - available_balance
                 *     * `-available_balance` - available_balance (descending)
                 *     * `pending_operations` - pending_operations
                 *     * `-pending_operations` - pending_operations (descending)
                 *     * `saved_emissions` - saved_emissions
                 *     * `-saved_emissions` - saved_emissions (descending) */
                order_by?: PathsApiTiruertOperationsGetParametersQueryOrder_by[];
                /** @description A page number within the paginated result set. */
                page?: number;
                /** @description Number of results to return per page. */
                page_size?: number;
                period?: string[];
                /** @description * `ESSENCE` - ESSENCE
                 *     * `GAZOLE` - GAZOLE
                 *     * `CARBURÉACTEUR` - CARBURÉACTEUR */
                sector?: PathsApiTiruertOperationsGetParametersQuerySector[];
                /** @description * `PENDING` - PENDING
                 *     * `ACCEPTED` - ACCEPTED
                 *     * `REJECTED` - REJECTED
                 *     * `CANCELED` - CANCELED
                 *     * `DECLARED` - DECLARED
                 *     * `CORRECTED` - CORRECTED
                 *     * `VALIDATED` - VALIDATED
                 *     * `DRAFT` - DRAFT */
                status?: PathsApiTiruertOperationsGetParametersQueryStatus[];
                /** @description * `CREDIT` - CREDIT
                 *     * `DEBIT` - DEBIT */
                type?: PathsApiTiruertElecOperationsGetParametersQueryType[];
                /** @description Specify the volume unit. */
                unit?: PathsApiTiruertOperationsGetParametersQueryUnit;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description A list of operations. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["PaginatedOperationListList"];
                };
            };
        };
    };
    create_operation: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
                /** @description Specify the volume unit. */
                unit?: PathsApiTiruertOperationsGetParametersQueryUnit;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["OperationInputRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["OperationInputRequest"];
                "multipart/form-data": components["schemas"]["OperationInputRequest"];
            };
        };
        responses: {
            /** @description The newly created operation. */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["OperationList"];
                };
            };
            /** @description Invalid input data. */
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    get_operation: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
                /** @description Specify the volume unit. */
                unit?: PathsApiTiruertOperationsGetParametersQueryUnit;
            };
            header?: never;
            path: {
                /** @description A unique integer value identifying this Opération. */
                id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Details of specific operation. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Operation"];
                };
            };
        };
    };
    delete_operation: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
                /** @description Specify the volume unit. */
                unit?: PathsApiTiruertOperationsGetParametersQueryUnit;
            };
            header?: never;
            path: {
                /** @description A unique integer value identifying this Opération. */
                id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Operation deleted successfully. */
            204: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Forbidden. The operation type or status does not allow deletion. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    update_operation: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
                /** @description Specify the volume unit. */
                unit?: PathsApiTiruertOperationsGetParametersQueryUnit;
            };
            header?: never;
            path: {
                /** @description A unique integer value identifying this Opération. */
                id: number;
            };
            cookie?: never;
        };
        requestBody?: {
            content: {
                "application/json": components["schemas"]["PatchedOperationUpdateRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["PatchedOperationUpdateRequest"];
                "multipart/form-data": components["schemas"]["PatchedOperationUpdateRequest"];
            };
        };
        responses: {
            /** @description The updated operation. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Operation"];
                };
            };
            /** @description Invalid input data. */
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    accept_operation: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
                /** @description Specify the volume unit. */
                unit?: PathsApiTiruertOperationsGetParametersQueryUnit;
            };
            header?: never;
            path: {
                /** @description A unique integer value identifying this Opération. */
                id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Success message */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Error message */
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Error message */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    correct_operation: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
                /** @description Specify the volume unit. */
                unit?: PathsApiTiruertOperationsGetParametersQueryUnit;
            };
            header?: never;
            path: {
                /** @description A unique integer value identifying this Opération. */
                id: number;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["OperationCorrectionRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["OperationCorrectionRequest"];
                "multipart/form-data": components["schemas"]["OperationCorrectionRequest"];
            };
        };
        responses: {
            /** @description Success message */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Error message */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    reject_operation: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
                /** @description Specify the volume unit. */
                unit?: PathsApiTiruertOperationsGetParametersQueryUnit;
            };
            header?: never;
            path: {
                /** @description A unique integer value identifying this Opération. */
                id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Success message */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Error message */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    list_balances: {
        parameters: {
            query: {
                biofuel?: string[];
                /** @description * `CONV` - Conventionnel
                 *     * `ANN-IX-A` - ANNEXE IX-A
                 *     * `ANN-IX-B` - ANNEXE IX-B
                 *     * `TALLOL` - Tallol
                 *     * `OTHER` - Autre
                 *     * `EP2AM` - EP2AM */
                customs_category?: PathsApiTiruertOperationsGetParametersQueryCustoms_category[];
                /** @description Date from where to calculate teneur and quantity */
                date_from?: string;
                date_to?: string;
                depot?: string[];
                /** @description Authorised entity ID. */
                entity_id: number;
                from_to?: string;
                ges_bound_max?: number;
                ges_bound_min?: number;
                /** @description Group by sector, lot or depot. */
                group_by?: PathsApiTiruertOperationsBalanceGetParametersQueryGroup_by;
                /** @description * `INCORPORATION` - INCORPORATION
                 *     * `CESSION` - CESSION
                 *     * `TENEUR` - TENEUR
                 *     * `LIVRAISON_DIRECTE` - LIVRAISON_DIRECTE
                 *     * `MAC_BIO` - MAC_BIO
                 *     * `EXPORTATION` - EXPORTATION
                 *     * `EXPEDITION` - EXPEDITION
                 *     * `DEVALUATION` - DEVALUATION
                 *     * `CUSTOMS_CORRECTION` - CUSTOMS_CORRECTION
                 *     * `TRANSFERT` - TRANSFERT
                 *     * `ACQUISITION` - ACQUISITION */
                operation?: PathsApiTiruertOperationsGetParametersQueryOperation[];
                /** @description Ordre
                 *
                 *     * `status` - Status
                 *     * `-status` - Status (décroissant)
                 *     * `created_at` - Created at
                 *     * `-created_at` - Created at (décroissant)
                 *     * `sector` - Sector
                 *     * `-sector` - Sector (décroissant)
                 *     * `biofuel` - Biofuel
                 *     * `-biofuel` - Biofuel (décroissant)
                 *     * `customs_category` - Customs category
                 *     * `-customs_category` - Customs category (décroissant)
                 *     * `type` - Type
                 *     * `-type` - Type (décroissant)
                 *     * `depot` - Depot
                 *     * `-depot` - Depot (décroissant)
                 *     * `from_to` - From to
                 *     * `-from_to` - From to (décroissant)
                 *     * `quantity` - Quantity
                 *     * `-quantity` - Quantity (décroissant)
                 *     * `available_balance` - available_balance
                 *     * `-available_balance` - available_balance (descending)
                 *     * `pending_operations` - pending_operations
                 *     * `-pending_operations` - pending_operations (descending)
                 *     * `saved_emissions` - saved_emissions
                 *     * `-saved_emissions` - saved_emissions (descending) */
                order_by?: PathsApiTiruertOperationsGetParametersQueryOrder_by[];
                /** @description A page number within the paginated result set. */
                page?: number;
                /** @description Number of results to return per page. */
                page_size?: number;
                period?: string[];
                /** @description * `ESSENCE` - ESSENCE
                 *     * `GAZOLE` - GAZOLE
                 *     * `CARBURÉACTEUR` - CARBURÉACTEUR */
                sector?: PathsApiTiruertOperationsGetParametersQuerySector[];
                /** @description * `PENDING` - PENDING
                 *     * `ACCEPTED` - ACCEPTED
                 *     * `REJECTED` - REJECTED
                 *     * `CANCELED` - CANCELED
                 *     * `DECLARED` - DECLARED
                 *     * `CORRECTED` - CORRECTED
                 *     * `VALIDATED` - VALIDATED
                 *     * `DRAFT` - DRAFT */
                status?: PathsApiTiruertOperationsGetParametersQueryStatus[];
                /** @description * `CREDIT` - CREDIT
                 *     * `DEBIT` - DEBIT */
                type?: PathsApiTiruertElecOperationsGetParametersQueryType[];
                /** @description Specify the volume unit. */
                unit?: PathsApiTiruertOperationsGetParametersQueryUnit;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["PaginatedBalanceResponseList"];
                };
            };
        };
    };
    filter_balances: {
        parameters: {
            query: {
                biofuel?: string[];
                /** @description * `CONV` - Conventionnel
                 *     * `ANN-IX-A` - ANNEXE IX-A
                 *     * `ANN-IX-B` - ANNEXE IX-B
                 *     * `TALLOL` - Tallol
                 *     * `OTHER` - Autre
                 *     * `EP2AM` - EP2AM */
                customs_category?: PathsApiTiruertOperationsGetParametersQueryCustoms_category[];
                date_from?: string;
                date_to?: string;
                depot?: string[];
                /** @description Authorised entity ID. */
                entity_id: number;
                /** @description Filter string to apply */
                filter: PathsApiTiruertOperationsBalanceFiltersGetParametersQueryFilter;
                from_to?: string;
                /** @description * `INCORPORATION` - INCORPORATION
                 *     * `CESSION` - CESSION
                 *     * `TENEUR` - TENEUR
                 *     * `LIVRAISON_DIRECTE` - LIVRAISON_DIRECTE
                 *     * `MAC_BIO` - MAC_BIO
                 *     * `EXPORTATION` - EXPORTATION
                 *     * `EXPEDITION` - EXPEDITION
                 *     * `DEVALUATION` - DEVALUATION
                 *     * `CUSTOMS_CORRECTION` - CUSTOMS_CORRECTION
                 *     * `TRANSFERT` - TRANSFERT
                 *     * `ACQUISITION` - ACQUISITION */
                operation?: PathsApiTiruertOperationsGetParametersQueryOperation[];
                /** @description Ordre
                 *
                 *     * `status` - Status
                 *     * `-status` - Status (décroissant)
                 *     * `created_at` - Created at
                 *     * `-created_at` - Created at (décroissant)
                 *     * `sector` - Sector
                 *     * `-sector` - Sector (décroissant)
                 *     * `biofuel` - Biofuel
                 *     * `-biofuel` - Biofuel (décroissant)
                 *     * `customs_category` - Customs category
                 *     * `-customs_category` - Customs category (décroissant)
                 *     * `type` - Type
                 *     * `-type` - Type (décroissant)
                 *     * `depot` - Depot
                 *     * `-depot` - Depot (décroissant)
                 *     * `from_to` - From to
                 *     * `-from_to` - From to (décroissant)
                 *     * `quantity` - Quantity
                 *     * `-quantity` - Quantity (décroissant)
                 *     * `available_balance` - available_balance
                 *     * `-available_balance` - available_balance (descending)
                 *     * `pending_operations` - pending_operations
                 *     * `-pending_operations` - pending_operations (descending)
                 *     * `saved_emissions` - saved_emissions
                 *     * `-saved_emissions` - saved_emissions (descending) */
                order_by?: PathsApiTiruertOperationsGetParametersQueryOrder_by[];
                period?: string[];
                /** @description * `ESSENCE` - ESSENCE
                 *     * `GAZOLE` - GAZOLE
                 *     * `CARBURÉACTEUR` - CARBURÉACTEUR */
                sector?: PathsApiTiruertOperationsGetParametersQuerySector[];
                /** @description * `PENDING` - PENDING
                 *     * `ACCEPTED` - ACCEPTED
                 *     * `REJECTED` - REJECTED
                 *     * `CANCELED` - CANCELED
                 *     * `DECLARED` - DECLARED
                 *     * `CORRECTED` - CORRECTED
                 *     * `VALIDATED` - VALIDATED
                 *     * `DRAFT` - DRAFT */
                status?: PathsApiTiruertOperationsGetParametersQueryStatus[];
                /** @description * `CREDIT` - CREDIT
                 *     * `DEBIT` - DEBIT */
                type?: PathsApiTiruertElecOperationsGetParametersQueryType[];
                /** @description Specify the volume unit. */
                unit?: PathsApiTiruertOperationsGetParametersQueryUnit;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": string[];
                };
            };
        };
    };
    tiruert_operations_export_retrieve: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
                /** @description Specify the volume unit. */
                unit?: PathsApiTiruertOperationsGetParametersQueryUnit;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["OperationList"];
                };
            };
        };
    };
    filter_operations: {
        parameters: {
            query: {
                biofuel?: string[];
                /** @description * `CONV` - Conventionnel
                 *     * `ANN-IX-A` - ANNEXE IX-A
                 *     * `ANN-IX-B` - ANNEXE IX-B
                 *     * `TALLOL` - Tallol
                 *     * `OTHER` - Autre
                 *     * `EP2AM` - EP2AM */
                customs_category?: PathsApiTiruertOperationsGetParametersQueryCustoms_category[];
                date_from?: string;
                date_to?: string;
                depot?: string[];
                /** @description Authorised entity ID. */
                entity_id: number;
                /** @description Filter string to apply */
                filter: PathsApiTiruertOperationsFiltersGetParametersQueryFilter;
                from_to?: string;
                /** @description * `INCORPORATION` - INCORPORATION
                 *     * `CESSION` - CESSION
                 *     * `TENEUR` - TENEUR
                 *     * `LIVRAISON_DIRECTE` - LIVRAISON_DIRECTE
                 *     * `MAC_BIO` - MAC_BIO
                 *     * `EXPORTATION` - EXPORTATION
                 *     * `EXPEDITION` - EXPEDITION
                 *     * `DEVALUATION` - DEVALUATION
                 *     * `CUSTOMS_CORRECTION` - CUSTOMS_CORRECTION
                 *     * `TRANSFERT` - TRANSFERT
                 *     * `ACQUISITION` - ACQUISITION */
                operation?: PathsApiTiruertOperationsGetParametersQueryOperation[];
                /** @description Ordre
                 *
                 *     * `status` - Status
                 *     * `-status` - Status (décroissant)
                 *     * `created_at` - Created at
                 *     * `-created_at` - Created at (décroissant)
                 *     * `sector` - Sector
                 *     * `-sector` - Sector (décroissant)
                 *     * `biofuel` - Biofuel
                 *     * `-biofuel` - Biofuel (décroissant)
                 *     * `customs_category` - Customs category
                 *     * `-customs_category` - Customs category (décroissant)
                 *     * `type` - Type
                 *     * `-type` - Type (décroissant)
                 *     * `depot` - Depot
                 *     * `-depot` - Depot (décroissant)
                 *     * `from_to` - From to
                 *     * `-from_to` - From to (décroissant)
                 *     * `quantity` - Quantity
                 *     * `-quantity` - Quantity (décroissant)
                 *     * `available_balance` - available_balance
                 *     * `-available_balance` - available_balance (descending)
                 *     * `pending_operations` - pending_operations
                 *     * `-pending_operations` - pending_operations (descending)
                 *     * `saved_emissions` - saved_emissions
                 *     * `-saved_emissions` - saved_emissions (descending) */
                order_by?: PathsApiTiruertOperationsGetParametersQueryOrder_by[];
                period?: string[];
                /** @description * `ESSENCE` - ESSENCE
                 *     * `GAZOLE` - GAZOLE
                 *     * `CARBURÉACTEUR` - CARBURÉACTEUR */
                sector?: PathsApiTiruertOperationsGetParametersQuerySector[];
                /** @description * `PENDING` - PENDING
                 *     * `ACCEPTED` - ACCEPTED
                 *     * `REJECTED` - REJECTED
                 *     * `CANCELED` - CANCELED
                 *     * `DECLARED` - DECLARED
                 *     * `CORRECTED` - CORRECTED
                 *     * `VALIDATED` - VALIDATED
                 *     * `DRAFT` - DRAFT */
                status?: PathsApiTiruertOperationsGetParametersQueryStatus[];
                /** @description * `CREDIT` - CREDIT
                 *     * `DEBIT` - DEBIT */
                type?: PathsApiTiruertElecOperationsGetParametersQueryType[];
                /** @description Specify the volume unit. */
                unit?: PathsApiTiruertOperationsGetParametersQueryUnit;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": string[];
                };
            };
        };
    };
    simulate: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
                /** @description Specify the volume unit. */
                unit?: PathsApiTiruertOperationsGetParametersQueryUnit;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["SimulationInputRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["SimulationInputRequest"];
                "multipart/form-data": components["schemas"]["SimulationInputRequest"];
            };
        };
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["SimulationOutput"];
                };
            };
        };
    };
    simulation_bounds: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
                /** @description Specify the volume unit. */
                unit?: PathsApiTiruertOperationsGetParametersQueryUnit;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["SimulationMinMaxInputRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["SimulationMinMaxInputRequest"];
                "multipart/form-data": components["schemas"]["SimulationMinMaxInputRequest"];
            };
        };
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["SimulationMinMaxOutput"];
                };
            };
        };
    };
    declare_teneur: {
        parameters: {
            query: {
                /** @description Authorised entity ID. */
                entity_id: number;
                /** @description Specify the volume unit. */
                unit?: PathsApiTiruertOperationsGetParametersQueryUnit;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Success message */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Error message */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    token_create: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["TokenObtainPairRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["TokenObtainPairRequest"];
                "multipart/form-data": components["schemas"]["TokenObtainPairRequest"];
            };
        };
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TokenObtainPair"];
                };
            };
        };
    };
    token_refresh_create: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["TokenRefreshRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["TokenRefreshRequest"];
                "multipart/form-data": components["schemas"]["TokenRefreshRequest"];
            };
        };
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TokenRefresh"];
                };
            };
        };
    };
    user_retrieve: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["UserSettingsResponse"];
                };
            };
        };
    };
    user_request_access_create: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["RequestAccessRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["RequestAccessRequest"];
                "multipart/form-data": components["schemas"]["RequestAccessRequest"];
            };
        };
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ResponseSuccess"];
                };
            };
        };
    };
    user_revoke_access_create: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["RevokeAccessRequest"];
                "application/x-www-form-urlencoded": components["schemas"]["RevokeAccessRequest"];
                "multipart/form-data": components["schemas"]["RevokeAccessRequest"];
            };
        };
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ResponseSuccess"];
                };
            };
        };
    };
}
export enum PathsApiBiomethaneSupplyInputGetParametersQueryCategory {
    CIVE = "CIVE",
    IAA_WASTE_RESIDUES = "IAA_WASTE_RESIDUES",
    INTERMEDIATE_CROPS = "INTERMEDIATE_CROPS",
    LIVESTOCK_EFFLUENTS = "LIVESTOCK_EFFLUENTS",
    PRIMARY_CROPS = "PRIMARY_CROPS"
}
export enum PathsApiBiomethaneSupplyInputGetParametersQuerySource {
    EXTERNAL = "EXTERNAL",
    INTERNAL = "INTERNAL"
}
export enum PathsApiBiomethaneSupplyInputFiltersGetParametersQueryFilter {
    category = "category",
    source = "source",
    type = "type",
    year = "year"
}
export enum PathsApiDoubleCountingAgreementsGetParametersQueryOrder_by {
    ValueMinuscertificate_id = "-certificate_id",
    ValueMinusproducer = "-producer",
    ValueMinusproduction_site = "-production_site",
    ValueMinusvalid_until = "-valid_until",
    certificate_id = "certificate_id",
    producer = "producer",
    production_site = "production_site",
    valid_until = "valid_until"
}
export enum PathsApiDoubleCountingApplicationsFiltersGetParametersQueryOrder_by {
    ValueMinuscertificate_id = "-certificate_id",
    ValueMinuscreated_at = "-created_at",
    ValueMinusproducer = "-producer",
    ValueMinusproduction_site = "-production_site",
    ValueMinusvalid_until = "-valid_until",
    certificate_id = "certificate_id",
    created_at = "created_at",
    producer = "producer",
    production_site = "production_site",
    valid_until = "valid_until"
}
export enum PathsApiElecProvisionCertificatesGetParametersQueryOrder_by {
    ValueMinuscpo = "-cpo",
    ValueMinusoperating_unit = "-operating_unit",
    ValueMinusquarter = "-quarter",
    ValueMinusremaining_energy_amount = "-remaining_energy_amount",
    ValueMinussource = "-source",
    cpo = "cpo",
    operating_unit = "operating_unit",
    quarter = "quarter",
    remaining_energy_amount = "remaining_energy_amount",
    source = "source"
}
export enum PathsApiElecProvisionCertificatesGetParametersQueryQuarter {
    Value1 = 1,
    Value2 = 2,
    Value3 = 3,
    Value4 = 4
}
export enum PathsApiElecProvisionCertificatesGetParametersQuerySource {
    MANUAL = "MANUAL",
    METER_READINGS = "METER_READINGS",
    QUALICHARGE = "QUALICHARGE"
}
export enum PathsApiElecProvisionCertificatesQualichargeGetParametersQueryValidated_by {
    BOTH = "BOTH",
    CPO = "CPO",
    DGEC = "DGEC",
    NO_ONE = "NO_ONE"
}
export enum PathsApiElecProvisionCertificatesQualichargeFiltersGetParametersQueryFilter {
    cpo = "cpo",
    date_from = "date_from",
    operating_unit = "operating_unit",
    station_id = "station_id",
    validated_by = "validated_by",
    year = "year"
}
export enum PathsApiElecProvisionCertificatesFiltersGetParametersQueryFilter {
    cpo = "cpo",
    energy_amount = "energy_amount",
    operating_unit = "operating_unit",
    order_by = "order_by",
    quarter = "quarter",
    source = "source",
    year = "year"
}
export enum PathsApiElecTransferCertificatesGetParametersQueryOrder_by {
    ValueMinuscertificate_id = "-certificate_id",
    ValueMinusconsumption_date = "-consumption_date",
    ValueMinuscpo = "-cpo",
    ValueMinusenergy_amount = "-energy_amount",
    ValueMinusoperator = "-operator",
    ValueMinusstatus = "-status",
    ValueMinustransfer_date = "-transfer_date",
    certificate_id = "certificate_id",
    consumption_date = "consumption_date",
    cpo = "cpo",
    energy_amount = "energy_amount",
    operator = "operator",
    status = "status",
    transfer_date = "transfer_date"
}
export enum PathsApiElecTransferCertificatesFiltersGetParametersQueryFilter {
    certificate_id = "certificate_id",
    client = "client",
    consumption_date = "consumption_date",
    cpo = "cpo",
    energy_amount = "energy_amount",
    month = "month",
    operator = "operator",
    order_by = "order_by",
    status = "status",
    supplier = "supplier",
    transfer_date = "transfer_date",
    used_in_tiruert = "used_in_tiruert",
    year = "year"
}
export enum PathsApiSafTicketSourcesGetParametersQueryOrder_by {
    ValueMinusadded_by = "-added_by",
    ValueMinusfeedstock = "-feedstock",
    ValueMinusghg_reduction = "-ghg_reduction",
    ValueMinusperiod = "-period",
    ValueMinusvolume = "-volume",
    added_by = "added_by",
    feedstock = "feedstock",
    ghg_reduction = "ghg_reduction",
    period = "period",
    volume = "volume"
}
export enum PathsApiSafTicketSourcesGetParametersQueryStatus {
    AVAILABLE = "AVAILABLE",
    HISTORY = "HISTORY"
}
export enum PathsApiSafTicketsGetParametersQueryConsumption_type {
    MAC = "MAC",
    MAC_DECLASSEMENT = "MAC_DECLASSEMENT"
}
export enum PathsApiSafTicketsGetParametersQueryOrder_by {
    ValueMinusclient = "-client",
    ValueMinusconsumption_type = "-consumption_type",
    ValueMinuscreated_at = "-created_at",
    ValueMinusfeedstock = "-feedstock",
    ValueMinusghg_reduction = "-ghg_reduction",
    ValueMinusperiod = "-period",
    ValueMinusreception_airport = "-reception_airport",
    ValueMinussupplier = "-supplier",
    ValueMinusvolume = "-volume",
    client = "client",
    consumption_type = "consumption_type",
    created_at = "created_at",
    feedstock = "feedstock",
    ghg_reduction = "ghg_reduction",
    period = "period",
    reception_airport = "reception_airport",
    supplier = "supplier",
    volume = "volume"
}
export enum PathsApiSafTicketsGetParametersQueryStatus {
    ACCEPTED = "ACCEPTED",
    PENDING = "PENDING",
    REJECTED = "REJECTED"
}
export enum PathsApiTiruertElecOperationsGetParametersQueryOperation {
    ACQUISITION_FROM_CPO = "ACQUISITION_FROM_CPO",
    CESSION = "CESSION",
    TENEUR = "TENEUR",
    ACQUISITION = "ACQUISITION"
}
export enum PathsApiTiruertElecOperationsGetParametersQueryOrder_by {
    ValueMinuscreated_at = "-created_at",
    ValueMinusfrom_to = "-from_to",
    ValueMinusoperation = "-operation",
    ValueMinusperiod = "-period",
    ValueMinusquantity = "-quantity",
    ValueMinusstatus = "-status",
    created_at = "created_at",
    from_to = "from_to",
    operation = "operation",
    period = "period",
    quantity = "quantity",
    status = "status"
}
export enum PathsApiTiruertElecOperationsGetParametersQueryStatus {
    PENDING = "PENDING",
    ACCEPTED = "ACCEPTED",
    REJECTED = "REJECTED",
    CANCELED = "CANCELED",
    DECLARED = "DECLARED"
}
export enum PathsApiTiruertElecOperationsGetParametersQueryType {
    CREDIT = "CREDIT",
    DEBIT = "DEBIT"
}
export enum PathsApiTiruertElecOperationsFiltersGetParametersQueryFilter {
    from_to = "from_to",
    operation = "operation",
    period = "period",
    status = "status",
    type = "type"
}
export enum PathsApiTiruertOperationsGetParametersQueryCustoms_category {
    ANN_IX_A = "ANN-IX-A",
    ANN_IX_B = "ANN-IX-B",
    CONV = "CONV",
    EP2AM = "EP2AM",
    OTHER = "OTHER",
    TALLOL = "TALLOL"
}
export enum PathsApiTiruertOperationsGetParametersQueryOperation {
    ACQUISITION = "ACQUISITION",
    CESSION = "CESSION",
    CUSTOMS_CORRECTION = "CUSTOMS_CORRECTION",
    DEVALUATION = "DEVALUATION",
    EXPEDITION = "EXPEDITION",
    EXPORTATION = "EXPORTATION",
    INCORPORATION = "INCORPORATION",
    LIVRAISON_DIRECTE = "LIVRAISON_DIRECTE",
    MAC_BIO = "MAC_BIO",
    TENEUR = "TENEUR",
    TRANSFERT = "TRANSFERT"
}
export enum PathsApiTiruertOperationsGetParametersQueryOrder_by {
    ValueMinusavailable_balance = "-available_balance",
    ValueMinusbiofuel = "-biofuel",
    ValueMinuscreated_at = "-created_at",
    ValueMinuscustoms_category = "-customs_category",
    ValueMinusdepot = "-depot",
    ValueMinusfrom_to = "-from_to",
    ValueMinuspending_operations = "-pending_operations",
    ValueMinusquantity = "-quantity",
    ValueMinussaved_emissions = "-saved_emissions",
    ValueMinussector = "-sector",
    ValueMinusstatus = "-status",
    ValueMinustype = "-type",
    available_balance = "available_balance",
    biofuel = "biofuel",
    created_at = "created_at",
    customs_category = "customs_category",
    depot = "depot",
    from_to = "from_to",
    pending_operations = "pending_operations",
    quantity = "quantity",
    saved_emissions = "saved_emissions",
    sector = "sector",
    status = "status",
    type = "type"
}
export enum PathsApiTiruertOperationsGetParametersQuerySector {
    CARBUR_ACTEUR = "CARBUR\u00C9ACTEUR",
    ESSENCE = "ESSENCE",
    GAZOLE = "GAZOLE"
}
export enum PathsApiTiruertOperationsGetParametersQueryStatus {
    ACCEPTED = "ACCEPTED",
    CANCELED = "CANCELED",
    CORRECTED = "CORRECTED",
    DECLARED = "DECLARED",
    DRAFT = "DRAFT",
    PENDING = "PENDING",
    REJECTED = "REJECTED",
    VALIDATED = "VALIDATED"
}
export enum PathsApiTiruertOperationsGetParametersQueryUnit {
    MJ = "MJ",
    kg = "kg",
    l = "l"
}
export enum PathsApiTiruertOperationsBalanceGetParametersQueryGroup_by {
    depot = "depot",
    lot = "lot",
    sector = "sector"
}
export enum PathsApiTiruertOperationsBalanceFiltersGetParametersQueryFilter {
    biofuel = "biofuel",
    customs_category = "customs_category",
    sector = "sector"
}
export enum PathsApiTiruertOperationsFiltersGetParametersQueryFilter {
    biofuel = "biofuel",
    customs_category = "customs_category",
    depot = "depot",
    from_to = "from_to",
    operation = "operation",
    period = "period",
    sector = "sector",
    status = "status",
    type = "type"
}
export enum AmendmentObjectEnum {
    CMAX_PAP_UPDATE = "CMAX_PAP_UPDATE",
    EFFECTIVE_DATE = "EFFECTIVE_DATE",
    CMAX_ANNUALIZATION = "CMAX_ANNUALIZATION",
    INPUT_BONUS_UPDATE = "INPUT_BONUS_UPDATE",
    L_INDEXATION_UPDATE = "L_INDEXATION_UPDATE",
    PRODUCER_BUYER_INFO_CHANGE = "PRODUCER_BUYER_INFO_CHANGE",
    ENERGY_ENVIRONMENTAL_EFFICIENCY_UPDATE = "ENERGY_ENVIRONMENTAL_EFFICIENCY_UPDATE",
    OTHER = "OTHER"
}
export enum BiomethaneAnnualDeclarationStatusEnum {
    PENDING = "PENDING",
    DECLARED = "DECLARED"
}
export enum BiomethaneDigestateStatusEnum {
    PENDING = "PENDING",
    VALIDATED = "VALIDATED"
}
export enum CarbureNotificationTypeEnum {
    CORRECTION_REQUEST = "CORRECTION_REQUEST",
    CORRECTION_DONE = "CORRECTION_DONE",
    LOTS_REJECTED = "LOTS_REJECTED",
    LOTS_RECEIVED = "LOTS_RECEIVED",
    LOTS_RECALLED = "LOTS_RECALLED",
    CERTIFICATE_EXPIRED = "CERTIFICATE_EXPIRED",
    CERTIFICATE_REJECTED = "CERTIFICATE_REJECTED",
    DECLARATION_VALIDATED = "DECLARATION_VALIDATED",
    DECLARATION_CANCELLED = "DECLARATION_CANCELLED",
    METER_READINGS_APP_STARTED = "METER_READINGS_APP_STARTED",
    METER_READINGS_APP_ENDING_SOON = "METER_READINGS_APP_ENDING_SOON",
    DECLARATION_REMINDER = "DECLARATION_REMINDER",
    SAF_TICKET_REJECTED = "SAF_TICKET_REJECTED",
    SAF_TICKET_ACCEPTED = "SAF_TICKET_ACCEPTED",
    SAF_TICKET_RECEIVED = "SAF_TICKET_RECEIVED",
    LOTS_UPDATED_BY_ADMIN = "LOTS_UPDATED_BY_ADMIN",
    LOTS_DELETED_BY_ADMIN = "LOTS_DELETED_BY_ADMIN",
    ELEC_TRANSFER_CERTIFICATE = "ELEC_TRANSFER_CERTIFICATE"
}
export enum CertificateTypeEnum {
    SYSTEME_NATIONAL = "SYSTEME_NATIONAL",
    ISCC = "ISCC",
    REDCERT = "REDCERT",
    Value2BS = "2BS"
}
export enum CompostingLocationsEnum {
    ON_SITE = "ON_SITE",
    EXTERNAL_PLATFORM = "EXTERNAL_PLATFORM"
}
export enum CorrectionStatusEnum {
    NO_PROBLEMO = "NO_PROBLEMO",
    IN_CORRECTION = "IN_CORRECTION",
    FIXED = "FIXED"
}
export enum CropTypeEnum {
    MAIN = "MAIN",
    INTERMEDIATE = "INTERMEDIATE"
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
    CONSUMPTION = "CONSUMPTION"
}
export enum DigestateSaleTypeEnum {
    DIG_AGRI_SPECIFICATIONS = "DIG_AGRI_SPECIFICATIONS",
    HOMOLOGATION = "HOMOLOGATION",
    STANDARDIZED_PRODUCT = "STANDARDIZED_PRODUCT"
}
export enum DigestateValorizationMethodsEnum {
    SPREADING = "SPREADING",
    COMPOSTING = "COMPOSTING",
    INCINERATION_LANDFILLING = "INCINERATION_LANDFILLING"
}
export enum DoubleCountingAgreementStatus {
    ACTIVE = "ACTIVE",
    EXPIRED = "EXPIRED",
    EXPIRES_SOON = "EXPIRES_SOON",
    INCOMING = "INCOMING"
}
export enum DoubleCountingStatus {
    PENDING = "PENDING",
    INPROGRESS = "INPROGRESS",
    REJECTED = "REJECTED",
    ACCEPTED = "ACCEPTED"
}
export enum ElecBalanceSectorEnum {
    ELEC = "ELEC"
}
export enum ElecOperationTypeEnum {
    ACQUISITION_FROM_CPO = "ACQUISITION_FROM_CPO",
    CESSION = "CESSION",
    TENEUR = "TENEUR"
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
    SAF_Trader = "SAF Trader",
    Producteur_de_biom_thane = "Producteur de biom\u00E9thane"
}
export enum EtsStatusEnum {
    ETS_VALUATION = "ETS_VALUATION",
    OUTSIDE_ETS = "OUTSIDE_ETS",
    NOT_CONCERNED = "NOT_CONCERNED"
}
export enum ExtAdminPagesEnum {
    DCA = "DCA",
    AGRIMER = "AGRIMER",
    TIRIB = "TIRIB",
    AIRLINE = "AIRLINE",
    ELEC = "ELEC",
    TRANSFERRED_ELEC = "TRANSFERRED_ELEC",
    BIOFUEL = "BIOFUEL"
}
export enum FileTypeEnum {
    EXCEL = "EXCEL",
    EXTRA = "EXTRA",
    DECISION = "DECISION"
}
export enum GesOptionEnum {
    Default = "Default",
    Actual = "Actual",
    NUTS2 = "NUTS2"
}
export enum HygienizationExemptionTypeEnum {
    TOTAL = "TOTAL",
    PARTIAL = "PARTIAL"
}
export enum IcpeRegimeEnum {
    AUTHORIZATION = "AUTHORIZATION",
    REGISTRATION = "REGISTRATION",
    DECLARATION_PERIODIC_CONTROLS = "DECLARATION_PERIODIC_CONTROLS"
}
export enum InstallationCategoryEnum {
    INSTALLATION_CATEGORY_1 = "INSTALLATION_CATEGORY_1",
    INSTALLATION_CATEGORY_2 = "INSTALLATION_CATEGORY_2",
    INSTALLATION_CATEGORY_3 = "INSTALLATION_CATEGORY_3"
}
export enum InstalledMetersEnum {
    BIOGAS_PRODUCTION_FLOWMETER = "BIOGAS_PRODUCTION_FLOWMETER",
    PURIFICATION_FLOWMETER = "PURIFICATION_FLOWMETER",
    FLARING_FLOWMETER = "FLARING_FLOWMETER",
    HEATING_FLOWMETER = "HEATING_FLOWMETER",
    PURIFICATION_ELECTRICAL_METER = "PURIFICATION_ELECTRICAL_METER",
    GLOBAL_ELECTRICAL_METER = "GLOBAL_ELECTRICAL_METER"
}
export enum LotStatusEnum {
    DRAFT = "DRAFT",
    PENDING = "PENDING",
    ACCEPTED = "ACCEPTED",
    REJECTED = "REJECTED",
    FROZEN = "FROZEN",
    DELETED = "DELETED"
}
export enum MalfunctionTypesEnum {
    CONCEPTION = "CONCEPTION",
    MAINTENANCE = "MAINTENANCE",
    BIOLOGICAL = "BIOLOGICAL",
    ACCIDENT = "ACCIDENT",
    PURIFIER = "PURIFIER",
    INJECTION_POST = "INJECTION_POST",
    INPUTS = "INPUTS",
    OTHER = "OTHER"
}
export enum MaterialUnitEnum {
    DRY = "DRY",
    WET = "WET"
}
export enum MethanizationProcessEnum {
    CONTINUOUS_INFINITELY_MIXED = "CONTINUOUS_INFINITELY_MIXED",
    PLUG_FLOW_SEMI_CONTINUOUS = "PLUG_FLOW_SEMI_CONTINUOUS",
    BATCH_SILOS = "BATCH_SILOS"
}
export enum NetworkTypeEnum {
    TRANSPORT = "TRANSPORT",
    DISTRIBUTION = "DISTRIBUTION"
}
export enum OperationTypeEnum {
    INCORPORATION = "INCORPORATION",
    CESSION = "CESSION",
    TENEUR = "TENEUR",
    LIVRAISON_DIRECTE = "LIVRAISON_DIRECTE",
    MAC_BIO = "MAC_BIO",
    EXPORTATION = "EXPORTATION",
    EXPEDITION = "EXPEDITION",
    DEVALUATION = "DEVALUATION",
    CUSTOMS_CORRECTION = "CUSTOMS_CORRECTION",
    TRANSFERT = "TRANSFERT"
}
export enum OwnershipTypeEnum {
    OWN = "OWN",
    THIRD_PARTY = "THIRD_PARTY",
    PROCESSING = "PROCESSING"
}
export enum ProcessTypeEnum {
    LIQUID_PROCESS = "LIQUID_PROCESS",
    DRY_PROCESS = "DRY_PROCESS"
}
export enum RoleEnum {
    ReadOnly = "RO",
    ReadWrite = "RW",
    Admin = "ADMIN",
    Auditor = "AUDITOR"
}
export enum ShippingMethodEnum {
    PIPELINE = "PIPELINE",
    TRUCK = "TRUCK",
    TRAIN = "TRAIN",
    BARGE = "BARGE"
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
    AIRPORT = "AIRPORT"
}
export enum SpreadingManagementMethodsEnum {
    DIRECT_SPREADING = "DIRECT_SPREADING",
    SPREADING_VIA_PROVIDER = "SPREADING_VIA_PROVIDER",
    TRANSFER = "TRANSFER",
    SALE = "SALE"
}
export enum TariffReferenceEnum {
    Value2011 = "2011",
    Value2020 = "2020",
    Value2021 = "2021",
    Value2023 = "2023"
}
export enum TrackedAmendmentTypesEnum {
    CMAX_PAP_UPDATE = "CMAX_PAP_UPDATE",
    CMAX_ANNUALIZATION = "CMAX_ANNUALIZATION",
    PRODUCER_BUYER_INFO_CHANGE = "PRODUCER_BUYER_INFO_CHANGE"
}
export enum TransportDocumentTypeEnum {
    DAU = "DAU",
    DAE = "DAE",
    DSA = "DSA",
    DSAC = "DSAC",
    DSP = "DSP",
    OTHER = "OTHER"
}
export enum UnitTypeEnum {
    AGRICULTURAL_AUTONOMOUS = "AGRICULTURAL_AUTONOMOUS",
    AGRICULTURAL_TERRITORIAL = "AGRICULTURAL_TERRITORIAL",
    INDUSTRIAL_TERRITORIAL = "INDUSTRIAL_TERRITORIAL",
    HOUSEHOLD_WASTE_BIOWASTE = "HOUSEHOLD_WASTE_BIOWASTE",
    ISDND = "ISDND"
}
export enum UserRightsRequestsStatusEnum {
    Pending = "PENDING",
    Accepted = "ACCEPTED",
    Rejected = "REJECTED",
    Revoked = "REVOKED"
}
