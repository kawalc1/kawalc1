SELECT p.kelurahan, p.tps,
--t.photo,
       p.pas1  AS 'bot-pas1', t.pas1,
       p.pas2  AS 'bot-pas2', t.pas2,
       p.jumlah  AS 'bot-jumlah', t.pas1 + t.pas2 AS 'jumlah',
       -1 as 'jumlah-sah',
       p.tidak_sah AS 'bot-tidak-sah', t.tSah as 'tidak-sah',
       t.pas1 = p.pas1 AND t.pas2 = p.pas2 as 'pas-match',
       t.tSah = p.tidak_sah 'tidak-sah-match',
       p.hash,
       p.aligned,
       p.roi,
       p.confidence,
       p.confidence_tidak_sah,
       p.photo,
       p.config,
       p.php_jumlah AS 'bot-php',
       t.jum AS 'php',
       p.php_jumlah = t.jum as 'php-match',
       IFNULL(t.error,0) AS error,
       similarity
FROM detections AS p
         INNER JOIN tps AS t ON p.photo = t.photo
WHERE p.config = 'digit_config_ppwp_scan_halaman_1_2019.json' AND t.halaman = 2
  AND similarity > 50