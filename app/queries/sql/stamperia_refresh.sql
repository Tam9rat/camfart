MERGE [Stamperia] AS tgt
USING (
    SELECT
        a.[ID], a.[ORD_CAM], a.[CHR_CAM], a.[NUM_SCHEDA], a.[SPECIFICA],
        COALESCE(CAST(a.[DIAMETRO] AS VARCHAR(20)),'') + ' x ' +
        COALESCE(CAST(a.[SPESSORE] AS VARCHAR(20)),'') + ' x ' +
        COALESCE(CAST(a.[FORO] AS VARCHAR(20)),'') AS [Dimensioni],
        a.[PEZZI_RIC], a.[PEZZI_ST], a.[D_PRESS] AS [D_STAMP],
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
WHERE [Data_valid] IS NULL;

UPDATE s SET s.[Data_stamp] = a.[D_PRESS]
FROM [Stamperia] s
INNER JOIN c4_attivi a ON a.[ID] = s.[Id]
WHERE a.[D_PRESS] IS NOT NULL AND s.[Data_stamp] IS NULL
