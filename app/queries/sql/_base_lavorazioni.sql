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
        ROUND(CAST(DATEDIFF(SECOND, p.[D_INIZIO], p.[D_FINE]) / 3600.0 AS DECIMAL(18,2)), 2) AS [Tempo_h],
        ROUND(CAST((COALESCE(a.[PEZZI_RIC],0) * COALESCE(s.[PESO_UNIT],0))
            / NULLIF(COALESCE(a.[N_IMPASTI],1), 0)
            + COALESCE(s.[SFRIDO],0) AS DECIMAL(18,6)), 2) AS [Peso_Tot_kg],
        a.[N_COMPL_PRESS] AS [N° Pz. Stampati], a.[N_CARICATI_COTT] AS [N° Pz. Infornati]
    FROM c4_attivi a
    INNER JOIN t_schede s ON s.[NUM_SCHEDA] = a.[NUM_SCHEDA]
    INNER JOIN c4_pesa p ON p.[ID_COMMESSA] = a.[ID]
    LEFT JOIN c4_utenti u ON u.[id] = p.[USER_ID]
    WHERE a.[D_PESAT] BETWEEN @date_from AND @date_to AND a.[N_PESAT] IS NOT NULL

    UNION ALL

    SELECT
        COALESCE(u.[firstName] + ' ' + u.[lastName], 'N/D'),
        a.[ORD_CAM], a.[CHR_CAM], a.[NUM_SCHEDA], a.[SPECIFICA],
        COALESCE(CAST(a.[DIAMETRO] AS VARCHAR(20)),'') + ' x ' +
        COALESCE(CAST(a.[SPESSORE] AS VARCHAR(20)),'') + ' x ' +
        COALESCE(CAST(a.[FORO] AS VARCHAR(20)),''),
        a.[PEZZI_RIC], 2, a.[N_MISC], CAST(a.[D_MISC] AS DATE),
        ROUND(CAST(DATEDIFF(SECOND, cm.[D_INIZIO], cm.[D_FINE]) / 3600.0 AS DECIMAL(18,2)), 2),
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

    SELECT
        COALESCE(u.[firstName] + ' ' + u.[lastName], 'N/D'),
        a.[ORD_CAM], a.[CHR_CAM], a.[NUM_SCHEDA], a.[SPECIFICA],
        COALESCE(CAST(a.[DIAMETRO] AS VARCHAR(20)),'') + ' x ' +
        COALESCE(CAST(a.[SPESSORE] AS VARCHAR(20)),'') + ' x ' +
        COALESCE(CAST(a.[FORO] AS VARCHAR(20)),''),
        a.[PEZZI_RIC], 3, a.[N_COMPL_PRESS], CAST(a.[D_PRESS] AS DATE),
        ROUND(CAST(p.[TEMPO_PRESS] / 3600.0 AS DECIMAL(18,2)), 2),
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

    SELECT
        COALESCE(u.[firstName] + ' ' + u.[lastName], 'N/D'),
        a.[ORD_CAM], a.[CHR_CAM], a.[NUM_SCHEDA], a.[SPECIFICA],
        COALESCE(CAST(a.[DIAMETRO] AS VARCHAR(20)),'') + ' x ' +
        COALESCE(CAST(a.[SPESSORE] AS VARCHAR(20)),'') + ' x ' +
        COALESCE(CAST(a.[FORO] AS VARCHAR(20)),''),
        a.[PEZZI_RIC], 11, a.[N_CARICATI_COTT], CAST(a.[D_COTT] AS DATE),
        ROUND(CAST(a.[ORE_COTT] / 60.0 AS DECIMAL(18,2)), 2),
        ROUND(CAST((COALESCE(a.[PEZZI_RIC],0) * COALESCE(s.[PESO_UNIT],0))
            / NULLIF(COALESCE(a.[N_IMPASTI],1), 0)
            + COALESCE(s.[SFRIDO],0) AS DECIMAL(18,6)), 2),
        a.[N_COMPL_PRESS], a.[N_CARICATI_COTT]
    FROM c4_attivi a
    INNER JOIN t_schede s ON a.[NUM_SCHEDA] = s.[NUM_SCHEDA]
    INNER JOIN c4_cott ct ON a.[ID] = ct.[ID_COMMESSA]
    LEFT JOIN c4_utenti u ON u.[id] = ct.[USER_ID]
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
        a.[N_COMPL_TORN], CAST(a.[D_TORN] AS DATE),
        ROUND(CAST(t.[TEMPO_LAVORAZIONE] / 60.0 AS DECIMAL(18,2)), 2),
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
        a.[N_COMPL_COLL], CAST(a.[D_COLL] AS DATE),
        ROUND(CAST(c.[TEMPO_LAVORAZIONE] / 60.0 AS DECIMAL(18,2)), 2),
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
