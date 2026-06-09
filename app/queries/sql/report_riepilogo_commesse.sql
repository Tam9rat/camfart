-- base: _base_lavorazioni
SELECT [Ord. Camfart],[Chr. Camfart],[N° Scheda],[Specifica],[Dimensioni],
       [Pz. Richiesti],[Operatore],[Fase],[N° Pz. Lavorati],[Data],[Tempo_h],[Peso_Tot_kg]
FROM lav ORDER BY [Ord. Camfart],[Chr. Camfart],[Operatore],[Fase],[Data]
