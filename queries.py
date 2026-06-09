# queries.py — Microsoft SQL Server (T-SQL)

_BASE_LAVORAZIONI = """
    WITH lav AS (
        SELECT
            COALESCE(u.[firstName] + ' ' + u.[lastName], 'N/D') AS [Operatore],
            a.[ORD_CAM] AS [Ord. Camfart], a.[CHR_CAM] AS [Chr. Camfart],
            a.[NUM_SCHEDA] AS [N° Scheda], a.[SPECIFICA] AS [Specifica],
            COALESCE(CAST(a.[DIAMETRO] AS VARCHAR(20)),'') + ' x ' +
            COALESCE(CAST(a.[SPESSORE] AS VARCHAR(20)),'') + ' x ' +
            COALESCE(CAST(a.[FORO] AS VARCHAR(20)),'') AS [Dimensioni],
            a.[PEZZI_RIC] AS [Pz. Richiesti], 1 AS [Fase],
            a.[N_PESAT] AS [N° Pz. Lavorati], CAST(a.[D_PESAT] AS DATE) AS [Data],
            a.[ORE_PESAT] AS [Tempo_h],
            ROUND(CAST((COALESCE(a.[PEZZI_RIC],0) * COALESCE(s.[PESO_UNIT],0))
                / NULLIF(COALESCE(a.[N_IMPASTI],1), 0)
                + COALESCE(s.[SFRIDO],0) AS DECIMAL(18,6)), 2) AS [Peso_Tot_kg],
            a.[N_COMPL_PRESS] AS [N° Pz. Stampati], a.[N_CARICATI_COTT] AS [N° Pz. Infornati]
        FROM c4_attivi a
        INNER JOIN t_schede s ON s.[NUM_SCHEDA] = a.[NUM_SCHEDA]
        LEFT JOIN c4_pesa p ON p.[ID_COMMESSA] = a.[ID]
        LEFT JOIN c4_utenti u ON u.[id] = p.[USER_ID]
        WHERE a.[D_PESAT] BETWEEN @date_from AND @date_to AND a.[N_PESAT] IS NOT NULL

        UNION ALL

        SELECT DISTINCT
            COALESCE(u.[firstName] + ' ' + u.[lastName], 'N/D'),
            a.[ORD_CAM], a.[CHR_CAM], a.[NUM_SCHEDA], a.[SPECIFICA],
            COALESCE(CAST(a.[DIAMETRO] AS VARCHAR(20)),'') + ' x ' +
            COALESCE(CAST(a.[SPESSORE] AS VARCHAR(20)),'') + ' x ' +
            COALESCE(CAST(a.[FORO] AS VARCHAR(20)),''),
            a.[PEZZI_RIC], 2, a.[N_MISC], CAST(a.[D_MISC] AS DATE), a.[ORE_MISC],
            ROUND(CAST((COALESCE(a.[PEZZI_RIC],0) * COALESCE(s.[PESO_UNIT],0))
                / NULLIF(COALESCE(a.[N_IMPASTI],1), 0)
                + COALESCE(s.[SFRIDO],0) AS DECIMAL(18,6)), 2),
            a.[N_COMPL_PRESS], a.[N_CARICATI_COTT]
        FROM c4_attivi a
        INNER JOIN c4_misc cm ON a.[ID] = cm.[ID_COMMESSA]
        INNER JOIN t_schede s ON a.[NUM_SCHEDA] = s.[NUM_SCHEDA]
        LEFT JOIN c4_utenti u ON u.[id] = cm.[USER_ID]
        WHERE a.[D_MISC] BETWEEN @date_from AND @date_to AND a.[N_MISC] IS NOT NULL

        UNION ALL

        SELECT DISTINCT
            COALESCE(u.[firstName] + ' ' + u.[lastName], 'N/D'),
            a.[ORD_CAM], a.[CHR_CAM], a.[NUM_SCHEDA], a.[SPECIFICA],
            COALESCE(CAST(a.[DIAMETRO] AS VARCHAR(20)),'') + ' x ' +
            COALESCE(CAST(a.[SPESSORE] AS VARCHAR(20)),'') + ' x ' +
            COALESCE(CAST(a.[FORO] AS VARCHAR(20)),''),
            a.[PEZZI_RIC], 3, a.[N_COMPL_PRESS], CAST(a.[D_PRESS] AS DATE), a.[ORE_PRESS],
            ROUND(CAST((COALESCE(a.[PEZZI_RIC],0) * COALESCE(s.[PESO_UNIT],0))
                / NULLIF(COALESCE(a.[N_IMPASTI],1), 0)
                + COALESCE(s.[SFRIDO],0) AS DECIMAL(18,6)), 2),
            a.[N_COMPL_PRESS], a.[N_CARICATI_COTT]
        FROM c4_attivi a
        INNER JOIN c4_press p ON a.[ID] = p.[ID_COMMESSA]
        INNER JOIN t_schede s ON a.[NUM_SCHEDA] = s.[NUM_SCHEDA]
        LEFT JOIN c4_utenti u ON u.[id] = p.[USER_ID]
        WHERE a.[D_PRESS] BETWEEN @date_from AND @date_to AND a.[N_COMPL_PRESS] IS NOT NULL

        UNION ALL

        SELECT DISTINCT 'N/D',
            a.[ORD_CAM], a.[CHR_CAM], a.[NUM_SCHEDA], a.[SPECIFICA],
            COALESCE(CAST(a.[DIAMETRO] AS VARCHAR(20)),'') + ' x ' +
            COALESCE(CAST(a.[SPESSORE] AS VARCHAR(20)),'') + ' x ' +
            COALESCE(CAST(a.[FORO] AS VARCHAR(20)),''),
            a.[PEZZI_RIC], 11, a.[N_CARICATI_COTT], CAST(a.[D_COTT] AS DATE), a.[ORE_COTT],
            ROUND(CAST((COALESCE(a.[PEZZI_RIC],0) * COALESCE(s.[PESO_UNIT],0))
                / NULLIF(COALESCE(a.[N_IMPASTI],1), 0)
                + COALESCE(s.[SFRIDO],0) AS DECIMAL(18,6)), 2),
            a.[N_COMPL_PRESS], a.[N_CARICATI_COTT]
        FROM c4_attivi a
        INNER JOIN t_schede s ON a.[NUM_SCHEDA] = s.[NUM_SCHEDA]
        WHERE a.[D_COTT] BETWEEN @date_from AND @date_to AND a.[N_CARICATI_COTT] IS NOT NULL

        UNION ALL

        SELECT DISTINCT
            COALESCE(u.[firstName] + ' ' + u.[lastName], 'N/D'),
            a.[ORD_CAM], a.[CHR_CAM], a.[NUM_SCHEDA], a.[SPECIFICA],
            COALESCE(CAST(a.[DIAMETRO] AS VARCHAR(20)),'') + ' x ' +
            COALESCE(CAST(a.[SPESSORE] AS VARCHAR(20)),'') + ' x ' +
            COALESCE(CAST(a.[FORO] AS VARCHAR(20)),''),
            a.[PEZZI_RIC],
            CASE t.[TIPO]
                WHEN 'Spianatura' THEN 21 WHEN 'Lapidello' THEN 22
                WHEN 'resinatura foro' THEN 23 WHEN 'Facce / foro / incavi' THEN 24
                WHEN 'Rettifica esterna' THEN 25 WHEN 'Profilatura' THEN 26
            END,
            a.[N_COMPL_TORN], CAST(a.[D_TORN] AS DATE), t.[TEMPO_LAVORAZIONE],
            ROUND(CAST((COALESCE(a.[PEZZI_RIC],0) * COALESCE(s.[PESO_UNIT],0))
                / NULLIF(COALESCE(a.[N_IMPASTI],1), 0)
                + COALESCE(s.[SFRIDO],0) AS DECIMAL(18,6)), 2),
            a.[N_COMPL_PRESS], a.[N_CARICATI_COTT]
        FROM c4_attivi a
        INNER JOIN c4_torn t ON a.[ID] = t.[ID_COMMESSA]
        INNER JOIN t_schede s ON a.[NUM_SCHEDA] = s.[NUM_SCHEDA]
        LEFT JOIN c4_utenti u ON u.[id] = t.[USER_ID]
        WHERE a.[D_TORN] BETWEEN @date_from AND @date_to
          AND t.[TIPO] IN ('Spianatura','Lapidello','resinatura foro',
                           'Facce / foro / incavi','Rettifica esterna','Profilatura')

        UNION ALL

        SELECT DISTINCT
            COALESCE(u.[firstName] + ' ' + u.[lastName], 'N/D'),
            a.[ORD_CAM], a.[CHR_CAM], a.[NUM_SCHEDA], a.[SPECIFICA],
            COALESCE(CAST(a.[DIAMETRO] AS VARCHAR(20)),'') + ' x ' +
            COALESCE(CAST(a.[SPESSORE] AS VARCHAR(20)),'') + ' x ' +
            COALESCE(CAST(a.[FORO] AS VARCHAR(20)),''),
            a.[PEZZI_RIC],
            CASE c.[TIPO]
                WHEN 'Pulizia / soffiaggio' THEN 31 WHEN 'Bilanciatura' THEN 32
                WHEN 'Marcatura' THEN 34 WHEN 'Imballaggio' THEN 35
            END,
            a.[N_COMPL_COLL], CAST(a.[D_COLL] AS DATE), c.[TEMPO_LAVORAZIONE],
            ROUND(CAST((COALESCE(a.[PEZZI_RIC],0) * COALESCE(s.[PESO_UNIT],0))
                / NULLIF(COALESCE(a.[N_IMPASTI],1), 0)
                + COALESCE(s.[SFRIDO],0) AS DECIMAL(18,6)), 2),
            a.[N_COMPL_PRESS], a.[N_CARICATI_COTT]
        FROM c4_attivi a
        INNER JOIN c4_coll c ON a.[ID] = c.[ID_COMMESSA]
        INNER JOIN t_schede s ON a.[NUM_SCHEDA] = s.[NUM_SCHEDA]
        LEFT JOIN c4_utenti u ON u.[id] = c.[USER_ID]
        WHERE a.[D_COLL] BETWEEN @date_from AND @date_to
          AND c.[TIPO] IN ('Pulizia / soffiaggio','Bilanciatura','Marcatura','Imballaggio')
    )
"""

_BASE_SINGOLA = """
    WITH lav AS (
        SELECT
            COALESCE(u.[firstName] + ' ' + u.[lastName], 'N/D') AS [Operatore],
            a.[ORD_CAM] AS [Ord. Camfart], a.[CHR_CAM] AS [Chr. Camfart],
            a.[NUM_SCHEDA] AS [N° Scheda], a.[SPECIFICA] AS [Specifica],
            COALESCE(CAST(a.[DIAMETRO] AS VARCHAR(20)),'') + ' x ' +
            COALESCE(CAST(a.[SPESSORE] AS VARCHAR(20)),'') + ' x ' +
            COALESCE(CAST(a.[FORO] AS VARCHAR(20)),'') AS [Dimensioni],
            a.[PEZZI_RIC] AS [Pz. Richiesti], 1 AS [Fase],
            a.[N_PESAT] AS [N° Pz. Lavorati], CAST(a.[D_PESAT] AS DATE) AS [Data],
            a.[ORE_PESAT] AS [Tempo_h],
            ROUND(CAST((COALESCE(a.[PEZZI_RIC],0) * COALESCE(s.[PESO_UNIT],0))
                / NULLIF(COALESCE(a.[N_IMPASTI],1), 0)
                + COALESCE(s.[SFRIDO],0) AS DECIMAL(18,6)), 2) AS [Peso_Tot_kg],
            a.[N_COMPL_PRESS] AS [N° Pz. Stampati], a.[N_CARICATI_COTT] AS [N° Pz. Infornati]
        FROM c4_attivi a
        INNER JOIN t_schede s ON s.[NUM_SCHEDA] = a.[NUM_SCHEDA]
        LEFT JOIN c4_pesa p ON p.[ID_COMMESSA] = a.[ID]
        LEFT JOIN c4_utenti u ON u.[id] = p.[USER_ID]
        WHERE a.[ORD_CAM] = @ord_cam AND a.[CHR_CAM] = @chr_cam AND a.[N_PESAT] IS NOT NULL

        UNION ALL

        SELECT DISTINCT
            COALESCE(u.[firstName] + ' ' + u.[lastName], 'N/D'),
            a.[ORD_CAM], a.[CHR_CAM], a.[NUM_SCHEDA], a.[SPECIFICA],
            COALESCE(CAST(a.[DIAMETRO] AS VARCHAR(20)),'') + ' x ' +
            COALESCE(CAST(a.[SPESSORE] AS VARCHAR(20)),'') + ' x ' +
            COALESCE(CAST(a.[FORO] AS VARCHAR(20)),''),
            a.[PEZZI_RIC], 2, a.[N_MISC], CAST(a.[D_MISC] AS DATE), a.[ORE_MISC],
            ROUND(CAST((COALESCE(a.[PEZZI_RIC],0) * COALESCE(s.[PESO_UNIT],0))
                / NULLIF(COALESCE(a.[N_IMPASTI],1), 0)
                + COALESCE(s.[SFRIDO],0) AS DECIMAL(18,6)), 2),
            a.[N_COMPL_PRESS], a.[N_CARICATI_COTT]
        FROM c4_attivi a
        INNER JOIN c4_misc cm ON a.[ID] = cm.[ID_COMMESSA]
        INNER JOIN t_schede s ON a.[NUM_SCHEDA] = s.[NUM_SCHEDA]
        LEFT JOIN c4_utenti u ON u.[id] = cm.[USER_ID]
        WHERE a.[ORD_CAM] = @ord_cam AND a.[CHR_CAM] = @chr_cam AND a.[N_MISC] IS NOT NULL

        UNION ALL

        SELECT DISTINCT
            COALESCE(u.[firstName] + ' ' + u.[lastName], 'N/D'),
            a.[ORD_CAM], a.[CHR_CAM], a.[NUM_SCHEDA], a.[SPECIFICA],
            COALESCE(CAST(a.[DIAMETRO] AS VARCHAR(20)),'') + ' x ' +
            COALESCE(CAST(a.[SPESSORE] AS VARCHAR(20)),'') + ' x ' +
            COALESCE(CAST(a.[FORO] AS VARCHAR(20)),''),
            a.[PEZZI_RIC], 3, a.[N_COMPL_PRESS], CAST(a.[D_PRESS] AS DATE), a.[ORE_PRESS],
            ROUND(CAST((COALESCE(a.[PEZZI_RIC],0) * COALESCE(s.[PESO_UNIT],0))
                / NULLIF(COALESCE(a.[N_IMPASTI],1), 0)
                + COALESCE(s.[SFRIDO],0) AS DECIMAL(18,6)), 2),
            a.[N_COMPL_PRESS], a.[N_CARICATI_COTT]
        FROM c4_attivi a
        INNER JOIN c4_press p ON a.[ID] = p.[ID_COMMESSA]
        INNER JOIN t_schede s ON a.[NUM_SCHEDA] = s.[NUM_SCHEDA]
        LEFT JOIN c4_utenti u ON u.[id] = p.[USER_ID]
        WHERE a.[ORD_CAM] = @ord_cam AND a.[CHR_CAM] = @chr_cam AND a.[N_COMPL_PRESS] IS NOT NULL

        UNION ALL

        SELECT DISTINCT 'N/D',
            a.[ORD_CAM], a.[CHR_CAM], a.[NUM_SCHEDA], a.[SPECIFICA],
            COALESCE(CAST(a.[DIAMETRO] AS VARCHAR(20)),'') + ' x ' +
            COALESCE(CAST(a.[SPESSORE] AS VARCHAR(20)),'') + ' x ' +
            COALESCE(CAST(a.[FORO] AS VARCHAR(20)),''),
            a.[PEZZI_RIC], 11, a.[N_CARICATI_COTT], CAST(a.[D_COTT] AS DATE), a.[ORE_COTT],
            ROUND(CAST((COALESCE(a.[PEZZI_RIC],0) * COALESCE(s.[PESO_UNIT],0))
                / NULLIF(COALESCE(a.[N_IMPASTI],1), 0)
                + COALESCE(s.[SFRIDO],0) AS DECIMAL(18,6)), 2),
            a.[N_COMPL_PRESS], a.[N_CARICATI_COTT]
        FROM c4_attivi a
        INNER JOIN t_schede s ON a.[NUM_SCHEDA] = s.[NUM_SCHEDA]
        WHERE a.[ORD_CAM] = @ord_cam AND a.[CHR_CAM] = @chr_cam AND a.[N_CARICATI_COTT] IS NOT NULL

        UNION ALL

        SELECT DISTINCT
            COALESCE(u.[firstName] + ' ' + u.[lastName], 'N/D'),
            a.[ORD_CAM], a.[CHR_CAM], a.[NUM_SCHEDA], a.[SPECIFICA],
            COALESCE(CAST(a.[DIAMETRO] AS VARCHAR(20)),'') + ' x ' +
            COALESCE(CAST(a.[SPESSORE] AS VARCHAR(20)),'') + ' x ' +
            COALESCE(CAST(a.[FORO] AS VARCHAR(20)),''),
            a.[PEZZI_RIC],
            CASE t.[TIPO]
                WHEN 'Spianatura' THEN 21 WHEN 'Lapidello' THEN 22
                WHEN 'resinatura foro' THEN 23 WHEN 'Facce / foro / incavi' THEN 24
                WHEN 'Rettifica esterna' THEN 25 WHEN 'Profilatura' THEN 26
            END,
            a.[N_COMPL_TORN], CAST(a.[D_TORN] AS DATE), t.[TEMPO_LAVORAZIONE],
            ROUND(CAST((COALESCE(a.[PEZZI_RIC],0) * COALESCE(s.[PESO_UNIT],0))
                / NULLIF(COALESCE(a.[N_IMPASTI],1), 0)
                + COALESCE(s.[SFRIDO],0) AS DECIMAL(18,6)), 2),
            a.[N_COMPL_PRESS], a.[N_CARICATI_COTT]
        FROM c4_attivi a
        INNER JOIN c4_torn t ON a.[ID] = t.[ID_COMMESSA]
        INNER JOIN t_schede s ON a.[NUM_SCHEDA] = s.[NUM_SCHEDA]
        LEFT JOIN c4_utenti u ON u.[id] = t.[USER_ID]
        WHERE a.[ORD_CAM] = @ord_cam AND a.[CHR_CAM] = @chr_cam
          AND t.[TIPO] IN ('Spianatura','Lapidello','resinatura foro',
                           'Facce / foro / incavi','Rettifica esterna','Profilatura')

        UNION ALL

        SELECT DISTINCT
            COALESCE(u.[firstName] + ' ' + u.[lastName], 'N/D'),
            a.[ORD_CAM], a.[CHR_CAM], a.[NUM_SCHEDA], a.[SPECIFICA],
            COALESCE(CAST(a.[DIAMETRO] AS VARCHAR(20)),'') + ' x ' +
            COALESCE(CAST(a.[SPESSORE] AS VARCHAR(20)),'') + ' x ' +
            COALESCE(CAST(a.[FORO] AS VARCHAR(20)),''),
            a.[PEZZI_RIC],
            CASE c.[TIPO]
                WHEN 'Pulizia / soffiaggio' THEN 31 WHEN 'Bilanciatura' THEN 32
                WHEN 'Marcatura' THEN 34 WHEN 'Imballaggio' THEN 35
            END,
            a.[N_COMPL_COLL], CAST(a.[D_COLL] AS DATE), c.[TEMPO_LAVORAZIONE],
            ROUND(CAST((COALESCE(a.[PEZZI_RIC],0) * COALESCE(s.[PESO_UNIT],0))
                / NULLIF(COALESCE(a.[N_IMPASTI],1), 0)
                + COALESCE(s.[SFRIDO],0) AS DECIMAL(18,6)), 2),
            a.[N_COMPL_PRESS], a.[N_CARICATI_COTT]
        FROM c4_attivi a
        INNER JOIN c4_coll c ON a.[ID] = c.[ID_COMMESSA]
        INNER JOIN t_schede s ON a.[NUM_SCHEDA] = s.[NUM_SCHEDA]
        LEFT JOIN c4_utenti u ON u.[id] = c.[USER_ID]
        WHERE a.[ORD_CAM] = @ord_cam AND a.[CHR_CAM] = @chr_cam
          AND c.[TIPO] IN ('Pulizia / soffiaggio','Bilanciatura','Marcatura','Imballaggio')
    )
"""


QUERIES = {

    "stamperia_refresh": """
        MERGE [Stamperia] AS tgt
        USING (
            SELECT
                a.[ID], a.[ORD_CAM], a.[CHR_CAM], a.[NUM_SCHEDA], a.[SPECIFICA],
                COALESCE(CAST(a.[DIAMETRO] AS VARCHAR(20)),'') + ' x ' +
                COALESCE(CAST(a.[SPESSORE] AS VARCHAR(20)),'') + ' x ' +
                COALESCE(CAST(a.[FORO] AS VARCHAR(20)),'') AS [Dimensioni],
                a.[PEZZI_RIC], a.[PEZZI_ST], a.[D_STAMP],
                a.[ORE_PESAT], a.[ORE_MISC], a.[ORE_PRESS],
                (SELECT TOP 1 u.[firstName] + ' ' + u.[lastName]
                 FROM c4_pesa p LEFT JOIN c4_utenti u ON u.[id] = p.[USER_ID]
                 WHERE p.[ID_COMMESSA] = a.[ID] ORDER BY p.[D_FINE] DESC) AS [Mat_op_pesa],
                (SELECT TOP 1 u.[firstName] + ' ' + u.[lastName]
                 FROM c4_misc m LEFT JOIN c4_utenti u ON u.[id] = m.[USER_ID]
                 WHERE m.[ID_COMMESSA] = a.[ID] ORDER BY m.[D_FINE] DESC) AS [Mat_op_misc],
                (SELECT TOP 1 u.[firstName] + ' ' + u.[lastName]
                 FROM c4_press p LEFT JOIN c4_utenti u ON u.[id] = p.[USER_ID]
                 WHERE p.[ID_COMMESSA] = a.[ID] ORDER BY p.[D_FINE] DESC) AS [Mat_op_press]
            FROM c4_attivi a
        ) AS src ON tgt.[Id] = src.[ID]
        WHEN MATCHED AND tgt.[Data_valid] IS NULL THEN UPDATE SET
            [Ord_cam]=src.[ORD_CAM],[Chr_cam]=src.[CHR_CAM],[Num_scheda]=src.[NUM_SCHEDA],
            [Specif]=src.[SPECIFICA],[Dimensioni]=src.[Dimensioni],[Pz_richi]=src.[PEZZI_RIC],
            [Pz_stamp]=src.[PEZZI_ST],[Data_stamp]=src.[D_STAMP],[Temp_pesa]=src.[ORE_PESAT],
            [Temp_misc]=src.[ORE_MISC],[Temp_press]=src.[ORE_PRESS],
            [Mat_op_pesa]=src.[Mat_op_pesa],[Mat_op_misc]=src.[Mat_op_misc],[Mat_op_press]=src.[Mat_op_press]
        WHEN NOT MATCHED THEN INSERT
            ([Id],[Ord_cam],[Chr_cam],[Num_scheda],[Specif],[Dimensioni],
             [Pz_richi],[Pz_stamp],[Data_stamp],[Temp_pesa],[Temp_misc],[Temp_press],
             [Mat_op_pesa],[Mat_op_misc],[Mat_op_press])
        VALUES (src.[ID],src.[ORD_CAM],src.[CHR_CAM],src.[NUM_SCHEDA],src.[SPECIFICA],src.[Dimensioni],
                src.[PEZZI_RIC],src.[PEZZI_ST],src.[D_STAMP],src.[ORE_PESAT],src.[ORE_MISC],src.[ORE_PRESS],
                src.[Mat_op_pesa],src.[Mat_op_misc],src.[Mat_op_press]);

        UPDATE [Stamperia] SET [Temp_tot] =
            COALESCE([Temp_pesa],0)+COALESCE([Temp_misc],0)+
            COALESCE([Temp_press],0)+COALESCE([Temp_assist_press],0)
        WHERE [Data_valid] IS NULL
    """,

    "stamperia_confirm": """
        UPDATE [Stamperia] SET [Data_valid] = CURRENT_TIMESTAMP
        WHERE [Flag] = 1 AND [Data_valid] IS NULL
    """,

    "forno_cottura_refresh": """
        MERGE [Forno_cottura] AS tgt
        USING (
            SELECT a.[ID], a.[ORD_CAM], a.[CHR_CAM], a.[NUM_SCHEDA], a.[SPECIFICA],
                COALESCE(CAST(a.[DIAMETRO] AS VARCHAR(20)),'') + ' x ' +
                COALESCE(CAST(a.[SPESSORE] AS VARCHAR(20)),'') + ' x ' +
                COALESCE(CAST(a.[FORO] AS VARCHAR(20)),'') AS [Dimensioni],
                a.[PEZZI_RIC], a.[N_CARICATI_COTT], a.[D_INIZIO_COTT]
            FROM c4_attivi a
        ) AS src ON tgt.[Id] = src.[ID]
        WHEN MATCHED AND tgt.[Data_valid] IS NULL THEN UPDATE SET
            [Ord_cam]=src.[ORD_CAM],[Chr_cam]=src.[CHR_CAM],[Num_scheda]=src.[NUM_SCHEDA],
            [Specif]=src.[SPECIFICA],[Dimensioni]=src.[Dimensioni],[Pz_richi]=src.[PEZZI_RIC],
            [Pz_inforna]=src.[N_CARICATI_COTT],[Data_inforna]=src.[D_INIZIO_COTT]
        WHEN NOT MATCHED THEN INSERT
            ([Id],[Ord_cam],[Chr_cam],[Num_scheda],[Specif],[Dimensioni],[Pz_richi],[Pz_inforna],[Data_inforna])
        VALUES (src.[ID],src.[ORD_CAM],src.[CHR_CAM],src.[NUM_SCHEDA],src.[SPECIFICA],src.[Dimensioni],
                src.[PEZZI_RIC],src.[N_CARICATI_COTT],src.[D_INIZIO_COTT])
    """,

    "forno_cottura_confirm": """
        UPDATE [Forno_cottura] SET [Data_valid] = CURRENT_TIMESTAMP
        WHERE [Flag] = 1 AND [Data_valid] IS NULL
    """,

    "tornitura_refresh": """
        MERGE [Tornitura] AS tgt
        USING (
            SELECT a.[ID], a.[ORD_CAM], a.[CHR_CAM], a.[NUM_SCHEDA], a.[SPECIFICA],
                COALESCE(CAST(a.[DIAMETRO] AS VARCHAR(20)),'') + ' x ' +
                COALESCE(CAST(a.[SPESSORE] AS VARCHAR(20)),'') + ' x ' +
                COALESCE(CAST(a.[FORO] AS VARCHAR(20)),'') AS [Dimensioni],
                a.[PEZZI_RIC], a.[N_COMPL_TORN], a.[D_TORN]
            FROM c4_attivi a
        ) AS src ON tgt.[Id] = src.[ID]
        WHEN MATCHED AND tgt.[Data_valid] IS NULL THEN UPDATE SET
            [Ord_cam]=src.[ORD_CAM],[Chr_cam]=src.[CHR_CAM],[Num_scheda]=src.[NUM_SCHEDA],
            [Specif]=src.[SPECIFICA],[Dimensioni]=src.[Dimensioni],[Pz_richi]=src.[PEZZI_RIC],
            [Pz_lav]=src.[N_COMPL_TORN],[Data_fine]=src.[D_TORN]
        WHEN NOT MATCHED THEN INSERT
            ([Id],[Ord_cam],[Chr_cam],[Num_scheda],[Specif],[Dimensioni],[Pz_richi],[Pz_lav],[Data_fine])
        VALUES (src.[ID],src.[ORD_CAM],src.[CHR_CAM],src.[NUM_SCHEDA],src.[SPECIFICA],src.[Dimensioni],
                src.[PEZZI_RIC],src.[N_COMPL_TORN],src.[D_TORN]);

        UPDATE t SET [Temp_spian]=x.tempo,[Mat_op_spian]=x.operatore FROM [Tornitura] t
        INNER JOIN (SELECT t.[ID_COMMESSA],t.[TEMPO_LAVORAZIONE] AS tempo,
            u.[firstName]+' '+u.[lastName] AS operatore FROM c4_torn t
            LEFT JOIN c4_utenti u ON u.[id]=t.[USER_ID] WHERE t.[TIPO]='Spianatura'
        ) x ON t.[Id]=x.[ID_COMMESSA] AND t.[Data_valid] IS NULL;

        UPDATE t SET [Temp_lapid]=x.tempo,[Mat_op_lapid]=x.operatore FROM [Tornitura] t
        INNER JOIN (SELECT t.[ID_COMMESSA],t.[TEMPO_LAVORAZIONE] AS tempo,
            u.[firstName]+' '+u.[lastName] AS operatore FROM c4_torn t
            LEFT JOIN c4_utenti u ON u.[id]=t.[USER_ID] WHERE t.[TIPO]='Lapidello'
        ) x ON t.[Id]=x.[ID_COMMESSA] AND t.[Data_valid] IS NULL;

        UPDATE t SET [Temp_ffi]=x.tempo,[Mat_op_ffi]=x.operatore FROM [Tornitura] t
        INNER JOIN (SELECT t.[ID_COMMESSA],t.[TEMPO_LAVORAZIONE] AS tempo,
            u.[firstName]+' '+u.[lastName] AS operatore FROM c4_torn t
            LEFT JOIN c4_utenti u ON u.[id]=t.[USER_ID] WHERE t.[TIPO]='Facce / foro / incavi'
        ) x ON t.[Id]=x.[ID_COMMESSA] AND t.[Data_valid] IS NULL;

        UPDATE t SET [Temp_rett]=x.tempo,[Mat_op_rett]=x.operatore FROM [Tornitura] t
        INNER JOIN (SELECT t.[ID_COMMESSA],t.[TEMPO_LAVORAZIONE] AS tempo,
            u.[firstName]+' '+u.[lastName] AS operatore FROM c4_torn t
            LEFT JOIN c4_utenti u ON u.[id]=t.[USER_ID] WHERE t.[TIPO]='Rettifica esterna'
        ) x ON t.[Id]=x.[ID_COMMESSA] AND t.[Data_valid] IS NULL;

        UPDATE t SET [Temp_prof]=x.tempo,[Mat_op_prof]=x.operatore FROM [Tornitura] t
        INNER JOIN (SELECT t.[ID_COMMESSA],t.[TEMPO_LAVORAZIONE] AS tempo,
            u.[firstName]+' '+u.[lastName] AS operatore FROM c4_torn t
            LEFT JOIN c4_utenti u ON u.[id]=t.[USER_ID] WHERE t.[TIPO]='Profilatura'
        ) x ON t.[Id]=x.[ID_COMMESSA] AND t.[Data_valid] IS NULL;

        UPDATE t SET [Temp_resin]=x.tempo,[Mat_op_resin]=x.operatore FROM [Tornitura] t
        INNER JOIN (SELECT t.[ID_COMMESSA],t.[TEMPO_LAVORAZIONE] AS tempo,
            u.[firstName]+' '+u.[lastName] AS operatore FROM c4_torn t
            LEFT JOIN c4_utenti u ON u.[id]=t.[USER_ID] WHERE t.[TIPO]='Piombatura / resinatura'
        ) x ON t.[Id]=x.[ID_COMMESSA] AND t.[Data_valid] IS NULL;

        UPDATE [Tornitura] SET [Temp_tot]=
            COALESCE([Temp_spian],0)+COALESCE([Temp_lapid],0)+COALESCE([Temp_ffi],0)+
            COALESCE([Temp_rett],0)+COALESCE([Temp_prof],0)+COALESCE([Temp_resin],0)
        WHERE [Data_valid] IS NULL
    """,

    "tornitura_confirm": """
        UPDATE [Tornitura] SET [Data_valid] = CURRENT_TIMESTAMP
        WHERE [Flag] = 1 AND [Data_valid] IS NULL
    """,

    "collaudo_refresh": """
        MERGE [Collaudo] AS tgt
        USING (
            SELECT a.[ID], a.[ORD_CAM], a.[CHR_CAM], a.[NUM_SCHEDA], a.[SPECIFICA],
                COALESCE(CAST(a.[DIAMETRO] AS VARCHAR(20)),'') + ' x ' +
                COALESCE(CAST(a.[SPESSORE] AS VARCHAR(20)),'') + ' x ' +
                COALESCE(CAST(a.[FORO] AS VARCHAR(20)),'') AS [Dimensioni],
                a.[PEZZI_RIC], a.[N_COMPL_COLL], a.[D_COLL]
            FROM c4_attivi a
        ) AS src ON tgt.[Id] = src.[ID]
        WHEN MATCHED AND tgt.[Data_valid] IS NULL THEN UPDATE SET
            [Ord_cam]=src.[ORD_CAM],[Chr_cam]=src.[CHR_CAM],[Num_scheda]=src.[NUM_SCHEDA],
            [Specif]=src.[SPECIFICA],[Dimensioni]=src.[Dimensioni],[Pz_richi]=src.[PEZZI_RIC],
            [Pz_lav]=src.[N_COMPL_COLL],[Data_fine]=src.[D_COLL]
        WHEN NOT MATCHED THEN INSERT
            ([Id],[Ord_cam],[Chr_cam],[Num_scheda],[Specif],[Dimensioni],[Pz_richi],[Pz_lav],[Data_fine])
        VALUES (src.[ID],src.[ORD_CAM],src.[CHR_CAM],src.[NUM_SCHEDA],src.[SPECIFICA],src.[Dimensioni],
                src.[PEZZI_RIC],src.[N_COMPL_COLL],src.[D_COLL]);

        UPDATE c SET [Temp_sabb]=x.tempo,[Mat_op_sabb]=x.operatore FROM [Collaudo] c
        INNER JOIN (SELECT cc.[ID_COMMESSA],cc.[TEMPO_LAVORAZIONE] AS tempo,
            u.[firstName]+' '+u.[lastName] AS operatore FROM c4_coll cc
            LEFT JOIN c4_utenti u ON u.[id]=cc.[USER_ID] WHERE cc.[TIPO]='Sabbiatura'
        ) x ON c.[Id]=x.[ID_COMMESSA] AND c.[Data_valid] IS NULL;

        UPDATE c SET [Temp_pul_sof]=x.tempo,[Mat_op_pul_sof]=x.operatore FROM [Collaudo] c
        INNER JOIN (SELECT cc.[ID_COMMESSA],cc.[TEMPO_LAVORAZIONE] AS tempo,
            u.[firstName]+' '+u.[lastName] AS operatore FROM c4_coll cc
            LEFT JOIN c4_utenti u ON u.[id]=cc.[USER_ID] WHERE cc.[TIPO]='Pulizia / soffiaggio'
        ) x ON c.[Id]=x.[ID_COMMESSA] AND c.[Data_valid] IS NULL;

        UPDATE c SET [Temp_bilanc]=x.tempo,[Mat_op_bilanc]=x.operatore FROM [Collaudo] c
        INNER JOIN (SELECT cc.[ID_COMMESSA],cc.[TEMPO_LAVORAZIONE] AS tempo,
            u.[firstName]+' '+u.[lastName] AS operatore FROM c4_coll cc
            LEFT JOIN c4_utenti u ON u.[id]=cc.[USER_ID] WHERE cc.[TIPO]='Bilanciatura'
        ) x ON c.[Id]=x.[ID_COMMESSA] AND c.[Data_valid] IS NULL;

        UPDATE c SET [Temp_velo]=x.tempo,[Mat_op_velo]=x.operatore FROM [Collaudo] c
        INNER JOIN (SELECT cc.[ID_COMMESSA],cc.[TEMPO_LAVORAZIONE] AS tempo,
            u.[firstName]+' '+u.[lastName] AS operatore FROM c4_coll cc
            LEFT JOIN c4_utenti u ON u.[id]=cc.[USER_ID] WHERE cc.[TIPO]='Prova velocità'
        ) x ON c.[Id]=x.[ID_COMMESSA] AND c.[Data_valid] IS NULL;

        UPDATE c SET [Temp_marca]=x.tempo,[Mat_op_marca]=x.operatore FROM [Collaudo] c
        INNER JOIN (SELECT cc.[ID_COMMESSA],cc.[TEMPO_LAVORAZIONE] AS tempo,
            u.[firstName]+' '+u.[lastName] AS operatore FROM c4_coll cc
            LEFT JOIN c4_utenti u ON u.[id]=cc.[USER_ID] WHERE cc.[TIPO]='Marcatura'
        ) x ON c.[Id]=x.[ID_COMMESSA] AND c.[Data_valid] IS NULL;

        UPDATE c SET [Temp_flang]=x.tempo,[Mat_op_flang]=x.operatore FROM [Collaudo] c
        INNER JOIN (SELECT cc.[ID_COMMESSA],cc.[TEMPO_LAVORAZIONE] AS tempo,
            u.[firstName]+' '+u.[lastName] AS operatore FROM c4_coll cc
            LEFT JOIN c4_utenti u ON u.[id]=cc.[USER_ID] WHERE cc.[TIPO]='Flangiatura'
        ) x ON c.[Id]=x.[ID_COMMESSA] AND c.[Data_valid] IS NULL;

        UPDATE c SET [Temp_imball]=x.tempo,[Mat_op_imball]=x.operatore FROM [Collaudo] c
        INNER JOIN (SELECT cc.[ID_COMMESSA],cc.[TEMPO_LAVORAZIONE] AS tempo,
            u.[firstName]+' '+u.[lastName] AS operatore FROM c4_coll cc
            LEFT JOIN c4_utenti u ON u.[id]=cc.[USER_ID] WHERE cc.[TIPO]='Imballaggio'
        ) x ON c.[Id]=x.[ID_COMMESSA] AND c.[Data_valid] IS NULL;

        UPDATE c SET [Temp_chius]=x.tempo,[Mat_op_chius]=x.operatore FROM [Collaudo] c
        INNER JOIN (SELECT cc.[ID_COMMESSA],cc.[TEMPO_LAVORAZIONE] AS tempo,
            u.[firstName]+' '+u.[lastName] AS operatore FROM c4_coll cc
            LEFT JOIN c4_utenti u ON u.[id]=cc.[USER_ID] WHERE cc.[TIPO]='Chiusura bancale'
        ) x ON c.[Id]=x.[ID_COMMESSA] AND c.[Data_valid] IS NULL;

        UPDATE [Collaudo] SET [Temp_tot]=
            COALESCE([Temp_sabb],0)+COALESCE([Temp_pul_sof],0)+COALESCE([Temp_bilanc],0)+
            COALESCE([Temp_velo],0)+COALESCE([Temp_marca],0)+COALESCE([Temp_flang],0)+
            COALESCE([Temp_imball],0)+COALESCE([Temp_chius],0)
        WHERE [Data_valid] IS NULL
    """,

    "collaudo_confirm": """
        UPDATE [Collaudo] SET [Data_valid] = CURRENT_TIMESTAMP
        WHERE [Flag] = 1 AND [Data_valid] IS NULL
    """,

    "report_quadratura": _BASE_LAVORAZIONI + """
        SELECT [Operatore],[Ord. Camfart],[Chr. Camfart],[N° Scheda],[Specifica],
               [Dimensioni],[Pz. Richiesti],[Fase],[N° Pz. Lavorati],[Data],
               [Tempo_h],[Peso_Tot_kg],[N° Pz. Stampati],[N° Pz. Infornati]
        FROM lav ORDER BY [Operatore],[Ord. Camfart],[Fase],[Data]
    """,

    "report_pezzi_discordanti": _BASE_LAVORAZIONI + """
        SELECT [Ord. Camfart],[Chr. Camfart],[N° Scheda],[Specifica],[Dimensioni],
               [Pz. Richiesti],[Operatore],[Fase],[N° Pz. Lavorati],[Data]
        FROM lav WHERE [N° Pz. Lavorati] <> [Pz. Richiesti]
        ORDER BY [Ord. Camfart],[Chr. Camfart],[Operatore],[Fase],[Data]
    """,

    "report_infornature_parziali": _BASE_LAVORAZIONI + """
        SELECT [Ord. Camfart],[Chr. Camfart],[N° Scheda],[Specifica],[Dimensioni],
               [Pz. Richiesti],[Operatore],[Fase],[N° Pz. Stampati],[N° Pz. Infornati],[Data]
        FROM lav WHERE [Fase]=11
          AND COALESCE([N° Pz. Infornati],0) <> COALESCE([N° Pz. Stampati],0)
        ORDER BY [Ord. Camfart],[Chr. Camfart],[Operatore],[Data]
    """,

    "report_riepilogo_commesse": _BASE_LAVORAZIONI + """
        SELECT [Ord. Camfart],[Chr. Camfart],[N° Scheda],[Specifica],[Dimensioni],
               [Pz. Richiesti],[Operatore],[Fase],[N° Pz. Lavorati],[Data],[Tempo_h],[Peso_Tot_kg]
        FROM lav ORDER BY [Ord. Camfart],[Chr. Camfart],[Operatore],[Fase],[Data]
    """,

    "report_singola_commessa": _BASE_SINGOLA + """
        SELECT [Ord. Camfart],[Chr. Camfart],[N° Scheda],[Specifica],[Dimensioni],
               [Pz. Richiesti],[Operatore],[Fase],[N° Pz. Lavorati],[Data],[Tempo_h],[Peso_Tot_kg]
        FROM lav ORDER BY [Fase],[Data]
    """,

    "report_imballate_non_evase": """
        SELECT a.[ORD_CAM] AS [Ord. Camfart],a.[CHR_CAM] AS [Chr. Camfart],
            a.[NUM_SCHEDA] AS [N° Scheda],a.[SPECIFICA] AS [Specifica],
            COALESCE(CAST(a.[DIAMETRO] AS VARCHAR(20)),'') + ' x ' +
            COALESCE(CAST(a.[SPESSORE] AS VARCHAR(20)),'') + ' x ' +
            COALESCE(CAST(a.[FORO] AS VARCHAR(20)),'') AS [Dimensioni],
            a.[PEZZI_RIC] AS [Pz. Richiesti],a.[N_COMPL_COLL] AS [N° Mole Imballate],
            CAST(MAX(c.[D_FINE]) AS DATE) AS [Data Imballo]
        FROM c4_attivi a
        INNER JOIN c4_coll c ON c.[ID_COMMESSA]=a.[ID] AND c.[TIPO]='Imballaggio'
        WHERE COALESCE(a.[N_COMPL_COLL],0) > 0
        GROUP BY a.[ORD_CAM],a.[CHR_CAM],a.[NUM_SCHEDA],a.[SPECIFICA],
                 a.[DIAMETRO],a.[SPESSORE],a.[FORO],a.[PEZZI_RIC],a.[N_COMPL_COLL]
        ORDER BY [Data Imballo] DESC
    """,

    "report_non_pesati": """
        WITH pesati AS (
            SELECT [ID_COMMESSA],COUNT(*) AS n_pesati FROM c4_pesa
            WHERE [N_IMPASTO] IS NOT NULL GROUP BY [ID_COMMESSA]
        )
        SELECT a.[ORD_CAM] AS [Ord. Camfart],a.[CHR_CAM] AS [Chr. Camfart],
            a.[NUM_SCHEDA] AS [N° Scheda],a.[SPECIFICA] AS [Specifica],
            COALESCE(CAST(a.[DIAMETRO] AS VARCHAR(20)),'') + ' x ' +
            COALESCE(CAST(a.[SPESSORE] AS VARCHAR(20)),'') + ' x ' +
            COALESCE(CAST(a.[FORO] AS VARCHAR(20)),'') AS [Dimensioni],
            a.[PEZZI_RIC] AS [Pz. Richiesti],
            COALESCE(a.[N_IMPASTI],0) AS [N° Impasti Richiesti],
            COALESCE(p.n_pesati,0) AS [N° Impasti Pesati],
            COALESCE(a.[N_IMPASTI],0)-COALESCE(p.n_pesati,0) AS [N° Impasti da Pesare]
        FROM c4_attivi a LEFT JOIN pesati p ON p.[ID_COMMESSA]=a.[ID]
        WHERE a.[D_ORDINE] BETWEEN @date_from AND @date_to
          AND a.[N_IMPASTI] IS NOT NULL
          AND COALESCE(a.[N_IMPASTI],0)-COALESCE(p.n_pesati,0) > 0
        ORDER BY a.[ORD_CAM],a.[CHR_CAM]
    """,

    "report_non_miscelati": """
        WITH miscelati AS (
            SELECT [ID_COMMESSA],COUNT(*) AS n_miscelati FROM c4_misc
            WHERE [N_IMPASTO] IS NOT NULL GROUP BY [ID_COMMESSA]
        )
        SELECT a.[ORD_CAM] AS [Ord. Camfart],a.[CHR_CAM] AS [Chr. Camfart],
            a.[NUM_SCHEDA] AS [N° Scheda],a.[SPECIFICA] AS [Specifica],
            COALESCE(CAST(a.[DIAMETRO] AS VARCHAR(20)),'') + ' x ' +
            COALESCE(CAST(a.[SPESSORE] AS VARCHAR(20)),'') + ' x ' +
            COALESCE(CAST(a.[FORO] AS VARCHAR(20)),'') AS [Dimensioni],
            a.[PEZZI_RIC] AS [Pz. Richiesti],
            COALESCE(a.[N_IMPASTI],0) AS [N° Impasti Richiesti],
            COALESCE(m.n_miscelati,0) AS [N° Impasti Miscelati],
            COALESCE(a.[N_IMPASTI],0)-COALESCE(m.n_miscelati,0) AS [N° Impasti da Miscelare]
        FROM c4_attivi a LEFT JOIN miscelati m ON m.[ID_COMMESSA]=a.[ID]
        WHERE a.[D_ORDINE] BETWEEN @date_from AND @date_to
          AND a.[N_IMPASTI] IS NOT NULL
          AND COALESCE(a.[N_IMPASTI],0)-COALESCE(m.n_miscelati,0) > 0
        ORDER BY a.[ORD_CAM],a.[CHR_CAM]
    """,

    "report_date_tornitura": """
        SELECT a.[ORD_CAM] AS [Ord. Camfart],a.[CHR_CAM] AS [Chr. Camfart],
            a.[NUM_SCHEDA] AS [N° Scheda],a.[SPECIFICA] AS [Specifica],
            COALESCE(CAST(a.[DIAMETRO] AS VARCHAR(20)),'') + ' x ' +
            COALESCE(CAST(a.[SPESSORE] AS VARCHAR(20)),'') + ' x ' +
            COALESCE(CAST(a.[FORO] AS VARCHAR(20)),'') AS [Dimensioni],
            a.[PEZZI_RIC] AS [Pz. Richiesti],
            COALESCE(a.[N_COMPL_TORN],0) AS [N° Pz. Finiti Tornitura],
            COALESCE(a.[N_SCARTI_TORN],0) AS [N° Pz. Scartati],
            CAST(MAX(t.[D_FINE]) AS DATE) AS [Data Fine Tornitura]
        FROM c4_attivi a LEFT JOIN c4_torn t ON t.[ID_COMMESSA]=a.[ID]
        GROUP BY a.[ORD_CAM],a.[CHR_CAM],a.[NUM_SCHEDA],a.[SPECIFICA],
                 a.[DIAMETRO],a.[SPESSORE],a.[FORO],a.[PEZZI_RIC],a.[N_COMPL_TORN],a.[N_SCARTI_TORN]
        HAVING (COALESCE(a.[N_COMPL_TORN],0)+COALESCE(a.[N_SCARTI_TORN],0)) >= COALESCE(a.[PEZZI_RIC],0)
           AND MAX(t.[D_FINE]) IS NOT NULL
        ORDER BY MAX(t.[D_FINE]) DESC
    """,

    "report_marcate_non_imballate": """
        SELECT a.[ORD_CAM] AS [Ord. Camfart],a.[CHR_CAM] AS [Chr. Camfart],
            a.[NUM_SCHEDA] AS [N° Scheda],a.[SPECIFICA] AS [Specifica],
            COALESCE(CAST(a.[DIAMETRO] AS VARCHAR(20)),'') + ' x ' +
            COALESCE(CAST(a.[SPESSORE] AS VARCHAR(20)),'') + ' x ' +
            COALESCE(CAST(a.[FORO] AS VARCHAR(20)),'') AS [Dimensioni],
            a.[PEZZI_RIC] AS [Pz. Richiesti],
            COALESCE(a.[N_COMPL_TORN],0) AS [N° Pz. Marcati],
            COALESCE(a.[N_SCARTI_TORN],0) AS [N° Pz. Imballati],
            CAST(MAX(c.[D_FINE]) AS DATE) AS [Data Imballo]
        FROM c4_attivi a
        LEFT JOIN c4_coll c ON c.[ID_COMMESSA]=a.[ID] AND c.[TIPO]='Imballaggio'
        WHERE COALESCE(a.[N_COMPL_TORN],0) > 0
        GROUP BY a.[ORD_CAM],a.[CHR_CAM],a.[NUM_SCHEDA],a.[SPECIFICA],
                 a.[DIAMETRO],a.[SPESSORE],a.[FORO],a.[PEZZI_RIC],a.[N_COMPL_TORN],a.[N_SCARTI_TORN]
        ORDER BY a.[ORD_CAM],a.[CHR_CAM]
    """,
}