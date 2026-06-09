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
