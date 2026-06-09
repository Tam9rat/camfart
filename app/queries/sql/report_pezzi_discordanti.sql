-- base: _base_lavorazioni
SELECT [Ord. Camfart],[Chr. Camfart],[N° Scheda],[Specifica],[Dimensioni],
       [Pz. Richiesti],[Operatore],[Fase],[N° Pz. Lavorati],[Data]
FROM lav WHERE [N° Pz. Lavorati] <> [Pz. Richiesti]
ORDER BY [Ord. Camfart],[Chr. Camfart],[Operatore],[Fase],[Data]
