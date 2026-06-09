TABLE_CONFIG = {

    "Stamperia": {
        "refresh_query": "stamperia_refresh",
        "confirm_query": "stamperia_confirm",
        "disabled_cols": [
            "Id", "Ord_cam", "Chr_cam", "Num_scheda",
            "Specif", "Dimensioni", "Pz_richi", "Pz_stamp",
            "Data_stamp", "Temp_tot",
            "Mat_op_pesa", "Mat_op_misc", "Mat_op_press",
            "Data_valid",
        ],
        "editable_cols": ["Temp_pesa", "Temp_misc", "Temp_press", "Temp_assist_press", "Flag"],
        "update_sql": """
            UPDATE [Stamperia]
            SET [Temp_pesa]         = :Temp_pesa,
                [Temp_misc]         = :Temp_misc,
                [Temp_press]        = :Temp_press,
                [Temp_assist_press] = :Temp_assist_press,
                [Flag]              = :Flag
            WHERE [Id] = :Id
        """,
        "pk": "Id",
    },

    "Forno_cottura": {
        "refresh_query": "forno_cottura_refresh",
        "confirm_query": "forno_cottura_confirm",
        "disabled_cols": [
            "Id", "Ord_cam", "Chr_cam", "Num_scheda",
            "Specif", "Dimensioni", "Pz_richi",
            "Data_inforna", "Data_valid",
        ],
        "editable_cols": ["Pz_inforna", "Flag"],
        "update_sql": """
            UPDATE [Forno_cottura]
            SET [Pz_inforna] = :Pz_inforna,
                [Flag]       = :Flag
            WHERE [Id] = :Id
        """,
        "pk": "Id",
    },

    "Tornitura": {
        "refresh_query": "tornitura_refresh",
        "confirm_query": "tornitura_confirm",
        "disabled_cols": [
            "Id", "Ord_cam", "Chr_cam", "Num_scheda",
            "Specif", "Dimensioni", "Pz_richi", "Pz_lav",
            "Data_fine", "Temp_tot",
            "Mat_op_spian", "Mat_op_lapid", "Mat_op_ffi",
            "Mat_op_resin", "Mat_op_rett", "Mat_op_prof",
            "Data_valid",
        ],
        "editable_cols": [
            "Temp_spian", "Temp_lapid", "Temp_ffi",
            "Temp_rett", "Temp_prof", "Temp_resin", "Flag",
        ],
        "update_sql": """
            UPDATE [Tornitura]
            SET [Temp_spian] = :Temp_spian,
                [Temp_lapid] = :Temp_lapid,
                [Temp_ffi]   = :Temp_ffi,
                [Temp_rett]  = :Temp_rett,
                [Temp_prof]  = :Temp_prof,
                [Temp_resin] = :Temp_resin,
                [Flag]       = :Flag
            WHERE [Id] = :Id
        """,
        "pk": "Id",
    },

    "Collaudo": {
        "refresh_query": "collaudo_refresh",
        "confirm_query": "collaudo_confirm",
        "disabled_cols": [
            "Id", "Ord_cam", "Chr_cam", "Num_scheda",
            "Specif", "Dimensioni", "Pz_richi", "Pz_lav",
            "Data_fine", "Temp_tot",
            "Mat_op_sabb", "Mat_op_pul_sof", "Mat_op_bilanc",
            "Mat_op_velo", "Mat_op_marca", "Mat_op_chius",
            "Data_valid",
        ],
        "editable_cols": [
            "Temp_sabb", "Temp_pul_sof", "Temp_bilanc",
            "Temp_velo", "Temp_marca", "Temp_chius", "Flag",
        ],
        "update_sql": """
            UPDATE [Collaudo]
            SET [Temp_sabb]    = :Temp_sabb,
                [Temp_pul_sof] = :Temp_pul_sof,
                [Temp_bilanc]  = :Temp_bilanc,
                [Temp_velo]    = :Temp_velo,
                [Temp_marca]   = :Temp_marca,
                [Temp_chius]   = :Temp_chius,
                [Flag]         = :Flag
            WHERE [Id] = :Id
        """,
        "pk": "Id",
    },
}

REPORT_CONFIG: dict[str, dict] = {
    "Quadratura operatore":  {"inputs": ["date_range"],         "query": "report_quadratura"},
    "Pezzi discordanti":     {"inputs": ["date_range"],         "query": "report_pezzi_discordanti"},
    "Infornature parziali":  {"inputs": ["date_range"],         "query": "report_infornature_parziali"},
    "Riepilogo commesse":    {"inputs": ["date_range"],         "query": "report_riepilogo_commesse"},
    "Singola commessa":      {"inputs": ["ord_cam", "chr_cam"], "query": "report_singola_commessa"},
    "Imballate non evase":   {"inputs": [],                     "query": "report_imballate_non_evase"},
    "Impasti non pesati":    {"inputs": ["date_range"],         "query": "report_non_pesati"},
    "Impasti non miscelati": {"inputs": ["date_range"],         "query": "report_non_miscelati"},
    "Date fine Tornitura":   {"inputs": [],                     "query": "report_date_tornitura"},
    "Marcate non imballate": {"inputs": [],                     "query": "report_marcate_non_imballate"},
}

GROUP_TABLES: dict[str, list[str]] = {
    "Group 1": list(TABLE_CONFIG.keys()),
    "Group 2": list(REPORT_CONFIG.keys()),
}

# Role-based visibility: which tables/reports each role may access
ROLE_PERMISSIONS: dict[str, dict[str, list[str]]] = {
    "admin": {
        "tables":  list(TABLE_CONFIG.keys()),
        "reports": list(REPORT_CONFIG.keys()),
    },
    "operator": {
        "tables":  list(TABLE_CONFIG.keys()),
        "reports": list(REPORT_CONFIG.keys()),
    },
    "viewer": {
        "tables":  [],
        "reports": list(REPORT_CONFIG.keys()),
    },
}
