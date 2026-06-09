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
