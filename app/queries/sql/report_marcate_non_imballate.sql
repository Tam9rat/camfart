SELECT a.[ORD_CAM] AS [Ord. Camfart],a.[CHR_CAM] AS [Chr. Camfart],
    a.[NUM_SCHEDA] AS [N° Scheda],a.[SPECIFICA] AS [Specifica],
    COALESCE(CAST(a.[DIAMETRO] AS VARCHAR(20)),'') + ' x ' +
    COALESCE(CAST(a.[SPESSORE] AS VARCHAR(20)),'') + ' x ' +
    COALESCE(CAST(a.[FORO] AS VARCHAR(20)),'') AS [Dimensioni],
    a.[PEZZI_RIC] AS [Pz. Richiesti],
    a.[N_COMPL_COLL] AS [N° Pz. Marcati],
    CAST(MAX(cm.[D_FINE]) AS DATE) AS [Data Marcatura]
FROM c4_attivi a
INNER JOIN c4_coll cm ON cm.[ID_COMMESSA]=a.[ID] AND cm.[TIPO]='Marcatura'
LEFT JOIN c4_coll ci ON ci.[ID_COMMESSA]=a.[ID] AND ci.[TIPO]='Imballaggio'
WHERE ci.[ID] IS NULL
GROUP BY a.[ORD_CAM],a.[CHR_CAM],a.[NUM_SCHEDA],a.[SPECIFICA],
         a.[DIAMETRO],a.[SPESSORE],a.[FORO],a.[PEZZI_RIC],a.[N_COMPL_COLL]
ORDER BY a.[ORD_CAM],a.[CHR_CAM]
