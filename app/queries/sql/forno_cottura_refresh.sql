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
