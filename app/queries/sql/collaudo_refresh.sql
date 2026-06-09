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
