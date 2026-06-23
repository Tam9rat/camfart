# Report Integrità Dati — Quadratura Operatore & Report Correlati

**Data:** 2026-06-23
**Periodo analizzato:** 2026-05-15 — 2026-06-23

---

## Problemi riscontrati e correzioni applicate

### 1. Tempo_h duplicato (Fase 1 Pesatura, Fase 2 Miscelazione)

**Problema:** La query effettuava un JOIN tra `c4_attivi` e `c4_pesa`/`c4_misc` per ottenere il nome dell'operatore. Il campo `ORE_PESAT` (tempo totale) veniva ripetuto per ogni riga del JOIN, moltiplicando il valore.

**Esempio:** ORD_CAM 134531 — 11 pesate in `c4_pesa`, ciascuna mostrava `ORE_PESAT = 4365.71` → totale gonfiato a 48,022.81 minuti.

**Correzione:** Sostituito `ORE_PESAT`/`ORE_MISC` con il calcolo diretto per ogni singola operazione:
```sql
DATEDIFF(SECOND, p.[D_INIZIO], p.[D_FINE]) / 60.0
```
Ogni riga del report ora mostra il tempo della singola operazione, non il totale ripetuto.

**File modificato:** `_base_lavorazioni.sql`, `_base_singola.sql`

---

### 2. Tempo_h sempre 0.00 per Fase 3 (Pressatura)

**Problema:** La query usava `ORE_PRESS` da `c4_attivi`, che era sempre 0 o quasi 0. Il tempo reale era registrato in `c4_press.TEMPO_PRESS` (in secondi).

**Correzione:** Sostituito con:
```sql
p.[TEMPO_PRESS] / 60.0
```
Converte i secondi in minuti.

**File modificato:** `_base_lavorazioni.sql`, `_base_singola.sql`

---

### 3. Operatore mancante (N/D) per Fase 11 (Cottura)

**Problema:** La query per la cottura aveva l'operatore hardcoded come `'N/D'`. Non effettuava nessun JOIN per recuperare chi aveva eseguito l'operazione.

**Correzione:** Aggiunto JOIN a `c4_cott` → `c4_utenti` per recuperare il nome dell'operatore, come già avveniva per le altre fasi.

**File modificato:** `_base_lavorazioni.sql`, `_base_singola.sql`

---

### 4. Colonna rinominata: Tempo_h → Tempo_min

**Problema:** I valori erano in minuti ma la colonna si chiamava `Tempo_h` (ore), creando confusione. Convertire in ore rendeva i valori piccoli (es. pressatura) prossimi a 0.

**Correzione:** Rinominata la colonna in `Tempo_min` in tutti i report che la utilizzano.

**File modificati:** `_base_lavorazioni.sql`, `_base_singola.sql`, `report_quadratura.sql`, `report_riepilogo_commesse.sql`, `report_singola_commessa.sql`

---

### 5. Data_stamp NULL in Stamperia

**Problema:** Il campo `Data_stamp` nella tabella Stamperia era NULL per molte righe. La query MERGE usava `D_STAMP` da `c4_attivi`, che è sempre NULL. Il dato corretto è `D_PRESS`.

Inoltre, la condizione MERGE `WHEN MATCHED AND tgt.[Data_valid] IS NULL` saltava le righe già validate, impedendo l'aggiornamento di `Data_stamp` anche per quelle.

**Correzione:**
1. Cambiato sorgente da `a.[D_STAMP]` a `a.[D_PRESS]` nel MERGE
2. Aggiunto UPDATE separato per sincronizzare le righe già validate:
```sql
UPDATE s SET s.[Data_stamp] = a.[D_PRESS]
FROM [Stamperia] s
INNER JOIN c4_attivi a ON a.[ID] = s.[Id]
WHERE a.[D_PRESS] IS NOT NULL AND s.[Data_stamp] IS NULL
```
2,334 righe aggiornate manualmente via SSMS.

**File modificato:** `stamperia_refresh.sql`

---

## Problemi noti — dati sorgente (Camfart4)

Questi problemi originano dall'applicazione Camfart4 e non possono essere corretti lato report.

### A. Tempi anomali molto alti

Alcune operazioni in `c4_pesa` hanno `D_INIZIO` lasciato aperto per giorni prima della chiusura (`D_FINE`). L'operatore non ha chiuso la sessione di pesatura.

**Esempio concreto — ORD_CAM 134304:**

| ID | Impasto | D_INIZIO | D_FINE | Minuti | Operatore |
|----|---------|----------|--------|--------|-----------|
| 11089 | 1 | 2026-05-26 04:57 | 2026-05-26 05:10 | 13.33 | Paolo Gheza |
| 11090 | 1 | 2026-05-26 05:10 | 2026-06-05 13:22 | **14,891** (10 giorni) | Paolo Gheza |
| 11285 | 1 | 2026-06-05 13:03 | NULL | NULL | NULL |

La riga ID 11090 è rimasta aperta dal 26 maggio al 5 giugno (10 giorni).

**Impatto:** Nel periodo 2026-05-15 / 2026-06-23 ci sono valori fino a 83,249 minuti (58 giorni) per singole operazioni di pesatura.

### B. Operatori N/D (USER_ID NULL)

Alcune righe nelle tabelle di dettaglio non hanno `USER_ID` registrato.

| Tabella | Righe totali | USER_ID NULL | Percentuale |
|---------|-------------|-------------|-------------|
| c4_pesa | 581 | 66 | 11% |
| c4_misc | 0 | - | - |
| c4_press | 2,050 | 0 | 0% |
| c4_cott | 113 | 0 | 0% |
| c4_torn | 142 | 3 | 2% |
| c4_coll | 162 | 0 | 0% |

Il problema è concentrato su `c4_pesa` (pesatura) con 66 righe senza operatore. Probabile causa: sessione non completata o app Camfart4 che non ha registrato l'utente.

### C. Righe incomplete (D_FINE NULL)

Esempio: ORD_CAM 134304, riga ID 11285 — `D_INIZIO` registrato ma `D_FINE` e `USER_ID` entrambi NULL. Operazione mai completata. Il report mostra `Tempo_min = NULL` e `Operatore = N/D`.

---

## Mappa sorgenti Tempo_min per fase

| Fase | Nome | Sorgente tempo | Unità originale | Conversione |
|------|------|---------------|----------------|-------------|
| 1 | Pesatura | `c4_pesa.D_INIZIO → D_FINE` | secondi | / 60 → minuti |
| 2 | Miscelazione | `c4_misc.D_INIZIO → D_FINE` | secondi | / 60 → minuti |
| 3 | Pressatura | `c4_press.TEMPO_PRESS` | secondi | / 60 → minuti |
| 11 | Cottura | `c4_attivi.ORE_COTT` | minuti | nessuna |
| 21-26 | Tornitura | `c4_torn.TEMPO_LAVORAZIONE` | minuti | nessuna |
| 31-35 | Collaudo | `c4_coll.TEMPO_LAVORAZIONE` | minuti | nessuna |
