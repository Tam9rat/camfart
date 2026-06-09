-- base: _base_lavorazioni
SELECT [Ord. Camfart],[Chr. Camfart],[N° Scheda],[Specifica],[Dimensioni],
       [Pz. Richiesti],[Operatore],[Fase],[N° Pz. Stampati],[N° Pz. Infornati],[Data]
FROM lav WHERE [Fase]=11
  AND COALESCE([N° Pz. Infornati],0) <> COALESCE([N° Pz. Stampati],0)
ORDER BY [Ord. Camfart],[Chr. Camfart],[Operatore],[Data]
