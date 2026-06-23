-- base: _base_lavorazioni
SELECT [Operatore],[Ord. Camfart],[Chr. Camfart],[N° Scheda],[Specifica],
       [Dimensioni],[Pz. Richiesti],[Fase],[N° Pz. Lavorati],[Data],
       [Tempo_min],[Peso_Tot_kg],[N° Pz. Stampati],[N° Pz. Infornati]
FROM lav ORDER BY [Operatore],[Ord. Camfart],[Fase],[Data]
