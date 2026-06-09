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
