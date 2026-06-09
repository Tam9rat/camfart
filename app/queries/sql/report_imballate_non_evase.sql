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
