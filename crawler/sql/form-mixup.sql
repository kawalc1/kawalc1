SELECT DISTINCT terbalik.kelurahan, terbalik.tps, terbalik."bot-pas1", terbalik."bot-pas2", terbalik."bot-jumlah",
                terbalik."bot-tidak-sah", terbalik.photo as "hal2photo",
                balikter."bot-php", balikter.photo as "hal2photo"
FROM (
         SELECT p.kelurahan, p.tps,
--t.photo,
                p.pas1  AS "bot-pas1", t.pas1,
                p.pas2  AS "bot-pas2", t.pas2,
                p.jumlah  AS "bot-jumlah", t.pas1 + t.pas2 AS "jumlah",
                -1 as "jumlah-sah",
                p.tidak_sah AS "bot-tidak-sah", "tSah" as "tidak-sah",
                t.pas1 = p.pas1 AND t.pas2 = p.pas2 as "pasmatch",
                "tSah" = p.tidak_sah AS "tidak-sah-match",
                p.hash,
                p.aligned,
                p.roi,
                p.confidence,
                p.confidence_tidak_sah,
                p.photo,
                p.config,
                p.php_jumlah AS "bot-php",
                t.jum AS "php",
                p.php_jumlah = t.jum as "php-match",
                t.error AS error,
                similarity,
                t.halaman
         FROM detections AS p
                  INNER JOIN tps AS t ON p.photo = t.photo
         WHERE p.config = 'digit_config_ppwp_scan_halaman_2_2019.json'
           AND t.halaman = '1'
           AND similarity > 50
           and confidence < 1.0
         ORDER BY similarity DESC
     ) AS terbalik inner join (
    SELECT p.kelurahan, p.tps,
--t.photo,
           p.pas1  AS "bot-pas1", t.pas1,
           p.pas2  AS "bot-pas2", t.pas2,
           p.jumlah  AS "bot-jumlah", t.pas1 + t.pas2 AS "jumlah",
           -1 as "jumlah-sah",
           p.tidak_sah AS "bot-tidak-sah", "tSah" as "tidak-sah",
           t.pas1 = p.pas1 AND t.pas2 = p.pas2 as "pasmatch",
           "tSah" = p.tidak_sah AS "tidak-sah-match",
           p.hash,
           p.aligned,
           p.roi,
           p.confidence,
           p.confidence_tidak_sah,
           p.photo,
           p.config,
           p.php_jumlah AS "bot-php",
           t.jum AS "php",
           p.php_jumlah = t.jum as "php-match",
           t.error AS error,
           similarity,
           t.halaman
    FROM detections AS p
             INNER JOIN tps AS t ON p.photo = t.photo
    WHERE p.config = 'digit_config_ppwp_scan_halaman_1_2019.json'
      AND t.halaman = '2'
      AND similarity > 50
      and confidence < 1.0
    ORDER BY similarity DESC
) AS balikter on terbalik.kelurahan = balikter.kelurahan
    AND terbalik.tps = balikter.tps and terbalik.php = balikter."bot-php"
    AND terbalik."bot-jumlah" = balikter.jumlah