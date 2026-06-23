-- base: _base_singola
SELECT [Ord. Camfart],[Chr. Camfart],[N° Scheda],[Specifica],[Dimensioni],
       [Pz. Richiesti],[Operatore],[Fase],[N° Pz. Lavorati],[Data],[Tempo_min],[Peso_Tot_kg]
FROM lav ORDER BY [Fase],[Data]
